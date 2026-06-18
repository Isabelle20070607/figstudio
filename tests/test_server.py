from fastapi.testclient import TestClient
import pandas as pd

from figstudio.models import AxesSpec, DatasetRef, FigureSpec, PlotLayer, RecipeDatasetRef, RecipeLayer
from figstudio.registry import VariableRegistry
from figstudio.server import create_app
from figstudio.session import FigStudioSession


def test_api_session_variables_render_and_notebook_save():
    session = FigStudioSession(registry=VariableRegistry({"values": [1, 2, 3]}), port=8001)
    client = TestClient(create_app(session))

    session_response = client.get("/api/session")
    assert session_response.status_code == 200
    assert session_response.json()["has_script_writeback"] is False

    variables_response = client.get("/api/variables")
    assert variables_response.status_code == 200
    assert variables_response.json()[0]["name"] == "values"

    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(variable="values"),
            )
        ]
    )
    render_response = client.post("/api/render", json={"spec": spec.model_dump(), "format": "svg"})
    assert render_response.status_code == 200
    assert "<svg" in render_response.json()["image"]

    save_response = client.post("/api/save-code", json={"spec": spec.model_dump()})
    assert save_response.status_code == 200
    assert save_response.json()["wrote_file"] is False
    assert "notebook_cell" in save_response.json()


def test_render_and_export_failures_return_structured_errors():
    session = FigStudioSession(registry=VariableRegistry({}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(variable="missing_values"),
            )
        ]
    )

    render_response = client.post("/api/render", json={"spec": spec.model_dump(), "format": "svg"})
    export_response = client.post("/api/export", json={"spec": spec.model_dump(), "format": "svg"})

    assert render_response.status_code == 400
    assert render_response.json()["detail"]["error"]["code"] == "validation_failed"
    assert export_response.status_code == 400
    assert export_response.json()["detail"]["error"]["code"] == "validation_failed"


def test_script_writeback_failure_returns_code_and_error(tmp_path):
    script = tmp_path / "analysis.py"
    script.write_text("print('no marker')\n", encoding="utf-8")
    session = FigStudioSession(
        registry=VariableRegistry({"values": [1, 2, 3]}),
        script_path=str(script),
        port=8001,
    )
    client = TestClient(create_app(session))
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(variable="values"),
            )
        ]
    )

    save_response = client.post("/api/save-code", json={"spec": spec.model_dump()})
    payload = save_response.json()

    assert save_response.status_code == 200
    assert payload["ok"] is False
    assert payload["wrote_file"] is False
    assert payload["error"]["code"] == "writeback_failed"
    assert "axes_flat[0].plot" in payload["code"]


def test_validate_endpoint_reports_missing_variable_before_render():
    session = FigStudioSession(registry=VariableRegistry({"values": [1, 2, 3]}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(variable="missing_values"),
            )
        ]
    )

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})
    rendered = client.post("/api/render", json={"spec": spec.model_dump(), "format": "svg"})

    assert validation.status_code == 200
    assert validation.json()["ok"] is False
    assert validation.json()["issues"][0]["code"] == "missing_variable"
    assert (
        validation.json()["issues"][0]["suggestion"]
        == "Set dataset.variable to 'values', or reopen FigStudio with 'missing_values' in scope."
    )
    assert validation.json()["issues"][0]["details"]["available_variables"] == ["values"]
    assert rendered.status_code == 400
    assert rendered.json()["detail"]["error"]["code"] == "validation_failed"


def test_validate_endpoint_reports_field_level_column_suggestions():
    df = pd.DataFrame({"condition": ["a", "b"], "response": [1.0, 1.5]})
    session = FigStudioSession(registry=VariableRegistry({"df": df}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="grouped_points",
                dataset=RecipeDatasetRef(variable="df", x="condition", y="missing"),
            )
        ]
    )

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})
    issue = validation.json()["issues"][0]

    assert validation.status_code == 200
    assert validation.json()["ok"] is False
    assert issue["code"] == "missing_column"
    assert issue["field"] == "dataset.y"
    assert issue["suggestion"] == "Set dataset.y to 'response', or choose another column on 'df'."
    assert issue["details"]["available_columns"] == ["condition", "response"]
    assert issue["details"]["suggested_value"] == "response"


def test_validate_endpoint_reports_dimension_mismatch():
    session = FigStudioSession(
        registry=VariableRegistry({"x": [1, 2, 3], "y": [1, 2]}),
        port=8001,
    )
    client = TestClient(create_app(session))
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(variable="y", x_variable="x", y_variable="y"),
            )
        ]
    )

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})

    assert validation.status_code == 200
    assert validation.json()["ok"] is False
    assert validation.json()["issues"][0]["code"] == "dimension_mismatch"


def test_validate_endpoint_reports_layout_geometry_errors():
    session = FigStudioSession(registry=VariableRegistry({}), port=8001)
    client = TestClient(create_app(session))

    cases = [
        (
            FigureSpec(
                rows=1,
                cols=2,
                axes=[
                    AxesSpec(id="ax0", row=0, col=0),
                    AxesSpec(id="ax0", row=0, col=1),
                ],
            ),
            "duplicate_axes_id",
        ),
        (
            FigureSpec(rows=1, cols=1, axes=[AxesSpec(id="ax0", row=0, col=0, rowspan=0)]),
            "invalid_axes_span",
        ),
        (
            FigureSpec(rows=1, cols=1, axes=[AxesSpec(id="ax0", row=0, col=0, colspan=2)]),
            "axes_out_of_bounds",
        ),
        (
            FigureSpec(
                rows=1,
                cols=2,
                axes=[
                    AxesSpec(id="ax0", row=0, col=0, colspan=2),
                    AxesSpec(id="ax1", row=0, col=1),
                ],
            ),
            "axes_overlap",
        ),
    ]

    for spec, expected_code in cases:
        validation = client.post("/api/validate", json={"spec": spec.model_dump()})
        issues = validation.json()["issues"]

        assert validation.status_code == 200
        assert validation.json()["ok"] is False
        assert any(issue["code"] == expected_code for issue in issues)


def test_recipe_api_smoke_workflow():
    df = pd.DataFrame(
        {
            "condition": ["before", "after", "before", "after"],
            "subject": ["s1", "s1", "s2", "s2"],
            "response": [1.0, 1.4, 0.8, 1.1],
        }
    )
    session = FigStudioSession(registry=VariableRegistry({"df": df}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="paired_before_after",
                dataset=RecipeDatasetRef(
                    variable="df",
                    x="condition",
                    y="response",
                    subject="subject",
                ),
            )
        ]
    )

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})
    rendered = client.post("/api/render", json={"spec": spec.model_dump(), "format": "svg"})

    assert validation.status_code == 200
    assert validation.json()["ok"] is True
    assert rendered.status_code == 200
    assert "<svg" in rendered.json()["image"]
    assert "_recipe_recipe_1_subjects" in rendered.json()["code"]


def test_recipe_validation_reports_non_dataframe_source():
    session = FigStudioSession(registry=VariableRegistry({"values": [1, 2, 3]}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="mean_sem_line",
                dataset=RecipeDatasetRef(variable="values", x="condition", y="response"),
            )
        ]
    )

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})

    assert validation.status_code == 200
    assert validation.json()["ok"] is False
    assert validation.json()["issues"][0]["code"] == "unsupported_recipe_source"


def test_recipe_validation_reports_missing_columns():
    session = FigStudioSession(registry=VariableRegistry({"df": pd.DataFrame({"condition": ["a"]})}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="grouped_points",
                dataset=RecipeDatasetRef(variable="df", x="condition", y="missing"),
            )
        ]
    )

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})

    assert validation.status_code == 200
    assert validation.json()["ok"] is False
    assert validation.json()["issues"][0]["code"] == "missing_column"
    assert validation.json()["issues"][0]["field"] == "dataset.y"

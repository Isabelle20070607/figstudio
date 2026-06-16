from fastapi.testclient import TestClient

from figstudio.models import DatasetRef, FigureSpec, PlotLayer
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

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})
    rendered = client.post("/api/render", json={"spec": spec.model_dump(), "format": "svg"})

    assert validation.status_code == 200
    assert validation.json()["ok"] is False
    assert validation.json()["issues"][0]["code"] == "missing_variable"
    assert rendered.status_code == 400
    assert rendered.json()["detail"]["error"]["code"] == "validation_failed"


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

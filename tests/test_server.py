from fastapi.testclient import TestClient
import pandas as pd

from figstudio.models import (
    AxesSpec,
    DataFilterSpec,
    DataSelectionSpec,
    DatasetRef,
    FigureSpec,
    PlotLayer,
    RecipeDatasetRef,
    RecipeLayer,
    ReferenceLineSpec,
    SecondaryYAxisSpec,
)
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
    save_payload = save_response.json()
    assert save_response.status_code == 200
    assert save_payload["ok"] is True
    assert save_payload["wrote_file"] is False
    assert save_payload["script_path"] is None
    assert save_payload["code"] == save_payload["notebook_cell"]
    assert "axes_flat[0].plot(range(len(values)), values" in save_payload["notebook_cell"]
    assert "No script_path was provided" in save_payload["message"]


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


def test_readiness_warnings_are_export_context_only_and_advisory():
    session = FigStudioSession(registry=VariableRegistry({"values": [1, 2, 3]}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(
        width=3.0,
        height=2.0,
        dpi=120,
        layers=[
            PlotLayer(id="layer-1", kind="line", dataset=DatasetRef(variable="values")),
            PlotLayer(id="layer-2", kind="scatter", dataset=DatasetRef(variable="values")),
        ],
    )

    edit_validation = client.post("/api/validate", json={"spec": spec.model_dump()})
    export_validation = client.post(
        "/api/validate",
        json={"spec": spec.model_dump(), "context": "export", "export_format": "png"},
    )
    export_response = client.post("/api/export", json={"spec": spec.model_dump(), "format": "png"})

    assert edit_validation.status_code == 200
    assert edit_validation.json()["ok"] is True
    assert not any(issue["code"].startswith("readiness_") for issue in edit_validation.json()["issues"])

    assert export_validation.status_code == 200
    assert export_validation.json()["ok"] is True
    issue_codes = {issue["code"] for issue in export_validation.json()["issues"]}
    assert {
        "readiness_missing_axis_label",
        "readiness_missing_legend_labels",
        "readiness_low_png_resolution",
    } <= issue_codes
    assert all(issue["severity"] == "warning" for issue in export_validation.json()["issues"])
    low_resolution = next(
        issue for issue in export_validation.json()["issues"] if issue["code"] == "readiness_low_png_resolution"
    )
    assert low_resolution["details"]["pixel_width"] == 360
    assert export_response.status_code == 200
    assert export_response.json()["format"] == "png"


def test_export_readiness_reports_empty_figure_and_secondary_axis_label():
    session = FigStudioSession(registry=VariableRegistry({"values": [1, 2, 3]}), port=8001)
    client = TestClient(create_app(session))
    empty_spec = FigureSpec(reference_lines=[ReferenceLineSpec(id="baseline", value=0.0)])
    right_axis_spec = FigureSpec(
        axes=[AxesSpec(id="ax0", xlabel="Time")],
        layers=[
            PlotLayer(
                id="rate",
                kind="line",
                y_axis="right",
                dataset=DatasetRef(variable="values"),
            )
        ],
    )

    empty_validation = client.post(
        "/api/validate",
        json={"spec": empty_spec.model_dump(), "context": "export", "export_format": "svg"},
    )
    right_axis_validation = client.post(
        "/api/validate",
        json={"spec": right_axis_spec.model_dump(), "context": "export", "export_format": "svg"},
    )

    assert empty_validation.status_code == 200
    assert empty_validation.json()["ok"] is True
    assert empty_validation.json()["issues"][0]["code"] == "readiness_empty_figure"
    assert empty_validation.json()["issues"][0]["severity"] == "warning"

    assert right_axis_validation.status_code == 200
    assert right_axis_validation.json()["ok"] is True
    issue_codes = {issue["code"] for issue in right_axis_validation.json()["issues"]}
    assert "readiness_missing_secondary_y_label" in issue_codes


def test_facet_values_endpoint_returns_ordered_dataframe_values():
    df = pd.DataFrame(
        {
            "condition": ["control", "drug", "control", None, float("nan"), "wash"],
            "response": [1, 2, 3, 4, 5, 6],
        }
    )
    session = FigStudioSession(registry=VariableRegistry({"df": df}), port=8001)
    client = TestClient(create_app(session))

    response = client.post(
        "/api/facet-values",
        json={"variable": "df", "column": "condition", "max_values": 2},
    )

    assert response.status_code == 200
    assert response.json() == {
        "values": [
            {"value": "control", "label": "control"},
            {"value": "drug", "label": "drug"},
        ],
        "truncated": True,
    }


def test_facet_values_endpoint_reports_invalid_source():
    session = FigStudioSession(registry=VariableRegistry({"values": [1, 2, 3]}), port=8001)
    client = TestClient(create_app(session))

    response = client.post(
        "/api/facet-values",
        json={"variable": "values", "column": "condition", "max_values": 12},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"]["code"] == "unsupported_facet_source"


def test_repeated_panel_candidates_return_dataframe_mapping_and_sequence_items():
    df = pd.DataFrame({"condition": ["control", "drug", "control"], "response": [1, 2, 3]})
    unsafe_key = object()
    mapping = {
        ("control", 1): pd.Series([1.0, 2.0], name="signal"),
        unsafe_key: [3.0, 4.0],
    }
    sequence = [[1.0, 2.0], 3.0]
    session = FigStudioSession(
        registry=VariableRegistry({"df": df, "signal_map": mapping, "signal_sequence": sequence}),
        port=8001,
    )
    client = TestClient(create_app(session))

    df_response = client.post(
        "/api/repeated-panel-candidates",
        json={"variable": "df", "source_kind": "dataframe_column", "column": "condition", "max_values": 2},
    )
    mapping_response = client.post(
        "/api/repeated-panel-candidates",
        json={"variable": "signal_map", "source_kind": "mapping_keys", "max_values": 12},
    )
    sequence_response = client.post(
        "/api/repeated-panel-candidates",
        json={"variable": "signal_sequence", "source_kind": "sequence_items", "max_values": 12},
    )

    assert df_response.status_code == 200
    assert df_response.json()["source_kind"] == "dataframe_column"
    assert [item["label"] for item in df_response.json()["candidates"]] == ["control", "drug"]
    assert mapping_response.status_code == 200
    mapping_payload = mapping_response.json()
    assert mapping_payload["source_kind"] == "mapping_keys"
    assert mapping_payload["candidates"][0]["selection"] == {
        "kind": "mapping_key",
        "key": ["control", 1],
        "index": None,
        "label": "('control', 1)",
    }
    assert mapping_payload["candidates"][0]["summary"]["kind"] == "series"
    assert mapping_payload["skipped"][0]["reason"] == "Mapping key cannot be represented as a stable Python literal."
    assert sequence_response.status_code == 200
    sequence_payload = sequence_response.json()
    assert sequence_payload["source_kind"] == "sequence_items"
    assert sequence_payload["candidates"][0]["selection"]["index"] == 0
    assert sequence_payload["candidates"][0]["summary"]["kind"] == "sequence"
    assert sequence_payload["candidates"][1]["summary"] is None


def test_selected_mapping_layer_validates_and_renders():
    session = FigStudioSession(registry=VariableRegistry({"signal_map": {"control": [1, 2, 3]}}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(
                    variable="signal_map",
                    selection=DataSelectionSpec(kind="mapping_key", key="control", label="Control"),
                ),
            )
        ]
    )

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})
    rendered = client.post("/api/render", json={"spec": spec.model_dump(), "format": "svg"})

    assert validation.status_code == 200
    assert validation.json()["ok"] is True
    assert rendered.status_code == 200
    assert "_layer_layer_1_selected = signal_map['control']" in rendered.json()["code"]


def test_selection_validation_reports_invalid_sources_and_items():
    specs = [
        (
            VariableRegistry({"values": [1, 2, 3]}),
            DatasetRef(
                variable="values",
                selection=DataSelectionSpec(kind="mapping_key", key="missing", label="Missing"),
            ),
            "unsupported_selection_source",
        ),
        (
            VariableRegistry({"signal_map": {"control": [1, 2, 3]}}),
            DatasetRef(
                variable="signal_map",
                selection=DataSelectionSpec(kind="mapping_key", key="missing", label="Missing"),
            ),
            "missing_selection_key",
        ),
        (
            VariableRegistry({"signal_sequence": [[1, 2, 3]]}),
            DatasetRef(
                variable="signal_sequence",
                selection=DataSelectionSpec(kind="sequence_index", index=3, label="3"),
            ),
            "selection_index_out_of_range",
        ),
        (
            VariableRegistry({"signal_map": {"scalar": 1.0}}),
            DatasetRef(
                variable="signal_map",
                selection=DataSelectionSpec(kind="mapping_key", key="scalar", label="Scalar"),
            ),
            "unplottable_selection_value",
        ),
        (
            VariableRegistry({"signal_map": {"control": [1, 2, 3]}}),
            DatasetRef(
                variable="signal_map",
                selection=DataSelectionSpec(kind="mapping_key", key="control", label="Control"),
                x="time",
            ),
            "unsupported_selected_channel",
        ),
    ]

    for registry, dataset, expected_code in specs:
        session = FigStudioSession(registry=registry, port=8001)
        client = TestClient(create_app(session))
        spec = FigureSpec(layers=[PlotLayer(id="layer-1", kind="line", dataset=dataset)])

        validation = client.post("/api/validate", json={"spec": spec.model_dump()})
        codes = [issue["code"] for issue in validation.json()["issues"]]

        assert validation.status_code == 200
        assert validation.json()["ok"] is False
        assert expected_code in codes


def test_validate_endpoint_reports_filter_column_and_empty_filter_result():
    df = pd.DataFrame({"condition": ["control"], "response": [1.0]})
    session = FigStudioSession(registry=VariableRegistry({"df": df}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="missing-filter-column",
                kind="line",
                dataset=DatasetRef(
                    variable="df",
                    y="response",
                    filters=[DataFilterSpec(column="missing", value="control")],
                ),
            ),
            PlotLayer(
                id="empty-filter",
                kind="line",
                axes_id="ax0",
                dataset=DatasetRef(
                    variable="df",
                    y="response",
                    filters=[DataFilterSpec(column="condition", value="drug")],
                ),
            ),
        ]
    )

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})
    issues = validation.json()["issues"]

    assert validation.status_code == 200
    assert validation.json()["ok"] is False
    assert [issue["code"] for issue in issues] == ["missing_column", "empty_filter_result"]
    assert issues[0]["field"] == "dataset.filters.column"
    assert issues[1]["severity"] == "warning"


def test_reference_line_api_smoke_workflow_without_data_layer():
    session = FigStudioSession(registry=VariableRegistry({}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(reference_lines=[ReferenceLineSpec(id="baseline", value=0.0)])

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})
    rendered = client.post("/api/render", json={"spec": spec.model_dump(), "format": "svg"})

    assert validation.status_code == 200
    assert validation.json()["ok"] is True
    assert rendered.status_code == 200
    assert "<svg" in rendered.json()["image"]
    assert "axes_flat[0].axhline(0.0" in rendered.json()["code"]


def test_secondary_y_axis_api_smoke_workflow():
    df = pd.DataFrame(
        {
            "time": [0, 1, 2],
            "signal": [0.1, 0.4, 0.2],
            "rate": [8.0, 12.0, 9.5],
        }
    )
    session = FigStudioSession(registry=VariableRegistry({"df": df}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(
        axes=[AxesSpec(id="ax0", secondary_y=SecondaryYAxisSpec(ylabel="Rate"))],
        layers=[
            PlotLayer(
                id="signal",
                kind="line",
                dataset=DatasetRef(variable="df", x="time", y="signal"),
            ),
            PlotLayer(
                id="rate",
                kind="line",
                y_axis="right",
                dataset=DatasetRef(variable="df", x="time", y="rate"),
            ),
        ],
    )

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})
    rendered = client.post("/api/render", json={"spec": spec.model_dump(), "format": "svg"})

    assert validation.status_code == 200
    assert validation.json()["ok"] is True
    assert rendered.status_code == 200
    assert "<svg" in rendered.json()["image"]
    assert "secondary_axes[0] = axes_flat[0].twinx()" in rendered.json()["code"]
    assert "secondary_axes[0].plot(df['time'], df['rate']" in rendered.json()["code"]


def test_secondary_y_axis_validation_reports_unsupported_layer_kind_and_log_data():
    session = FigStudioSession(
        registry=VariableRegistry({"matrix": [[1, 2], [3, 4]], "rate": [0.0, 1.0]}),
        port=8001,
    )
    client = TestClient(create_app(session))
    spec = FigureSpec(
        axes=[AxesSpec(id="ax0", secondary_y=SecondaryYAxisSpec(yscale="log"))],
        layers=[
            PlotLayer(
                id="field",
                kind="heatmap",
                y_axis="right",
                dataset=DatasetRef(variable="matrix"),
            ),
            PlotLayer(
                id="rate",
                kind="line",
                y_axis="right",
                dataset=DatasetRef(variable="rate"),
            ),
        ],
    )

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})
    issues = validation.json()["issues"]

    assert validation.status_code == 200
    assert validation.json()["ok"] is False
    assert [issue["code"] for issue in issues] == [
        "unsupported_secondary_y_layer",
        "log_scale_non_positive",
    ]
    assert issues[0]["field"] == "y_axis"
    assert issues[1]["field"] == "dataset.y"


def test_validate_endpoint_reports_reference_line_errors():
    session = FigStudioSession(registry=VariableRegistry({}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(
        axes=[AxesSpec(id="ax0", yscale="log")],
        reference_lines=[
            ReferenceLineSpec(id="missing-axis", axes_id="missing", value=1.0),
            ReferenceLineSpec(id="bad-log-value", axes_id="ax0", value=0.0),
        ],
    )

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})
    issues = validation.json()["issues"]

    assert validation.status_code == 200
    assert validation.json()["ok"] is False
    assert [issue["code"] for issue in issues] == ["missing_axes", "invalid_reference_line_value"]
    assert issues[0]["field"] == "reference_lines.axes_id"
    assert issues[1]["field"] == "reference_lines.value"


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


def test_mean_sem_bar_recipe_api_smoke_workflow():
    df = pd.DataFrame(
        {
            "condition": ["control", "drug", "control", "drug", "control", "drug"],
            "genotype": ["wt", "wt", "mut", "mut", "wt", "wt"],
            "response": [1.0, 1.4, 0.8, 1.1, 1.2, 1.6],
        }
    )
    session = FigStudioSession(registry=VariableRegistry({"df": df}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="mean_sem_bar",
                dataset=RecipeDatasetRef(
                    variable="df",
                    x="condition",
                    y="response",
                    group="genotype",
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
    assert "axes_flat[0].bar(_recipe_recipe_1_positions" in rendered.json()["code"]


def test_count_bar_recipe_api_smoke_workflow():
    df = pd.DataFrame(
        {
            "condition": ["control", "drug", "control", "drug", "drug"],
            "genotype": ["wt", "wt", "mut", "mut", "wt"],
        }
    )
    session = FigStudioSession(registry=VariableRegistry({"df": df}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="count_bar",
                dataset=RecipeDatasetRef(
                    variable="df",
                    x="condition",
                    group="genotype",
                ),
                error="none",
            )
        ]
    )

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})
    rendered = client.post("/api/render", json={"spec": spec.model_dump(), "format": "svg"})

    assert validation.status_code == 200
    assert validation.json()["ok"] is True
    assert rendered.status_code == 200
    assert "<svg" in rendered.json()["image"]
    assert "groupby(['condition', 'genotype'], sort=False).size().unstack(fill_value=0)" in rendered.json()["code"]


def test_stacked_bar_recipe_api_smoke_workflow():
    df = pd.DataFrame(
        {
            "condition": ["control", "drug", "control", "drug", "drug"],
            "genotype": ["wt", "wt", "mut", "mut", "wt"],
        }
    )
    session = FigStudioSession(registry=VariableRegistry({"df": df}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="stacked_bar",
                dataset=RecipeDatasetRef(
                    variable="df",
                    x="condition",
                    group="genotype",
                ),
                error="none",
            )
        ]
    )

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})
    rendered = client.post("/api/render", json={"spec": spec.model_dump(), "format": "svg"})

    assert validation.status_code == 200
    assert validation.json()["ok"] is True
    assert rendered.status_code == 200
    assert "<svg" in rendered.json()["image"]
    assert "bottom=_recipe_recipe_1_bottom" in rendered.json()["code"]


def test_boxplot_by_category_recipe_api_smoke_workflow():
    df = pd.DataFrame(
        {
            "condition": ["control", "control", "drug", "drug", "drug"],
            "genotype": ["wt", "mut", "wt", "mut", "wt"],
            "response": [1.0, 0.8, 1.4, 1.1, 1.6],
        }
    )
    session = FigStudioSession(registry=VariableRegistry({"df": df}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="boxplot_by_category",
                dataset=RecipeDatasetRef(
                    variable="df",
                    x="condition",
                    y="response",
                    group="genotype",
                ),
                error="none",
            )
        ]
    )

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})
    rendered = client.post("/api/render", json={"spec": spec.model_dump(), "format": "svg"})

    assert validation.status_code == 200
    assert validation.json()["ok"] is True
    assert rendered.status_code == 200
    assert "<svg" in rendered.json()["image"]
    assert "axes_flat[0].boxplot(_recipe_recipe_1_group_values" in rendered.json()["code"]


def test_violin_by_category_recipe_api_smoke_workflow():
    df = pd.DataFrame(
        {
            "condition": ["control", "control", "drug", "drug", "drug"],
            "genotype": ["wt", "mut", "wt", "mut", "wt"],
            "response": [1.0, 0.8, 1.4, 1.1, 1.6],
        }
    )
    session = FigStudioSession(registry=VariableRegistry({"df": df}), port=8001)
    client = TestClient(create_app(session))
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="violin_by_category",
                dataset=RecipeDatasetRef(
                    variable="df",
                    x="condition",
                    y="response",
                    group="genotype",
                ),
                error="none",
            )
        ]
    )

    validation = client.post("/api/validate", json={"spec": spec.model_dump()})
    rendered = client.post("/api/render", json={"spec": spec.model_dump(), "format": "svg"})

    assert validation.status_code == 200
    assert validation.json()["ok"] is True
    assert rendered.status_code == 200
    assert "<svg" in rendered.json()["image"]
    assert "axes_flat[0].violinplot(_recipe_recipe_1_group_values" in rendered.json()["code"]


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


def test_count_bar_validation_accepts_missing_y_and_reports_missing_x_or_group():
    df = pd.DataFrame({"condition": ["control", "drug"], "genotype": ["wt", "mut"]})
    session = FigStudioSession(registry=VariableRegistry({"df": df}), port=8001)
    client = TestClient(create_app(session))

    valid_spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="count-ok",
                kind="count_bar",
                dataset=RecipeDatasetRef(variable="df", x="condition"),
                error="none",
            )
        ]
    )
    missing_x_spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="count-missing-x",
                kind="count_bar",
                dataset=RecipeDatasetRef(variable="df"),
                error="none",
            )
        ]
    )
    missing_group_spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="count-missing-group",
                kind="count_bar",
                dataset=RecipeDatasetRef(variable="df", x="condition", group="missing_group"),
                error="none",
            )
        ]
    )

    valid = client.post("/api/validate", json={"spec": valid_spec.model_dump()})
    missing_x = client.post("/api/validate", json={"spec": missing_x_spec.model_dump()})
    missing_group = client.post("/api/validate", json={"spec": missing_group_spec.model_dump()})

    assert valid.status_code == 200
    assert valid.json()["ok"] is True
    assert missing_x.status_code == 200
    assert missing_x.json()["ok"] is False
    assert missing_x.json()["issues"][0]["field"] == "dataset.x"
    assert missing_group.status_code == 200
    assert missing_group.json()["ok"] is False
    assert missing_group.json()["issues"][0]["field"] == "dataset.group"


def test_stacked_bar_validation_requires_group_and_ignores_y():
    df = pd.DataFrame({"condition": ["control", "drug"], "genotype": ["wt", "mut"], "response": [1.0, 2.0]})
    session = FigStudioSession(registry=VariableRegistry({"df": df}), port=8001)
    client = TestClient(create_app(session))

    valid_spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="stacked-ok",
                kind="stacked_bar",
                dataset=RecipeDatasetRef(variable="df", x="condition", y="missing", group="genotype"),
                error="none",
            )
        ]
    )
    missing_group_spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="stacked-missing-group",
                kind="stacked_bar",
                dataset=RecipeDatasetRef(variable="df", x="condition"),
                error="none",
            )
        ]
    )

    valid = client.post("/api/validate", json={"spec": valid_spec.model_dump()})
    missing_group = client.post("/api/validate", json={"spec": missing_group_spec.model_dump()})

    assert valid.status_code == 200
    assert valid.json()["ok"] is True
    assert missing_group.status_code == 200
    assert missing_group.json()["ok"] is False
    assert missing_group.json()["issues"][0]["field"] == "dataset.group"


def test_boxplot_by_category_validation_requires_y_and_accepts_optional_group():
    df = pd.DataFrame({"condition": ["control", "drug"], "genotype": ["wt", "mut"], "response": [1.0, 2.0]})
    session = FigStudioSession(registry=VariableRegistry({"df": df}), port=8001)
    client = TestClient(create_app(session))

    valid_spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="boxplot-ok",
                kind="boxplot_by_category",
                dataset=RecipeDatasetRef(variable="df", x="condition", y="response", group="genotype"),
                error="none",
            )
        ]
    )
    missing_y_spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="boxplot-missing-y",
                kind="boxplot_by_category",
                dataset=RecipeDatasetRef(variable="df", x="condition"),
                error="none",
            )
        ]
    )

    valid = client.post("/api/validate", json={"spec": valid_spec.model_dump()})
    missing_y = client.post("/api/validate", json={"spec": missing_y_spec.model_dump()})

    assert valid.status_code == 200
    assert valid.json()["ok"] is True
    assert missing_y.status_code == 200
    assert missing_y.json()["ok"] is False
    assert missing_y.json()["issues"][0]["field"] == "dataset.y"


def test_violin_by_category_validation_requires_y_and_ignores_subject_and_error():
    df = pd.DataFrame({"condition": ["control", "drug"], "genotype": ["wt", "mut"], "response": [1.0, 2.0]})
    session = FigStudioSession(registry=VariableRegistry({"df": df}), port=8001)
    client = TestClient(create_app(session))

    valid_spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="violin-ok",
                kind="violin_by_category",
                dataset=RecipeDatasetRef(
                    variable="df",
                    x="condition",
                    y="response",
                    group="genotype",
                    subject="missing_subject",
                ),
                error="sd",
            )
        ]
    )
    missing_y_spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="violin-missing-y",
                kind="violin_by_category",
                dataset=RecipeDatasetRef(variable="df", x="condition"),
                error="none",
            )
        ]
    )

    valid = client.post("/api/validate", json={"spec": valid_spec.model_dump()})
    missing_y = client.post("/api/validate", json={"spec": missing_y_spec.model_dump()})

    assert valid.status_code == 200
    assert valid.json()["ok"] is True
    assert missing_y.status_code == 200
    assert missing_y.json()["ok"] is False
    assert missing_y.json()["issues"][0]["field"] == "dataset.y"

import figstudio
from figstudio.models import (
    AxesSpec,
    DataFilterSpec,
    DataSelectionSpec,
    DatasetRef,
    FigureSpec,
    PlotLayer,
    ReferenceLineSpec,
)


def test_load_and_save_figstudio_spec_json(tmp_path):
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(variable="values"),
            )
        ],
    )
    path = tmp_path / "figure.figstudio.json"

    saved = figstudio.save_spec(spec, path)
    loaded = figstudio.load_spec(saved)

    assert saved == path
    assert loaded.layers[0].id == "layer-1"
    assert loaded.style.preset == "custom"


def test_reference_lines_round_trip_spec_json(tmp_path):
    spec = FigureSpec(reference_lines=[ReferenceLineSpec(id="baseline", value=0.0)])
    path = tmp_path / "reference-lines.figstudio.json"

    loaded = figstudio.load_spec(figstudio.save_spec(spec, path))

    assert loaded.reference_lines[0].id == "baseline"
    assert loaded.reference_lines[0].orientation == "horizontal"


def test_filtered_faceted_spec_round_trip_json(tmp_path):
    spec = FigureSpec(
        rows=1,
        cols=2,
        share_x=True,
        layers=[
            PlotLayer(
                id="control",
                kind="line",
                axes_id="ax0",
                dataset=DatasetRef(
                    variable="df",
                    x="time",
                    y="signal",
                    filters=[DataFilterSpec(column="condition", value="control", label="Control")],
                ),
            )
        ],
    )
    path = tmp_path / "facets.figstudio.json"

    loaded = figstudio.load_spec(figstudio.save_spec(spec, path))

    assert loaded.share_x is True
    assert loaded.share_y is False
    assert loaded.layers[0].dataset.filters[0].column == "condition"
    assert loaded.layers[0].dataset.filters[0].label == "Control"


def test_selected_panel_spec_round_trip_json(tmp_path):
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="control",
                kind="line",
                dataset=DatasetRef(
                    variable="signal_map",
                    selection=DataSelectionSpec(kind="mapping_key", key="control", label="Control"),
                ),
            ),
            PlotLayer(
                id="sequence-item",
                kind="line",
                dataset=DatasetRef(
                    variable="signal_sequence",
                    selection=DataSelectionSpec(kind="sequence_index", index=1, label="1"),
                ),
            ),
        ],
    )
    path = tmp_path / "selected-panels.figstudio.json"

    loaded = figstudio.load_spec(figstudio.save_spec(spec, path))

    assert loaded.layers[0].dataset.selection is not None
    assert loaded.layers[0].dataset.selection.kind == "mapping_key"
    assert loaded.layers[0].dataset.selection.key == "control"
    assert loaded.layers[1].dataset.selection is not None
    assert loaded.layers[1].dataset.selection.index == 1


def test_loads_legacy_axes_without_span_fields(tmp_path):
    path = tmp_path / "legacy.figstudio.json"
    path.write_text(
        """
{
  "version": 1,
  "mode": "explore",
  "width": 6.4,
  "height": 4.8,
  "dpi": 120,
  "rows": 1,
  "cols": 1,
  "axes": [
    {
      "id": "ax0",
      "row": 0,
      "col": 0,
      "title": "",
      "xlabel": "",
      "ylabel": "",
      "xscale": "linear",
      "yscale": "linear",
      "xlim": null,
      "ylim": null,
      "grid": false,
      "legend": true,
      "colorbar": false
    }
  ],
  "layers": [],
  "recipes": [],
  "annotations": [],
  "style": {
    "preset": "custom",
    "title": "",
    "font_size": 10,
    "constrained_layout": true
  },
  "show": false
}
""".strip(),
        encoding="utf-8",
    )

    loaded = figstudio.load_spec(path)

    assert loaded.axes[0].rowspan == 1
    assert loaded.axes[0].colspan == 1
    assert loaded.share_x is False
    assert loaded.share_y is False
    assert loaded.reference_lines == []


def test_spanned_axes_round_trip_spec_json(tmp_path):
    spec = FigureSpec(
        rows=2,
        cols=2,
        axes=[
            AxesSpec(id="ax0", row=0, col=0, rowspan=2, colspan=1),
            AxesSpec(id="ax1", row=0, col=1),
            AxesSpec(id="ax2", row=1, col=1),
        ],
    )
    path = tmp_path / "spanned.figstudio.json"

    loaded = figstudio.load_spec(figstudio.save_spec(spec, path))

    assert loaded.axes[0].rowspan == 2
    assert loaded.axes[0].colspan == 1
    assert [axis.id for axis in loaded.axes] == ["ax0", "ax1", "ax2"]

import figstudio
from figstudio.models import DatasetRef, FigureSpec, PlotLayer


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

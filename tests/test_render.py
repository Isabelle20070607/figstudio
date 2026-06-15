from figstudio.models import DatasetRef, FigureSpec, PlotLayer
from figstudio.render import RenderEngine


def test_render_svg_from_generated_spec():
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(variable="values"),
            )
        ]
    )

    svg, code = RenderEngine({"values": [1, 2, 3]}).render_base64(spec, "svg")

    assert "<svg" in svg
    assert "axes_flat[0].plot" in code

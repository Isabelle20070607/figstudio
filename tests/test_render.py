from figstudio.models import AxesSpec, DatasetRef, FigureSpec, PlotLayer
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


def test_render_svg_from_spanned_layout():
    spec = FigureSpec(
        rows=2,
        cols=2,
        axes=[
            AxesSpec(id="ax0", row=0, col=0, rowspan=2, colspan=1),
            AxesSpec(id="ax1", row=0, col=1),
            AxesSpec(id="ax2", row=1, col=1),
        ],
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                axes_id="ax0",
                dataset=DatasetRef(variable="values"),
            )
        ],
    )

    svg, code = RenderEngine({"values": [1, 2, 3]}).render_base64(spec, "svg")

    assert "<svg" in svg
    assert "fig.add_gridspec(2, 2)" in code

from figstudio.models import AxesSpec, DatasetRef, FigureSpec, PlotLayer, SecondaryYAxisSpec
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


def test_render_svg_from_secondary_y_axis_overlay():
    spec = FigureSpec(
        axes=[AxesSpec(id="ax0", secondary_y=SecondaryYAxisSpec(ylabel="Rate"))],
        layers=[
            PlotLayer(
                id="signal",
                kind="line",
                dataset=DatasetRef(variable="signal", x_variable="time", y_variable="signal"),
            ),
            PlotLayer(
                id="rate",
                kind="line",
                y_axis="right",
                dataset=DatasetRef(variable="rate", x_variable="time", y_variable="rate"),
            ),
        ],
    )

    svg, code = RenderEngine(
        {"time": [0, 1, 2], "signal": [0.1, 0.3, 0.2], "rate": [8.0, 10.0, 12.0]}
    ).render_base64(spec, "svg")

    assert "<svg" in svg
    assert "secondary_axes[0] = axes_flat[0].twinx()" in code
    assert "secondary_axes[0].plot(time, rate" in code

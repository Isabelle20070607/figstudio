from figstudio.codegen import MatplotlibCodegen
from figstudio.models import DatasetRef, FigureSpec, LayerStyle, PlotLayer


def test_generates_plain_oo_matplotlib_code_for_dataframe_line():
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(variable="df", x="time", y="value"),
                style=LayerStyle(label="Signal", color="#1f77b4", marker="o"),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "import matplotlib.pyplot as plt" in code
    assert "fig, axes = plt.subplots" in code
    assert "axes_flat[0].plot(df['time'], df['value']" in code
    assert "label='Signal'" in code
    assert "axes_flat[0].legend()" in code
    assert "figstudio" not in code.lower()


def test_heatmap_adds_colorbar():
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="heat-1",
                kind="heatmap",
                dataset=DatasetRef(variable="matrix"),
                style=LayerStyle(cmap="magma"),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "imshow(matrix, cmap='magma')" in code
    assert "fig.colorbar(image_heat_1, ax=axes_flat[0])" in code


def test_generates_code_for_independent_x_and_y_variables():
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(
                    variable="signal",
                    x_variable="time",
                    y_variable="signal",
                ),
                style=LayerStyle(label="Signal"),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "axes_flat[0].plot(time, signal" in code
    assert code.count("axes_flat[0].legend()") == 1


def test_axis_can_disable_legend_for_labeled_layers():
    spec = FigureSpec(
        axes=[{"id": "ax0", "legend": False}],
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(variable="values"),
                style=LayerStyle(label="Values"),
            )
        ],
    )

    code = MatplotlibCodegen().generate(spec)

    assert "label='Values'" in code
    assert ".legend()" not in code

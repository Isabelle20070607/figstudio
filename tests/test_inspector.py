import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from figstudio.codegen import MatplotlibCodegen
from figstudio.inspector import FigureInspector


def test_existing_figure_line_inspection_preserves_x_and_y_data():
    fig, ax = plt.subplots()
    ax.plot([10, 20, 30], [1, 4, 9], label="Measured")

    try:
        inspector = FigureInspector(fig)
        namespace = inspector.extracted_namespace()
        spec = inspector.to_spec()
        code = MatplotlibCodegen().generate(spec)

        assert "_figstudio_line_0_x" in namespace
        assert "_figstudio_line_0_y" in namespace
        assert spec.layers[0].dataset.x_variable == "_figstudio_line_0_x"
        assert spec.layers[0].dataset.y_variable == "_figstudio_line_0_y"
        assert "axes_flat[0].plot(_figstudio_line_0_x, _figstudio_line_0_y" in code
    finally:
        plt.close(fig)


def test_existing_figure_inspection_extracts_scatter_image_and_bar_layers():
    fig, axes = plt.subplots(1, 3)
    axes[0].scatter([0, 1, 2], [2, 3, 5], label="Points", color="#2563eb")
    axes[1].imshow([[1, 2], [3, 4]], cmap="magma")
    axes[2].bar([0, 1], [4, 6], label="Bars", color="#0f766e")

    try:
        inspector = FigureInspector(fig)
        namespace = inspector.extracted_namespace()
        spec = inspector.to_spec()
        kinds = {layer.kind for layer in spec.layers}

        assert {"scatter", "heatmap", "bar"} <= kinds
        assert any(name.startswith("_figstudio_scatter_") for name in namespace)
        assert any(name.startswith("_figstudio_image_") for name in namespace)
        assert any(name.startswith("_figstudio_bar_") for name in namespace)
        assert any(layer.style.label == "Points" for layer in spec.layers)
        assert any(layer.style.cmap == "magma" for layer in spec.layers)
    finally:
        plt.close(fig)


def test_existing_figure_tree_reports_statistical_artist_metadata_without_fake_layers():
    fig, axes = plt.subplots(2, 2)
    axes[0, 0].hist([1, 2, 2, 3], bins=3, label="Histogram", color="#2563eb")
    axes[0, 0].legend()
    axes[0, 1].boxplot([[1, 2, 3], [2, 3, 4]])
    axes[0, 1].set_xticklabels(["A", "B"])
    axes[1, 0].violinplot([[1, 2, 3], [2, 3, 4]], showmeans=True)
    image = axes[1, 1].imshow([[1, 2], [3, 4]], cmap="magma")
    fig.colorbar(image, ax=axes[1, 1], label="Intensity")

    try:
        inspector = FigureInspector(fig)
        tree = inspector.tree()
        spec = inspector.to_spec()
        kinds = {layer.kind for layer in spec.layers}

        assert len(tree["axes"]) == 4
        assert len(tree["colorbars"]) == 1
        assert tree["colorbars"][0]["label"] == "Intensity"
        assert tree["axes"][0]["legend"]["labels"] == ["Histogram"]
        assert tree["axes"][0]["histograms"][0]["bins"] == 3
        assert tree["axes"][1]["boxplots"][0]["label"] == "A"
        assert len(tree["axes"][2]["violin_plots"]) == 2
        assert "bar" not in kinds
        assert "line" not in kinds
        assert "heatmap" in kinds
    finally:
        plt.close(fig)

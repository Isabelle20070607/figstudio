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

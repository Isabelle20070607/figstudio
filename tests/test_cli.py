from __future__ import annotations

import json

import pytest

from figstudio import save_spec
from figstudio.cli import EXIT_OK, EXIT_USAGE_OR_RUNTIME_ERROR, EXIT_VALIDATION_FAILED, main
from figstudio.models import AxesSpec, DatasetRef, FigureSpec, LayerStyle, PlotLayer


def _write_line_spec(path, *, variable: str = "values") -> None:
    save_spec(
        FigureSpec(
            axes=[AxesSpec(xlabel="Index", ylabel="Signal")],
            layers=[
                PlotLayer(
                    id="layer-1",
                    kind="line",
                    dataset=DatasetRef(variable=variable),
                    style=LayerStyle(label="Signal"),
                )
            ],
        ),
        path,
    )


def _write_data_script(path) -> None:
    path.write_text("values = [1, 2, 3, 5]\n", encoding="utf-8")


def test_cli_codegen_prints_to_stdout(tmp_path, capsys):
    spec_path = tmp_path / "figure.figstudio.json"
    _write_line_spec(spec_path)

    exit_code = main(["codegen", str(spec_path)])
    output = capsys.readouterr().out

    assert exit_code == EXIT_OK
    assert "import matplotlib.pyplot as plt" in output
    assert "axes_flat[0].plot(range(len(values)), values" in output
    assert "figstudio" not in output.lower()


def test_cli_codegen_writes_output_file(tmp_path, capsys):
    spec_path = tmp_path / "figure.figstudio.json"
    output_path = tmp_path / "figure.py"
    _write_line_spec(spec_path)

    exit_code = main(["codegen", str(spec_path), "--output", str(output_path)])

    assert exit_code == EXIT_OK
    assert capsys.readouterr().out == ""
    assert "axes_flat[0].plot(range(len(values)), values" in output_path.read_text(encoding="utf-8")


def test_cli_validate_success_json(tmp_path, capsys):
    spec_path = tmp_path / "figure.figstudio.json"
    data_script = tmp_path / "data.py"
    _write_line_spec(spec_path)
    _write_data_script(data_script)

    exit_code = main(["validate", str(spec_path), "--data-script", str(data_script), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == EXIT_OK
    assert payload["ok"] is True
    assert payload["issues"] == []


def test_cli_validate_failure_json_returns_validation_exit(tmp_path, capsys):
    spec_path = tmp_path / "missing.figstudio.json"
    _write_line_spec(spec_path, variable="missing_values")

    exit_code = main(["validate", str(spec_path), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == EXIT_VALIDATION_FAILED
    assert payload["ok"] is False
    assert payload["issues"][0]["code"] == "missing_variable"


def test_cli_render_writes_svg_and_png_outputs(tmp_path, capsys):
    spec_path = tmp_path / "figure.figstudio.json"
    data_script = tmp_path / "data.py"
    svg_path = tmp_path / "preview.svg"
    png_path = tmp_path / "preview.png"
    _write_line_spec(spec_path)
    _write_data_script(data_script)

    svg_exit = main(
        [
            "render",
            str(spec_path),
            "--data-script",
            str(data_script),
            "--output",
            str(svg_path),
        ]
    )
    png_exit = main(
        [
            "render",
            str(spec_path),
            "--data-script",
            str(data_script),
            "--output",
            str(png_path),
            "--dpi",
            "96",
        ]
    )

    assert svg_exit == EXIT_OK
    assert png_exit == EXIT_OK
    assert "<svg" in svg_path.read_text(encoding="utf-8")
    assert png_path.read_bytes().startswith(b"\x89PNG")
    assert str(svg_path) in capsys.readouterr().out


@pytest.mark.parametrize(
    ("suffix", "signature"),
    [
        ("svg", b"<svg"),
        ("png", b"\x89PNG"),
        ("pdf", b"%PDF"),
    ],
)
def test_cli_export_writes_supported_formats(tmp_path, suffix, signature):
    spec_path = tmp_path / "figure.figstudio.json"
    data_script = tmp_path / "data.py"
    output_path = tmp_path / f"export.{suffix}"
    _write_line_spec(spec_path)
    _write_data_script(data_script)

    exit_code = main(
        [
            "export",
            str(spec_path),
            "--data-script",
            str(data_script),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == EXIT_OK
    assert signature in output_path.read_bytes()[:500]


def test_cli_rejects_ambiguous_output_format(tmp_path, capsys):
    spec_path = tmp_path / "figure.figstudio.json"
    data_script = tmp_path / "data.py"
    output_path = tmp_path / "preview.unknown"
    _write_line_spec(spec_path)
    _write_data_script(data_script)

    exit_code = main(
        [
            "render",
            str(spec_path),
            "--data-script",
            str(data_script),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == EXIT_USAGE_OR_RUNTIME_ERROR
    assert "Cannot infer format" in capsys.readouterr().err


def test_cli_missing_spec_returns_usage_or_runtime_error(tmp_path, capsys):
    missing_path = tmp_path / "missing.figstudio.json"

    exit_code = main(["codegen", str(missing_path)])

    assert exit_code == EXIT_USAGE_OR_RUNTIME_ERROR
    assert "Spec file not found" in capsys.readouterr().err


def test_cli_render_requires_data_script(tmp_path):
    spec_path = tmp_path / "figure.figstudio.json"
    _write_line_spec(spec_path)

    with pytest.raises(SystemExit) as exc_info:
        main(["render", str(spec_path), "--output", str(tmp_path / "preview.svg")])

    assert exc_info.value.code == EXIT_USAGE_OR_RUNTIME_ERROR

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

import figstudio
from figstudio.codegen import MatplotlibCodegen
from figstudio.validation import validate_figure_spec


GALLERY_DIR = Path(__file__).resolve().parents[1] / "examples" / "gallery"
WORKFLOWS = [
    "faceted_dose_response",
    "secondary_axis_timecourse",
    "spanned_layout_signal_map",
]


def _load_example_module(stem: str):
    module_path = GALLERY_DIR / f"{stem}.py"
    spec = importlib.util.spec_from_file_location(f"_figstudio_gallery_{stem}", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _namespace(module) -> dict[str, object]:
    return {
        name: getattr(module, name)
        for name in ("df", "time", "signal_map", "spectral_power")
        if hasattr(module, name)
    }


def _issue_summary(response) -> str:
    return "\n".join(
        f"{issue.severity}:{issue.code}:{issue.field}:{issue.message}"
        for issue in response.issues
    )


@pytest.mark.parametrize("stem", WORKFLOWS)
def test_gallery_workflow_specs_validate_and_generate(stem: str):
    module = _load_example_module(stem)
    spec = figstudio.load_spec(GALLERY_DIR / f"{stem}.figstudio.json")

    response = validate_figure_spec(_namespace(module), spec)
    assert response.ok, _issue_summary(response)

    code = MatplotlibCodegen().generate(spec)
    assert "import matplotlib.pyplot as plt" in code
    assert "figstudio" not in code.lower()

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

import figstudio
from figstudio.codegen import MatplotlibCodegen
from figstudio.validation import validate_figure_spec


GALLERY_DIR = Path(__file__).resolve().parents[1] / "examples" / "gallery"
GALLERY_ASSET_DIR = Path(__file__).resolve().parents[1] / "docs" / "assets" / "gallery"
STACKED_BAR_WORKFLOW = "stacked_bar_sample_composition"
PREVIEW_ASSETS = {
    "faceted_dose_response": "faceted-dose-response.svg",
    STACKED_BAR_WORKFLOW: "stacked-bar-sample-composition.svg",
    "secondary_axis_timecourse": "secondary-axis-timecourse.svg",
    "spanned_layout_signal_map": "spanned-layout-signal-map.svg",
}
WORKFLOWS = list(PREVIEW_ASSETS)


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


@pytest.mark.parametrize("stem, asset_name", PREVIEW_ASSETS.items())
def test_gallery_preview_assets_are_committed(stem: str, asset_name: str):
    asset_path = GALLERY_ASSET_DIR / asset_name

    assert asset_path.exists(), f"{stem} is missing preview asset {asset_name}"
    assert "<svg" in asset_path.read_text(encoding="utf-8")[:500]


def test_stacked_bar_gallery_workflow_is_svg_export_ready():
    module = _load_example_module(STACKED_BAR_WORKFLOW)
    spec = figstudio.load_spec(GALLERY_DIR / f"{STACKED_BAR_WORKFLOW}.figstudio.json")

    response = validate_figure_spec(_namespace(module), spec, context="export", export_format="svg")
    assert response.ok, _issue_summary(response)
    readiness_issues = [issue for issue in response.issues if issue.code.startswith("readiness_")]
    assert readiness_issues == [], _issue_summary(response)

    code = MatplotlibCodegen().generate(spec)
    assert "groupby(['stage', 'qc_status'], sort=False).size().unstack(fill_value=0)" in code
    assert "bottom=_recipe_stage_composition_bottom" in code

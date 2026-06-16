from __future__ import annotations

import re
from pathlib import Path
from typing import get_args

from figstudio.models import (
    AnnotationSpec,
    AxesSpec,
    DatasetRef,
    FigurePreset,
    FigureSpec,
    FigureStyle,
    LayerStyle,
    PlotKind,
    PlotLayer,
    RenderResponse,
    SaveCodeResponse,
    SessionInfo,
    ValidationIssue,
    ValidationResponse,
    VariableSummary,
)


FRONTEND_TYPES = Path(__file__).resolve().parents[1] / "frontend" / "src" / "types.ts"


def _typescript_source() -> str:
    return FRONTEND_TYPES.read_text(encoding="utf-8")


def _type_literals(source: str, name: str) -> set[str]:
    match = re.search(rf"export type {name}\s*=\s*(?P<body>.*?);", source, re.DOTALL)
    assert match, f"Missing TypeScript type {name}"
    return set(re.findall(r'"([^"]+)"', match.group("body")))


def _interface_fields(source: str, name: str) -> set[str]:
    match = re.search(rf"export interface {name}\s*{{(?P<body>.*?)^}}", source, re.DOTALL | re.MULTILINE)
    assert match, f"Missing TypeScript interface {name}"
    return set(re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\??:", match.group("body"), re.MULTILINE))


def test_frontend_plot_and_preset_literals_match_backend_contracts():
    source = _typescript_source()

    assert _type_literals(source, "PlotKind") == set(get_args(PlotKind))
    assert _type_literals(source, "FigurePreset") == set(get_args(FigurePreset))


def test_frontend_interfaces_cover_backend_model_fields():
    source = _typescript_source()
    model_interfaces = {
        VariableSummary: "VariableSummary",
        DatasetRef: "DatasetRef",
        LayerStyle: "LayerStyle",
        PlotLayer: "PlotLayer",
        AxesSpec: "AxesSpec",
        AnnotationSpec: "AnnotationSpec",
        FigureStyle: "FigureStyle",
        FigureSpec: "FigureSpec",
        SessionInfo: "SessionInfo",
        RenderResponse: "RenderResponse",
        SaveCodeResponse: "SaveCodeResponse",
        ValidationIssue: "ValidationIssue",
        ValidationResponse: "ValidationResponse",
    }

    for model, interface in model_interfaces.items():
        expected = set(model.model_fields)
        actual = _interface_fields(source, interface)
        assert expected <= actual, f"{interface} missing fields: {sorted(expected - actual)}"

"""Import and export helpers for portable FigStudio session specs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from figstudio.models import FigureSpec


def load_spec(path: str | Path) -> FigureSpec:
    """Load a FigureSpec from a .figstudio.json file."""

    source = Path(path)
    return FigureSpec.model_validate_json(source.read_text(encoding="utf-8"))


def save_spec(spec: FigureSpec | dict[str, Any], path: str | Path) -> Path:
    """Save a FigureSpec to a .figstudio.json file and return the output path."""

    output = Path(path)
    figure_spec = spec if isinstance(spec, FigureSpec) else FigureSpec.model_validate(spec)
    output.write_text(figure_spec.model_dump_json(indent=2), encoding="utf-8")
    return output

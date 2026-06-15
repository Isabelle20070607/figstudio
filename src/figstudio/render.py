"""Matplotlib rendering for FigStudio previews and exports."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from figstudio.codegen import MatplotlibCodegen
from figstudio.models import FigureSpec


@dataclass
class RenderEngine:
    namespace: dict[str, Any]
    codegen: MatplotlibCodegen | None = None

    def __post_init__(self) -> None:
        if self.codegen is None:
            self.codegen = MatplotlibCodegen()

    def render_base64(self, spec: FigureSpec, format: str = "svg") -> tuple[str, str]:
        raw = self.render_bytes(spec, format=format)
        if format == "svg":
            return raw.decode("utf-8"), self.codegen.generate(spec)
        return base64.b64encode(raw).decode("ascii"), self.codegen.generate(spec)

    def render_bytes(self, spec: FigureSpec, format: str = "svg", dpi: int | None = None) -> bytes:
        fig = self._execute(spec)
        output = BytesIO()
        fig.savefig(output, format=format, dpi=dpi or spec.dpi)
        plt.close(fig)
        return output.getvalue()

    def export(self, spec: FigureSpec, output_path: str | None, format: str, dpi: int | None = None) -> str | None:
        raw = self.render_bytes(spec, format=format, dpi=dpi)
        if output_path:
            Path(output_path).write_bytes(raw)
            return None
        return base64.b64encode(raw).decode("ascii")

    def _execute(self, spec: FigureSpec):
        code = self.codegen.generate(spec)
        exec_globals = {
            "__builtins__": __builtins__,
            **self.namespace,
        }
        exec_locals: dict[str, Any] = {}
        exec(code, exec_globals, exec_locals)
        fig = exec_locals.get("fig")
        if fig is None:
            raise RuntimeError("Generated Matplotlib code did not create a fig object.")
        return fig

"""Best-effort inspection of existing Matplotlib figures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from figstudio.models import AxesSpec, DatasetRef, FigureSpec, LayerStyle, PlotLayer


@dataclass
class FigureInspector:
    figure: Any

    def extracted_namespace(self) -> dict[str, Any]:
        extracted: dict[str, Any] = {}
        for axis in getattr(self.figure, "axes", []):
            for line in axis.lines:
                index = len(extracted) // 2
                extracted[f"_figstudio_line_{index}_x"] = line.get_xdata()
                extracted[f"_figstudio_line_{index}_y"] = line.get_ydata()
        return extracted

    def tree(self) -> dict[str, Any]:
        axes_nodes = []
        for index, axis in enumerate(getattr(self.figure, "axes", [])):
            axes_nodes.append(
                {
                    "id": f"ax{index}",
                    "title": axis.get_title(),
                    "xlabel": axis.get_xlabel(),
                    "ylabel": axis.get_ylabel(),
                    "lines": [
                        {
                            "label": line.get_label(),
                            "color": line.get_color(),
                            "linestyle": line.get_linestyle(),
                            "marker": line.get_marker(),
                            "readonly": False,
                        }
                        for line in axis.lines
                    ],
                    "images": len(axis.images),
                    "collections": len(axis.collections),
                    "patches": len(axis.patches),
                }
            )
        return {
            "type": type(self.figure).__name__,
            "axes": axes_nodes,
        }

    def to_spec(self) -> FigureSpec:
        width, height = self.figure.get_size_inches()
        axes_specs: list[AxesSpec] = []
        layers: list[PlotLayer] = []
        for index, axis in enumerate(getattr(self.figure, "axes", [])):
            axis_id = f"ax{index}"
            axes_specs.append(
                AxesSpec(
                    id=axis_id,
                    row=index,
                    col=0,
                    title=axis.get_title(),
                    xlabel=axis.get_xlabel(),
                    ylabel=axis.get_ylabel(),
                    xscale=axis.get_xscale(),
                    yscale=axis.get_yscale(),
                    grid=any(line.get_visible() for line in axis.get_xgridlines()),
                    legend=axis.get_legend() is not None,
                )
            )
            for line in axis.lines:
                x_name = f"_figstudio_line_{len(layers)}_x"
                y_name = f"_figstudio_line_{len(layers)}_y"
                layers.append(
                    PlotLayer(
                        id=f"line-{uuid4().hex[:8]}",
                        kind="line",
                        axes_id=axis_id,
                        dataset=DatasetRef(variable=y_name),
                        style=LayerStyle(
                            label=line.get_label() if not line.get_label().startswith("_") else None,
                            color=line.get_color(),
                            marker=line.get_marker(),
                            linestyle=line.get_linestyle(),
                            linewidth=float(line.get_linewidth()),
                            alpha=line.get_alpha(),
                        ),
                        source="inspected",
                    )
                )
        return FigureSpec(
            mode="publish",
            width=float(width),
            height=float(height),
            dpi=int(self.figure.dpi),
            rows=max(1, len(axes_specs)),
            cols=1,
            axes=axes_specs or [AxesSpec()],
            layers=layers,
        )

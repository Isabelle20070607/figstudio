"""Matplotlib code generation from FigureSpec."""

from __future__ import annotations

import keyword
import re
from dataclasses import dataclass

from figstudio.models import AxesSpec, DatasetRef, FigureSpec, PlotLayer


_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _safe_var(name: str) -> str:
    if not _IDENT_RE.match(name) or keyword.iskeyword(name):
        raise ValueError(f"Cannot generate Python code for invalid variable name: {name!r}")
    return name


def _column_expr(variable: str, column: str | None) -> str:
    variable = _safe_var(variable)
    if column:
        return f"{variable}[{column!r}]"
    return variable


def _literal(value: object) -> str:
    return repr(value)


def _kwargs(**kwargs: object) -> str:
    parts = []
    for key, value in kwargs.items():
        if value is None:
            continue
        parts.append(f"{key}={_literal(value)}")
    return ", ".join(parts)


@dataclass
class MatplotlibCodegen:
    """Converts a declarative FigureSpec into plain Matplotlib OO code."""

    include_imports: bool = True

    def generate(self, spec: FigureSpec) -> str:
        lines: list[str] = []
        if self.include_imports:
            lines.extend(["import matplotlib.pyplot as plt", ""])

        layout = (
            f"fig, axes = plt.subplots({spec.rows}, {spec.cols}, "
            f"figsize=({spec.width!r}, {spec.height!r}), dpi={spec.dpi!r}, "
            f"squeeze=False, constrained_layout={spec.style.constrained_layout!r})"
        )
        lines.append(layout)
        lines.append("axes_flat = axes.ravel()")

        if spec.style.font_family:
            lines.append(f"plt.rcParams['font.family'] = {spec.style.font_family!r}")
        if spec.style.font_size:
            lines.append(f"plt.rcParams['font.size'] = {spec.style.font_size!r}")
        if spec.style.title:
            lines.append(f"fig.suptitle({spec.style.title!r})")

        lines.append("")
        axis_lookup = {axis.id: index for index, axis in enumerate(spec.axes)}
        for index, axis in enumerate(spec.axes):
            lines.extend(self._axis_setup(axis, index))
            lines.append("")

        for layer in spec.layers:
            axis_index = axis_lookup.get(layer.axes_id, 0)
            lines.extend(self._layer_code(layer, axis_index))
            lines.append("")

        for annotation in spec.annotations:
            axis_index = axis_lookup.get(annotation.axes_id, 0)
            if annotation.xytext:
                lines.append(
                    f"axes_flat[{axis_index}].annotate({annotation.text!r}, "
                    f"xy=({annotation.x!r}, {annotation.y!r}), "
                    f"xytext={annotation.xytext!r}, arrowprops={{'arrowstyle': '->'}})"
                )
            else:
                lines.append(
                    f"axes_flat[{axis_index}].annotate({annotation.text!r}, "
                    f"xy=({annotation.x!r}, {annotation.y!r}))"
                )
        if spec.annotations:
            lines.append("")

        if spec.show:
            lines.append("plt.show()")

        return "\n".join(lines).rstrip() + "\n"

    def notebook_cell(self, spec: FigureSpec) -> str:
        return self.generate(spec)

    def _axis_setup(self, axis: AxesSpec, index: int) -> list[str]:
        prefix = f"axes_flat[{index}]"
        lines = [f"{prefix}.set_title({axis.title!r})" if axis.title else ""]
        if axis.xlabel:
            lines.append(f"{prefix}.set_xlabel({axis.xlabel!r})")
        if axis.ylabel:
            lines.append(f"{prefix}.set_ylabel({axis.ylabel!r})")
        if axis.xscale != "linear":
            lines.append(f"{prefix}.set_xscale({axis.xscale!r})")
        if axis.yscale != "linear":
            lines.append(f"{prefix}.set_yscale({axis.yscale!r})")
        if axis.xlim:
            lines.append(f"{prefix}.set_xlim({axis.xlim!r})")
        if axis.ylim:
            lines.append(f"{prefix}.set_ylim({axis.ylim!r})")
        if axis.grid:
            lines.append(f"{prefix}.grid(True, alpha=0.25)")
        return [line for line in lines if line]

    def _layer_code(self, layer: PlotLayer, axis_index: int) -> list[str]:
        data = layer.dataset
        style = layer.style
        ax = f"axes_flat[{axis_index}]"
        label = style.label
        common = {
            "label": label,
            "color": style.color,
            "alpha": style.alpha,
        }
        line_common = {
            **common,
            "marker": style.marker,
            "linestyle": style.linestyle,
            "linewidth": style.linewidth,
        }

        call = ""
        if layer.kind == "line":
            call = f"{ax}.plot({self._xy(data)}, {_kwargs(**line_common)})"
        elif layer.kind == "scatter":
            call = f"{ax}.scatter({self._xy(data)}, {_kwargs(**common, marker=style.marker)})"
        elif layer.kind == "bar":
            call = f"{ax}.bar({self._xy(data)}, {_kwargs(**common)})"
        elif layer.kind == "barh":
            call = f"{ax}.barh({self._xy(data)}, {_kwargs(**common)})"
        elif layer.kind == "hist":
            call = (
                f"{ax}.hist({_column_expr(data.variable, data.y or data.x)}, "
                f"{_kwargs(bins=style.bins or 30, label=label, color=style.color, alpha=style.alpha)})"
            )
        elif layer.kind == "boxplot":
            call = f"{ax}.boxplot({_column_expr(data.variable, data.y or data.x)})"
        elif layer.kind == "violin":
            call = f"{ax}.violinplot({_column_expr(data.variable, data.y or data.x)}, showmeans=True)"
        elif layer.kind == "errorbar":
            yerr = _column_expr(data.variable, data.yerr) if data.yerr else "None"
            call = f"{ax}.errorbar({self._xy(data)}, yerr={yerr}, {_kwargs(**line_common)})"
        elif layer.kind == "heatmap":
            call = f"image_{layer.id.replace('-', '_')} = {ax}.imshow({_column_expr(data.variable, data.z or data.y or data.x)}, cmap={style.cmap or 'viridis'!r})"
        elif layer.kind == "contour":
            if data.x and data.y and data.z:
                call = (
                    f"contour_{layer.id.replace('-', '_')} = {ax}.contour("
                    f"{_column_expr(data.variable, data.x)}, {_column_expr(data.variable, data.y)}, "
                    f"{_column_expr(data.variable, data.z)}, cmap={style.cmap or 'viridis'!r})"
                )
            else:
                call = (
                    f"contour_{layer.id.replace('-', '_')} = {ax}.contour("
                    f"{_column_expr(data.variable, data.z or data.y or data.x)}, "
                    f"cmap={style.cmap or 'viridis'!r})"
                )
        elif layer.kind == "step":
            call = f"{ax}.step({self._xy(data)}, where='mid', {_kwargs(**line_common)})"
        elif layer.kind == "fill_between":
            call = (
                f"{ax}.fill_between({self._xy(data)}, "
                f"{_kwargs(label=label, color=style.color, alpha=style.fill_alpha or style.alpha or 0.3)})"
            )
        else:
            raise ValueError(f"Unsupported plot kind: {layer.kind}")

        lines = [call.replace(", )", ")").replace("(, ", "(")]
        if label and layer.kind not in {"heatmap", "contour"}:
            lines.append(f"{ax}.legend()")
        if layer.kind == "heatmap":
            lines.append(f"fig.colorbar(image_{layer.id.replace('-', '_')}, ax={ax})")
        if layer.kind == "contour":
            lines.append(f"{ax}.clabel(contour_{layer.id.replace('-', '_')}, inline=True, fontsize=8)")
        return lines

    def _xy(self, data: DatasetRef) -> str:
        x_expr = _column_expr(data.variable, data.x) if data.x else "range(len(" + _column_expr(data.variable, data.y) + "))"
        y_expr = _column_expr(data.variable, data.y)
        return f"{x_expr}, {y_expr}"

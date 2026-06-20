"""Matplotlib code generation from FigureSpec."""

from __future__ import annotations

import keyword
import re
from dataclasses import dataclass

from figstudio.models import (
    AxesSpec,
    DatasetRef,
    FigureSpec,
    LayerStyle,
    PlotLayer,
    RecipeDatasetRef,
    RecipeLayer,
    ReferenceLineSpec,
    StyleProfile,
)
from figstudio.selection import python_literal_key
from figstudio.style_profiles import (
    resolved_figure_value,
    resolved_layer_style,
    resolved_recipe_style,
)


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
    style_profiles: dict[str, StyleProfile] | None = None

    def generate(self, spec: FigureSpec) -> str:
        lines: list[str] = []
        if self.include_imports:
            lines.extend(["import matplotlib.pyplot as plt", ""])

        rc_params: dict[str, object] = {}
        font_family = resolved_figure_value(spec, self.style_profiles, "font_family")
        font_size = resolved_figure_value(spec, self.style_profiles, "font_size")
        if font_family:
            rc_params["font.family"] = font_family
        if font_size:
            rc_params["font.size"] = font_size

        body = self._figure_body(spec)
        if rc_params:
            lines.append(f"with plt.rc_context({_literal(rc_params)}):")
            lines.extend(f"    {line}" if line else "" for line in body)
        else:
            lines.extend(body)

        return "\n".join(lines).rstrip() + "\n"

    def _figure_body(self, spec: FigureSpec) -> list[str]:
        lines: list[str] = []
        width = resolved_figure_value(spec, self.style_profiles, "width")
        height = resolved_figure_value(spec, self.style_profiles, "height")
        dpi = resolved_figure_value(spec, self.style_profiles, "dpi")
        constrained_layout = resolved_figure_value(spec, self.style_profiles, "constrained_layout")

        if _uses_dense_subplots(spec):
            layout = (
                f"fig, axes = plt.subplots({spec.rows}, {spec.cols}, "
                f"figsize=({width!r}, {height!r}), dpi={dpi!r}, "
                f"squeeze=False, sharex={spec.share_x!r}, sharey={spec.share_y!r}, "
                f"constrained_layout={constrained_layout!r})"
            )
            lines.append(layout)
            lines.append("axes_flat = axes.ravel()")
        else:
            lines.append(
                f"fig = plt.figure(figsize=({width!r}, {height!r}), "
                f"dpi={dpi!r}, constrained_layout={constrained_layout!r})"
            )
            lines.append(f"grid = fig.add_gridspec({spec.rows}, {spec.cols})")
            lines.append("axes_flat = [")
            for axis in spec.axes:
                lines.append(f"    fig.add_subplot({_grid_slice(axis)}),")
            lines.append("]")

        if spec.style.title:
            lines.append(f"fig.suptitle({spec.style.title!r})")

        lines.append("")
        axis_lookup = {axis.id: index for index, axis in enumerate(spec.axes)}
        for index, axis in enumerate(spec.axes):
            lines.extend(self._axis_setup(axis, index))
            lines.append("")

        secondary_axis_indices = self._secondary_axis_indices(spec, axis_lookup)
        if secondary_axis_indices:
            lines.append("secondary_axes = {}")
            for axis_index in sorted(secondary_axis_indices):
                lines.extend(self._secondary_axis_setup(spec.axes[axis_index], axis_index))
            lines.append("")

        legend_axes: set[int] = set()
        for layer in spec.layers:
            axis_index = axis_lookup.get(layer.axes_id, 0)
            style = resolved_layer_style(spec, layer, self.style_profiles)
            filter_lines, filtered_layer = self._filtered_layer(layer)
            lines.extend(filter_lines)
            axis_expr = self._layer_axis_expr(filtered_layer, axis_index)
            lines.extend(self._layer_code(filtered_layer, style, axis_expr, spec.axes[axis_index]))
            if style.label and layer.kind not in {"heatmap", "contour"}:
                legend_axes.add(axis_index)
            lines.append("")

        for recipe in spec.recipes:
            axis_index = axis_lookup.get(recipe.axes_id, 0)
            style = resolved_recipe_style(spec, recipe, self.style_profiles)
            filter_lines, filtered_recipe = self._filtered_recipe(recipe)
            lines.extend(filter_lines)
            lines.extend(self._recipe_code(filtered_recipe, style, axis_index))
            if style.label:
                legend_axes.add(axis_index)
            lines.append("")

        for reference_line in spec.reference_lines:
            axis_index = axis_lookup.get(reference_line.axes_id, 0)
            lines.extend(self._reference_line_code(reference_line, axis_index))
            if reference_line.style.label:
                legend_axes.add(axis_index)
            lines.append("")

        for axis_index in sorted(legend_axes):
            if spec.axes[axis_index].legend:
                if axis_index in secondary_axis_indices:
                    lines.extend(self._combined_legend_code(axis_index))
                else:
                    lines.append(f"axes_flat[{axis_index}].legend()")
        if legend_axes:
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

        return lines

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

    def _secondary_axis_indices(self, spec: FigureSpec, axis_lookup: dict[str, int]) -> set[int]:
        if not spec.axes:
            return set()
        return {
            axis_lookup.get(layer.axes_id, 0)
            for layer in spec.layers
            if layer.y_axis == "right" and axis_lookup.get(layer.axes_id, 0) < len(spec.axes)
        }

    def _secondary_axis_setup(self, axis: AxesSpec, index: int) -> list[str]:
        prefix = f"secondary_axes[{index}]"
        secondary = axis.secondary_y
        lines = [f"{prefix} = axes_flat[{index}].twinx()"]
        if secondary.ylabel:
            lines.append(f"{prefix}.set_ylabel({secondary.ylabel!r})")
        if secondary.yscale != "linear":
            lines.append(f"{prefix}.set_yscale({secondary.yscale!r})")
        if secondary.ylim:
            lines.append(f"{prefix}.set_ylim({secondary.ylim!r})")
        return lines

    def _layer_axis_expr(self, layer: PlotLayer, axis_index: int) -> str:
        if layer.y_axis == "right":
            return f"secondary_axes[{axis_index}]"
        return f"axes_flat[{axis_index}]"

    def _combined_legend_code(self, axis_index: int) -> list[str]:
        return [
            f"primary_handles_{axis_index}, primary_labels_{axis_index} = "
            f"axes_flat[{axis_index}].get_legend_handles_labels()",
            f"secondary_handles_{axis_index}, secondary_labels_{axis_index} = "
            f"secondary_axes[{axis_index}].get_legend_handles_labels()",
            (
                f"axes_flat[{axis_index}].legend("
                f"primary_handles_{axis_index} + secondary_handles_{axis_index}, "
                f"primary_labels_{axis_index} + secondary_labels_{axis_index})"
            ),
        ]

    def _layer_code(self, layer: PlotLayer, style: LayerStyle, ax: str, axis: AxesSpec) -> list[str]:
        data = layer.dataset
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
                f"{ax}.hist({self._value(data)}, "
                f"{_kwargs(bins=style.bins or 30, label=label, color=style.color, alpha=style.alpha)})"
            )
        elif layer.kind == "boxplot":
            call = f"{ax}.boxplot({self._value(data)})"
        elif layer.kind == "violin":
            call = f"{ax}.violinplot({self._value(data)}, showmeans=True)"
        elif layer.kind == "errorbar":
            yerr = self._channel(data, "yerr") if data.yerr or data.yerr_variable else "None"
            call = f"{ax}.errorbar({self._xy(data)}, yerr={yerr}, {_kwargs(**line_common)})"
        elif layer.kind == "heatmap":
            call = f"image_{layer.id.replace('-', '_')} = {ax}.imshow({self._z(data)}, cmap={style.cmap or 'viridis'!r})"
        elif layer.kind == "contour":
            if (data.x or data.x_variable) and (data.y or data.y_variable) and (data.z or data.z_variable):
                call = (
                    f"contour_{layer.id.replace('-', '_')} = {ax}.contour("
                    f"{self._channel(data, 'x')}, {self._channel(data, 'y')}, "
                    f"{self._channel(data, 'z')}, cmap={style.cmap or 'viridis'!r})"
                )
            else:
                call = (
                    f"contour_{layer.id.replace('-', '_')} = {ax}.contour("
                    f"{self._z(data)}, "
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
        if layer.kind == "heatmap":
            if style.colorbar is not False:
                lines.append(f"fig.colorbar(image_{layer.id.replace('-', '_')}, ax={ax})")
        if layer.kind == "contour":
            contour_name = f"contour_{layer.id.replace('-', '_')}"
            show_colorbar = style.colorbar if style.colorbar is not None else axis.colorbar
            if show_colorbar:
                lines.append(f"fig.colorbar({contour_name}, ax={ax})")
            lines.append(f"{ax}.clabel({contour_name}, inline=True, fontsize=8)")
        return lines

    def _recipe_code(self, recipe: RecipeLayer, style: LayerStyle, axis_index: int) -> list[str]:
        if recipe.kind == "mean_sem_line":
            return self._mean_sem_line_code(recipe, style, axis_index)
        if recipe.kind == "mean_sem_bar":
            return self._mean_sem_bar_code(recipe, style, axis_index)
        if recipe.kind == "count_bar":
            return self._count_bar_code(recipe, style, axis_index)
        if recipe.kind == "grouped_points":
            return self._grouped_points_code(recipe, style, axis_index)
        if recipe.kind == "paired_before_after":
            return self._paired_before_after_code(recipe, style, axis_index)
        raise ValueError(f"Unsupported recipe kind: {recipe.kind}")

    def _reference_line_code(self, reference_line: ReferenceLineSpec, axis_index: int) -> list[str]:
        ax = f"axes_flat[{axis_index}]"
        method = "axhline" if reference_line.orientation == "horizontal" else "axvline"
        style = reference_line.style
        kwargs = _kwargs(
            label=style.label,
            color=style.color,
            linestyle=style.linestyle,
            linewidth=style.linewidth,
            alpha=style.alpha,
        )
        return [f"{ax}.{method}({reference_line.value!r}, {kwargs})".replace(", )", ")")]

    def _mean_sem_line_code(self, recipe: RecipeLayer, style: LayerStyle, axis_index: int) -> list[str]:
        data = recipe.dataset
        var = _safe_var(data.variable)
        prefix = self._recipe_prefix(recipe)
        ax = f"axes_flat[{axis_index}]"
        stat = self._recipe_error_stat(recipe)
        yerr = f"{prefix}_summary[{stat!r}]" if stat else "None"
        agg = "['mean', " + repr(stat) + "]" if stat else "['mean']"
        kwargs = self._recipe_line_kwargs(style)

        lines = [
            f"{prefix}_df = {var}",
            f"{prefix}_x_order = list(dict.fromkeys({prefix}_df[{data.x!r}].dropna().tolist()))",
        ]
        if data.group:
            lines.extend(
                [
                    f"{prefix}_groups = list(dict.fromkeys({prefix}_df[{data.group!r}].dropna().tolist()))",
                    f"for {prefix}_group in {prefix}_groups:",
                    f"    {prefix}_group_df = {prefix}_df[{prefix}_df[{data.group!r}] == {prefix}_group]",
                    (
                        f"    {prefix}_summary = {prefix}_group_df.groupby({data.x!r}, sort=False)"
                        f"[{data.y!r}].agg({agg}).reindex({prefix}_x_order)"
                    ),
                    (
                        f"    {ax}.errorbar({prefix}_x_order, {prefix}_summary['mean'], "
                        f"yerr={yerr}, label=f'{style.label or data.y} {{{prefix}_group}}', "
                        f"{kwargs})"
                    ),
                ]
            )
        else:
            lines.extend(
                [
                    (
                        f"{prefix}_summary = {prefix}_df.groupby({data.x!r}, sort=False)"
                        f"[{data.y!r}].agg({agg}).reindex({prefix}_x_order)"
                    ),
                    (
                        f"{ax}.errorbar({prefix}_x_order, {prefix}_summary['mean'], "
                        f"yerr={yerr}, {_kwargs(label=style.label, **self._line_style(style))})"
                    ),
                ]
            )
        return [line.replace(", )", ")").replace("(, ", "(") for line in lines]

    def _mean_sem_bar_code(self, recipe: RecipeLayer, style: LayerStyle, axis_index: int) -> list[str]:
        data = recipe.dataset
        var = _safe_var(data.variable)
        prefix = self._recipe_prefix(recipe)
        ax = f"axes_flat[{axis_index}]"
        stat = self._recipe_error_stat(recipe)
        agg = "['mean', " + repr(stat) + "]" if stat else "['mean']"
        yerr = f"{prefix}_summary[{stat!r}]" if stat else "None"
        bar_kwargs = _kwargs(
            color=style.color,
            alpha=style.alpha if style.alpha is not None else 0.85,
            linewidth=style.linewidth,
        )

        lines = [
            f"{prefix}_df = {var}",
            f"{prefix}_x_order = list(dict.fromkeys({prefix}_df[{data.x!r}].dropna().tolist()))",
            f"{prefix}_x = list(range(len({prefix}_x_order)))",
        ]
        if data.group:
            lines.extend(
                [
                    f"{prefix}_groups = list(dict.fromkeys({prefix}_df[{data.group!r}].dropna().tolist()))",
                    f"{prefix}_bar_width = 0.8 / max(len({prefix}_groups), 1)",
                    f"for {prefix}_group_index, {prefix}_group in enumerate({prefix}_groups):",
                    f"    {prefix}_group_df = {prefix}_df[{prefix}_df[{data.group!r}] == {prefix}_group]",
                    (
                        f"    {prefix}_summary = {prefix}_group_df.groupby({data.x!r}, sort=False)"
                        f"[{data.y!r}].agg({agg}).reindex({prefix}_x_order)"
                    ),
                    (
                        f"    {prefix}_offset = "
                        f"({prefix}_group_index - (len({prefix}_groups) - 1) / 2) * {prefix}_bar_width"
                    ),
                    f"    {prefix}_positions = [value + {prefix}_offset for value in {prefix}_x]",
                    (
                        f"    {ax}.bar({prefix}_positions, {prefix}_summary['mean'], yerr={yerr}, "
                        f"width={prefix}_bar_width, label=f'{style.label or data.y} {{{prefix}_group}}', "
                        f"capsize=4, {bar_kwargs})"
                    ),
                ]
            )
        else:
            lines.extend(
                [
                    (
                        f"{prefix}_summary = {prefix}_df.groupby({data.x!r}, sort=False)"
                        f"[{data.y!r}].agg({agg}).reindex({prefix}_x_order)"
                    ),
                    (
                        f"{ax}.bar({prefix}_x, {prefix}_summary['mean'], yerr={yerr}, width=0.72, "
                        f"label={style.label!r}, capsize=4, {bar_kwargs})"
                    ),
                ]
            )
        lines.extend(
            [
                f"{ax}.set_xticks({prefix}_x)",
                f"{ax}.set_xticklabels([str(value) for value in {prefix}_x_order])",
            ]
        )
        return [line.replace(", )", ")").replace("(, ", "(") for line in lines]

    def _count_bar_code(self, recipe: RecipeLayer, style: LayerStyle, axis_index: int) -> list[str]:
        data = recipe.dataset
        var = _safe_var(data.variable)
        prefix = self._recipe_prefix(recipe)
        ax = f"axes_flat[{axis_index}]"
        label_base = style.label or "Count"
        bar_kwargs = _kwargs(
            color=style.color,
            alpha=style.alpha if style.alpha is not None else 0.85,
            linewidth=style.linewidth,
        )

        lines = [
            f"{prefix}_df = {var}",
            f"{prefix}_x_order = list(dict.fromkeys({prefix}_df[{data.x!r}].dropna().tolist()))",
            f"{prefix}_x = list(range(len({prefix}_x_order)))",
        ]
        if data.group:
            lines.extend(
                [
                    f"{prefix}_groups = list(dict.fromkeys({prefix}_df[{data.group!r}].dropna().tolist()))",
                    (
                        f"{prefix}_counts = {prefix}_df.groupby([{data.x!r}, {data.group!r}], "
                        "sort=False).size().unstack(fill_value=0)"
                    ),
                    f"{prefix}_counts = {prefix}_counts.reindex(index={prefix}_x_order, fill_value=0)",
                    f"{prefix}_counts = {prefix}_counts.reindex(columns={prefix}_groups, fill_value=0)",
                    f"{prefix}_bar_width = 0.8 / max(len({prefix}_groups), 1)",
                    f"for {prefix}_group_index, {prefix}_group in enumerate({prefix}_groups):",
                    (
                        f"    {prefix}_offset = "
                        f"({prefix}_group_index - (len({prefix}_groups) - 1) / 2) * {prefix}_bar_width"
                    ),
                    f"    {prefix}_positions = [value + {prefix}_offset for value in {prefix}_x]",
                    (
                        f"    {ax}.bar({prefix}_positions, {prefix}_counts[{prefix}_group], "
                        f"width={prefix}_bar_width, label=f'{label_base} {{{prefix}_group}}', "
                        f"{bar_kwargs})"
                    ),
                ]
            )
        else:
            lines.extend(
                [
                    (
                        f"{prefix}_counts = {prefix}_df.groupby({data.x!r}, sort=False)"
                        f".size().reindex({prefix}_x_order, fill_value=0)"
                    ),
                    (
                        f"{ax}.bar({prefix}_x, {prefix}_counts, width=0.72, "
                        f"label={style.label!r}, {bar_kwargs})"
                    ),
                ]
            )
        lines.extend(
            [
                f"{ax}.set_xticks({prefix}_x)",
                f"{ax}.set_xticklabels([str(value) for value in {prefix}_x_order])",
            ]
        )
        return [line.replace(", )", ")").replace("(, ", "(") for line in lines]

    def _grouped_points_code(self, recipe: RecipeLayer, style: LayerStyle, axis_index: int) -> list[str]:
        data = recipe.dataset
        var = _safe_var(data.variable)
        prefix = self._recipe_prefix(recipe)
        ax = f"axes_flat[{axis_index}]"
        stat = self._recipe_error_stat(recipe)
        point_kwargs = _kwargs(color=style.color, marker=style.marker, alpha=style.alpha)
        mean_kwargs = _kwargs(color=style.color, linewidth=style.linewidth or 1.8)

        lines = [
            f"{prefix}_df = {var}",
            f"{prefix}_order = list(dict.fromkeys({prefix}_df[{data.x!r}].dropna().tolist()))",
            f"{prefix}_positions = {{value: index for index, value in enumerate({prefix}_order)}}",
            f"for {prefix}_category in {prefix}_order:",
            f"    {prefix}_values = {prefix}_df.loc[{prefix}_df[{data.x!r}] == {prefix}_category, {data.y!r}].dropna()",
            (
                f"    {prefix}_offsets = [((index % 7) - 3) * 0.035 "
                f"for index in range(len({prefix}_values))]"
            ),
            (
                f"    {prefix}_x = [{prefix}_positions[{prefix}_category] + offset "
                f"for offset in {prefix}_offsets]"
            ),
            f"    {ax}.scatter({prefix}_x, {prefix}_values, {point_kwargs})",
            f"    if len({prefix}_values):",
            f"        {prefix}_mean = {prefix}_values.mean()",
            (
                f"        {ax}.hlines({prefix}_mean, {prefix}_positions[{prefix}_category] - 0.22, "
                f"{prefix}_positions[{prefix}_category] + 0.22, {mean_kwargs})"
            ),
        ]
        if stat:
            lines.extend(
                [
                    f"        {prefix}_error = {prefix}_values.{stat}()",
                    (
                        f"        {ax}.errorbar([{prefix}_positions[{prefix}_category]], "
                        f"[{prefix}_mean], yerr=[{prefix}_error], fmt='none', "
                        f"ecolor={style.color!r}, capsize=4)"
                    ),
                ]
            )
        lines.extend(
            [
                f"{ax}.set_xticks(list({prefix}_positions.values()))",
                f"{ax}.set_xticklabels([str(value) for value in {prefix}_order])",
            ]
        )
        if style.label:
            lines.append(f"{ax}.scatter([], [], label={style.label!r}, {point_kwargs})")
        return [line.replace(", )", ")").replace("(, ", "(") for line in lines]

    def _paired_before_after_code(self, recipe: RecipeLayer, style: LayerStyle, axis_index: int) -> list[str]:
        data = recipe.dataset
        var = _safe_var(data.variable)
        prefix = self._recipe_prefix(recipe)
        ax = f"axes_flat[{axis_index}]"
        stat = self._recipe_error_stat(recipe)
        yerr = f"{prefix}_summary[{stat!r}]" if stat else "None"
        agg = "['mean', " + repr(stat) + "]" if stat else "['mean']"
        subject_kwargs = _kwargs(
            color=style.color,
            marker=style.marker,
            linewidth=style.linewidth or 1.0,
            alpha=style.alpha if style.alpha is not None else 0.35,
        )
        summary_kwargs = _kwargs(
            label=style.label,
            color=style.color,
            marker=style.marker or "o",
            linewidth=(style.linewidth or 1.8) + 0.4,
            alpha=1.0,
        )

        lines = [
            f"{prefix}_df = {var}",
            f"{prefix}_order = list(dict.fromkeys({prefix}_df[{data.x!r}].dropna().tolist()))",
            f"{prefix}_x = list(range(len({prefix}_order)))",
            f"{prefix}_subjects = list(dict.fromkeys({prefix}_df[{data.subject!r}].dropna().tolist()))",
            f"for {prefix}_subject in {prefix}_subjects:",
            f"    {prefix}_subject_df = {prefix}_df[{prefix}_df[{data.subject!r}] == {prefix}_subject]",
            (
                f"    {prefix}_paired = {prefix}_subject_df.groupby({data.x!r}, sort=False)"
                f"[{data.y!r}].mean().reindex({prefix}_order)"
            ),
            f"    {ax}.plot({prefix}_x, {prefix}_paired.tolist(), {subject_kwargs})",
            (
                f"{prefix}_summary = {prefix}_df.groupby({data.x!r}, sort=False)"
                f"[{data.y!r}].agg({agg}).reindex({prefix}_order)"
            ),
            (
                f"{ax}.errorbar({prefix}_x, {prefix}_summary['mean'], yerr={yerr}, "
                f"{summary_kwargs})"
            ),
            f"{ax}.set_xticks({prefix}_x)",
            f"{ax}.set_xticklabels([str(value) for value in {prefix}_order])",
        ]
        return [line.replace(", )", ")").replace("(, ", "(") for line in lines]

    def _recipe_prefix(self, recipe: RecipeLayer) -> str:
        return f"_recipe_{recipe.id.replace('-', '_')}"

    def _filtered_layer(self, layer: PlotLayer) -> tuple[list[str], PlotLayer]:
        lines, dataset = _filter_dataset(layer.dataset, f"_layer_{layer.id.replace('-', '_')}")
        if not lines:
            return [], layer
        return lines, layer.model_copy(update={"dataset": dataset})

    def _filtered_recipe(self, recipe: RecipeLayer) -> tuple[list[str], RecipeLayer]:
        lines, dataset = _filter_dataset(recipe.dataset, self._recipe_prefix(recipe))
        if not lines:
            return [], recipe
        return lines, recipe.model_copy(update={"dataset": dataset})

    def _recipe_error_stat(self, recipe: RecipeLayer) -> str | None:
        if recipe.error == "sem":
            return "sem"
        if recipe.error == "sd":
            return "std"
        return None

    def _line_style(self, style: LayerStyle) -> dict[str, object]:
        return {
            "color": style.color,
            "marker": style.marker,
            "linestyle": style.linestyle,
            "linewidth": style.linewidth,
            "alpha": style.alpha,
        }

    def _recipe_line_kwargs(self, style: LayerStyle) -> str:
        return _kwargs(**self._line_style(style))

    def _xy(self, data: DatasetRef) -> str:
        y_expr = self._value(data)
        x_expr = self._channel(data, "x") if data.x or data.x_variable else f"range(len({y_expr}))"
        return f"{x_expr}, {y_expr}"

    def _value(self, data: DatasetRef) -> str:
        if data.y or data.y_variable:
            return self._channel(data, "y")
        return _column_expr(data.variable, None)

    def _z(self, data: DatasetRef) -> str:
        if data.z or data.z_variable:
            return self._channel(data, "z")
        return self._value(data)

    def _channel(self, data: DatasetRef, channel: str) -> str:
        channel_variable = getattr(data, f"{channel}_variable")
        column = getattr(data, channel)
        variable = channel_variable or data.variable
        return _column_expr(variable, column)


def _uses_dense_subplots(spec: FigureSpec) -> bool:
    if spec.rows < 1 or spec.cols < 1:
        return False
    if len(spec.axes) != spec.rows * spec.cols:
        return False
    expected_positions = [(row, col) for row in range(spec.rows) for col in range(spec.cols)]
    for axis, (row, col) in zip(spec.axes, expected_positions):
        if axis.row != row or axis.col != col:
            return False
        if axis.rowspan != 1 or axis.colspan != 1:
            return False
    return True


def _filter_dataset(
    data: DatasetRef | RecipeDatasetRef,
    prefix: str,
) -> tuple[list[str], DatasetRef | RecipeDatasetRef]:
    source_var = _safe_var(data.variable)
    current_var = source_var
    lines: list[str] = []
    update: dict[str, object] = {}
    selection = getattr(data, "selection", None)
    if selection is not None:
        selected_var = f"{prefix}_selected"
        if selection.kind == "mapping_key":
            lines.append(f"{selected_var} = {source_var}[{python_literal_key(selection.key)}]")
        elif selection.kind == "sequence_index":
            lines.append(f"{selected_var} = {source_var}[{selection.index!r}]")
        current_var = selected_var
        update["selection"] = None

    if data.filters:
        filtered_var = f"{prefix}_filtered_df"
        lines.append(f"{filtered_var} = {current_var}")
        current_var = filtered_var
        update["filters"] = []
    for data_filter in data.filters:
        if data_filter.op != "eq":
            continue
        column = data_filter.column
        if data_filter.value is None:
            lines.append(f"{current_var} = {current_var}[{current_var}[{column!r}].isna()]")
        else:
            lines.append(
                f"{current_var} = {current_var}[{current_var}[{column!r}] == "
                f"{data_filter.value!r}]"
            )
    if not lines:
        return [], data
    update["variable"] = current_var
    return lines, data.model_copy(update=update)


def _grid_slice(axis: AxesSpec) -> str:
    row = _slice_part(axis.row, axis.rowspan)
    col = _slice_part(axis.col, axis.colspan)
    return f"grid[{row}, {col}]"


def _slice_part(start: int, span: int) -> str:
    if span == 1:
        return repr(start)
    return f"{start}:{start + span}"

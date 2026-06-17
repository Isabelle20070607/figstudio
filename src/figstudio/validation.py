"""Pre-render validation for FigureSpec objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from figstudio.models import (
    AxesSpec,
    DatasetRef,
    FigureSpec,
    PlotLayer,
    RecipeLayer,
    StyleProfile,
    ValidationIssue,
    ValidationResponse,
)
from figstudio.style_profiles import missing_profile_issue_details


@dataclass
class _ResolvedValue:
    value: Any
    label: str


def validate_figure_spec(
    namespace: dict[str, Any],
    spec: FigureSpec,
    style_profiles: dict[str, StyleProfile] | None = None,
) -> ValidationResponse:
    issues: list[ValidationIssue] = []
    profile_details = missing_profile_issue_details(spec, style_profiles)
    if profile_details is not None:
        issues.append(
            ValidationIssue(
                severity="warning",
                code="missing_style_profile",
                message=f"Style profile {spec.style.profile_id!r} is not available in this project.",
                field="style.profile_id",
                details=profile_details,
            )
        )
    _validate_axes_layout(spec, issues)
    axes_by_id = {axis.id: axis for axis in spec.axes}

    for layer in spec.layers:
        if layer.axes_id not in axes_by_id:
            issues.append(
                ValidationIssue(
                    code="missing_axes",
                    message=f"Layer {layer.id!r} targets missing axes {layer.axes_id!r}.",
                    layer_id=layer.id,
                    axes_id=layer.axes_id,
                    field="axes_id",
                )
            )
            continue

        axis = axes_by_id[layer.axes_id]
        y_value = _resolve_value(namespace, layer, "y", issues)
        x_value = _resolve_channel(namespace, layer, "x", issues)
        z_value = _resolve_z(namespace, layer, issues)
        yerr_value = _resolve_channel(namespace, layer, "yerr", issues)

        if layer.kind in {"line", "scatter", "bar", "barh", "step", "fill_between", "errorbar"}:
            _check_lengths(layer, issues, x=x_value, y=y_value)
        if layer.kind == "errorbar":
            _check_lengths(layer, issues, y=y_value, yerr=yerr_value)
        if layer.kind in {"heatmap", "contour"}:
            _check_two_dimensional(layer, issues, z_value)

        if axis.xscale == "log" and x_value is not None:
            _check_positive(layer, issues, x_value, "x")
        if axis.yscale == "log" and y_value is not None and layer.kind not in {"heatmap", "contour"}:
            _check_positive(layer, issues, y_value, "y")

    for recipe in spec.recipes:
        if recipe.axes_id not in axes_by_id:
            issues.append(
                ValidationIssue(
                    code="missing_axes",
                    message=f"Recipe {recipe.id!r} targets missing axes {recipe.axes_id!r}.",
                    layer_id=recipe.id,
                    axes_id=recipe.axes_id,
                    field="axes_id",
                )
            )
            continue
        _validate_recipe(namespace, recipe, issues)

    return ValidationResponse(ok=not any(issue.severity == "error" for issue in issues), issues=issues)


def _validate_axes_layout(spec: FigureSpec, issues: list[ValidationIssue]) -> None:
    if spec.rows < 1:
        issues.append(
            ValidationIssue(
                code="invalid_grid_size",
                message=f"FigureSpec rows must be positive; got {spec.rows}.",
                field="rows",
                details={"rows": spec.rows, "cols": spec.cols},
            )
        )
    if spec.cols < 1:
        issues.append(
            ValidationIssue(
                code="invalid_grid_size",
                message=f"FigureSpec cols must be positive; got {spec.cols}.",
                field="cols",
                details={"rows": spec.rows, "cols": spec.cols},
            )
        )
    if spec.rows < 1 or spec.cols < 1:
        return

    seen_ids: set[str] = set()
    duplicate_ids: set[str] = set()
    occupied: dict[tuple[int, int], str] = {}
    overlaps: list[dict[str, Any]] = []

    for axis in spec.axes:
        if axis.id in seen_ids:
            duplicate_ids.add(axis.id)
        seen_ids.add(axis.id)

        if axis.rowspan < 1 or axis.colspan < 1:
            _append_invalid_span(axis, issues)
            continue

        row_end = axis.row + axis.rowspan
        col_end = axis.col + axis.colspan
        if axis.row < 0 or axis.col < 0 or row_end > spec.rows or col_end > spec.cols:
            issues.append(
                ValidationIssue(
                    code="axes_out_of_bounds",
                    message=(
                        f"Axes {axis.id!r} spans rows {axis.row}:{row_end} and "
                        f"cols {axis.col}:{col_end}, outside a {spec.rows}x{spec.cols} grid."
                    ),
                    axes_id=axis.id,
                    field="axes",
                    details=_axis_layout_details(axis) | {"rows": spec.rows, "cols": spec.cols},
                )
            )
            continue

        for row in range(axis.row, row_end):
            for col in range(axis.col, col_end):
                cell = (row, col)
                owner = occupied.get(cell)
                if owner is not None:
                    overlaps.append(
                        {
                            "row": row,
                            "col": col,
                            "axes": [owner, axis.id],
                        }
                    )
                else:
                    occupied[cell] = axis.id

    for axis_id in sorted(duplicate_ids):
        issues.append(
            ValidationIssue(
                code="duplicate_axes_id",
                message=f"Axes id {axis_id!r} is used more than once.",
                axes_id=axis_id,
                field="axes.id",
                details={"axes_id": axis_id},
            )
        )

    for overlap in overlaps:
        issues.append(
            ValidationIssue(
                code="axes_overlap",
                message=(
                    f"Axes {overlap['axes'][0]!r} and {overlap['axes'][1]!r} "
                    f"both occupy cell ({overlap['row'] + 1}, {overlap['col'] + 1})."
                ),
                axes_id=overlap["axes"][1],
                field="axes",
                details=overlap,
            )
        )


def _append_invalid_span(axis: AxesSpec, issues: list[ValidationIssue]) -> None:
    if axis.rowspan < 1:
        issues.append(
            ValidationIssue(
                code="invalid_axes_span",
                message=f"Axes {axis.id!r} rowspan must be positive; got {axis.rowspan}.",
                axes_id=axis.id,
                field="axes.rowspan",
                details=_axis_layout_details(axis),
            )
        )
    if axis.colspan < 1:
        issues.append(
            ValidationIssue(
                code="invalid_axes_span",
                message=f"Axes {axis.id!r} colspan must be positive; got {axis.colspan}.",
                axes_id=axis.id,
                field="axes.colspan",
                details=_axis_layout_details(axis),
            )
        )


def _axis_layout_details(axis: AxesSpec) -> dict[str, Any]:
    return {
        "axes_id": axis.id,
        "row": axis.row,
        "col": axis.col,
        "rowspan": axis.rowspan,
        "colspan": axis.colspan,
    }


def _validate_recipe(
    namespace: dict[str, Any],
    recipe: RecipeLayer,
    issues: list[ValidationIssue],
) -> None:
    data = recipe.dataset
    value = namespace.get(data.variable)
    if value is None:
        issues.append(
            ValidationIssue(
                code="missing_variable",
                message=f"Recipe {recipe.id!r} references missing variable {data.variable!r}.",
                layer_id=recipe.id,
                axes_id=recipe.axes_id,
                field="dataset.variable",
                details={"variable": data.variable, "dataset": data.model_dump()},
            )
        )
        return

    if not _is_dataframe(value):
        issues.append(
            ValidationIssue(
                code="unsupported_recipe_source",
                message=(
                    f"Recipe {recipe.id!r} requires a pandas DataFrame variable; "
                    f"{data.variable!r} is {type(value).__name__}."
                ),
                layer_id=recipe.id,
                axes_id=recipe.axes_id,
                field="dataset.variable",
                details={"variable": data.variable, "type": type(value).__name__},
            )
        )
        return

    required = ["x", "y"]
    if recipe.kind == "paired_before_after":
        required.append("subject")

    for field in required:
        if not getattr(data, field):
            issues.append(
                ValidationIssue(
                    code="missing_column",
                    message=f"Recipe {recipe.id!r} requires dataset.{field}.",
                    layer_id=recipe.id,
                    axes_id=recipe.axes_id,
                    field=f"dataset.{field}",
                    details={"field": field, "dataset": data.model_dump()},
                )
            )

    for field in ["x", "y", "group", "subject"]:
        column = getattr(data, field)
        if column:
            _check_dataframe_column(value, recipe, column, field, issues)


def _is_dataframe(value: Any) -> bool:
    return type(value).__module__.startswith("pandas") and type(value).__name__ == "DataFrame"


def _check_dataframe_column(
    value: Any,
    recipe: RecipeLayer,
    column: str,
    field: str,
    issues: list[ValidationIssue],
) -> None:
    columns = [str(item) for item in getattr(value, "columns", [])]
    if column in columns:
        return
    issues.append(
        ValidationIssue(
            code="missing_column",
            message=f"Recipe {recipe.id!r} references missing column {column!r}.",
            layer_id=recipe.id,
            axes_id=recipe.axes_id,
            field=f"dataset.{field}",
            details={"variable": recipe.dataset.variable, "column": column},
        )
    )


def _resolve_z(
    namespace: dict[str, Any],
    layer: PlotLayer,
    issues: list[ValidationIssue],
) -> _ResolvedValue | None:
    data = layer.dataset
    if data.z or data.z_variable or layer.kind in {"heatmap", "contour"}:
        return _resolve_channel(namespace, layer, "z", issues) or _resolve_value(namespace, layer, "y", issues)
    return None


def _resolve_value(
    namespace: dict[str, Any],
    layer: PlotLayer,
    channel: str,
    issues: list[ValidationIssue],
) -> _ResolvedValue | None:
    data = layer.dataset
    if getattr(data, channel) or getattr(data, f"{channel}_variable"):
        return _resolve_channel(namespace, layer, channel, issues)
    return _resolve_variable_column(namespace, layer, data, data.variable, None, channel, issues)


def _resolve_channel(
    namespace: dict[str, Any],
    layer: PlotLayer,
    channel: str,
    issues: list[ValidationIssue],
) -> _ResolvedValue | None:
    data = layer.dataset
    if channel != "y" and not getattr(data, channel) and not getattr(data, f"{channel}_variable"):
        return None
    variable_name = getattr(data, f"{channel}_variable") or data.variable
    column = getattr(data, channel)
    return _resolve_variable_column(namespace, layer, data, variable_name, column, channel, issues)


def _resolve_variable_column(
    namespace: dict[str, Any],
    layer: PlotLayer,
    data: DatasetRef,
    variable_name: str | None,
    column: str | None,
    channel: str,
    issues: list[ValidationIssue],
) -> _ResolvedValue | None:
    if not variable_name or variable_name not in namespace:
        issues.append(
            ValidationIssue(
                code="missing_variable",
                message=f"Layer {layer.id!r} references missing variable {variable_name!r}.",
                layer_id=layer.id,
                axes_id=layer.axes_id,
                field=f"dataset.{channel}_variable" if channel != "y" else "dataset.variable",
                details={"variable": variable_name, "dataset": data.model_dump()},
            )
        )
        return None

    value = namespace[variable_name]
    label = variable_name
    if column:
        columns = getattr(value, "columns", None)
        if columns is not None and column not in [str(item) for item in columns]:
            issues.append(
                ValidationIssue(
                    code="missing_column",
                    message=f"Layer {layer.id!r} references missing column {column!r} on {variable_name!r}.",
                    layer_id=layer.id,
                    axes_id=layer.axes_id,
                    field=f"dataset.{channel}",
                    details={"variable": variable_name, "column": column},
                )
            )
            return None
        try:
            value = value[column]
            label = f"{variable_name}[{column!r}]"
        except Exception as exc:
            issues.append(
                ValidationIssue(
                    code="missing_column",
                    message=f"Layer {layer.id!r} could not read column {column!r} on {variable_name!r}: {exc}",
                    layer_id=layer.id,
                    axes_id=layer.axes_id,
                    field=f"dataset.{channel}",
                    details={"variable": variable_name, "column": column},
                )
            )
            return None

    return _ResolvedValue(value=value, label=label)


def _check_lengths(
    layer: PlotLayer,
    issues: list[ValidationIssue],
    **channels: _ResolvedValue | None,
) -> None:
    lengths = {
        channel: _length(resolved.value)
        for channel, resolved in channels.items()
        if resolved is not None and _length(resolved.value) is not None
    }
    if len(lengths) < 2:
        return
    unique_lengths = set(lengths.values())
    if len(unique_lengths) == 1:
        return
    issues.append(
        ValidationIssue(
            code="dimension_mismatch",
            message=f"Layer {layer.id!r} channel lengths differ: {lengths}.",
            layer_id=layer.id,
            axes_id=layer.axes_id,
            details={"lengths": lengths},
        )
    )


def _check_two_dimensional(
    layer: PlotLayer,
    issues: list[ValidationIssue],
    resolved: _ResolvedValue | None,
) -> None:
    if resolved is None:
        return
    shape = _shape(resolved.value)
    if shape is None or len(shape) < 2:
        issues.append(
            ValidationIssue(
                code="requires_2d_data",
                message=f"{layer.kind} layer {layer.id!r} needs 2D value data.",
                layer_id=layer.id,
                axes_id=layer.axes_id,
                field="dataset.z",
                details={"shape": list(shape or [])},
            )
        )


def _check_positive(
    layer: PlotLayer,
    issues: list[ValidationIssue],
    resolved: _ResolvedValue,
    channel: str,
) -> None:
    try:
        array = np.asarray(resolved.value, dtype=float)
    except Exception:
        return
    if array.size == 0:
        return
    finite = array[np.isfinite(array)]
    if finite.size and np.nanmin(finite) <= 0:
        issues.append(
            ValidationIssue(
                code="log_scale_non_positive",
                message=f"Layer {layer.id!r} has non-positive {channel} data for a log-scaled axis.",
                layer_id=layer.id,
                axes_id=layer.axes_id,
                field=f"dataset.{channel}",
            )
        )


def _shape(value: Any) -> tuple[int, ...] | None:
    try:
        return tuple(int(part) for part in np.asarray(value).shape)
    except Exception:
        shape = getattr(value, "shape", None)
        if shape is None:
            return None
        return tuple(int(part) for part in shape)


def _length(value: Any) -> int | None:
    shape = _shape(value)
    if shape:
        return int(shape[0])
    try:
        return len(value)
    except Exception:
        return None

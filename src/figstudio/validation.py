"""Pre-render validation for FigureSpec objects."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import math
from typing import Any

import numpy as np

from figstudio.models import (
    AxesSpec,
    DataFilterSpec,
    DatasetRef,
    FigureSpec,
    PlotLayer,
    RecipeDatasetRef,
    RecipeLayer,
    ReferenceLineSpec,
    StyleProfile,
    ValidationIssue,
    ValidationResponse,
)
from figstudio.selection import (
    is_python_literal_key,
    normalize_mapping_key,
)
from figstudio.style_profiles import missing_profile_issue_details


MAX_REPAIR_CHOICES = 12
SECONDARY_Y_SUPPORTED_KINDS = {
    "line",
    "scatter",
    "bar",
    "hist",
    "errorbar",
    "step",
    "fill_between",
}


@dataclass
class _ResolvedValue:
    value: Any
    label: str


def _limited_strings(values: list[str]) -> tuple[list[str], bool]:
    return values[:MAX_REPAIR_CHOICES], len(values) > MAX_REPAIR_CHOICES


def _choice_details(values: list[str], key: str) -> tuple[dict[str, Any], str | None]:
    visible, truncated = _limited_strings(values)
    details: dict[str, Any] = {key: visible}
    if truncated:
        details[f"{key}_truncated"] = True
    if visible:
        details["suggested_value"] = visible[0]
    return details, visible[0] if visible else None


def _available_variable_names(namespace: dict[str, Any]) -> list[str]:
    return sorted(str(name) for name in namespace if not str(name).startswith("_"))


def _dataframe_variable_names(namespace: dict[str, Any]) -> list[str]:
    return sorted(str(name) for name, value in namespace.items() if _is_dataframe(value))


def _variable_repair(
    namespace: dict[str, Any],
    *,
    field: str,
    missing: str | None,
) -> tuple[dict[str, Any], str]:
    details, suggested = _choice_details(_available_variable_names(namespace), "available_variables")
    details["variable"] = missing
    if suggested:
        return (
            details,
            f"Set {field} to {suggested!r}, or reopen FigStudio with {missing!r} in scope.",
        )
    return details, f"Reopen FigStudio from a Python scope that contains {missing!r}."


def _dataframe_source_repair(
    namespace: dict[str, Any],
    *,
    variable: str,
) -> tuple[dict[str, Any], str]:
    details, suggested = _choice_details(_dataframe_variable_names(namespace), "available_dataframes")
    details["variable"] = variable
    details["type"] = type(namespace.get(variable)).__name__
    if suggested:
        return details, f"Set dataset.variable to DataFrame {suggested!r}, or switch to a normal plot layer."
    return details, "Use a pandas DataFrame source for this recipe, or switch to a normal plot layer."


def _dataframe_columns(value: Any) -> list[str]:
    columns = getattr(value, "columns", None)
    if columns is None:
        return []
    return [str(item) for item in columns]


def _is_numeric_column(value: Any, column: str) -> bool:
    try:
        dtype = value[column].dtype
        return bool(np.issubdtype(dtype, np.number))
    except Exception:
        try:
            return bool(np.issubdtype(np.asarray(value[column]).dtype, np.number))
        except Exception:
            return False


def _suggested_dataframe_column(value: Any, field: str) -> str | None:
    columns = _dataframe_columns(value)
    if not columns:
        return None
    if field in {"y", "z", "yerr"}:
        for column in columns:
            if _is_numeric_column(value, column):
                return column
    if field in {"group", "subject"}:
        for column in columns:
            if not _is_numeric_column(value, column):
                return column
    return columns[0]


def _column_repair(
    value: Any,
    *,
    variable: str,
    field: str,
) -> tuple[dict[str, Any], str]:
    columns = _dataframe_columns(value)
    visible, truncated = _limited_strings(columns)
    suggested = _suggested_dataframe_column(value, field)
    details: dict[str, Any] = {"variable": variable, "available_columns": visible}
    if truncated:
        details["available_columns_truncated"] = True
    if suggested:
        details["suggested_value"] = suggested
        return details, f"Set dataset.{field} to {suggested!r}, or choose another column on {variable!r}."
    return details, f"Choose an existing column on {variable!r} for dataset.{field}."


def _axes_repair(axes: list[AxesSpec], axes_id: str | None) -> tuple[dict[str, Any], str]:
    details, suggested = _choice_details([axis.id for axis in axes], "available_axes")
    details["axes_id"] = axes_id
    if suggested:
        return details, f"Set axes_id to {suggested!r}, or choose another existing panel."
    return details, "Create a target axes before assigning this item."


def _missing_profile_suggestion(details: dict[str, Any]) -> str:
    available = details.get("available_profiles") or []
    if available:
        return f"Select profile {available[0]!r}, or choose No project profile."
    return "Choose No project profile, or add this profile id to .figstudio/styles.json."


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
                suggestion=_missing_profile_suggestion(profile_details),
                field="style.profile_id",
                details=profile_details,
            )
        )
    _validate_axes_layout(spec, issues)
    axes_by_id = {axis.id: axis for axis in spec.axes}

    for layer in spec.layers:
        if layer.axes_id not in axes_by_id:
            details, suggestion = _axes_repair(spec.axes, layer.axes_id)
            issues.append(
                ValidationIssue(
                    code="missing_axes",
                    message=f"Layer {layer.id!r} targets missing axes {layer.axes_id!r}.",
                    suggestion=suggestion,
                    layer_id=layer.id,
                    axes_id=layer.axes_id,
                    field="axes_id",
                    details=details,
                )
            )
            continue

        axis = axes_by_id[layer.axes_id]
        _validate_layer_y_axis(layer, axis, issues)
        dataset_source = _resolve_dataset_source(namespace, layer, issues)
        if dataset_source is None:
            continue
        if dataset_source is not None:
            _validate_data_filters(
                namespace,
                layer.id,
                layer.axes_id,
                layer.dataset,
                issues,
                source_value=dataset_source.value,
                source_label=dataset_source.label,
            )
        y_value = _resolve_value(namespace, layer, "y", issues, dataset_source)
        x_value = _resolve_channel(namespace, layer, "x", issues, dataset_source)
        z_value = _resolve_z(namespace, layer, issues, dataset_source)
        yerr_value = _resolve_channel(namespace, layer, "yerr", issues, dataset_source)

        if layer.kind in {"line", "scatter", "bar", "barh", "step", "fill_between", "errorbar"}:
            _check_lengths(layer, issues, x=x_value, y=y_value)
        if layer.kind == "errorbar":
            _check_lengths(layer, issues, y=y_value, yerr=yerr_value)
        if layer.kind in {"heatmap", "contour"}:
            _check_two_dimensional(layer, issues, z_value)

        if axis.xscale == "log" and x_value is not None:
            _check_positive(layer, issues, x_value, "x")
        yscale = _layer_yscale(layer, axis)
        if yscale == "log" and y_value is not None and layer.kind not in {"heatmap", "contour"}:
            _check_positive(layer, issues, y_value, "y")

    for recipe in spec.recipes:
        if recipe.axes_id not in axes_by_id:
            details, suggestion = _axes_repair(spec.axes, recipe.axes_id)
            issues.append(
                ValidationIssue(
                    code="missing_axes",
                    message=f"Recipe {recipe.id!r} targets missing axes {recipe.axes_id!r}.",
                    suggestion=suggestion,
                    layer_id=recipe.id,
                    axes_id=recipe.axes_id,
                    field="axes_id",
                    details=details,
                )
            )
            continue
        _validate_recipe(namespace, recipe, issues)

    for reference_line in spec.reference_lines:
        _validate_reference_line(reference_line, axes_by_id, spec.axes, issues)

    return ValidationResponse(ok=not any(issue.severity == "error" for issue in issues), issues=issues)


def _validate_axes_layout(spec: FigureSpec, issues: list[ValidationIssue]) -> None:
    if spec.rows < 1:
        issues.append(
            ValidationIssue(
                code="invalid_grid_size",
                message=f"FigureSpec rows must be positive; got {spec.rows}.",
                suggestion="Set figure rows to at least 1 in the Figure controls.",
                field="rows",
                details={"rows": spec.rows, "cols": spec.cols},
            )
        )
    if spec.cols < 1:
        issues.append(
            ValidationIssue(
                code="invalid_grid_size",
                message=f"FigureSpec cols must be positive; got {spec.cols}.",
                suggestion="Set figure columns to at least 1 in the Figure controls.",
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
                    suggestion="Move this axes inside the grid, reduce its span, or increase figure rows/columns.",
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
                suggestion="Use a built-in panel layout or make every axes id unique.",
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
                suggestion="Choose a valid panel layout or adjust row, column, and span values so cells do not overlap.",
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
                suggestion="Set axes rowspan to at least 1, or choose a built-in panel layout.",
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
                suggestion="Set axes colspan to at least 1, or choose a built-in panel layout.",
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
        details, suggestion = _variable_repair(namespace, field="dataset.variable", missing=data.variable)
        details["dataset"] = data.model_dump()
        issues.append(
            ValidationIssue(
                code="missing_variable",
                message=f"Recipe {recipe.id!r} references missing variable {data.variable!r}.",
                suggestion=suggestion,
                layer_id=recipe.id,
                axes_id=recipe.axes_id,
                field="dataset.variable",
                details=details,
            )
        )
        return

    if not _is_dataframe(value):
        details, suggestion = _dataframe_source_repair(namespace, variable=data.variable)
        issues.append(
            ValidationIssue(
                code="unsupported_recipe_source",
                message=(
                    f"Recipe {recipe.id!r} requires a pandas DataFrame variable; "
                    f"{data.variable!r} is {type(value).__name__}."
                ),
                suggestion=suggestion,
                layer_id=recipe.id,
                axes_id=recipe.axes_id,
                field="dataset.variable",
                details=details,
            )
        )
        return

    _validate_data_filters(namespace, recipe.id, recipe.axes_id, data, issues)

    required = ["x", "y"]
    if recipe.kind == "paired_before_after":
        required.append("subject")

    for field in required:
        if not getattr(data, field):
            details, suggestion = _column_repair(value, variable=data.variable, field=field)
            details["field"] = field
            details["dataset"] = data.model_dump()
            issues.append(
                ValidationIssue(
                    code="missing_column",
                    message=f"Recipe {recipe.id!r} requires dataset.{field}.",
                    suggestion=suggestion,
                    layer_id=recipe.id,
                    axes_id=recipe.axes_id,
                    field=f"dataset.{field}",
                    details=details,
                )
            )

    for field in ["x", "y", "group", "subject"]:
        column = getattr(data, field)
        if column:
            _check_dataframe_column(value, recipe, column, field, issues)


def _validate_layer_y_axis(layer: PlotLayer, axis: AxesSpec, issues: list[ValidationIssue]) -> None:
    if layer.y_axis != "right":
        return
    if layer.kind in SECONDARY_Y_SUPPORTED_KINDS:
        return
    issues.append(
        ValidationIssue(
            code="unsupported_secondary_y_layer",
            message=(
                f"Layer {layer.id!r} uses the right y-axis, but {layer.kind!r} "
                "is not supported for secondary-axis overlays yet."
            ),
            suggestion=(
                "Switch this layer back to the left y-axis, or use a line, scatter, "
                "bar, histogram, errorbar, step, or fill_between layer."
            ),
            layer_id=layer.id,
            axes_id=axis.id,
            field="y_axis",
            details={
                "kind": layer.kind,
                "y_axis": layer.y_axis,
                "supported_kinds": sorted(SECONDARY_Y_SUPPORTED_KINDS),
            },
        )
    )


def _layer_yscale(layer: PlotLayer, axis: AxesSpec) -> str:
    if layer.y_axis == "right":
        return axis.secondary_y.yscale
    return axis.yscale


def _validate_reference_line(
    reference_line: ReferenceLineSpec,
    axes_by_id: dict[str, AxesSpec],
    axes: list[AxesSpec],
    issues: list[ValidationIssue],
) -> None:
    axis = axes_by_id.get(reference_line.axes_id)
    if axis is None:
        details, suggestion = _axes_repair(axes, reference_line.axes_id)
        details["reference_line_id"] = reference_line.id
        issues.append(
            ValidationIssue(
                code="missing_axes",
                message=(
                    f"Reference line {reference_line.id!r} targets missing axes "
                    f"{reference_line.axes_id!r}."
                ),
                suggestion=suggestion,
                axes_id=reference_line.axes_id,
                field="reference_lines.axes_id",
                details=details,
            )
        )
        return

    if not math.isfinite(reference_line.value):
        issues.append(
            ValidationIssue(
                code="invalid_reference_line_value",
                message=f"Reference line {reference_line.id!r} needs a finite numeric value.",
                suggestion="Set the reference line value to a finite number.",
                axes_id=reference_line.axes_id,
                field="reference_lines.value",
                details={"reference_line_id": reference_line.id, "value": reference_line.value},
            )
        )
        return

    scaled_axis = axis.yscale if reference_line.orientation == "horizontal" else axis.xscale
    if scaled_axis == "log" and reference_line.value <= 0:
        channel = "Y" if reference_line.orientation == "horizontal" else "X"
        issues.append(
            ValidationIssue(
                code="invalid_reference_line_value",
                message=(
                    f"Reference line {reference_line.id!r} has a non-positive {channel} value "
                    f"for a log-scaled axes."
                ),
                suggestion=f"Use a positive {channel} reference value, or switch this axes back to linear scale.",
                axes_id=reference_line.axes_id,
                field="reference_lines.value",
                details={
                    "reference_line_id": reference_line.id,
                    "orientation": reference_line.orientation,
                    "value": reference_line.value,
                    "scale": scaled_axis,
                },
            )
        )


def _is_dataframe(value: Any) -> bool:
    return type(value).__module__.startswith("pandas") and type(value).__name__ == "DataFrame"


def _validate_data_filters(
    namespace: dict[str, Any],
    layer_id: str,
    axes_id: str,
    data: DatasetRef | RecipeDatasetRef,
    issues: list[ValidationIssue],
    source_value: Any | None = None,
    source_label: str | None = None,
) -> None:
    if not data.filters:
        return
    value = source_value if source_value is not None else namespace.get(data.variable)
    if value is None:
        return
    variable_label = source_label or data.variable
    if not _is_dataframe(value):
        issues.append(
            ValidationIssue(
                code="unsupported_filter_source",
                message=f"Filters on {layer_id!r} require a pandas DataFrame source.",
                suggestion="Use filters only with DataFrame-backed layers or recipes.",
                layer_id=layer_id,
                axes_id=axes_id,
                field="dataset.filters",
                details={"variable": variable_label, "type": type(value).__name__},
            )
        )
        return

    valid = True
    columns = _dataframe_columns(value)
    for index, data_filter in enumerate(data.filters):
        if data_filter.column not in columns:
            details, suggestion = _column_repair(value, variable=variable_label, field="filters.column")
            details["filter"] = _filter_details(data_filter, index)
            issues.append(
                ValidationIssue(
                    code="missing_column",
                    message=(
                        f"Filter {index + 1} on {layer_id!r} references missing column "
                        f"{data_filter.column!r}."
                    ),
                    suggestion=suggestion,
                    layer_id=layer_id,
                    axes_id=axes_id,
                    field="dataset.filters.column",
                    details=details,
                )
            )
            valid = False
    if not valid:
        return

    filtered = _apply_data_filters(value, data.filters)
    try:
        is_empty = len(filtered) == 0
    except Exception:
        is_empty = False
    if is_empty:
        issues.append(
            ValidationIssue(
                severity="warning",
                code="empty_filter_result",
                message=f"Filters on {layer_id!r} match no rows.",
                suggestion="Choose another facet value, remove the filter, or check the live DataFrame data.",
                layer_id=layer_id,
                axes_id=axes_id,
                field="dataset.filters",
                details={
                    "variable": data.variable,
                    "filters": [_filter_details(data_filter, index) for index, data_filter in enumerate(data.filters)],
                },
            )
        )


def _filter_details(data_filter: DataFilterSpec, index: int) -> dict[str, Any]:
    return {
        "index": index,
        "column": data_filter.column,
        "op": data_filter.op,
        "value": data_filter.value,
        "label": data_filter.label,
    }


def _apply_data_filters(value: Any, filters: list[DataFilterSpec]) -> Any:
    if not filters or not _is_dataframe(value):
        return value
    filtered = value
    for data_filter in filters:
        if data_filter.op != "eq" or data_filter.column not in _dataframe_columns(filtered):
            continue
        try:
            if data_filter.value is None:
                filtered = filtered[filtered[data_filter.column].isna()]
            else:
                filtered = filtered[filtered[data_filter.column] == data_filter.value]
        except Exception:
            return filtered
    return filtered


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
    details, suggestion = _column_repair(value, variable=recipe.dataset.variable, field=field)
    details["column"] = column
    issues.append(
        ValidationIssue(
            code="missing_column",
            message=f"Recipe {recipe.id!r} references missing column {column!r}.",
            suggestion=suggestion,
            layer_id=recipe.id,
            axes_id=recipe.axes_id,
            field=f"dataset.{field}",
            details=details,
        )
    )


def _resolve_z(
    namespace: dict[str, Any],
    layer: PlotLayer,
    issues: list[ValidationIssue],
    dataset_source: _ResolvedValue | None,
) -> _ResolvedValue | None:
    data = layer.dataset
    if data.z or data.z_variable or layer.kind in {"heatmap", "contour"}:
        return _resolve_channel(namespace, layer, "z", issues, dataset_source) or _resolve_value(
            namespace,
            layer,
            "y",
            issues,
            dataset_source,
        )
    return None


def _resolve_value(
    namespace: dict[str, Any],
    layer: PlotLayer,
    channel: str,
    issues: list[ValidationIssue],
    dataset_source: _ResolvedValue | None,
) -> _ResolvedValue | None:
    data = layer.dataset
    if getattr(data, channel) or getattr(data, f"{channel}_variable"):
        return _resolve_channel(namespace, layer, channel, issues, dataset_source)
    return _resolve_variable_column(namespace, layer, data, data.variable, None, channel, issues, dataset_source)


def _resolve_channel(
    namespace: dict[str, Any],
    layer: PlotLayer,
    channel: str,
    issues: list[ValidationIssue],
    dataset_source: _ResolvedValue | None,
) -> _ResolvedValue | None:
    data = layer.dataset
    if channel != "y" and not getattr(data, channel) and not getattr(data, f"{channel}_variable"):
        return None
    variable_name = getattr(data, f"{channel}_variable") or data.variable
    column = getattr(data, channel)
    return _resolve_variable_column(namespace, layer, data, variable_name, column, channel, issues, dataset_source)


def _resolve_variable_column(
    namespace: dict[str, Any],
    layer: PlotLayer,
    data: DatasetRef,
    variable_name: str | None,
    column: str | None,
    channel: str,
    issues: list[ValidationIssue],
    dataset_source: _ResolvedValue | None,
) -> _ResolvedValue | None:
    if variable_name == data.variable and dataset_source is not None:
        value = dataset_source.value
        label = dataset_source.label
    elif not variable_name or variable_name not in namespace:
        field = f"dataset.{channel}_variable" if channel != "y" else "dataset.variable"
        details, suggestion = _variable_repair(namespace, field=field, missing=variable_name)
        details["dataset"] = data.model_dump()
        issues.append(
            ValidationIssue(
                code="missing_variable",
                message=f"Layer {layer.id!r} references missing variable {variable_name!r}.",
                suggestion=suggestion,
                layer_id=layer.id,
                axes_id=layer.axes_id,
                field=field,
                details=details,
            )
        )
        return None
    else:
        value = namespace[variable_name]
        label = variable_name
    if variable_name == data.variable:
        value = _apply_data_filters(value, data.filters)
    if column:
        columns = getattr(value, "columns", None)
        if columns is not None and column not in [str(item) for item in columns]:
            details, suggestion = _column_repair(value, variable=variable_name, field=channel)
            details["column"] = column
            issues.append(
                ValidationIssue(
                    code="missing_column",
                    message=f"Layer {layer.id!r} references missing column {column!r} on {variable_name!r}.",
                    suggestion=suggestion,
                    layer_id=layer.id,
                    axes_id=layer.axes_id,
                    field=f"dataset.{channel}",
                    details=details,
                )
            )
            return None
        try:
            value = value[column]
            label = f"{variable_name}[{column!r}]"
        except Exception as exc:
            details, suggestion = _column_repair(value, variable=variable_name, field=channel)
            details["column"] = column
            details["error"] = str(exc)
            issues.append(
                ValidationIssue(
                    code="missing_column",
                    message=f"Layer {layer.id!r} could not read column {column!r} on {variable_name!r}: {exc}",
                    suggestion=suggestion,
                    layer_id=layer.id,
                    axes_id=layer.axes_id,
                    field=f"dataset.{channel}",
                    details=details,
                )
            )
            return None

    return _ResolvedValue(value=value, label=label)


def _resolve_dataset_source(
    namespace: dict[str, Any],
    layer: PlotLayer,
    issues: list[ValidationIssue],
) -> _ResolvedValue | None:
    data = layer.dataset
    if data.variable not in namespace:
        details, suggestion = _variable_repair(namespace, field="dataset.variable", missing=data.variable)
        details["dataset"] = data.model_dump()
        issues.append(
            ValidationIssue(
                code="missing_variable",
                message=f"Layer {layer.id!r} references missing variable {data.variable!r}.",
                suggestion=suggestion,
                layer_id=layer.id,
                axes_id=layer.axes_id,
                field="dataset.variable",
                details=details,
            )
        )
        return None

    value = namespace[data.variable]
    label = data.variable
    selection = data.selection
    if selection is None:
        return _ResolvedValue(value=value, label=label)

    if data.x and not data.x_variable:
        issues.append(
            ValidationIssue(
                code="unsupported_selected_channel",
                message=f"Layer {layer.id!r} uses selected source data for X, which is not supported yet.",
                suggestion="Use index X or choose an independent X variable for repeated mapping/sequence panels.",
                layer_id=layer.id,
                axes_id=layer.axes_id,
                field="dataset.x",
                details={"dataset": data.model_dump()},
            )
        )
    if data.yerr and not data.yerr_variable:
        issues.append(
            ValidationIssue(
                code="unsupported_selected_channel",
                message=f"Layer {layer.id!r} uses selected source data for Y error, which is not supported yet.",
                suggestion="Use no error channel or choose an independent error variable for repeated mapping/sequence panels.",
                layer_id=layer.id,
                axes_id=layer.axes_id,
                field="dataset.yerr",
                details={"dataset": data.model_dump()},
            )
        )

    if selection.kind == "mapping_key":
        if not isinstance(value, Mapping):
            issues.append(
                ValidationIssue(
                    code="unsupported_selection_source",
                    message=f"Layer {layer.id!r} uses a mapping-key selection on non-mapping variable {data.variable!r}.",
                    suggestion="Choose a mapping source, remove dataset.selection, or use a DataFrame facet filter instead.",
                    layer_id=layer.id,
                    axes_id=layer.axes_id,
                    field="dataset.selection",
                    details={"variable": data.variable, "type": type(value).__name__, "selection": selection.model_dump()},
                )
            )
            return None
        if not is_python_literal_key(selection.key):
            issues.append(
                ValidationIssue(
                    code="unsupported_selection_key",
                    message=f"Layer {layer.id!r} uses a mapping key that cannot be generated as a Python literal.",
                    suggestion="Use string, number, boolean, None, or tuple keys for mapping repeated panels.",
                    layer_id=layer.id,
                    axes_id=layer.axes_id,
                    field="dataset.selection.key",
                    details={"variable": data.variable, "key": selection.key},
                )
            )
            return None
        key = normalize_mapping_key(selection.key)
        if key not in value:
            issues.append(
                ValidationIssue(
                    code="missing_selection_key",
                    message=f"Layer {layer.id!r} references missing mapping key {selection.key!r}.",
                    suggestion="Choose a key that still exists in the live mapping source.",
                    layer_id=layer.id,
                    axes_id=layer.axes_id,
                    field="dataset.selection.key",
                    details={"variable": data.variable, "key": selection.key},
                )
            )
            return None
        selected = value[key]
        selected_label = selection.label or f"{data.variable}[{key!r}]"
        _validate_selected_value(layer, selected, selected_label, issues)
        return _ResolvedValue(value=selected, label=selected_label)

    if selection.kind == "sequence_index":
        if not isinstance(value, list | tuple):
            issues.append(
                ValidationIssue(
                    code="unsupported_selection_source",
                    message=f"Layer {layer.id!r} uses a sequence-index selection on non-sequence variable {data.variable!r}.",
                    suggestion="Choose a list or tuple source, remove dataset.selection, or use a DataFrame facet filter instead.",
                    layer_id=layer.id,
                    axes_id=layer.axes_id,
                    field="dataset.selection",
                    details={"variable": data.variable, "type": type(value).__name__, "selection": selection.model_dump()},
                )
            )
            return None
        if selection.index is None or selection.index < 0 or selection.index >= len(value):
            issues.append(
                ValidationIssue(
                    code="selection_index_out_of_range",
                    message=f"Layer {layer.id!r} references sequence index {selection.index!r} outside {data.variable!r}.",
                    suggestion="Choose an index that exists in the live sequence source.",
                    layer_id=layer.id,
                    axes_id=layer.axes_id,
                    field="dataset.selection.index",
                    details={"variable": data.variable, "index": selection.index, "length": len(value)},
                )
            )
            return None
        selected = value[selection.index]
        selected_label = selection.label or f"{data.variable}[{selection.index}]"
        _validate_selected_value(layer, selected, selected_label, issues)
        return _ResolvedValue(value=selected, label=selected_label)

    issues.append(
        ValidationIssue(
            code="unsupported_selection_kind",
            message=f"Layer {layer.id!r} uses unsupported selection kind {selection.kind!r}.",
            suggestion="Use mapping_key or sequence_index selection.",
            layer_id=layer.id,
            axes_id=layer.axes_id,
            field="dataset.selection.kind",
            details={"selection": selection.model_dump()},
        )
    )
    return None


def _validate_selected_value(
    layer: PlotLayer,
    value: Any,
    label: str,
    issues: list[ValidationIssue],
) -> None:
    type_name = type(value).__name__
    module = type(value).__module__
    if _is_dataframe(value) or (module.startswith("pandas") and type_name in {"Series", "Index"}):
        return
    if isinstance(value, list | tuple):
        return
    shape = _shape(value)
    if type(value).__module__.startswith("numpy") and shape:
        return
    if _length(value) is None:
        issues.append(
            ValidationIssue(
                code="unplottable_selection_value",
                message=f"Layer {layer.id!r} selects scalar value {label!r}, which cannot be plotted as a panel.",
                suggestion="Use mapping or sequence items that contain arrays, Series, DataFrames, or list-like values.",
                layer_id=layer.id,
                axes_id=layer.axes_id,
                field="dataset.selection",
                details={"label": label, "type": type(value).__name__},
            )
        )


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
            suggestion="Use X, Y, and error channels with matching first dimensions, or switch X back to index values.",
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
                suggestion="Set dataset.z to a 2D value source, or switch to a plot type that accepts one-dimensional data.",
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
                suggestion=f"Filter non-positive {channel} values, set positive limits, or switch this axis back to linear scale.",
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

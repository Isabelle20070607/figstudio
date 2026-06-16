"""Pre-render validation for FigureSpec objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from figstudio.models import DatasetRef, FigureSpec, PlotLayer, ValidationIssue, ValidationResponse


@dataclass
class _ResolvedValue:
    value: Any
    label: str


def validate_figure_spec(namespace: dict[str, Any], spec: FigureSpec) -> ValidationResponse:
    issues: list[ValidationIssue] = []
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

    return ValidationResponse(ok=not any(issue.severity == "error" for issue in issues), issues=issues)


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

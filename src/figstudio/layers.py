"""Bundled plot-layer registry metadata for FigStudio."""

from __future__ import annotations

from dataclasses import dataclass
from typing import get_args

from figstudio.models import (
    LayerCatalogResponse,
    LayerDatasetField,
    LayerDefinition,
    LayerQuestionGroup,
    LayerStyle,
    PlotKind,
)


CATALOG_VERSION = 1


@dataclass(frozen=True)
class RegisteredLayer:
    definition: LayerDefinition
    codegen_method: str
    length_checks: tuple[tuple[LayerDatasetField, ...], ...] = ()


_LAYER_GROUPS = [
    LayerQuestionGroup(
        id="cartesian",
        label="Cartesian layers",
        summary="Plot one-dimensional values against an index or explicit X source.",
    ),
    LayerQuestionGroup(
        id="distribution",
        label="Distribution/value layers",
        summary="Inspect value distributions or single value channels.",
    ),
    LayerQuestionGroup(
        id="field",
        label="2D field layers",
        summary="Render matrix, image, or gridded value data.",
    ),
]

_LAYER_REGISTRY = [
    RegisteredLayer(
        LayerDefinition(
            kind="line",
            label="Line",
            group_id="cartesian",
            role="Plots Y values against index or an explicit X source.",
            required_fields=["y"],
            optional_fields=["x"],
            supports_secondary_y=True,
            default_style=LayerStyle(color="#2563eb", marker="", linestyle="-", linewidth=1.8),
        ),
        "_line_layer_code",
        length_checks=(("x", "y"),),
    ),
    RegisteredLayer(
        LayerDefinition(
            kind="scatter",
            label="Scatter",
            group_id="cartesian",
            role="Plots individual Y observations against index or an explicit X source.",
            required_fields=["y"],
            optional_fields=["x"],
            supports_secondary_y=True,
            default_style=LayerStyle(color="#2563eb", marker="o", alpha=0.85),
        ),
        "_scatter_layer_code",
        length_checks=(("x", "y"),),
    ),
    RegisteredLayer(
        LayerDefinition(
            kind="bar",
            label="Vertical bars",
            group_id="cartesian",
            role="Plots Y values as vertical bars.",
            required_fields=["y"],
            optional_fields=["x"],
            supports_secondary_y=True,
            default_style=LayerStyle(color="#2563eb", alpha=0.85),
        ),
        "_bar_layer_code",
        length_checks=(("x", "y"),),
    ),
    RegisteredLayer(
        LayerDefinition(
            kind="barh",
            label="Horizontal bars",
            group_id="cartesian",
            role="Plots Y values as horizontal bars.",
            required_fields=["y"],
            optional_fields=["x"],
            default_style=LayerStyle(color="#2563eb", alpha=0.85),
        ),
        "_barh_layer_code",
        length_checks=(("x", "y"),),
    ),
    RegisteredLayer(
        LayerDefinition(
            kind="hist",
            label="Histogram",
            group_id="distribution",
            role="Bins a value channel into a histogram.",
            required_fields=["y"],
            ignores_x=True,
            supports_secondary_y=True,
            default_style=LayerStyle(color="#2563eb", alpha=0.85, bins=30),
        ),
        "_hist_layer_code",
    ),
    RegisteredLayer(
        LayerDefinition(
            kind="boxplot",
            label="Boxplot",
            group_id="distribution",
            role="Summarizes a value channel with quartiles and whiskers.",
            required_fields=["y"],
            ignores_x=True,
            legend_policy="none",
        ),
        "_boxplot_layer_code",
    ),
    RegisteredLayer(
        LayerDefinition(
            kind="violin",
            label="Violin",
            group_id="distribution",
            role="Summarizes a value channel with a smoothed distribution.",
            required_fields=["y"],
            ignores_x=True,
            legend_policy="none",
        ),
        "_violin_layer_code",
    ),
    RegisteredLayer(
        LayerDefinition(
            kind="errorbar",
            label="Error bars",
            group_id="cartesian",
            role="Plots Y values with an optional Y-error channel.",
            required_fields=["y"],
            optional_fields=["x", "yerr"],
            supports_secondary_y=True,
            default_style=LayerStyle(color="#2563eb", marker="o", linestyle="-", linewidth=1.8),
        ),
        "_errorbar_layer_code",
        length_checks=(("x", "y"), ("y", "yerr")),
    ),
    RegisteredLayer(
        LayerDefinition(
            kind="heatmap",
            label="Heatmap",
            group_id="field",
            role="Displays 2D value data as an image.",
            required_fields=["y"],
            optional_fields=["x", "z"],
            expects_2d=True,
            supports_colorbar=True,
            legend_policy="none",
            default_style=LayerStyle(cmap="viridis", colorbar=True),
        ),
        "_heatmap_layer_code",
    ),
    RegisteredLayer(
        LayerDefinition(
            kind="contour",
            label="Contour",
            group_id="field",
            role="Displays 2D value data as contour lines.",
            required_fields=["y"],
            optional_fields=["x", "z"],
            expects_2d=True,
            supports_colorbar=True,
            legend_policy="none",
            default_style=LayerStyle(cmap="viridis"),
        ),
        "_contour_layer_code",
    ),
    RegisteredLayer(
        LayerDefinition(
            kind="step",
            label="Step",
            group_id="cartesian",
            role="Plots Y values as a stepped line.",
            required_fields=["y"],
            optional_fields=["x"],
            supports_secondary_y=True,
            default_style=LayerStyle(color="#2563eb", linestyle="-", linewidth=1.8),
        ),
        "_step_layer_code",
        length_checks=(("x", "y"),),
    ),
    RegisteredLayer(
        LayerDefinition(
            kind="fill_between",
            label="Fill between",
            group_id="cartesian",
            role="Fills the area below or between Y values.",
            required_fields=["y"],
            optional_fields=["x"],
            supports_secondary_y=True,
            default_style=LayerStyle(color="#2563eb", alpha=0.3, fill_alpha=0.3),
        ),
        "_fill_between_layer_code",
        length_checks=(("x", "y"),),
    ),
]

_REGISTRY_BY_KIND = {entry.definition.kind: entry for entry in _LAYER_REGISTRY}
_DEFINITIONS_BY_KIND = {kind: entry.definition for kind, entry in _REGISTRY_BY_KIND.items()}


def layer_catalog() -> LayerCatalogResponse:
    return LayerCatalogResponse(
        version=CATALOG_VERSION,
        groups=list(_LAYER_GROUPS),
        layers=[entry.definition for entry in _LAYER_REGISTRY],
    )


def layer_definition(kind: PlotKind) -> LayerDefinition:
    return _DEFINITIONS_BY_KIND[kind]


def layer_codegen_method(kind: PlotKind) -> str:
    return _REGISTRY_BY_KIND[kind].codegen_method


def layer_length_checks(kind: PlotKind) -> tuple[tuple[LayerDatasetField, ...], ...]:
    return _REGISTRY_BY_KIND[kind].length_checks


def layer_expects_2d(kind: PlotKind) -> bool:
    return layer_definition(kind).expects_2d


def layer_supports_secondary_y(kind: PlotKind) -> bool:
    return layer_definition(kind).supports_secondary_y


def secondary_y_supported_kinds() -> set[PlotKind]:
    return {entry.definition.kind for entry in _LAYER_REGISTRY if entry.definition.supports_secondary_y}


def validate_catalog_complete() -> None:
    expected = set(get_args(PlotKind))
    actual = set(_DEFINITIONS_BY_KIND)
    if expected != actual:
        missing = ", ".join(sorted(expected - actual)) or "none"
        extra = ", ".join(sorted(actual - expected)) or "none"
        raise RuntimeError(f"Layer catalog mismatch; missing: {missing}; extra: {extra}")
    group_ids = {group.id for group in _LAYER_GROUPS}
    invalid_groups = sorted(
        definition.group_id for definition in _DEFINITIONS_BY_KIND.values() if definition.group_id not in group_ids
    )
    if invalid_groups:
        raise RuntimeError(f"Layer catalog references unknown groups: {', '.join(invalid_groups)}")


validate_catalog_complete()

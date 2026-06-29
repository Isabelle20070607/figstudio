"""Bundled recipe registry metadata for FigStudio."""

from __future__ import annotations

from dataclasses import dataclass
from typing import get_args

from figstudio.models import (
    LayerStyle,
    RecipeCatalogResponse,
    RecipeDatasetField,
    RecipeDefinition,
    RecipeKind,
    RecipeQuestionGroup,
)


CATALOG_VERSION = 1


@dataclass(frozen=True)
class RegisteredRecipe:
    definition: RecipeDefinition
    codegen_method: str


_RECIPE_GROUPS = [
    RecipeQuestionGroup(
        id="time-course",
        label="Time-course comparison",
        summary="Compare trajectories across time, dose, or another ordered X variable.",
    ),
    RecipeQuestionGroup(
        id="group-condition",
        label="Group/condition comparison",
        summary="Compare measured values across experimental conditions or cohorts.",
    ),
    RecipeQuestionGroup(
        id="distribution-inspection",
        label="Distribution inspection",
        summary="Review empirical distributions and their group-level differences.",
    ),
    RecipeQuestionGroup(
        id="categorical-counts",
        label="Categorical counts/composition",
        summary="Count observations or compare category composition.",
    ),
    RecipeQuestionGroup(
        id="paired-observations",
        label="Paired observations",
        summary="Track repeated measurements for the same subject across conditions.",
    ),
    RecipeQuestionGroup(
        id="neuro.ephys",
        label="Neuro ephys (experimental)",
        summary="Build bundled electrophysiology summaries from time-aligned DataFrame columns.",
    ),
]

_RECIPE_REGISTRY = [
    RegisteredRecipe(
        RecipeDefinition(
            kind="mean_sem_line",
            label="Mean +/- SEM line",
            question_group_id="time-course",
            role="Summarizes a measured value across ordered X values with optional groups.",
            required_fields=["x", "y"],
            optional_fields=["group"],
            legend_group_field="group",
            default_style=LayerStyle(color="#2563eb", linestyle="-", linewidth=1.8),
        ),
        "_mean_sem_line_code",
    ),
    RegisteredRecipe(
        RecipeDefinition(
            kind="mean_sem_bar",
            label="Mean +/- SEM bars",
            question_group_id="group-condition",
            role="Compares category means with optional grouped bars and error caps.",
            required_fields=["x", "y"],
            optional_fields=["group"],
            legend_group_field="group",
            default_style=LayerStyle(color="#2563eb", alpha=0.85),
        ),
        "_mean_sem_bar_code",
    ),
    RegisteredRecipe(
        RecipeDefinition(
            kind="count_bar",
            label="Count bars",
            question_group_id="categorical-counts",
            role="Counts rows by category with an optional grouping column.",
            required_fields=["x"],
            optional_fields=["group"],
            uses_error=False,
            default_error="none",
            default_label="count",
            legend_group_field="group",
            default_style=LayerStyle(color="#2563eb", alpha=0.85),
        ),
        "_count_bar_code",
    ),
    RegisteredRecipe(
        RecipeDefinition(
            kind="stacked_bar",
            label="Stacked count bars",
            question_group_id="categorical-counts",
            role="Shows category composition from row counts split by a required group column.",
            required_fields=["x", "group"],
            uses_error=False,
            default_error="none",
            default_label="count",
            legend_group_field="group",
            default_style=LayerStyle(alpha=0.85),
        ),
        "_stacked_bar_code",
    ),
    RegisteredRecipe(
        RecipeDefinition(
            kind="boxplot_by_category",
            label="Category boxplots",
            question_group_id="group-condition",
            role="Shows value distributions by category with optional group offsets.",
            required_fields=["x", "y"],
            optional_fields=["group"],
            uses_error=False,
            default_error="none",
            legend_group_field="group",
            default_style=LayerStyle(color="#2563eb", marker="o", alpha=0.32),
        ),
        "_boxplot_by_category_code",
    ),
    RegisteredRecipe(
        RecipeDefinition(
            kind="violin_by_category",
            label="Category violins",
            question_group_id="group-condition",
            role="Shows smoothed value distributions by category with optional group offsets.",
            required_fields=["x", "y"],
            optional_fields=["group"],
            uses_error=False,
            default_error="none",
            legend_group_field="group",
            default_style=LayerStyle(color="#2563eb", linewidth=1.1, alpha=0.34),
        ),
        "_violin_by_category_code",
    ),
    RegisteredRecipe(
        RecipeDefinition(
            kind="grouped_points",
            label="Grouped points",
            question_group_id="group-condition",
            role="Shows individual observations by category with a mean and error summary.",
            required_fields=["x", "y"],
            default_style=LayerStyle(color="#2563eb", marker="o", alpha=0.78),
        ),
        "_grouped_points_code",
    ),
    RegisteredRecipe(
        RecipeDefinition(
            kind="paired_before_after",
            label="Paired before/after",
            question_group_id="paired-observations",
            role="Connects repeated observations by subject and overlays condition means.",
            required_fields=["x", "y", "subject"],
            default_style=LayerStyle(color="#2563eb", marker="o", linewidth=1.8),
        ),
        "_paired_before_after_code",
    ),
    RegisteredRecipe(
        RecipeDefinition(
            kind="ecdf",
            label="ECDF",
            question_group_id="distribution-inspection",
            role="Plots the empirical cumulative distribution of a value column with optional groups.",
            required_fields=["x"],
            optional_fields=["group"],
            uses_error=False,
            default_error="none",
            default_label="x_or_variable",
            legend_group_field="group",
            default_style=LayerStyle(color="#2563eb", linestyle="-", linewidth=1.8),
        ),
        "_ecdf_code",
    ),
    RegisteredRecipe(
        RecipeDefinition(
            kind="neuro.ephys.event_rate_timecourse",
            label="Ephys event-rate timecourse",
            question_group_id="neuro.ephys",
            role="Summarizes event or firing rate over time with optional condition groups.",
            required_fields=["x", "y"],
            optional_fields=["group"],
            legend_group_field="group",
            default_style=LayerStyle(color="#dc2626", marker="o", linestyle="-", linewidth=1.8),
        ),
        "_mean_sem_line_code",
    ),
]

_REGISTRY_BY_KIND = {entry.definition.kind: entry for entry in _RECIPE_REGISTRY}
_DEFINITIONS_BY_KIND = {kind: entry.definition for kind, entry in _REGISTRY_BY_KIND.items()}


def recipe_catalog() -> RecipeCatalogResponse:
    return RecipeCatalogResponse(
        version=CATALOG_VERSION,
        groups=list(_RECIPE_GROUPS),
        recipes=[entry.definition for entry in _RECIPE_REGISTRY],
    )


def recipe_definition(kind: RecipeKind) -> RecipeDefinition:
    return _DEFINITIONS_BY_KIND[kind]


def required_recipe_fields(kind: RecipeKind) -> list[RecipeDatasetField]:
    return list(recipe_definition(kind).required_fields)


def checked_recipe_fields(kind: RecipeKind) -> list[RecipeDatasetField]:
    definition = recipe_definition(kind)
    return list(dict.fromkeys([*definition.required_fields, *definition.optional_fields]))


def recipe_codegen_method(kind: RecipeKind) -> str:
    return _REGISTRY_BY_KIND[kind].codegen_method


def recipe_legend_group_field(kind: RecipeKind) -> RecipeDatasetField | None:
    return recipe_definition(kind).legend_group_field


def validate_catalog_complete() -> None:
    expected = set(get_args(RecipeKind))
    actual = set(_DEFINITIONS_BY_KIND)
    if expected != actual:
        missing = ", ".join(sorted(expected - actual)) or "none"
        extra = ", ".join(sorted(actual - expected)) or "none"
        raise RuntimeError(f"Recipe catalog mismatch; missing: {missing}; extra: {extra}")
    group_ids = {group.id for group in _RECIPE_GROUPS}
    invalid_groups = sorted(
        definition.question_group_id
        for definition in _DEFINITIONS_BY_KIND.values()
        if definition.question_group_id not in group_ids
    )
    if invalid_groups:
        raise RuntimeError(f"Recipe catalog references unknown groups: {', '.join(invalid_groups)}")


validate_catalog_complete()

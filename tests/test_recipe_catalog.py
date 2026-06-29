from __future__ import annotations

from typing import get_args

from fastapi.testclient import TestClient

from figstudio.models import RecipeKind
from figstudio.recipes import recipe_catalog
from figstudio.registry import VariableRegistry
from figstudio.server import create_app
from figstudio.session import FigStudioSession


def _recipe(payload: dict, kind: str) -> dict:
    return next(recipe for recipe in payload["recipes"] if recipe["kind"] == kind)


def test_bundled_recipe_catalog_covers_recipe_kind_contract():
    catalog = recipe_catalog()

    assert catalog.version == 1
    assert len(catalog.groups) == 6
    assert {recipe.kind for recipe in catalog.recipes} == set(get_args(RecipeKind))
    assert {recipe.question_group_id for recipe in catalog.recipes} <= {group.id for group in catalog.groups}
    assert any(group.id == "neuro.ephys" for group in catalog.groups)


def test_recipe_catalog_api_exposes_field_metadata():
    session = FigStudioSession(registry=VariableRegistry({}), port=8001)
    client = TestClient(create_app(session))

    response = client.get("/api/recipe-catalog")

    assert response.status_code == 200
    payload = response.json()
    assert payload["version"] == 1
    assert len(payload["groups"]) == 6
    assert any(group["id"] == "neuro.ephys" for group in payload["groups"])
    assert {recipe["kind"] for recipe in payload["recipes"]} == set(get_args(RecipeKind))

    stacked = _recipe(payload, "stacked_bar")
    assert stacked["required_fields"] == ["x", "group"]
    assert stacked["optional_fields"] == []
    assert stacked["uses_error"] is False
    assert stacked["default_error"] == "none"
    assert stacked["default_label"] == "count"
    assert stacked["legend_group_field"] == "group"
    assert stacked["default_style"]["alpha"] == 0.85

    count = _recipe(payload, "count_bar")
    assert count["required_fields"] == ["x"]
    assert count["optional_fields"] == ["group"]
    assert count["uses_error"] is False
    assert count["legend_group_field"] == "group"

    paired = _recipe(payload, "paired_before_after")
    assert paired["required_fields"] == ["x", "y", "subject"]
    assert paired["uses_error"] is True
    assert paired["default_error"] == "sem"
    assert paired["legend_group_field"] is None

    violin = _recipe(payload, "violin_by_category")
    assert violin["required_fields"] == ["x", "y"]
    assert violin["optional_fields"] == ["group"]
    assert violin["uses_error"] is False
    assert violin["default_style"]["linewidth"] == 1.1

    ecdf = _recipe(payload, "ecdf")
    assert ecdf["question_group_id"] == "distribution-inspection"
    assert ecdf["required_fields"] == ["x"]
    assert ecdf["optional_fields"] == ["group"]
    assert ecdf["uses_error"] is False
    assert ecdf["default_error"] == "none"
    assert ecdf["default_label"] == "x_or_variable"

    neuro = _recipe(payload, "neuro.ephys.event_rate_timecourse")
    assert neuro["question_group_id"] == "neuro.ephys"
    assert neuro["required_fields"] == ["x", "y"]
    assert neuro["optional_fields"] == ["group"]
    assert neuro["uses_error"] is True
    assert neuro["default_error"] == "sem"
    assert neuro["default_label"] == "y_or_variable"
    assert neuro["legend_group_field"] == "group"
    assert neuro["default_style"]["color"] == "#dc2626"

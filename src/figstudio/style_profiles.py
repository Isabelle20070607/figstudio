"""Project-level style profile loading and resolution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from pydantic import ValidationError

from figstudio.models import (
    FigureSpec,
    LayerStyle,
    PlotLayer,
    RecipeLayer,
    StyleProfile,
    StyleProfilesResponse,
)


PROFILE_CONFIG_PATH = Path(".figstudio") / "styles.json"
FIGURE_OVERRIDE_FIELDS = {
    "width",
    "height",
    "dpi",
    "font_family",
    "font_size",
    "constrained_layout",
}


def resolve_project_path(
    *,
    script_path: str | Path | None = None,
    project_path: str | Path | None = None,
) -> Path:
    if project_path is not None:
        return Path(project_path).expanduser().resolve()
    if script_path is not None:
        return Path(script_path).expanduser().resolve().parent
    return Path.cwd().resolve()


def load_style_profiles(project_path: str | Path) -> StyleProfilesResponse:
    config_path = Path(project_path) / PROFILE_CONFIG_PATH
    if not config_path.exists():
        return StyleProfilesResponse(source_path=str(config_path))

    warnings: list[str] = []
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return StyleProfilesResponse(
            source_path=str(config_path),
            warnings=[f"Could not read style profiles: {exc}"],
        )

    if not isinstance(payload, dict):
        return StyleProfilesResponse(
            source_path=str(config_path),
            warnings=["Style profile config must be a JSON object."],
        )

    version = payload.get("version")
    if version != 1:
        warnings.append(f"Unsupported style profile config version {version!r}; expected 1.")

    raw_profiles = payload.get("profiles", [])
    if not isinstance(raw_profiles, list):
        return StyleProfilesResponse(
            source_path=str(config_path),
            warnings=[*warnings, "Style profile config field 'profiles' must be a list."],
        )

    profiles: list[StyleProfile] = []
    seen_ids: set[str] = set()
    for index, raw_profile in enumerate(raw_profiles):
        try:
            profile = StyleProfile.model_validate(raw_profile)
        except ValidationError as exc:
            warnings.append(f"Skipped invalid style profile at index {index}: {exc.errors()[0]['msg']}")
            continue
        if profile.id in seen_ids:
            warnings.append(f"Skipped duplicate style profile id {profile.id!r}.")
            continue
        seen_ids.add(profile.id)
        profiles.append(profile)

    return StyleProfilesResponse(profiles=profiles, source_path=str(config_path), warnings=warnings)


def profile_map(
    profiles: Mapping[str, StyleProfile] | StyleProfilesResponse | list[StyleProfile] | None,
) -> dict[str, StyleProfile]:
    if profiles is None:
        return {}
    if isinstance(profiles, Mapping):
        return dict(profiles)
    if isinstance(profiles, StyleProfilesResponse):
        profile_list = profiles.profiles
    else:
        profile_list = profiles
    return {profile.id: profile for profile in profile_list}


def profile_for_spec(
    spec: FigureSpec,
    profiles: Mapping[str, StyleProfile] | StyleProfilesResponse | list[StyleProfile] | None,
) -> StyleProfile | None:
    if not spec.style.profile_id:
        return None
    return profile_map(profiles).get(spec.style.profile_id)


def missing_profile_issue_details(
    spec: FigureSpec,
    profiles: Mapping[str, StyleProfile] | StyleProfilesResponse | list[StyleProfile] | None,
) -> dict[str, Any] | None:
    if not spec.style.profile_id:
        return None
    available = sorted(profile_map(profiles))
    if spec.style.profile_id in available:
        return None
    return {"profile_id": spec.style.profile_id, "available_profiles": available}


def resolved_figure_value(
    spec: FigureSpec,
    profiles: Mapping[str, StyleProfile] | StyleProfilesResponse | list[StyleProfile] | None,
    field: str,
) -> Any:
    profile = profile_for_spec(spec, profiles)
    if profile is not None and field not in spec.style.profile_overrides:
        value = getattr(profile.figure, field, None)
        if value is not None:
            return value
    if field in {"font_family", "font_size", "constrained_layout"}:
        return getattr(spec.style, field)
    return getattr(spec, field)


def resolved_layer_style(
    spec: FigureSpec,
    layer: PlotLayer,
    profiles: Mapping[str, StyleProfile] | StyleProfilesResponse | list[StyleProfile] | None,
) -> LayerStyle:
    profile = profile_for_spec(spec, profiles)
    default_style = profile.layers.get(layer.kind) if profile else None
    return _merge_layer_style(default_style, layer.style)


def resolved_recipe_style(
    spec: FigureSpec,
    recipe: RecipeLayer,
    profiles: Mapping[str, StyleProfile] | StyleProfilesResponse | list[StyleProfile] | None,
) -> LayerStyle:
    profile = profile_for_spec(spec, profiles)
    default_style = profile.recipes.get(recipe.kind) if profile else None
    return _merge_layer_style(default_style, recipe.style)


def _merge_layer_style(default_style: LayerStyle | None, explicit_style: LayerStyle) -> LayerStyle:
    if default_style is None:
        return explicit_style
    merged = default_style.model_dump()
    for field, value in explicit_style.model_dump().items():
        if value is not None:
            merged[field] = value
    return LayerStyle.model_validate(merged)

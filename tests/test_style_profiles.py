from pathlib import Path

from fastapi.testclient import TestClient

from figstudio.codegen import MatplotlibCodegen
from figstudio.models import (
    DatasetRef,
    FigureSpec,
    FigureStyle,
    LayerStyle,
    PlotLayer,
    RecipeDatasetRef,
    RecipeLayer,
    StyleProfile,
    StyleProfileFigureDefaults,
)
from figstudio.render import RenderEngine
from figstudio.registry import VariableRegistry
from figstudio.server import create_app
from figstudio.session import FigStudioSession
from figstudio.style_profiles import load_style_profiles, profile_map


def _write_profile_config(project_path: Path) -> Path:
    config_path = project_path / ".figstudio" / "styles.json"
    config_path.parent.mkdir()
    config_path.write_text(
        """
{
  "version": 1,
  "profiles": [
    {
      "id": "paper",
      "label": "Paper",
      "description": "Paper defaults",
      "figure": {
        "width": 3.35,
        "height": 2.2,
        "dpi": 300,
        "font_family": "Arial",
        "font_size": 8,
        "constrained_layout": true
      },
      "layers": {
        "line": {
          "color": "#123456",
          "marker": "o",
          "linewidth": 2.2
        }
      },
      "recipes": {
        "mean_sem_line": {
          "color": "#654321",
          "marker": "s",
          "linewidth": 1.4
        }
      }
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )
    return config_path


def _profile() -> StyleProfile:
    return StyleProfile(
        id="paper",
        label="Paper",
        figure=StyleProfileFigureDefaults(
            width=3.35,
            height=2.2,
            dpi=300,
            font_family="Arial",
            font_size=8,
            constrained_layout=True,
        ),
        layers={"line": LayerStyle(color="#123456", marker="o", linewidth=2.2)},
        recipes={"mean_sem_line": LayerStyle(color="#654321", marker="s", linewidth=1.4)},
    )


def test_loads_project_style_profiles_from_config(tmp_path):
    config_path = _write_profile_config(tmp_path)

    response = load_style_profiles(tmp_path)

    assert response.source_path == str(config_path)
    assert response.warnings == []
    assert response.profiles[0].id == "paper"
    assert response.profiles[0].layers["line"].color == "#123456"


def test_session_infers_and_overrides_project_path(tmp_path):
    script_dir = tmp_path / "script-project"
    explicit_dir = tmp_path / "explicit-project"
    script_dir.mkdir()
    explicit_dir.mkdir()
    script = script_dir / "analysis.py"
    script.write_text("", encoding="utf-8")

    inferred = FigStudioSession(registry=VariableRegistry({}), script_path=str(script))
    explicit = FigStudioSession(
        registry=VariableRegistry({}),
        script_path=str(script),
        project_path=explicit_dir,
    )

    assert inferred.project_path == str(script_dir.resolve())
    assert explicit.project_path == str(explicit_dir.resolve())


def test_style_profiles_endpoint_exposes_loaded_profiles(tmp_path):
    config_path = _write_profile_config(tmp_path)
    session = FigStudioSession(registry=VariableRegistry({}), project_path=tmp_path)
    client = TestClient(create_app(session))

    response = client.get("/api/style-profiles")

    assert response.status_code == 200
    assert response.json()["source_path"] == str(config_path)
    assert response.json()["profiles"][0]["id"] == "paper"


def test_unknown_style_profile_validates_as_warning(tmp_path):
    _write_profile_config(tmp_path)
    session = FigStudioSession(registry=VariableRegistry({}), project_path=tmp_path)
    client = TestClient(create_app(session))
    spec = FigureSpec(style=FigureStyle(profile_id="missing"))

    response = client.post("/api/validate", json={"spec": spec.model_dump()})

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["issues"][0]["severity"] == "warning"
    assert response.json()["issues"][0]["code"] == "missing_style_profile"


def test_codegen_uses_profile_defaults_without_mutating_spec():
    spec = FigureSpec(
        style=FigureStyle(profile_id="paper"),
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(variable="values"),
            )
        ],
    )
    profiles = profile_map([_profile()])

    code = MatplotlibCodegen(style_profiles=profiles).generate(spec)

    assert "figsize=(3.35, 2.2), dpi=300" in code
    assert "with plt.rc_context({'font.family': 'Arial', 'font.size': 8.0}):" in code
    assert "color='#123456'" in code
    assert "marker='o'" in code
    assert spec.width == 6.4
    assert spec.layers[0].style.color is None


def test_figure_profile_overrides_supersede_profile_defaults():
    spec = FigureSpec(
        width=5.0,
        style=FigureStyle(profile_id="paper", profile_overrides=["width"]),
    )

    code = MatplotlibCodegen(style_profiles=profile_map([_profile()])).generate(spec)

    assert "figsize=(5.0, 2.2), dpi=300" in code


def test_recipe_profile_defaults_merge_by_kind():
    spec = FigureSpec(
        style=FigureStyle(profile_id="paper"),
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="mean_sem_line",
                dataset=RecipeDatasetRef(variable="df", x="condition", y="value"),
            )
        ],
    )

    code = MatplotlibCodegen(style_profiles=profile_map([_profile()])).generate(spec)

    assert "color='#654321'" in code
    assert "marker='s'" in code


def test_render_uses_profile_defaults():
    spec = FigureSpec(
        style=FigureStyle(profile_id="paper"),
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(variable="values"),
            )
        ],
    )
    profiles = profile_map([_profile()])

    svg, code = RenderEngine({"values": [1, 2, 3]}, style_profiles=profiles).render_base64(spec, "svg")

    assert "<svg" in svg
    assert "figsize=(3.35, 2.2), dpi=300" in code


def test_render_syncs_profiles_into_supplied_codegen():
    spec = FigureSpec(
        style=FigureStyle(profile_id="paper"),
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(variable="values"),
            )
        ],
    )
    profiles = profile_map([_profile()])

    svg, code = RenderEngine(
        {"values": [1, 2, 3]},
        MatplotlibCodegen(),
        style_profiles=profiles,
    ).render_base64(spec, "svg")

    assert "<svg" in svg
    assert "figsize=(3.35, 2.2), dpi=300" in code

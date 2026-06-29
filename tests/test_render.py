import pandas as pd

from figstudio.models import (
    AxesSpec,
    DatasetRef,
    FigureSpec,
    PlotLayer,
    RecipeDatasetRef,
    RecipeLayer,
    SecondaryYAxisSpec,
)
from figstudio.render import RenderEngine


def test_render_svg_from_generated_spec():
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(variable="values"),
            )
        ]
    )

    svg, code = RenderEngine({"values": [1, 2, 3]}).render_base64(spec, "svg")

    assert "<svg" in svg
    assert "axes_flat[0].plot" in code


def test_render_svg_from_spanned_layout():
    spec = FigureSpec(
        rows=2,
        cols=2,
        axes=[
            AxesSpec(id="ax0", row=0, col=0, rowspan=2, colspan=1),
            AxesSpec(id="ax1", row=0, col=1),
            AxesSpec(id="ax2", row=1, col=1),
        ],
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                axes_id="ax0",
                dataset=DatasetRef(variable="values"),
            )
        ],
    )

    svg, code = RenderEngine({"values": [1, 2, 3]}).render_base64(spec, "svg")

    assert "<svg" in svg
    assert "fig.add_gridspec(2, 2)" in code


def test_render_svg_from_secondary_y_axis_overlay():
    spec = FigureSpec(
        axes=[AxesSpec(id="ax0", secondary_y=SecondaryYAxisSpec(ylabel="Rate"))],
        layers=[
            PlotLayer(
                id="signal",
                kind="line",
                dataset=DatasetRef(variable="signal", x_variable="time", y_variable="signal"),
            ),
            PlotLayer(
                id="rate",
                kind="line",
                y_axis="right",
                dataset=DatasetRef(variable="rate", x_variable="time", y_variable="rate"),
            ),
        ],
    )

    svg, code = RenderEngine(
        {"time": [0, 1, 2], "signal": [0.1, 0.3, 0.2], "rate": [8.0, 10.0, 12.0]}
    ).render_base64(spec, "svg")

    assert "<svg" in svg
    assert "secondary_axes[0] = axes_flat[0].twinx()" in code
    assert "secondary_axes[0].plot(time, rate" in code


def test_render_svg_from_mean_sem_bar_recipe():
    df = pd.DataFrame(
        {
            "condition": ["control", "drug", "control", "drug"],
            "genotype": ["wt", "wt", "mut", "mut"],
            "response": [1.0, 1.4, 0.8, 1.1],
        }
    )
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="mean_sem_bar",
                dataset=RecipeDatasetRef(
                    variable="df",
                    x="condition",
                    y="response",
                    group="genotype",
                ),
            )
        ]
    )

    svg, code = RenderEngine({"df": df}).render_base64(spec, "svg")

    assert "<svg" in svg
    assert "axes_flat[0].bar(_recipe_recipe_1_positions" in code


def test_render_svg_from_count_bar_recipe():
    df = pd.DataFrame(
        {
            "condition": ["control", "drug", "control", "drug", "drug"],
            "genotype": ["wt", "wt", "mut", "mut", "wt"],
        }
    )
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="count_bar",
                dataset=RecipeDatasetRef(variable="df", x="condition", group="genotype"),
            )
        ]
    )

    svg, code = RenderEngine({"df": df}).render_base64(spec, "svg")

    assert "<svg" in svg
    assert "groupby(['condition', 'genotype'], sort=False).size().unstack(fill_value=0)" in code
    assert "axes_flat[0].bar(_recipe_recipe_1_positions" in code


def test_render_svg_from_stacked_bar_recipe():
    df = pd.DataFrame(
        {
            "condition": ["control", "drug", "control", "drug", "drug"],
            "genotype": ["wt", "wt", "mut", "mut", "wt"],
        }
    )
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="stacked_bar",
                dataset=RecipeDatasetRef(variable="df", x="condition", group="genotype"),
                error="none",
            )
        ]
    )

    svg, code = RenderEngine({"df": df}).render_base64(spec, "svg")

    assert "<svg" in svg
    assert "groupby(['condition', 'genotype'], sort=False).size().unstack(fill_value=0)" in code
    assert "bottom=_recipe_recipe_1_bottom" in code


def test_render_svg_from_boxplot_by_category_recipe():
    df = pd.DataFrame(
        {
            "condition": ["control", "control", "drug", "drug", "drug"],
            "genotype": ["wt", "mut", "wt", "mut", "wt"],
            "response": [1.0, 0.8, 1.4, 1.1, 1.6],
        }
    )
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="boxplot_by_category",
                dataset=RecipeDatasetRef(variable="df", x="condition", y="response", group="genotype"),
                error="none",
            )
        ]
    )

    svg, code = RenderEngine({"df": df}).render_base64(spec, "svg")

    assert "<svg" in svg
    assert "axes_flat[0].boxplot(_recipe_recipe_1_group_values" in code


def test_render_svg_from_violin_by_category_recipe():
    df = pd.DataFrame(
        {
            "condition": ["control", "control", "drug", "drug", "drug"],
            "genotype": ["wt", "mut", "wt", "mut", "wt"],
            "response": [1.0, 0.8, 1.4, 1.1, 1.6],
        }
    )
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="violin_by_category",
                dataset=RecipeDatasetRef(variable="df", x="condition", y="response", group="genotype"),
                error="none",
            )
        ]
    )

    svg, code = RenderEngine({"df": df}).render_base64(spec, "svg")

    assert "<svg" in svg
    assert "axes_flat[0].violinplot(_recipe_recipe_1_group_values" in code


def test_render_svg_from_ecdf_recipe():
    df = pd.DataFrame(
        {
            "condition": ["control", "control", "drug", "drug", "drug"],
            "response": [1.0, 0.8, 1.4, 1.1, 1.6],
        }
    )
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="ecdf",
                dataset=RecipeDatasetRef(variable="df", x="response", group="condition"),
                error="none",
            )
        ]
    )

    svg, code = RenderEngine({"df": df}).render_base64(spec, "svg")

    assert "<svg" in svg
    assert "dropna().sort_values().reset_index(drop=True)" in code
    assert "axes_flat[0].step(_recipe_recipe_1_values, _recipe_recipe_1_y, where='post'" in code


def test_render_svg_from_neuro_ephys_event_rate_timecourse_recipe():
    df = pd.DataFrame(
        {
            "condition": ["baseline", "baseline", "stim", "stim", "stim"],
            "time_s": [0, 1, 0, 1, 2],
            "event_rate_hz": [4.1, 4.4, 7.2, 8.1, 8.5],
        }
    )
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="neuro.ephys.event_rate_timecourse",
                dataset=RecipeDatasetRef(variable="df", x="time_s", y="event_rate_hz", group="condition"),
            )
        ]
    )

    svg, code = RenderEngine({"df": df}).render_base64(spec, "svg")

    assert "<svg" in svg
    assert "groupby('time_s', sort=False)['event_rate_hz'].agg(['mean', 'sem']).reindex" in code
    assert "axes_flat[0].errorbar(_recipe_recipe_1_x_order" in code

import pytest

from figstudio.codegen import MatplotlibCodegen
from figstudio.models import (
    AxesSpec,
    DataFilterSpec,
    DataSelectionSpec,
    DatasetRef,
    FigureSpec,
    LayerStyle,
    PlotLayer,
    RecipeDatasetRef,
    RecipeLayer,
    ReferenceLineSpec,
    SecondaryYAxisSpec,
)


@pytest.mark.parametrize(
    ("kind", "dataset", "expected"),
    [
        ("line", DatasetRef(variable="values"), ".plot("),
        ("scatter", DatasetRef(variable="values"), ".scatter("),
        ("bar", DatasetRef(variable="values"), ".bar("),
        ("barh", DatasetRef(variable="values"), ".barh("),
        ("hist", DatasetRef(variable="values"), ".hist("),
        ("boxplot", DatasetRef(variable="values"), ".boxplot("),
        ("violin", DatasetRef(variable="values"), ".violinplot("),
        ("errorbar", DatasetRef(variable="values", yerr_variable="errors"), ".errorbar("),
        ("heatmap", DatasetRef(variable="matrix"), ".imshow("),
        ("contour", DatasetRef(variable="matrix"), ".contour("),
        ("step", DatasetRef(variable="values"), ".step("),
        ("fill_between", DatasetRef(variable="values"), ".fill_between("),
    ],
)
def test_layer_registry_dispatches_each_plot_kind(kind, dataset, expected):
    spec = FigureSpec(layers=[PlotLayer(id=f"{kind}-layer", kind=kind, dataset=dataset)])

    code = MatplotlibCodegen().generate(spec)

    assert expected in code
    assert "figstudio" not in code.lower()


def test_generates_plain_oo_matplotlib_code_for_dataframe_line():
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(variable="df", x="time", y="value"),
                style=LayerStyle(label="Signal", color="#1f77b4", marker="o"),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "import matplotlib.pyplot as plt" in code
    assert "with plt.rc_context({'font.size': 10}):" in code
    assert "plt.rcParams" not in code
    assert "fig, axes = plt.subplots" in code
    assert "axes_flat[0].plot(df['time'], df['value']" in code
    assert "label='Signal'" in code
    assert "axes_flat[0].legend()" in code
    assert "figstudio" not in code.lower()


def test_dense_grid_keeps_subplots_codegen():
    spec = FigureSpec(
        rows=2,
        cols=2,
        axes=[
            AxesSpec(id="ax0", row=0, col=0),
            AxesSpec(id="ax1", row=0, col=1),
            AxesSpec(id="ax2", row=1, col=0),
            AxesSpec(id="ax3", row=1, col=1),
        ],
    )

    code = MatplotlibCodegen().generate(spec)

    assert "fig, axes = plt.subplots(2, 2" in code
    assert "fig.add_gridspec" not in code
    assert "axes_flat = axes.ravel()" in code


def test_dense_grid_can_share_axes():
    spec = FigureSpec(
        rows=1,
        cols=2,
        share_x=True,
        share_y=True,
        axes=[
            AxesSpec(id="ax0", row=0, col=0),
            AxesSpec(id="ax1", row=0, col=1),
        ],
    )

    code = MatplotlibCodegen().generate(spec)

    assert "sharex=True, sharey=True" in code


def test_generates_filtered_dataframe_layer_code():
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(
                    variable="df",
                    x="time",
                    y="signal",
                    filters=[DataFilterSpec(column="condition", value="drug", label="Drug")],
                ),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "_layer_layer_1_filtered_df = df" in code
    assert "_layer_layer_1_filtered_df[_layer_layer_1_filtered_df['condition'] == 'drug']" in code
    assert "axes_flat[0].plot(_layer_layer_1_filtered_df['time'], _layer_layer_1_filtered_df['signal']" in code
    assert "figstudio" not in code.lower()


def test_generates_selected_mapping_layer_code_before_plotting():
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(
                    variable="signal_map",
                    selection=DataSelectionSpec(kind="mapping_key", key=("control", 1), label="Control"),
                ),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "_layer_layer_1_selected = signal_map[('control', 1)]" in code
    assert "axes_flat[0].plot(range(len(_layer_layer_1_selected)), _layer_layer_1_selected" in code
    assert "figstudio" not in code.lower()


def test_generates_selected_sequence_dataframe_filter_code_before_plotting():
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(
                    variable="frames",
                    selection=DataSelectionSpec(kind="sequence_index", index=2, label="2"),
                    x="time",
                    y="signal",
                    filters=[DataFilterSpec(column="condition", value="drug", label="Drug")],
                ),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "_layer_layer_1_selected = frames[2]" in code
    assert "_layer_layer_1_filtered_df = _layer_layer_1_selected" in code
    assert "axes_flat[0].plot(_layer_layer_1_filtered_df['time'], _layer_layer_1_filtered_df['signal']" in code


def test_generates_null_filtered_recipe_code():
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="grouped_points",
                dataset=RecipeDatasetRef(
                    variable="df",
                    x="condition",
                    y="response",
                    filters=[DataFilterSpec(column="batch", value=None, label="Missing batch")],
                ),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "_recipe_recipe_1_filtered_df = df" in code
    assert "_recipe_recipe_1_filtered_df[_recipe_recipe_1_filtered_df['batch'].isna()]" in code
    assert "_recipe_recipe_1_df = _recipe_recipe_1_filtered_df" in code


def test_spanned_layout_uses_gridspec_codegen():
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

    code = MatplotlibCodegen().generate(spec)

    assert "fig = plt.figure" in code
    assert "grid = fig.add_gridspec(2, 2)" in code
    assert "fig.add_subplot(grid[0:2, 0])" in code
    assert "fig.add_subplot(grid[0, 1])" in code
    assert "axes_flat[0].plot" in code


def test_heatmap_adds_colorbar():
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="heat-1",
                kind="heatmap",
                dataset=DatasetRef(variable="matrix"),
                style=LayerStyle(cmap="magma"),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "imshow(matrix, cmap='magma')" in code
    assert "fig.colorbar(image_heat_1, ax=axes_flat[0])" in code


def test_heatmap_colorbar_can_be_disabled():
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="heat-1",
                kind="heatmap",
                dataset=DatasetRef(variable="matrix"),
                style=LayerStyle(cmap="magma", colorbar=False),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "imshow(matrix, cmap='magma')" in code
    assert "fig.colorbar(image_heat_1, ax=axes_flat[0])" not in code


def test_generates_code_for_independent_x_and_y_variables():
    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(
                    variable="signal",
                    x_variable="time",
                    y_variable="signal",
                ),
                style=LayerStyle(label="Signal"),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "axes_flat[0].plot(time, signal" in code
    assert code.count("axes_flat[0].legend()") == 1


def test_generates_secondary_y_axis_overlay_code():
    spec = FigureSpec(
        axes=[
            AxesSpec(
                id="ax0",
                ylabel="Signal",
                secondary_y=SecondaryYAxisSpec(ylabel="Rate", yscale="log", ylim=(1.0, None)),
            )
        ],
        layers=[
            PlotLayer(
                id="signal-layer",
                kind="line",
                dataset=DatasetRef(variable="df", x="time", y="signal"),
                style=LayerStyle(label="Signal", color="#2563eb"),
            ),
            PlotLayer(
                id="rate-layer",
                kind="line",
                y_axis="right",
                dataset=DatasetRef(variable="df", x="time", y="rate"),
                style=LayerStyle(label="Rate", color="#dc2626"),
            ),
        ],
    )

    code = MatplotlibCodegen().generate(spec)

    assert "secondary_axes = {}" in code
    assert "secondary_axes[0] = axes_flat[0].twinx()" in code
    assert "secondary_axes[0].set_ylabel('Rate')" in code
    assert "secondary_axes[0].set_yscale('log')" in code
    assert "secondary_axes[0].set_ylim((1.0, None))" in code
    assert "axes_flat[0].plot(df['time'], df['signal']" in code
    assert "secondary_axes[0].plot(df['time'], df['rate']" in code
    assert "axes_flat[0].legend(primary_handles_0 + secondary_handles_0" in code
    assert "figstudio" not in code.lower()


def test_axis_can_disable_legend_for_labeled_layers():
    spec = FigureSpec(
        axes=[{"id": "ax0", "legend": False}],
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(variable="values"),
                style=LayerStyle(label="Values"),
            )
        ],
    )

    code = MatplotlibCodegen().generate(spec)

    assert "label='Values'" in code
    assert ".legend()" not in code


def test_generates_reference_line_code_and_legend():
    spec = FigureSpec(
        reference_lines=[
            ReferenceLineSpec(
                id="baseline",
                orientation="horizontal",
                value=0.0,
                style=LayerStyle(
                    label="Baseline",
                    color="#6b7280",
                    linestyle="--",
                    linewidth=1.2,
                    alpha=0.8,
                ),
            ),
            ReferenceLineSpec(
                id="cutoff",
                orientation="vertical",
                value=2.5,
                style=LayerStyle(label="Cutoff", color="#dc2626"),
            ),
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "axes_flat[0].axhline(0.0" in code
    assert "axes_flat[0].axvline(2.5" in code
    assert "label='Baseline'" in code
    assert "linestyle='--'" in code
    assert "label='Cutoff'" in code
    assert code.count("axes_flat[0].legend()") == 1
    assert "figstudio" not in code.lower()


def test_generates_mean_sem_line_recipe_code():
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="mean_sem_line",
                dataset=RecipeDatasetRef(variable="df", x="time", y="signal", group="condition"),
                style=LayerStyle(label="Signal", color="#2563eb", marker="o"),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "_recipe_recipe_1_df = df" in code
    assert "groupby('time', sort=False)['signal'].agg(['mean', 'sem'])" in code
    assert "label=f'Signal {_recipe_recipe_1_group}'" in code
    assert "axes_flat[0].legend()" in code
    assert "figstudio" not in code.lower()


def test_generates_mean_sem_bar_recipe_code():
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="mean_sem_bar",
                dataset=RecipeDatasetRef(variable="df", x="condition", y="response", group="genotype"),
                style=LayerStyle(label="Response", color="#0f766e"),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "_recipe_recipe_1_x_order = list(dict.fromkeys" in code
    assert "_recipe_recipe_1_bar_width = 0.8 / max(len(_recipe_recipe_1_groups), 1)" in code
    assert "groupby('condition', sort=False)['response'].agg(['mean', 'sem'])" in code
    assert "axes_flat[0].bar(_recipe_recipe_1_positions, _recipe_recipe_1_summary['mean']" in code
    assert "label=f'Response {_recipe_recipe_1_group}'" in code
    assert "capsize=4" in code
    assert "set_xticklabels([str(value) for value in _recipe_recipe_1_x_order])" in code
    assert "figstudio" not in code.lower()


def test_generates_count_bar_recipe_code():
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="count_bar",
                dataset=RecipeDatasetRef(variable="df", x="condition"),
                style=LayerStyle(label="Cells", color="#0f766e"),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "_recipe_recipe_1_x_order = list(dict.fromkeys" in code
    assert "groupby('condition', sort=False).size().reindex(_recipe_recipe_1_x_order, fill_value=0)" in code
    assert "axes_flat[0].bar(_recipe_recipe_1_x, _recipe_recipe_1_counts" in code
    assert "label='Cells'" in code
    assert "set_xticklabels([str(value) for value in _recipe_recipe_1_x_order])" in code
    assert "figstudio" not in code.lower()


def test_generates_grouped_count_bar_recipe_code():
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="count_bar",
                dataset=RecipeDatasetRef(variable="df", x="condition", group="genotype"),
                style=LayerStyle(label="Cells", color="#0f766e"),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "groupby(['condition', 'genotype'], sort=False).size().unstack(fill_value=0)" in code
    assert "_recipe_recipe_1_counts = _recipe_recipe_1_counts.reindex(index=_recipe_recipe_1_x_order" in code
    assert "_recipe_recipe_1_counts = _recipe_recipe_1_counts.reindex(columns=_recipe_recipe_1_groups" in code
    assert "_recipe_recipe_1_bar_width = 0.8 / max(len(_recipe_recipe_1_groups), 1)" in code
    assert "axes_flat[0].bar(_recipe_recipe_1_positions, _recipe_recipe_1_counts[_recipe_recipe_1_group]" in code
    assert "label=f'Cells {_recipe_recipe_1_group}'" in code
    assert "figstudio" not in code.lower()


def test_generates_stacked_bar_recipe_code():
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="stacked_bar",
                dataset=RecipeDatasetRef(variable="df", x="condition", group="genotype"),
                style=LayerStyle(label="Cells", color="#0f766e"),
                error="none",
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "groupby(['condition', 'genotype'], sort=False).size().unstack(fill_value=0)" in code
    assert "_recipe_recipe_1_bottom = [0] * len(_recipe_recipe_1_x_order)" in code
    assert "axes_flat[0].bar(_recipe_recipe_1_x, _recipe_recipe_1_counts[_recipe_recipe_1_group]" in code
    assert "bottom=_recipe_recipe_1_bottom" in code
    assert "label=f'Cells {_recipe_recipe_1_group}'" in code
    assert "axes_flat[0].legend()" in code
    assert "figstudio" not in code.lower()


def test_generates_boxplot_by_category_recipe_code():
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="boxplot_by_category",
                dataset=RecipeDatasetRef(variable="df", x="condition", y="response", group="genotype"),
                style=LayerStyle(label="Response", color="#0f766e", marker="o", alpha=0.35),
                error="none",
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "_recipe_recipe_1_x_order = list(dict.fromkeys" in code
    assert "_recipe_recipe_1_group_values = []" in code
    assert "_recipe_recipe_1_group_positions.append" in code
    assert "axes_flat[0].boxplot(_recipe_recipe_1_group_values" in code
    assert "patch_artist=True" in code
    assert "showmeans=True" in code
    assert "label=f'Response {_recipe_recipe_1_group}'" in code
    assert "set_xticklabels([str(value) for value in _recipe_recipe_1_x_order])" in code
    assert "figstudio" not in code.lower()


def test_generates_violin_by_category_recipe_code():
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="violin_by_category",
                dataset=RecipeDatasetRef(variable="df", x="condition", y="response", group="genotype"),
                style=LayerStyle(label="Response", color="#0f766e", alpha=0.34, linewidth=1.1),
                error="none",
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "_recipe_recipe_1_x_order = list(dict.fromkeys" in code
    assert "_recipe_recipe_1_group_values = []" in code
    assert "_recipe_recipe_1_group_positions.append" in code
    assert "axes_flat[0].violinplot(_recipe_recipe_1_group_values" in code
    assert "showmeans=True" in code
    assert "showmedians=True" in code
    assert "_recipe_recipe_1_body.set_facecolor('#0f766e')" in code
    assert "label=f'Response {_recipe_recipe_1_group}'" in code
    assert "set_xticklabels([str(value) for value in _recipe_recipe_1_x_order])" in code
    assert "figstudio" not in code.lower()


def test_generates_grouped_points_recipe_code():
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="grouped_points",
                dataset=RecipeDatasetRef(variable="df", x="condition", y="response"),
                style=LayerStyle(label="Response", color="#0f766e", marker="o"),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "_recipe_recipe_1_order = list(dict.fromkeys" in code
    assert "axes_flat[0].scatter(_recipe_recipe_1_x, _recipe_recipe_1_values" in code
    assert ".hlines(_recipe_recipe_1_mean" in code
    assert "set_xticklabels([str(value) for value in _recipe_recipe_1_order])" in code


def test_generates_paired_before_after_recipe_code():
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="paired_before_after",
                dataset=RecipeDatasetRef(
                    variable="df",
                    x="condition",
                    y="response",
                    subject="subject",
                ),
                style=LayerStyle(label="Response", color="#dc2626", marker="o"),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "_recipe_recipe_1_subjects = list(dict.fromkeys" in code
    assert "groupby('condition', sort=False)['response'].mean().reindex" in code
    assert "axes_flat[0].plot(_recipe_recipe_1_x, _recipe_recipe_1_paired.tolist()" in code
    assert "axes_flat[0].errorbar(_recipe_recipe_1_x, _recipe_recipe_1_summary['mean']" in code


def test_generates_ecdf_recipe_code():
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="recipe-1",
                kind="ecdf",
                dataset=RecipeDatasetRef(variable="df", x="response", group="condition"),
                style=LayerStyle(label="Response", color="#2563eb"),
                error="none",
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "_recipe_recipe_1_groups = list(dict.fromkeys" in code
    assert (
        "_recipe_recipe_1_values = "
        "_recipe_recipe_1_group_df['response'].dropna().sort_values().reset_index(drop=True)"
        in code
    )
    assert "_recipe_recipe_1_y = [(index + 1) / len(_recipe_recipe_1_values)" in code
    assert "axes_flat[0].step(_recipe_recipe_1_values, _recipe_recipe_1_y, where='post'" in code
    assert "label=f'Response {_recipe_recipe_1_group}'" in code


def test_generates_neuro_ephys_event_rate_timecourse_code():
    spec = FigureSpec(
        recipes=[
            RecipeLayer(
                id="event-rate",
                kind="neuro.ephys.event_rate_timecourse",
                dataset=RecipeDatasetRef(variable="df", x="time_s", y="event_rate_hz", group="condition"),
                style=LayerStyle(label="Event rate", color="#dc2626", marker="o"),
            )
        ]
    )

    code = MatplotlibCodegen().generate(spec)

    assert "import matplotlib.pyplot as plt" in code
    assert "figstudio" not in code.lower()
    assert "_recipe_event_rate_groups = list(dict.fromkeys" in code
    assert "groupby('time_s', sort=False)['event_rate_hz'].agg(['mean', 'sem']).reindex" in code
    assert "axes_flat[0].errorbar(_recipe_event_rate_x_order" in code
    assert "label=f'Event rate {_recipe_event_rate_group}'" in code

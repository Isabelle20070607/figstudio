# Scientific Workflows

FigStudio is strongest when the scientific data work is already done and you want a faster, reproducible path from prepared variables to a polished Matplotlib panel.

## Plot Layers

Use plot layers for direct visual encodings from live variables.

Supported public beta plot kinds are `line`, `scatter`, `bar`, `barh`, `hist`, `boxplot`, `violin`, `errorbar`, `heatmap`, `contour`, `step`, and `fill_between`.

For DataFrame columns, usually use the same DataFrame as the X and Y source, then choose columns. For independent arrays or lists, use `index` for X or choose another variable as the X source.

Single-value-source plots such as `hist`, `boxplot`, and `violin` use the Y/value source; generated code ignores X. `errorbar` can use an optional Y error source. `heatmap` and `contour` work best with 2D ndarray data or gridded values.

## Statistics Recipes

Use recipe mode when the selected variable is a pandas DataFrame and you want a common statistical figure without writing the plotting boilerplate.

Bundled recipes:

| Recipe | Use it for |
| --- | --- |
| `mean_sem_line` | Group by X and optional group column, compute mean plus SEM or SD, then draw a line with error bars. |
| `mean_sem_bar` | Group by X and optional group column, compute mean plus SEM or SD, then draw categorical bars with error caps. |
| `count_bar` | Count rows by X category and optional group column, then draw categorical frequency bars. |
| `stacked_bar` | Count rows by X category and required group column, then draw stacked categorical bars. |
| `grouped_points` | Preserve first-seen category order, scatter individual points by category, and overlay mean plus SEM or SD. |
| `paired_before_after` | Group paired observations by subject, draw subject traces, and overlay condition means. |

Recipes store variable names, column names, style choices, and target axes in the `FigureSpec`. They do not store raw DataFrame data. `count_bar` uses X and optional group columns only; `stacked_bar` uses X plus group columns; value/error columns are ignored for both. Generated code still imports Matplotlib only and computes statistics from your live DataFrame variable.

Try `examples/general_stats_recipe.py` to exercise the bundled recipes with synthetic repeated-measures data.

## Faceted Panels

Use **Facet panels** in the Explore builder when a plot layer or statistics recipe is backed by a pandas DataFrame. Choose a categorical DataFrame column, a panel limit, and shared-axis options; FigStudio creates one axes per first-seen value and adds filtered layers or recipes to those axes.

Facet specs stay data-light. They store equality filters such as `condition == "drug"`, display labels, target axes, and shared-axis flags, not DataFrame rows. Generated code filters the live DataFrame variable with pandas expressions before calling Matplotlib.

For normal plot layers, the same repeated-panel controls also work with mapping and sequence sources. A mapping source repeats by literal-safe keys, and a list or tuple repeats by item index. FigStudio stores a `DatasetRef.selection`, selects the live item before plotting, and skips candidates that are not compatible with the current layer settings.

Mapping and sequence repeated panels are intentionally v1-scoped: use index X or an independent X variable, and do not use same-source selected X or Y-error channels yet. Statistics recipes remain DataFrame-only.

## Secondary Y-Axis Overlays

Use a secondary Y axis when two related measures need to share one panel and X scale, such as signal amplitude plus event rate. Add the primary plot layer normally, add the overlay layer, then set that layer's **Y axis** control to **Right** in the polish panel.

The active axes exposes right-side label, scale, and limit controls. FigStudio stores `PlotLayer.y_axis: "right"` on the overlay layer and `AxesSpec.secondary_y` for the right-side axis settings. Generated code creates one Matplotlib `twinx()` axes for that panel and combines primary plus secondary legend entries when the panel legend is enabled.

The first beta slice supports simple overlay plot layers: `line`, `scatter`, `bar`, `hist`, `errorbar`, `step`, and `fill_between`. Statistics recipes, reference lines, heatmaps, contours, horizontal bars, boxplots, and violins stay on the primary Y axis for now.

## Publication Polish

Use **Publish** mode when you are preparing manuscript or presentation output. It exposes publication-oriented controls such as font family and constrained layout while preserving the same generated-code path as **Explore** mode.

In **Publish** mode and before export, FigStudio runs deterministic publication-readiness checks. These checks warn about empty data-bearing figures, missing axis labels, unlabeled secondary Y axes, missing legend labels when multiple visual items share an axes, and low-resolution PNG settings. Readiness warnings are advisory: they appear in the validation card list, but export continues unless the figure also has validation errors.

The right-side polish panel covers:

- figure size, DPI, title, font settings, built-in presets, and project style profile;
- panel layout rows, columns, shared-axis options, and presets;
- axes titles, labels, scales, limits, secondary Y-axis settings, grid, legend, and colorbar fallback;
- layer and recipe target axes, layer left/right Y-axis target, labels, colors, markers, line styles, linewidths, alpha, colormap, histogram bins, and fill alpha;
- horizontal and vertical reference lines for baselines, thresholds, cutoff markers, and guide labels;
- text and arrow annotations on the active axes.

## Reference Lines

Use **Reference lines** to add horizontal or vertical guide lines to the active axes. They are useful for baselines, thresholds, cutoff values, and other cross-domain constants that should stay independent from the plotted data.

Reference lines store an orientation, numeric value, optional legend label, color, line style, linewidth, and alpha in the `FigureSpec`. Generated code uses Matplotlib `axhline` or `axvline`, so previews, exports, and saved code stay on the same path.

## Annotations

Use **Annotations** to add text labels or arrow callouts to the active axes. Annotation coordinates are data coordinates on the selected axes.

Text annotations generate `annotate(text, xy=(x, y))`. Arrow annotations also set `xytext` and `arrowprops`.

## Existing Matplotlib Figures

You can pass an existing Matplotlib `Figure`:

```python
figstudio.open(locals(), figure=fig)
```

The public beta inspects supported line, scatter, image, and bar artists and recreates editable generated layers when enough data is available. Unsupported artists remain best-effort metadata and should be treated as read-only context, not recovered source code.

Histograms, boxplots, violins, legends, and colorbars may appear as metadata unless the current `FigureSpec` model can reproduce them honestly.

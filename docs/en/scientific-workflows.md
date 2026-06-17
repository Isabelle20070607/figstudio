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
| `grouped_points` | Preserve first-seen category order, scatter individual points by category, and overlay mean plus SEM or SD. |
| `paired_before_after` | Group paired observations by subject, draw subject traces, and overlay condition means. |

Recipes store variable names, column names, style choices, and target axes in the `FigureSpec`. They do not store raw DataFrame data. Generated code still imports Matplotlib only and computes statistics from your live DataFrame variable.

Try `examples/general_stats_recipe.py` to exercise all three bundled recipes with synthetic repeated-measures data.

## Publication Polish

Use **Publish** mode when you are preparing manuscript or presentation output. It exposes publication-oriented controls such as font family and constrained layout while preserving the same generated-code path as **Explore** mode.

The right-side polish panel covers:

- figure size, DPI, title, font settings, built-in presets, and project style profile;
- panel layout rows, columns, and presets;
- axes titles, labels, scales, limits, grid, legend, and colorbar fallback;
- layer and recipe target axes, labels, colors, markers, line styles, linewidths, alpha, colormap, histogram bins, and fill alpha;
- text and arrow annotations on the active axes.

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

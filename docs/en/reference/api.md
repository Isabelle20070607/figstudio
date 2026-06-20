# API Reference

This reference documents the current public beta API surface. Future capabilities belong in the [roadmap](../product/roadmap.md).

## Python API

```python
figstudio.open(
    namespace=None,
    *,
    figure=None,
    script_path=None,
    project_path=None,
    block_id="main",
    mode="auto",
    open_browser=True,
) -> FigStudioSession
```

| Parameter | Meaning |
| --- | --- |
| `namespace` | Usually `locals()`. Supported public values are summarized for the UI; live objects stay server-side. |
| `figure` | Optional Matplotlib `Figure` for best-effort inspection. |
| `script_path` | Enables controlled `.py` writeback. |
| `project_path` | Project root for `.figstudio/styles.json`; defaults to `Path(script_path).parent` or current working directory. |
| `block_id` | Selects `# figstudio:start <block_id>` and `# figstudio:end <block_id>`. |
| `mode` | Session metadata for editor mode selection. |
| `open_browser` | Opens the local editor URL when true. |

```python
figstudio.save_spec(spec, path) -> pathlib.Path
figstudio.load_spec(path) -> FigureSpec
```

`save_spec` accepts a `FigureSpec` or compatible dict and writes UTF-8 JSON. `load_spec` validates JSON into `FigureSpec`.

## CLI

```powershell
figstudio --version
figstudio --no-browser
figstudio --port 8767 --no-browser
figstudio --project G:\workspace\figstudio --no-browser
figstudio demo
figstudio demo --project G:\workspace\figstudio --port 8767 --no-browser
```

The CLI prints the session URL and runs until interrupted.

## FigureSpec

`FigureSpec` is the JSON-serializable editor state and codegen input.

| Field | Meaning |
| --- | --- |
| `version` | Spec format marker, currently defaulting to `1`. |
| `mode` | `explore` or `publish`. |
| `width`, `height`, `dpi` | Figure size and render/export DPI. |
| `rows`, `cols`, `share_x`, `share_y`, `axes` | Panel layout grid, shared-axis flags, axes geometry, and primary/secondary axis metadata. |
| `layers` | Plot layer definitions. |
| `recipes` | Statistics recipe definitions. |
| `reference_lines` | Horizontal and vertical guide lines for baselines, thresholds, and cutoff labels. |
| `annotations` | Text and arrow annotations. |
| `style` | Figure title, font, layout, built-in preset, and project profile reference. |
| `show` | Whether generated code calls `plt.show()`. |

Supported `PlotLayer.kind` values are `line`, `scatter`, `bar`, `barh`, `hist`, `boxplot`, `violin`, `errorbar`, `heatmap`, `contour`, `step`, and `fill_between`.

`PlotLayer.y_axis` is `left` by default. Set it to `right` for simple secondary Y-axis overlays on the same `axes_id`; `AxesSpec.secondary_y` stores the right-side `ylabel`, `yscale`, and `ylim`. Generated code emits Matplotlib `twinx()` for panels that have at least one right-axis layer.

Supported `RecipeLayer.kind` values are `mean_sem_line`, `mean_sem_bar`, `grouped_points`, and `paired_before_after`.

`ReferenceLineSpec.orientation` is `horizontal` or `vertical`. The `value` field is numeric and `style` uses the same label, color, line style, linewidth, and alpha fields as plot layers. Generated code emits Matplotlib `axhline` or `axvline`.

`DatasetRef` fields can point to DataFrame columns or independent variables through `x_variable`, `y_variable`, `z_variable`, and `yerr_variable`. Normal plot layers can also set `DatasetRef.selection` with `kind: "mapping_key"` or `kind: "sequence_index"` so repeated panels can select an item before plotting. `RecipeDatasetRef.variable` must name a pandas DataFrame and stores column names only. Both dataset refs can include `filters`; each `DataFilterSpec` stores `column`, `op: "eq"`, `value`, and optional `label` for DataFrame-backed facet panels.

`FigureStyle.profile_id` references a project style profile. `FigureStyle.profile_overrides` lists figure fields that should use explicit spec values instead of profile defaults: `width`, `height`, `dpi`, `font_family`, `font_size`, and `constrained_layout`.

## REST API

The local FastAPI server is created per session and binds to `127.0.0.1` by default.

| Endpoint | Purpose |
| --- | --- |
| `GET /api/session` | Session metadata, writeback capability, optional inspected figure tree. |
| `GET /api/variables` | Safe variable summaries. |
| `GET /api/style-profiles` | Loaded project style profiles, source path, and non-fatal load warnings. |
| `GET /api/spec` | Current `FigureSpec`. |
| `POST /api/validate` | Validate a `FigureSpec` against the live namespace. |
| `POST /api/facet-values` | Return ordered unique DataFrame values for small-multiple panel authoring. |
| `POST /api/repeated-panel-candidates` | Return DataFrame values, mapping keys, or sequence indices plus bounded item summaries for repeated-panel authoring. |
| `POST /api/spec` | Store the current spec, validate it, and return an SVG render response. |
| `POST /api/render` | Render SVG or PNG preview. |
| `POST /api/save-code` | Write a controlled script block or return notebook replacement code. |
| `POST /api/export` | Return base64 PNG/SVG/PDF export data or write to an explicit output path. |
| `WS /api/events` | Lightweight connected/ack channel reserved for editor events. |

`POST /api/save-code` returns HTTP 200 even for writeback failures so the response can include generated code and an error object.

## Error Payloads

HTTP errors use:

```json
{
  "detail": {
    "error": {
      "code": "validation_failed",
      "message": "FigureSpec has validation errors.",
      "details": {}
    }
  }
}
```

Current error codes are `validation_failed`, `render_failed`, `export_failed`, `writeback_failed`, `writeback_io_failed`, `missing_variable`, `missing_column`, `unsupported_facet_source`, and `unsupported_repeated_panel_source`. Writeback errors appear inside `SaveCodeResponse.error`; render, export, validation, facet-value, and repeated-panel candidate failures are HTTP errors.

Validation issue codes include `missing_style_profile`, `invalid_grid_size`, `duplicate_axes_id`, `invalid_axes_span`, `axes_out_of_bounds`, `axes_overlap`, `missing_axes`, `missing_variable`, `missing_column`, `unsupported_recipe_source`, `unsupported_filter_source`, `empty_filter_result`, `unsupported_selection_source`, `unsupported_selection_key`, `missing_selection_key`, `selection_index_out_of_range`, `unsupported_selected_channel`, `unplottable_selection_value`, `dimension_mismatch`, `requires_2d_data`, `log_scale_non_positive`, `unsupported_secondary_y_layer`, and `invalid_reference_line_value`.

Each validation issue may include `suggestion` for UI repair guidance. `details` can include bounded context such as `available_variables`, `available_columns`, `available_axes`, `available_profiles`, and `suggested_value`; it does not include raw DataFrame contents.

## Compatibility Notes

- Generated plotting code must run without importing FigStudio.
- Generated recipe code may call methods on existing pandas DataFrame variables, but imports remain limited to Matplotlib.
- Saved FigureSpec files depend on compatible variable names, mapping keys, sequence indices, DataFrame columns, and data shapes in the next session.
- Saved recipe, facet, repeated-panel, and secondary-axis specs store column mappings, equality filters, selections, labels, axis settings, and recipe intent, not raw data.
- Saved reference line specs store numeric constants and style only, not derived data.
- Runtime wheel installs should not require Node/npm.
- Notebook workflows return code and do not directly edit notebook files.

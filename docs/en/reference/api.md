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
| `rows`, `cols`, `axes` | Panel layout grid and axes geometry. |
| `layers` | Plot layer definitions. |
| `recipes` | Statistics recipe definitions. |
| `annotations` | Text and arrow annotations. |
| `style` | Figure title, font, layout, built-in preset, and project profile reference. |
| `show` | Whether generated code calls `plt.show()`. |

Supported `PlotLayer.kind` values are `line`, `scatter`, `bar`, `barh`, `hist`, `boxplot`, `violin`, `errorbar`, `heatmap`, `contour`, `step`, and `fill_between`.

Supported `RecipeLayer.kind` values are `mean_sem_line`, `grouped_points`, and `paired_before_after`.

`DatasetRef` fields can point to DataFrame columns or independent variables through `x_variable`, `y_variable`, `z_variable`, and `yerr_variable`. `RecipeDatasetRef.variable` must name a pandas DataFrame and stores column names only.

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

Current error codes are `validation_failed`, `render_failed`, `export_failed`, `writeback_failed`, and `writeback_io_failed`. Writeback errors appear inside `SaveCodeResponse.error`; render, export, and validation failures are HTTP errors.

Validation issue codes include `missing_style_profile`, `invalid_grid_size`, `duplicate_axes_id`, `invalid_axes_span`, `axes_out_of_bounds`, `axes_overlap`, `missing_axes`, `missing_variable`, `missing_column`, `unsupported_recipe_source`, `dimension_mismatch`, `requires_2d_data`, and `log_scale_non_positive`.

Each validation issue may include `suggestion` for UI repair guidance. `details` can include bounded context such as `available_variables`, `available_columns`, `available_axes`, `available_profiles`, and `suggested_value`; it does not include raw DataFrame contents.

## Compatibility Notes

- Generated plotting code must run without importing FigStudio.
- Generated recipe code may call methods on existing pandas DataFrame variables, but imports remain limited to Matplotlib.
- Saved FigureSpec files depend on compatible variable names, DataFrame columns, and data shapes in the next session.
- Saved recipe specs store column mappings and recipe intent, not raw data.
- Runtime wheel installs should not require Node/npm.
- Notebook workflows return code and do not directly edit notebook files.

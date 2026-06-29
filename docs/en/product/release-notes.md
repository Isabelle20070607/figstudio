# Release Notes / What's New

This page is the user-facing release summary for published FigStudio versions.
For the full chronological record and release evidence, see
[CHANGELOG.md](../../../CHANGELOG.md).

## 0.4.0 - 2026-06-29

Focus: richer scientific authoring, more bundled recipes, gallery proof, and
headless automation.

What's new:

- Repeated panels can now be built from DataFrame facets, mapping keys, or
  sequence items while generated code remains plain Matplotlib.
- Plot layers can target a secondary right Y axis for overlays such as raw
  traces plus summary rates.
- New bundled recipes cover categorical bars, count bars, stacked bars,
  grouped boxplots, grouped violins, ECDF distribution inspection, and the
  first experimental `neuro.ephys.event_rate_timecourse` workflow.
- Recipe and layer catalogs now expose structured metadata for the editor,
  validation, generated code, and API clients.
- The CLI now supports deterministic `validate`, `render`, `export`, and
  `codegen` commands for `.figstudio.json` specs.
- The gallery now includes source scripts, portable specs, and SVG proof for
  repeated panels, secondary axes, category distributions, ECDF, stacked
  composition, GridSpec spans, and neuro ephys event rates.
- Publication-readiness advisories now catch more final-mile issues before
  export, including missing data-bearing content, weak labels, legend crowding,
  and low-resolution PNG settings.
- Notebook-style sessions have a smoother prepare-cell handoff without
  silently editing notebook files.

Upgrade notes:

- Existing `.figstudio.json` specs remain compatible.
- Active roadmap docs now list future work only; shipped 0.4.0 details are
  recorded here and in `CHANGELOG.md`.
- Use `pip install --upgrade figstudio` to install the latest published wheel.

## 0.3.1 - 2026-06-18

Focus: validation repair suggestions and desktop workspace fit.

What's new:

- Validation issue cards now show `Suggested fix: ...` text from the backend
  when FigStudio can infer a likely repair.
- Missing variables, missing DataFrame columns, missing axes, invalid panel
  layout spans, missing style profiles, and log-scale positivity warnings now
  include more actionable guidance.
- Validation payloads can include bounded context such as available variables,
  DataFrame columns, axes ids, profile ids, and a suggested replacement value.
- Desktop fullscreen sessions keep the editor shell inside the viewport, with
  scrolling contained inside the preview area instead of the whole page.
- Browser smoke tests now guard against the desktop code panel falling below
  the viewport.

Upgrade notes:

- Existing `.figstudio.json` specs remain compatible.
- Use `pip install --upgrade figstudio` to install the latest published wheel.

## 0.3.0 - 2026-06-18

Focus: style governance, panel layouts, bilingual docs, and release hardening.

What's new:

- Projects can define shared style defaults in `.figstudio/styles.json`.
- `figstudio.open(..., project_path=...)`, CLI `--project`, and
  `GET /api/style-profiles` now expose the active project style profile root.
- Specs can reference `style.profile_id` and record explicit
  `style.profile_overrides` instead of copying every default into the spec.
- Render, export, and generated code resolve project profile defaults for
  figure, layer, and recipe styles.
- Panel layout presets now support spanned axes through `rowspan` and
  `colspan`; generated code uses `GridSpec` only when needed.
- Documentation is now split into paired English and Chinese trees.
- Browser smoke coverage includes a real project style profile fixture.

Upgrade notes:

- Existing specs without profiles continue to work.
- Specs that reference a missing profile produce a warning and fall back to
  explicit spec values and defaults.
- Use `pip install --upgrade figstudio` to install the latest published wheel.

## 0.2.0 - 2026-06-17

Focus: general statistics recipes for pandas DataFrames.

What's new:

- Added three bundled recipe kinds: `mean_sem_line`, `grouped_points`, and
  `paired_before_after`.
- Added a recipe builder in the editor for selecting DataFrames, columns,
  grouping, subject identifiers, error style, and target axes.
- Generated recipe code stays plain Matplotlib and computes statistics from
  the user's existing DataFrame variable.
- Recipe validation reports non-DataFrame sources and missing columns before
  render/export.
- Added `examples/general_stats_recipe.py` and recipe smoke coverage.

Upgrade notes:

- Recipes require pandas DataFrame inputs.
- Recipe specs store variable names, column mappings, style, target axes, and
  recipe kind, not raw DataFrame data.

## 0.1.0 - 2026-06-16

Focus: first public beta on PyPI.

What's new:

- Installable package with `figstudio.open(...)`, `figstudio demo`, and
  `figstudio --version`.
- Local browser editor served from the Python wheel; users do not need Node/npm
  at runtime.
- Variable summaries for common Scientific Python data objects and best-effort
  existing Matplotlib figure inspection.
- Public beta plot layers, Matplotlib preview, generated code panel, PNG/SVG/PDF
  export, and FigureSpec JSON import/export.
- Safe script writeback to one controlled marker block.
- Notebook-style sessions return replacement cell code instead of editing
  notebook files.
- CI and release workflows for PyPI/TestPyPI publishing, bundle checks, clean
  install smoke, and browser smoke.

Upgrade notes:

- First public install path: `pip install figstudio`.
- Generated plotting code does not import FigStudio at runtime.

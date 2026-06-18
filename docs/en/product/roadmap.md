# Roadmap

This roadmap separates current public beta commitments from likely future work. User instructions belong in the user docs, and API contracts belong in the API reference.

## Direction

- Keep FigStudio a local-first, AI-compatible figure editor and compiler, not an AI figure-generator chat surface.
- Keep model calls outside the core app. External agents may propose `FigureSpec` or `FigureSpec` patch changes, but FigStudio should validate, preview, diff, apply, export, and generate code deterministically.
- Treat `FigureSpec` as the durable contract for editing, validation, generated Matplotlib OO code, provenance, and future agent tooling.

## Now: Public Beta

- Keep the script and notebook loop stable: launch, map data, validate, render preview, generate code, save or copy, export.
- Keep generated code plain Matplotlib OO code with no FigStudio runtime dependency.
- Serve the bundled React editor from the Python wheel without requiring Node/npm at runtime.
- Support manuscript presets, project style profiles, text/arrow annotations, FigureSpec JSON import/export, preset-backed panel layouts, and the public beta plot kinds.
- Support the first general statistics recipes for pandas DataFrames: `mean_sem_line`, `grouped_points`, and `paired_before_after`.
- Keep recipe specs data-light: store variable names, column mappings, style, target axes, and recipe kind, not raw DataFrame contents.
- Show field-level validation repair suggestions when the live namespace, DataFrame columns, axes, or profile context can identify a likely fix.
- Maintain tests around codegen, validation, layout geometry, render/export failures, writeback safety, existing Figure inspection, API smoke behavior, spec import/export, API/type drift, bundle size, and browser smoke behavior.
- Keep English and Chinese docs aligned with current behavior.

## Next: Beta Hardening

- Keep release notes, changelog, and PyPI/GitHub workflow evidence current for every public tag.
- Add cross-domain reference or guide lines before domain-specific recipes: vertical and horizontal constants, baselines, thresholds, cutoff labels, and style controls.
- Add small-multiple or faceted panel authoring before domain-specific recipes: repeat axes from DataFrame groups, mapping keys, or sequence items, with shared-axis options and panel title templates.
- Add secondary y-axis support for overlays such as raw events plus summary rates after reference lines and repeated panels are stable.
- Explore full `subplot_mosaic` authoring after preset-backed GridSpec panel layouts prove stable.
- Strengthen notebook workflow with better copy/cell output ergonomics while avoiding silent notebook file mutation.
- Build a real example gallery, README screenshots, and short workflow GIFs that exercise plot layers, statistics recipes, existing Figure inspection, notebook-style output, and package install flows. Each example should show input data, user intent, preview, generated code, and export result.
- Add publication-readiness checks for export: readable font size, DPI/export format, missing axes or colorbar labels, legend overlap, panel labels, saved `FigureSpec`, generated code sync, and clear recipe error definitions.
- Add a deterministic AI-compatible handoff without built-in model calls: copy current figure context, import a `FigureSpec` or patch, show the spec diff, validate, preview, and let the user apply or reject the change.
- Expand existing Figure inspection into editable statistical recipes only when Matplotlib exposes enough raw or reproducible data.
- Monitor startup and bundle size trends as dependencies change.

## Later: Ecosystem

- Add recipe packs for neuroscience, image panels, matrix/heatmap workflows, time series, and other domain-specific figure conventions once the shared reference-line, repeated-panel, and secondary-axis primitives can carry the common structure.
- Add deeper editing ergonomics such as undo/redo history, scoped command-palette actions, and selected-object operations once common workflows remain deterministic.
- Add figure manifests and provenance records for `FigureSpec` version, FigStudio version, source script, data variable summaries, recipe semantics, export format, and generated-code hash.
- Add headless agent tooling such as `validate`, `render`, `export`, and `codegen` commands only after the `FigureSpec` and patch contracts stay stable.
- Add optional project-level templates for figure style governance once style profiles are proven.
- Explore richer style systems only after the current generated-code contract stays stable.
- Explore desktop installers only after the Python package workflow is stable.
- Explore plugin or template distribution only after the bundled recipe and gallery patterns are clear.

## Non-Goals Until Revisited

- Cloud accounts or collaboration.
- Built-in AI model calls, API-key management, or cloud inference in the core app.
- Direct AI generation or rewriting of Matplotlib code as the primary workflow.
- Hosted dashboard publishing.
- Automatic rewriting of arbitrary user Matplotlib source code.
- Direct mutation of notebook files by the local public beta.
- Full Matplotlib artist coverage, including every custom artist, 3D, polar plots, animation, or browser-native interactive publishing.
- Automatic recovery of arbitrary seaborn, statannotations, or custom statistical artists as editable recipes.
- Desktop installers in the first public beta.

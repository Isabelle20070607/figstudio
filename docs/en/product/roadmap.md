# Roadmap

This roadmap separates current public beta commitments from likely future work. User instructions belong in the user docs, and API contracts belong in the API reference.

## Now: Public Beta

- Keep the script and notebook loop stable: launch, map data, validate, render preview, generate code, save or copy, export.
- Keep generated code plain Matplotlib OO code with no FigStudio runtime dependency.
- Serve the bundled React editor from the Python wheel without requiring Node/npm at runtime.
- Support manuscript presets, project style profiles, text/arrow annotations, FigureSpec JSON import/export, preset-backed panel layouts, and the public beta plot kinds.
- Support the first general statistics recipes for pandas DataFrames: `mean_sem_line`, `grouped_points`, and `paired_before_after`.
- Keep recipe specs data-light: store variable names, column mappings, style, target axes, and recipe kind, not raw DataFrame contents.
- Maintain tests around codegen, validation, layout geometry, render/export failures, writeback safety, existing Figure inspection, API smoke behavior, spec import/export, API/type drift, bundle size, and browser smoke behavior.
- Keep English and Chinese docs aligned with current behavior.

## Next: Beta Hardening

- Run and monitor the first TestPyPI and PyPI releases after pending Trusted Publishers are configured.
- Improve validation guidance beyond selection/focus with field-level repair suggestions where the UI has enough context.
- Explore full `subplot_mosaic` authoring after preset-backed GridSpec panel layouts prove stable.
- Strengthen notebook workflow with better copy/cell output ergonomics while avoiding silent notebook file mutation.
- Build a real example gallery that exercises plot layers, statistics recipes, existing Figure inspection, notebook-style output, and package install flows.
- Expand existing Figure inspection into editable statistical recipes only when Matplotlib exposes enough raw or reproducible data.
- Monitor startup and bundle size trends as dependencies change.

## Later: Ecosystem

- Add recipe packs for neuroscience, image panels, matrix/heatmap workflows, time series, and other domain-specific figure conventions.
- Add optional project-level templates for figure style governance once style profiles are proven.
- Explore richer style systems only after the current generated-code contract stays stable.
- Explore desktop installers only after the Python package workflow is stable.
- Explore plugin or template distribution only after the bundled recipe and gallery patterns are clear.

## Non-Goals Until Revisited

- Cloud accounts or collaboration.
- Hosted dashboard publishing.
- Automatic rewriting of arbitrary user Matplotlib source code.
- Direct mutation of notebook files by the local public beta.
- Full Matplotlib artist coverage, including every custom artist, 3D, polar plots, animation, or browser-native interactive publishing.
- Automatic recovery of arbitrary seaborn, statannotations, or custom statistical artists as editable recipes.
- Desktop installers in the first public beta.

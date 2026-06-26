# Product Requirements

## Product Definition

FigStudio is a public beta local figure workflow for turning data already present in a Python session into reproducible, publication-ready Matplotlib figure panels.

Users install the Python package, open a local browser editor from a script or notebook, apply optional project style profiles, map variables to plot layers or supported statistics recipes, preview authoritative Matplotlib output, export files, save generated OO code, and optionally save the GUI session as a portable `FigureSpec` JSON file.

Future product direction and candidate work live in the [roadmap](roadmap.md).

## Target Users

- Scientific Python users who prepare data in scripts or notebooks and want faster Matplotlib figure assembly.
- Researchers who need publication-style figures with reproducible Python output.
- Cautious Matplotlib users who want GUI help without losing control of generated code.
- Project teams that want shared figure defaults without freezing every individual figure.
- Package users who expect the editor UI to work from a wheel without installing frontend tooling.

## Beta Scope

- Install from a Python package and run without Node/npm at runtime.
- Launch from Python with `figstudio.open(locals(), ...)` or from `figstudio demo`.
- Inspect safe summaries of DataFrame, Series, ndarray, mapping, list, tuple, and existing Matplotlib Figure objects.
- Create and edit the public beta plot kinds and bundled statistics recipes: mean/SEM lines, mean/SEM bars, count bars, stacked count bars, grouped points, category boxplots, category violins, paired before/after panels, and ECDF distributions.
- Create DataFrame-backed faceted panels from first-seen column values, plus mapping-key and sequence-index repeated panels for normal plot layers, with compact initial layout suggestions.
- Configure manuscript presets, project style profiles, panel layouts, axes settings, secondary Y-axis overlays, layer styles, reference lines, and text/arrow annotations.
- Load `.figstudio/styles.json` project style profiles and store profile references plus explicit override fields in `FigureSpec`.
- Render previews and exports through Matplotlib Agg.
- Run deterministic headless `codegen`, `validate`, `render`, and `export` commands against `.figstudio.json` specs, with data-dependent commands using an explicit trusted Python data script.
- Save generated code to one unique controlled script block or return notebook replacement code.
- Import and export `.figstudio.json` session specs.
- Store recipe intent, column mappings, facet equality filters, and repeated-panel selections in specs, not raw data.
- Show validation issue cards with field-level repair suggestions when the live session provides enough context.

## User Stories

- As a scientific Python user, I want to open an editor from `locals()` so I can reuse data I already prepared.
- As a researcher, I want manuscript presets and annotation controls so I can prepare publication-style figures faster.
- As a researcher, I want baseline and threshold reference lines so common scientific cutoffs are visible without encoding them as data layers.
- As a researcher, I want to overlay related measures on a shared X axis with a right-side Y axis without hand-editing generated code.
- As a researcher, I want to split a DataFrame plot or recipe into small multiples by a condition column without manually creating every axes.
- As a researcher, I want to split normal plot layers by mapping keys or sequence items when my prepared data is already grouped outside a DataFrame.
- As a project maintainer, I want shared style profiles so figures can inherit project defaults while still recording explicit overrides.
- As a cautious script user, I want writeback limited to a marked block so my data-processing code is not changed.
- As a notebook user, I want replacement cell code instead of automatic notebook mutation.
- As a Matplotlib user, I want generated code that runs without importing FigStudio.
- As a returning user, I want FigureSpec JSON import/export so I can continue a GUI editing session later with compatible data.

## Acceptance Criteria

- A script can launch FigStudio, create a DataFrame plot or statistics recipe, render a preview, and save code back into a controlled block.
- A notebook-style session without `script_path` returns complete replacement code.
- Generated code imports Matplotlib only and can run with the same user variables.
- Export downloads PNG, SVG, and PDF produced by Matplotlib.
- Reference lines generate Matplotlib `axhline` or `axvline` code and round-trip through `.figstudio.json`.
- Secondary Y-axis overlays generate Matplotlib `twinx()` code, preserve right-side axis settings, and round-trip through `.figstudio.json`.
- DataFrame facet panels generate filtered Matplotlib code, preserve shared-axis flags, and round-trip through `.figstudio.json`.
- Mapping-key and sequence-index repeated panels generate selected-item Matplotlib code and round-trip through `.figstudio.json`.
- Validation, render, export, and writeback failures return readable structured errors, including repair suggestions for common validation issues.
- Headless CLI commands can generate code from a spec, validate with a trusted data script, render preview files, export publication files, infer output formats from file suffixes, and return deterministic exit codes.
- Existing Figure inspection preserves supported line, scatter, image, and bar data as editable generated layers.
- A built wheel includes the React editor and serves it from `127.0.0.1` after clean install.
- `figstudio.load_spec()` and `figstudio.save_spec()` round-trip a `.figstudio.json` file.

## Out Of Scope

- Cloud accounts, collaboration, or hosted dashboards.
- Automatic rewriting of arbitrary user Matplotlib source code.
- Direct notebook file mutation.
- Full support for every Matplotlib artist, 3D, polar plots, animation, or interactive web publishing.
- Domain-specific recipe packs beyond the bundled general statistics recipes.
- Desktop installers for the public beta.

## Product Quality Bar

- The editor must stay local-first and bind the server to `127.0.0.1` by default.
- Generated plotting code must stay understandable Matplotlib OO code.
- Project style governance must remain reference-based.
- Writeback must fail closed when the controlled block cannot be identified safely.
- Docs must separate current beta behavior from roadmap items.

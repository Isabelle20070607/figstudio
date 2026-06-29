# Changelog

This file is the canonical chronological release record for FigStudio. User-facing
release summaries live in [English release notes](docs/en/product/release-notes.md)
and [Chinese release notes](docs/zh/product/release-notes.md).

## [0.4.0] - 2026-06-29

Release theme: broader scientific figure authoring, recipe catalogs, gallery
proof, and headless automation.

Release evidence:

- Tag: `v0.4.0`
- PyPI: `figstudio==0.4.0`

### Added

- Repeated-panel authoring now supports DataFrame facets, literal-safe mapping
  keys, and sequence-backed panels while preserving generated Matplotlib code.
- Plot layers can target a secondary right Y axis with validation, rendering,
  JSON round-trip, and `twinx()` code generation.
- Bundled recipes now cover more scientific-paper patterns: categorical
  mean/error bars, count bars, stacked bars, grouped boxplots, grouped violins,
  ECDF distribution inspection, and the first experimental
  `neuro.ephys.event_rate_timecourse` recipe.
- Internal layer and recipe registries now drive capability metadata,
  generated-code dispatch, validation, UI selectors, tests, and
  `GET /api/layer-catalog` / `GET /api/recipe-catalog`.
- Headless CLI commands now support deterministic `validate`, `render`,
  `export`, and `codegen` workflows for `.figstudio.json` specs.
- A checked-in gallery now pairs source scripts, portable specs, and SVG
  outputs for repeated panels, secondary axes, category distributions, ECDF,
  stacked composition, GridSpec spans, and neuro ephys event rates.
- Publication-readiness advisories now flag final-mile issues such as missing
  data-bearing content, weak labels or titles, legend overlap risk, and
  low-resolution PNG export settings.

### Changed

- The recipe builder is organized around research questions and chart families
  instead of a flat primitive list.
- Notebook-style sessions now provide a mode-aware prepare-cell handoff, keep
  replacement-cell output easy to copy, and return to generated-code preview
  after later spec edits without mutating notebook files.
- Repeated-panel builders now choose compact initial rows and columns from the
  panel count and figure aspect while staying within the existing
  `FigureSpec.rows`, `FigureSpec.cols`, and one-cell `AxesSpec` contract.
- Active roadmap pages now remove completed release content before publishing;
  shipped history lives in this changelog and the paired release notes.

### Fixed

- Repeated-panel smoke coverage avoids Matplotlib layout warnings for
  aspect-sensitive panels.
- Notebook and no-script handoff flows no longer leave stale code-panel state
  after save or later spec edits.

## [0.3.1] - 2026-06-18

Release theme: clearer validation repair guidance and desktop workspace fit.

Release evidence:

- Tag: `v0.3.1`
- PyPI: `figstudio==0.3.1`

### Added

- Validation issues can now carry a `suggestion` field for direct repair text.
- Validation issue `details` now include bounded repair context such as
  available variables, DataFrame columns, available axes, profile ids, and a
  suggested replacement value when the live session can infer one.
- Browser smoke coverage now checks that the desktop editor workspace fits the
  viewport without page-level scrolling.

### Changed

- The editor shows API-provided validation suggestions as `Suggested fix: ...`
  before falling back to local generic repair text.
- Full-size desktop layouts now lock the app shell to the viewport and keep
  scrolling inside the preview surface instead of the whole page.
- Release workflow smoke installs were synchronized to `figstudio==0.3.1`.

### Fixed

- Missing variables, missing DataFrame columns, missing axes, invalid layout
  spans, log-scale positivity, and missing style profiles now produce more
  actionable validation repair guidance.
- Fullscreen desktop sessions no longer require scrolling the page to reach the
  code panel in the browser smoke viewport.

## [0.3.0] - 2026-06-18

Release theme: publish-ready style governance, layout reliability, bilingual
documentation, and release automation hardening.

Release evidence:

- Tag: `v0.3.0`
- PyPI: `figstudio==0.3.0`
- PyPI publish workflow: `publish-pypi` run `27741981921`, success

### Added

- Project style profiles loaded from `.figstudio/styles.json`, with
  `figstudio.open(..., project_path=...)`, CLI `--project`, session
  `project_path`, and `GET /api/style-profiles`.
- `FigureStyle.profile_id` and `FigureStyle.profile_overrides` so specs can
  reference shared project defaults without copying them into each spec.
- Profile resolution for figure defaults, plot-layer defaults, and recipe
  defaults in validation, render, export, and generated Matplotlib code.
- `AxesSpec.rowspan` and `AxesSpec.colspan`, layout presets, and `GridSpec`
  code generation for spanned or non-dense panel layouts.
- Paired English and Chinese documentation under `docs/en/` and `docs/zh/`,
  with top-level docs kept as compatibility stubs.
- `examples/smoke_project/.figstudio/styles.json` for browser smoke coverage
  of project style profiles.

### Changed

- Publish/polish UI now surfaces project profiles, inherited style values,
  profile override notes, and preset-backed panel layouts.
- Dense regular grids still generate `plt.subplots`; only spanned or non-dense
  layouts switch to `fig.add_gridspec`.
- Validation now reports invalid grid size, duplicate axes ids, invalid axes
  spans, out-of-bounds axes, overlapping axes, and missing profile ids.
- GitHub Actions release and CI workflows were moved to Node 24-compatible
  action versions.

### Fixed

- Browser smoke profile fixture now provides a real style profile config during
  release validation.
- Runtime render, export, and code generation now receive resolved profile
  defaults consistently instead of relying only on raw spec fields.

## [0.2.0] - 2026-06-17

Release theme: first general statistics recipe workflow for pandas DataFrames.

Release evidence:

- Tag: `v0.2.0`
- PyPI: `figstudio==0.2.0`
- PyPI publish workflow: `publish-pypi` run `27672790446`, success

### Added

- Bundled general statistics recipes: `mean_sem_line`, `grouped_points`, and
  `paired_before_after`.
- `RecipeLayer`, `RecipeDatasetRef`, and `FigureSpec.recipes` contracts.
- UI recipe builder for choosing a pandas DataFrame, mapping columns, selecting
  group or subject columns, choosing SEM/SD/no error display, and targeting an
  axes.
- Plain Matplotlib code generation for recipes while computing statistics from
  the user's live pandas DataFrame variable.
- Recipe validation for non-DataFrame sources and missing columns.
- `examples/general_stats_recipe.py` and recipe-focused API, codegen, and
  browser smoke coverage.

### Changed

- README and docs were updated so recipes are discoverable from the public
  package workflow, API reference, user guide, roadmap, and developer guide.
- Package metadata, backend version, frontend package metadata, lockfiles, and
  release workflow version checks were synchronized to `0.2.0`.

## [0.1.0] - 2026-06-16

Release theme: first public beta on PyPI.

Release evidence:

- Tag: `v0.1.0`
- PyPI: `figstudio==0.1.0`
- PyPI publish workflow: `publish-pypi` run `27629737016`, success

### Added

- Installable Python package with `figstudio.open(...)`, `figstudio demo`, and
  `figstudio --version`.
- Local FastAPI session server bound to `127.0.0.1` by default and serving the
  bundled React editor from the Python wheel.
- Safe variable summaries for DataFrames, Series, ndarrays, sequences, and
  best-effort existing Matplotlib figures.
- Public beta plot layers: `line`, `scatter`, `bar`, `barh`, `hist`, `boxplot`,
  `violin`, `errorbar`, `heatmap`, `contour`, `step`, and `fill_between`.
- Browser editor flow for selecting variables, mapping plot layers, previewing
  Matplotlib output, editing axes/style/annotations, importing/exporting
  `FigureSpec`, exporting PNG/SVG/PDF, and showing generated code.
- Controlled script writeback that only replaces one matching
  `# figstudio:start <block_id>` to `# figstudio:end <block_id>` block.
- Notebook-style sessions that return replacement cell code instead of mutating
  notebook files.
- `figstudio.save_spec()` and `figstudio.load_spec()` helpers for
  `.figstudio.json` round trips.
- CI, TestPyPI, PyPI, bundle-size, clean-install, and Playwright smoke release
  checks.

### Fixed

- TestPyPI smoke install now gets runtime dependencies from PyPI and installs
  the FigStudio artifact from TestPyPI with `--no-deps`, avoiding broken or
  missing dependency packages on TestPyPI.

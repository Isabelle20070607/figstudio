# Roadmap Initiatives

This page groups future roadmap work by product theme. It is not a release plan; maturity and horizon labels explain readiness and likely sequencing.

## Scientific Authoring Primitives

| Field | Value |
| --- | --- |
| Theme | Scientific authoring primitives |
| Initiative | Extend small-multiple or faceted panel authoring to mapping keys or sequence items. |
| Status | Completed in beta. |
| Completion note | Normal plot layers can repeat by DataFrame values, literal-safe mapping keys, or sequence indices; statistics recipes remain DataFrame-only. |

| Field | Value |
| --- | --- |
| Theme | Scientific authoring primitives |
| Initiative | Add secondary y-axis support for overlays such as raw events plus summary rates. |
| Status | Completed in beta. |
| Completion note | Plot layers can target the left or right Y axis on the same panel; the right axis supports label, scale, limits, validation, Matplotlib `twinx()` codegen, and JSON round-trip. Recipes and reference lines remain primary-axis scoped. |

| Field | Value |
| --- | --- |
| Theme | Scientific authoring primitives |
| Initiative | Add automatic repeated-panel layout optimization as an initial layout suggestion. |
| Status | Completed in beta. |
| Completion note | Facet and repeated-panel builders now choose compact, non-overlapping initial rows and columns from the panel count and current figure aspect, while still emitting only existing `FigureSpec.rows`, `FigureSpec.cols`, and one-cell `AxesSpec` geometry. |

| Field | Value |
| --- | --- |
| Theme | Scientific authoring primitives |
| Initiative | Explore full `subplot_mosaic` authoring. |
| Why it matters | Mosaic layouts can express publication panels that outgrow named presets. |
| Maturity | `exploratory` |
| Horizon | `later` |
| Readiness | GridSpec, span validation, and gallery proof make feasibility clearer, but a mosaic syntax would still introduce a new public layout authoring surface. |
| Gate/Prerequisite | Preset-backed GridSpec panel layouts prove stable in real workflows. |

| Field | Value |
| --- | --- |
| Theme | Scientific authoring primitives |
| Initiative | Revisit limited polar plots, animation-lite, and static 3D only as bounded scientific exploration views. |
| Why it matters | Circular data, parameter sliders, frame sequences, and simple state-space views can help exploration, but they should not turn FigStudio into a full artist or animation editor. |
| Maturity | `exploratory` |
| Horizon | `later` |
| Gate/Prerequisite | Core 2D recipes, repeated-panel workflows, validation, export, and generated-code contracts stay stable. |

## Recipe And Statistical Coverage

| Field | Value |
| --- | --- |
| Theme | Recipe and statistical coverage |
| Initiative | Organize analysis recipes around research questions such as group comparison, paired conditions, time course comparison, distribution inspection, relationships, and matrix or heatmap review. |
| Why it matters | Users explore scientific data by asking questions, not by choosing chart primitives first. |
| Maturity | `ready` |
| Horizon | `near` |
| Progress | The recipe model now covers line summaries, mean-plus-error bars, count bars, and stacked count bars with role-specific validation and pure Matplotlib codegen; remaining work is the research-question UI grouping. |
| Gate/Prerequisite | Recipe roles, validation, and generated-code templates remain simple enough to explain and test. |

| Field | Value |
| --- | --- |
| Theme | Recipe and statistical coverage |
| Initiative | Add categorical summary recipes such as grouped bars, stacked bars, count bars, bar-with-error panels, and point/box/violin overlays. |
| Why it matters | These cover common scientific-paper chart patterns without expanding into generic business dashboards. |
| Maturity | `ready` |
| Horizon | `near` |
| Progress | Beta slices added `mean_sem_bar` for mean-plus-error categorical bars, `count_bar` for ungrouped or grouped frequency bars, and `stacked_bar` for grouped stacked frequency bars; distribution overlays remain future work. |
| Readiness | Shared recipe roles and validation paths now make the remaining categorical overlays incremental rather than foundational. |
| Gate/Prerequisite | Shared recipe roles and validation errors are clear enough for multiple recipe families. |

| Field | Value |
| --- | --- |
| Theme | Recipe and statistical coverage |
| Initiative | Add distribution and relationship recipes: regression scatter with fitted trend, confidence or percentile bands, ECDF, two-dimensional histograms, hexbin summaries, and stronger heatmap or matrix controls. |
| Why it matters | These fill high-value reproducible Matplotlib workflows for exploratory and manuscript figures. |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | Existing recipe dispatch, dataset-role validation, and generated-code templates reduce implementation risk; the next risks are statistical semantics for fitted trends, bands, binning, and matrix controls. |
| Gate/Prerequisite | Generated-code templates and recipe validation remain understandable as recipe complexity grows. |

| Field | Value |
| --- | --- |
| Theme | Recipe and statistical coverage |
| Initiative | Expand existing Figure inspection into editable statistical recipes when recoverable data allows it. |
| Why it matters | Users should be able to continue editing supported figures only when FigStudio can preserve reproducibility. |
| Maturity | `exploratory` |
| Horizon | `later` |
| Gate/Prerequisite | Matplotlib exposes enough raw or reproducible data for the relevant artists. |

## Exploration Workspace

| Field | Value |
| --- | --- |
| Theme | Exploration workspace |
| Initiative | Add an exploration result board with result cards, pinned findings, spec snapshots, notes, and restore or duplicate actions. |
| Why it matters | Exploration is branching and iterative; users need to remember which data view, mapping, filter, recipe, and style produced a useful result. |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Gate/Prerequisite | Saved specs, generated-code hashes, and provenance records are stable enough to store lightweight session history without raw data. |

| Field | Value |
| --- | --- |
| Theme | Exploration workspace |
| Initiative | Add parameter sweeps for common analysis choices such as bin size, smoothing, normalization, aggregation level, filter, time window, scale, and error style. |
| Why it matters | Researchers need to see whether a conclusion survives reasonable parameter changes before investing in publication polish. |
| Maturity | `exploratory` |
| Horizon | `later` |
| Gate/Prerequisite | Sweep results can be represented as repeatable specs, result cards, or generated Matplotlib code rather than hidden browser-only state. |

| Field | Value |
| --- | --- |
| Theme | Exploration workspace |
| Initiative | Add object drill-down, from-plot data selection, selected-vs-rest comparison, and basic data hierarchy warnings. |
| Why it matters | Users should be able to trace points, curves, or panels back to objects and detect outliers, scale traps, imbalance, or pseudoreplication risks. |
| Maturity | `exploratory` |
| Horizon | `later` |
| Gate/Prerequisite | Data previews and warnings remain advisory, deterministic, and non-mutating. |

## Publication Workflow

| Field | Value |
| --- | --- |
| Theme | Publication workflow |
| Initiative | Build a real example gallery, README screenshots, and short workflow GIFs. |
| Why it matters | Users need production-like proof of plot layers, statistics recipes, existing Figure inspection, notebook-style output, and package install flows from source data through visible preview and export artifacts. |
| Maturity | `ready` |
| Horizon | `near` |
| Gate/Prerequisite | Each example shows input data, user intent or figure contract, preview screenshot, generated Matplotlib code, FigureSpec/export artifact, and the publication workflow it demonstrates. |

| Field | Value |
| --- | --- |
| Theme | Publication workflow |
| Initiative | Add publication-readiness checks for export. |
| Why it matters | Missing figure intent, unreadable final-size typography, non-editable vector text, weak panel labels, legend or label overlap, untraceable statistics/source data, stale spec/code sync, and recipe errors are common final-mile problems. |
| Maturity | `ready` |
| Horizon | `near` |
| Progress | First advisory slice covers empty data-bearing figures, missing primary and secondary axis labels, missing legend labels for multi-item axes, and low-resolution PNG export settings. |
| Readiness | Export-context advisory warnings are now proven; additional final-mile checks can layer on the same validation contract. |
| Gate/Prerequisite | Checks are advisory and deterministic, with clear issue definitions and no hidden journal-specific or AI judgment. |

| Field | Value |
| --- | --- |
| Theme | Publication workflow |
| Initiative | Strengthen notebook copy and cell-output ergonomics. |
| Why it matters | Notebook users need a smoother handoff while staying in control of file mutation. |
| Maturity | `foundation-needed` |
| Horizon | `near` |
| Gate/Prerequisite | Notebook workflow continues to return replacement code rather than silently editing notebook files. |

## AI-Compatible Handoff And Provenance

| Field | Value |
| --- | --- |
| Theme | AI-compatible handoff and provenance |
| Initiative | Add deterministic AI-compatible handoff without built-in model calls. |
| Why it matters | External agents can propose `FigureSpec` or patch changes from figure-contract-style reasoning while FigStudio remains the deterministic validator, previewer, differ, and applier. |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Gate/Prerequisite | Import a `FigureSpec` or patch, show the spec diff, validate, preview, and let the user apply or reject the change. |

| Field | Value |
| --- | --- |
| Theme | AI-compatible handoff and provenance |
| Initiative | Add figure manifests and provenance records. |
| Why it matters | Reproducibility improves when manifests record figure intent, FigStudio version, source script, data summaries, recipe semantics, export formats, generated-code hash, and readiness-check results. |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | Readiness warning codes and exported `FigureSpec` artifacts now provide manifestable facts; generated-code hashing and source/session provenance remain the next prerequisites. |
| Gate/Prerequisite | `FigureSpec` versioning, generated-code hashing, and advisory readiness-check definitions are stable. |

| Field | Value |
| --- | --- |
| Theme | AI-compatible handoff and provenance |
| Initiative | Add headless agent tooling such as `validate`, `render`, `export`, and `codegen` commands. |
| Why it matters | Automation needs deterministic command surfaces after the interactive contract is stable. |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | Validate, render, and codegen behavior is deterministic through the API and tests; CLI wrappers are lower risk, but patch diff/apply contracts remain future work. |
| Gate/Prerequisite | `FigureSpec` and patch contracts stay stable. |

## Ecosystem And Templates

| Field | Value |
| --- | --- |
| Theme | Ecosystem and templates |
| Initiative | Prepare the recipe/template pack substrate. |
| Why it matters | Namespaced recipe IDs, reusable chart-family roles, shared role schemas, validation hooks, generated-code templates, style defaults, gallery fixtures, and import/export compatibility should exist before external or domain-specific packs. |
| Maturity | `ready` |
| Horizon | `near` |
| Progress | Bundled recipes now share `RecipeKind`, dataset-role validation, generated-code dispatch, UI selectors, tests, and gallery-backed workflows across line and categorical families. |
| Gate/Prerequisite | Bundled recipes and gallery fixtures share enough structure to avoid freezing a weak extension contract. |

| Field | Value |
| --- | --- |
| Theme | Ecosystem and templates |
| Initiative | Add recipe and template packs for neuroscience, image panels, matrix/heatmap workflows, time series, and other domain-specific figure conventions. |
| Why it matters | Domain packs should reuse stable primitives instead of becoming separate products. |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | Reference lines, repeated panels, secondary axes, and scientific-summary recipes are now available beta primitives; remaining prerequisites are pack substrate, domain fixtures, and loading rules. |
| Gate/Prerequisite | Reference-line, repeated-panel, secondary-axis, and scientific-summary primitives can carry the common structure. |

| Field | Value |
| --- | --- |
| Theme | Ecosystem and templates |
| Initiative | Start domain work with a bundled experimental neuroscience pack before considering an optional `figstudio-neuro` distribution. |
| Why it matters | The neuroscience surface should prove recipe contracts, gallery examples, and package loading before splitting distribution. |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | The cross-domain primitives needed by `neuro.core` and ephys-style overlays are now present; keep this bundled and experimental until pack loading and gallery evidence exist. |
| Gate/Prerequisite | Keep neuroscience organized as subdomains: `neuro.core`, `neuro.ephys`, and `neuro.neuroimaging`. |

## Product Ergonomics And Operations

| Field | Value |
| --- | --- |
| Theme | Product ergonomics and operations |
| Initiative | Add deeper editing ergonomics such as undo/redo history, scoped command-palette actions, and selected-object operations. |
| Why it matters | Richer editing should wait until common workflows remain deterministic. |
| Maturity | `exploratory` |
| Horizon | `later` |
| Gate/Prerequisite | Core editing and generated-code flows stay predictable. |

| Field | Value |
| --- | --- |
| Theme | Product ergonomics and operations |
| Initiative | Add optional project-level templates for figure style governance. |
| Why it matters | Teams may need shared figure conventions after style profiles are proven. |
| Maturity | `exploratory` |
| Horizon | `later` |
| Gate/Prerequisite | Current style profiles prove stable in project workflows. |

| Field | Value |
| --- | --- |
| Theme | Product ergonomics and operations |
| Initiative | Monitor startup and bundle size trends as dependencies change. |
| Why it matters | Runtime installs must keep serving the packaged editor without frontend tooling or heavy startup cost. |
| Maturity | `ready` |
| Horizon | `near` |
| Gate/Prerequisite | Bundle and smoke checks remain part of release evidence. |

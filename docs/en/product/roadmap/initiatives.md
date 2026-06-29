# Roadmap Initiatives

This page groups future roadmap work by product theme. It is not a release plan; maturity and horizon labels explain readiness and likely sequencing.

## Scientific Authoring Primitives

| Field | Value |
| --- | --- |
| Theme | Scientific authoring primitives |
| Initiative | Explore full `subplot_mosaic` authoring. |
| Why it matters | Mosaic layouts can express publication panels that outgrow named presets. |
| Maturity | `exploratory` |
| Horizon | `later` |
| Readiness | A mosaic syntax would introduce a new public layout authoring surface and needs a compact user model before implementation. |
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
| Initiative | Add remaining distribution and relationship recipes such as regression scatter with fitted trend, confidence or percentile bands, two-dimensional histograms, hexbin summaries, and stronger heatmap or matrix controls. |
| Why it matters | These fill high-value reproducible Matplotlib workflows for exploratory and manuscript figures. |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | The main risks are statistical semantics for fitted trends, bands, binning, hexbin summaries, and matrix controls. |
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
| Initiative | Expand gallery discoverability with README screenshots and short workflow GIFs. |
| Why it matters | Users need quick visual proof of source data through visible preview, generated code, and export artifacts before opening the full docs. |
| Maturity | `ready` |
| Horizon | `near` |
| Gate/Prerequisite | Gallery assets stay reproducible from source scripts and portable specs. |

| Field | Value |
| --- | --- |
| Theme | Publication workflow |
| Initiative | Broaden publication-readiness checks for export. |
| Why it matters | Missing figure intent, unreadable final-size typography, non-editable vector text, weak panel labels, legend or label overlap, untraceable statistics/source data, stale spec/code sync, and recipe errors are common final-mile problems. |
| Maturity | `ready` |
| Horizon | `near` |
| Gate/Prerequisite | Checks are advisory and deterministic, with clear issue definitions and no hidden journal-specific or AI judgment. |

## AI-Compatible Handoff And Provenance

| Field | Value |
| --- | --- |
| Theme | AI-compatible handoff and provenance |
| Initiative | Add deterministic AI-compatible handoff without built-in model calls. |
| Why it matters | External agents can propose `FigureSpec` or patch changes from figure-contract-style reasoning while FigStudio remains the deterministic validator, previewer, differ, and applier. |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | Spec diff/apply UX and patch acceptance rules remain prerequisites. |
| Gate/Prerequisite | Import a `FigureSpec` or patch, show the spec diff, validate, preview, and let the user apply or reject the change. |

| Field | Value |
| --- | --- |
| Theme | AI-compatible handoff and provenance |
| Initiative | Add figure manifests and provenance records. |
| Why it matters | Reproducibility improves when manifests record figure intent, FigStudio version, source script, data summaries, recipe semantics, export formats, generated-code hash, and readiness-check results. |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | Generated-code hashing and source/session provenance remain the next prerequisites. |
| Gate/Prerequisite | `FigureSpec` versioning, generated-code hashing, and advisory readiness-check definitions are stable. |

## Ecosystem And Templates

| Field | Value |
| --- | --- |
| Theme | Ecosystem and templates |
| Initiative | Add recipe and template packs for neuroscience, image panels, matrix/heatmap workflows, time series, and other domain-specific figure conventions. |
| Why it matters | Domain packs should reuse stable primitives instead of becoming separate products. |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | Broader domain packs still need more fixtures, loading rules, and compatibility expectations. |
| Gate/Prerequisite | Domain packs reuse stable cross-domain primitives and do not become separate products. |

| Field | Value |
| --- | --- |
| Theme | Ecosystem and templates |
| Initiative | Expand bundled experimental neuroscience coverage before considering an optional `figstudio-neuro` distribution. |
| Why it matters | The neuroscience surface should prove recipe contracts, gallery examples, and package loading before splitting distribution. |
| Maturity | `exploratory` |
| Horizon | `later` |
| Readiness | Keep this bundled and experimental until broader pack loading and more gallery evidence exist. |
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

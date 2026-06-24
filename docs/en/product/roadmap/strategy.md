# Roadmap Strategy

This page explains how FigStudio chooses roadmap work. Current beta commitments live in the [PRD](../prd.md), and the theme backlog lives in [initiatives](initiatives.md).

## Product Direction

- Keep FigStudio a local-first, AI-compatible figure editor and compiler, not an AI figure-generator chat surface.
- Position FigStudio as an explore-first scientific visualization workbench: help Python users quickly compare data views, then export reproducible Matplotlib figures when a result is worth keeping.
- Keep model calls outside the core app. External agents may propose `FigureSpec` or `FigureSpec` patch changes, but FigStudio should validate, preview, diff, apply, export, and generate code deterministically.
- Treat `FigureSpec` as the durable contract for editing, validation, generated Matplotlib OO code, provenance, and future agent tooling.
- Keep generated code plain Matplotlib OO code with no FigStudio runtime dependency.
- Keep the runtime wheel self-contained: the bundled React editor must be served from the Python package without requiring Node/npm after install.

## Sequencing Principles

- Stabilize cross-domain plotting primitives before domain-specific recipe packs.
- Prefer features that reduce repeated exploration work, make analysis variants easier to compare, or reveal object-level heterogeneity before adding final-mile polishing controls.
- Prefer scientific-paper figure coverage over general business chart coverage.
- Keep recipe specs data-light: store variable names, column mappings, style, target axes, filters, and recipe kind, not raw DataFrame contents.
- Keep repeated-panel and layout work compatible with existing `FigureSpec.rows`, `FigureSpec.cols`, and `AxesSpec` geometry until a stronger layout contract is justified.
- Build reusable package, gallery, and validation substrate before external recipe/template distribution.
- Strengthen notebook ergonomics without silently mutating notebook files.
- Add AI-compatible handoff only as deterministic import, diff, validate, preview, and apply/reject flows.
- Defer richer ecosystem surfaces until the `FigureSpec`, generated-code, package, and patch contracts stay stable.

## Roadmap Labels

Initiatives use two labels so planning can stay readable without forcing every item into a single time bucket.

| Label | Values | Meaning |
| --- | --- | --- |
| Maturity | `ready`, `foundation-needed`, `exploratory` | How much product or technical groundwork is still needed. |
| Horizon | `near`, `later`, `deferred` | Expected planning distance, used as a guide rather than a release promise. |

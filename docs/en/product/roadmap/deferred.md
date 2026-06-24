# Deferred Work

This page records work that is intentionally out of the current roadmap shape. Some items may be revisited after the product contracts are stable.

| Deferred Area | Why Deferred | Revisit When |
| --- | --- | --- |
| Cloud accounts or collaboration | The product is local-first and does not require hosted identity or collaboration to deliver the beta workflow. | Local workflow, package distribution, and reproducibility contracts are stable and users ask for hosted collaboration. |
| Built-in AI model calls, API-key management, or cloud inference in the core app | FigStudio should remain a deterministic editor/compiler; model calls belong outside the core app. | Deterministic `FigureSpec` patch import, diff, validation, and apply/reject flows are stable. |
| Direct AI generation or rewriting of Matplotlib code as the primary workflow | Generated code should come from validated specs, not opaque rewrites. | AI handoff can operate through reviewable spec patches without weakening codegen determinism. |
| Hosted dashboard publishing | Publishing dashboards is outside the reproducible manuscript-figure workflow. | The project deliberately expands beyond local scientific figure authoring. |
| Automatic rewriting of arbitrary user Matplotlib source code | Safe writeback is limited to controlled marker blocks. | A separate, explicit source-transformation design exists with strong safety boundaries. |
| Direct mutation of notebook files | Notebook writeback is semi-automatic and returns replacement code. | A user-approved notebook file mutation workflow has a clear rollback and review model. |
| Full Matplotlib artist coverage, including every custom artist, full 3D editing, full animation timeline editing, or browser-native interactive publishing | Full artist coverage would dilute support for reproducible exploration and publication panels. | High-demand artist families can be supported through clear, testable contracts; limited polar, animation-lite, or static 3D views may be handled as bounded roadmap initiatives first. |
| Automatic recovery of arbitrary seaborn, statannotations, or custom statistical artists as editable recipes | Recovery is only useful when raw or reproducible data can be preserved. | The source artist exposes enough data and semantics for reproducible generated code. |
| Desktop installers | The public beta is package-first. | The Python package workflow is stable and installer demand is strong enough to justify distribution work. |
| Richer style systems | Current generated-code and style-profile contracts should prove stable first. | Style profiles are widely used and users need a more expressive governance model. |
| Plugin or template distribution | External distribution would freeze extension contracts too early. | Bundled recipe and gallery patterns are clear enough to support compatibility promises. |

# Developer Guide

This guide is for people continuing FigStudio development. It covers local workflows, change surfaces, and checks.

## Local Environment

Use `uv` for Python tasks and `npm` inside `frontend/` for the React editor.

```powershell
uv run --extra dev pytest
```

```powershell
cd frontend
npm install
npm run build
npm run check:bundle
npm run test:e2e
npm run dev
```

The development server binds to `127.0.0.1`. The Python app also binds to `127.0.0.1` by default.

## Repository Map

- `src/figstudio/session.py`: public `open()` lifecycle, local port, browser launch, optional Figure inspection.
- `src/figstudio/models.py`: Pydantic models shared by backend behavior and API documentation.
- `src/figstudio/registry.py`: variable filtering and summaries.
- `src/figstudio/style_profiles.py`: project `.figstudio/styles.json` loading and effective style resolution.
- `src/figstudio/validation.py`: pre-render validation.
- `src/figstudio/codegen.py`: Matplotlib OO code generation.
- `src/figstudio/render.py`: Agg rendering and export.
- `src/figstudio/sync.py`: controlled script writeback.
- `src/figstudio/server.py`: FastAPI routes and static editor serving.
- `src/figstudio/spec_io.py`: `.figstudio.json` helpers.
- `frontend/src/App.tsx`: editor shell, controls, import/export, preview, validation display.
- `frontend/src/types.ts`: TypeScript mirror of the public data contracts.
- `tests/`: behavior and smoke coverage.

## Feature Change Rules

When adding a plot kind, update the full contract in one pass: Pydantic literal, TypeScript type, UI creation and controls, codegen, validation when needed, tests, and docs.

When adding a recipe, keep generated imports limited to Matplotlib, use methods on existing user DataFrame variables instead of serializing data into code, and update recipe validation and smoke coverage.

When changing request, response, or FigureSpec fields, treat `src/figstudio/models.py` as the backend source of truth and update `frontend/src/types.ts`, request construction, serialization tests, and the API reference.

Keep old fields compatible when reasonable because saved `.figstudio.json` files may exist.

## Writeback Rules

Script writeback may only replace a unique controlled block:

```python
# figstudio:start main
# generated code lives here
# figstudio:end main
```

`CodeSyncEngine` rejects missing blocks, duplicate blocks for the same id, nested markers, unmatched start/end markers, and IO failures. Do not add fallback behavior that edits outside the controlled block.

Notebook-style sessions return replacement cell code and must not mutate notebook files directly.

## Documentation Ownership

Keep each topic in one owning surface and cross-link instead of copying:

- `README.md` owns positioning, first-run commands, and the docs index; `CHANGELOG.md` is the canonical chronological release record.
- User workflows belong in `getting-started.md`, `scientific-workflows.md`, `styles-and-layouts.md`, `save-export-reuse.md`, and `troubleshooting.md`.
- `reference/api.md` owns public contracts, `architecture/technical-design.md` owns internals, and this guide owns contributor workflow.
- `product/prd.md` owns current beta scope, `product/roadmap*.md` owns future work, and `product/release-notes.md` gives the localized release summary.

Keep old top-level docs as short compatibility stubs.

## Documentation Sync

- Give every long-form `docs/en` page a matching `docs/zh` path and maintain both as peers.
- When behavior changes, update the owning page and its locale peer. Scope changes update both PRDs and the relevant roadmap pages.
- Before a release, derive `CHANGELOG.md` and both release notes from the full previous-tag delta.
- Before finishing docs work, scan for stale planning or phase wording. Check onboarding headings with `Get-ChildItem README.md,docs -Recurse -File -Filter *.md | Select-String -Pattern '^#+ .*?(Quick Start|快速开始)'`; only the README and localized getting-started pages may own them.
- Verify locale-path parity, links, and `git diff --check -- AGENTS.md README.md docs`.

## Release Checks

For package-oriented changes:

- run `uv run --extra dev pytest`;
- run `cd frontend`; `npm run build`;
- run `cd frontend`; `npm run check:bundle`;
- run `cd frontend`; `npm run test:e2e`;
- run `uv build`;
- install the built wheel in a clean virtual environment;
- run `figstudio demo --no-browser` and confirm `/` and `/api/session` are served from `127.0.0.1`.

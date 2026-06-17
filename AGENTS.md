# AGENTS.md

Project guidance for `figstudio`.

## Commands

- Use `uv` for Python tasks: `uv run --extra dev pytest`, `uv run python -m figstudio`.
- Use `npm` inside `frontend/` for UI tasks: `npm run build`, `npm run check:bundle`, `npm run test:e2e`, `npm run dev`.
- Use `uv build` for release package verification; the Hatch hook builds and bundles the frontend.
- The `dev` extra intentionally uses `httpx2`; do not normalize it to `httpx` without revalidating FastAPI/TestClient compatibility and updating `uv.lock` deliberately.

## Product Invariants

- Generated plotting code must remain plain Matplotlib OO code and must not require `figstudio` at runtime.
- Code writeback may only replace a unique `# figstudio:start <block_id>` to `# figstudio:end <block_id>` block. Never modify user data-processing code outside the controlled block.
- The local web server must bind to `127.0.0.1` by default.
- Do not use ports `8765` or `8766` as FigStudio defaults or smoke-test ports; reserve them for AnkiConnect/default-client compatibility and use `8767` unless the user overrides it.
- Treat notebook writeback as semi-automatic: return replacement cell code, do not edit notebook files directly.
- Runtime wheels must serve the React editor from `figstudio/static` and must not require Node/npm after install.

## Documentation Ownership

Follow Codex AGENTS guidance: keep this file to durable repository expectations, commands, verification steps, and review expectations. Put product detail in `docs/` and link to it instead of duplicating it here.

| Path | Owns | Must not contain |
| --- | --- | --- |
| `README.md` | project positioning, quick start, development commands, docs index | detailed architecture, roadmap, long troubleshooting |
| `docs/en/` and `docs/zh/` | paired English and Chinese docs with matching relative paths | one language drifting structurally from the other |
| `docs/*` top-level legacy stubs | compatibility links to the new locale pages | long-form duplicated content |
| `docs/*/getting-started.md` | install, demo, script/notebook launch, first plot | API contracts, roadmap, developer workflow |
| `docs/*/scientific-workflows.md` | plot layers, recipes, existing figures, annotations, publication polish | architecture internals, future backlog |
| `docs/*/styles-and-layouts.md` | presets, panel layouts, GridSpec behavior, style profiles | low-level REST details, developer workflow |
| `docs/*/save-export-reuse.md` | safe save code, notebook replacement, export, FigureSpec reuse | implementation architecture |
| `docs/*/troubleshooting.md` | validation, render/export, writeback, style-profile recovery | broad product roadmap |
| `docs/*/reference/api.md` | Python API, CLI, REST endpoints, FigureSpec fields, error payloads, compatibility notes | user tutorial, product backlog |
| `docs/*/architecture/technical-design.md` | architecture, data flow, safety decisions, packaging, verification | user tutorial, product backlog |
| `docs/*/contributing/developer-guide.md` | local development, feature-change workflow, tests, package checks, documentation sync | product positioning, user tutorial |
| `docs/*/product/prd.md` | beta product definition, user stories, scope, acceptance criteria, non-goals | setup steps, API reference |
| `docs/*/product/roadmap.md` | Now/Next/Later planning and explicit non-goals | current user instructions, detailed API contracts |

## Documentation Rules

- Keep English and Chinese docs in paired locale trees: every long-form `docs/en/**/*.md` page must have the same relative path under `docs/zh/`, and vice versa.
- Treat English and Chinese as equal-maintenance peers. Do not use one language as the only canonical source.
- Keep old top-level files such as `docs/user-guide.md`, `docs/api-reference.md`, and `docs/developer-guide.md` as short compatibility stubs only.
- When behavior changes, update the owning locale pages above and add cross-links instead of repeating the same explanation elsewhere.
- Before finishing documentation work, scan `README.md`, `docs`, and `AGENTS.md` for stale planning labels, phase-style headings, and obsolete implementation-flow wording.
- For onboarding heading duplication, run `rg -n "^#+ .*?(Quick Start|快速开始)" README.md docs` and allow only `README.md` plus localized getting-started pages.
- Before finishing locale docs work, verify paired paths under `docs/en` and `docs/zh`.
- If a feature moves between beta scope and roadmap, update both locale copies of `product/prd.md` and `product/roadmap.md` together so current commitments and future plans stay consistent.
- For public package work, verify `uv run --extra dev pytest`, frontend build/bundle/e2e checks, `uv build`, and a clean wheel install that serves `/api/session`.

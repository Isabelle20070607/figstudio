# AGENTS.md

Project guidance for `figstudio`.

## Commands

- Use `uv` for Python tasks: `uv run pytest`, `uv run python -m figstudio`.
- Use `npm` inside `frontend/` for UI tasks: `npm run build`, `npm run dev`.

## Product Invariants

- Generated plotting code must remain plain Matplotlib OO code and must not require `figstudio` at runtime.
- Code writeback may only replace a unique `# figstudio:start <block_id>` to `# figstudio:end <block_id>` block. Never modify user data-processing code outside the controlled block.
- The local web server must bind to `127.0.0.1` by default.
- Treat notebook writeback as semi-automatic: return replacement cell code, do not edit notebook files directly.

## Documentation Ownership

Follow Codex AGENTS guidance: keep this file to durable repository expectations, commands, verification steps, and review expectations. Put product detail in `docs/` and link to it instead of duplicating it here.

| File | Owns | Must not contain |
| --- | --- | --- |
| `README.md` | project positioning, quick start, development commands, docs index | detailed architecture, roadmap, long troubleshooting |
| `docs/prd.md` | beta product definition, user stories, scope, acceptance criteria, non-goals | implementation phases, API reference, setup steps |
| `docs/technical-design.md` | architecture, public API, data model, endpoints, safety decisions, verification commands | user tutorial, roadmap, product backlog |
| `docs/user-guide.md` | script/notebook workflows, data mapping, editing, export, common errors, recovery | internal architecture, future roadmap |
| `docs/roadmap.md` | Now/Next/Later planning and explicit non-goals | current user instructions, detailed API contracts |

## Documentation Rules

- Keep product docs bilingual in the same file; do not create separate English and Chinese copies.
- When behavior changes, update only the owning doc above and add cross-links instead of repeating the same explanation elsewhere.
- Before finishing documentation work, scan stale planning language with `rg -n "V1|v1|Phase|Implementation Flow" README.md docs`.
- For quick-start duplication, run `rg -n "Quick Start|快速开始" README.md docs` and keep matches limited to `README.md`.
- If a feature moves between beta scope and roadmap, update `docs/prd.md` and `docs/roadmap.md` together so current commitments and future plans stay consistent.

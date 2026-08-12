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
- Runtime wheels must serve the React editor from `src/figstudio/static` and must not require Node/npm after install.

## Completion Rules

- Before reporting implementation or documentation work complete, run `git status --short` and finish with a local commit for the task's changes. If earlier agent-created dirty work is part of the same unfinished FigStudio slice, include it in the commit instead of leaving it behind; report the commit hash and clean/dirty status.
- For roadmap-driven slices, close out implementation, verification, UI/docs discoverability, roadmap maturity/status sync, and the local commit together. Update only directly affected roadmap areas; if proof is blocked, record the partial or blocked state instead of upgrading maturity.
- Also update roadmap readiness/dependency notes when a slice improves or weakens the feasibility, risk profile, or implementation prerequisites of a future item, even if that item was not directly implemented. Phrase future-item updates as readiness, dependency, risk, or proof changes; do not mark the item implemented unless the user-facing capability shipped.
- Before any public tag or package publish, remove completed roadmap items from active roadmap docs; shipped history belongs in `CHANGELOG.md` and paired locale release notes.
- Before final status, remove ignored cache, temp, and build output created during the turn after inspecting paths and confirming they are ignored; do not delete dependency installs such as `.venv/` or `frontend/node_modules/` as routine cleanup.

## Documentation

- Follow ownership and sync rules in `docs/en/contributing/developer-guide.md` and `docs/zh/contributing/developer-guide.md`.
- Keep locale paths paired and top-level legacy docs as short compatibility stubs.
- Update the owning pages when behavior changes; build `CHANGELOG.md` and both release notes from the full previous-tag delta.

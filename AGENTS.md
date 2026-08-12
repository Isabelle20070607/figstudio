# AGENTS.md

Project guidance for `figstudio`.

## Commands

- Use `uv` for Python tasks: `uv run --extra dev pytest`, `uv run python -m figstudio`.
- Use `npm` inside `frontend/` for UI tasks: `npm run build`, `npm run check:bundle`, `npm run test:e2e`, `npm run dev`.
- Use `uv build` for release package verification; the Hatch hook builds and bundles the frontend.
- The `dev` extra intentionally uses `httpx2`; do not replace it with `httpx` without revalidating FastAPI/TestClient compatibility and deliberately updating `uv.lock`.

## Product Invariants

- Generated plotting code must remain plain Matplotlib OO code and must not require `figstudio` at runtime.
- Code writeback may only replace a unique `# figstudio:start <block_id>` to `# figstudio:end <block_id>` block. Never modify user data-processing code outside the controlled block.
- The local web server must bind to `127.0.0.1` by default.
- Do not use ports `8765` or `8766` as FigStudio defaults or smoke-test ports; reserve them for AnkiConnect/default-client compatibility and use `8767` unless the user overrides it.
- Treat notebook updates as semi-automatic: return replacement cell code instead of editing notebook files directly.
- Runtime wheels must serve the React editor from `src/figstudio/static` and must not require Node/npm after install.

## Completion Rules

- Before reporting implementation or documentation work complete, run `git status --short` and finish with a local commit for the task's changes. If earlier agent-created changes belong to the same unfinished piece of FigStudio work, include them in the commit instead of leaving them behind; report the commit hash and whether the worktree is clean.
- For work selected from the roadmap, complete the implementation, verification, UI/docs discoverability, roadmap maturity and status updates, and local commit together. Update only the directly affected roadmap areas; if verification cannot be completed, record the partial or blocked state instead of raising the maturity status.
- Also update roadmap readiness or dependency notes when the work changes a future item's feasibility, risks, or prerequisites, even if that item was not implemented. Describe those changes in terms of readiness, dependencies, risks, or proof; do not mark the future item implemented unless its user-facing capability has shipped.
- Before any public tag or package publish, remove completed roadmap items from active roadmap docs; shipped history belongs in `CHANGELOG.md` and paired locale release notes.
- Before reporting completion, remove ignored cache, temporary, and build files created during the task after inspecting their paths and confirming that Git ignores them; do not routinely delete dependency installs such as `.venv/` or `frontend/node_modules/`.

## Documentation

- Follow ownership and sync rules in `docs/en/contributing/developer-guide.md` and `docs/zh/contributing/developer-guide.md`.
- Keep corresponding English and Chinese paths paired, and retain top-level legacy docs only as short compatibility stubs.
- When behavior changes, update the pages responsible for documenting it; build `CHANGELOG.md` and both release notes from all changes since the previous tag.

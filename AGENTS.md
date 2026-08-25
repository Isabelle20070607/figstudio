# AGENTS.md

Project guidance for `figstudio`.

## Runtime and Validation

- Use the workspace profile `..\.agents\validation\figstudio.psd1`; developer and release commands live in the paired contributor guides.
- The `dev` extra intentionally uses `httpx2`; do not replace it with `httpx` without revalidating FastAPI/TestClient compatibility and deliberately updating `uv.lock`.

## Product Invariants

- Generated plotting code must remain plain Matplotlib OO code and must not require `figstudio` at runtime.
- Code writeback may only replace a unique `# figstudio:start <block_id>` to `# figstudio:end <block_id>` block. Never modify user data-processing code outside the controlled block.
- The local web server must bind to `127.0.0.1` by default.
- Do not use ports `8765` or `8766` as FigStudio defaults or smoke-test ports; reserve them for AnkiConnect/default-client compatibility and use `8767` unless the user overrides it.
- Treat notebook updates as semi-automatic: return replacement cell code instead of editing notebook files directly.
- Runtime wheels must serve the React editor from `src/figstudio/static` and must not require Node/npm after install.

## Completion Rules

- For substantive implementation or documentation work, make a local commit containing only task-owned changes. Include earlier agent changes only when they are part of the same unfinished work; report the commit and remaining worktree state.
- Follow the paired contributor guides for roadmap, release, and documentation closeout. Record blocked verification without advancing maturity.
- Roadmap work updates only affected maturity, readiness, dependencies, and risks; mark an item implemented only after its user-facing capability ships. Before tag or publish, move shipped items from active roadmaps to `CHANGELOG.md` and paired release notes.
- Remove only task-created ignored artifacts after verifying their paths and ignore status; dependency installations are not routine cleanup targets.

## Documentation

- Follow ownership and sync rules in `docs/en/contributing/developer-guide.md` and `docs/zh/contributing/developer-guide.md`.
- Keep corresponding English and Chinese paths paired, and retain top-level legacy docs only as short compatibility stubs.

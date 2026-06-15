# AGENTS.md

Project guidance for `figstudio`.

- Use `uv` for Python tasks: `uv run pytest`, `uv run python -m figstudio`.
- Use `npm` inside `frontend/` for UI tasks: `npm run build`, `npm run dev`.
- Generated plotting code must remain plain Matplotlib OO code and must not require `figstudio` at runtime.
- Code writeback may only replace a unique `# figstudio:start <block_id>` to `# figstudio:end <block_id>` block. Never modify user data-processing code outside the controlled block.
- The local web server must bind to `127.0.0.1` by default.
- Treat notebook writeback as semi-automatic: return replacement cell code, do not edit notebook files directly.

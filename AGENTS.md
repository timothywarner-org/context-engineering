# Repository Guidelines

## Project Structure & Module Organization

- `coretext-mcp/`: Node.js MCP server; source in `src/`, sample memory in `data/`, demos in `scripts/`.
- `stoic-mcp/`: npm workspace; `local/` is a TypeScript build targeting `dist/`, `azure/` holds deployment assets.
- `context_journal_mcp_local/` and `_azure/`: Python training servers with `requirements.txt`, diagrams, and instructor guides.
- Shared references live under `docs/`, `images/`, and top-level runbooks; reference them instead of duplicating assets.

## Build, Test, and Development Commands

- `cd coretext-mcp && npm install && npm run dev` for hot-reload development; use `npm run inspector` when you need protocol traces.
- `npm test` in `coretext-mcp` exercises the scripted client; rerun after changing tool schemas or data persistence.
- `cd stoic-mcp && npm install` hydrates workspaces, then `npm run build --workspace local` or `npm start --workspace local` to validate quote tooling.
- `cd context_journal_mcp_local && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`; confirm changes with `python context_journal_mcp.py --help`.

## Coding Style & Naming Conventions

- JavaScript and TypeScript use ES modules, 2-space indentation, semicolons, and `camelCase` utilities; keep DTOs beside their tool handlers.
- Python follows 4-space indentation, `snake_case`, and type-hinted Pydantic models.
- Environment variables stay in `.env` files cloned from `.env.example`; document new keys in the nearest README before use.

## Testing Guidelines

- Extend the `coretext-mcp` smoke test (`npm test`) whenever you add commands or storage paths, and record expected output in PRs.
- `stoic-mcp` currently depends on Inspector/manual checks; capture CLI transcripts when adjusting importers or Azure bindings.
- For the Python servers, adopt `pytest` under `context_journal_mcp_local/tests` when introducing automated coverage so both phases share fixtures.

## Commit & Pull Request Guidelines

- Mirror the existing history: imperative, sentence-case summaries under ~70 characters (example: `Add Azure deployment infrastructure for CoreText`).
- Use the body to list modules touched and test commands; flag required config changes or secret rotations.
- PRs should link issues when available, include setup/rollback notes, and add Inspector or console screenshots for demo updates.

## Security & Configuration Tips

- Do not commit populated `.env` files or filled `parameters.json`; load secrets through Azure Key Vault or local managers.
- Review deployment defaults in `coretext-mcp/azure` and `stoic-mcp/azure` before running pipelines—resource names and regions must match the target tenant.
- Scrub sample datasets in `data/` and `docs/` before sharing externally to avoid leaking course attendee information.

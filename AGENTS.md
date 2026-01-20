# Repository Guidelines

## Project Structure & Module Organization
- `mcp-servers/` contains runnable MCP servers (Node, TypeScript, Python) such as `coretext-mcp/`, `stoic-mcp/`, `context_journal_mcp_local/`, `context_journal_mcp_azure/`, and `deepseek-context-demo/`.
- `labs/` holds course exercises; `labs/lab-01-hello-mcp/` includes `starter/` and `solution/`.
- `docs/`, `diagrams/`, and `instructor/` store course docs, architecture notes, and teaching materials.
- `config/` provides sample config files; `images/` holds assets used in documentation.

## Build, Test, and Development Commands
- `mcp-servers/coretext-mcp`: `npm install`, `npm start` (run server), `npm run dev` (watch mode), `npm run inspector`, `npm test` (test client).
- `mcp-servers/stoic-mcp`: `npm install`, `npm run build` (all workspaces), `npm run clean`.
- `mcp-servers/stoic-mcp/local`: `npm install`, `npm run build`, `npm start`, `npm run inspector`, `npm run import <quotes.txt>`.
- `mcp-servers/context_journal_mcp_local`: `pip install -r requirements.txt`, `python context_journal_mcp.py --help` (server entry).
- `mcp-servers/deepseek-context-demo`: `npm install`, `npm start`.

## Coding Style & Naming Conventions
- JavaScript and TypeScript use 2-space indentation and ES modules (`import ... from`).
- Python files use 4-space indentation and snake_case filenames (example: `context_journal_mcp.py`).
- Match existing naming patterns such as `src/index.js`, `src/index.ts`, `scripts/demo-segment1.js`, and guide files in `UPPER_SNAKE.md`.

## Testing Guidelines
- `coretext-mcp` has an automated test client: run `npm test` in `mcp-servers/coretext-mcp`.
- Other servers rely on manual checks via `npm run inspector` or their README checklists.
- Add or update tests alongside tool changes when possible; document manual verification if no tests exist.

## Commit & Pull Request Guidelines
- Commit messages are short, imperative, sentence case (example: "Reorganize repository structure for condensed 2-hour course").
- PRs should describe scope, affected subproject, and how you verified changes (commands and results). Include screenshots for diagram or doc updates when useful.
- Link related issues if applicable.

## Security & Configuration Tips
- Use `.env.example` in server folders as templates; do not commit secrets.
- Keep config samples in `config/` and update docs when configuration steps change.

## Agent-Specific Instructions
- Review `CLAUDE.md` and any subproject guidance such as `mcp-servers/coretext-mcp/CLAUDE.md` before automated edits.

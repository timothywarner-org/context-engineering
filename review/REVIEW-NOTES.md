# Review Folder - Items for Potential Deletion

**Created:** January 2026
**Purpose:** Contains legacy/deprecated code that has been superseded by newer implementations. Review before permanent deletion.

---

## Contents

### 1. `context_journal_mcp_azure/`
**What:** Python MCP server for context journal with Azure Cosmos DB
**Why moved:** Superseded by `memory_server/` + `memory_stores/` which offers:
- More flexible storage backends (JSON, SQLite, ChromaDB, Pinecone)
- Modern FastMCP patterns
- Better abstraction via interface pattern
- Same CRUD functionality but more extensible

**Keep if:** Need historical example of older MCP patterns for comparison teaching

---

### 2. `context_journal_mcp_local/`
**What:** Python MCP server for context journal with local JSON storage
**Why moved:** Same as above - superseded by `memory_server/` + `memory_stores/json_store.py`

**Keep if:** Need step-by-step migration example (local → Azure)

---

### 3. `GEMINI.md`
**What:** Guidelines for Gemini AI assistant
**Why moved:** Largely duplicates `CLAUDE.md` content. Could consolidate into single `LLM_ASSISTANT.md`

**Keep if:** Using multiple AI assistants and want separate configs

---

## What's Staying (NOT in this folder)

| Directory | Reason to Keep |
|-----------|----------------|
| `coretext-mcp/` | JavaScript teaching example, richer resources |
| `stoic-mcp/` | TypeScript example, different domain (quotes) |
| `deepseek-context-demo/` | Segment 1 visualization tool |
| `memory_server/` | **Canonical** - modern FastMCP implementation |
| `memory_stores/` | Pluggable backend infrastructure |
| `langgraph_integration/` | Advanced Segment 4 patterns |
| `labs/` | Essential hands-on exercises |
| `config/` | Client setup templates |
| `docs/` | Student documentation |
| `diagrams/` | Architecture visuals |
| `AGENTS.md` | Active development guidelines |
| `CLAUDE.md` | Active AI assistant guidelines |

---

## Recommendation

After review, if items are confirmed unneeded:
```bash
rm -rf review/  # Delete entire review folder
```

Or to restore:
```bash
mv review/context_journal_mcp_azure mcp-servers/
mv review/context_journal_mcp_local mcp-servers/
mv review/GEMINI.md ./
```

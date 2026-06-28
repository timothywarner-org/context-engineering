# MCP Chat

MCP Chat is a command-line interface application that enables interactive chat capabilities with Claude through the Anthropic API. The application supports document retrieval, command-based prompts, and extensible tool integrations via the **Model Context Protocol** (MCP).

> **Attribution:** This code is reference material from Anthropic's [Claude with the Anthropic API](https://anthropic.skilljar.com/claude-with-the-anthropic-api/) Skilljar course, vendored here as study material for the Claude Architect Foundations training. See [`./NOTICE.md`](./NOTICE.md) for full attribution and modifications.

## Prerequisites

- Python 3.10+ (the upstream README said 3.9+; `pyproject.toml` pins `>=3.10`)
- An Anthropic API key from https://console.anthropic.com

## Quickstart (on-rails, one command)

From the repo root, the wrapper script handles `.env` bootstrap and the `uv run` handoff in one shot:

```powershell
.\scripts\run-mcp-cli.ps1
```

What it does on **first run**:

1. Creates `examples/mcp_cli/.env` from `.env.example` if it does not exist.
2. Lifts `ANTHROPIC_API_KEY` from the repo-root `.env` (the one the teaching notebooks already use) so you do not paste the key twice.
3. Invokes `uv run --directory examples/mcp_cli main.py`. uv auto-creates `examples/mcp_cli/.venv` and installs all deps (~20s cold, ~1.5s warm thereafter).

Subsequent runs skip step 1 and 2 and go straight to the REPL. The script is idempotent.

If you have **no repo-root `.env`**, the wrapper creates a stub `.env` inside `examples/mcp_cli/` and exits non-zero with a "fill in your key" message so you do not burn tokens on a placeholder.

The manual ceremony below is preserved for reference fidelity with the upstream Skilljar course.

## Manual setup (upstream Skilljar workflow, kept for reference)

### Step 1: Configure the environment variables

1. Copy `.env.example` to `.env` and fill in your API key:

   ```powershell
   Copy-Item .env.example .env
   ```

   The committed template has the variables you need:

   ```
   CLAUDE_MODEL="claude-sonnet-4-6"
   ANTHROPIC_API_KEY=""  # paste your key here
   USE_UV=1              # set to 0 if not using uv
   ```

   The `.env` file is gitignored.

### Step 2: Install dependencies

#### Option 1: Setup with uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

1. Install uv, if not already installed:

```bash
pip install uv
```

2. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
uv pip install -e .
```

4. Run the project

```bash
uv run main.py
```

#### Option 2: Setup without uv

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install anthropic python-dotenv prompt-toolkit "mcp[cli]==1.8.0"
```

3. Run the project

```bash
python main.py
```

## Usage

### Basic Interaction

Simply type your message and press Enter to chat with the model.

### Document Retrieval

Use the @ symbol followed by a document ID to include document content in your query:

```
> Tell me about @deposition.md
```

### Commands

Use the / prefix to execute commands defined in the MCP server:

```
> /summarize deposition.md
```

Commands will auto-complete when you press Tab.

## Development

### Adding New Documents

Edit the `mcp_server.py` file to add new documents to the `docs` dictionary.

### Implementing MCP Features

The MCP features are **already implemented** in this copy — `mcp_server.py` registers the tools, resources, and prompt, and `mcp_client.py` implements `list_tools` / `call_tool` / `list_prompts` / `get_prompt` / `read_resource`. The upstream scaffold shipped with `# TODO` markers above these; this vendored copy has them filled in, so the app runs as-is. The old TODO comments are kept inline as a teaching artifact so you can see the before/after.

### Linting and Typing Check

There are no lint or type checks implemented.

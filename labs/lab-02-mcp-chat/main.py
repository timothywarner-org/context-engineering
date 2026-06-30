import asyncio
import sys
import os
import shutil
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp_client import MCPClient
from core.claude import Claude

from core.cli_chat import CliChat
from core.cli import CliApp

load_dotenv()

# Anthropic Config
claude_model = os.getenv("CLAUDE_MODEL", "")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")


assert claude_model, "Error: CLAUDE_MODEL cannot be empty. Update .env"
assert anthropic_api_key, (
    "Error: ANTHROPIC_API_KEY cannot be empty. Update .env"
)


async def main():
    claude_service = Claude(model=claude_model)

    server_scripts = sys.argv[1:]
    clients = {}

    # How to launch the MCP server subprocess. The server's deps (mcp, pydantic)
    # live in this project's uv-managed .venv, so bare `python mcp_server.py`
    # only works if that venv's interpreter is already active. Default to `uv run`
    # whenever uv is on PATH so the subprocess always resolves its deps; honor an
    # explicit USE_UV=0 for learners who deliberately run without uv. This makes
    # the app correct regardless of whether an older .env set USE_UV.
    use_uv_env = os.getenv("USE_UV")
    if use_uv_env is None:
        use_uv = shutil.which("uv") is not None
    else:
        use_uv = use_uv_env == "1"

    command, args = (
        ("uv", ["run", "mcp_server.py"])
        if use_uv
        else (sys.executable, ["mcp_server.py"])
    )

    async with AsyncExitStack() as stack:
        doc_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )
        clients["doc_client"] = doc_client

        for i, server_script in enumerate(server_scripts):
            client_id = f"client_{i}_{server_script}"
            client = await stack.enter_async_context(
                MCPClient(command="uv", args=["run", server_script])
            )
            clients[client_id] = client

        chat = CliChat(
            doc_client=doc_client,
            clients=clients,
            claude_service=claude_service,
        )

        cli = CliApp(chat)
        await cli.initialize()
        await cli.run()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # A second Ctrl+C can interrupt MCP stdio subprocess cleanup on Windows.
        # Treat that as an operator-requested shutdown, not a crash report.
        print("\nInterrupted. MCP CLI stopped.")

"""MCP stdio server entry point for WARNERCO Robotics Schematica.

This module provides the stdio transport for MCP, allowing the tools
to be used with Claude Desktop, VS Code, and other MCP clients.

Usage with uv:
    uv run warnerco-mcp

Usage with Poetry:
    poetry run warnerco-mcp

Direct execution:
    python -m app.mcp_stdio
"""

import sys
from pathlib import Path

# Ensure the app module is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.mcp_tools import mcp


def main():
    """Run the MCP server using stdio transport."""
    # FastMCP's run() method handles stdio transport by default
    mcp.run()


if __name__ == "__main__":
    main()

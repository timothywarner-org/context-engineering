"""Minimal MCP server on the OFFICIAL Python SDK (mcp.server.fastmcp).

Segment 2 teaching artifact. The course says "official Anthropic SDKs first,"
so this is the reference for the official path: `from mcp.server.fastmcp import
FastMCP`, shipped inside the `mcp` package. Contrast with WARNERCO, which runs
on the standalone `fastmcp` package (now Anthropic-stewarded). Both speak the
same protocol; the import and a few method names differ.

Two-SDK cheat sheet (introspection):
    official  (mcp.server.fastmcp):  await mcp.list_tools()
    standalone (fastmcp):            await mcp.get_tools()

Run it:
    uv run --with mcp python official_sdk_server.py           # stdio
    npx @modelcontextprotocol/inspector uv run --with mcp python official_sdk_server.py
"""
from mcp.server.fastmcp import FastMCP

# One server object. The name shows up in the client's server list.
mcp = FastMCP("hello-official-sdk")


@mcp.tool()
def add(a: float, b: float) -> str:
    """Add two numbers and return a human-readable result.

    The SDK builds the JSON schema from these type hints and this docstring -
    no hand-written schema. That auto-generation is the whole point of FastMCP.
    """
    return f"The sum of {a} and {b} is {a + b}"


@mcp.resource("demo://greeting")
def greeting() -> str:
    """A read-only resource. Resources are data the client can pull into context;
    tools are actions the model can invoke. Same server, different primitive."""
    return "Hello from the official MCP Python SDK."


@mcp.prompt()
def explain_mcp() -> str:
    """A reusable prompt template - the third primitive. Clients surface these
    as slash commands or pickable templates."""
    return "Explain the Model Context Protocol to a developer in three sentences."


if __name__ == "__main__":
    # Default transport is stdio - the local-first default the course recommends.
    mcp.run()

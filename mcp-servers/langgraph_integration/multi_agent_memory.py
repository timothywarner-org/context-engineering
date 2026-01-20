"""
LangGraph Multi-Agent Memory Integration
========================================
Demonstrates using MCP memory servers with LangGraph workflows.

This example shows how multiple AI agents can share context through
a common MCP memory server, enabling sophisticated multi-step workflows.

Requirements:
    pip install langgraph langchain-anthropic mcp

Usage:
    python multi_agent_memory.py

Author: Tim Warner
Course: Context Engineering with MCP
"""

import asyncio
import json
import os
from typing import TypedDict, Annotated, Sequence, Optional
import operator

# LangGraph imports
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

# MCP Client imports
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP client not available. Install with: pip install mcp")


# ============================================================================
# Configuration
# ============================================================================

MEMORY_SERVER_CMD = ["python", "../memory_server/server.py"]
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"


# ============================================================================
# State Definition
# ============================================================================

class AgentState(TypedDict):
    """State shared between all agents in the workflow."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    memory_context: str
    current_task: str
    research_findings: str
    analysis: str
    final_output: str
    error: Optional[str]


# ============================================================================
# MCP Memory Client
# ============================================================================

class MCPMemoryClient:
    """
    Client for interacting with MCP memory server.

    Provides async methods to store and retrieve memories,
    designed for integration with LangGraph agent workflows.
    """

    def __init__(self, server_command: list):
        """
        Initialize MCP memory client.

        Args:
            server_command: Command to start the MCP server
        """
        self.server_params = StdioServerParameters(
            command=server_command[0],
            args=server_command[1:]
        )
        self.session: Optional[ClientSession] = None
        self._read = None
        self._write = None

    async def connect(self):
        """Establish connection to MCP server."""
        if not MCP_AVAILABLE:
            raise ImportError("MCP client not available")

        # Start the server and get read/write streams
        self._read, self._write = await stdio_client(self.server_params).__aenter__()

        # Create client session
        self.session = ClientSession(self._read, self._write)
        await self.session.initialize()

        # List available tools for verification
        tools = await self.session.list_tools()
        print(f"Connected to MCP server with {len(tools.tools)} tools")

    async def disconnect(self):
        """Close connection to MCP server."""
        if self.session:
            # Clean shutdown would go here
            self.session = None

    async def store_memory(
        self,
        content: str,
        category: str = "general",
        tags: list = None,
        importance: int = 5
    ) -> dict:
        """
        Store a memory via MCP tool.

        Args:
            content: The content to remember
            category: Category for organization
            tags: Tags for filtering
            importance: Importance score 1-10

        Returns:
            Response from the MCP tool
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.call_tool(
            "store_memory",
            {
                "content": content,
                "category": category,
                "tags": tags or [],
                "importance": importance
            }
        )

        return json.loads(result.content[0].text)

    async def search_memories(
        self,
        query: str,
        limit: int = 5,
        category: Optional[str] = None
    ) -> dict:
        """
        Search memories via MCP tool.

        Args:
            query: Search query
            limit: Maximum results
            category: Optional category filter

        Returns:
            Search results from MCP tool
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        params = {
            "query": query,
            "limit": limit
        }
        if category:
            params["category"] = category

        result = await self.session.call_tool("search_memories", params)
        return json.loads(result.content[0].text)

    async def get_context(self) -> str:
        """
        Get relevant context for current task.

        Returns:
            Recent memories as context string
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.read_resource("memory://recent")
        return result.contents[0].text

    async def get_important_context(self) -> str:
        """
        Get high-importance memories.

        Returns:
            Important memories as context string
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.read_resource("memory://important")
        return result.contents[0].text


# ============================================================================
# Agent Nodes
# ============================================================================

# Global memory client (initialized in main)
memory_client: Optional[MCPMemoryClient] = None


async def research_node(state: AgentState) -> AgentState:
    """
    Research agent: Gathers information and retrieves relevant context.

    This agent:
    1. Searches existing memories for relevant context
    2. Performs research on the task
    3. Stores findings in memory for future use
    """
    task = state["current_task"]

    # Search for relevant existing context
    try:
        search_results = await memory_client.search_memories(task, limit=5)
        existing_context = json.dumps(search_results.get("results", []), indent=2)
    except Exception as e:
        existing_context = f"No existing context found: {e}"

    # Create research prompt
    model = ChatAnthropic(model=ANTHROPIC_MODEL, temperature=0)

    research_prompt = f"""You are a research agent. Your task is to gather relevant information.

TASK: {task}

EXISTING CONTEXT FROM MEMORY:
{existing_context}

Please research this topic and provide:
1. Key facts and information
2. Relevant background context
3. Important considerations
4. Sources or references if applicable

Be thorough but concise. Focus on actionable information."""

    response = await model.ainvoke([HumanMessage(content=research_prompt)])
    findings = response.content

    # Store research findings in memory
    try:
        await memory_client.store_memory(
            content=f"Research findings for '{task}': {findings[:500]}...",
            category="research",
            tags=["research", "findings"],
            importance=7
        )
    except Exception as e:
        print(f"Warning: Could not store research findings: {e}")

    return {
        **state,
        "messages": state["messages"] + [response],
        "memory_context": existing_context,
        "research_findings": findings
    }


async def analysis_node(state: AgentState) -> AgentState:
    """
    Analysis agent: Processes research findings and extracts insights.

    This agent:
    1. Analyzes the research findings
    2. Identifies key insights and patterns
    3. Stores analysis in memory
    """
    model = ChatAnthropic(model=ANTHROPIC_MODEL, temperature=0)

    analysis_prompt = f"""You are an analysis agent. Your task is to synthesize research into insights.

ORIGINAL TASK: {state["current_task"]}

RESEARCH FINDINGS:
{state["research_findings"]}

MEMORY CONTEXT:
{state["memory_context"]}

Please provide:
1. Key insights from the research
2. Patterns or themes identified
3. Potential implications
4. Recommendations based on analysis

Be analytical and structured in your response."""

    response = await model.ainvoke([HumanMessage(content=analysis_prompt)])
    analysis = response.content

    # Store analysis in memory
    try:
        await memory_client.store_memory(
            content=f"Analysis for '{state['current_task']}': {analysis[:500]}...",
            category="analysis",
            tags=["analysis", "insights"],
            importance=8
        )
    except Exception as e:
        print(f"Warning: Could not store analysis: {e}")

    return {
        **state,
        "messages": state["messages"] + [response],
        "analysis": analysis
    }


async def generation_node(state: AgentState) -> AgentState:
    """
    Generation agent: Creates final output based on analysis.

    This agent:
    1. Synthesizes all previous work
    2. Generates comprehensive final output
    3. Stores summary in memory for future reference
    """
    model = ChatAnthropic(model=ANTHROPIC_MODEL, temperature=0.3)

    generation_prompt = f"""You are a generation agent. Create a comprehensive response.

ORIGINAL TASK: {state["current_task"]}

RESEARCH FINDINGS:
{state["research_findings"]}

ANALYSIS:
{state["analysis"]}

Based on all the above, generate a comprehensive, well-structured response that:
1. Directly addresses the original task
2. Incorporates key research findings
3. Applies analytical insights
4. Provides actionable conclusions

Make the response clear, professional, and useful."""

    response = await model.ainvoke([HumanMessage(content=generation_prompt)])
    final_output = response.content

    # Store final output summary in memory
    try:
        await memory_client.store_memory(
            content=f"Completed task '{state['current_task']}': {final_output[:300]}...",
            category="completed",
            tags=["output", "completed"],
            importance=9
        )
    except Exception as e:
        print(f"Warning: Could not store final output: {e}")

    return {
        **state,
        "messages": state["messages"] + [response],
        "final_output": final_output
    }


# ============================================================================
# Workflow Graph
# ============================================================================

def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow with MCP memory integration.

    The workflow consists of three sequential agents:
    1. Research Agent: Gathers information and context
    2. Analysis Agent: Processes and synthesizes findings
    3. Generation Agent: Creates final output

    All agents share context through the MCP memory server.

    Returns:
        Compiled LangGraph workflow
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("analyze", analysis_node)
    workflow.add_node("generate", generation_node)

    # Define edges (sequential flow)
    workflow.set_entry_point("research")
    workflow.add_edge("research", "analyze")
    workflow.add_edge("analyze", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()


# ============================================================================
# Main Entry Point
# ============================================================================

async def run_workflow(task: str) -> str:
    """
    Run the multi-agent workflow with MCP memory.

    Args:
        task: The task to accomplish

    Returns:
        Final generated output
    """
    global memory_client

    # Initialize memory client
    memory_client = MCPMemoryClient(MEMORY_SERVER_CMD)

    try:
        # Connect to MCP server
        print("Connecting to MCP memory server...")
        await memory_client.connect()

        # Create and run workflow
        print("Creating workflow...")
        workflow = create_workflow()

        print(f"Running workflow for task: {task}")
        result = await workflow.ainvoke({
            "messages": [],
            "memory_context": "",
            "current_task": task,
            "research_findings": "",
            "analysis": "",
            "final_output": "",
            "error": None
        })

        return result["final_output"]

    finally:
        # Disconnect from MCP server
        await memory_client.disconnect()


async def main():
    """Main entry point with example usage."""
    print("=" * 60)
    print("LangGraph Multi-Agent Memory Integration Demo")
    print("=" * 60)

    # Example task
    task = "Analyze the best practices for implementing authentication in a REST API"

    try:
        result = await run_workflow(task)

        print("\n" + "=" * 60)
        print("FINAL OUTPUT")
        print("=" * 60)
        print(result)

    except Exception as e:
        print(f"Error running workflow: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

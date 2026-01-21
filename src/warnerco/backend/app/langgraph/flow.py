"""LangGraph flow for retrieval-augmented reasoning about robot schematics."""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Annotated, Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field

from app.adapters import get_memory_store
from app.config import settings
from app.models import SearchResult


class QueryIntent(str, Enum):
    """Classified query intent types."""

    LOOKUP = "lookup"  # Direct lookup by ID or name
    DIAGNOSTIC = "diagnostic"  # Troubleshooting, status queries
    ANALYTICS = "analytics"  # Aggregations, statistics
    SEARCH = "search"  # General semantic search


class GraphState(TypedDict):
    """State passed between LangGraph nodes."""

    # Input
    query: str
    filters: Optional[Dict[str, Any]]
    top_k: int

    # Processing
    intent: Optional[QueryIntent]
    candidates: List[SearchResult]
    compressed_context: str

    # Output
    response: Dict[str, Any]
    error: Optional[str]

    # Telemetry
    start_time: str
    timings: Dict[str, float]


class QueryResponse(BaseModel):
    """Structured response from the LangGraph flow."""

    success: bool
    intent: str
    results: List[Dict[str, Any]]
    context_summary: str
    total_matches: int
    query_time_ms: float
    reasoning: Optional[str] = None


def parse_intent(state: GraphState) -> GraphState:
    """Classify the query intent based on keywords and patterns.

    Node 1: Parse Intent
    """
    query_lower = state["query"].lower()

    # Check for direct lookup patterns
    if any(pattern in query_lower for pattern in ["wrn-", "wc-", "id:", "get "]):
        state["intent"] = QueryIntent.LOOKUP

    # Check for diagnostic patterns
    elif any(pattern in query_lower for pattern in [
        "status", "problem", "issue", "error", "failing",
        "maintenance", "offline", "not working", "diagnose"
    ]):
        state["intent"] = QueryIntent.DIAGNOSTIC

    # Check for analytics patterns
    elif any(pattern in query_lower for pattern in [
        "how many", "count", "total", "statistics", "breakdown",
        "distribution", "all ", "list all", "summary"
    ]):
        state["intent"] = QueryIntent.ANALYTICS

    # Default to semantic search
    else:
        state["intent"] = QueryIntent.SEARCH

    state["timings"]["parse_intent"] = _elapsed_ms(state["start_time"])
    return state


async def retrieve(state: GraphState) -> GraphState:
    """Retrieve candidate schematics from memory backend.

    Node 2: Retrieve
    """
    memory = get_memory_store()

    try:
        # For lookup, try to extract specific ID
        if state["intent"] == QueryIntent.LOOKUP:
            # Try to find ID pattern in query
            import re
            id_match = re.search(r"(WRN-\d+)", state["query"].upper())
            if id_match:
                schematic = await memory.get_schematic(id_match.group(1))
                if schematic:
                    state["candidates"] = [
                        SearchResult(schematic=schematic, score=1.0, chunk_id=schematic.id)
                    ]
                else:
                    state["candidates"] = []
            else:
                # Fall back to search
                state["candidates"] = await memory.semantic_search(
                    state["query"], state["filters"], state["top_k"]
                )

        # For analytics, get all matching and compute stats
        elif state["intent"] == QueryIntent.ANALYTICS:
            # Get broader results for analytics
            state["candidates"] = await memory.semantic_search(
                state["query"], state["filters"], min(state["top_k"] * 2, 20)
            )

        # For diagnostic/search, use semantic search
        else:
            state["candidates"] = await memory.semantic_search(
                state["query"], state["filters"], state["top_k"]
            )

    except Exception as e:
        state["error"] = f"Retrieval error: {str(e)}"
        state["candidates"] = []

    state["timings"]["retrieve"] = _elapsed_ms(state["start_time"])
    return state


def compress_context(state: GraphState) -> GraphState:
    """Minimize token bloat by extracting only needed fields.

    Node 3: Compress Context
    """
    if not state["candidates"]:
        state["compressed_context"] = "No matching schematics found."
        state["timings"]["compress_context"] = _elapsed_ms(state["start_time"])
        return state

    # Build compressed context based on intent
    if state["intent"] == QueryIntent.LOOKUP:
        # Full details for lookup
        contexts = []
        for result in state["candidates"][:3]:
            s = result.schematic
            context = f"""
[{s.id}] {s.model} - {s.name}
Component: {s.component} ({s.version})
Category: {s.category} | Status: {s.status.value}
Summary: {s.summary}
Specs: {json.dumps(s.specifications) if s.specifications else 'N/A'}
"""
            contexts.append(context.strip())
        state["compressed_context"] = "\n\n".join(contexts)

    elif state["intent"] == QueryIntent.ANALYTICS:
        # Aggregate data for analytics
        categories = {}
        models = {}
        statuses = {}
        for result in state["candidates"]:
            s = result.schematic
            categories[s.category] = categories.get(s.category, 0) + 1
            models[s.model] = models.get(s.model, 0) + 1
            statuses[s.status.value] = statuses.get(s.status.value, 0) + 1

        state["compressed_context"] = f"""
Found {len(state['candidates'])} matching schematics.
Categories: {json.dumps(categories)}
Models: {json.dumps(models)}
Statuses: {json.dumps(statuses)}
"""

    else:
        # Concise summaries for search/diagnostic
        contexts = []
        for result in state["candidates"][:5]:
            s = result.schematic
            context = f"[{s.id}] {s.model}/{s.name}: {s.component} ({s.category}) - {s.summary[:100]}..."
            contexts.append(context)
        state["compressed_context"] = "\n".join(contexts)

    state["timings"]["compress_context"] = _elapsed_ms(state["start_time"])
    return state


async def reason(state: GraphState) -> GraphState:
    """Call LLM for reasoning (stub if no LLM configured).

    Node 4: Reason
    """
    # If LLM is configured, use it for enhanced reasoning
    if settings.has_llm_config:
        try:
            from langchain_openai import ChatOpenAI

            if settings.azure_openai_endpoint:
                from langchain_openai import AzureChatOpenAI
                llm = AzureChatOpenAI(
                    azure_endpoint=settings.azure_openai_endpoint,
                    api_key=settings.azure_openai_api_key,
                    azure_deployment=settings.azure_openai_deployment,
                    api_version=settings.azure_openai_api_version,
                )
            else:
                llm = ChatOpenAI(
                    api_key=settings.openai_api_key,
                    model="gpt-4o-mini",
                )

            prompt = f"""You are a robotics engineer assistant. Based on the query and context, provide a helpful response.

Query: {state['query']}
Intent: {state['intent'].value if state['intent'] else 'unknown'}

Context:
{state['compressed_context']}

Provide a concise, technical response that directly addresses the query."""

            response = await llm.ainvoke(prompt)
            state["response"]["reasoning"] = response.content

        except Exception as e:
            # Fallback to stub reasoning
            state["response"]["reasoning"] = f"[LLM unavailable: {str(e)}] Based on retrieved data."

    else:
        # Stub reasoning without LLM
        intent = state["intent"].value if state["intent"] else "search"
        count = len(state["candidates"])

        if count == 0:
            state["response"]["reasoning"] = f"No schematics found matching your {intent} query."
        elif intent == "lookup":
            state["response"]["reasoning"] = f"Found {count} schematic(s) matching your lookup."
        elif intent == "analytics":
            state["response"]["reasoning"] = f"Analytics summary based on {count} matching schematics."
        elif intent == "diagnostic":
            state["response"]["reasoning"] = f"Found {count} relevant schematic(s) for diagnostics."
        else:
            state["response"]["reasoning"] = f"Found {count} schematic(s) matching your search."

    state["timings"]["reason"] = _elapsed_ms(state["start_time"])
    return state


def respond(state: GraphState) -> GraphState:
    """Format final response for dashboards and MCP.

    Node 5: Respond
    """
    total_time = _elapsed_ms(state["start_time"])

    state["response"] = {
        "success": state["error"] is None,
        "intent": state["intent"].value if state["intent"] else "unknown",
        "results": [
            {
                "id": r.schematic.id,
                "model": r.schematic.model,
                "name": r.schematic.name,
                "component": r.schematic.component,
                "category": r.schematic.category,
                "summary": r.schematic.summary,
                "score": r.score,
                "status": r.schematic.status.value,
            }
            for r in state["candidates"]
        ],
        "context_summary": state["compressed_context"],
        "total_matches": len(state["candidates"]),
        "query_time_ms": total_time,
        "reasoning": state["response"].get("reasoning", ""),
        "error": state["error"],
        "timings": state["timings"],
    }

    return state


def _elapsed_ms(start_time: str) -> float:
    """Calculate elapsed milliseconds from ISO timestamp."""
    start = datetime.fromisoformat(start_time)
    return (datetime.utcnow() - start).total_seconds() * 1000


class SchematicaGraph:
    """LangGraph orchestration for schematic queries."""

    def __init__(self):
        """Initialize the graph."""
        self._graph = None

    async def _build_graph(self):
        """Build the LangGraph workflow."""
        try:
            from langgraph.graph import StateGraph, END

            workflow = StateGraph(GraphState)

            # Add nodes
            workflow.add_node("parse_intent", parse_intent)
            workflow.add_node("retrieve", retrieve)
            workflow.add_node("compress_context", compress_context)
            workflow.add_node("reason", reason)
            workflow.add_node("respond", respond)

            # Define edges
            workflow.set_entry_point("parse_intent")
            workflow.add_edge("parse_intent", "retrieve")
            workflow.add_edge("retrieve", "compress_context")
            workflow.add_edge("compress_context", "reason")
            workflow.add_edge("reason", "respond")
            workflow.add_edge("respond", END)

            self._graph = workflow.compile()

        except ImportError:
            # Fallback if langgraph not available
            self._graph = None

    async def run(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Run the graph on a query."""
        if self._graph is None:
            await self._build_graph()

        initial_state: GraphState = {
            "query": query,
            "filters": filters,
            "top_k": top_k,
            "intent": None,
            "candidates": [],
            "compressed_context": "",
            "response": {},
            "error": None,
            "start_time": datetime.utcnow().isoformat(),
            "timings": {},
        }

        if self._graph:
            # Run through LangGraph
            result = await self._graph.ainvoke(initial_state)
            return result["response"]
        else:
            # Fallback: run nodes sequentially
            state = parse_intent(initial_state)
            state = await retrieve(state)
            state = compress_context(state)
            state = await reason(state)
            state = respond(state)
            return state["response"]


# Singleton instance
_graph: Optional[SchematicaGraph] = None


async def run_query(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    top_k: int = 5,
) -> Dict[str, Any]:
    """Run a query through the LangGraph flow.

    Args:
        query: Natural language query
        filters: Optional filters (category, model, status)
        top_k: Number of results to return

    Returns:
        QueryResponse as dictionary
    """
    global _graph
    if _graph is None:
        _graph = SchematicaGraph()

    return await _graph.run(query, filters, top_k)

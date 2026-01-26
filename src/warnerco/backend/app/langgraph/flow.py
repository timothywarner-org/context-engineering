"""LangGraph flow for retrieval-augmented reasoning about robot schematics.

This module implements a 7-node RAG pipeline with Knowledge Graph and Scratchpad integration:

    parse_intent -> query_graph -> inject_scratchpad -> retrieve -> compress_context -> reason -> respond

The query_graph node enriches the context with relationship data from the
Knowledge Graph, enabling the LLM to understand connections between entities
that vector search alone cannot capture.

The inject_scratchpad node adds session-scoped working memory context,
allowing the system to remember observations and inferences from the current session.
"""

import json
import re
import threading
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Annotated, Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field

from app.adapters import get_memory_store
from app.adapters.graph_store import get_graph_store
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
    graph_context: List[str]  # Context from Knowledge Graph
    scratchpad_context: List[str]  # Context from Scratchpad Memory
    scratchpad_token_count: int  # Tokens used by scratchpad context
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


def extract_entities(query: str) -> List[str]:
    """Extract entity mentions from a query string.

    This function identifies references to:
    - Schematic IDs (WRN-XXXXX pattern)
    - Model IDs (WC-XXX pattern)
    - Status keywords (active, deprecated, etc.)
    - Category keywords (sensors, power, etc.)
    - Component keywords (hydraulic, sensor, etc.)

    Args:
        query: The search query string

    Returns:
        List of entity IDs found in the query
    """
    query_lower = query.lower()
    query_upper = query.upper()
    mentioned_entities = []

    # 1. Check for schematic IDs (WRN-XXXXX pattern)
    id_matches = re.findall(r"WRN-\d+", query_upper)
    mentioned_entities.extend(id_matches)

    # 2. Check for model IDs (WC-XXX pattern)
    model_matches = re.findall(r"WC-\d+", query_upper)
    for model in model_matches:
        mentioned_entities.append(f"model:{model}")

    # 3. Check for status keywords
    status_keywords = ["active", "deprecated", "draft", "offline", "maintenance"]
    for status in status_keywords:
        if status in query_lower:
            mentioned_entities.append(f"status:{status}")

    # 4. Check for category keywords
    category_keywords = [
        "sensors", "power", "control", "mobility", "communication",
        "thermal", "safety", "actuators", "manipulation", "tooling",
        "structural", "mechanical", "environmental"
    ]
    for category in category_keywords:
        if category in query_lower:
            mentioned_entities.append(f"category:{category}")

    # 5. Check for component keywords
    component_keywords = {
        "hydraulic": "component:hydraulic_system",
        "sensor": "component:sensor_array",
        "motor": "component:motor_system",
        "battery": "component:power_system",
        "thermal": "component:thermal_system",
        "lidar": "component:lidar_system",
        "camera": "component:vision_system",
        "wireless": "component:communication_system",
        "safety": "component:safety_system",
        "gripper": "component:manipulation_system",
        "welding": "component:welding_system",
        "navigation": "component:navigation_system",
    }
    for keyword, component_id in component_keywords.items():
        if keyword in query_lower:
            mentioned_entities.append(component_id)

    return mentioned_entities


async def query_graph(state: GraphState) -> GraphState:
    """Query the Knowledge Graph for related entities.

    Node 2: Query Graph

    For DIAGNOSTIC and LOOKUP intents, this node extracts entity mentions
    from the query and retrieves 1-hop neighbors from the Knowledge Graph.
    This provides relationship context that complements vector search.
    """
    graph_context: List[str] = []

    # Only query graph for relevant intents
    if state["intent"] not in (QueryIntent.DIAGNOSTIC, QueryIntent.LOOKUP, QueryIntent.SEARCH):
        state["graph_context"] = graph_context
        state["timings"]["query_graph"] = _elapsed_ms(state["start_time"])
        return state

    try:
        graph_store = get_graph_store()

        # Extract entity mentions using the helper function
        mentioned_entities = extract_entities(state["query"])

        # Query the graph for each mentioned entity
        for entity_id in mentioned_entities[:5]:  # Limit to avoid over-fetching
            # Get entity info
            entity = await graph_store.get_entity(entity_id)
            if entity:
                graph_context.append(f"Entity: {entity.name} ({entity.entity_type})")

            # Get 1-hop neighbors
            neighbors = await graph_store.get_neighbors(entity_id, direction="both")
            if neighbors:
                # Get relationship details
                outgoing = await graph_store.get_related(entity_id)
                for rel in outgoing[:3]:  # Limit relationships
                    target_entity = await graph_store.get_entity(rel.object)
                    target_name = target_entity.name if target_entity else rel.object
                    graph_context.append(f"  -> {rel.predicate} -> {target_name}")

                incoming = await graph_store.get_subjects(entity_id)
                for rel in incoming[:3]:
                    source_entity = await graph_store.get_entity(rel.subject)
                    source_name = source_entity.name if source_entity else rel.subject
                    graph_context.append(f"  <- {rel.predicate} <- {source_name}")

        # Search for entities matching query keywords
        if not mentioned_entities:
            # Try searching by keywords in the query
            search_results = await graph_store.search_entities(state["query"])
            for entity in search_results[:3]:
                graph_context.append(f"Related: {entity.name} ({entity.entity_type})")

    except Exception as e:
        # Graph query failures should not break the pipeline
        print(f"Graph query error (non-fatal): {e}", flush=True)

    state["graph_context"] = graph_context
    state["timings"]["query_graph"] = _elapsed_ms(state["start_time"])
    return state


async def inject_scratchpad(state: GraphState) -> GraphState:
    """Inject context from the session-scoped Scratchpad Memory.

    Node 3: Inject Scratchpad

    This node retrieves recent observations and inferences from the scratchpad
    memory and adds them to the state for use in retrieval and reasoning.
    The scratchpad provides session-scoped working memory that complements
    the persistent vector and graph stores.
    """
    from app.adapters.scratchpad_store import get_scratchpad_store

    scratchpad_context: List[str] = []
    token_count = 0

    try:
        scratchpad = get_scratchpad_store()
        context_lines, token_count = scratchpad.get_context_for_injection(
            token_budget=settings.scratchpad_inject_budget,
            query_context=state["query"],
        )
        scratchpad_context = context_lines

    except Exception as e:
        # Scratchpad failures should not break the pipeline
        print(f"Scratchpad injection error (non-fatal): {e}", flush=True)

    state["scratchpad_context"] = scratchpad_context
    state["scratchpad_token_count"] = token_count
    state["timings"]["inject_scratchpad"] = _elapsed_ms(state["start_time"])
    return state


async def retrieve(state: GraphState) -> GraphState:
    """Retrieve candidate schematics from memory backend.

    Node 4: Retrieve
    """
    memory = get_memory_store()

    try:
        # For lookup, try to extract specific ID
        if state["intent"] == QueryIntent.LOOKUP:
            # Try to find ID pattern in query
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

    Node 5: Compress Context

    Combines vector search results with Scratchpad and Knowledge Graph context.
    """
    context_parts = []

    # Include scratchpad context first (session working memory)
    scratchpad_context = state.get("scratchpad_context", [])
    if scratchpad_context:
        context_parts.append("=== Session Memory (Scratchpad) ===")
        context_parts.extend(scratchpad_context)
        context_parts.append("")

    # Include graph context if available
    graph_context = state.get("graph_context", [])
    if graph_context:
        context_parts.append("=== Knowledge Graph Context ===")
        context_parts.extend(graph_context)
        context_parts.append("")

    if not state["candidates"]:
        if context_parts:
            context_parts.append("=== Search Results ===")
            context_parts.append("No matching schematics found in vector search.")
            state["compressed_context"] = "\n".join(context_parts)
        else:
            state["compressed_context"] = "No matching schematics found."
        state["timings"]["compress_context"] = _elapsed_ms(state["start_time"])
        return state

    # Build compressed context based on intent
    context_parts.append("=== Search Results ===")

    if state["intent"] == QueryIntent.LOOKUP:
        # Full details for lookup
        for result in state["candidates"][:3]:
            s = result.schematic
            context = f"""
[{s.id}] {s.model} - {s.name}
Component: {s.component} ({s.version})
Category: {s.category} | Status: {s.status.value}
Summary: {s.summary}
Specs: {json.dumps(s.specifications) if s.specifications else 'N/A'}
"""
            context_parts.append(context.strip())

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

        context_parts.append(f"""
Found {len(state['candidates'])} matching schematics.
Categories: {json.dumps(categories)}
Models: {json.dumps(models)}
Statuses: {json.dumps(statuses)}
""")

    else:
        # Concise summaries for search/diagnostic
        for result in state["candidates"][:5]:
            s = result.schematic
            context = f"[{s.id}] {s.model}/{s.name}: {s.component} ({s.category}) - {s.summary[:100]}..."
            context_parts.append(context)

    state["compressed_context"] = "\n".join(context_parts)
    state["timings"]["compress_context"] = _elapsed_ms(state["start_time"])
    return state


async def reason(state: GraphState) -> GraphState:
    """Call LLM for reasoning (stub if no LLM configured).

    Node 6: Reason
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

    Node 7: Respond
    """
    total_time = _elapsed_ms(state["start_time"])

    # Preserve reasoning from previous node before overwriting response dict
    reasoning = state["response"].get("reasoning", "")

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
        "graph_context": state.get("graph_context", []),
        "scratchpad_context": state.get("scratchpad_context", []),
        "context_summary": state["compressed_context"],
        "total_matches": len(state["candidates"]),
        "query_time_ms": total_time,
        "reasoning": reasoning,
        "error": state["error"],
        "timings": state["timings"],
    }

    return state


def _elapsed_ms(start_time: str) -> float:
    """Calculate elapsed milliseconds from ISO timestamp."""
    start = datetime.fromisoformat(start_time)
    return (datetime.now(timezone.utc) - start).total_seconds() * 1000


class SchematicaGraph:
    """LangGraph orchestration for schematic queries."""

    def __init__(self):
        """Initialize the graph."""
        self._graph = None

    async def _build_graph(self):
        """Build the LangGraph workflow.

        The workflow follows this 7-node pipeline:
        parse_intent -> query_graph -> inject_scratchpad -> retrieve -> compress_context -> reason -> respond

        The query_graph node enriches context with Knowledge Graph relationships.
        The inject_scratchpad node adds session-scoped working memory.
        """
        try:
            from langgraph.graph import StateGraph, END

            workflow = StateGraph(GraphState)

            # Add nodes (7-node pipeline)
            workflow.add_node("parse_intent", parse_intent)
            workflow.add_node("query_graph", query_graph)
            workflow.add_node("inject_scratchpad", inject_scratchpad)
            workflow.add_node("retrieve", retrieve)
            workflow.add_node("compress_context", compress_context)
            workflow.add_node("reason", reason)
            workflow.add_node("respond", respond)

            # Define edges
            workflow.set_entry_point("parse_intent")
            workflow.add_edge("parse_intent", "query_graph")
            workflow.add_edge("query_graph", "inject_scratchpad")
            workflow.add_edge("inject_scratchpad", "retrieve")
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
            "graph_context": [],
            "scratchpad_context": [],
            "scratchpad_token_count": 0,
            "candidates": [],
            "compressed_context": "",
            "response": {},
            "error": None,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "timings": {},
        }

        if self._graph:
            # Run through LangGraph
            result = await self._graph.ainvoke(initial_state)
            return result["response"]
        else:
            # Fallback: run nodes sequentially (7-node pipeline)
            state = parse_intent(initial_state)
            state = await query_graph(state)
            state = await inject_scratchpad(state)
            state = await retrieve(state)
            state = compress_context(state)
            state = await reason(state)
            state = respond(state)
            return state["response"]


# Singleton instance with thread-safe initialization
_graph: Optional[SchematicaGraph] = None
_graph_lock = threading.Lock()


async def run_query(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    top_k: int = 5,
) -> Dict[str, Any]:
    """Run a query through the LangGraph flow.

    Thread-safe singleton pattern using double-checked locking.

    Args:
        query: Natural language query
        filters: Optional filters (category, model, status)
        top_k: Number of results to return

    Returns:
        QueryResponse as dictionary
    """
    global _graph
    if _graph is None:
        with _graph_lock:
            if _graph is None:
                _graph = SchematicaGraph()

    return await _graph.run(query, filters, top_k)

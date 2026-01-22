"""
WARNERCO Robotics Schematica - MCP Server Implementation
=========================================================

This module demonstrates a comprehensive implementation of ALL Model Context Protocol
(MCP) primitives using the FastMCP Python SDK. It serves as both a production-ready
MCP server and a teaching example for MCP development.

MCP Primitives Implemented:
---------------------------
1. TOOLS (@mcp.tool) - Executable functions the LLM can call
2. RESOURCES (@mcp.resource) - Data sources the LLM can read (static and templated)
3. PROMPTS (@mcp.prompt) - Reusable prompt templates for common tasks
4. ELICITATIONS (ctx.elicit) - Interactive user input during tool execution

Key Concepts:
-------------
- Tools are for ACTIONS (search, index, compare)
- Resources are for DATA (read-only content)
- Prompts are for TEMPLATES (reusable instructions)
- Elicitations are for INTERACTION (multi-turn dialogs)

FastMCP automatically generates JSON schemas from Python type hints and docstrings,
making tools self-documenting and type-safe.

Usage:
------
    # As MCP stdio server (for Claude Desktop):
    uv run warnerco-mcp

    # As HTTP server (for remote clients):
    uvicorn app.main:app --reload

Author: WARNERCO Robotics Engineering
Version: 2.0.0
"""

from typing import Any, Dict, List, Literal, Optional
from datetime import datetime

from pydantic import BaseModel, Field
from fastmcp import FastMCP, Context

from app.adapters import get_memory_store
from app.langgraph import run_query


# =============================================================================
# MCP SERVER CONFIGURATION
# =============================================================================
# FastMCP creates a server instance that handles all MCP protocol communication.
# The server name appears in client UIs and helps identify capabilities.

mcp = FastMCP(
    "warnerco-schematica",
    # Server metadata for MCP capabilities discovery
)

# Server version - used in self-documenting resources
SERVER_VERSION = "2.0.0"


# =============================================================================
# PYDANTIC MODELS FOR STRUCTURED OUTPUT
# =============================================================================
# These models define the structure of tool responses. FastMCP automatically
# converts them to JSON schemas for the MCP protocol.


class SchematicSummary(BaseModel):
    """Summary view of a schematic for list operations.

    This model provides a lightweight representation suitable for
    listing and browsing operations.
    """

    id: str = Field(description="Unique schematic identifier (e.g., WRN-00001)")
    model: str = Field(description="Robot model identifier (e.g., WC-100)")
    name: str = Field(description="Human-readable robot name")
    component: str = Field(description="Component being documented")
    category: str = Field(description="Classification category")
    status: str = Field(description="Current status (active, deprecated, draft)")
    version: str = Field(description="Component version string")


class SchematicListResult(BaseModel):
    """Result of a list schematics operation.

    Contains both the schematics and metadata about the query.
    """

    count: int = Field(description="Number of schematics returned")
    schematics: List[SchematicSummary] = Field(description="List of schematic summaries")


class SchematicDetail(BaseModel):
    """Full detail view of a schematic.

    Includes all fields for complete schematic information.
    """

    id: str = Field(description="Unique schematic identifier")
    model: str = Field(description="Robot model identifier")
    name: str = Field(description="Human-readable robot name")
    component: str = Field(description="Component being documented")
    version: str = Field(description="Component version string")
    category: str = Field(description="Classification category")
    status: str = Field(description="Current status")
    summary: str = Field(description="Technical summary of the component")
    url: str = Field(description="URL to schematic document")
    tags: List[str] = Field(description="Searchable tags")
    specifications: Optional[Dict[str, Any]] = Field(
        default=None, description="Technical specifications"
    )
    last_verified: str = Field(description="ISO date of last verification")


class SearchResultItem(BaseModel):
    """Individual search result with relevance information."""

    id: str = Field(description="Schematic ID")
    model: str = Field(description="Robot model")
    name: str = Field(description="Robot name")
    component: str = Field(description="Component name")
    score: float = Field(description="Relevance score (0-1)")
    summary: str = Field(description="Component summary")


class SemanticSearchResult(BaseModel):
    """Result of a semantic search operation."""

    query: str = Field(description="Original search query")
    intent: str = Field(description="Detected query intent")
    results: List[SearchResultItem] = Field(description="Matching schematics")
    total: int = Field(description="Total matches found")
    reasoning: str = Field(description="Explanation of search strategy")
    query_time_ms: int = Field(description="Query execution time in milliseconds")


class MemoryStatsResult(BaseModel):
    """Statistics about the memory backend."""

    backend: str = Field(description="Active memory backend name")
    total_schematics: int = Field(description="Total number of schematics")
    indexed_count: int = Field(description="Number of indexed schematics")
    chunk_count: int = Field(description="Total embedding chunks")
    categories: Dict[str, int] = Field(description="Count by category")
    status_counts: Dict[str, int] = Field(description="Count by status")
    last_update: Optional[str] = Field(description="ISO timestamp of last update")


class ComparisonResult(BaseModel):
    """Result of comparing two schematics."""

    schematic_1: SchematicDetail = Field(description="First schematic")
    schematic_2: SchematicDetail = Field(description="Second schematic")
    similarities: List[str] = Field(description="Common characteristics")
    differences: List[str] = Field(description="Key differences")
    recommendation: str = Field(description="Use-case recommendation")


class IndexResult(BaseModel):
    """Result of indexing a schematic."""

    schematic_id: str = Field(description="ID of indexed schematic")
    success: bool = Field(description="Whether indexing succeeded")
    message: str = Field(description="Status message")
    indexed_at: str = Field(description="ISO timestamp of indexing")


class GuidedSearchResult(BaseModel):
    """Result of a guided search session."""

    category: Optional[str] = Field(description="Selected category")
    model: Optional[str] = Field(description="Selected model")
    keywords: str = Field(description="Search keywords")
    results: List[SearchResultItem] = Field(description="Search results")
    session_summary: str = Field(description="Summary of the guided session")


class FeedbackResult(BaseModel):
    """Result of collecting feedback."""

    schematic_id: str = Field(description="Schematic being reviewed")
    rating: int = Field(description="User rating (1-5)")
    feedback_text: str = Field(description="User's feedback comments")
    submitted_at: str = Field(description="ISO timestamp of submission")
    acknowledged: bool = Field(description="Whether feedback was recorded")


# =============================================================================
# CRUD OPERATION RESULT MODELS
# =============================================================================
# These models define the structure of create, update, and delete responses.


class CreateSchematicResult(BaseModel):
    """Result of creating a new schematic."""

    success: bool = Field(description="Whether the operation succeeded")
    schematic_id: str = Field(description="ID of the created schematic")
    message: str = Field(description="Human-readable status message")
    schematic: Optional[SchematicDetail] = Field(
        default=None, description="The created schematic details"
    )


class UpdateSchematicResult(BaseModel):
    """Result of updating a schematic."""

    success: bool = Field(description="Whether the operation succeeded")
    schematic_id: str = Field(description="ID of the updated schematic")
    message: str = Field(description="Human-readable status message")
    updated_fields: List[str] = Field(
        default_factory=list, description="List of fields that were updated"
    )
    schematic: Optional[SchematicDetail] = Field(
        default=None, description="The updated schematic details"
    )


class DeleteSchematicResult(BaseModel):
    """Result of deleting a schematic."""

    success: bool = Field(description="Whether the operation succeeded")
    schematic_id: str = Field(description="ID of the deleted schematic")
    message: str = Field(description="Human-readable status message")
    deleted_component: Optional[str] = Field(
        default=None, description="Name of the deleted component"
    )


# =============================================================================
# ELICITATION SCHEMAS
# =============================================================================
# These Pydantic models define the structure of user input for elicitations.
# FastMCP uses these to generate input forms in MCP clients.


class CategorySelection(BaseModel):
    """Schema for category selection in guided search."""

    category: Optional[str] = Field(
        default=None,
        description="Category to filter by (leave empty for all)",
        json_schema_extra={
            "enum": ["sensors", "power", "control", "mobility", "communication", ""]
        },
    )


class ModelSelection(BaseModel):
    """Schema for model selection in guided search."""

    model: Optional[str] = Field(
        default=None,
        description="Robot model to filter by (leave empty for all)",
    )


class KeywordInput(BaseModel):
    """Schema for keyword input in guided search."""

    keywords: str = Field(
        description="Search keywords or natural language query",
        min_length=1,
        max_length=500,
    )


class FeedbackInput(BaseModel):
    """Schema for collecting user feedback on a schematic."""

    rating: int = Field(
        description="Rating from 1 (poor) to 5 (excellent)",
        ge=1,
        le=5,
    )
    comments: str = Field(
        description="Additional feedback or suggestions",
        max_length=1000,
    )
    would_recommend: bool = Field(
        description="Would you recommend this schematic to others?",
    )


# =============================================================================
# TOOLS - Executable Functions
# =============================================================================
# Tools are the primary way LLMs interact with external systems. Each tool:
# - Has a clear, descriptive name (verb_noun format recommended)
# - Includes comprehensive docstring (becomes the tool description)
# - Uses type hints for all parameters (generates JSON schema)
# - Returns structured data (Pydantic models or dicts)


@mcp.tool()
async def warn_list_robots(
    category: Optional[str] = None,
    model: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
) -> SchematicListResult:
    """List robot schematics with optional filtering.

    Retrieves a list of robot schematics from the WARNERCO Schematica database.
    Results can be filtered by category, model, or status. Use this tool to
    discover available schematics before drilling down into specific ones.

    Args:
        category: Filter by component category. Valid values include:
            - "sensors" - Sensing and detection components
            - "power" - Power supply and energy management
            - "control" - Control systems and processors
            - "mobility" - Movement and locomotion systems
            - "communication" - Network and data transmission
        model: Filter by robot model identifier (e.g., "WC-100", "WC-200").
            Models follow the WC-XXX naming convention.
        status: Filter by schematic status:
            - "active" - Current, production-ready schematics
            - "deprecated" - Superseded, not recommended for new designs
            - "draft" - Work in progress, not verified
        limit: Maximum number of results to return. Default is 20, max is 100.

    Returns:
        SchematicListResult containing:
            - count: Number of schematics matching the filters
            - schematics: List of SchematicSummary objects with basic info

    Example:
        >>> # List all active sensor schematics
        >>> await warn_list_robots(category="sensors", status="active")
        >>> # List schematics for WC-100 model
        >>> await warn_list_robots(model="WC-100", limit=10)
    """
    memory = get_memory_store()

    # Build filters dict only with provided values
    filters = {}
    if category:
        filters["category"] = category
    if model:
        filters["model"] = model
    if status:
        filters["status"] = status

    schematics = await memory.list_schematics(
        filters=filters if filters else None,
        limit=min(limit, 100),  # Enforce max limit
    )

    return SchematicListResult(
        count=len(schematics),
        schematics=[
            SchematicSummary(
                id=s.id,
                model=s.model,
                name=s.name,
                component=s.component,
                category=s.category,
                status=s.status.value,
                version=s.version,
            )
            for s in schematics
        ],
    )


@mcp.tool()
async def warn_get_robot(schematic_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific robot schematic.

    Retrieves the complete details of a single schematic by its unique ID.
    Use this after discovering a schematic via warn_list_robots or
    warn_semantic_search to get full specifications and metadata.

    Args:
        schematic_id: The unique schematic identifier in WRN-XXXXX format
            (e.g., "WRN-00001", "WRN-00015"). Case-sensitive.

    Returns:
        Dictionary containing full schematic details:
            - id: Schematic identifier
            - model: Robot model (WC-XXX)
            - name: Human-readable robot name
            - component: Component being documented
            - version: Component version string
            - category: Classification category
            - status: Current status (active/deprecated/draft)
            - summary: Technical summary
            - url: Link to full schematic document
            - tags: List of searchable tags
            - specifications: Technical specs (varies by component)
            - last_verified: Date of last verification

        If schematic not found, returns {"error": "Schematic {id} not found"}

    Example:
        >>> # Get details for a specific schematic
        >>> result = await warn_get_robot("WRN-00001")
        >>> print(result["component"])  # "Thermal Sensor Array"
        >>> print(result["specifications"]["range"])  # "-40C to 150C"
    """
    memory = get_memory_store()
    schematic = await memory.get_schematic(schematic_id)

    if not schematic:
        return {"error": f"Schematic {schematic_id} not found"}

    return {
        "id": schematic.id,
        "model": schematic.model,
        "name": schematic.name,
        "component": schematic.component,
        "version": schematic.version,
        "category": schematic.category,
        "status": schematic.status.value,
        "summary": schematic.summary,
        "url": schematic.url,
        "tags": schematic.tags,
        "specifications": schematic.specifications,
        "last_verified": schematic.last_verified,
    }


@mcp.tool()
async def warn_semantic_search(
    query: str,
    category: Optional[str] = None,
    model: Optional[str] = None,
    top_k: int = 5,
) -> SemanticSearchResult:
    """Search robot schematics using natural language queries.

    Performs semantic search using vector embeddings to find schematics
    that match the meaning of your query, not just keywords. The search
    uses a 5-node LangGraph RAG pipeline:

    1. parse_intent - Understand query intent
    2. retrieve - Semantic vector search
    3. compress_context - Filter and rank results
    4. reason - Generate explanations
    5. respond - Format final response

    Args:
        query: Natural language search query describing what you need.
            Be specific and include technical terms when relevant.
            Examples:
            - "thermal sensors for extreme temperatures"
            - "power management for heavy-duty industrial robots"
            - "control systems with low latency requirements"
        category: Optional filter to narrow by category before semantic search.
            Improves accuracy when you know the component type.
        model: Optional filter to search within a specific robot model line.
            Use when looking for model-specific components.
        top_k: Number of results to return (1-50). Default is 5.
            Higher values return more results but may include less relevant matches.

    Returns:
        SemanticSearchResult containing:
            - query: Original search query
            - intent: Detected intent (search, lookup, compare, etc.)
            - results: List of matching schematics with relevance scores
            - total: Total number of matches
            - reasoning: Explanation of how results were selected
            - query_time_ms: Execution time for performance monitoring

    Example:
        >>> # Find sensors for harsh environments
        >>> result = await warn_semantic_search(
        ...     query="sensors that work in extreme cold",
        ...     category="sensors",
        ...     top_k=3
        ... )
        >>> for item in result.results:
        ...     print(f"{item.id}: {item.score:.2f} - {item.component}")
    """
    filters = {}
    if category:
        filters["category"] = category
    if model:
        filters["model"] = model

    # Run through LangGraph RAG pipeline
    result = await run_query(
        query=query,
        filters=filters if filters else None,
        top_k=top_k,
    )

    # Transform results to structured format
    search_results = []
    for r in result.get("results", []):
        search_results.append(
            SearchResultItem(
                id=r.get("id", ""),
                model=r.get("model", ""),
                name=r.get("name", ""),
                component=r.get("component", ""),
                score=r.get("score", 0.0),
                summary=r.get("summary", ""),
            )
        )

    return SemanticSearchResult(
        query=query,
        intent=result.get("intent", "search"),
        results=search_results,
        total=result.get("total_matches", 0),
        reasoning=result.get("reasoning", ""),
        query_time_ms=result.get("query_time_ms", 0),
    )


@mcp.tool()
async def warn_memory_stats() -> MemoryStatsResult:
    """Get statistics about the schematic memory system.

    Returns comprehensive statistics about the current memory backend,
    including document counts, index status, and categorical breakdowns.
    Useful for monitoring system health and understanding data distribution.

    The memory system supports three backends:
    - json: Fast keyword search, no embedding required
    - chroma: Local vector database with semantic search
    - azure_search: Enterprise Azure AI Search integration

    Returns:
        MemoryStatsResult containing:
            - backend: Name of active memory backend (json/chroma/azure_search)
            - total_schematics: Total documents in the system
            - indexed_count: Documents indexed for semantic search
            - chunk_count: Total text chunks (for chunked embedding)
            - categories: Dictionary mapping category names to counts
            - status_counts: Dictionary mapping status values to counts
            - last_update: ISO timestamp of last data modification

    Example:
        >>> stats = await warn_memory_stats()
        >>> print(f"Backend: {stats.backend}")
        >>> print(f"Total: {stats.total_schematics}, Indexed: {stats.indexed_count}")
        >>> print(f"Categories: {stats.categories}")
    """
    memory = get_memory_store()
    stats = await memory.get_memory_stats()

    return MemoryStatsResult(
        backend=stats.backend,
        total_schematics=stats.total_schematics,
        indexed_count=stats.indexed_count,
        chunk_count=stats.chunk_count,
        categories=stats.categories,
        status_counts=stats.status_counts,
        last_update=stats.last_update,
    )


@mcp.tool()
async def warn_index_schematic(schematic_id: str) -> IndexResult:
    """Index a single schematic for semantic search.

    Generates embeddings for the specified schematic and adds it to the
    vector index. This enables the schematic to be found via semantic
    search queries. Use this after adding new schematics or when a
    schematic is not appearing in search results.

    The indexing process:
    1. Retrieves the schematic from storage
    2. Generates text representation for embedding
    3. Creates vector embeddings using the configured model
    4. Stores embeddings in the active vector backend

    Args:
        schematic_id: The unique schematic identifier to index (e.g., "WRN-00001").
            The schematic must exist in the database.

    Returns:
        IndexResult containing:
            - schematic_id: ID of the schematic that was indexed
            - success: Boolean indicating if indexing completed
            - message: Human-readable status message
            - indexed_at: ISO timestamp of indexing operation

    Raises:
        Returns error result if schematic not found or indexing fails.

    Example:
        >>> # Index a newly added schematic
        >>> result = await warn_index_schematic("WRN-00025")
        >>> if result.success:
        ...     print(f"Indexed at {result.indexed_at}")
        ... else:
        ...     print(f"Failed: {result.message}")
    """
    memory = get_memory_store()

    # Verify schematic exists
    schematic = await memory.get_schematic(schematic_id)
    if not schematic:
        return IndexResult(
            schematic_id=schematic_id,
            success=False,
            message=f"Schematic {schematic_id} not found",
            indexed_at=datetime.utcnow().isoformat(),
        )

    try:
        # Perform indexing
        success = await memory.embed_and_index(schematic_id)

        if success:
            return IndexResult(
                schematic_id=schematic_id,
                success=True,
                message=f"Successfully indexed schematic {schematic_id}",
                indexed_at=datetime.utcnow().isoformat(),
            )
        else:
            return IndexResult(
                schematic_id=schematic_id,
                success=False,
                message="Indexing returned false - check backend configuration",
                indexed_at=datetime.utcnow().isoformat(),
            )
    except Exception as e:
        return IndexResult(
            schematic_id=schematic_id,
            success=False,
            message=f"Indexing error: {str(e)}",
            indexed_at=datetime.utcnow().isoformat(),
        )


@mcp.tool()
async def warn_compare_schematics(id1: str, id2: str) -> Dict[str, Any]:
    """Compare two schematics side-by-side.

    Retrieves two schematics and generates a structured comparison showing
    their similarities, differences, and recommendations for use cases.
    Useful for deciding between alternative components or understanding
    version differences.

    The comparison analyzes:
    - Model compatibility
    - Component specifications
    - Status and version differences
    - Use case recommendations

    Args:
        id1: First schematic ID to compare (e.g., "WRN-00001")
        id2: Second schematic ID to compare (e.g., "WRN-00005")

    Returns:
        Dictionary containing:
            - schematic_1: Full details of first schematic
            - schematic_2: Full details of second schematic
            - similarities: List of common characteristics
            - differences: List of key differences
            - recommendation: Suggested use case guidance

        Returns error dict if either schematic is not found.

    Example:
        >>> # Compare two sensor schematics
        >>> result = await warn_compare_schematics("WRN-00001", "WRN-00005")
        >>> print("Similarities:", result["similarities"])
        >>> print("Differences:", result["differences"])
        >>> print("Recommendation:", result["recommendation"])
    """
    memory = get_memory_store()

    # Fetch both schematics
    schematic1 = await memory.get_schematic(id1)
    schematic2 = await memory.get_schematic(id2)

    if not schematic1:
        return {"error": f"Schematic {id1} not found"}
    if not schematic2:
        return {"error": f"Schematic {id2} not found"}

    # Analyze similarities
    similarities = []
    if schematic1.category == schematic2.category:
        similarities.append(f"Same category: {schematic1.category}")
    if schematic1.model == schematic2.model:
        similarities.append(f"Same robot model: {schematic1.model}")
    if schematic1.status == schematic2.status:
        similarities.append(f"Same status: {schematic1.status.value}")

    # Check for common tags
    common_tags = set(schematic1.tags) & set(schematic2.tags)
    if common_tags:
        similarities.append(f"Common tags: {', '.join(common_tags)}")

    # Analyze differences
    differences = []
    if schematic1.category != schematic2.category:
        differences.append(
            f"Category: {schematic1.category} vs {schematic2.category}"
        )
    if schematic1.model != schematic2.model:
        differences.append(f"Model: {schematic1.model} vs {schematic2.model}")
    if schematic1.version != schematic2.version:
        differences.append(f"Version: {schematic1.version} vs {schematic2.version}")
    if schematic1.status != schematic2.status:
        differences.append(
            f"Status: {schematic1.status.value} vs {schematic2.status.value}"
        )

    # Generate recommendation
    recommendation = _generate_comparison_recommendation(schematic1, schematic2)

    return {
        "schematic_1": {
            "id": schematic1.id,
            "model": schematic1.model,
            "name": schematic1.name,
            "component": schematic1.component,
            "version": schematic1.version,
            "category": schematic1.category,
            "status": schematic1.status.value,
            "summary": schematic1.summary,
            "tags": schematic1.tags,
            "specifications": schematic1.specifications,
        },
        "schematic_2": {
            "id": schematic2.id,
            "model": schematic2.model,
            "name": schematic2.name,
            "component": schematic2.component,
            "version": schematic2.version,
            "category": schematic2.category,
            "status": schematic2.status.value,
            "summary": schematic2.summary,
            "tags": schematic2.tags,
            "specifications": schematic2.specifications,
        },
        "similarities": similarities if similarities else ["No significant similarities found"],
        "differences": differences if differences else ["No significant differences found"],
        "recommendation": recommendation,
    }


def _generate_comparison_recommendation(schematic1, schematic2) -> str:
    """Generate a use-case recommendation based on schematic comparison."""
    recommendations = []

    # Status-based recommendations
    if schematic1.status.value == "active" and schematic2.status.value == "deprecated":
        recommendations.append(
            f"Prefer {schematic1.id} ({schematic1.component}) - it is actively maintained while "
            f"{schematic2.id} is deprecated."
        )
    elif schematic2.status.value == "active" and schematic1.status.value == "deprecated":
        recommendations.append(
            f"Prefer {schematic2.id} ({schematic2.component}) - it is actively maintained while "
            f"{schematic1.id} is deprecated."
        )

    # Model compatibility
    if schematic1.model != schematic2.model:
        recommendations.append(
            f"Note: These schematics are for different robot models "
            f"({schematic1.model} vs {schematic2.model}). Ensure compatibility with your target platform."
        )

    # Category alignment
    if schematic1.category == schematic2.category:
        recommendations.append(
            f"Both are {schematic1.category} components - compare specifications carefully "
            "to choose the best fit for your requirements."
        )

    if not recommendations:
        recommendations.append(
            "Both schematics appear viable. Review detailed specifications and "
            "your specific requirements to make the best choice."
        )

    return " ".join(recommendations)


# =============================================================================
# CRUD TOOLS - Create, Update, Delete Operations
# =============================================================================
# These tools provide write operations for managing schematics in the database.
# They complement the read-only tools (list, get, search) with full CRUD support.

# Valid categories and statuses for validation
VALID_CATEGORIES = {"sensors", "power", "control", "mobility", "communication"}
VALID_STATUSES = {"draft", "active", "deprecated"}


async def _generate_schematic_id(memory) -> str:
    """Generate the next schematic ID in WRN-XXXXX format."""
    # Get all existing schematics to find the highest ID
    schematics = await memory.list_schematics(limit=10000)
    max_num = 0
    for s in schematics:
        if s.id.startswith("WRN-"):
            try:
                num = int(s.id.replace("WRN-", ""))
                max_num = max(max_num, num)
            except ValueError:
                continue
    return f"WRN-{max_num + 1:05d}"


@mcp.tool()
async def warn_create_schematic(
    model: str,
    name: str,
    component: str,
    category: str,
    summary: str,
    version: str = "1.0.0",
    status: str = "draft",
    tags: Optional[List[str]] = None,
    specifications: Optional[Dict[str, Any]] = None,
    url: Optional[str] = None,
) -> CreateSchematicResult:
    """Create a new robot schematic in the database.

    Creates a new schematic entry with the provided details. The schematic ID
    is automatically generated in the WRN-XXXXX format (auto-incrementing from
    the highest existing ID).

    Args:
        model: Robot model identifier (e.g., "WC-100", "WC-200", "WC-300").
            Should follow the WC-XXX naming convention.
        name: Human-readable robot name (e.g., "Atlas Prime", "Titan Heavy").
            This is the friendly name for the robot model.
        component: Name of the component being documented (e.g., "Thermal Sensor Array",
            "Power Distribution Unit"). Should be descriptive and unique within the model.
        category: Classification category. Must be one of:
            - "sensors" - Sensing and detection components
            - "power" - Power supply and energy management
            - "control" - Control systems and processors
            - "mobility" - Movement and locomotion systems
            - "communication" - Network and data transmission
        summary: Technical summary describing the component's function, capabilities,
            and key characteristics. Should be comprehensive but concise (1-3 paragraphs).
        version: Component version string (default: "1.0.0"). Use semantic versioning
            format (major.minor.patch) when possible.
        status: Current status of the schematic (default: "draft"). Must be one of:
            - "draft" - Work in progress, not verified
            - "active" - Current, production-ready
            - "deprecated" - Superseded, not recommended for new designs
        tags: Optional list of searchable tags for categorization and discovery.
            Tags should be lowercase, hyphenated if multi-word.
        specifications: Optional dictionary of technical specifications.
            Keys are specification names, values are the spec values.
            Example: {"range": "-40C to 150C", "accuracy": "+/- 0.5C"}
        url: Optional URL to the full schematic document. Defaults to a
            placeholder URL based on the schematic ID.

    Returns:
        CreateSchematicResult containing:
            - success: True if schematic was created successfully
            - schematic_id: The generated WRN-XXXXX identifier
            - message: Human-readable status message
            - schematic: Full details of the created schematic

    Example:
        >>> result = await warn_create_schematic(
        ...     model="WC-400",
        ...     name="Apex Elite",
        ...     component="Advanced GPS Module",
        ...     category="sensors",
        ...     summary="High-precision GPS module with RTK support...",
        ...     version="1.0.0",
        ...     status="draft",
        ...     tags=["gps", "navigation", "rtk"],
        ...     specifications={"accuracy": "1cm RTK", "channels": "184"}
        ... )
        >>> print(f"Created: {result.schematic_id}")
    """
    # Import Schematic model for creating the entity
    from app.models import Schematic, SchematicStatus

    # Validate category
    if category.lower() not in VALID_CATEGORIES:
        return CreateSchematicResult(
            success=False,
            schematic_id="",
            message=f"Invalid category '{category}'. Must be one of: {', '.join(sorted(VALID_CATEGORIES))}",
            schematic=None,
        )

    # Validate status
    if status.lower() not in VALID_STATUSES:
        return CreateSchematicResult(
            success=False,
            schematic_id="",
            message=f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
            schematic=None,
        )

    memory = get_memory_store()

    try:
        # Generate new schematic ID
        new_id = await _generate_schematic_id(memory)

        # Set default URL if not provided
        if not url:
            url = f"https://docs.warnerco.com/schematics/{new_id.lower()}"

        # Get current date for last_verified
        current_date = datetime.utcnow().strftime("%Y-%m-%d")

        # Map string status to enum
        status_enum = SchematicStatus(status.lower())

        # Create the Schematic object
        schematic = Schematic(
            id=new_id,
            model=model,
            name=name,
            component=component,
            category=category.lower(),
            summary=summary,
            version=version,
            status=status_enum,
            tags=tags or [],
            specifications=specifications,
            url=url,
            last_verified=current_date,
        )

        # Upsert to memory store
        created = await memory.upsert_schematic(schematic)

        # Build result detail
        schematic_detail = SchematicDetail(
            id=created.id,
            model=created.model,
            name=created.name,
            component=created.component,
            version=created.version,
            category=created.category,
            status=created.status.value,
            summary=created.summary,
            url=created.url,
            tags=created.tags,
            specifications=created.specifications,
            last_verified=created.last_verified,
        )

        return CreateSchematicResult(
            success=True,
            schematic_id=new_id,
            message=f"Successfully created schematic {new_id}: {component}",
            schematic=schematic_detail,
        )

    except Exception as e:
        return CreateSchematicResult(
            success=False,
            schematic_id="",
            message=f"Failed to create schematic: {str(e)}",
            schematic=None,
        )


@mcp.tool()
async def warn_update_schematic(
    schematic_id: str,
    model: Optional[str] = None,
    name: Optional[str] = None,
    component: Optional[str] = None,
    category: Optional[str] = None,
    summary: Optional[str] = None,
    version: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[List[str]] = None,
    specifications: Optional[Dict[str, Any]] = None,
    url: Optional[str] = None,
) -> UpdateSchematicResult:
    """Update an existing schematic's fields.

    Updates specified fields of an existing schematic. Only fields that are
    explicitly provided will be modified - omitted fields retain their current
    values. The last_verified date is automatically updated to the current date.

    Args:
        schematic_id: The unique schematic identifier to update (e.g., "WRN-00001").
            Required - specifies which schematic to modify.
        model: New robot model identifier (optional).
        name: New robot name (optional).
        component: New component name (optional).
        category: New category (optional). If provided, must be one of:
            sensors, power, control, mobility, communication
        summary: New technical summary (optional).
        version: New version string (optional).
        status: New status (optional). If provided, must be one of:
            draft, active, deprecated
        tags: New list of tags (optional). Replaces existing tags entirely.
        specifications: New specifications dict (optional). Replaces existing specs.
        url: New document URL (optional).

    Returns:
        UpdateSchematicResult containing:
            - success: True if update completed successfully
            - schematic_id: ID of the updated schematic
            - message: Human-readable status message
            - updated_fields: List of field names that were modified
            - schematic: Full details of the updated schematic

    Example:
        >>> # Update just the status and version
        >>> result = await warn_update_schematic(
        ...     schematic_id="WRN-00001",
        ...     status="active",
        ...     version="1.1.0"
        ... )
        >>> print(f"Updated fields: {result.updated_fields}")
        >>> # Output: Updated fields: ['status', 'version', 'last_verified']

        >>> # Update specifications
        >>> result = await warn_update_schematic(
        ...     schematic_id="WRN-00001",
        ...     specifications={"range": "-50C to 200C", "accuracy": "+/- 0.3C"}
        ... )
    """
    from app.models import Schematic, SchematicStatus

    memory = get_memory_store()

    # Verify schematic exists
    existing = await memory.get_schematic(schematic_id)
    if not existing:
        return UpdateSchematicResult(
            success=False,
            schematic_id=schematic_id,
            message=f"Schematic {schematic_id} not found",
            updated_fields=[],
            schematic=None,
        )

    # Validate category if provided
    if category is not None and category.lower() not in VALID_CATEGORIES:
        return UpdateSchematicResult(
            success=False,
            schematic_id=schematic_id,
            message=f"Invalid category '{category}'. Must be one of: {', '.join(sorted(VALID_CATEGORIES))}",
            updated_fields=[],
            schematic=None,
        )

    # Validate status if provided
    if status is not None and status.lower() not in VALID_STATUSES:
        return UpdateSchematicResult(
            success=False,
            schematic_id=schematic_id,
            message=f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
            updated_fields=[],
            schematic=None,
        )

    try:
        # Track which fields are being updated
        updated_fields: List[str] = []

        # Build updated schematic with only changed fields
        new_model = model if model is not None else existing.model
        if model is not None and model != existing.model:
            updated_fields.append("model")

        new_name = name if name is not None else existing.name
        if name is not None and name != existing.name:
            updated_fields.append("name")

        new_component = component if component is not None else existing.component
        if component is not None and component != existing.component:
            updated_fields.append("component")

        new_category = category.lower() if category is not None else existing.category
        if category is not None and category.lower() != existing.category:
            updated_fields.append("category")

        new_summary = summary if summary is not None else existing.summary
        if summary is not None and summary != existing.summary:
            updated_fields.append("summary")

        new_version = version if version is not None else existing.version
        if version is not None and version != existing.version:
            updated_fields.append("version")

        new_status = SchematicStatus(status.lower()) if status is not None else existing.status
        if status is not None and status.lower() != existing.status.value:
            updated_fields.append("status")

        new_tags = tags if tags is not None else existing.tags
        if tags is not None and tags != existing.tags:
            updated_fields.append("tags")

        new_specs = specifications if specifications is not None else existing.specifications
        if specifications is not None and specifications != existing.specifications:
            updated_fields.append("specifications")

        new_url = url if url is not None else existing.url
        if url is not None and url != existing.url:
            updated_fields.append("url")

        # Always update last_verified when making changes
        new_last_verified = datetime.utcnow().strftime("%Y-%m-%d")
        if updated_fields:  # Only if there were actual changes
            updated_fields.append("last_verified")

        # Create updated schematic
        updated_schematic = Schematic(
            id=schematic_id,
            model=new_model,
            name=new_name,
            component=new_component,
            category=new_category,
            summary=new_summary,
            version=new_version,
            status=new_status,
            tags=new_tags,
            specifications=new_specs,
            url=new_url,
            last_verified=new_last_verified,
        )

        # Upsert the updated schematic
        saved = await memory.upsert_schematic(updated_schematic)

        # Build result detail
        schematic_detail = SchematicDetail(
            id=saved.id,
            model=saved.model,
            name=saved.name,
            component=saved.component,
            version=saved.version,
            category=saved.category,
            status=saved.status.value,
            summary=saved.summary,
            url=saved.url,
            tags=saved.tags,
            specifications=saved.specifications,
            last_verified=saved.last_verified,
        )

        if updated_fields:
            return UpdateSchematicResult(
                success=True,
                schematic_id=schematic_id,
                message=f"Successfully updated schematic {schematic_id}. Modified: {', '.join(updated_fields)}",
                updated_fields=updated_fields,
                schematic=schematic_detail,
            )
        else:
            return UpdateSchematicResult(
                success=True,
                schematic_id=schematic_id,
                message=f"No changes made to schematic {schematic_id} - all provided values match existing values",
                updated_fields=[],
                schematic=schematic_detail,
            )

    except Exception as e:
        return UpdateSchematicResult(
            success=False,
            schematic_id=schematic_id,
            message=f"Failed to update schematic: {str(e)}",
            updated_fields=[],
            schematic=None,
        )


@mcp.tool()
async def warn_delete_schematic(
    schematic_id: str,
    confirm: bool = False,
) -> DeleteSchematicResult:
    """Delete a schematic from the database.

    Permanently removes a schematic from the database and any associated
    vector indexes. This action cannot be undone.

    SAFETY: This operation requires explicit confirmation. You must set
    confirm=True to actually delete the schematic. Without confirmation,
    the tool will return the schematic details but not delete it.

    Args:
        schematic_id: The unique schematic identifier to delete (e.g., "WRN-00001").
            Case-sensitive.
        confirm: Safety flag that must be set to True to proceed with deletion.
            Default is False. When False, the tool returns schematic details
            without deleting, allowing you to verify before confirming.

    Returns:
        DeleteSchematicResult containing:
            - success: True if deletion completed (or if dry-run completed)
            - schematic_id: ID of the (deleted) schematic
            - message: Human-readable status message explaining what happened
            - deleted_component: Name of the deleted component (only if deleted)

    Example:
        >>> # First, check what will be deleted (dry run)
        >>> result = await warn_delete_schematic("WRN-00025", confirm=False)
        >>> print(result.message)  # "Confirm deletion of 'Advanced GPS Module'..."

        >>> # Then confirm the deletion
        >>> result = await warn_delete_schematic("WRN-00025", confirm=True)
        >>> if result.success:
        ...     print(f"Deleted: {result.deleted_component}")
    """
    memory = get_memory_store()

    # Verify schematic exists
    schematic = await memory.get_schematic(schematic_id)
    if not schematic:
        return DeleteSchematicResult(
            success=False,
            schematic_id=schematic_id,
            message=f"Schematic {schematic_id} not found",
            deleted_component=None,
        )

    # If not confirmed, return details for verification
    if not confirm:
        return DeleteSchematicResult(
            success=False,
            schematic_id=schematic_id,
            message=(
                f"Confirm deletion of '{schematic.component}' ({schematic_id}) "
                f"from {schematic.model} ({schematic.name}). "
                f"Category: {schematic.category}, Status: {schematic.status.value}. "
                f"Set confirm=True to proceed with permanent deletion."
            ),
            deleted_component=None,
        )

    try:
        # Perform the deletion
        component_name = schematic.component
        deleted = await memory.delete_schematic(schematic_id)

        if deleted:
            return DeleteSchematicResult(
                success=True,
                schematic_id=schematic_id,
                message=f"Successfully deleted schematic {schematic_id}: {component_name}",
                deleted_component=component_name,
            )
        else:
            return DeleteSchematicResult(
                success=False,
                schematic_id=schematic_id,
                message=f"Delete operation returned false for {schematic_id}. The schematic may already be deleted.",
                deleted_component=None,
            )

    except Exception as e:
        return DeleteSchematicResult(
            success=False,
            schematic_id=schematic_id,
            message=f"Failed to delete schematic: {str(e)}",
            deleted_component=None,
        )


# =============================================================================
# TOOLS WITH ELICITATION - Interactive User Input
# =============================================================================
# Elicitations allow tools to request structured input from users during
# execution. This enables multi-turn interactions within a single tool call.
# The ctx.elicit() method presents a form to the user based on a Pydantic schema.


@mcp.tool()
async def warn_guided_search(ctx: Context) -> GuidedSearchResult:
    """Perform a guided, multi-step search for robot schematics.

    This interactive tool walks you through a structured search process:
    1. Select a category (optional)
    2. Select a robot model (optional)
    3. Enter search keywords

    Each step uses elicitation to gather your input, making it easy to
    refine your search progressively. The tool then executes a semantic
    search with your combined criteria.

    This demonstrates MCP elicitation - a way for tools to request
    structured user input during execution.

    Args:
        ctx: MCP Context object (automatically injected by FastMCP).
            Provides access to elicit(), logging, and progress reporting.

    Returns:
        GuidedSearchResult containing:
            - category: Selected category (or None if skipped)
            - model: Selected model (or None if skipped)
            - keywords: Search keywords entered
            - results: Semantic search results
            - session_summary: Summary of the guided session

    Example:
        When invoked, the tool will interactively prompt:
        1. "Select a category to filter by..."
        2. "Select a robot model to filter by..."
        3. "Enter your search keywords..."
        Then return combined results.
    """
    # Log the start of the guided search
    await ctx.info("Starting guided search session")

    # Step 1: Category selection via elicitation
    await ctx.info("Step 1/3: Category selection")
    category_result = await ctx.elicit(
        message="Select a category to filter by (or leave empty for all categories):",
        schema=CategorySelection,
    )

    # Check if user cancelled or provided input
    if category_result.action != "submit":
        return GuidedSearchResult(
            category=None,
            model=None,
            keywords="",
            results=[],
            session_summary="Search cancelled by user at category selection.",
        )

    selected_category = category_result.data.category if category_result.data.category else None

    # Step 2: Model selection via elicitation
    await ctx.info("Step 2/3: Model selection")
    model_result = await ctx.elicit(
        message="Select a robot model to filter by (or leave empty for all models):",
        schema=ModelSelection,
    )

    if model_result.action != "submit":
        return GuidedSearchResult(
            category=selected_category,
            model=None,
            keywords="",
            results=[],
            session_summary="Search cancelled by user at model selection.",
        )

    selected_model = model_result.data.model if model_result.data.model else None

    # Step 3: Keyword input via elicitation
    await ctx.info("Step 3/3: Keyword input")
    keyword_result = await ctx.elicit(
        message="Enter your search keywords or natural language query:",
        schema=KeywordInput,
    )

    if keyword_result.action != "submit":
        return GuidedSearchResult(
            category=selected_category,
            model=selected_model,
            keywords="",
            results=[],
            session_summary="Search cancelled by user at keyword input.",
        )

    keywords = keyword_result.data.keywords

    # Build filters and execute search
    await ctx.info(f"Executing search: '{keywords}' with filters")
    filters = {}
    if selected_category:
        filters["category"] = selected_category
    if selected_model:
        filters["model"] = selected_model

    # Run through LangGraph RAG pipeline
    result = await run_query(
        query=keywords,
        filters=filters if filters else None,
        top_k=5,
    )

    # Transform results
    search_results = []
    for r in result.get("results", []):
        search_results.append(
            SearchResultItem(
                id=r.get("id", ""),
                model=r.get("model", ""),
                name=r.get("name", ""),
                component=r.get("component", ""),
                score=r.get("score", 0.0),
                summary=r.get("summary", ""),
            )
        )

    # Build session summary
    filter_parts = []
    if selected_category:
        filter_parts.append(f"category={selected_category}")
    if selected_model:
        filter_parts.append(f"model={selected_model}")
    filter_str = ", ".join(filter_parts) if filter_parts else "none"

    session_summary = (
        f"Guided search completed. Query: '{keywords}', "
        f"Filters: {filter_str}, "
        f"Found {len(search_results)} results."
    )

    await ctx.info(session_summary)

    return GuidedSearchResult(
        category=selected_category,
        model=selected_model,
        keywords=keywords,
        results=search_results,
        session_summary=session_summary,
    )


@mcp.tool()
async def warn_feedback_loop(ctx: Context, schematic_id: str) -> FeedbackResult:
    """Collect user feedback on a schematic using elicitation.

    This tool demonstrates MCP elicitation for collecting structured
    user feedback. It presents a form with rating, comments, and
    recommendation fields, then processes and acknowledges the feedback.

    Feedback helps improve the schematic database and can be used for:
    - Quality assessment
    - Documentation improvement
    - Priority ranking for updates

    Args:
        ctx: MCP Context object (automatically injected by FastMCP).
        schematic_id: The schematic ID to provide feedback on (e.g., "WRN-00001").

    Returns:
        FeedbackResult containing:
            - schematic_id: ID of the reviewed schematic
            - rating: User's rating (1-5)
            - feedback_text: User's comments
            - submitted_at: Timestamp of submission
            - acknowledged: Confirmation of receipt

    Example:
        When invoked with a schematic ID, the tool will prompt:
        - "Rate this schematic (1-5)"
        - "Additional comments..."
        - "Would you recommend?"
        Then return the collected feedback.
    """
    memory = get_memory_store()

    # Verify schematic exists first
    schematic = await memory.get_schematic(schematic_id)
    if not schematic:
        return FeedbackResult(
            schematic_id=schematic_id,
            rating=0,
            feedback_text="",
            submitted_at=datetime.utcnow().isoformat(),
            acknowledged=False,
        )

    # Log the feedback collection start
    await ctx.info(f"Collecting feedback for schematic: {schematic_id}")
    await ctx.info(f"Schematic: {schematic.component} ({schematic.model})")

    # Elicit feedback using structured schema
    feedback_result = await ctx.elicit(
        message=(
            f"Please provide feedback for schematic {schematic_id}:\n"
            f"Component: {schematic.component}\n"
            f"Model: {schematic.model}\n"
            f"Category: {schematic.category}"
        ),
        schema=FeedbackInput,
    )

    if feedback_result.action != "submit":
        await ctx.info("Feedback collection cancelled by user")
        return FeedbackResult(
            schematic_id=schematic_id,
            rating=0,
            feedback_text="Feedback cancelled",
            submitted_at=datetime.utcnow().isoformat(),
            acknowledged=False,
        )

    # Process the feedback
    feedback_data = feedback_result.data
    submitted_at = datetime.utcnow().isoformat()

    # In a production system, this would persist to a database
    await ctx.info(
        f"Feedback received: Rating {feedback_data.rating}/5, "
        f"Recommend: {feedback_data.would_recommend}"
    )

    # Build feedback text summary
    feedback_text = (
        f"Rating: {feedback_data.rating}/5. "
        f"Comments: {feedback_data.comments}. "
        f"Would recommend: {'Yes' if feedback_data.would_recommend else 'No'}"
    )

    return FeedbackResult(
        schematic_id=schematic_id,
        rating=feedback_data.rating,
        feedback_text=feedback_text,
        submitted_at=submitted_at,
        acknowledged=True,
    )


# =============================================================================
# RESOURCES - Read-Only Data Sources
# =============================================================================
# Resources provide read-only access to data. Unlike tools, resources don't
# perform actions - they simply return content. Resources can be:
# - Static: Fixed URI, same content each time
# - Templated: URI with parameters, dynamic content based on parameters
#
# Resources are identified by URIs and return text content (often Markdown).


@mcp.resource("memory://overview")
async def memory_overview() -> str:
    """Get an overview of the WARNERCO Schematica memory system.

    This static resource provides a formatted Markdown overview of the
    current memory backend status, including statistics and data distribution.
    Use this to understand the state of the schematic database.

    Returns:
        Markdown-formatted overview of the memory system.
    """
    memory = get_memory_store()
    stats = await memory.get_memory_stats()

    overview = f"""# WARNERCO Robotics Schematica Memory Overview

## Backend: {stats.backend}

The memory system provides persistent storage and semantic search capabilities
for robot schematics. The current backend is **{stats.backend}**.

### Statistics
| Metric | Value |
|--------|-------|
| Total Schematics | {stats.total_schematics} |
| Indexed for Search | {stats.indexed_count} |
| Embedding Chunks | {stats.chunk_count} |

### Categories
"""
    for category, count in sorted(stats.categories.items()):
        overview += f"- **{category}**: {count} schematics\n"

    overview += "\n### Status Distribution\n"
    for status, count in sorted(stats.status_counts.items()):
        overview += f"- **{status}**: {count} schematics\n"

    if stats.last_update:
        overview += f"\n---\n*Last Updated: {stats.last_update}*"

    return overview


@mcp.resource("memory://recent-queries")
async def recent_queries() -> str:
    """Get recent search queries and their results.

    This resource provides telemetry about recent searches, including
    query text, execution time, and result counts. Useful for understanding
    usage patterns and identifying common queries.

    Returns:
        Markdown-formatted list of recent queries with metadata.
    """
    memory = get_memory_store()
    hits = await memory.get_recent_hits(limit=10)

    if not hits:
        return """# Recent Queries

No recent queries recorded yet. Use the `warn_semantic_search` tool to
perform searches, and they will appear here.
"""

    output = """# Recent Queries

This resource shows the most recent search queries executed against the
schematic database.

---

"""
    for i, hit in enumerate(hits, 1):
        output += f"""## {i}. Query: "{hit.query}"

| Field | Value |
|-------|-------|
| Time | {hit.timestamp} |
| Backend | {hit.backend} |
| Duration | {hit.duration_ms:.1f}ms |
| Results | {len(hit.robot_ids)} matches |

**Matched IDs**: {', '.join(hit.robot_ids[:5])}{'...' if len(hit.robot_ids) > 5 else ''}

---

"""

    return output


@mcp.resource("memory://architecture")
async def memory_architecture() -> str:
    """Explain the 3-tier memory system architecture.

    This static resource provides detailed documentation about the
    WARNERCO Schematica memory architecture, including the three
    backend tiers and their use cases.

    Returns:
        Markdown documentation of the memory architecture.
    """
    return """# WARNERCO Schematica 3-Tier Memory Architecture

## Overview

The WARNERCO Schematica system uses a flexible 3-tier memory architecture
that allows you to choose the right backend for your deployment needs.

```
+-------------------+     +-------------------+     +-------------------+
|    Tier 1: JSON   |     |   Tier 2: Chroma  |     | Tier 3: Azure AI  |
|   (Development)   | --> |     (Staging)     | --> |     (Production)  |
+-------------------+     +-------------------+     +-------------------+
     Fast startup          Local vectors           Enterprise-scale
     Keyword search         Semantic search         Full-text + vectors
     No dependencies        Chroma DB               Azure AI Search
```

## Tier 1: JSON Store (`json`)

**Best for**: Development, testing, demos

- **Storage**: Local `schematics.json` file
- **Search**: Keyword/filter matching
- **Indexing**: None (no embeddings)
- **Dependencies**: None (Python standard library)
- **Startup Time**: ~100ms

```python
# Configuration
MEMORY_BACKEND=json
```

## Tier 2: Chroma Store (`chroma`)

**Best for**: Local development with semantic search, staging environments

- **Storage**: Local Chroma database + JSON source
- **Search**: Vector similarity search
- **Indexing**: Local embedding generation
- **Dependencies**: `chromadb`, `sentence-transformers`
- **Startup Time**: ~2-5 seconds (model loading)

```python
# Configuration
MEMORY_BACKEND=chroma
```

### Indexing with Chroma
```bash
uv run python -c "from app.adapters.chroma_store import ChromaMemoryStore; \\
    import asyncio; asyncio.run(ChromaMemoryStore().index_all())"
```

## Tier 3: Azure AI Search Store (`azure_search`)

**Best for**: Production deployments, enterprise scale

- **Storage**: Azure AI Search index
- **Search**: Hybrid (full-text + vector)
- **Indexing**: Azure OpenAI embeddings
- **Dependencies**: `azure-search-documents`, `openai`
- **Startup Time**: ~500ms (API connection)

```python
# Configuration
MEMORY_BACKEND=azure_search
AZURE_SEARCH_ENDPOINT=https://<name>.search.windows.net
AZURE_SEARCH_KEY=<your-key>
AZURE_SEARCH_INDEX=warnerco-schematics
AZURE_OPENAI_ENDPOINT=https://<name>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

### Indexing with Azure
```bash
uv run python scripts/index_azure_search.py
```

## Choosing a Backend

| Criteria | JSON | Chroma | Azure AI Search |
|----------|------|--------|-----------------|
| Semantic search | No | Yes | Yes |
| Scalability | Low | Medium | High |
| Cost | Free | Free | Pay-per-use |
| Setup complexity | None | Low | Medium |
| Production-ready | No | Maybe | Yes |

## Data Flow

1. **Source of Truth**: `data/schematics/schematics.json`
2. **Indexing**: Backends read from JSON and create their indexes
3. **Querying**: Tools query the active backend
4. **Results**: Backend returns Schematic objects

---

*Configure the backend via the `MEMORY_BACKEND` environment variable.*
"""


@mcp.resource("schematic://{schematic_id}")
async def get_schematic_resource(schematic_id: str) -> str:
    """Get a schematic as a Markdown document.

    This templated resource returns a formatted Markdown representation
    of a specific schematic. Use the schematic ID in the URI path.

    URI Template: schematic://{schematic_id}
    Example: schematic://WRN-00001

    Args:
        schematic_id: The unique schematic identifier (extracted from URI).

    Returns:
        Markdown-formatted schematic document, or error message if not found.
    """
    memory = get_memory_store()
    schematic = await memory.get_schematic(schematic_id)

    if not schematic:
        return f"""# Schematic Not Found

The schematic with ID `{schematic_id}` was not found in the database.

## Troubleshooting

1. Verify the schematic ID format (should be WRN-XXXXX)
2. Use `warn_list_robots` to see available schematics
3. Check if the schematic has been indexed
"""

    # Build Markdown document
    doc = f"""# {schematic.component}

**Schematic ID**: {schematic.id}
**Robot Model**: {schematic.model} ({schematic.name})
**Version**: {schematic.version}
**Category**: {schematic.category}
**Status**: {schematic.status.value}

---

## Summary

{schematic.summary}

## Tags

{', '.join(f'`{tag}`' for tag in schematic.tags) if schematic.tags else '_No tags_'}

"""

    if schematic.specifications:
        doc += "## Specifications\n\n| Specification | Value |\n|---------------|-------|\n"
        for key, value in schematic.specifications.items():
            doc += f"| {key} | {value} |\n"
        doc += "\n"

    doc += f"""## Resources

- [View Full Schematic]({schematic.url})

---

*Last Verified: {schematic.last_verified}*
"""

    return doc


@mcp.resource("catalog://categories")
async def list_categories() -> str:
    """List all available schematic categories.

    This resource provides a catalog of all categories in the schematic
    database, with descriptions and counts.

    Returns:
        Markdown-formatted category catalog.
    """
    memory = get_memory_store()
    stats = await memory.get_memory_stats()

    # Category descriptions (these could come from a config in production)
    descriptions = {
        "sensors": "Sensing and detection components including thermal, proximity, and environmental sensors",
        "power": "Power supply, battery management, and energy distribution systems",
        "control": "Control processors, PLCs, and decision-making units",
        "mobility": "Movement systems including motors, actuators, and locomotion components",
        "communication": "Network interfaces, radio modules, and data transmission systems",
    }

    doc = """# Schematic Categories

This catalog lists all categories of robot schematics available in the database.

---

"""

    for category, count in sorted(stats.categories.items()):
        desc = descriptions.get(category, "No description available")
        doc += f"""## {category.title()}

{desc}

**Schematics**: {count}

Use `warn_list_robots(category="{category}")` to browse these schematics.

---

"""

    return doc


@mcp.resource("catalog://models")
async def list_models() -> str:
    """List all robot models in the schematic database.

    This resource provides a catalog of all robot models represented
    in the schematic database.

    Returns:
        Markdown-formatted model catalog.
    """
    memory = get_memory_store()
    schematics = await memory.list_schematics(limit=1000)

    # Group by model
    models: Dict[str, Dict[str, Any]] = {}
    for s in schematics:
        if s.model not in models:
            models[s.model] = {"name": s.name, "count": 0, "categories": set()}
        models[s.model]["count"] += 1
        models[s.model]["categories"].add(s.category)

    doc = """# Robot Models Catalog

This catalog lists all robot models with schematics in the database.

---

"""

    for model_id, info in sorted(models.items()):
        categories_str = ", ".join(sorted(info["categories"]))
        doc += f"""## {model_id}: {info["name"]}

**Schematics**: {info["count"]}
**Categories**: {categories_str}

Use `warn_list_robots(model="{model_id}")` to browse schematics for this model.

---

"""

    return doc


@mcp.resource("help://tools")
async def help_tools() -> str:
    """Self-documenting resource listing all available tools.

    This meta-resource provides documentation for all tools registered
    with this MCP server, including their signatures and descriptions.

    Returns:
        Markdown documentation of all available tools.
    """
    return f"""# WARNERCO Schematica - Available Tools

This MCP server provides {11} tools for interacting with robot schematics.

---

## Data Retrieval Tools

### `warn_list_robots`

List robot schematics with optional filtering.

**Parameters**:
- `category` (optional, string): Filter by category (sensors, power, control, mobility, communication)
- `model` (optional, string): Filter by robot model (WC-100, WC-200, etc.)
- `status` (optional, string): Filter by status (active, deprecated, draft)
- `limit` (optional, int): Maximum results to return (default: 20, max: 100)

**Returns**: List of schematic summaries with count

---

### `warn_get_robot`

Get detailed information about a specific robot schematic.

**Parameters**:
- `schematic_id` (required, string): Schematic ID in WRN-XXXXX format

**Returns**: Full schematic details or error message

---

### `warn_semantic_search`

Search robot schematics using natural language queries.

**Parameters**:
- `query` (required, string): Natural language search query
- `category` (optional, string): Filter by category
- `model` (optional, string): Filter by robot model
- `top_k` (optional, int): Number of results (default: 5, max: 50)

**Returns**: Search results with relevance scores and reasoning

---

### `warn_memory_stats`

Get statistics about the schematic memory system.

**Parameters**: None

**Returns**: Memory backend statistics including counts and distribution

---

## Data Modification Tools

### `warn_create_schematic`

Create a new robot schematic in the database.

**Parameters**:
- `model` (required, string): Robot model identifier (e.g., "WC-100")
- `name` (required, string): Robot name (e.g., "Atlas Prime")
- `component` (required, string): Component being documented
- `category` (required, string): Category (sensors, power, control, mobility, communication)
- `summary` (required, string): Technical summary
- `version` (optional, string): Version string (default: "1.0.0")
- `status` (optional, string): Status (draft, active, deprecated) (default: "draft")
- `tags` (optional, list): Searchable tags
- `specifications` (optional, dict): Technical specifications
- `url` (optional, string): URL to schematic document

**Returns**: Created schematic with auto-generated WRN-XXXXX ID

---

### `warn_update_schematic`

Update an existing schematic's fields.

**Parameters**:
- `schematic_id` (required, string): Which schematic to update
- All other fields optional - only provided fields are updated
- Automatically updates `last_verified` date

**Returns**: Updated schematic with list of modified fields

---

### `warn_delete_schematic`

Delete a schematic from the database.

**Parameters**:
- `schematic_id` (required, string): Schematic ID to delete
- `confirm` (required, bool): Safety flag - must be True to delete

**Returns**: Deletion confirmation with deleted component name

---

### `warn_index_schematic`

Index a single schematic for semantic search.

**Parameters**:
- `schematic_id` (required, string): Schematic ID to index

**Returns**: Indexing result with success status

---

### `warn_compare_schematics`

Compare two schematics side-by-side.

**Parameters**:
- `id1` (required, string): First schematic ID
- `id2` (required, string): Second schematic ID

**Returns**: Comparison with similarities, differences, and recommendations

---

## Interactive Tools (with Elicitation)

### `warn_guided_search`

Perform a guided, multi-step search with user input.

**Parameters**: None (uses elicitation for input)

**Returns**: Search results from guided session

---

### `warn_feedback_loop`

Collect user feedback on a schematic.

**Parameters**:
- `schematic_id` (required, string): Schematic to provide feedback on

**Returns**: Collected feedback with acknowledgment

---

*Server Version: {SERVER_VERSION}*
"""


@mcp.resource("help://resources")
async def help_resources() -> str:
    """Self-documenting resource listing all available resources.

    This meta-resource provides documentation for all resources registered
    with this MCP server, including their URIs and descriptions.

    Returns:
        Markdown documentation of all available resources.
    """
    return f"""# WARNERCO Schematica - Available Resources

This MCP server provides resources for accessing schematic data and documentation.

---

## Memory System Resources

### `memory://overview`

Get an overview of the WARNERCO Schematica memory system.

**Type**: Static
**Content**: Memory backend statistics in Markdown format

---

### `memory://recent-queries`

Get recent search queries and their results.

**Type**: Static (dynamic content)
**Content**: List of recent queries with performance metrics

---

### `memory://architecture`

Explain the 3-tier memory system architecture.

**Type**: Static
**Content**: Documentation of JSON/Chroma/Azure backends

---

## Catalog Resources

### `catalog://categories`

List all available schematic categories.

**Type**: Static (dynamic content)
**Content**: Category catalog with descriptions and counts

---

### `catalog://models`

List all robot models in the schematic database.

**Type**: Static (dynamic content)
**Content**: Robot model catalog with schematic counts

---

## Schematic Resources

### `schematic://{{schematic_id}}`

Get a schematic as a Markdown document.

**Type**: Templated
**URI Example**: `schematic://WRN-00001`
**Content**: Formatted schematic documentation

---

## Help Resources

### `help://tools`

Self-documenting resource listing all available tools.

**Type**: Static
**Content**: This documentation

---

### `help://resources`

Self-documenting resource listing all available resources.

**Type**: Static
**Content**: Resource catalog with descriptions

---

### `help://prompts`

Self-documenting resource listing all available prompts.

**Type**: Static
**Content**: Prompt templates with usage examples

---

## Meta Resources

### `mcp://capabilities`

Comprehensive overview of all server capabilities.

**Type**: Static
**Content**: Complete server documentation

---

*Server Version: {SERVER_VERSION}*
"""


@mcp.resource("help://prompts")
async def help_prompts() -> str:
    """Self-documenting resource listing all available prompts.

    This meta-resource provides documentation for all prompts registered
    with this MCP server, including their arguments and usage.

    Returns:
        Markdown documentation of all available prompts.
    """
    return f"""# WARNERCO Schematica - Available Prompts

This MCP server provides reusable prompt templates for common schematic tasks.

---

## Analysis Prompts

### `diagnostic_prompt`

Generate a diagnostic analysis prompt for a robot schematic.

**Arguments**:
- `robot_id` (required, string): The schematic ID to analyze

**Use Case**: When you need to diagnose issues or analyze a specific schematic

**Example**:
```
Use the diagnostic_prompt for WRN-00001 to analyze the thermal sensor array.
```

---

### `schematic_review_prompt`

Generate a technical review prompt for a schematic.

**Arguments**:
- `schematic_id` (required, string): The schematic ID to review

**Use Case**: When you need to perform a thorough technical review

---

## Comparison Prompts

### `comparison_prompt`

Generate a comparison analysis prompt for two schematics.

**Arguments**:
- `id1` (required, string): First schematic ID
- `id2` (required, string): Second schematic ID

**Use Case**: When deciding between alternative components

---

## Search Prompts

### `search_strategy_prompt`

Create an optimized search strategy prompt.

**Arguments**:
- `query` (required, string): The search query
- `filters` (optional, string): Comma-separated filters

**Use Case**: When you need help formulating an effective search

---

## Maintenance Prompts

### `maintenance_report_prompt`

Generate a maintenance report template for a robot model.

**Arguments**:
- `robot_model` (required, string): The robot model (e.g., WC-100)

**Use Case**: When creating maintenance documentation

---

*Server Version: {SERVER_VERSION}*
"""


@mcp.resource("mcp://capabilities")
async def mcp_capabilities() -> str:
    """Comprehensive overview of all server capabilities.

    This meta-resource provides complete documentation of the MCP server,
    including all tools, resources, prompts, and usage examples.

    Returns:
        Complete server documentation in Markdown format.
    """
    memory = get_memory_store()
    stats = await memory.get_memory_stats()

    return f"""# WARNERCO Schematica MCP Server

**Version**: {SERVER_VERSION}
**Server Name**: warnerco-schematica
**Backend**: {stats.backend}
**Total Schematics**: {stats.total_schematics}

---

## Overview

The WARNERCO Schematica MCP server provides access to robot schematic
documentation through the Model Context Protocol. It demonstrates all
MCP primitives:

- **11 Tools** - Executable functions for data retrieval, modification, and interaction
- **10 Resources** - Read-only data sources (static and templated)
- **5 Prompts** - Reusable prompt templates
- **2 Elicitation Tools** - Interactive user input (included in tool count)

---

## Tools Summary

| Tool | Description |
|------|-------------|
| `warn_list_robots` | List schematics with filtering |
| `warn_get_robot` | Get schematic details by ID |
| `warn_semantic_search` | Natural language search |
| `warn_memory_stats` | Memory system statistics |
| `warn_create_schematic` | Create new schematic (auto-generates ID) |
| `warn_update_schematic` | Update existing schematic fields |
| `warn_delete_schematic` | Delete schematic (requires confirmation) |
| `warn_index_schematic` | Index for semantic search |
| `warn_compare_schematics` | Side-by-side comparison |
| `warn_guided_search` | Interactive guided search |
| `warn_feedback_loop` | Collect user feedback |

---

## Resources Summary

| URI | Type | Description |
|-----|------|-------------|
| `memory://overview` | Static | Memory system overview |
| `memory://recent-queries` | Static | Recent query telemetry |
| `memory://architecture` | Static | 3-tier architecture docs |
| `schematic://{{id}}` | Template | Schematic as Markdown |
| `catalog://categories` | Static | Category catalog |
| `catalog://models` | Static | Robot model catalog |
| `help://tools` | Static | Tool documentation |
| `help://resources` | Static | Resource documentation |
| `help://prompts` | Static | Prompt documentation |
| `mcp://capabilities` | Static | This overview |

---

## Prompts Summary

| Prompt | Arguments | Description |
|--------|-----------|-------------|
| `diagnostic_prompt` | robot_id | Diagnostic analysis |
| `comparison_prompt` | id1, id2 | Compare schematics |
| `search_strategy_prompt` | query, filters? | Search optimization |
| `maintenance_report_prompt` | robot_model | Maintenance docs |
| `schematic_review_prompt` | schematic_id | Technical review |

---

## Quick Start

### List all sensors
```
warn_list_robots(category="sensors")
```

### Search for temperature-related components
```
warn_semantic_search(query="temperature monitoring in extreme environments")
```

### Get schematic details
```
warn_get_robot(schematic_id="WRN-00001")
```

### Read schematic as Markdown
Access resource: `schematic://WRN-00001`

---

## Architecture

```
                    +-----------------------+
                    |   MCP Client (LLM)    |
                    +-----------+-----------+
                                |
                                v
+-----------------------------------------------------------------------------------+
|                        FastMCP Server (warnerco-schematica)                       |
+-----------------------------------------------------------------------------------+
|  Tools              |  Resources          |  Prompts            |  Elicitations   |
|  - list_robots      |  - memory://        |  - diagnostic       |  - guided       |
|  - get_robot        |  - schematic://     |  - comparison       |  - feedback     |
|  - semantic_search  |  - catalog://       |  - search_strategy  |                 |
|  - memory_stats     |  - help://          |  - maintenance      |                 |
|  - index_schematic  |  - mcp://           |  - schematic_review |                 |
|  - compare          |                     |                     |                 |
+-----------------------------------------------------------------------------------+
                                |
                                v
+-----------------------------------------------------------------------------------+
|                      LangGraph RAG Pipeline (5 nodes)                             |
|  parse_intent -> retrieve -> compress_context -> reason -> respond                |
+-----------------------------------------------------------------------------------+
                                |
                                v
+-----------------------------------------------------------------------------------+
|                      3-Tier Memory Backend                                        |
|  JSON (dev) <-> Chroma (staging) <-> Azure AI Search (production)                 |
+-----------------------------------------------------------------------------------+
```

---

*This MCP server is a teaching example demonstrating all MCP primitives.*
*See https://spec.modelcontextprotocol.io for the full MCP specification.*
"""


# =============================================================================
# PROMPTS - Reusable Prompt Templates
# =============================================================================
# Prompts are reusable templates that generate structured content for the LLM.
# Unlike tools (which perform actions) and resources (which return data),
# prompts return instructions or templates that guide LLM behavior.
#
# Prompts can take arguments and return formatted strings that incorporate
# context from the schematic database.


@mcp.prompt()
async def diagnostic_prompt(robot_id: str) -> str:
    """Generate a diagnostic analysis prompt for a robot schematic.

    This prompt template retrieves schematic details and generates a
    structured diagnostic analysis prompt that guides the LLM through
    a systematic evaluation of the component.

    Args:
        robot_id: The schematic ID to analyze (e.g., "WRN-00001")

    Returns:
        A formatted prompt string for diagnostic analysis, or an error
        message if the schematic is not found.

    Example:
        >>> prompt = await diagnostic_prompt("WRN-00001")
        >>> # Returns a structured prompt for analyzing the thermal sensor
    """
    memory = get_memory_store()
    schematic = await memory.get_schematic(robot_id)

    if not schematic:
        return f"""# Error: Schematic Not Found

The schematic `{robot_id}` could not be found. Please verify the ID and try again.

Use the `warn_list_robots` tool to see available schematics.
"""

    specs_text = ""
    if schematic.specifications:
        specs_text = "\n".join(
            f"- {k}: {v}" for k, v in schematic.specifications.items()
        )
    else:
        specs_text = "No specifications available"

    return f"""# Diagnostic Analysis: {schematic.component}

## Schematic Information
- **ID**: {schematic.id}
- **Model**: {schematic.model} ({schematic.name})
- **Component**: {schematic.component}
- **Version**: {schematic.version}
- **Category**: {schematic.category}
- **Status**: {schematic.status.value}

## Technical Summary
{schematic.summary}

## Specifications
{specs_text}

## Diagnostic Instructions

Please analyze this schematic and provide:

1. **Component Health Assessment**
   - Evaluate the component's current status
   - Identify any potential reliability concerns
   - Assess version currency (is an update needed?)

2. **Performance Analysis**
   - Review specifications against typical requirements
   - Identify any specification gaps or limitations
   - Compare to industry standards where applicable

3. **Integration Considerations**
   - Compatibility with the {schematic.model} platform
   - Dependencies on other components
   - Interface requirements

4. **Maintenance Recommendations**
   - Suggested inspection intervals
   - Common failure modes to monitor
   - Preventive maintenance actions

5. **Upgrade Path**
   - Available newer versions
   - Migration considerations
   - Cost-benefit assessment

## Tags for Context
{', '.join(schematic.tags) if schematic.tags else 'No tags'}

---
*Use the `warn_semantic_search` tool to find related schematics or alternatives.*
"""


@mcp.prompt()
async def comparison_prompt(id1: str, id2: str) -> str:
    """Generate a comparison analysis prompt for two schematics.

    This prompt retrieves both schematics and generates a structured
    comparison prompt that guides the LLM through a systematic evaluation
    of similarities and differences.

    Args:
        id1: First schematic ID to compare
        id2: Second schematic ID to compare

    Returns:
        A formatted comparison prompt string, or error if either schematic
        is not found.

    Example:
        >>> prompt = await comparison_prompt("WRN-00001", "WRN-00005")
        >>> # Returns a structured prompt for comparing two components
    """
    memory = get_memory_store()
    schematic1 = await memory.get_schematic(id1)
    schematic2 = await memory.get_schematic(id2)

    errors = []
    if not schematic1:
        errors.append(f"Schematic `{id1}` not found")
    if not schematic2:
        errors.append(f"Schematic `{id2}` not found")

    if errors:
        return f"""# Error: Schematic(s) Not Found

{chr(10).join(f'- {e}' for e in errors)}

Please verify the schematic IDs and try again.
Use the `warn_list_robots` tool to see available schematics.
"""

    def format_specs(specs):
        if not specs:
            return "No specifications available"
        return "\n".join(f"  - {k}: {v}" for k, v in specs.items())

    return f"""# Schematic Comparison Analysis

## Schematic 1: {schematic1.component}
- **ID**: {schematic1.id}
- **Model**: {schematic1.model} ({schematic1.name})
- **Version**: {schematic1.version}
- **Category**: {schematic1.category}
- **Status**: {schematic1.status.value}
- **Summary**: {schematic1.summary}
- **Specifications**:
{format_specs(schematic1.specifications)}

## Schematic 2: {schematic2.component}
- **ID**: {schematic2.id}
- **Model**: {schematic2.model} ({schematic2.name})
- **Version**: {schematic2.version}
- **Category**: {schematic2.category}
- **Status**: {schematic2.status.value}
- **Summary**: {schematic2.summary}
- **Specifications**:
{format_specs(schematic2.specifications)}

## Comparison Instructions

Please analyze these two schematics and provide:

1. **Functional Comparison**
   - Primary purpose of each component
   - Functional overlap and uniqueness
   - Performance characteristics

2. **Specification Analysis**
   - Side-by-side specification comparison
   - Key differences in capabilities
   - Which specs favor which component

3. **Compatibility Assessment**
   - Robot model compatibility
   - Integration requirements
   - Cross-compatibility potential

4. **Use Case Recommendations**
   - When to prefer Schematic 1
   - When to prefer Schematic 2
   - Scenarios where either works

5. **Lifecycle Considerations**
   - Version comparison
   - Status implications
   - Future support outlook

6. **Decision Matrix**
   | Criterion | {schematic1.id} | {schematic2.id} |
   |-----------|-----------------|-----------------|
   | [Criterion 1] | [Rating] | [Rating] |
   | [Criterion 2] | [Rating] | [Rating] |

---
*Use `warn_compare_schematics` for a programmatic comparison.*
"""


@mcp.prompt()
async def search_strategy_prompt(
    query: str,
    filters: Optional[str] = None,
) -> str:
    """Create an optimized search strategy prompt.

    This prompt generates guidance for formulating effective searches
    in the schematic database, based on the user's query and any filters.

    Args:
        query: The user's search query or intent
        filters: Optional comma-separated filters (e.g., "category=sensors,model=WC-100")

    Returns:
        A formatted prompt with search strategy guidance.

    Example:
        >>> prompt = await search_strategy_prompt(
        ...     query="temperature monitoring",
        ...     filters="category=sensors"
        ... )
    """
    memory = get_memory_store()
    stats = await memory.get_memory_stats()

    # Parse filters if provided
    filter_dict = {}
    if filters:
        for f in filters.split(","):
            if "=" in f:
                key, value = f.strip().split("=", 1)
                filter_dict[key.strip()] = value.strip()

    filter_text = (
        "\n".join(f"- {k}: {v}" for k, v in filter_dict.items())
        if filter_dict
        else "No filters specified"
    )

    categories = ", ".join(stats.categories.keys())

    return f"""# Search Strategy: "{query}"

## Query Analysis

**Original Query**: {query}

**Applied Filters**:
{filter_text}

## Database Context

- **Total Schematics**: {stats.total_schematics}
- **Available Categories**: {categories}
- **Backend**: {stats.backend}

## Search Strategy Instructions

Please optimize this search using the following approach:

1. **Query Decomposition**
   - Break down the query into key concepts
   - Identify the primary intent (find, compare, analyze, etc.)
   - Extract implicit requirements

2. **Keyword Expansion**
   - Suggest related terms and synonyms
   - Include technical terminology
   - Consider component-specific vocabulary

3. **Filter Recommendations**
   Based on the query, suggest appropriate filters:
   - Category: [recommendation]
   - Model: [recommendation]
   - Status: [recommendation]

4. **Query Reformulation**
   Provide 3 optimized query variants:
   - Broad search: [query]
   - Focused search: [query]
   - Specific search: [query]

5. **Execution Plan**
   ```
   Step 1: [First search approach]
   Step 2: [Refinement based on results]
   Step 3: [Follow-up actions]
   ```

6. **Expected Results**
   - Likely matching categories: [list]
   - Estimated result count: [range]
   - Potential challenges: [notes]

## Tools to Use

- `warn_semantic_search` - For natural language queries
- `warn_list_robots` - For filtered browsing
- `warn_get_robot` - For detailed inspection

---
*Execute the search using `warn_semantic_search(query="{query}")`*
"""


@mcp.prompt()
async def maintenance_report_prompt(robot_model: str) -> str:
    """Generate a maintenance report template for a robot model.

    This prompt retrieves all schematics for a specific robot model and
    generates a maintenance report template covering all components.

    Args:
        robot_model: The robot model identifier (e.g., "WC-100")

    Returns:
        A formatted maintenance report template.

    Example:
        >>> prompt = await maintenance_report_prompt("WC-100")
        >>> # Returns a maintenance report template for WC-100
    """
    memory = get_memory_store()
    schematics = await memory.list_schematics(
        filters={"model": robot_model},
        limit=100,
    )

    if not schematics:
        return f"""# Error: No Schematics Found

No schematics found for robot model `{robot_model}`.

Available models can be found using the `catalog://models` resource.
"""

    # Get the robot name from first schematic
    robot_name = schematics[0].name

    # Group by category
    by_category: Dict[str, list] = {}
    for s in schematics:
        if s.category not in by_category:
            by_category[s.category] = []
        by_category[s.category].append(s)

    components_text = ""
    for category, items in sorted(by_category.items()):
        components_text += f"\n### {category.title()}\n"
        for s in items:
            components_text += f"""
#### {s.component} (v{s.version})
- **Schematic**: {s.id}
- **Status**: {s.status.value}
- **Summary**: {s.summary}
- [ ] Visual inspection completed
- [ ] Functional test passed
- [ ] Calibration verified
- [ ] Notes: _________________
"""

    return f"""# Maintenance Report Template

## Robot Information
- **Model**: {robot_model}
- **Name**: {robot_name}
- **Report Date**: [DATE]
- **Technician**: [NAME]
- **Location**: [LOCATION]

## Executive Summary
[Provide overall assessment of robot condition]

## Components Inspected ({len(schematics)} total)
{components_text}

## Maintenance Actions Required

| Priority | Component | Action | Estimated Time | Parts Needed |
|----------|-----------|--------|----------------|--------------|
| [ ] High | | | | |
| [ ] Medium | | | | |
| [ ] Low | | | | |

## Recommendations

### Immediate Actions
1. [List urgent maintenance needs]

### Scheduled Maintenance
1. [List planned maintenance activities]

### Upgrades to Consider
1. [List potential component upgrades]

## Sign-off

- **Inspected By**: _________________ Date: _______
- **Reviewed By**: _________________ Date: _______
- **Approved By**: _________________ Date: _______

---
*Generated from WARNERCO Schematica for {robot_model} ({robot_name})*
*Use `warn_list_robots(model="{robot_model}")` for current component status*
"""


@mcp.prompt()
async def schematic_review_prompt(schematic_id: str) -> str:
    """Generate a technical review prompt for a schematic.

    This prompt retrieves a schematic and generates a structured technical
    review template that guides thorough documentation review.

    Args:
        schematic_id: The schematic ID to review (e.g., "WRN-00001")

    Returns:
        A formatted technical review prompt.

    Example:
        >>> prompt = await schematic_review_prompt("WRN-00001")
        >>> # Returns a technical review template for the schematic
    """
    memory = get_memory_store()
    schematic = await memory.get_schematic(schematic_id)

    if not schematic:
        return f"""# Error: Schematic Not Found

The schematic `{schematic_id}` could not be found.

Use the `warn_list_robots` tool to see available schematics.
"""

    specs_text = ""
    if schematic.specifications:
        specs_text = "\n".join(
            f"| {k} | {v} | [ ] Verified |"
            for k, v in schematic.specifications.items()
        )
    else:
        specs_text = "| No specifications | - | - |"

    tags_text = ", ".join(f"`{t}`" for t in schematic.tags) if schematic.tags else "None"

    return f"""# Technical Review: {schematic.component}

## Document Information
- **Schematic ID**: {schematic.id}
- **Review Date**: [DATE]
- **Reviewer**: [NAME]
- **Review Type**: [ ] Initial [ ] Update [ ] Annual

## Component Details
| Field | Value | Status |
|-------|-------|--------|
| Model | {schematic.model} ({schematic.name}) | [ ] Correct |
| Component | {schematic.component} | [ ] Correct |
| Version | {schematic.version} | [ ] Current |
| Category | {schematic.category} | [ ] Appropriate |
| Status | {schematic.status.value} | [ ] Accurate |
| Last Verified | {schematic.last_verified} | [ ] Recent |

## Technical Summary Review

**Current Summary**:
> {schematic.summary}

**Summary Assessment**:
- [ ] Accurate and complete
- [ ] Needs minor updates
- [ ] Needs major revision
- [ ] Notes: _________________

## Specification Verification

| Specification | Value | Verified |
|---------------|-------|----------|
{specs_text}

## Tag Review

**Current Tags**: {tags_text}

- [ ] Tags are comprehensive
- [ ] Tags follow naming conventions
- [ ] Suggested additions: _________________

## Documentation Quality

### Completeness
- [ ] All required fields populated
- [ ] Specifications are detailed
- [ ] Summary is informative
- [ ] URL is accessible

### Accuracy
- [ ] Technical details are correct
- [ ] Version is current
- [ ] Specifications match actual component
- [ ] No contradictions found

### Clarity
- [ ] Summary is clear and concise
- [ ] Specifications are understandable
- [ ] No ambiguous terminology

## Issues Found

| Issue | Severity | Recommendation |
|-------|----------|----------------|
| | [ ] High [ ] Med [ ] Low | |
| | [ ] High [ ] Med [ ] Low | |

## Recommendations

1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

## Review Decision

- [ ] **Approved** - No changes needed
- [ ] **Approved with Changes** - Minor updates required
- [ ] **Revision Required** - Significant updates needed
- [ ] **Rejected** - Major issues, needs rework

## Sign-off

- **Reviewer**: _________________ Date: _______
- **Technical Lead**: _________________ Date: _______

---
*Full schematic available at: {schematic.url}*
*Use `warn_get_robot("{schematic_id}")` for programmatic access*
"""


# =============================================================================
# MODULE EXPORTS
# =============================================================================
# The mcp instance is the main export. It is used by:
# - FastAPI to mount the MCP endpoint
# - The CLI entry point for stdio transport
# - Tests to verify tool behavior

__all__ = ["mcp", "SERVER_VERSION"]

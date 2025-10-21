"""
Context Journal MCP Server
===========================
A pedagogical MCP server that manages conversation context as a persistent journal.
Demonstrates core MCP concepts with clear CRUD operations on JSON storage.

Perfect for teaching context engineering before scaling to Azure Cosmos DB.
"""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum
import json
import os
from pathlib import Path

# Constants
CHARACTER_LIMIT = 25000
JOURNAL_FILE = "context_journal.json"

# Initialize MCP server
mcp = FastMCP("context_journal_mcp")


# ============================================================================
# Shared Utilities - DRY principle in action
# ============================================================================

def load_journal() -> Dict[str, Any]:
    """Load journal from JSON file, creating if doesn't exist."""
    if not os.path.exists(JOURNAL_FILE):
        initial_data = {
            "entries": [],
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0"
            }
        }
        save_journal(initial_data)
        return initial_data
    
    with open(JOURNAL_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_journal(data: Dict[str, Any]) -> None:
    """Save journal data to JSON file."""
    with open(JOURNAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_entry_by_id(journal: Dict[str, Any], entry_id: str) -> Optional[Dict[str, Any]]:
    """Find a journal entry by ID."""
    for entry in journal["entries"]:
        if entry["id"] == entry_id:
            return entry
    return None


def format_entry_markdown(entry: Dict[str, Any]) -> str:
    """Format a single entry as Markdown."""
    created = datetime.fromisoformat(entry["created_at"]).strftime("%Y-%m-%d %H:%M:%S UTC")
    updated = datetime.fromisoformat(entry["updated_at"]).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    md = f"""## {entry['title']}
**ID:** `{entry['id']}`
**Tags:** {', '.join(entry['tags']) if entry['tags'] else 'None'}
**Created:** {created}
**Updated:** {updated}

### Context
{entry['context']}
"""
    if entry.get('notes'):
        md += f"\n### Notes\n{entry['notes']}\n"
    
    return md


def truncate_if_needed(content: str, message_prefix: str = "") -> str:
    """Truncate content if it exceeds CHARACTER_LIMIT."""
    if len(content) <= CHARACTER_LIMIT:
        return content
    
    truncated = content[:CHARACTER_LIMIT]
    notice = f"\n\n⚠️ **Response truncated at {CHARACTER_LIMIT} characters.** {message_prefix}"
    return truncated + notice


# ============================================================================
# Pydantic Models - Input Validation
# ============================================================================

class ResponseFormat(str, Enum):
    """Output format options for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


class CreateEntryInput(BaseModel):
    """Input model for creating a new context journal entry."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    title: str = Field(
        ...,
        description="Title for this context entry (e.g., 'Python Project Setup', 'API Design Discussion')",
        min_length=1,
        max_length=200
    )
    context: str = Field(
        ...,
        description="The actual context content to preserve (e.g., conversation summary, code snippets, decisions made)",
        min_length=1,
        max_length=10000
    )
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Tags for categorization (e.g., ['python', 'api', 'azure'])",
        max_length=20
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional additional notes or metadata",
        max_length=5000
    )
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Ensure tags are lowercase and unique."""
        return list(set(tag.lower() for tag in v if tag.strip()))


class ReadEntryInput(BaseModel):
    """Input model for reading a specific journal entry."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    entry_id: str = Field(
        ...,
        description="Unique identifier of the entry to retrieve",
        min_length=1
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )


class UpdateEntryInput(BaseModel):
    """Input model for updating an existing journal entry."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    entry_id: str = Field(
        ...,
        description="Unique identifier of the entry to update",
        min_length=1
    )
    title: Optional[str] = Field(
        default=None,
        description="New title (leave empty to keep current)",
        max_length=200
    )
    context: Optional[str] = Field(
        default=None,
        description="New context content (leave empty to keep current)",
        max_length=10000
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="New tags (leave empty to keep current, use empty list to clear all tags)"
    )
    notes: Optional[str] = Field(
        default=None,
        description="New notes (leave empty to keep current, use empty string to clear)"
    )
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Ensure tags are lowercase and unique if provided."""
        if v is None:
            return None
        return list(set(tag.lower() for tag in v if tag.strip()))


class DeleteEntryInput(BaseModel):
    """Input model for deleting a journal entry."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    entry_id: str = Field(
        ...,
        description="Unique identifier of the entry to delete",
        min_length=1
    )


class ListEntriesInput(BaseModel):
    """Input model for listing journal entries with filtering and pagination."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    tags: Optional[List[str]] = Field(
        default=None,
        description="Filter by tags (returns entries matching ANY tag)"
    )
    search_text: Optional[str] = Field(
        default=None,
        description="Search in title, context, and notes",
        max_length=200
    )
    limit: Optional[int] = Field(
        default=20,
        description="Maximum number of entries to return",
        ge=1,
        le=100
    )
    offset: Optional[int] = Field(
        default=0,
        description="Number of entries to skip for pagination",
        ge=0
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Ensure tags are lowercase if provided."""
        if v is None:
            return None
        return [tag.lower() for tag in v if tag.strip()]


class SearchEntriesInput(BaseModel):
    """Input model for searching journal entries by tags or text."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    query: str = Field(
        ...,
        description="Search query to match against title, context, notes, and tags",
        min_length=1,
        max_length=200
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )


# ============================================================================
# MCP Tools - CRUD Operations
# ============================================================================

@mcp.tool(
    name="create_context_entry",
    annotations={
        "title": "Create Context Journal Entry",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def create_context_entry(params: CreateEntryInput) -> str:
    """Create a new context journal entry to preserve conversation context.
    
    This tool enables persistent memory by storing important conversation context,
    decisions, code snippets, or any information worth preserving across sessions.
    Each entry gets a unique ID for later retrieval, update, or deletion.
    
    Args:
        params (CreateEntryInput): Input parameters containing:
            - title (str): Entry title (1-200 chars)
            - context (str): Context content to preserve (1-10,000 chars)
            - tags (Optional[List[str]]): Categorization tags
            - notes (Optional[str]): Additional notes/metadata
    
    Returns:
        str: JSON response containing:
            {
                "success": true,
                "entry_id": "unique-identifier",
                "message": "Confirmation message",
                "created_at": "ISO-8601 timestamp"
            }
    
    Example Usage:
        Create an entry to remember a Python project decision:
        - title: "Python Project: FastAPI vs Flask Decision"
        - context: "Team decided on FastAPI for async support and automatic docs..."
        - tags: ["python", "architecture", "decision"]
    """
    try:
        journal = load_journal()
        
        # Generate unique ID
        entry_id = f"ctx_{len(journal['entries']) + 1:04d}"
        timestamp = datetime.utcnow().isoformat()
        
        # Create new entry
        entry = {
            "id": entry_id,
            "title": params.title,
            "context": params.context,
            "tags": params.tags,
            "notes": params.notes,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        journal["entries"].append(entry)
        save_journal(journal)
        
        response = {
            "success": True,
            "entry_id": entry_id,
            "message": f"Context entry '{params.title}' created successfully",
            "created_at": timestamp
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "message": "Failed to create context entry. Please verify inputs and try again."
        }
        return json.dumps(error_response, indent=2)


@mcp.tool(
    name="read_context_entry",
    annotations={
        "title": "Read Context Journal Entry",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def read_context_entry(params: ReadEntryInput) -> str:
    """Retrieve a specific context journal entry by ID.
    
    Use this tool to recall previously stored context. Perfect for continuing
    conversations, reviewing past decisions, or accessing saved code snippets.
    
    Args:
        params (ReadEntryInput): Input parameters containing:
            - entry_id (str): Unique identifier of the entry
            - response_format (ResponseFormat): 'markdown' or 'json'
    
    Returns:
        str: Entry data in requested format (markdown or JSON)
        
    Error Handling:
        - If entry not found: Returns clear error with suggestion to list entries
        - Returns entry details in markdown or JSON format as requested
    
    Example Usage:
        To recall a previous discussion: entry_id="ctx_0001"
    """
    try:
        journal = load_journal()
        entry = find_entry_by_id(journal, params.entry_id)
        
        if not entry:
            error_response = {
                "success": False,
                "error": f"Entry '{params.entry_id}' not found",
                "message": "Entry not found. Use 'list_context_entries' to see available entries."
            }
            return json.dumps(error_response, indent=2)
        
        if params.response_format == ResponseFormat.MARKDOWN:
            return format_entry_markdown(entry)
        else:
            return json.dumps(entry, indent=2)
            
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "message": "Failed to read context entry. Please verify the entry ID."
        }
        return json.dumps(error_response, indent=2)


@mcp.tool(
    name="update_context_entry",
    annotations={
        "title": "Update Context Journal Entry",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def update_context_entry(params: UpdateEntryInput) -> str:
    """Update an existing context journal entry.
    
    Modify any field of an existing entry while preserving unchanged fields.
    The updated_at timestamp is automatically updated. Use this to refine context,
    add new information, or reorganize tags.
    
    Args:
        params (UpdateEntryInput): Input parameters containing:
            - entry_id (str): Entry to update
            - title (Optional[str]): New title (omit to keep current)
            - context (Optional[str]): New context (omit to keep current)
            - tags (Optional[List[str]]): New tags (omit to keep current, empty list clears)
            - notes (Optional[str]): New notes (omit to keep current, empty string clears)
    
    Returns:
        str: JSON response containing:
            {
                "success": true,
                "entry_id": "entry-id",
                "message": "Update confirmation",
                "updated_fields": ["field1", "field2"],
                "updated_at": "ISO-8601 timestamp"
            }
    
    Example Usage:
        Add new tags to an existing entry:
        - entry_id: "ctx_0001"
        - tags: ["python", "fastapi", "production"]
    """
    try:
        journal = load_journal()
        entry = find_entry_by_id(journal, params.entry_id)
        
        if not entry:
            error_response = {
                "success": False,
                "error": f"Entry '{params.entry_id}' not found",
                "message": "Entry not found. Use 'list_context_entries' to see available entries."
            }
            return json.dumps(error_response, indent=2)
        
        # Track what changed
        updated_fields = []
        
        if params.title is not None:
            entry["title"] = params.title
            updated_fields.append("title")
        
        if params.context is not None:
            entry["context"] = params.context
            updated_fields.append("context")
        
        if params.tags is not None:
            entry["tags"] = params.tags
            updated_fields.append("tags")
        
        if params.notes is not None:
            entry["notes"] = params.notes
            updated_fields.append("notes")
        
        entry["updated_at"] = datetime.utcnow().isoformat()
        save_journal(journal)
        
        response = {
            "success": True,
            "entry_id": params.entry_id,
            "message": f"Entry updated successfully",
            "updated_fields": updated_fields,
            "updated_at": entry["updated_at"]
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "message": "Failed to update context entry. Please verify inputs and try again."
        }
        return json.dumps(error_response, indent=2)


@mcp.tool(
    name="delete_context_entry",
    annotations={
        "title": "Delete Context Journal Entry",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def delete_context_entry(params: DeleteEntryInput) -> str:
    """Delete a context journal entry permanently.
    
    ⚠️ WARNING: This operation cannot be undone. The entry will be permanently removed.
    Consider reading the entry first to confirm you're deleting the correct one.
    
    Args:
        params (DeleteEntryInput): Input parameters containing:
            - entry_id (str): Unique identifier of entry to delete
    
    Returns:
        str: JSON response containing:
            {
                "success": true,
                "entry_id": "deleted-entry-id",
                "message": "Deletion confirmation",
                "deleted_at": "ISO-8601 timestamp"
            }
    
    Error Handling:
        - If entry not found: Returns error with suggestion to list entries
        - Confirms successful deletion with entry ID
    
    Example Usage:
        Delete an outdated entry: entry_id="ctx_0001"
    """
    try:
        journal = load_journal()
        entry = find_entry_by_id(journal, params.entry_id)
        
        if not entry:
            error_response = {
                "success": False,
                "error": f"Entry '{params.entry_id}' not found",
                "message": "Entry not found. Use 'list_context_entries' to see available entries."
            }
            return json.dumps(error_response, indent=2)
        
        # Remove entry
        journal["entries"] = [e for e in journal["entries"] if e["id"] != params.entry_id]
        save_journal(journal)
        
        response = {
            "success": True,
            "entry_id": params.entry_id,
            "message": f"Entry '{entry['title']}' deleted successfully",
            "deleted_at": datetime.utcnow().isoformat()
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "message": "Failed to delete context entry. Please verify the entry ID."
        }
        return json.dumps(error_response, indent=2)


@mcp.tool(
    name="list_context_entries",
    annotations={
        "title": "List Context Journal Entries",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def list_context_entries(params: ListEntriesInput) -> str:
    """List all context journal entries with filtering and pagination.
    
    Browse your context journal with flexible filtering by tags and search text.
    Results are paginated to prevent overwhelming responses. Use this to discover
    relevant past context before diving into specific entries.
    
    Args:
        params (ListEntriesInput): Input parameters containing:
            - tags (Optional[List[str]]): Filter by tags (matches ANY tag)
            - search_text (Optional[str]): Search in title, context, notes
            - limit (Optional[int]): Max results (1-100, default 20)
            - offset (Optional[int]): Skip N results for pagination (default 0)
            - response_format (ResponseFormat): 'markdown' or 'json'
    
    Returns:
        str: Paginated list in requested format with:
            - Total count and filtered count
            - Entry summaries (ID, title, tags, timestamps)
            - Pagination info (has_more, next_offset)
    
    Example Usage:
        - Find Python-related entries: tags=["python"]
        - Search for API discussions: search_text="API"
        - Get next page: offset=20, limit=20
    """
    try:
        journal = load_journal()
        entries = journal["entries"]
        
        # Apply filters
        filtered = entries
        
        if params.tags:
            filtered = [e for e in filtered if any(tag in e.get("tags", []) for tag in params.tags)]
        
        if params.search_text:
            search_lower = params.search_text.lower()
            filtered = [
                e for e in filtered
                if search_lower in e["title"].lower()
                or search_lower in e["context"].lower()
                or search_lower in (e.get("notes", "") or "").lower()
                or any(search_lower in tag.lower() for tag in e.get("tags", []))
            ]
        
        # Apply pagination
        total_filtered = len(filtered)
        paginated = filtered[params.offset:params.offset + params.limit]
        has_more = (params.offset + len(paginated)) < total_filtered
        next_offset = params.offset + len(paginated) if has_more else None
        
        if params.response_format == ResponseFormat.MARKDOWN:
            output = f"# Context Journal Entries\n\n"
            output += f"**Total Entries:** {len(entries)} | **Filtered:** {total_filtered} | **Showing:** {len(paginated)}\n\n"
            
            if params.tags:
                output += f"**Filtered by tags:** {', '.join(params.tags)}\n"
            if params.search_text:
                output += f"**Search:** \"{params.search_text}\"\n"
            
            output += "\n---\n\n"
            
            for entry in paginated:
                created = datetime.fromisoformat(entry["created_at"]).strftime("%Y-%m-%d %H:%M")
                tags_str = ", ".join(entry["tags"]) if entry["tags"] else "No tags"
                output += f"### {entry['title']}\n"
                output += f"**ID:** `{entry['id']}` | **Tags:** {tags_str} | **Created:** {created}\n\n"
                # Show first 200 chars of context as preview
                preview = entry["context"][:200] + "..." if len(entry["context"]) > 200 else entry["context"]
                output += f"{preview}\n\n---\n\n"
            
            if has_more:
                output += f"\n**More results available.** Use offset={next_offset} to see next page.\n"
            
            return truncate_if_needed(output, "Use 'offset' parameter to see more results.")
        
        else:  # JSON format
            response = {
                "total_entries": len(entries),
                "filtered_count": total_filtered,
                "returned_count": len(paginated),
                "offset": params.offset,
                "limit": params.limit,
                "has_more": has_more,
                "next_offset": next_offset,
                "entries": [
                    {
                        "id": e["id"],
                        "title": e["title"],
                        "tags": e["tags"],
                        "created_at": e["created_at"],
                        "updated_at": e["updated_at"],
                        "context_preview": e["context"][:200] + "..." if len(e["context"]) > 200 else e["context"]
                    }
                    for e in paginated
                ]
            }
            return json.dumps(response, indent=2)
            
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "message": "Failed to list context entries. Please try again."
        }
        return json.dumps(error_response, indent=2)


@mcp.tool(
    name="search_context_entries",
    annotations={
        "title": "Search Context Journal Entries",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def search_context_entries(params: SearchEntriesInput) -> str:
    """Search context journal entries by query text.
    
    Full-text search across titles, context, notes, and tags. More focused than
    list_context_entries - use this when you know what you're looking for.
    
    Args:
        params (SearchEntriesInput): Input parameters containing:
            - query (str): Search query (1-200 chars)
            - response_format (ResponseFormat): 'markdown' or 'json'
    
    Returns:
        str: Matching entries in requested format with relevance ordering
    
    Example Usage:
        - Find Azure-related context: query="azure"
        - Search for FastAPI info: query="fastapi"
    """
    try:
        journal = load_journal()
        query_lower = params.query.lower()
        
        # Search and score relevance
        results = []
        for entry in journal["entries"]:
            score = 0
            
            # Title matches are most important
            if query_lower in entry["title"].lower():
                score += 10
            
            # Context matches
            if query_lower in entry["context"].lower():
                score += 5
            
            # Tag matches
            if any(query_lower in tag.lower() for tag in entry.get("tags", [])):
                score += 8
            
            # Notes matches
            if query_lower in (entry.get("notes", "") or "").lower():
                score += 3
            
            if score > 0:
                results.append((score, entry))
        
        # Sort by relevance
        results.sort(key=lambda x: x[0], reverse=True)
        entries = [entry for score, entry in results]
        
        if params.response_format == ResponseFormat.MARKDOWN:
            if not entries:
                return f"# Search Results\n\nNo entries found matching \"{params.query}\".\n\nTry:\n- Using different search terms\n- Using 'list_context_entries' to browse all entries"
            
            output = f"# Search Results: \"{params.query}\"\n\n"
            output += f"**Found:** {len(entries)} matching entries\n\n---\n\n"
            
            for entry in entries:
                output += format_entry_markdown(entry)
                output += "\n---\n\n"
            
            return truncate_if_needed(output, "Refine your search query to see more specific results.")
        
        else:  # JSON format
            response = {
                "query": params.query,
                "result_count": len(entries),
                "entries": entries
            }
            return json.dumps(response, indent=2)
            
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "message": "Failed to search context entries. Please try again."
        }
        return json.dumps(error_response, indent=2)


# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    # Run with stdio transport (default for MCP)
    mcp.run()

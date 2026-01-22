# WARNERCO Robotics Schematica - MCP Primitives

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#7c3aed', 'primaryTextColor': '#fff', 'primaryBorderColor': '#5b21b6', 'lineColor': '#6b7280', 'fontFamily': 'Inter, system-ui, sans-serif'}}}%%
flowchart TB
    subgraph Server["<b>MCP SERVER: warnerco-schematica v2.0</b>"]
        direction TB

        subgraph Tools["<b>TOOLS</b> (11) - Executable Actions"]
            direction LR

            subgraph DataTools["Data Retrieval"]
                T1["<b>warn_list_robots</b><br/>category?, model?, status?, limit"]
                T2["<b>warn_get_robot</b><br/>schematic_id"]
                T3["<b>warn_semantic_search</b><br/>query, category?, model?, top_k"]
                T4["<b>warn_memory_stats</b><br/>no params"]
            end

            subgraph ModTools["Data Modification"]
                T5["<b>warn_index_schematic</b><br/>schematic_id"]
                T6["<b>warn_compare_schematics</b><br/>id1, id2"]
            end

            subgraph CrudTools["CRUD Operations"]
                T9["<b>warn_create_schematic</b><br/>model, name, component, category, summary"]
                T10["<b>warn_update_schematic</b><br/>schematic_id, field updates"]
                T11["<b>warn_delete_schematic</b><br/>schematic_id, confirm"]
            end

            subgraph IntTools["Interactive (Elicitation)"]
                T7["<b>warn_guided_search</b><br/>ctx: Context"]
                T8["<b>warn_feedback_loop</b><br/>ctx: Context, schematic_id"]
            end
        end

        subgraph Resources["<b>RESOURCES</b> (10) - Read-Only Data"]
            direction LR

            subgraph MemRes["Memory Resources"]
                R1["<b>memory://overview</b><br/>Backend stats"]
                R2["<b>memory://recent-queries</b><br/>Query telemetry"]
                R3["<b>memory://architecture</b><br/>3-tier docs"]
            end

            subgraph CatRes["Catalog Resources"]
                R4["<b>catalog://categories</b><br/>Category list"]
                R5["<b>catalog://models</b><br/>Robot models"]
            end

            subgraph HelpRes["Help Resources"]
                R6["<b>help://tools</b><br/>Tool docs"]
                R7["<b>help://resources</b><br/>Resource docs"]
                R8["<b>help://prompts</b><br/>Prompt docs"]
            end

            subgraph MetaRes["Meta Resources"]
                R9["<b>schematic://{id}</b><br/>Template resource"]
                R10["<b>mcp://capabilities</b><br/>Full server docs"]
            end
        end

        subgraph Prompts["<b>PROMPTS</b> (5) - Reusable Templates"]
            direction LR
            P1["<b>diagnostic_prompt</b><br/>robot_id → analysis template"]
            P2["<b>comparison_prompt</b><br/>id1, id2 → comparison template"]
            P3["<b>search_strategy_prompt</b><br/>query, filters? → search guidance"]
            P4["<b>maintenance_report_prompt</b><br/>robot_model → maintenance template"]
            P5["<b>schematic_review_prompt</b><br/>schematic_id → review template"]
        end

    end

    subgraph Client["<b>MCP CLIENT</b>"]
        direction LR
        C1["Claude Desktop"]
        C2["VS Code Copilot"]
        C3["Claude Code"]
    end

    subgraph Protocol["<b>MCP PROTOCOL</b>"]
        direction TB
        STDIO["<b>stdio</b><br/>Local transport"]
        HTTP["<b>HTTP/SSE</b><br/>Remote transport"]
    end

    %% Connections
    C1 --> STDIO
    C2 --> STDIO
    C3 --> STDIO
    STDIO --> Server
    HTTP --> Server

    %% Tool returns
    DataTools -->|"Returns: Pydantic models"| C1
    ModTools -->|"Returns: Status + data"| C1
    CrudTools -->|"Returns: CRUD results"| C1
    IntTools -->|"Elicit → Submit → Return"| C1

    %% Resource access
    Resources -->|"Returns: Markdown text"| C1

    %% Prompt execution
    Prompts -->|"Returns: Formatted prompt"| C1

    %% Styling
    classDef toolBox fill:#059669,stroke:#047857,color:#fff,stroke-width:2px
    classDef resBox fill:#0284c7,stroke:#0369a1,color:#fff,stroke-width:2px
    classDef promptBox fill:#7c3aed,stroke:#6d28d9,color:#fff,stroke-width:2px
    classDef clientBox fill:#dc2626,stroke:#b91c1c,color:#fff,stroke-width:2px
    classDef protoBox fill:#475569,stroke:#334155,color:#fff,stroke-width:2px

    class T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11 toolBox
    class R1,R2,R3,R4,R5,R6,R7,R8,R9,R10 resBox
    class P1,P2,P3,P4,P5 promptBox
    class C1,C2,C3 clientBox
    class STDIO,HTTP protoBox
```

## MCP Primitives Reference

### Tools vs Resources vs Prompts

| Primitive | Purpose | Input | Output | Side Effects |
|-----------|---------|-------|--------|--------------|
| **Tool** | Execute actions | Parameters | Structured data | Yes (may modify state) |
| **Resource** | Read data | URI | Text/Markdown | No (read-only) |
| **Prompt** | Generate templates | Arguments | Formatted string | No (template only) |

### Tool Categories

#### Data Retrieval Tools
| Tool | Parameters | Returns |
|------|------------|---------|
| `warn_list_robots` | category?, model?, status?, limit | `SchematicListResult` |
| `warn_get_robot` | schematic_id | `SchematicDetail` |
| `warn_semantic_search` | query, category?, model?, top_k | `SemanticSearchResult` |
| `warn_memory_stats` | (none) | `MemoryStatsResult` |

#### Data Modification Tools
| Tool | Parameters | Returns |
|------|------------|---------|
| `warn_index_schematic` | schematic_id | `IndexResult` |
| `warn_compare_schematics` | id1, id2 | Comparison dict |

#### CRUD Tools
| Tool | Parameters | Returns |
|------|------------|---------|
| `warn_create_schematic` | model, name, component, category, summary, version?, status?, tags?, specifications?, url? | `CreateSchematicResult` |
| `warn_update_schematic` | schematic_id, model?, name?, component?, category?, summary?, version?, status?, tags?, specifications?, url? | `UpdateSchematicResult` |
| `warn_delete_schematic` | schematic_id, confirm | `DeleteSchematicResult` |

#### Interactive Tools (with Elicitation)
| Tool | Elicitation Flow | Returns |
|------|------------------|---------|
| `warn_guided_search` | Category → Model → Keywords | `GuidedSearchResult` |
| `warn_feedback_loop` | Rating + Comments form | `FeedbackResult` |

### Resource URI Schemes

| Scheme | Type | Description |
|--------|------|-------------|
| `memory://` | Static | Memory system information |
| `catalog://` | Static | Category and model catalogs |
| `help://` | Static | Self-documentation |
| `schematic://` | Template | Individual schematic documents |
| `mcp://` | Static | Server capabilities |

### Prompt Templates

| Prompt | Input | Output Purpose |
|--------|-------|----------------|
| `diagnostic_prompt` | robot_id | Guide diagnostic analysis |
| `comparison_prompt` | id1, id2 | Structure comparison review |
| `search_strategy_prompt` | query, filters? | Optimize search approach |
| `maintenance_report_prompt` | robot_model | Generate maintenance checklist |
| `schematic_review_prompt` | schematic_id | Technical review framework |

## Elicitation Pattern

```python
# Multi-step elicitation in warn_guided_search
@mcp.tool()
async def warn_guided_search(ctx: Context) -> GuidedSearchResult:
    # Step 1: Elicit category selection
    cat_result = await ctx.elicit(
        message="Select a category:",
        schema=CategorySelection
    )
    if cat_result.action != "submit":
        return cancelled_result()

    # Step 2: Elicit model selection
    model_result = await ctx.elicit(
        message="Select a robot model:",
        schema=ModelSelection
    )

    # Step 3: Elicit keywords
    kw_result = await ctx.elicit(
        message="Enter search keywords:",
        schema=KeywordInput
    )

    # Execute search with collected inputs
    return await execute_search(cat_result, model_result, kw_result)
```

## Pydantic Models

The server uses 17 Pydantic models for structured I/O:

**Output Models:**
- `SchematicSummary`, `SchematicListResult`, `SchematicDetail`
- `SearchResultItem`, `SemanticSearchResult`, `MemoryStatsResult`
- `ComparisonResult`, `IndexResult`, `GuidedSearchResult`, `FeedbackResult`
- `CreateSchematicResult`, `UpdateSchematicResult`, `DeleteSchematicResult`

**Elicitation Schemas:**
- `CategorySelection`, `ModelSelection`, `KeywordInput`, `FeedbackInput`

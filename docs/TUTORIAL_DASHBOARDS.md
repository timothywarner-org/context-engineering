# WARNERCO Schematica Dashboard Tutorial

A hands-on guide to exploring the WARNERCO Robotics Schematica system through its REST API and web dashboards.

## What You Will Learn

- How to start the Schematica server and verify it is running
- How to use the interactive OpenAPI documentation to explore and test endpoints
- How to query the REST API directly using PowerShell and curl
- How to understand the 3-tier memory architecture (JSON, Chroma, Azure AI Search)
- How to build and view the Astro static dashboards

## Prerequisites

Before starting this tutorial, ensure you have:

- **Python 3.11+** with `uv` package manager installed
- **Node.js 18+** (for building Astro dashboards)
- The repository cloned locally
- A terminal open at `C:\github\context-engineering\src\warnerco\backend`

**Verify your setup:**

```powershell
# Check Python
python --version

# Check uv
uv --version

# Check Node.js (for dashboards)
node --version
```

## Step 1: Start the HTTP Server

Navigate to the backend directory and start the FastAPI server.

**Open a terminal and run:**

```powershell
cd C:\github\context-engineering\src\warnerco\backend
uv sync
uv run uvicorn app.main:app --reload
```

**Expected output:**

```
Starting WARNERCO Robotics Schematica...
Memory Backend: json
Debug Mode: True
Loaded 25 schematics
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx]
```

> **Tip:** The `--reload` flag enables auto-reload during development. The server will restart automatically when you modify Python files.

**Quick verification:**

Open your browser and navigate to http://localhost:8000. You should see either the dashboard (if built) or a JSON response showing available endpoints.

## Step 2: Explore the OpenAPI Documentation

FastAPI automatically generates interactive API documentation. This is your primary tool for understanding and testing the API.

### 2.1 Open the Swagger UI

Navigate to: **http://localhost:8000/docs**

You will see the Swagger UI with all available endpoints organized by tags:

| Tag | Purpose |
|-----|---------|
| **System** | Health check and system status |
| **Robots** | CRUD operations for robot schematics |
| **Search** | Semantic search functionality |
| **Memory** | Memory backend statistics and telemetry |
| **Metadata** | Categories and models for filtering |

### 2.2 Understanding the Interface

The Swagger UI provides:

1. **Endpoint list** - All available routes grouped by tag
2. **Method indicators** - GET, POST, PUT, DELETE with color coding
3. **Request/Response schemas** - Click any endpoint to see expected input/output
4. **"Try it out" button** - Execute requests directly from the browser

### 2.3 Try It Out: Health Check

Let's test the health endpoint directly from Swagger:

1. Click on **GET /api/health** under the "System" tag
2. Click the **Try it out** button
3. Click **Execute**

**Expected response:**

```json
{
  "status": "healthy",
  "backend": "json",
  "timestamp": "2025-01-21T10:30:00.000000",
  "version": "1.0.0"
}
```

This confirms your server is running and shows which memory backend is active.

### 2.4 Try It Out: List Robots

1. Expand **GET /api/robots** under "Robots"
2. Click **Try it out**
3. Leave all parameters empty for now
4. Click **Execute**

You will see a paginated list of all 25 robot schematics. Note the response structure:

```json
{
  "items": [...],
  "total": 25,
  "offset": 0,
  "limit": 100
}
```

### 2.5 Try It Out: Semantic Search

1. Expand **POST /api/search** under "Search"
2. Click **Try it out**
3. Replace the request body with:

```json
{
  "query": "precision manipulation",
  "filters": {},
  "top_k": 5
}
```

4. Click **Execute**

The response includes relevance scores and optional reasoning from the LangGraph flow.

> **Why this approach?** The OpenAPI documentation provides a zero-config way to explore APIs. You do not need to install Postman or write code - just click and test.

## Step 3: Using the REST API Directly (PowerShell)

While Swagger UI is convenient for exploration, you will often need to call APIs from scripts or terminals.

### 3.1 Health Check

```powershell
# Simple GET request
Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get | ConvertTo-Json
```

**Expected output:**

```json
{
  "status": "healthy",
  "backend": "json",
  "timestamp": "2025-01-21T10:30:00.000000",
  "version": "1.0.0"
}
```

### 3.2 List All Robots

```powershell
# List all robots (default pagination)
Invoke-RestMethod -Uri "http://localhost:8000/api/robots" -Method Get | ConvertTo-Json -Depth 5
```

**Filter by category:**

```powershell
# List only sensor schematics
Invoke-RestMethod -Uri "http://localhost:8000/api/robots?category=sensors" -Method Get | ConvertTo-Json -Depth 5
```

**Filter by status:**

```powershell
# List only active schematics
Invoke-RestMethod -Uri "http://localhost:8000/api/robots?status=active" -Method Get | ConvertTo-Json -Depth 5
```

### 3.3 Get a Specific Robot

```powershell
# Get details for a specific schematic
Invoke-RestMethod -Uri "http://localhost:8000/api/robots/WRN-00001" -Method Get | ConvertTo-Json -Depth 3
```

**Expected output:**

```json
{
  "id": "WRN-00001",
  "model": "WC-100",
  "name": "Atlas Prime",
  "component": "force feedback sensor array",
  "version": "v3.4",
  "summary": "High-precision force sensing system for WC-100 manipulation tasks...",
  "url": "https://schematics.warnerco.io/wc-100/force_feedback_sensor_v3_4.pdf",
  "last_verified": "2025-01-15",
  "category": "sensors",
  "status": "active",
  "tags": ["manipulation", "precision", "feedback"],
  "specifications": {
    "resolution": "0.1N",
    "range": "0-500N",
    "response_time": "2ms"
  }
}
```

### 3.4 Perform Semantic Search

```powershell
# Semantic search with POST request
$body = @{
    query = "precision manipulation"
    filters = @{}
    top_k = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/search" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body | ConvertTo-Json -Depth 5
```

**Alternative using curl (if available):**

```powershell
curl -X POST "http://localhost:8000/api/search" `
    -H "Content-Type: application/json" `
    -d '{"query": "precision manipulation", "filters": {}, "top_k": 5}'
```

**Expected response structure:**

```json
{
  "results": [
    {
      "schematic": { ... },
      "score": 0.89,
      "chunk_id": "WRN-00001"
    }
  ],
  "query": "precision manipulation",
  "total": 5,
  "query_time_ms": 45.2,
  "reasoning": "The query focuses on precision handling. Returning schematics related to manipulation, grippers, and force feedback systems."
}
```

### 3.5 Get Available Categories and Models

```powershell
# List all categories
Invoke-RestMethod -Uri "http://localhost:8000/api/categories" -Method Get

# List all robot models
Invoke-RestMethod -Uri "http://localhost:8000/api/models" -Method Get
```

## Step 4: Memory System Exploration

The Schematica system uses a 3-tier memory architecture. Understanding this helps you optimize searches and troubleshoot issues.

### 4.1 Check Memory Statistics

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/memory/stats" -Method Get | ConvertTo-Json -Depth 3
```

**Expected output:**

```json
{
  "backend": "json",
  "total_schematics": 25,
  "indexed_count": 0,
  "chunk_count": 0,
  "categories": {
    "sensors": 5,
    "manipulation": 4,
    "power": 3,
    "thermal": 3,
    "mobility": 4,
    "communication": 3,
    "actuators": 3
  },
  "status_counts": {
    "active": 20,
    "deprecated": 3,
    "draft": 2
  }
}
```

### 4.2 Understanding the 3-Tier Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Memory Backend Tiers                        │
├─────────────────────────────────────────────────────────────────┤
│  Tier 1: JSON Store                                             │
│  ├── Fastest startup                                            │
│  ├── Keyword search only                                        │
│  ├── No indexing required                                       │
│  └── Best for: Development, small datasets                      │
├─────────────────────────────────────────────────────────────────┤
│  Tier 2: Chroma (Local Vector Store)                            │
│  ├── Semantic search with embeddings                            │
│  ├── Requires indexing schematics first                         │
│  ├── Uses local embedding model                                 │
│  └── Best for: Local development with semantic search           │
├─────────────────────────────────────────────────────────────────┤
│  Tier 3: Azure AI Search                                        │
│  ├── Enterprise-grade semantic search                           │
│  ├── Scalable to millions of documents                          │
│  ├── Requires Azure subscription                                │
│  └── Best for: Production deployments                           │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Switching Memory Backends

Create or edit `.env` in the backend directory:

```powershell
# Edit environment configuration
notepad C:\github\context-engineering\src\warnerco\backend\.env
```

Set the `MEMORY_BACKEND` variable:

```
# Options: json, chroma, azure_search
MEMORY_BACKEND=chroma
```

Restart the server to apply changes.

### 4.4 View Query Telemetry

After performing searches, you can view recent query history:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/memory/hits?limit=10" -Method Get | ConvertTo-Json -Depth 3
```

This shows:

- Query text
- Results returned
- Duration in milliseconds
- Which backend was used

### 4.5 Index Schematics (for Chroma/Azure)

If using Chroma or Azure AI Search, you must index schematics before semantic search works:

```powershell
# Index a single schematic
Invoke-RestMethod -Uri "http://localhost:8000/api/robots/WRN-00001/index" -Method Post

# Index all schematics
Invoke-RestMethod -Uri "http://localhost:8000/api/robots/index-all" -Method Post | ConvertTo-Json
```

**Expected response:**

```json
{
  "success": true,
  "indexed_count": 25,
  "message": "Indexed 25 schematics"
}
```

## Step 5: Building and Viewing Astro Dashboards

The Schematica system includes pre-built Astro dashboards for visual exploration.

### 5.1 Check if Dashboards Are Built

The dashboards should already be built and available at `/dash/`. Try navigating to:

**http://localhost:8000/dash/**

If you see the dashboard, skip to section 5.3.

### 5.2 Build the Dashboards (If Needed)

If the dashboards are not available or you want to rebuild them:

```powershell
# Navigate to dashboards directory
cd C:\github\context-engineering\src\warnerco\dashboards

# Install dependencies
npm install

# Build static files (outputs to ../backend/static/dash)
npm run build
```

**Expected output:**

```
> warnerco-dashboards@1.0.0 build
> astro build

21:30:00 [build] output: "static"
21:30:00 [build] Compiling pages...
21:30:02 [build] Completed in 1.8s
21:30:02 [build] 3 page(s) built in 2.1s
```

The built files are automatically placed in `../backend/static/dash`, which FastAPI serves at `/dash/`.

### 5.3 Dashboard Tour

The dashboards provide three main views:

#### Home Dashboard (http://localhost:8000/dash/)

- Overview of the Schematica system
- Quick links to Schematics and Memory dashboards
- Feature highlights: Semantic Search, LangGraph Orchestration, MCP Integration
- Quick reference for API endpoints and MCP tools

#### Schematics Dashboard (http://localhost:8000/dash/schematics/)

| Feature | Description |
|---------|-------------|
| **Search bar** | Natural language semantic search |
| **Filters** | Category, Model, Status dropdowns |
| **Stats cards** | Total, Active, Indexed, Categories counts |
| **Schematic cards** | Visual cards with status indicators |
| **Index buttons** | Index individual schematics for semantic search |
| **Index All** | Batch index all schematics |

**Try this:**

1. Type "thermal sensors for heavy-duty robots" in the search bar
2. Click Search
3. View the results panel with relevance scores

#### Memory Dashboard (http://localhost:8000/dash/memory/)

| Feature | Description |
|---------|-------------|
| **Backend indicator** | Shows active memory backend |
| **Stats cards** | Total, Indexed, Chunks counts |
| **Category chart** | Distribution by category |
| **Status chart** | Active/Deprecated/Draft breakdown |
| **Index coverage** | Progress bar showing indexing status |
| **Recent queries** | Table of recent search queries with timing |
| **Auto-refresh** | Toggle for live updates |

**Try this:**

1. Enable "Auto-refresh" checkbox
2. In another terminal, perform a search via API
3. Watch the Recent Queries table update automatically

### 5.4 Development Mode (Optional)

For dashboard development with hot reload:

```powershell
# Terminal 1: Run the FastAPI backend
cd C:\github\context-engineering\src\warnerco\backend
uv run uvicorn app.main:app --reload

# Terminal 2: Run Astro dev server
cd C:\github\context-engineering\src\warnerco\dashboards
npm run dev
```

The Astro dev server runs on http://localhost:4321 and proxies API requests to the FastAPI backend at port 8000.

## Troubleshooting

### Server Will Not Start

**Symptom:** `ModuleNotFoundError` or `ImportError`

**Fix:**

```powershell
cd C:\github\context-engineering\src\warnerco\backend
uv sync --reinstall
```

### Port Already in Use

**Symptom:** `Address already in use`

**Fix:**

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

### Semantic Search Returns No Results

**Symptom:** Search queries return empty results

**Cause:** Schematics not indexed (when using Chroma or Azure AI Search)

**Fix:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/robots/index-all" -Method Post
```

### Dashboard Shows "Loading..." Forever

**Symptom:** Schematics page stuck on loading spinner

**Cause:** API requests failing (CORS, server not running, etc.)

**Fix:**

1. Verify the server is running: http://localhost:8000/api/health
2. Check browser console for errors (F12 > Console)
3. Verify you are accessing via http://localhost:8000/dash/ (not file://)

### Chroma Errors on Startup

**Symptom:** `chromadb` import errors or database locked

**Fix:**

```powershell
# Delete existing Chroma data
Remove-Item -Recurse -Force C:\github\context-engineering\src\warnerco\backend\data\chroma

# Restart server
uv run uvicorn app.main:app --reload
```

## Summary

You have now learned how to:

1. Start the WARNERCO Schematica server
2. Use Swagger UI at `/docs` to explore and test endpoints
3. Call the REST API from PowerShell
4. Understand the 3-tier memory architecture
5. Build and navigate the Astro dashboards
6. Troubleshoot common issues

## Next Steps

- Explore the MCP tools in Claude Desktop (see `CLAUDE.md` for configuration)
- Try the LangGraph flow with different query types
- Deploy to Azure using the scripts in `scripts/`
- Customize the dashboards in `src/warnerco/dashboards/`

---

**Author**: Tim Warner
**Repository**: [github.com/timothywarner/context-engineering](https://github.com/timothywarner/context-engineering)
**Last Updated**: 2025-01-21

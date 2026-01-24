"""Main FastAPI application for WARNERCO Robotics Schematica."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

from app.api import router as api_router
from app.config import settings
from app.mcp_tools import mcp


def get_cors_origins() -> list[str]:
    """Get CORS origins from environment or use defaults.

    In production, set CORS_ORIGINS to a comma-separated list of allowed origins.
    Example: CORS_ORIGINS=https://app.example.com,https://admin.example.com

    Falls back to ["*"] only in development (when debug=True).
    """
    cors_env = os.environ.get("CORS_ORIGINS", "")
    if cors_env:
        return [origin.strip() for origin in cors_env.split(",") if origin.strip()]
    # Only allow wildcard in development mode
    if settings.debug:
        return ["*"]
    # Production default: no origins (CORS will block cross-origin requests)
    return []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print(f"Starting WARNERCO Robotics Schematica...")
    print(f"Memory Backend: {settings.memory_backend.value}")
    print(f"Debug Mode: {settings.debug}")

    # Initialize memory backend
    from app.adapters import get_memory_store
    memory = get_memory_store()
    stats = await memory.get_memory_stats()
    print(f"Loaded {stats.total_schematics} schematics")

    yield

    # Shutdown
    print("Shutting down WARNERCO Robotics Schematica...")


# Create FastAPI app
app = FastAPI(
    title="WARNERCO Robotics Schematica",
    description="Agentic robot schematics system with semantic memory",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware - configure CORS_ORIGINS env var for production
cors_origins = get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Mount FastMCP at /mcp
app.mount("/mcp", mcp.http_app())

# Static files paths
STATIC_DIR = Path(__file__).parent.parent / "static"
DASH_DIR = STATIC_DIR / "dash"
ASSETS_DIR = STATIC_DIR / "assets"


# Mount static directories if they exist
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

if DASH_DIR.exists():
    app.mount("/dash", StaticFiles(directory=str(DASH_DIR), html=True), name="dash")


# Root redirect to dashboard
@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to dashboard or return API info."""
    if (DASH_DIR / "index.html").exists():
        return RedirectResponse(url="/dash/")
    return {
        "name": "WARNERCO Robotics Schematica",
        "version": "1.0.0",
        "api_docs": "/docs",
        "mcp_endpoint": "/mcp",
        "dashboard": "/dash/",
    }


# Favicon
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve favicon."""
    favicon_path = ASSETS_DIR / "favicon.svg"
    if favicon_path.exists():
        return FileResponse(str(favicon_path), media_type="image/svg+xml")
    raise HTTPException(status_code=404, detail="Favicon not found")


def run_server():
    """Run the HTTP server (entry point for poetry/uv scripts)."""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run_server()

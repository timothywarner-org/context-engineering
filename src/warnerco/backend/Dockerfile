# WARNERCO Robotics Schematica - Production Dockerfile
# Simplified for Azure Container Registry build

FROM python:3.11-slim

# Install system dependencies (build tools for some pip packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies using pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY static ./static
COPY data ./data

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000
ENV MEMORY_BACKEND=chroma
# FastMCP HTTP transport is mounted at /mcp in app.main
ENV MCP_HTTP_BASE_PATH=/mcp

# Expose port
EXPOSE 8000

# Health check (REST API)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import sys,urllib.request; \
    sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3).status==200 else 1)" || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]

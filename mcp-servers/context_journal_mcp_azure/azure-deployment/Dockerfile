# Dockerfile for Context Journal MCP Server
# Optimized for Azure Container Apps deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements-azure.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-azure.txt

# Copy application code
COPY context_journal_mcp_azure.py .

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Expose port for HTTP transport (if using HTTP instead of stdio)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the MCP server
# For stdio transport (default):
CMD ["python", "context_journal_mcp_azure.py"]

# For HTTP transport (uncomment if needed):
# CMD ["python", "-c", "from context_journal_mcp_azure import mcp; mcp.run(transport='streamable_http', port=8000, host='0.0.0.0')"]

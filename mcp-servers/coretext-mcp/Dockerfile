# ============================================================
# CoreText MCP - Production Dockerfile for Azure Container Apps
# ============================================================
# Multi-stage build for minimal image size and security
# ============================================================

# ============================================================
# Stage 1: Dependencies
# ============================================================
FROM node:20-alpine AS deps

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install production dependencies only
RUN npm ci --only=production && \
    npm cache clean --force

# ============================================================
# Stage 2: Production Runtime
# ============================================================
FROM node:20-alpine

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps --chown=nodejs:nodejs /app/node_modules ./node_modules

# Copy application source
COPY --chown=nodejs:nodejs package*.json ./
COPY --chown=nodejs:nodejs src/ ./src/

# Create data directory for fallback storage
RUN mkdir -p /app/data && chown nodejs:nodejs /app/data

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Use dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]

# Start the server
CMD ["node", "src/index.js"]

# ============================================================
# Build & Run Instructions:
#
# Build:
#   docker build -t coretext-mcp:latest .
#
# Local Test:
#   docker run -p 3000:3000 \
#     -e DEEPSEEK_API_KEY=your_key \
#     coretext-mcp:latest
# ============================================================

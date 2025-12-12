# ============================================================
# Stoic MCP - Production Dockerfile for Azure Container Apps
# ============================================================
# Multi-stage build for minimal image size and security
# ============================================================

# ============================================================
# Stage 1: Build TypeScript
# ============================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies (including dev dependencies for TypeScript)
RUN npm install

# Copy source code
COPY src/ ./src/
COPY quotes.json ./quotes.json

# Build TypeScript
RUN npm run build

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

# Copy only production dependencies
COPY package*.json ./
RUN npm install --only=production && \
    npm cache clean --force

# Copy compiled JavaScript from builder
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/quotes.json ./quotes.json

# Create quotes-source directory (for bulk imports)
RUN mkdir -p /app/quotes-source && chown nodejs:nodejs /app/quotes-source

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
CMD ["node", "dist/index.js"]

# ============================================================
# Build & Run Instructions:
#
# Build:
#   cd stoic-mcp/local
#   docker build -t stoic-mcp:latest .
#
# Local Test:
#   docker run -p 3000:3000 \
#     -e DEEPSEEK_API_KEY=your_key \
#     stoic-mcp:latest
# ============================================================

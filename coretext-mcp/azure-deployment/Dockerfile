# CoreText MCP - Azure Container Apps Dockerfile
# Optimized for production deployment with minimal image size

FROM node:20-alpine AS base

# Install production dependencies only
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY src/ ./src/

# Create data directory for JSON storage
RUN mkdir -p /app/data

# Set environment variables
ENV NODE_ENV=production
ENV HEALTH_PORT=3001

# Health check for Container Apps
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3001/health', (r) => { process.exit(r.statusCode === 200 ? 0 : 1); })"

# Run as non-root user for security
USER node

# Expose health endpoint port
EXPOSE 3001

# Start the MCP server
CMD ["node", "src/index.js"]

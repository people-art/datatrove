# Frontend Dockerfile for FineData Next.js application (Development)
FROM node:20-alpine

# Install libc6-compat and curl for Next.js and health checks
RUN apk add --no-cache libc6-compat curl

# Create app directory
WORKDIR /app

# Create non-root user first
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci && npm cache clean --force

# Copy source code
COPY . .

# Create next-env.d.ts if it doesn't exist
RUN touch /app/next-env.d.ts 2>/dev/null || true

# Set environment variables
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV development

# Create necessary directories and set permissions
RUN mkdir -p /app/.next && \
    chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 3000

# Default command (can be overridden in docker-compose)
CMD ["npm", "run", "dev"]

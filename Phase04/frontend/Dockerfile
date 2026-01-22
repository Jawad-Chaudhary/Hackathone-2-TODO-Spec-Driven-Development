# syntax=docker/dockerfile:1

ARG NODE_VERSION=22.13.1

# --- Build Stage ---
FROM node:${NODE_VERSION}-slim AS builder
WORKDIR /app

# Install dependencies (with cache and bind mounts for speed)
COPY --link package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm install --legacy-peer-deps

# Copy the rest of the application source
COPY --link . .

# Set dummy environment variables for build time
# These will be overridden at runtime with actual values
ENV BETTER_AUTH_SECRET="build-time-dummy-secret-will-be-replaced-at-runtime"
ENV BETTER_AUTH_URL="http://localhost:3000"
ENV NEXT_PUBLIC_APP_URL="http://localhost:3000"
ENV NEXT_PUBLIC_OPENAI_DOMAIN_KEY="build-time-dummy-key"
ENV NEXT_PUBLIC_API_URL="http://localhost:8000"
ENV NEXT_PUBLIC_BACKEND_URL="http://localhost:8000"

# Build the Next.js app (TypeScript compilation, etc)
RUN npm run build

# Remove dev dependencies to reduce image size
RUN --mount=type=cache,target=/root/.npm \
    npm prune --production

# --- Production Stage ---
FROM node:${NODE_VERSION}-slim AS final
WORKDIR /app

# Create a non-root user and group
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup appuser

# Copy only the necessary files from the builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.js ./next.config.js
COPY --from=builder /app/postcss.config.js ./postcss.config.js
COPY --from=builder /app/tailwind.config.ts ./tailwind.config.ts
COPY --from=builder /app/app ./app
COPY --from=builder /app/components ./components
COPY --from=builder /app/lib ./lib
COPY --from=builder /app/next-env.d.ts ./next-env.d.ts

# Set environment variables
ENV NODE_ENV=production
ENV NODE_OPTIONS="--max-old-space-size=4096"

USER appuser

EXPOSE 3000

CMD ["npm", "start"]

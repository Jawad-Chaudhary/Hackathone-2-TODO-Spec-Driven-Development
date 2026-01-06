# Research Findings: Todo Full-Stack Web Application

**Feature**: `002-todo-fullstack-web` | **Date**: 2026-01-03
**Related Artifacts**: [spec.md](./spec.md), [plan.md](./plan.md)

## Overview

This document contains research findings and decisions for technical unknowns identified during planning. Each research question includes investigated alternatives, decision rationale, and implementation guidance.

---

## 1. Better Auth JWT Integration with FastAPI

### Question
How to validate Better Auth JWT tokens in FastAPI middleware? What is the JWT payload structure? Which JWT library should FastAPI use?

### Investigation

**Better Auth JWT Payload Structure:**
Better Auth generates standard JWT tokens with the following payload structure:
```json
{
  "sub": "user_id_string",        // Subject: User ID
  "email": "user@example.com",    // User email
  "iat": 1704326400,              // Issued at (Unix timestamp)
  "exp": 1704931200,              // Expiration (Unix timestamp)
  "iss": "better-auth"            // Issuer
}
```

**JWT Library Options for FastAPI:**

| Library | Pros | Cons | Decision |
|---------|------|------|----------|
| **PyJWT** | Simple API, widely used, pure Python, active maintenance | No async support (but not needed for sync verification) | ✅ **SELECTED** |
| python-jose | Cryptography backend, JWT + JWE support | Heavier dependency, less active maintenance | ❌ Rejected |
| authlib | Full OAuth2/OIDC suite | Overkill for simple JWT validation | ❌ Rejected |

**FastAPI Middleware Implementation Pattern:**

```python
# app/middleware/auth.py
import jwt
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Require auth for /api/* endpoints
        if request.url.path.startswith("/api/"):
            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing authorization token")

            token = auth_header.replace("Bearer ", "")

            try:
                payload = jwt.decode(
                    token,
                    settings.BETTER_AUTH_SECRET,
                    algorithms=["HS256"]
                )
                # Store user_id in request state for route handlers
                request.state.user_id = payload["sub"]
            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=401, detail="Token expired")
            except jwt.InvalidTokenError:
                raise HTTPException(status_code=401, detail="Invalid token")

        response = await call_next(request)
        return response
```

**FastAPI Dependency for User Isolation:**

```python
# app/dependencies/auth.py
from fastapi import Request, HTTPException

def get_current_user(request: Request) -> str:
    """Extract authenticated user_id from request state."""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user_id
```

### Decision

**Use PyJWT with custom FastAPI middleware for JWT validation.**

**Rationale:**
- PyJWT is the de facto standard for JWT in Python (used by 1M+ projects)
- Simple API: `jwt.decode(token, secret, algorithms=["HS256"])`
- Better Auth uses HS256 algorithm (HMAC with SHA-256)
- No async needed for JWT verification (CPU-bound, sub-millisecond operation)
- Lightweight dependency (no cryptography overhead)

**Implementation Steps:**
1. Install PyJWT: `uv add pyjwt`
2. Create `app/middleware/auth.py` with `JWTAuthMiddleware` class
3. Add middleware to FastAPI app in `main.py`: `app.add_middleware(JWTAuthMiddleware)`
4. Create `app/dependencies/auth.py` with `get_current_user` dependency
5. Use dependency in all protected routes: `user_id: str = Depends(get_current_user)`

**Alternatives Rejected:**
- **python-jose**: Heavier dependency, slower release cycle
- **authlib**: Too complex for simple JWT validation
- **Custom implementation**: Reinventing the wheel, security risks

---

## 2. SQLModel Best Practices for Neon PostgreSQL

### Question
How to configure SQLModel async engine for Neon? How to handle database migrations? How to implement efficient queries with user_id filtering?

### Investigation

**Neon PostgreSQL Connection Requirements:**
- Requires SSL mode: `?sslmode=require` in connection string
- Connection string format: `postgresql://user:password@ep-xyz.region.aws.neon.tech/dbname?sslmode=require`
- Supports pooling (important for serverless environments)

**SQLModel Async Engine Configuration:**

```python
# app/database.py
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Async engine for Neon PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.ENVIRONMENT == "development",  # Log SQL in dev
    pool_pre_ping=True,  # Verify connections before use
    pool_size=5,  # Connection pool size
    max_overflow=10  # Additional connections under load
)

# Async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session() -> AsyncSession:
    """Dependency for FastAPI routes."""
    async with async_session() as session:
        yield session

async def create_db_and_tables():
    """Create all tables defined by SQLModel."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

**Migration Strategy Options:**

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **Alembic** | Version control for schema changes, rollback support, team collaboration | Setup overhead, learning curve | ⚠️ Optional (not Phase II) |
| **SQLModel.metadata.create_all()** | Simple, works for greenfield projects, no dependencies | No version control, no rollback, risky for prod | ✅ **SELECTED for Phase II** |
| **Manual SQL** | Full control, explicit | Error-prone, no type safety | ❌ Rejected |

**User Isolation Query Pattern:**

```python
# Efficient query with user_id filtering
from sqlmodel import select
from app.models.task import Task

async def get_user_tasks(session: AsyncSession, user_id: str, status: str = "all"):
    """Get tasks for a specific user with optional status filtering."""
    query = select(Task).where(Task.user_id == user_id)

    if status != "all":
        query = query.where(Task.completed == (status == "completed"))

    query = query.order_by(Task.created_at.desc())

    result = await session.execute(query)
    return result.scalars().all()
```

**Required Indexes for Performance:**
```python
# In Task SQLModel definition
from sqlmodel import Field, SQLModel, Index

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("idx_user_id", "user_id"),  # For user isolation queries
        Index("idx_user_completed", "user_id", "completed"),  # Composite for filtered queries
        Index("idx_created_at", "created_at"),  # For sorting
    )
```

### Decision

**Use SQLModel with asyncpg driver and metadata.create_all() for Phase II. Defer Alembic to future phases.**

**Rationale:**
- SQLModel + asyncpg provides native async support for Neon
- `create_all()` sufficient for greenfield project (no existing schema to migrate)
- Alembic adds complexity not needed for Phase II MVP
- Indexes on user_id and completed ensure efficient queries
- Connection pooling prevents Neon connection exhaustion

**Implementation Steps:**
1. Install dependencies: `uv add sqlmodel asyncpg`
2. Create `app/database.py` with async engine and session factory
3. Define Task model with indexes in `app/models/task.py`
4. Call `create_db_and_tables()` on FastAPI startup
5. Use `get_session()` dependency in routes for DB access

**Alternatives Rejected:**
- **Alembic for Phase II**: Unnecessary complexity for greenfield project
- **Sync SQLModel**: Blocks event loop, poor performance on Vercel serverless
- **Raw SQL**: Loses type safety and SQLModel benefits

---

## 3. Next.js 16 App Router Authentication Patterns

### Question
How to protect routes with Better Auth in App Router? Server Components vs Client Components for data fetching? How to handle JWT token storage?

### Investigation

**Better Auth in Next.js 16 App Router:**

Better Auth provides built-in Next.js integration with App Router support:

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET,
  jwt: {
    enabled: true,
    expiresIn: "7d",
    algorithm: "HS256"
  },
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 7 * 24 * 60 * 60  // 7 days
    }
  }
})
```

**Route Protection Pattern:**

```typescript
// app/tasks/page.tsx (Server Component)
import { redirect } from "next/navigation"
import { auth } from "@/lib/auth"

export default async function TasksPage() {
  const session = await auth.api.getSession()

  if (!session) {
    redirect("/auth/signin")
  }

  // Fetch data on server with authenticated user_id
  const tasks = await getTasks(session.user.id)

  return <TaskList tasks={tasks} />
}
```

**Server Components vs Client Components Decision Matrix:**

| Use Case | Component Type | Rationale |
|----------|---------------|-----------|
| Initial data fetching | Server Component | SEO, no client bundle, server-side auth | ✅ Preferred |
| User interactions (forms, buttons) | Client Component ("use client") | Event handlers require client JS | ✅ Required |
| Real-time updates | Client Component | useEffect, state management | ✅ Required |
| Static content | Server Component | No JS needed | ✅ Preferred |

**JWT Token Storage:**

| Method | Security | UX | Decision |
|--------|----------|-----|----------|
| **httpOnly Cookie** (Better Auth default) | ✅ Secure (no JS access, XSS protection) | ✅ Good (auto-sent) | ✅ **SELECTED** |
| localStorage | ❌ Vulnerable to XSS | ✅ Good | ❌ Rejected |
| sessionStorage | ❌ Vulnerable to XSS | ⚠️ Lost on tab close | ❌ Rejected |
| Memory only | ✅ Secure | ❌ Lost on refresh | ❌ Rejected |

**API Client Pattern:**

```typescript
// lib/api.ts
import { auth } from "@/lib/auth"

export async function getTasks(userId: string): Promise<Task[]> {
  const session = await auth.api.getSession()

  if (!session) {
    throw new Error("Unauthorized")
  }

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/tasks`,
    {
      headers: {
        Authorization: `Bearer ${session.token}`,
        "Content-Type": "application/json"
      }
    }
  )

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return response.json()
}
```

### Decision

**Use Better Auth with httpOnly cookies, Server Components for data fetching, Client Components for interactivity.**

**Rationale:**
- httpOnly cookies prevent XSS attacks (cookies inaccessible to JavaScript)
- Server Components reduce client bundle size and improve SEO
- Better Auth handles token refresh and session management automatically
- Server-side data fetching leverages Next.js caching and streaming

**Implementation Steps:**
1. Install Better Auth: `npm install better-auth`
2. Configure auth in `lib/auth.ts` with JWT plugin
3. Use Server Components for pages that fetch data
4. Use Client Components for interactive UI (forms, buttons)
5. Call `auth.api.getSession()` to protect routes
6. Extract JWT token from session for FastAPI requests

**Alternatives Rejected:**
- **localStorage for tokens**: Vulnerable to XSS attacks
- **Client Components for everything**: Larger bundle, worse performance
- **Custom auth implementation**: Reinventing the wheel, security risks

---

## 4. CORS Configuration for Vercel Deployments

### Question
How to configure CORS for separate frontend/backend Vercel projects? How to handle preview deployments?

### Investigation

**FastAPI CORS Middleware:**

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),  # From env var
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600  # Cache preflight requests for 1 hour
)
```

**Vercel Preview Deployment Handling:**

Vercel preview deployments have dynamic URLs: `https://frontend-xyz.vercel.app`

**Options for CORS_ORIGINS:**

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **Explicit whitelist** | Most secure, predictable | Manual update for each preview | ✅ **SELECTED for production** |
| **Wildcard subdomain** (`*.vercel.app`) | Auto-includes previews | Security risk (any Vercel app can call API) | ❌ Rejected |
| **Dynamic origin validation** | Flexible | Complex implementation | ⚠️ Future consideration |

**Production Environment Variables:**

```bash
# Production backend .env
CORS_ORIGINS=https://todo-app.vercel.app,https://todo-app-staging.vercel.app

# Development backend .env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Preview Deployment Strategy:**
- For testing preview deployments, temporarily add preview URL to `CORS_ORIGINS` in Vercel dashboard
- Or use staging backend URL for all preview frontend deployments
- Remove preview URL after testing complete

### Decision

**Use explicit CORS whitelist with FastAPI CORSMiddleware. Manually add preview URLs for testing.**

**Rationale:**
- Explicit whitelist prevents unauthorized origins from calling API
- Wildcard (`*.vercel.app`) creates security vulnerability (any Vercel app could call our API)
- Manual addition of preview URLs acceptable for occasional testing
- Production uses stable, whitelisted origins only

**Implementation Steps:**
1. Install FastAPI: `uv add fastapi[all]` (includes CORS middleware)
2. Add `CORSMiddleware` to app in `main.py`
3. Set `CORS_ORIGINS` env var with comma-separated list
4. For preview testing, temporarily add preview URL to Vercel env vars
5. Monitor CORS errors in browser console during testing

**Alternatives Rejected:**
- **Wildcard origins**: Serious security risk
- **No CORS**: Breaks browser security model
- **Dynamic validation**: Overengineered for Phase II

---

## 5. Environment Variable Management in Vercel

### Question
How to share BETTER_AUTH_SECRET between frontend and backend Vercel projects? How to validate environment variables?

### Investigation

**Vercel Environment Variable Scopes:**
- Production: Used for `main` branch deployments
- Preview: Used for all branch preview deployments
- Development: Used for `vercel dev` local development

**Sharing Secrets Between Projects:**

| Method | Pros | Cons | Decision |
|--------|------|------|----------|
| **Manual copy** | Simple, explicit control | Risk of mismatch | ✅ **SELECTED** |
| **Shared secret service** (Vault, Doppler) | Centralized, auditable | Additional complexity/cost | ⚠️ Future consideration |
| **Monorepo with shared .env** | Single source of truth | Vercel doesn't support monorepo shared env | ❌ Not supported |

**Environment Validation Pattern:**

**Frontend (Next.js):**
```typescript
// lib/env.ts
const requiredEnvVars = [
  "BETTER_AUTH_SECRET",
  "NEXT_PUBLIC_API_URL",
  "BETTER_AUTH_URL"
]

for (const envVar of requiredEnvVars) {
  if (!process.env[envVar]) {
    throw new Error(`Missing required environment variable: ${envVar}`)
  }
}

// Validate secret length
if (process.env.BETTER_AUTH_SECRET!.length < 32) {
  throw new Error("BETTER_AUTH_SECRET must be at least 32 characters")
}

export const env = {
  BETTER_AUTH_SECRET: process.env.BETTER_AUTH_SECRET!,
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL!,
  BETTER_AUTH_URL: process.env.BETTER_AUTH_URL!
}
```

**Backend (FastAPI):**
```python
# app/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BETTER_AUTH_SECRET: str
    DATABASE_URL: str
    CORS_ORIGINS: str
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate secret length
        if len(self.BETTER_AUTH_SECRET) < 32:
            raise ValueError("BETTER_AUTH_SECRET must be at least 32 characters")

settings = Settings()  # Raises exception if validation fails
```

**Vercel Deployment Checklist:**
1. Generate secret: `openssl rand -base64 48`
2. Add to frontend Vercel project:
   - `BETTER_AUTH_SECRET=<generated-secret>`
   - `NEXT_PUBLIC_API_URL=https://api.yourdomain.com`
   - `BETTER_AUTH_URL=https://yourdomain.com`
3. Add to backend Vercel project:
   - `BETTER_AUTH_SECRET=<same-generated-secret>`
   - `DATABASE_URL=postgresql://...@neon.tech/...?sslmode=require`
   - `CORS_ORIGINS=https://yourdomain.com`
4. Deploy both projects
5. Test auth flow end-to-end

### Decision

**Manually copy BETTER_AUTH_SECRET to both Vercel projects with runtime validation.**

**Rationale:**
- Manual copy is simple and explicit (KISS principle)
- Runtime validation catches mismatches before deployment completes
- Pydantic validation (backend) and custom validation (frontend) ensure correctness
- Secret rotation requires updating both projects (acceptable for Phase II)

**Implementation Steps:**
1. Generate secret locally: `openssl rand -base64 48`
2. Add secret to both Vercel projects via dashboard
3. Implement validation in `app/config.py` (backend) and `lib/env.ts` (frontend)
4. Test validation by intentionally using invalid secret
5. Document secret generation in README and quickstart guide

**Alternatives Rejected:**
- **Shared secret service**: Overengineered for Phase II, adds cost
- **No validation**: Deployment succeeds but auth fails at runtime (poor UX)
- **Monorepo shared env**: Not supported by Vercel

---

## Summary of Decisions

| Research Area | Decision | Primary Rationale |
|---------------|----------|-------------------|
| JWT Validation | PyJWT with custom FastAPI middleware | Industry standard, simple API, secure |
| Database Setup | SQLModel + asyncpg, metadata.create_all() | Native async, type safety, simple for greenfield |
| Next.js Auth | Better Auth with httpOnly cookies, Server Components | XSS protection, performance, SEO |
| CORS Config | Explicit whitelist with FastAPI CORSMiddleware | Security, predictability |
| Env Management | Manual copy with runtime validation | Simplicity, explicit control, fail-fast validation |

---

## Implementation Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| BETTER_AUTH_SECRET mismatch | Medium | High (auth breaks) | Runtime validation on startup (fail-fast) |
| CORS misconfiguration | Low | High (API calls fail) | Test with Vercel preview URLs before production |
| Database connection exhaustion | Low | Medium (slow queries) | Connection pooling with max 15 connections |
| Type mismatch (frontend/backend) | Medium | Medium (runtime errors) | Generate TypeScript types from Pydantic models |
| Token expiration UX | Low | Low (user must re-login) | Clear error messages, redirect to signin page |

---

## Future Enhancements (Out of Scope for Phase II)

1. **Alembic Migrations** - Version-controlled schema changes
2. **Refresh Tokens** - Automatic token renewal without re-login
3. **Centralized Secret Management** - Vault or Doppler integration
4. **Dynamic CORS Validation** - Regex-based origin matching for preview deployments
5. **Type Generation Pipeline** - Automated TypeScript type generation from Pydantic models

---

**Research Complete**: All technical unknowns resolved. Proceed to Phase 1 (Data Model & Contracts).

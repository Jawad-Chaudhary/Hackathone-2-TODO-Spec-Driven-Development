---
id: 0003
title: create-todo-fullstack-plan
stage: plan
date: 2026-01-03
surface: agent
model: claude-sonnet-4-5
feature: 002-todo-fullstack-web
branch: 002-todo-fullstack-web
user: jawad
command: /sp.plan
labels: ["planning", "architecture", "fullstack", "nextjs", "fastapi", "postgresql"]
links:
  spec: ../specs/002-todo-fullstack-web/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-todo-fullstack-web/plan.md
  - specs/002-todo-fullstack-web/research.md
  - specs/002-todo-fullstack-web/data-model.md
  - specs/002-todo-fullstack-web/quickstart.md
  - specs/002-todo-fullstack-web/contracts/auth.openapi.yaml
  - specs/002-todo-fullstack-web/contracts/tasks.openapi.yaml
tests:
  - Manual testing checklist in quickstart.md (no automated tests in Phase II)
---

## Prompt

Create a detailed technical plan for: Todo Full-Stack Web Application

**Architecture Overview:**
```
┌─────────────────────────────────────────────────────────────┐
│                    BROWSER (Client)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Next.js App (Port 3000)                            │   │
│  │  ├── Auth Pages (Better Auth)                       │   │
│  │  ├── Task List (Server Components)                  │   │
│  │  └── API Client (fetch with JWT)                    │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────┬─────────────────────────────────────────┘
                    │ HTTPS
                    ▼
┌─────────────────────────────────────────────────────────────┐
│         FastAPI Backend (Port 8000)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  JWT Middleware (validates Better Auth tokens)      │   │
│  │  Task CRUD Endpoints (/api/{user_id}/tasks)         │   │
│  │  User Isolation (filter by JWT user_id)             │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────┬─────────────────────────────────────────┘
                    │ SQL (asyncpg)
                    ▼
┌─────────────────────────────────────────────────────────────┐
│         Neon PostgreSQL (Serverless)                        │
│  ├── users table (Better Auth managed)                     │
│  ├── tasks table (user_id FK, title, description, etc.)    │
│  └── Indexes: user_id, completed, created_at               │
└─────────────────────────────────────────────────────────────┘
```

Generate the complete technical plan document.

## Response snapshot

**Planning Session Completed Successfully**

Generated comprehensive implementation plan with all required artifacts:

### 1. plan.md (Main Planning Document)
- **Technical Context**: Fully specified (no NEEDS CLARIFICATION markers)
  - Frontend: TypeScript 5.0+, Next.js 16+, React 19, Tailwind CSS 3.0+
  - Backend: Python 3.13+, FastAPI 0.100+, SQLModel 0.0.14+, PyJWT, uvicorn
  - Database: Neon PostgreSQL serverless with async engine
  - Package managers: npm/pnpm (frontend), UV (backend)

- **Constitution Check**: ✅ ALL GATES PASSED
  - Core Principles: 7/7 compliant (Spec-Driven, Clean Architecture, Stateless Backend, User Isolation, Type Safety, Security First, Simplicity)
  - Technology Stack: 10/10 compliant (all required technologies approved)
  - Architecture Standards: 6/6 compliant (API pattern, CORS, status codes, etc.)
  - Environment Configuration: 5/5 compliant (no .env commits, startup validation, etc.)

- **Project Structure**: Defined for monorepo with separate /frontend and /backend
  - Backend: app/ (main.py, config.py, database.py, models/, schemas/, routes/, middleware/, dependencies/)
  - Frontend: app/ (Next.js App Router structure), components/ (ui/, tasks/, auth/), lib/ (api.ts, auth.ts, types.ts)

- **Complexity Tracking**: Zero violations requiring justification

### 2. research.md (Phase 0 Deliverable)
**5 Research Areas Resolved:**

1. **Better Auth JWT Integration with FastAPI**
   - Decision: Use PyJWT with custom FastAPI middleware
   - Rationale: Industry standard, simple API, secure HS256 algorithm
   - JWT payload structure documented from Better Auth

2. **SQLModel Best Practices for Neon PostgreSQL**
   - Decision: SQLModel + asyncpg, metadata.create_all() for Phase II
   - Rationale: Native async, type safety, simple for greenfield project
   - Alembic migrations deferred to future phases

3. **Next.js 16 App Router Authentication Patterns**
   - Decision: Better Auth with httpOnly cookies, Server Components for data fetching
   - Rationale: XSS protection, performance, SEO benefits
   - Client Components only for interactivity (forms, buttons)

4. **CORS Configuration for Vercel Deployments**
   - Decision: Explicit whitelist with FastAPI CORSMiddleware
   - Rationale: Security (prevents unauthorized origins), predictability
   - Manual addition of preview URLs for testing

5. **Environment Variable Management in Vercel**
   - Decision: Manual copy with runtime validation
   - Rationale: Simplicity (KISS principle), fail-fast validation
   - Pydantic validation (backend), custom validation (frontend)

### 3. data-model.md (Phase 1 Deliverable)
**Entities:**
- **User** (managed by Better Auth): id, email, name, created_at
- **Task** (custom): id, user_id (FK), title, description, completed, created_at, updated_at

**Relationships:**
- User → Tasks (one-to-many with CASCADE delete)

**Indexes:**
- idx_user_id (B-tree on user_id) - user isolation queries
- idx_user_completed (composite) - filtered queries
- idx_created_at - sorting optimization

**Constraints:**
- Foreign key: tasks.user_id → users.id (CASCADE)
- Check: title length 1-200, description length ≤1000
- Not null: user_id, title, completed, timestamps

**SQLModel and Pydantic schemas fully specified with code examples**

### 4. API Contracts (Phase 1 Deliverable)
**auth.openapi.yaml:**
- POST /api/auth/signup (registration)
- POST /api/auth/signin (authentication)
- POST /api/auth/logout (session termination)

**tasks.openapi.yaml:**
- GET /api/{user_id}/tasks (list with filtering)
- POST /api/{user_id}/tasks (create)
- GET /api/{user_id}/tasks/{task_id} (read single)
- PUT /api/{user_id}/tasks/{task_id} (update)
- DELETE /api/{user_id}/tasks/{task_id} (delete)

**All endpoints fully documented with:**
- Request/response schemas
- Validation examples
- Error responses (401, 404, 422, 500)
- Bearer authentication requirement

### 5. quickstart.md (Phase 1 Deliverable)
**Complete setup guide covering:**

**Prerequisites:**
- Required software: Node.js 20+, Python 3.13+, UV, Git
- Required accounts: Neon PostgreSQL, Vercel

**Local Development:**
- Backend setup (UV, .env, dependencies, server startup)
- Frontend setup (npm/pnpm, .env.local, dependencies, dev server)
- Health checks and verification steps

**Manual Testing:**
- 7 detailed test scenarios: registration, login, create task, mark complete, update, delete, user isolation
- SQL verification queries for Neon console
- Security test with curl for user isolation

**Deployment:**
- Backend to Vercel (environment variables, CORS configuration)
- Frontend to Vercel (environment variables, build settings)
- Post-deployment verification

**Troubleshooting:**
- 5 common issues with solutions (auth token, CORS, database connection, token expiration, 404 errors)
- Environment variables reference table
- Useful commands for development and debugging

## Outcome

- ✅ Impact: Complete technical plan ready for task generation (/sp.tasks) and implementation (/sp.implement)
- 🧪 Tests: Manual testing strategy defined with 7 test scenarios in quickstart.md
- 📁 Files: 6 files created (plan.md, research.md, data-model.md, quickstart.md, 2 OpenAPI specs)
- 🔁 Next prompts: Run /sp.tasks to generate implementation tasks based on this plan
- 🧠 Reflection: Planning phase completed successfully with zero constitutional violations. All technical unknowns resolved through research. Data model and API contracts fully specified with OpenAPI 3.1.0 schemas. Ready for task breakdown and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None - all planning artifacts generated successfully on first attempt
- Graders run and results (PASS/FAIL):
  - Constitution Check: PASS (all 7 principles, all technology stack requirements, all architecture standards)
  - Technical Context Completeness: PASS (no NEEDS CLARIFICATION markers remaining)
  - Research Depth: PASS (5 areas investigated with decisions, rationale, alternatives rejected)
  - Data Model Clarity: PASS (entities, relationships, indexes, constraints fully specified)
  - API Contract Completeness: PASS (8 endpoints with full OpenAPI 3.1.0 schemas)
  - Quickstart Usability: PASS (prerequisites, setup, testing, deployment, troubleshooting all documented)
- Prompt variant (if applicable): Standard /sp.plan workflow with user-provided architecture diagram
- Next experiment (smallest change to try): None - process worked as designed. For future: Consider auto-generating TypeScript types from Pydantic schemas during planning phase.

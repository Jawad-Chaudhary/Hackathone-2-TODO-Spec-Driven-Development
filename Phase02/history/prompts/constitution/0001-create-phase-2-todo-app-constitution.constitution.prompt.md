---
id: 0001
title: Create Phase 2 Todo App Constitution
stage: constitution
date: 2026-01-03
surface: agent
model: claude-sonnet-4-5
feature: none
branch: 001-phase-1-todo-cli
user: user
command: /sp.constitution
labels: ["constitution", "phase-2", "full-stack", "governance", "principles"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - history/prompts/constitution/0001-create-phase-2-todo-app-constitution.constitution.prompt.md
tests:
  - N/A (documentation only)
---

## Prompt

Create a constitution for Phase II: Todo Full-Stack Web Application with the following principles and constraints:

**Project Context:**
Evolving a console-based Todo app into a full-stack multi-user web application with persistent storage and authentication.

**Core Principles:**
1. Spec-Driven Development - No manual coding allowed; all implementation must be generated through Claude Code based on refined specifications
2. Clean Architecture - Separation of concerns between frontend, backend, and data layers
3. Stateless Backend - RESTful API design with JWT-based authentication
4. User Isolation - Each user can only access their own tasks
5. Type Safety - Use TypeScript for frontend, Pydantic models for backend
6. Security First - JWT tokens, environment-based secrets, proper CORS configuration

**Technology Stack Constraints:**
- Frontend: Next.js 16+ (App Router only), TypeScript, Tailwind CSS
- Backend: Python 3.13+, FastAPI, SQLModel ORM
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth with JWT plugin
- Package Manager: UV for Python, npm/pnpm for Node.js

**Architecture Standards:**
1. Monorepo structure with /frontend and /backend directories
2. RESTful API with /api/{user_id}/* endpoints
3. JWT tokens in Authorization: Bearer <token> headers
4. Environment variables for all secrets and configuration
5. Better Auth frontend <-> FastAPI backend JWT verification
6. Shared secret (BETTER_AUTH_SECRET) between frontend and backend

**Environment Configuration Standards:**
1. Separate .env files for local and deployment
2. Never commit .env files to version control
3. Use .env.example as template with dummy values
4. Support multiple environments: development, staging, production
5. CORS origins must support both local (localhost:3000) and deployed URLs
6. All API keys and secrets in environment variables
7. Validate required environment variables on app startup

**Code Standards:**
1. All API responses must be JSON
2. Use Pydantic models for request/response validation
3. HTTP status codes: 200 (success), 201 (created), 401 (unauthorized), 404 (not found), 422 (validation error)
4. Error handling with HTTPException in FastAPI
5. Server components by default in Next.js; client components only when needed
6. No inline styles - Tailwind CSS only

**Feature Requirements:**
Basic Level functionality:
1. Add Task - Create new todo items with title and description
2. Delete Task - Remove tasks from the list
3. Update Task - Modify existing task details
4. View Task List - Display all tasks with status indicators
5. Mark as Complete - Toggle task completion status
6. User Authentication - Signup/Signin with Better Auth

**Non-Functional Requirements:**
1. Responsive UI design
2. API response time < 500ms for CRUD operations
3. Secure password handling (Better Auth manages this)
4. Proper error messages for users
5. Loading states in UI

**Deliverables Structure:**
```
hackathon-todo/
├── .spec-kit/
│   └── config.yaml
├── specs/
│   ├── overview.md
│   ├── architecture.md
│   ├── features/
│   ├── api/
│   ├── database/
│   └── ui/
├── CLAUDE.md (root)
├── frontend/
│   ├── CLAUDE.md
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
├── backend/
│   ├── CLAUDE.md
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   ├── db.py
│   └── pyproject.toml
├── docker-compose.yml
└── README.md
```

**Deployment Targets:**
- Frontend: Vercel
- Backend: Vercel or Railway
- Database: Neon Serverless PostgreSQL (free tier)

Generate the constitution that enforces these principles throughout the development lifecycle.

## Response snapshot

Created comprehensive constitution (v1.0.0) for Phase II Todo Full-Stack Web Application with 7 core principles:

**Core Principles Established:**
1. Spec-Driven Development (NON-NEGOTIABLE) - All implementation through Claude Code
2. Clean Architecture - Strict layer separation
3. Stateless Backend - JWT-based, no server-side sessions
4. User Isolation (SECURITY CRITICAL) - Per-user data access only
5. Type Safety - TypeScript + Pydantic throughout
6. Security First - JWT, env vars, CORS, HTTPS
7. Simplicity and Pragmatism - Start simple, justify complexity

**Additional Sections:**
- Technology Stack Requirements (mandatory components + prohibited technologies)
- Architecture Standards (monorepo structure, API contracts, auth flow)
- Environment Configuration (required vars, file rules, startup validation)
- Code Quality Standards (Python/TypeScript file structure, examples, error handling)
- Feature Delivery Requirements (MVP features, acceptance criteria, definition of done)
- Non-Functional Requirements (performance, reliability, security, usability)
- Deployment Architecture (local dev with Docker Compose, production on Vercel/Railway/Neon)
- Governance (constitution authority, amendment process, compliance review, tooling)

**Key Technical Details:**
- API pattern: `VERB /api/{user_id}/<resource>` with JWT-based authorization
- Shared secret: `BETTER_AUTH_SECRET` between frontend and backend
- Status codes: 200/201/400/401/404/422/500
- Performance targets: <500ms API response, <200KB bundle, <3s TTI
- Security: User isolation via JWT claims, 404 for unauthorized (not 403)

**Template Compatibility:**
✅ plan-template.md - Constitution Check section compatible
✅ spec-template.md - Requirements alignment compatible
✅ tasks-template.md - Task categorization compatible

Constitution is now ready to guide all Phase II development through spec-driven workflow.

## Outcome

- ✅ Impact: Established comprehensive governance framework for Phase II full-stack Todo app development
- 🧪 Tests: N/A (documentation artifact)
- 📁 Files: Created constitution.md (v1.0.0) with 7 principles, technology stack, architecture standards, code quality guidelines, and governance rules
- 🔁 Next prompts: Ready for /sp.specify to create feature specifications aligned with constitution
- 🧠 Reflection: Constitution successfully translates hackathon requirements into enforceable development principles, ensuring spec-driven workflow, security-first approach, and clean architecture throughout Phase II

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution creation successful on first attempt
- Graders run and results (PASS/FAIL): Manual validation PASS - all placeholders filled, 7 principles defined, governance rules clear
- Prompt variant (if applicable): N/A (initial constitution)
- Next experiment (smallest change to try): Create first feature specification using /sp.specify to validate constitution's practical applicability

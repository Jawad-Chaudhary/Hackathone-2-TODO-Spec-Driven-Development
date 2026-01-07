<!--
Sync Impact Report:
- Version change: (new) → 1.0.0
- Modified principles: N/A (initial creation)
- Added sections:
  * Core Principles (7 principles)
  * Technology Stack Requirements
  * Architecture Standards
  * Environment Configuration
  * Code Quality Standards
  * Feature Delivery Requirements
  * Non-Functional Requirements
  * Governance
- Removed sections: None
- Templates requiring updates:
  ✅ plan-template.md - Constitution Check section compatible
  ✅ spec-template.md - Requirements alignment compatible
  ✅ tasks-template.md - Task categorization compatible
- Follow-up TODOs: None
-->

# Todo Full-Stack Web Application - Phase II Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

All implementation MUST be generated through Claude Code based on refined specifications. Manual coding is strictly prohibited.

**Rules:**
- NO manual file creation or editing outside of Claude Code workflow
- ALL code generation flows through specification artifacts (spec.md, plan.md, tasks.md)
- Specifications MUST be complete and unambiguous before implementation begins
- Changes to code require corresponding specification updates first

**Rationale:** Ensures traceability, reproducibility, and alignment between intent and implementation. Prevents drift between documentation and code.

### II. Clean Architecture

Strict separation of concerns between frontend, backend, and data layers is mandatory.

**Rules:**
- Frontend MUST NOT contain business logic; UI rendering and user interaction only
- Backend MUST NOT contain presentation logic; API contracts and business rules only
- Data layer MUST be accessed exclusively through repository/service patterns
- No direct database queries in API route handlers
- Each layer communicates through well-defined interfaces

**Rationale:** Enables independent testing, parallel development, and technology stack evolution without cascading changes.

### III. Stateless Backend

Backend services MUST be stateless; all session state resides in JWT tokens.

**Rules:**
- NO server-side session storage (Redis, in-memory, etc.)
- ALL authentication state encoded in JWT tokens
- User identity derived exclusively from validated JWT claims
- API endpoints MUST be idempotent where applicable
- No reliance on request ordering or server affinity

**Rationale:** Horizontal scalability, simplified deployment, zero-downtime updates, and cloud-native architecture compatibility.

### IV. User Isolation (SECURITY CRITICAL)

Each user MUST only access their own data; cross-user data leakage is a critical security failure.

**Rules:**
- ALL database queries MUST filter by authenticated user_id from JWT token
- NO endpoints may accept user_id as a request parameter for data access
- Backend MUST validate user_id from JWT matches requested resource ownership
- Return 404 (not 403) for unauthorized access to prevent information disclosure
- Implement automated tests verifying user isolation for every data endpoint

**Rationale:** Protects user privacy, prevents unauthorized access, and ensures regulatory compliance (GDPR, etc.).

### V. Type Safety

Strong typing is mandatory across the entire stack to prevent runtime errors.

**Rules:**
- Frontend: TypeScript strict mode enabled; no `any` types without explicit justification
- Backend: Pydantic models for all request/response payloads; SQLModel for database schemas
- NO unvalidated JSON parsing; all data MUST pass through typed schemas
- Type definitions shared between frontend and backend where possible (OpenAPI, TypeScript types from Pydantic)
- CI MUST fail on type errors

**Rationale:** Catches errors at compile time, improves IDE support, reduces debugging time, and serves as living documentation.

### VI. Security First

Security is a foundational requirement, not an add-on feature.

**Rules:**
- JWT tokens MUST be signed with BETTER_AUTH_SECRET (minimum 32 characters, cryptographically random)
- ALL secrets in environment variables; NEVER hardcoded
- CORS configured explicitly; NO `Access-Control-Allow-Origin: *` in production
- HTTPS required for all production deployments
- Passwords MUST be hashed (Better Auth handles this); never stored in plaintext
- SQL injection prevention via parameterized queries (SQLModel handles this)
- XSS prevention via React's automatic escaping and Content-Security-Policy headers
- Environment validation on app startup; fail fast if required secrets missing

**Rationale:** Prevents common vulnerabilities (OWASP Top 10), protects user data, and ensures regulatory compliance.

### VII. Simplicity and Pragmatism

Start simple; add complexity only when justified by measurable need.

**Rules:**
- NO premature optimization; working code first, performance tuning after measurement
- NO frameworks/libraries without clear justification documented in ADR
- Prefer boring, proven technologies over bleeding-edge experiments
- Remove unused code immediately; no "we might need this later" retention
- Refactoring requires spec update and explicit approval
- Each PR/task MUST solve exactly one problem

**Rationale:** Reduces cognitive load, accelerates development, minimizes bugs, and lowers maintenance burden.

## Technology Stack Requirements

**Mandatory Stack Components:**

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Frontend Framework | Next.js | 16+ | App Router for server components, file-based routing, optimal performance |
| Frontend Language | TypeScript | 5.0+ | Type safety principle enforcement |
| Frontend Styling | Tailwind CSS | 3.0+ | Utility-first CSS, no inline styles, rapid UI development |
| Backend Framework | FastAPI | 0.100+ | Async support, automatic OpenAPI, Pydantic integration |
| Backend Language | Python | 3.13+ | Modern syntax, performance improvements, type hints |
| ORM | SQLModel | 0.0.14+ | Pydantic integration, type safety, async support |
| Database | Neon PostgreSQL | Serverless | Free tier, zero-config, automatic backups |
| Authentication | Better Auth | Latest | JWT plugin support, secure defaults, Next.js integration |
| Python Package Manager | UV | Latest | Fast, deterministic, modern dependency resolution |
| Node Package Manager | npm or pnpm | Latest | Lockfile for reproducible builds |

**Prohibited Technologies:**
- NO custom authentication implementations (use Better Auth)
- NO ORMs other than SQLModel (Prisma, TypeORM, raw SQL)
- NO CSS-in-JS libraries (styled-components, emotion)
- NO pages directory in Next.js (App Router only)
- NO class components in React (function components with hooks only)

## Architecture Standards

### Monorepo Structure

```
/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── specs/             # Specification artifacts
├── history/           # PHRs and ADRs
├── .spec-kit/         # SpecKit configuration
├── docker-compose.yml # Local development environment
└── README.md          # Project overview
```

### API Contract Standards

**Endpoint Pattern:** `VERB /api/{user_id}/<resource>`

**Rules:**
- `{user_id}` in URL is for routing/logging ONLY; NEVER trust it for authorization
- Authorization MUST use `user_id` from validated JWT token
- All endpoints return JSON (no HTML, XML, plain text)
- Use standard HTTP methods: GET (read), POST (create), PUT (update), DELETE (delete)
- Idempotent operations: PUT/DELETE (safe to retry)

**Status Codes:**
- `200 OK` - Successful GET/PUT/DELETE
- `201 Created` - Successful POST
- `400 Bad Request` - Client error (malformed request)
- `401 Unauthorized` - Missing or invalid JWT token
- `404 Not Found` - Resource not found OR user not authorized (prevents information disclosure)
- `422 Unprocessable Entity` - Validation error (Pydantic)
- `500 Internal Server Error` - Server error (log stack trace, return generic message)

### Authentication Flow

**Better Auth (Frontend) ↔ FastAPI (Backend):**

1. User signs up/in via Better Auth UI components (frontend)
2. Better Auth generates JWT token signed with `BETTER_AUTH_SECRET`
3. Frontend stores token in httpOnly cookie (Better Auth handles this)
4. Frontend includes token in `Authorization: Bearer <token>` header for API calls
5. FastAPI middleware validates JWT signature using shared `BETTER_AUTH_SECRET`
6. FastAPI extracts `user_id` from validated token claims
7. API handlers use `user_id` for database queries (user isolation)

**Shared Secret:** `BETTER_AUTH_SECRET` MUST be identical in frontend and backend `.env` files.

## Environment Configuration

### Required Environment Variables

**Frontend (.env.local):**
```bash
BETTER_AUTH_SECRET=<32+ character random string>
BETTER_AUTH_URL=http://localhost:3000  # Production: https://yourdomain.com
NEXT_PUBLIC_API_URL=http://localhost:8000  # Production: https://api.yourdomain.com
```

**Backend (.env):**
```bash
BETTER_AUTH_SECRET=<same as frontend>
DATABASE_URL=postgresql://user:password@host:5432/dbname  # Neon connection string
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Environment File Rules

1. **NEVER commit `.env` files** - Add to `.gitignore`
2. **DO commit `.env.example`** - Template with dummy values
3. **Validate on startup** - App MUST crash if required variables missing
4. **Support multiple environments** - `.env.local`, `.env.staging`, `.env.production`
5. **CORS origins** - Comma-separated list supporting both local and deployed URLs
6. **Secrets rotation** - Document process in runbook (not yet implemented)

### Startup Validation Example

**Backend (FastAPI):**
```python
# main.py
import os
from fastapi import FastAPI

REQUIRED_ENV_VARS = ["BETTER_AUTH_SECRET", "DATABASE_URL", "CORS_ORIGINS"]

for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        raise RuntimeError(f"Missing required environment variable: {var}")

app = FastAPI()
```

## Code Quality Standards

### Python (Backend)

**File Structure:**
```
backend/
├── main.py              # FastAPI app initialization, middleware
├── models.py            # SQLModel database schemas
├── routes/
│   ├── __init__.py
│   ├── tasks.py         # Task CRUD endpoints
│   └── auth.py          # Auth status endpoints (if needed)
├── db.py                # Database connection, session management
├── middleware/
│   └── auth.py          # JWT validation middleware
└── pyproject.toml       # UV dependencies
```

**Code Standards:**
- Pydantic models for ALL request/response schemas
- SQLModel for ALL database tables
- HTTPException for error handling (never raise generic exceptions)
- Async functions for database operations (`async def`, `await`)
- Type hints on ALL function signatures
- Docstrings for public APIs (Google style)

**Example:**
```python
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from models import Task, TaskCreate, TaskUpdate
from db import get_session

router = APIRouter()

@router.get("/api/{user_id}/tasks", response_model=List[Task])
async def get_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user),  # From JWT
    session: Session = Depends(get_session)
):
    """Get all tasks for the authenticated user."""
    if current_user_id != user_id:
        raise HTTPException(status_code=404, detail="Not found")

    statement = select(Task).where(Task.user_id == current_user_id)
    tasks = session.exec(statement).all()
    return tasks
```

### TypeScript (Frontend)

**File Structure:**
```
frontend/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home page
│   ├── tasks/
│   │   └── page.tsx         # Task list page
│   └── auth/
│       ├── signin/
│       │   └── page.tsx     # Sign-in page
│       └── signup/
│           └── page.tsx     # Sign-up page
├── components/
│   ├── TaskList.tsx         # Task list component
│   ├── TaskForm.tsx         # Create/update task form
│   └── Header.tsx           # App header with auth status
├── lib/
│   ├── api.ts               # API client functions
│   └── types.ts             # TypeScript types
└── package.json
```

**Code Standards:**
- Server Components by default; Client Components (`"use client"`) only for interactivity
- NO `any` types; use `unknown` if type truly unknown, then narrow
- API calls in Server Components (data fetching) or Server Actions (mutations)
- Loading states for async operations
- Error boundaries for error handling
- Tailwind classes ONLY (no inline styles, no CSS modules)

**Example:**
```typescript
// app/tasks/page.tsx (Server Component)
import { TaskList } from '@/components/TaskList';
import { getTasks } from '@/lib/api';

export default async function TasksPage() {
  const tasks = await getTasks();  // Fetch on server

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">My Tasks</h1>
      <TaskList tasks={tasks} />
    </div>
  );
}
```

### Error Handling

**Backend:**
```python
from fastapi import HTTPException

# User-facing errors (validation, not found, unauthorized)
raise HTTPException(status_code=404, detail="Task not found")

# System errors (log stack trace, return generic message)
try:
    result = await db_operation()
except Exception as e:
    logger.exception("Database operation failed")
    raise HTTPException(status_code=500, detail="Internal server error")
```

**Frontend:**
```typescript
// lib/api.ts
export async function getTasks(): Promise<Task[]> {
  const response = await fetch('/api/tasks');

  if (!response.ok) {
    if (response.status === 401) {
      redirect('/auth/signin');
    }
    throw new Error('Failed to fetch tasks');
  }

  return response.json();
}
```

## Feature Delivery Requirements

### Basic Level Functionality (MVP)

**MUST-HAVE Features:**

1. **Add Task** - Create new todo items with title and description
   - API: `POST /api/{user_id}/tasks`
   - Input: `{ title: string, description?: string }`
   - Validation: Title required, max 200 chars; description optional, max 1000 chars

2. **Delete Task** - Remove tasks from the list
   - API: `DELETE /api/{user_id}/tasks/{task_id}`
   - Authorization: User MUST own the task (user_id match)

3. **Update Task** - Modify existing task details
   - API: `PUT /api/{user_id}/tasks/{task_id}`
   - Input: `{ title?: string, description?: string, completed?: boolean }`
   - Validation: Same as Add Task

4. **View Task List** - Display all tasks with status indicators
   - API: `GET /api/{user_id}/tasks`
   - Response: Array of tasks sorted by created_at DESC
   - UI: Show title, completion status, created date

5. **Mark as Complete** - Toggle task completion status
   - API: `PUT /api/{user_id}/tasks/{task_id}` with `{ completed: true/false }`
   - UI: Checkbox or toggle button

6. **User Authentication** - Signup/Signin with Better Auth
   - Better Auth handles: User creation, password hashing, JWT generation
   - UI: Sign-up form (email, password, confirm password)
   - UI: Sign-in form (email, password)
   - Protected routes: Redirect to sign-in if not authenticated

### Feature Acceptance Criteria

**Each feature MUST have:**
- API endpoint documented in `specs/api/` with request/response schemas
- UI mockup or description in `specs/ui/`
- Acceptance scenarios in Given-When-Then format (spec.md)
- Implementation tasks in tasks.md
- Manual test plan (automated tests optional for Phase II)

**Definition of Done:**
- Feature works in local development environment
- Error handling implemented and tested
- User cannot access other users' data (user isolation verified)
- UI is responsive (mobile, tablet, desktop)
- No console errors in browser or server logs

## Non-Functional Requirements

### Performance

- **API Response Time:** < 500ms for CRUD operations (p95)
- **Database Queries:** Use indexes on `user_id` and `created_at` columns
- **Frontend Bundle Size:** < 200KB gzipped for initial load
- **Time to Interactive:** < 3 seconds on 3G connection

**Measurement:** Use browser DevTools Network tab and FastAPI logging middleware.

### Reliability

- **Error Recovery:** Display user-friendly error messages; log technical details server-side
- **Data Validation:** Pydantic MUST validate all inputs; return 422 with field-level errors
- **Graceful Degradation:** If API unavailable, show cached data (if implemented) or offline message

### Security

- **Password Handling:** Better Auth MUST hash passwords (bcrypt or argon2); never log passwords
- **Token Expiration:** JWT tokens expire after 24 hours (configurable in Better Auth)
- **HTTPS Only:** Production MUST use HTTPS; NO mixed content
- **SQL Injection:** SQLModel parameterized queries prevent this (no raw SQL)
- **XSS:** React automatic escaping prevents this (no `dangerouslySetInnerHTML` without justification)

### Usability

- **Responsive Design:** UI MUST work on mobile (320px+), tablet (768px+), desktop (1024px+)
- **Loading States:** Show spinner or skeleton UI during async operations
- **Error Messages:** User-facing errors MUST be actionable (e.g., "Email already exists" not "Error 409")
- **Accessibility:** Semantic HTML, ARIA labels for screen readers (WCAG 2.1 Level A minimum)

## Deployment Architecture

### Local Development

**Docker Compose Setup:**
```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: ./backend/.env
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    env_file: ./frontend/.env.local
    depends_on:
      - backend

  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: devpassword
    ports:
      - "5432:5432"
```

**Commands:**
- `docker-compose up` - Start all services
- `docker-compose down` - Stop all services
- `docker-compose logs -f backend` - Follow backend logs

### Production Deployment

**Targets:**

| Component | Platform | Configuration |
|-----------|----------|---------------|
| Frontend | Vercel | Auto-deploy from `main` branch; environment variables in Vercel dashboard |
| Backend | Vercel or Railway | Docker container; environment variables in platform dashboard |
| Database | Neon PostgreSQL | Free tier; connection string in backend env vars |

**Pre-Deployment Checklist:**
1. All environment variables set in platform dashboards
2. `BETTER_AUTH_SECRET` matches between frontend and backend
3. `CORS_ORIGINS` includes production frontend URL
4. Database migrations applied (if schema changed)
5. HTTPS enabled and enforced
6. Error monitoring configured (optional: Sentry, LogRocket)

**Deployment Process:**
1. Merge PR to `main` branch
2. Vercel auto-deploys frontend (if configured)
3. Manually trigger backend deploy on Railway/Vercel
4. Verify deployment: Check health endpoints, test auth flow, test CRUD operations
5. Monitor error logs for 24 hours post-deployment

## Governance

### Constitution Authority

This constitution supersedes all other development practices, coding standards, and architectural decisions. When conflicts arise:

1. Constitution principles take precedence
2. Architecture Decision Records (ADRs) justify deviations (requires explicit approval)
3. Emergency hotfixes may bypass process but MUST be documented post-facto

### Amendment Process

**Minor Amendments (Patch Version):**
- Clarifications, typo fixes, non-semantic wording changes
- Approval: Single reviewer (project lead or senior developer)
- Process: Update constitution, commit with message `docs: constitution v1.0.1 - clarify <topic>`

**Major Amendments (Minor/Major Version):**
- New principles, removed principles, significant redefinitions
- Approval: Team consensus (all developers) or project stakeholder sign-off
- Process:
  1. Propose change via ADR (document rationale, alternatives, impact)
  2. Review ADR in team meeting
  3. Update constitution and increment version
  4. Update dependent templates (plan, spec, tasks)
  5. Communicate changes to all developers
  6. Create migration guide if existing code affected

### Compliance Review

**When Required:**
- Before merging any PR
- During spec review (before implementation starts)
- During retrospectives (identify systematic violations)

**Review Checklist:**
1. Spec-driven development: Is implementation based on approved spec?
2. Clean architecture: Are frontend/backend/data layers properly separated?
3. User isolation: Do all queries filter by authenticated user_id?
4. Type safety: Are TypeScript/Pydantic types used throughout?
5. Security: Are secrets in env vars? Is CORS configured? Is JWT validated?
6. Simplicity: Is complexity justified by measurable need?

**Violation Handling:**
- **Blocking violations** (security, user isolation): Reject PR immediately
- **Non-blocking violations** (style, simplicity): Request changes, merge with tech debt ticket
- **Systematic violations**: Update constitution or improve tooling/documentation

### Tooling and Automation

**Constitution Enforcement:**
- TypeScript strict mode (compiler enforces type safety)
- Pydantic validation (runtime enforces schema compliance)
- ESLint/Prettier (enforces code style)
- Pre-commit hooks (future: run linters, type checks)
- CI/CD pipeline (future: automated testing, deployment gates)

**Living Documentation:**
- Constitution MUST be referenced in `CLAUDE.md` (AI agent instructions)
- Templates (spec, plan, tasks) MUST include constitution check sections
- ADRs MUST reference specific constitution principles affected
- PHRs (Prompt History Records) MUST document constitution compliance

### Version History

**Current Version:** 1.0.0

**Changelog:**
- **1.0.0** (2026-01-03): Initial constitution for Phase II Todo Full-Stack Web Application
  - 7 core principles established
  - Technology stack defined (Next.js, FastAPI, Neon PostgreSQL, Better Auth)
  - Architecture standards documented (monorepo, API contracts, auth flow)
  - Environment configuration standards defined
  - Code quality standards specified
  - Feature requirements and NFRs documented
  - Deployment architecture outlined

**Version**: 1.0.0 | **Ratified**: 2026-01-03 | **Last Amended**: 2026-01-03

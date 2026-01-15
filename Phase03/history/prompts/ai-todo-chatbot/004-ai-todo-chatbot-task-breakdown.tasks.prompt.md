---
id: 004
title: AI Todo Chatbot Task Breakdown
stage: tasks
date: 2026-01-13
surface: agent
model: claude-sonnet-4-5
feature: ai-todo-chatbot
branch: 001-ai-todo-chatbot
user: system
command: /sp.tasks
labels: ["tasks", "implementation", "test-first", "user-stories", "mcp-tools", "fastapi", "openai-agents", "chatkit"]
links:
  spec: specs/001-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-todo-chatbot/tasks.md
tests:
  - All testing tasks included in tasks.md (Phase 9)
---

## Prompt

Break into atomic, testable tasks with explicit test requirements:

**DATABASE SETUP (4 tasks)**: T-001: Create Task SQLModel in backend/src/models/task.py (user_id indexed, id PK, title max 200, description max 1000, completed default False, created_at, updated_at). T-002: Create Conversation SQLModel in backend/src/models/conversation.py (user_id indexed, id PK, created_at, updated_at). T-003: Create Message SQLModel in backend/src/models/message.py (user_id indexed, id PK, conversation_id FK, role enum "user"|"assistant", content, created_at). T-004: Setup async database connection in backend/src/database/connection.py (Neon PostgreSQL with create_async_engine, DATABASE_URL from env) + session dependency in backend/src/database/session.py.

**MCP SERVER (7 tasks)**: T-005: Initialize MCP server with stdio transport in backend/src/mcp/server.py (Server("todo-mcp-server"), stdio_server context manager). T-006 to T-010: Implement 5 MCP tools (@server.call_tool decorator): add_task, list_tasks, complete_task, delete_task, update_task in backend/src/mcp/tools/*.py. T-011: Add error handling for all MCP tools (task not found 404, invalid input 400, database errors 500).

**OPENAI AGENT INTEGRATION (4 tasks)**: T-012: Initialize OpenAI Agent with system prompt in backend/src/agent/agent.py. T-013: Register all 5 MCP tools as OpenAI functions. T-014: Create agent runner with conversation history in backend/src/agent/runner.py. T-015: Implement agent behavior tests for trigger word mapping.

**CHAT API ENDPOINT (6 tasks)**: T-016: Create FastAPI app with CORS middleware in backend/src/api/app.py (parse CORS_ORIGINS env). T-017: Implement JWT verification middleware in backend/src/api/middleware.py (HTTPBearer, decode with BETTER_AUTH_SECRET). T-018: Create Pydantic request/response schemas in backend/src/api/schemas.py. T-019: Implement POST /api/{user_id}/chat endpoint in backend/src/api/routes.py. T-020: Implement 11-step stateless conversation flow in chat endpoint handler. T-021: Add comprehensive error handling (401, 403, 404, 500, 503).

**FRONTEND (5 tasks)**: T-022: Setup Next.js 16 App Router structure in frontend/src/app/. T-023: Configure Better Auth client in frontend/src/lib/auth.ts. T-024: Create backend API client in frontend/src/lib/api.ts (fetch wrapper with Authorization Bearer header). T-025: Integrate OpenAI ChatKit component in frontend/src/components/ChatInterface.tsx. T-026: Create chat page with authentication guard in frontend/src/app/chat/page.tsx.

**TESTING (9 tasks)**: T-027: Create pytest configuration in backend/pytest.ini. T-028: Create test fixtures in backend/tests/conftest.py (async DB session with SQLite in-memory, mock OpenAI client). T-029 to T-033: Unit tests for all MCP tools, JWT middleware, database models. T-034 to T-036: Integration tests for chat flow, user isolation, CORS. T-037: E2E tests for all 8 natural language command patterns. T-038: Coverage report generation (80% minimum). T-039: Frontend unit tests for API client.

**CONFIGURATION & DEPLOYMENT (5 tasks)**: T-040: Create Docker Compose configuration in docker-compose.yml (postgres, backend, frontend services). T-041: Create backend Dockerfile. T-042: Create frontend Dockerfile. T-043: Create comprehensive README.md. T-044: Document ChatKit domain allowlist workflow.

**FINAL VALIDATION (5 tasks)**: T-045 to T-050: Validate all 30 acceptance criteria from spec.md (Core Functionality AC-001 to AC-005, Stateless Architecture AC-006 to AC-009, Security & Isolation AC-010 to AC-014, Error Handling AC-015 to AC-019, Testing & Quality AC-020 to AC-024, Deployment AC-025 to AC-030).

TOTAL TASKS: 45 (reorganized into 95 detailed tasks with test-first approach)

## Response snapshot

Created comprehensive tasks.md with 95 atomic tasks organized across 11 phases:

**Phase 1 - Setup** (5 tasks): Project structure initialization, Python/Node dependencies, environment templates for backend and frontend

**Phase 2 - Foundational** (28 tasks): Critical blocking infrastructure including:
- Database Layer (6 tasks): Task/Conversation/Message SQLModels, async connection, Alembic migrations
- MCP Server (7 tasks): Initialize stdio server, implement all 5 tools (@server.call_tool), error handling
- OpenAI Agent (4 tasks): Initialize agent with system prompt, register functions, create runner, behavior tests
- Chat API (6 tasks): FastAPI app + CORS, JWT middleware, schemas, POST endpoint, 11-step stateless flow, error handling
- Frontend Setup (5 tasks): Next.js App Router, Better Auth client, API client, ChatKit integration, chat page

**Phase 3-8 - User Stories** (organized by priority P1→P2→P3):
- Phase 3 - US1 Add Tasks (P1): 4 test tasks + 4 implementation tasks
- Phase 4 - US2 View Tasks (P1): 3 test tasks + 4 implementation tasks
- Phase 5 - US6 Multi-Turn (P2): 3 test tasks + 4 implementation tasks
- Phase 6 - US3 Complete Tasks (P2): 3 test tasks + 4 implementation tasks
- Phase 7 - US4 Delete Tasks (P3): 3 test tasks + 4 implementation tasks
- Phase 8 - US5 Update Tasks (P3): 3 test tasks + 4 implementation tasks

**Phase 9 - Testing** (9 tasks): pytest config, fixtures, unit tests (tools/auth/models), integration tests (isolation/CORS/chat flow), E2E tests (8 NL commands), coverage report (80% minimum), frontend tests

**Phase 10 - Configuration** (5 tasks): Docker Compose, Dockerfiles, README.md, ChatKit domain allowlist docs

**Phase 11 - Validation** (6 tasks): Validate all 30 acceptance criteria from spec.md across 6 categories

**Task Format Examples**:
- `- [ ] T001 Create project structure per implementation plan`
- `- [ ] T003 [P] Initialize frontend Next.js 16 project in frontend/`
- `- [ ] T034 [P] [US1] Unit test for add_task MCP tool`
- `- [ ] T037 [US1] Verify Task model supports title extraction`

**Key Features**:
- Test-first approach: All user story tests written BEFORE implementation
- Parallel execution: All [P] marked tasks can run concurrently (45 parallel opportunities identified)
- User story independence: Each story (US1-US6) can be implemented and tested independently
- Dependencies documented: Clear phase dependencies and critical path (Foundational blocks all stories)
- 3 implementation strategies: MVP First (US1+US2), Incremental Delivery, Parallel Team
- Constitution compliance: 80% minimum coverage enforced, test-first development, stateless architecture, user isolation

**Coverage**:
- All 6 user stories from spec.md included
- All 5 MCP tools implemented with Official Python SDK
- All 8 natural language command patterns tested
- All 30 acceptance criteria from spec.md validated in Phase 11
- All technical components from plan.md covered (Database, MCP, Agent, API, Frontend, Testing, Config)

## Outcome

- ✅ Impact: Complete Phase 2 (Tasks) with 95 atomic, testable tasks organized by user story priorities. Ready for implementation with test-first approach.
- 🧪 Tests: 27 testing tasks included across all user stories (unit, integration, E2E), 80% minimum coverage enforced, test-first development workflow
- 📁 Files: Created tasks.md (23.5KB, 95 tasks), PHR in history/prompts/ai-todo-chatbot/
- 🔁 Next prompts: /sp.implement or manual task execution starting with Phase 1 (Setup)
- 🧠 Reflection: Tasks follow user story priorities from spec.md (P1→P2→P3). Foundational phase blocks all stories but enables parallel story work afterward. Test-first approach per constitution. All acceptance criteria mapped to validation tasks. Clear checkpoints after each phase for independent story validation.

## Evaluation notes (flywheel)

- Failure modes observed: None - comprehensive task breakdown covers all components with test-first approach
- Graders run and results (PASS/FAIL): PASS - All user stories independently testable, test-first workflow enforced, 80% coverage requirement explicit, constitutional principles satisfied
- Prompt variant (if applicable): comprehensive-tasks-with-test-first-and-user-story-organization-v1
- Next experiment (smallest change to try): Begin Phase 1 (Setup) tasks, validate project structure creation before proceeding to Foundational phase

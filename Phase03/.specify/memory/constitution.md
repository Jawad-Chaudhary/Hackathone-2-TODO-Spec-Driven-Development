<!--
Sync Impact Report
==================
Version: 1.0.0 → 2.0.0 (MAJOR - new governance model for Phase 3 AI-powered conversational todo app)
Modified Principles:
  - Complete rewrite from template to Phase 3 AI todo chatbot architecture
Added Sections:
  - 8 Core Principles (Stateless Architecture, MCP-First Integration, Conversation Persistence, Natural Language Interface, Official SDKs Only, Test-Driven Development, Specialized Agents, Strict Security)
  - Tech Stack Requirements
  - Agent Usage Guidelines
  - Key Architecture Decisions
  - Testing Standards
Removed Sections:
  - Generic template placeholders
Templates Requiring Updates:
  ✅ constitution.md - updated
  ⚠ plan-template.md - verify constitution checks align with new principles
  ⚠ spec-template.md - ensure requirements section supports conversational AI features
  ⚠ tasks-template.md - validate task categorization supports MCP tools and agent workflow
Follow-up TODOs:
  - Review plan-template.md Constitution Check section to reference new Phase 3 principles
  - Update slash commands to validate against new architecture constraints
-->

# AI-Powered Conversational Todo App Constitution

## Core Principles

### I. Stateless Architecture (NON-NEGOTIABLE)

All application state MUST be stored exclusively in Neon PostgreSQL database. The application MUST NOT maintain any in-memory state, session data, or cache that persists across requests. Every request MUST be self-contained, loading necessary context from the database and saving results back to the database.

**Rationale**: Stateless architecture ensures horizontal scalability, simplifies debugging, enables server restarts without data loss, and provides a consistent foundation for serverless deployment models.

**Implementation Requirements**:
- All conversation history loaded from database before agent execution
- All agent responses persisted to database after generation
- No global variables or in-memory caches
- Conversation survives server restarts

### II. MCP-First Integration (NON-NEGOTIABLE)

All todo operations MUST be performed through MCP (Model Context Protocol) tools. Direct API calls to the todo database from the agent are FORBIDDEN. The agent MUST interact with todos exclusively through the five MCP tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`.

**Rationale**: MCP tools provide a standardized, type-safe interface between AI agents and system capabilities. This separation ensures the agent layer remains decoupled from database implementation, enables better testing through tool mocking, and follows the official OpenAI Agents SDK integration pattern.

**Implementation Requirements**:
- Agent code never imports database models directly
- All CRUD operations via MCP tool calls
- Each MCP tool validates user_id for isolation
- Tools are stateless and reusable

### III. Conversation Persistence (NON-NEGOTIABLE)

Every message in a conversation—both user inputs and assistant responses—MUST be persisted to the database immediately. The database schema MUST include `conversations` and `messages` tables with proper foreign key relationships. All messages MUST be associated with a `user_id` for multi-tenant isolation.

**Rationale**: Persisting every message enables conversation history replay, debugging, analytics, user experience continuity across sessions, and compliance with data retention policies.

**Implementation Requirements**:
- Messages table with user_id, conversation_id, role, content, timestamp
- User messages saved before agent invocation
- Assistant messages saved after agent response generation
- Proper indexing on user_id and conversation_id

### IV. Natural Language Interface

The user interface MUST be conversational, with NO traditional form-based todo management UI. Users interact with todos exclusively through natural language commands in a chat interface. The AI agent interprets intent and executes appropriate MCP tool calls.

**Rationale**: Natural language interfaces reduce cognitive load, support accessibility, enable voice-based interaction, and provide a more human-centric experience compared to rigid form UIs.

**Example Commands**:
- "Add task: buy groceries"
- "Show my tasks"
- "Mark task 3 as done"
- "Delete all completed tasks"

### V. Official SDKs Only (NON-NEGOTIABLE)

The project MUST use only official, stable SDKs:
- **OpenAI Agents SDK** for AI agent implementation
- **Official Python MCP SDK** for MCP server and tool implementation

Custom AI orchestration libraries, unofficial MCP implementations, and third-party agent frameworks are FORBIDDEN.

**Rationale**: Official SDKs receive vendor support, security patches, and backward compatibility guarantees. Using unofficial implementations introduces maintenance risk, security vulnerabilities, and breaking changes without migration paths.

### VI. Test-Driven Development (NON-NEGOTIABLE)

All code MUST achieve ≥80% test coverage. Tests MUST be written in this order:
1. **Unit tests** for MCP tools and database operations
2. **Integration tests** for chat endpoint + agent + tools interaction
3. **Frontend component tests** for ChatKit UI
4. **End-to-end tests** for complete user workflows

No code merges to main branch without passing all tests and meeting coverage threshold.

**Rationale**: High test coverage ensures refactoring safety, catches regressions early, serves as executable documentation, and enables confident deployments to production.

**Coverage Requirements**:
- MCP tools: 100% (critical integration layer)
- Database operations: ≥90%
- API endpoints: ≥85%
- Frontend components: ≥75%
- E2E workflows: All primary user journeys

### VII. Specialized Agents

Development tasks MUST be delegated to specialized domain agents:
- **@database-agent**: Schema, migrations, SQLModel, DB tests
- **@backend-agent**: FastAPI routes, MCP server, agent integration, CORS
- **@frontend-agent**: ChatKit UI, API client, deployment
- **@testing-agent**: All test types (unit/integration/E2E)
- **@devops-agent**: CORS, environment variables, deployment, security config

Generic "do everything" agents are FORBIDDEN. Each task MUST be routed to the agent with appropriate domain expertise.

**Rationale**: Specialized agents maintain focused context, reduce token usage, minimize cross-domain errors, and enable parallel task execution across domains.

### VIII. Strict Security

- **JWT Authentication**: ALL chat endpoints MUST validate JWT tokens before processing
- **User Isolation**: ALL database queries MUST filter by user_id
- **CORS Policy**: Development uses `http://localhost:3000`, production uses Vercel domain from environment variable (NO wildcard origins in production)
- **No Secrets in Code**: API keys, database URLs, JWT secrets MUST be environment variables
- **SQL Injection Prevention**: Use SQLModel parameterized queries (never string concatenation)

**Rationale**: Security principles prevent unauthorized access, data leakage between users, XSS/CSRF attacks, and credential exposure in version control.

## Tech Stack Requirements

The following technology stack is MANDATORY and MUST NOT be substituted:

**Frontend**:
- OpenAI ChatKit (React/Next.js 15+ App Router)
- Better Auth integration for authentication flows
- TypeScript for type safety

**Backend**:
- FastAPI (async endpoints)
- Better Auth + JWT for authentication
- Official Python MCP SDK for tool implementation
- Official OpenAI Agents SDK for conversational AI

**Database**:
- Neon PostgreSQL (serverless Postgres)
- SQLModel for ORM and migrations
- Async database operations (asyncpg)

**Testing**:
- Backend: pytest + pytest-asyncio + httpx
- Frontend: Jest + React Testing Library
- E2E: Playwright or Cypress

**Workflow**:
- Claude Code for task execution
- SpecKit Plus for spec-driven development

## Agent Usage Guidelines

When coordinating work across domains, specialized agents MUST communicate through file references (not direct collaboration). Example workflow:

1. @database-agent creates schema in `backend/app/models/conversation.py`
2. @backend-agent references new models in `backend/app/api/chat.py`
3. @frontend-agent consumes API in `frontend/lib/chat-api.ts`
4. @testing-agent writes integration tests for the full stack

Each agent produces artifacts in their domain; subsequent agents read those artifacts as context.

## Key Architecture Decisions

### Single Chat Endpoint

**Endpoint**: `POST /api/{user_id}/chat`

**Contract**:
```json
Request: { "message": "user input text", "conversation_id": "uuid or null" }
Response: { "response": "agent response", "conversation_id": "uuid", "tool_calls": [...] }
```

This single endpoint handles all conversational interactions. The backend loads conversation history, invokes the agent with MCP tools, and saves the response.

### MCP Tool Catalog

Exactly five MCP tools:

1. `add_task(user_id: str, title: str, description: str | None) -> Task`
2. `list_tasks(user_id: str, status: str | None) -> List[Task]`
3. `complete_task(user_id: str, task_id: int) -> Task`
4. `delete_task(user_id: str, task_id: int) -> bool`
5. `update_task(user_id: str, task_id: int, title: str | None, description: str | None) -> Task`

All tools MUST validate `user_id` and enforce user-scoped data access.

### Conversation Flow

```
1. User sends message → POST /api/{user_id}/chat
2. Backend validates JWT, extracts user_id
3. Load conversation history from DB (if conversation_id provided)
4. Save user message to DB
5. Invoke OpenAI agent with:
   - Conversation history
   - New user message
   - MCP tools registered
6. Agent executes (may call MCP tools)
7. Save assistant response to DB
8. Return response + conversation_id to frontend
```

### CORS Configuration

- **Development**: `http://localhost:3000` (hardcoded)
- **Production**: Read from `FRONTEND_URL` environment variable (e.g., `https://app.vercel.app`)
- **Forbidden**: Wildcard `*` origins in production

### Existing Phase 2 REST API

The Phase 2 REST API for todos (`/api/tasks`, `/api/tasks/{id}`) MUST remain untouched. Users can still use the traditional API if desired. The conversational interface is an additive feature, not a replacement.

## Testing Standards

### Unit Tests

**Scope**: Individual functions, MCP tools, database operations

**Requirements**:
- Mock external dependencies (database, OpenAI API)
- Test edge cases (empty inputs, invalid user_id, duplicate task IDs)
- Verify error handling (database connection failures, tool validation errors)

**Example**: Test `add_task` MCP tool with valid/invalid inputs, mock database session

### Integration Tests

**Scope**: Chat endpoint + agent + MCP tools + database

**Requirements**:
- Use test database (not production)
- Test complete workflows (user asks → agent calls tools → response returned)
- Verify conversation persistence (messages saved correctly)
- Test multi-turn conversations (history loaded properly)

**Example**: POST message "add task buy milk" → verify task created in DB → verify assistant response references new task

### E2E Tests

**Scope**: Full user journey through frontend UI

**Requirements**:
- Test authentication flow (login → chat)
- Test task creation via chat ("add task X")
- Test task listing ("show my tasks")
- Test task completion ("mark task 2 done")
- Test conversation continuity (refresh page, history persists)

**Example**: User signs in → sends "add task buy groceries" → sees confirmation → sends "show my tasks" → sees task in response

### Coverage Report

Single command MUST generate coverage report:

```bash
# Backend
pytest --cov=backend/app --cov-report=html

# Frontend
npm test -- --coverage

# Combined report in CI/CD
```

## Non-Negotiables Summary

The following constraints CANNOT be relaxed without amending this constitution:

1. ✅ State only in PostgreSQL (no in-memory sessions)
2. ✅ Todo operations only via MCP tools (no direct DB from agent)
3. ✅ All messages persisted to database
4. ✅ Natural language interface (no form-based todo UI)
5. ✅ Official OpenAI + MCP SDKs only
6. ✅ ≥80% test coverage before merge
7. ✅ Specialized agents for each domain
8. ✅ JWT auth on all chat endpoints
9. ✅ User_id validation in every MCP tool
10. ✅ No wildcard CORS in production
11. ✅ Conversation survives server restarts
12. ✅ Integration tests pass before deployment

## Governance

This constitution supersedes all other coding practices, documentation, and architectural preferences. Any code, design, or implementation that violates these principles MUST be rejected during code review.

### Amendment Procedure

1. Propose amendment with justification (document "why current principle is blocking progress")
2. Discuss alternatives that preserve principle intent
3. If amendment approved, update constitution with version bump:
   - **MAJOR**: Backward-incompatible principle removal or redefinition
   - **MINOR**: New principle added or material expansion
   - **PATCH**: Clarifications, typo fixes, non-semantic refinements
4. Update all dependent templates (plan, spec, tasks) to reflect changes
5. Create migration plan for existing code that conflicts with new principle

### Compliance Review

All pull requests MUST verify:
- [ ] Changes comply with stateless architecture
- [ ] No direct database access from agent code
- [ ] All messages persisted to database
- [ ] Test coverage ≥80%
- [ ] JWT validation on protected endpoints
- [ ] User_id validated in MCP tools
- [ ] CORS configuration follows environment rules
- [ ] Official SDKs used (no custom implementations)

### Complexity Justification

If a design decision violates a principle (e.g., caching for performance), it MUST be documented in the plan.md "Complexity Tracking" section with:
- Which principle is violated
- Why the violation is necessary
- Simpler alternatives considered and why they were rejected

**Version**: 2.0.0 | **Ratified**: 2026-01-18 | **Last Amended**: 2026-01-18

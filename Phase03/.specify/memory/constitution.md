<!--
  Sync Impact Report:
  - Version: NEW → 1.0.0 (initial constitution creation)
  - Principles added: 6 core principles defined
  - Sections added: Architecture, Database, Security, Frontend, Testing
  - Templates: ✅ Validated against plan-template.md, spec-template.md, tasks-template.md
  - Follow-up: Ratification date to be confirmed by project team
-->

# AI Todo Chatbot Constitution

## Core Principles

### I. Stateless Architecture

All backend services MUST be stateless with no in-memory state storage. This ensures horizontal scalability and enables seamless deployment of multiple instances without session affinity requirements. State MUST be persisted exclusively in the Neon PostgreSQL database.

**Rationale**: Stateless design enables cloud-native horizontal scaling, simplifies deployment, eliminates single points of failure, and allows zero-downtime rolling updates.

### II. User Isolation & Security

Every database query and API operation MUST enforce user-level isolation through user_id filtering. JWT tokens issued by Better Auth MUST be verified on every API request via middleware. No cross-user data leakage is permitted under any circumstances.

**Requirements**:
- Authorization: Bearer token required on all endpoints
- JWT verification middleware executes before business logic
- All database models include user_id with indexed filtering
- BETTER_AUTH_SECRET shared securely between frontend and backend
- CORS configured via environment variables (CORS_ORIGINS, CORS_ALLOW_CREDENTIALS)

**Rationale**: Multi-tenant security by design prevents data breaches and ensures compliance with data privacy regulations.

### III. Tool-Based AI Architecture

AI agent capabilities MUST be implemented as discrete MCP (Model Context Protocol) tools using the Official Python MCP SDK. The five required tools are: add_task, list_tasks, complete_task, delete_task, and update_task. Tool composition MUST be enabled to allow the OpenAI Agents SDK to orchestrate multi-step operations.

**Requirements**:
- One tool per CRUD operation following single responsibility principle
- Clear tool schemas with typed parameters and return values
- Tools must be stateless and idempotent where applicable
- Error handling with descriptive messages for agent interpretation

**Rationale**: Tool-based design provides clear separation of concerns, makes AI capabilities testable and composable, and aligns with industry standards for AI agent development.

### IV. Database-First Conversation State

Conversation history MUST be persisted in the database, not in memory. Every message exchange MUST create records in the Conversation and Message tables. The backend provides a stateless chat interface; the OpenAI Agents SDK manages conversation context by loading history from the database.

**Data Models**:
- **Task**: user_id, id, title, description, completed, created_at, updated_at
- **Conversation**: user_id, id, created_at, updated_at
- **Message**: user_id, id, conversation_id, role, content, created_at

**Requirements**:
- All user_id fields MUST be indexed for query performance
- SQLModel ORM for type-safe database operations
- Async database operations throughout
- Neon Serverless PostgreSQL for managed infrastructure

**Rationale**: Database-backed conversation state enables stateless backend scaling, provides audit trails, supports conversation recovery, and allows future analytics capabilities.

### V. Single Endpoint Simplicity

The backend MUST expose a single chat endpoint: POST /api/{user_id}/chat. This endpoint handles all user interactions, delegates to the OpenAI Agents SDK, which invokes MCP tools as needed, and returns the complete agent response.

**Requirements**:
- Path parameter: user_id (validated against JWT claims)
- Request body: user message content
- Response: agent response with tool invocation results
- All business logic routed through this single interface

**Rationale**: Single endpoint design reduces API surface area, simplifies client integration, centralizes authentication/authorization, and aligns with conversational interface patterns.

### VI. Test-First Development (NON-NEGOTIABLE)

All code MUST achieve minimum 80% test coverage. Unit tests MUST be written for every function. Integration tests MUST cover API endpoints and database operations. Use pytest with pytest-asyncio for async testing and httpx for HTTP client testing.

**Requirements**:
- pytest as test framework
- pytest-asyncio for async test support
- httpx for testing FastAPI endpoints
- Minimum 80% code coverage measured and enforced
- Tests written before or alongside implementation (TDD encouraged)
- CI/CD pipeline fails on coverage threshold violations

**Rationale**: High test coverage ensures reliability, catches regressions early, enables confident refactoring, and serves as executable documentation.

## Architecture Standards

### Technology Stack

- **Backend Framework**: FastAPI (Python)
- **AI Framework**: OpenAI Agents SDK
- **Tool Protocol**: Official MCP SDK (Python implementation)
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel (async operations)
- **Authentication**: Better Auth with JWT tokens
- **Frontend**: OpenAI ChatKit with Next.js
- **Testing**: pytest, pytest-asyncio, httpx

### API Design

- RESTful single endpoint: POST /api/{user_id}/chat
- JSON request/response format
- JWT Bearer token authentication
- Error responses include descriptive messages for debugging
- HTTP status codes follow REST conventions (200, 400, 401, 403, 500)

### Environment Configuration

**Required Backend Variables**:
- DATABASE_URL (Neon PostgreSQL connection string)
- BETTER_AUTH_SECRET (shared with frontend)
- OPENAI_API_KEY (for OpenAI Agents SDK)
- CORS_ORIGINS (comma-separated allowed origins)
- CORS_ALLOW_CREDENTIALS (boolean)

**Required Frontend Variables**:
- NEXT_PUBLIC_OPENAI_DOMAIN_KEY (ChatKit domain allowlist)
- NEXT_PUBLIC_API_BASE_URL (backend endpoint)
- BETTER_AUTH_SECRET (shared with backend)

## Quality Gates

### Before Phase 0 Research
- [ ] Constitution reviewed and approved by team
- [ ] All required environment variables documented
- [ ] Technology stack versions specified

### Before Phase 1 Design
- [ ] Database schema aligns with data models in constitution
- [ ] Security architecture reviewed for JWT flow
- [ ] MCP tool schemas drafted

### Before Phase 2 Implementation
- [ ] Test framework configured (pytest, pytest-asyncio, httpx)
- [ ] CI/CD pipeline includes coverage enforcement
- [ ] All dependencies locked with version constraints

### Before Production Deployment
- [ ] 80% test coverage achieved and verified
- [ ] Security audit completed (JWT verification, user isolation)
- [ ] Load testing validates horizontal scalability
- [ ] Environment variables secured (no secrets in code)

## Governance

### Amendment Process

Constitutional amendments require:
1. Written proposal documenting change rationale and impact
2. Review by project team
3. Update to this document with version increment
4. Propagation of changes to affected templates (plan, spec, tasks)
5. Update to CLAUDE.md if development guidelines affected

### Versioning Policy

- **MAJOR** version bump: Backward-incompatible principle changes (e.g., removing stateless requirement)
- **MINOR** version bump: New principles added or existing principles significantly expanded
- **PATCH** version bump: Clarifications, typo fixes, non-semantic improvements

### Compliance Review

All pull requests and architecture decisions MUST verify compliance with this constitution. Violations require explicit justification documented in plan.md Complexity Tracking section. Use the constitution check section in plan-template.md to validate adherence.

**Version**: 1.0.0 | **Ratified**: 2026-01-13 | **Last Amended**: 2026-01-13

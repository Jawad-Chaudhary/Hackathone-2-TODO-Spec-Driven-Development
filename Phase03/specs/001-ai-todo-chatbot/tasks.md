# Tasks: AI Todo Chatbot

**Input**: Design documents from `/specs/001-ai-todo-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: All testing tasks included - 80% minimum coverage enforced per constitution

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths based on plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan (backend/ and frontend/ directories with src/, tests/, config files)
- [ ] T002 Initialize backend Python project in backend/ with requirements.txt (FastAPI, SQLModel, Official MCP SDK, OpenAI Agents SDK, pytest, pytest-asyncio, httpx, alembic)
- [ ] T003 [P] Initialize frontend Next.js 16 project in frontend/ with package.json (OpenAI ChatKit, Better Auth, TypeScript)
- [ ] T004 [P] Create backend/.env.example with DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY, CORS_ORIGINS, CORS_ALLOW_CREDENTIALS
- [ ] T005 [P] Create frontend/.env.local.example with NEXT_PUBLIC_API_URL, NEXT_PUBLIC_OPENAI_DOMAIN_KEY, BETTER_AUTH_SECRET

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Layer

- [ ] T006 Create Task SQLModel in backend/src/models/task.py (user_id indexed, id PK, title max 200, description max 1000, completed default False, created_at, updated_at)
- [ ] T007 [P] Create Conversation SQLModel in backend/src/models/conversation.py (user_id indexed, id PK, created_at, updated_at)
- [ ] T008 [P] Create Message SQLModel with MessageRole enum in backend/src/models/message.py (user_id indexed, id PK, conversation_id FK, role enum "user"|"assistant", content, created_at)
- [ ] T009 Setup async database connection in backend/src/database/connection.py (Neon PostgreSQL with create_async_engine, DATABASE_URL from env)
- [ ] T010 [P] Create database session dependency in backend/src/database/session.py (AsyncSession factory for FastAPI Depends)
- [ ] T011 Initialize Alembic in backend/alembic/ and create initial migration for Task, Conversation, Message tables

### MCP Server (Official Python SDK)

- [ ] T012 Initialize MCP server with stdio transport in backend/src/mcp/server.py (Server("todo-mcp-server"), stdio_server context manager)
- [ ] T013 [P] Implement add_task MCP tool in backend/src/mcp/tools/add_task.py (@server.call_tool, validate user_id/title/description, INSERT task, return JSON)
- [ ] T014 [P] Implement list_tasks MCP tool in backend/src/mcp/tools/list_tasks.py (@server.call_tool, validate user_id/status filter, SELECT tasks, return array)
- [ ] T015 [P] Implement complete_task MCP tool in backend/src/mcp/tools/complete_task.py (@server.call_tool, validate user_id/task_id, UPDATE completed=true, return JSON)
- [ ] T016 [P] Implement delete_task MCP tool in backend/src/mcp/tools/delete_task.py (@server.call_tool, validate user_id/task_id, DELETE task, return JSON)
- [ ] T017 [P] Implement update_task MCP tool in backend/src/mcp/tools/update_task.py (@server.call_tool, validate user_id/task_id/title/description, UPDATE task, return JSON)
- [ ] T018 Add error handling for all MCP tools (task not found 404, invalid input 400, database errors 500, return error objects)

### OpenAI Agent Integration

- [ ] T019 Initialize OpenAI Agent with system prompt in backend/src/agent/agent.py (Agent class, OpenAIChatCompletionsModel, system prompt from plan.md)
- [ ] T020 Register all 5 MCP tools as OpenAI functions in backend/src/agent/agent.py (convert MCP tool schemas to function format)
- [ ] T021 Create agent runner with conversation history in backend/src/agent/runner.py (Runner class, run() method accepting messages array)
- [ ] T022 Implement agent behavior tests for trigger word mapping in backend/tests/unit/test_agent_behavior.py (verify "add/create" → add_task, "show/list" → list_tasks, etc.)

### Chat API Endpoint

- [ ] T023 Create FastAPI app with CORS middleware in backend/src/api/app.py (parse CORS_ORIGINS env, allow_credentials=True, explicit methods/headers)
- [ ] T024 Implement JWT verification middleware in backend/src/api/middleware.py (HTTPBearer, decode with BETTER_AUTH_SECRET HS256, extract user_id from token)
- [ ] T025 Create Pydantic request/response schemas in backend/src/api/schemas.py (ChatRequest with conversation_id optional + message required, ChatResponse with conversation_id + response + tool_calls)
- [ ] T026 Implement POST /api/{user_id}/chat endpoint in backend/src/api/routes.py (validate user_id vs JWT, load conversation history, build messages array, run agent, store messages, return response)
- [ ] T027 Implement 11-step stateless conversation flow in chat endpoint handler (1. receive message, 2. verify JWT, 3. get/create conversation, 4. load history, 5. build messages, 6. save user msg, 7. run agent, 8. execute tools, 9. format response, 10. save assistant msg, 11. return & forget state)
- [ ] T028 Add error handling to chat endpoint (401 unauthorized, 403 forbidden user_id mismatch, 404 conversation not found, 500 internal errors, 503 OpenAI unavailable)

### Frontend Setup

- [ ] T029 Setup Next.js 16 App Router structure in frontend/src/app/ (layout.tsx, page.tsx, chat/page.tsx, login/page.tsx)
- [ ] T030 [P] Configure Better Auth client in frontend/src/lib/auth.ts (useSession hook, session management)
- [ ] T031 [P] Create backend API client in frontend/src/lib/api.ts (fetch wrapper with Authorization Bearer header, POST /api/{user_id}/chat method)
- [ ] T032 Integrate OpenAI ChatKit component in frontend/src/components/ChatInterface.tsx (ChatKit wrapper with domain allowlist, pass JWT token, handle message send/receive)
- [ ] T033 Create chat page with authentication guard in frontend/src/app/chat/page.tsx (useSession hook, redirect if unauthenticated, render ChatInterface)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Tasks via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks by typing natural language commands without remembering syntax

**Independent Test**: User types "I need to remember to buy groceries", receives confirmation, verifies task exists in list

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T034 [P] [US1] Unit test for add_task MCP tool in backend/tests/unit/test_tools.py (test valid input, invalid title length, missing user_id, database error handling)
- [ ] T035 [P] [US1] Integration test for add task chat flow in backend/tests/integration/test_chat_flow.py (send "Add task to buy groceries", verify task created in DB, verify response confirmation)
- [ ] T036 [P] [US1] E2E test for natural language add command in backend/tests/e2e/test_nl_commands.py (test all add trigger words: add, create, remember, need to)

### Implementation for User Story 1

- [ ] T037 [US1] Verify Task model supports title extraction from natural language in add_task tool (agent extracts title from "Add task to X" format)
- [ ] T038 [US1] Add title validation in add_task tool (1-200 chars, required, return 400 if validation fails)
- [ ] T039 [US1] Add description parsing support in add_task tool (optional, extract from "Add task: X - Y" format, max 1000 chars)
- [ ] T040 [US1] Implement confirmation response templates in agent system prompt (use plan.md templates: "I've added '[TITLE]' to your task list!")

**Checkpoint**: At this point, User Story 1 should be fully functional - users can add tasks via natural language

---

## Phase 4: User Story 2 - View and Filter Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can view tasks through natural language queries, filtering by status

**Independent Test**: User with existing tasks types "Show me all my tasks", receives formatted list

### Tests for User Story 2

- [ ] T041 [P] [US2] Unit test for list_tasks MCP tool in backend/tests/unit/test_tools.py (test all status filters: all, pending, completed, empty list, user isolation)
- [ ] T042 [P] [US2] Integration test for list tasks chat flow in backend/tests/integration/test_chat_flow.py (create 5 tasks, request "show all", verify response includes all 5)
- [ ] T043 [P] [US2] E2E test for natural language list commands in backend/tests/e2e/test_nl_commands.py (test: "Show me all my tasks", "What's pending?", "What have I completed?")

### Implementation for User Story 2

- [ ] T044 [US2] Verify list_tasks tool supports status filtering ("all" | "pending" | "completed")
- [ ] T045 [US2] Implement formatted list response in agent (numbered list with status indicators, e.g., "1. Buy groceries (pending)")
- [ ] T046 [US2] Add empty list response template to agent system prompt ("You don't have any tasks yet! Want to add one?")
- [ ] T047 [US2] Verify user isolation in list_tasks (user_id filter on all queries, test cross-user data leakage prevention)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can add and view tasks

---

## Phase 5: User Story 6 - Multi-Turn Conversations (Priority: P2)

**Goal**: Users can have contextual conversations where AI remembers previous exchanges

**Independent Test**: User creates task, then asks "What did I just add?" without task ID, system references history

### Tests for User Story 6

- [ ] T048 [P] [US6] Unit test for conversation history loading in backend/tests/unit/test_conversation.py (test message retrieval by conversation_id, ordering by created_at)
- [ ] T049 [P] [US6] Integration test for multi-turn conversation in backend/tests/integration/test_stateless.py (create task, ask follow-up question, verify agent uses context from previous message)
- [ ] T050 [P] [US6] Integration test for conversation persistence in backend/tests/integration/test_stateless.py (simulate server restart, verify conversation history loads from DB)

### Implementation for User Story 6

- [ ] T051 [US6] Verify chat endpoint loads conversation history from DB on every request (SELECT messages WHERE conversation_id ORDER BY created_at)
- [ ] T052 [US6] Verify chat endpoint builds messages array correctly (history + new user message)
- [ ] T053 [US6] Verify chat endpoint stores both user and assistant messages in DB after agent run
- [ ] T054 [US6] Test conversation resumption after browser refresh (verify conversation_id persists, history loads correctly)

**Checkpoint**: At this point, User Stories 1, 2, AND 6 should work independently - conversational context is maintained

---

## Phase 6: User Story 3 - Complete Tasks (Priority: P2)

**Goal**: Users can mark tasks complete through conversational commands using ID or descriptions

**Independent Test**: User with task ID 3 types "Mark task 3 as complete", system updates status, user verifies in list

### Tests for User Story 3

- [ ] T055 [P] [US3] Unit test for complete_task MCP tool in backend/tests/unit/test_tools.py (test valid task_id, task not found, invalid user_id, already completed)
- [ ] T056 [P] [US3] Integration test for complete task chat flow in backend/tests/integration/test_chat_flow.py (create task, complete by ID, verify status updated in DB)
- [ ] T057 [P] [US3] E2E test for natural language complete commands in backend/tests/e2e/test_nl_commands.py (test: "Mark task 3 as complete", "I'm done with groceries", trigger words: done, complete, finished)

### Implementation for User Story 3

- [ ] T058 [US3] Verify complete_task tool validates task_id (positive integer required, return 400 if invalid)
- [ ] T059 [US3] Verify complete_task tool checks task ownership (user_id filter, return 404 if not found or wrong user)
- [ ] T060 [US3] Add completion confirmation template to agent system prompt ("Great! I've marked '[TITLE]' as complete. ✓")
- [ ] T061 [US3] Implement task lookup by title for natural language completion (agent uses list_tasks first, then complete_task with found ID)

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 6 should work - users can add, view, complete tasks with context

---

## Phase 7: User Story 4 - Delete Tasks (Priority: P3)

**Goal**: Users can remove tasks through conversational commands with system help identifying tasks

**Independent Test**: User types "Delete the meeting task", system finds by title, confirms deletion, user verifies removal

### Tests for User Story 4

- [ ] T062 [P] [US4] Unit test for delete_task MCP tool in backend/tests/unit/test_tools.py (test valid task_id, task not found, user isolation, cascade message cleanup)
- [ ] T063 [P] [US4] Integration test for delete task chat flow in backend/tests/integration/test_chat_flow.py (create task, delete by ID, verify removed from DB)
- [ ] T064 [P] [US4] E2E test for natural language delete commands in backend/tests/e2e/test_nl_commands.py (test: "Delete the meeting task", "Delete task 5", trigger words: delete, remove, cancel, forget)

### Implementation for User Story 4

- [ ] T065 [US4] Verify delete_task tool validates task_id and user_id (return 404 if not found)
- [ ] T066 [US4] Add deletion confirmation template to agent system prompt ("I've deleted '[TITLE]' from your task list.")
- [ ] T067 [US4] Implement task lookup by title for natural language deletion (agent uses list_tasks to find task, then delete_task)
- [ ] T068 [US4] Add ambiguous deletion handling (if multiple matches found, ask user to clarify with task ID)

**Checkpoint**: At this point, User Stories 1, 2, 3, 4, AND 6 should work - users can add, view, complete, delete tasks

---

## Phase 8: User Story 5 - Update Tasks (Priority: P3)

**Goal**: Users can modify task titles and descriptions through conversational commands

**Independent Test**: User with task ID 1 types "Change task 1 to 'Call mom tonight'", system updates title, user verifies

### Tests for User Story 5

- [ ] T069 [P] [US5] Unit test for update_task MCP tool in backend/tests/unit/test_tools.py (test title update, description update, both updates, task not found, validation errors)
- [ ] T070 [P] [US5] Integration test for update task chat flow in backend/tests/integration/test_chat_flow.py (create task, update title, verify changes in DB)
- [ ] T071 [P] [US5] E2E test for natural language update commands in backend/tests/e2e/test_nl_commands.py (test: "Change task 1 to 'Call mom tonight'", trigger words: change, update, rename, modify)

### Implementation for User Story 5

- [ ] T072 [US5] Verify update_task tool validates task_id and user_id (return 404 if not found)
- [ ] T073 [US5] Verify update_task tool validates new title/description lengths (title 1-200, description max 1000, return 400 if invalid)
- [ ] T074 [US5] Add update confirmation template to agent system prompt ("Done! I've updated task [ID] to '[NEW_TITLE]'.")
- [ ] T075 [US5] Implement updated_at timestamp update on task modifications

**Checkpoint**: All user stories should now be independently functional - complete task management via natural language

---

## Phase 9: Testing & Quality Assurance

**Purpose**: Ensure 80% minimum coverage and all acceptance criteria met

- [ ] T076 [P] Create pytest configuration in backend/pytest.ini (asyncio_mode=auto, coverage settings, test discovery)
- [ ] T077 [P] Create test fixtures in backend/tests/conftest.py (async DB session with SQLite in-memory, mock OpenAI client, test user fixtures)
- [ ] T078 [P] Unit test for JWT verification middleware in backend/tests/unit/test_auth.py (valid token, expired token, invalid signature, missing token, user_id mismatch)
- [ ] T079 [P] Unit test for database models in backend/tests/unit/test_models.py (Task CRUD, Conversation CRUD, Message CRUD, user_id filtering, validation)
- [ ] T080 [P] Integration test for user isolation in backend/tests/integration/test_isolation.py (create tasks for user A, verify user B cannot access, test malicious user_id attempts)
- [ ] T081 [P] Integration test for CORS configuration in backend/tests/integration/test_cors.py (preflight requests, allowed origins, blocked origins, credentials handling)
- [ ] T082 [P] E2E test for all 8 natural language command patterns in backend/tests/e2e/test_nl_commands.py (comprehensive test of spec's 8 example commands)
- [ ] T083 [P] Coverage report generation (pytest --cov=src --cov-report=html --cov-fail-under=80, verify 80% minimum achieved)
- [ ] T084 [P] Frontend unit tests for API client in frontend/src/lib/__tests__/api.test.ts (test message sending, error handling, JWT inclusion)

**Checkpoint**: All tests passing, 80% coverage achieved, acceptance criteria validated

---

## Phase 10: Configuration & Deployment

**Purpose**: Production readiness and deployment artifacts

- [ ] T085 [P] Create Docker Compose configuration in repository root docker-compose.yml (postgres service, backend service, frontend service, healthchecks, volume mounts)
- [ ] T086 [P] Create backend Dockerfile in backend/Dockerfile (Python 3.11-slim, install dependencies, copy source, uvicorn command)
- [ ] T087 [P] Create frontend Dockerfile in frontend/Dockerfile (Node 18-alpine, install dependencies, copy source, npm dev/build commands)
- [ ] T088 [P] Create comprehensive README.md in repository root (features, prerequisites, quick start with Docker, manual setup, testing, deployment, architecture diagram, troubleshooting)
- [ ] T089 [P] Document ChatKit domain allowlist workflow in README.md (deploy frontend, add domain to OpenAI platform, get key, set env, redeploy)

**Checkpoint**: Project is deployment-ready with complete documentation

---

## Phase 11: Final Validation

**Purpose**: End-to-end validation of all acceptance criteria from spec.md

- [ ] T090 [P] Validate AC-001 to AC-005 (Core Functionality): Test all 8 NL commands, verify 90% accuracy, check response times <5s
- [ ] T091 [P] Validate AC-006 to AC-009 (Stateless Architecture): Test conversation persistence across server restarts, verify no in-memory state, test horizontal scaling scenario
- [ ] T092 [P] Validate AC-010 to AC-014 (Security & Isolation): Test user isolation, verify zero data leakage, test JWT requirements, test CORS validation
- [ ] T093 [P] Validate AC-015 to AC-019 (Error Handling): Test all error scenarios from spec.md error handling section, verify appropriate HTTP codes and friendly messages
- [ ] T094 [P] Validate AC-020 to AC-024 (Testing & Quality): Verify 80% coverage achieved, all unit/integration/E2E tests passing, 100% coverage for security-critical code
- [ ] T095 Manual deployment validation (deploy backend, deploy frontend to Vercel, configure ChatKit domain allowlist, test production environment, verify all env vars configured)

**Checkpoint**: All 30 acceptance criteria validated, project ready for production deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Testing (Phase 9)**: Depends on all desired user stories being complete
- **Configuration (Phase 10)**: Can run in parallel with Testing
- **Validation (Phase 11)**: Depends on Testing and Configuration completion

### User Story Dependencies

- **User Story 1 (P1) - Add Tasks**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1) - View Tasks**: Can start after Foundational (Phase 2) - Independent but may integrate with US1
- **User Story 6 (P2) - Multi-Turn**: Can start after Foundational (Phase 2) - Independent conversation infrastructure
- **User Story 3 (P2) - Complete Tasks**: Can start after Foundational (Phase 2) - Independent but enhances US1
- **User Story 4 (P3) - Delete Tasks**: Can start after Foundational (Phase 2) - Independent but may use list_tasks from US2
- **User Story 5 (P3) - Update Tasks**: Can start after Foundational (Phase 2) - Independent but enhances US1

### Within Each User Story

- Tests MUST be written and FAIL before implementation (test-first per constitution)
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005)
- All Foundational models marked [P] can run in parallel (T007, T008, T010)
- All MCP tools marked [P] can run in parallel (T013-T017)
- All Frontend setup tasks marked [P] can run in parallel (T030, T031)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests within a user story marked [P] can run in parallel
- All testing tasks in Phase 9 marked [P] can run in parallel
- All configuration tasks in Phase 10 marked [P] can run in parallel
- All validation tasks in Phase 11 marked [P] can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch all MCP tools in parallel after database models are complete:
Task: "Implement add_task MCP tool in backend/src/mcp/tools/add_task.py"
Task: "Implement list_tasks MCP tool in backend/src/mcp/tools/list_tasks.py"
Task: "Implement complete_task MCP tool in backend/src/mcp/tools/complete_task.py"
Task: "Implement delete_task MCP tool in backend/src/mcp/tools/delete_task.py"
Task: "Implement update_task MCP tool in backend/src/mcp/tools/update_task.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add Tasks)
4. Complete Phase 4: User Story 2 (View Tasks)
5. **STOP and VALIDATE**: Test User Stories 1 & 2 independently
6. Deploy/demo if ready (minimal viable chatbot)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 & 2 (P1) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 6 (P2) → Test independently → Deploy/Demo (conversational context)
4. Add User Story 3 (P2) → Test independently → Deploy/Demo (task completion)
5. Add User Story 4 (P3) → Test independently → Deploy/Demo (task deletion)
6. Add User Story 5 (P3) → Test independently → Deploy/Demo (task updates)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (critical path)
2. Once Foundational is done:
   - Developer A: User Story 1 & 2 (P1 - MVP features)
   - Developer B: User Story 6 (P2 - conversation context)
   - Developer C: User Story 3 (P2 - task completion)
   - Developer D: Testing infrastructure (Phase 9)
3. Stories complete and integrate independently
4. P3 stories (4 & 5) can be added as team capacity allows

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (test-first per constitution)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- 80% minimum code coverage enforced (constitution principle VI)
- 100% coverage required for security-critical code (JWT verification, user_id filtering)
- All 5 MCP tools use Official Python MCP SDK with @server.call_tool decorator
- Stateless architecture enforced - all state in PostgreSQL, no in-memory sessions
- User isolation enforced - user_id filter on all database queries
- Agent behavior follows trigger word mapping table from plan.md
- Error handling follows 8 error categories from spec.md
- All 30 acceptance criteria from spec.md must be validated in Phase 11

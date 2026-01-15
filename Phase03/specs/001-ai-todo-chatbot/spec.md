# Feature Specification: AI Todo Chatbot

**Feature Branch**: `001-ai-todo-chatbot`
**Created**: 2026-01-13
**Status**: Draft
**Input**: Comprehensive AI Todo Chatbot with MCP tools, OpenAI Agents SDK, stateless FastAPI backend, and ChatKit frontend

## User Scenarios & Testing

### User Story 1 - Add Tasks via Natural Language (Priority: P1)

Users can create tasks by typing natural language commands in a conversational interface without needing to remember specific syntax or use traditional form-based input.

**Why this priority**: Core value proposition of the AI chatbot - enables hands-free, intuitive task creation that differentiates this from traditional todo apps.

**Independent Test**: User opens chatbot, types "I need to remember to buy groceries", receives confirmation that task was created, can verify task exists in their list.

**Acceptance Scenarios**:

1. **Given** user is authenticated, **When** user types "Add a task to buy groceries", **Then** system creates task with title "Buy groceries" and returns confirmation message
2. **Given** user is authenticated, **When** user types "I need to remember to pay bills", **Then** system creates task with title "Pay bills" and returns friendly confirmation
3. **Given** user types ambiguous command like "groceries", **When** AI agent interprets intent, **Then** system creates appropriate task or asks clarifying question
4. **Given** user provides task with description, **When** user types "Add task: Call mom tonight - discuss birthday plans", **Then** system extracts title and description appropriately

---

### User Story 2 - View and Filter Tasks (Priority: P1)

Users can view their tasks through natural language queries, filtering by status (all, pending, completed) without navigating complex UI menus.

**Why this priority**: Essential for task visibility - users need to see what they've created to get value from the system. This is MVP-critical functionality.

**Independent Test**: User with existing tasks types "Show me all my tasks", receives formatted list of all tasks, can distinguish pending from completed tasks.

**Acceptance Scenarios**:

1. **Given** user has 5 tasks (3 pending, 2 completed), **When** user types "Show me all my tasks", **Then** system returns all 5 tasks with status indicators
2. **Given** user has pending tasks, **When** user types "What's pending?", **Then** system returns only incomplete tasks
3. **Given** user has completed tasks, **When** user types "What have I completed?", **Then** system returns only completed tasks
4. **Given** user has no tasks, **When** user requests task list, **Then** system returns friendly message indicating empty list

---

### User Story 3 - Complete Tasks (Priority: P2)

Users can mark tasks as complete through conversational commands, using either task IDs or natural language descriptions to identify the task.

**Why this priority**: Task completion is core functionality but can be implemented after creation and viewing. Users can technically complete tasks by deleting them as a workaround in MVP.

**Independent Test**: User with task ID 3 types "Mark task 3 as complete", system updates task status to completed, user can verify by listing completed tasks.

**Acceptance Scenarios**:

1. **Given** user has task with ID 3, **When** user types "Mark task 3 as complete", **Then** system marks task complete and returns confirmation with task title
2. **Given** user has task titled "Buy groceries", **When** user types "I'm done with groceries", **Then** agent identifies task by title and marks it complete
3. **Given** user types "done/complete/finished" with task reference, **When** agent processes command, **Then** appropriate task is marked complete
4. **Given** user tries to complete non-existent task ID, **When** system processes request, **Then** returns friendly error message indicating task not found

---

### User Story 4 - Delete Tasks (Priority: P3)

Users can remove tasks they no longer need through conversational commands, with the system helping identify tasks by title or ID.

**Why this priority**: Nice-to-have for task management but not critical for MVP - users can leave unwanted tasks incomplete or mark them complete as workaround.

**Independent Test**: User types "Delete the meeting task", system finds task by title, confirms deletion, user verifies task no longer appears in list.

**Acceptance Scenarios**:

1. **Given** user has task titled "Team meeting", **When** user types "Delete the meeting task", **Then** system finds task by title match and removes it
2. **Given** user knows task ID 5, **When** user types "Delete task 5", **Then** system removes task and confirms deletion
3. **Given** multiple tasks match description, **When** user requests deletion, **Then** system asks for clarification or provides options
4. **Given** user tries to delete non-existent task, **When** system processes request, **Then** returns friendly error indicating task not found

---

### User Story 5 - Update Tasks (Priority: P3)

Users can modify existing task titles and descriptions through conversational commands without needing to delete and recreate tasks.

**Why this priority**: Enhancement feature that improves user experience but not required for basic task management. Users can work around by creating new tasks.

**Independent Test**: User with task ID 1 types "Change task 1 to 'Call mom tonight'", system updates task title, user verifies updated title in task list.

**Acceptance Scenarios**:

1. **Given** user has task with ID 1, **When** user types "Change task 1 to 'Call mom tonight'", **Then** system updates title and returns confirmation
2. **Given** user has task, **When** user requests update with both title and description, **Then** system updates both fields appropriately
3. **Given** user uses keywords "change/update/rename", **When** agent processes command, **Then** identifies appropriate task and updates it
4. **Given** user tries to update non-existent task, **When** system processes request, **Then** returns friendly error message

---

### User Story 6 - Multi-Turn Conversations (Priority: P2)

Users can have contextual conversations where the AI remembers previous exchanges within the same conversation session, enabling natural follow-up questions and clarifications.

**Why this priority**: Differentiates AI chatbot from basic command interface - enables truly conversational experience. Important for user experience but not blocking MVP launch.

**Independent Test**: User creates task, then asks "What did I just add?" without providing task ID, system references conversation history to provide relevant answer.

**Acceptance Scenarios**:

1. **Given** user creates task in message 1, **When** user asks "Can you add a description to that?" in message 2, **Then** agent references previous task from context
2. **Given** conversation spans multiple exchanges, **When** user returns after browser refresh, **Then** system loads conversation history from database
3. **Given** user asks ambiguous follow-up question, **When** agent has context from previous messages, **Then** interprets question correctly using history
4. **Given** long conversation history, **When** agent processes new message, **Then** maintains relevant context while staying within token limits

---

### Edge Cases

- **Ambiguous natural language**: User types incomplete command like "groceries" - system should intelligently infer intent (add task) or ask clarifying question
- **Task not found by title**: User references task by partial or incorrect title - system should suggest closest matches or ask for task ID
- **Empty task lists**: User requests tasks when none exist - system provides friendly encouragement to create first task
- **Concurrent operations**: Multiple users or same user in multiple tabs performing operations simultaneously - database transactions ensure data integrity
- **Very long task titles/descriptions**: User exceeds 200/1000 character limits - system truncates gracefully or provides friendly error
- **Special characters in titles**: Tasks with quotes, apostrophes, or unicode - system handles without breaking queries
- **Conversation context limits**: Very long conversations approaching token limits - system summarizes or truncates older context intelligently
- **Tool invocation failures**: MCP tool fails (DB error, timeout) - agent receives error and communicates gracefully to user
- **Invalid JWT tokens**: Expired or malformed tokens - middleware rejects with 401 and clear error message
- **Cross-user data leakage**: Malicious attempt to access another user's tasks - user_id filtering prevents any data exposure

## Requirements

### Functional Requirements

- **FR-001**: System MUST persist all tasks in PostgreSQL database with user_id isolation
- **FR-002**: System MUST provide 5 MCP tools: add_task, list_tasks, complete_task, delete_task, update_task
- **FR-003**: System MUST expose single chat endpoint POST /api/{user_id}/chat accepting conversation_id (optional) and message (required)
- **FR-004**: System MUST verify JWT tokens on every API request via middleware before processing
- **FR-005**: System MUST enforce user_id from JWT matches URL parameter for all operations
- **FR-006**: System MUST store all conversation history in database (Conversation and Message tables)
- **FR-007**: System MUST support stateless operation with no in-memory session state
- **FR-008**: System MUST integrate OpenAI Agents SDK for natural language understanding and tool orchestration
- **FR-009**: System MUST enable tool composition allowing agent to chain multiple tool calls in single response
- **FR-010**: System MUST support task filtering by status: all, pending, completed
- **FR-011**: System MUST validate task title max 200 characters, description max 1000 characters
- **FR-012**: System MUST return descriptive error messages for tool failures, task not found, validation failures
- **FR-013**: Frontend MUST use OpenAI ChatKit component with domain allowlist configuration
- **FR-014**: Frontend MUST send Authorization Bearer token with every API request
- **FR-015**: System MUST handle 8 natural language command patterns (documented in spec)
- **FR-016**: System MUST support multi-turn conversations with context retention across messages
- **FR-017**: System MUST load conversation history from database on each request to maintain stateless architecture
- **FR-018**: System MUST index all user_id fields in database for query performance
- **FR-019**: System MUST use SQLModel ORM for type-safe database operations
- **FR-020**: System MUST implement CORS configuration via environment variables

### Key Entities

- **Task**: Represents a todo item with title, description, completion status, and timestamps. Belongs to a user via user_id. Core entity for task management operations.

- **Conversation**: Represents a chat session between user and AI agent. Contains sequence of messages. Enables conversation history tracking and multi-turn context.

- **Message**: Individual message within a conversation with role (user/assistant) and content. Building block of conversation history enabling context-aware responses.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can create tasks through natural language commands in under 5 seconds from message send to confirmation
- **SC-002**: Users can complete all 8 documented natural language command patterns successfully on first attempt
- **SC-003**: System correctly interprets user intent for task operations (add/list/complete/delete/update) with 90% accuracy
- **SC-004**: Users can resume conversations after browser refresh without losing context or needing to re-authenticate within session
- **SC-005**: System supports 100 concurrent users performing task operations without performance degradation
- **SC-006**: All task operations respect user isolation with zero cross-user data leakage incidents
- **SC-007**: System achieves 99.9% uptime for task operations during business hours
- **SC-008**: Users report task completion rate improvement of 30% compared to traditional todo apps (measured via user survey)
- **SC-009**: Average conversation requires fewer than 2 messages to complete task operation (measured via conversation analytics)
- **SC-010**: System response time remains under 2 seconds for 95th percentile of requests
- **SC-011**: Zero security incidents related to JWT verification or user_id filtering in production
- **SC-012**: 80% of users successfully complete first task creation without documentation or help

## Technical Constraints

### Database Schema

**Task Table**:
- user_id: string (indexed, required)
- id: integer (primary key, auto-increment)
- title: string (max 200 characters, required)
- description: string (max 1000 characters, optional)
- completed: boolean (default false)
- created_at: datetime (auto-set)
- updated_at: datetime (auto-updated)

**Conversation Table**:
- user_id: string (indexed, required)
- id: integer (primary key, auto-increment)
- created_at: datetime (auto-set)
- updated_at: datetime (auto-updated)

**Message Table**:
- user_id: string (indexed, required)
- id: integer (primary key, auto-increment)
- conversation_id: integer (foreign key to Conversation.id)
- role: enum ("user" | "assistant")
- content: string (required)
- created_at: datetime (auto-set)

### MCP Tool Schemas

**add_task**:
- Input: user_id (string, required), title (string, required, max 200), description (string, optional, max 1000)
- Output: {task_id: int, status: string, title: string}

**list_tasks**:
- Input: user_id (string, required), status (string, optional, values: "all"|"pending"|"completed")
- Output: array of {task_id: int, title: string, description: string, completed: boolean, created_at: string, updated_at: string}

**complete_task**:
- Input: user_id (string, required), task_id (integer, required)
- Output: {task_id: int, status: string, title: string}

**delete_task**:
- Input: user_id (string, required), task_id (integer, required)
- Output: {task_id: int, status: string, title: string}

**update_task**:
- Input: user_id (string, required), task_id (integer, required), title (string, optional), description (string, optional)
- Output: {task_id: int, status: string, title: string}

### API Contract

**Endpoint**: POST /api/{user_id}/chat

**Request Headers**:
- Authorization: Bearer {jwt_token} (required)

**Request Body**:
```json
{
  "conversation_id": 123,  // optional, creates new if omitted
  "message": "Add a task to buy groceries"  // required
}
```

**Response Body**:
```json
{
  "conversation_id": 123,
  "response": "I've added 'Buy groceries' to your task list!",
  "tool_calls": ["add_task"]
}
```

**Error Response**:
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired JWT token"
}
```

### Stateless Conversation Flow

1. Receive user message with optional conversation_id
2. Extract user_id from verified JWT token
3. Fetch conversation history from database (if conversation_id provided)
4. Build message array from history + new user message
5. Store new user message in Message table
6. Invoke OpenAI Agent with tools, history, and new message
7. Agent determines appropriate tool(s) to invoke
8. Execute tool(s) with user_id isolation
9. Store agent response in Message table
10. Return response with conversation_id and tool_calls to client
11. Server discards all state (ready for next request)

### Natural Language Command Mappings

**Trigger word → Tool mapping**:
- add/create/remember/need to → add_task
- show/see/list/what/display → list_tasks (with appropriate filter)
- done/complete/finished/did → complete_task
- delete/remove/cancel/forget → delete_task
- change/update/rename/modify → update_task

**Example Commands**:
1. "Add a task to buy groceries" → add_task(title="Buy groceries")
2. "Show me all my tasks" → list_tasks(status="all")
3. "What's pending?" → list_tasks(status="pending")
4. "Mark task 3 as complete" → complete_task(task_id=3)
5. "Delete the meeting task" → list_tasks to find + delete_task
6. "Change task 1 to 'Call mom tonight'" → update_task(task_id=1, title="Call mom tonight")
7. "I need to remember to pay bills" → add_task(title="Pay bills")
8. "What have I completed?" → list_tasks(status="completed")

## Environment Requirements

### Backend Environment Variables

- **DATABASE_URL**: Neon PostgreSQL connection string (required)
- **BETTER_AUTH_SECRET**: Shared secret for JWT verification (required)
- **OPENAI_API_KEY**: OpenAI API key for Agents SDK (required)
- **CORS_ORIGINS**: Comma-separated allowed origins (required, e.g., "http://localhost:3000,https://app.example.com")
- **CORS_ALLOW_CREDENTIALS**: Boolean flag for credentials (required, typically "true")

### Frontend Environment Variables

- **NEXT_PUBLIC_OPENAI_DOMAIN_KEY**: ChatKit domain key from OpenAI platform (required)
- **NEXT_PUBLIC_API_URL**: Backend API base URL (required, e.g., "http://localhost:8000")
- **BETTER_AUTH_SECRET**: Shared secret matching backend (required)

## Testing Strategy

### Unit Tests

Each function/component must have unit tests:
- Each MCP tool function (add_task, list_tasks, complete_task, delete_task, update_task)
- Database model CRUD operations (Task, Conversation, Message)
- JWT verification middleware
- User_id extraction from JWT
- Conversation history retrieval
- Message persistence logic
- Task validation (title/description length limits)
- Tool schema validation

### Integration Tests

Complete workflow testing:
- Full chat flow: send message → process → return response
- Multi-turn conversation with context retention
- Conversation resumption after simulated restart
- Database transaction integrity across operations
- Tool composition: agent invoking multiple tools in sequence
- Error propagation from tools to agent to user
- Authentication failures (invalid/expired JWT)
- CORS preflight and actual requests
- User isolation enforcement across all endpoints

### End-to-End Tests

User-facing scenarios via ChatKit:
- All 8 natural language command patterns
- Ambiguous requests requiring clarification
- Tool chaining (e.g., "show pending tasks and mark the first one done")
- Context-aware follow-ups ("add description to that task")
- Concurrent users performing operations simultaneously
- Session persistence across page refreshes
- Error handling with user-friendly messages
- Edge cases (empty lists, task not found, validation failures)

### Coverage Target

- Minimum 80% code coverage across all modules
- 100% coverage for security-critical code (JWT verification, user_id filtering)
- Tests must be written for each function at creation time
- Final integration validation before deployment

## Error Handling

### Error Categories and Responses

**Task Not Found (404)**:
- **Scenario**: User references non-existent task_id or title match fails
- **Response**: "I couldn't find that task. Could you provide the task ID or check your task list?"
- **HTTP Status**: 404 Not Found
- **Tool Behavior**: MCP tool returns error object, agent translates to friendly message

**Invalid Task ID (400)**:
- **Scenario**: User provides non-numeric task_id or negative number
- **Response**: "That doesn't look like a valid task ID. Task IDs are positive numbers like 1, 2, 3..."
- **HTTP Status**: 400 Bad Request
- **Tool Behavior**: Validation occurs before database query

**Database Errors (500)**:
- **Scenario**: PostgreSQL connection failure, query timeout, constraint violation
- **Response**: "I'm having trouble accessing your tasks right now. Please try again in a moment."
- **HTTP Status**: 500 Internal Server Error
- **Tool Behavior**: Exception caught, logged, generic error returned to user

**OpenAI API Errors (503)**:
- **Scenario**: OpenAI API unavailable, rate limit exceeded, timeout
- **Response**: "I'm temporarily unable to process your request. Please try again shortly."
- **HTTP Status**: 503 Service Unavailable
- **Fallback**: Return last known good response or prompt user to retry

**Authentication Errors (401)**:
- **Scenario**: Missing JWT token, expired token, invalid signature
- **Response**: {"error": "Unauthorized", "message": "Please log in to continue"}
- **HTTP Status**: 401 Unauthorized
- **Middleware Behavior**: Request rejected before reaching business logic

**Authorization Errors (403)**:
- **Scenario**: Valid JWT but user_id mismatch with URL parameter
- **Response**: {"error": "Forbidden", "message": "You can only access your own tasks"}
- **HTTP Status**: 403 Forbidden
- **Middleware Behavior**: User_id validation fails after JWT verification

**Validation Errors (400)**:
- **Scenario**: Title exceeds 200 chars, description exceeds 1000 chars, empty required fields
- **Response**: "Task title must be between 1 and 200 characters" or similar
- **HTTP Status**: 400 Bad Request
- **Tool Behavior**: Pydantic validation occurs before processing

**CORS Errors (403)**:
- **Scenario**: Request from origin not in CORS_ORIGINS environment variable
- **Response**: Browser blocks request, CORS preflight fails
- **HTTP Status**: 403 Forbidden (preflight rejection)
- **Prevention**: Configure CORS_ORIGINS to include all legitimate frontend domains

### HTTP Status Code Summary

- **200 OK**: Successful operation
- **400 Bad Request**: Validation failure, invalid input
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: Valid auth but insufficient permissions or CORS violation
- **404 Not Found**: Task not found
- **500 Internal Server Error**: Database error, unexpected server failure
- **503 Service Unavailable**: OpenAI API unavailable

### Error Response Format

All errors return consistent JSON structure:
```json
{
  "error": "ErrorType",
  "message": "User-friendly description",
  "code": "TASK_NOT_FOUND",
  "conversation_id": 123
}
```

Agent responses for tool errors use natural language:
```json
{
  "conversation_id": 123,
  "response": "I couldn't find that task. Could you provide the task ID?",
  "tool_calls": ["list_tasks"]
}
```

## Acceptance Criteria

### Core Functionality

- [ ] **AC-001**: Users can manage tasks (add, list, complete, delete, update) exclusively via natural language chat interface
- [ ] **AC-002**: All 8 documented natural language command patterns execute successfully and return expected results
- [ ] **AC-003**: Agent correctly interprets user intent for task operations with 90% accuracy across diverse phrasings
- [ ] **AC-004**: MCP tools return exact JSON schemas as documented (task_id, status, title fields)
- [ ] **AC-005**: Task operations complete within 5 seconds from user message to response

### Stateless Architecture

- [ ] **AC-006**: Conversations persist across server restarts - history loaded from database on every request
- [ ] **AC-007**: No in-memory session state maintained - server can be restarted without losing conversations
- [ ] **AC-008**: Multiple backend instances can serve same user without session affinity
- [ ] **AC-009**: Conversation history correctly resumes after browser refresh

### Security & Isolation

- [ ] **AC-010**: User isolation enforced - users can only see and modify their own tasks
- [ ] **AC-011**: Zero cross-user data leakage in all scenarios including malicious attempts
- [ ] **AC-012**: All API requests require valid JWT token in Authorization header
- [ ] **AC-013**: Requests with user_id mismatch (JWT vs URL parameter) are rejected with 403
- [ ] **AC-014**: CORS accepts requests only from origins listed in CORS_ORIGINS environment variable

### Error Handling

- [ ] **AC-015**: Task not found returns user-friendly message (not technical error)
- [ ] **AC-016**: Invalid task_id provides helpful guidance about expected format
- [ ] **AC-017**: Database errors return HTTP 500 with generic message (no sensitive details exposed)
- [ ] **AC-018**: OpenAI API errors trigger fallback response or retry prompt
- [ ] **AC-019**: All error responses include appropriate HTTP status codes (401, 403, 404, 500, 503)

### Testing & Quality

- [ ] **AC-020**: Minimum 80% code coverage achieved across all modules
- [ ] **AC-021**: 100% coverage for security-critical code (JWT verification, user_id filtering)
- [ ] **AC-022**: All unit tests pass for MCP tools, database models, middleware
- [ ] **AC-023**: All integration tests pass for full chat flow, multi-turn conversations
- [ ] **AC-024**: All E2E tests pass for 8 natural language commands via ChatKit

### Deployment

- [ ] **AC-025**: Frontend deployed to Vercel and accessible via public URL
- [ ] **AC-026**: Backend deployed with public URL and reachable from frontend
- [ ] **AC-027**: Frontend successfully connects to backend API (CORS configured correctly)
- [ ] **AC-028**: ChatKit domain added to OpenAI platform allowlist and NEXT_PUBLIC_OPENAI_DOMAIN_KEY set
- [ ] **AC-029**: Database migrations applied to Neon PostgreSQL instance
- [ ] **AC-030**: All required environment variables configured in production (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET, CORS_ORIGINS, NEXT_PUBLIC_OPENAI_DOMAIN_KEY, NEXT_PUBLIC_API_URL)

## Assumptions

- Users have valid Better Auth JWT tokens before accessing chat endpoint
- Frontend handles initial authentication flow and token refresh
- OpenAI API availability and rate limits are acceptable for expected user load
- Neon PostgreSQL Serverless can handle expected concurrent connection load
- Browser supports modern JavaScript features required by ChatKit
- Users have stable internet connection for real-time chat experience
- Task titles and descriptions are primarily English text (no specific i18n requirements)
- Conversation history retention is indefinite (no automatic cleanup policy)
- Single deployment region acceptable (no multi-region requirements specified)

## Dependencies

- **External Services**: OpenAI API (Agents SDK), Neon PostgreSQL, Better Auth service
- **Frontend Dependencies**: OpenAI ChatKit, Next.js 16 App Router
- **Backend Dependencies**: FastAPI, SQLModel, Official MCP SDK (Python), OpenAI Python SDK
- **Authentication**: Better Auth service must be running and accessible
- **Database**: Neon PostgreSQL instance must be provisioned with connection URL

## Out of Scope

- Task priority levels or categorization beyond completed/pending
- Task due dates, reminders, or scheduling
- Task sharing or collaboration between users
- Rich text formatting in task descriptions
- File attachments or media in tasks
- Task templates or recurring tasks
- Mobile native apps (web-only via ChatKit)
- Offline mode or local storage
- Task import/export functionality
- Analytics dashboard or reporting
- Admin panel for user management
- Rate limiting per user (relies on infrastructure-level controls)
- Multi-language support (English only)
- Voice input/output
- Task search beyond list filtering

## Notes

- This specification focuses on WHAT users need and WHY, avoiding implementation details of HOW
- Architecture decisions (FastAPI, OpenAI Agents SDK, MCP tools) are documented in constitution and plan documents
- Success criteria are measurable and technology-agnostic
- All requirements support the core value proposition: natural language task management via conversational AI

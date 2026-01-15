---
id: 002
title: AI Todo Chatbot Specification
stage: spec
date: 2026-01-13
surface: agent
model: claude-sonnet-4-5
feature: ai-todo-chatbot
branch: 001-ai-todo-chatbot
user: system
command: /sp.specify
labels: ["spec", "ai-chatbot", "mcp-tools", "openai-agents", "fastapi", "chatkit"]
links:
  spec: specs/001-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-todo-chatbot/spec.md
  - specs/001-ai-todo-chatbot/checklists/requirements.md
tests:
  - none
---

## Prompt

Define Specification for AI Todo Chatbot:

- **DATABASE MODELS** (exact fields):
  - Task: user_id (str indexed), id (int PK auto), title (str max 200 required), description (str max 1000 optional), completed (bool default False), created_at (datetime), updated_at (datetime)
  - Conversation: user_id (str indexed), id (int PK auto), created_at (datetime), updated_at (datetime)
  - Message: user_id (str indexed), id (int PK auto), conversation_id (int FK), role (enum "user"|"assistant"), content (str required), created_at (datetime)

- **MCP TOOLS** (5 tools with exact schemas):
  1. add_task(user_id: str required, title: str required max 200, description: str optional max 1000) → {task_id: int, status: str, title: str}
  2. list_tasks(user_id: str required, status: optional "all"|"pending"|"completed") → array of task objects
  3. complete_task(user_id: str required, task_id: int required) → {task_id: int, status: str, title: str}
  4. delete_task(user_id: str required, task_id: int required) → {task_id: int, status: str, title: str}
  5. update_task(user_id: str required, task_id: int required, title: str optional, description: str optional) → {task_id: int, status: str, title: str}

- **CHAT API ENDPOINT**:
  - POST /api/{user_id}/chat
  - Request: {conversation_id?: int, message: str required}
  - Response: {conversation_id: int, response: str, tool_calls: str[]}

- **9-STEP STATELESS CONVERSATION FLOW**: (1) Receive user message, (2) Fetch conversation history from DB, (3) Build message array, (4) Store user message, (5) Run OpenAI Agent with MCP tools, (6) Agent invokes tools, (7) Store assistant response, (8) Return response, (9) Server holds NO state

- **AGENT BEHAVIOR** (trigger word mapping): add/create/remember → add_task, see/show/list → list_tasks, done/complete/finished → complete_task, delete/remove/cancel → delete_task, change/update/rename → update_task

- **8 NATURAL LANGUAGE COMMANDS**: (1) "Add a task to buy groceries", (2) "Show me all my tasks", (3) "What's pending?", (4) "Mark task 3 as complete", (5) "Delete the meeting task", (6) "Change task 1 to 'Call mom tonight'", (7) "I need to remember to pay bills", (8) "What have I completed?"

- **AUTHENTICATION**: Better Auth JWT on all endpoints, Authorization Bearer header required, JWT verification middleware, user isolation via user_id filtering, shared BETTER_AUTH_SECRET

- **TESTING REQUIREMENTS**: Unit (each MCP tool, DB models, JWT verification), Integration (full chat flow, multi-turn, resume after restart), E2E (all 8 NL commands via ChatKit), ≥80% coverage

## Response snapshot

Created comprehensive specification for AI Todo Chatbot with 6 user stories (prioritized P1-P3):

**P1 MVP Stories**:
1. Add Tasks via Natural Language - Core value proposition enabling intuitive task creation
2. View and Filter Tasks - Essential visibility for task management

**P2 Stories**:
3. Complete Tasks - Using task IDs or natural language descriptions
4. Multi-Turn Conversations - Context retention for conversational experience

**P3 Enhancement Stories**:
5. Delete Tasks - Remove unwanted tasks
6. Update Tasks - Modify titles and descriptions

Specification includes:
- 20 functional requirements (FR-001 to FR-020) covering database, MCP tools, API, security, testing
- 12 measurable success criteria (all technology-agnostic: response times, accuracy rates, user satisfaction)
- Complete database schema (Task, Conversation, Message tables with indexes)
- 5 MCP tool schemas with exact input/output contracts
- API contract for POST /api/{user_id}/chat endpoint
- 11-step stateless conversation flow
- Natural language command mappings for all 8 example commands
- Comprehensive testing strategy (unit, integration, E2E with 80% coverage target)
- Environment variables for backend and frontend
- Dependencies, assumptions, and out-of-scope items clearly defined

All content focuses on WHAT users need and WHY, avoiding implementation HOW. Success criteria are measurable and technology-agnostic.

## Outcome

- ✅ Impact: Complete feature specification ready for planning phase, covering all aspects of AI Todo Chatbot. Updated with comprehensive error handling (8 error types, HTTP codes) and 30 acceptance criteria across 5 categories (functionality, architecture, security, errors, deployment).
- 🧪 Tests: Testing strategy defined (80% coverage, unit/integration/E2E), no tests written yet (spec phase)
- 📁 Files: Created/updated spec.md, requirements checklist, PHR in specs/001-ai-todo-chatbot/
- 🔁 Next prompts: /sp.plan for implementation planning
- 🧠 Reflection: Specification complete with zero [NEEDS CLARIFICATION] markers. All user stories independently testable. Error handling and acceptance criteria comprehensive. Ready for architecture planning.

## Evaluation notes (flywheel)

- Failure modes observed: Initial directory structure created outside Phase03 - corrected by creating specs/ within Phase03
- Graders run and results (PASS/FAIL): PASS - All checklist items validated, no implementation details leaked, success criteria technology-agnostic
- Prompt variant (if applicable): comprehensive-spec-with-detailed-schemas-v1
- Next experiment (smallest change to try): Validate spec against constitution principles before planning phase

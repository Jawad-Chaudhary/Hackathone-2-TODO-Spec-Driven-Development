# Implementation Plan: AI Todo Chatbot

**Branch**: `001-ai-todo-chatbot` | **Date**: 2026-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-ai-todo-chatbot/spec.md`

## Summary

Build a conversational AI todo chatbot using OpenAI Agents SDK with MCP tool integration, stateless FastAPI backend, and Next.js ChatKit frontend. The system enables users to manage tasks through natural language commands with complete user isolation, database-backed conversation persistence, and horizontal scalability.

**Core Capabilities**:
- 5 MCP tools (add/list/complete/delete/update tasks) via Official Python SDK
- Single stateless FastAPI endpoint POST /api/{user_id}/chat
- JWT-based authentication with Better Auth
- Database-first architecture (Neon PostgreSQL)
- OpenAI ChatKit frontend with domain allowlist

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Next.js 16 (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Official MCP SDK (Python), OpenAI Agents SDK, OpenAI ChatKit, Better Auth
**Storage**: Neon Serverless PostgreSQL (async SQLAlchemy + SQLModel ORM)
**Testing**: pytest with pytest-asyncio, httpx for API testing, 80% minimum coverage
**Target Platform**: Cloud (Vercel for frontend, any Python hosting for backend)
**Project Type**: Web application (separate backend/frontend)
**Performance Goals**: <2s response time (p95), 100 concurrent users without degradation
**Constraints**: Stateless architecture (no in-memory session state), user isolation (zero data leakage), OpenAI API rate limits
**Scale/Scope**: Small-medium scale (hundreds of users), conversational task management, 8 natural language command patterns

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Stateless Architecture
- [x] No in-memory state storage - all state in PostgreSQL
- [x] Conversation history loaded from DB on every request
- [x] Backend can be restarted without losing state
- [x] Horizontal scaling supported without session affinity

### ✅ II. User Isolation & Security
- [x] JWT verification middleware on all endpoints
- [x] user_id filtering on all database queries
- [x] BETTER_AUTH_SECRET shared between services
- [x] CORS configured via environment variables
- [x] All models include indexed user_id fields

### ✅ III. Tool-Based AI Architecture
- [x] 5 MCP tools using Official Python MCP SDK
- [x] One tool per CRUD operation (single responsibility)
- [x] Clear input/output schemas with validation
- [x] Stateless tool handlers (DB session per call)
- [x] Tool composition enabled for multi-step operations

### ✅ IV. Database-First Conversation State
- [x] Task, Conversation, Message models defined
- [x] All user_id fields indexed
- [x] SQLModel ORM for type-safe operations
- [x] Async database operations throughout
- [x] Neon PostgreSQL as target database

### ✅ V. Single Endpoint Simplicity
- [x] POST /api/{user_id}/chat as sole endpoint
- [x] user_id in path validated against JWT
- [x] All business logic routed through agent + tools
- [x] Response includes conversation_id and tool_calls

### ✅ VI. Test-First Development
- [x] pytest + pytest-asyncio + httpx configured
- [x] 80% minimum coverage target
- [x] Unit tests for all MCP tools and models
- [x] Integration tests for chat flow
- [x] E2E tests for 8 natural language commands

**Result**: ✅ All constitutional requirements satisfied. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-todo-chatbot/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 - Technology research
├── data-model.md        # Phase 1 - Database schema
├── quickstart.md        # Phase 1 - Setup instructions
├── contracts/           # Phase 1 - API contracts
│   └── chat-api.yaml    # OpenAPI spec for chat endpoint
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 - Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root - Phase03/)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py              # Task SQLModel
│   │   ├── conversation.py      # Conversation SQLModel
│   │   └── message.py           # Message SQLModel
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py            # MCP Server initialization
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── add_task.py      # add_task tool
│   │       ├── list_tasks.py    # list_tasks tool
│   │       ├── complete_task.py # complete_task tool
│   │       ├── delete_task.py   # delete_task tool
│   │       └── update_task.py   # update_task tool
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── agent.py             # OpenAI Agent initialization
│   │   └── runner.py            # Agent runner with history
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py               # FastAPI app + CORS
│   │   ├── middleware.py        # JWT verification
│   │   ├── routes.py            # POST /api/{user_id}/chat
│   │   └── schemas.py           # Pydantic request/response
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py        # Async engine/session
│   │   └── session.py           # DB session dependency
│   └── main.py                  # Application entry point
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── unit/
│   │   ├── test_models.py       # Model CRUD tests
│   │   ├── test_tools.py        # MCP tool tests
│   │   └── test_auth.py         # JWT middleware tests
│   ├── integration/
│   │   ├── test_chat_flow.py    # Complete chat cycle
│   │   ├── test_stateless.py    # Restart simulation
│   │   └── test_isolation.py    # User isolation tests
│   └── e2e/
│       └── test_nl_commands.py  # 8 NL command patterns
├── alembic/
│   ├── versions/                # Migration scripts
│   ├── env.py
│   └── alembic.ini
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
└── .env.example                 # Environment template

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Home page
│   │   ├── chat/
│   │   │   └── page.tsx         # Chat interface (ChatKit)
│   │   ├── login/
│   │   │   └── page.tsx         # Login page
│   │   └── signup/
│   │       └── page.tsx         # Signup page
│   ├── lib/
│   │   ├── auth.ts              # Better Auth client
│   │   └── api.ts               # Backend API client
│   └── components/
│       └── ChatInterface.tsx    # ChatKit wrapper
├── public/
├── package.json                 # Node dependencies
├── tsconfig.json                # TypeScript config
├── next.config.js               # Next.js config
└── .env.local.example           # Frontend env template
```

**Structure Decision**: Web application structure (Option 2) selected due to separate backend (Python FastAPI) and frontend (Next.js) requirements. Backend provides stateless REST API, frontend consumes it via ChatKit interface.

## Complexity Tracking

> No constitutional violations detected. All principles satisfied.

(This section intentionally empty - no violations to justify)

---

## Phase 0: Research & Technology Validation

### Research Tasks

1. **Official MCP SDK Python Patterns**
   - **Question**: How to initialize MCP server with stdio transport and register async tools?
   - **Findings**: Use `mcp.server.stdio.stdio_server()` context manager with `Server("name")`. Register tools with `@server.call_tool()` decorator and input schemas via `Tool` class with JSON Schema validation.
   - **Decision**: Use stdio pattern with async tool handlers, DB session per tool invocation
   - **Code Pattern**:
     ```python
     from mcp.server import Server
     from mcp.server.stdio import stdio_server
     import mcp.types as types

     server = Server("todo-mcp-server")

     @server.call_tool()
     async def add_task(arguments: dict) -> list[types.TextContent]:
         # Validate arguments
         # Create DB session
         # Execute logic
         # Return JSON as TextContent
         return [types.TextContent(type="text", text=json.dumps(result))]

     async def main():
         async with stdio_server() as (read_stream, write_stream):
             await server.run(read_stream, write_stream, server.create_initialization_options())
     ```

2. **OpenAI Agents SDK Integration**
   - **Question**: How to initialize agent with MCP tools and pass conversation history?
   - **Findings**: Use `OpenAI` client with `Agent` class. Define functions matching MCP tool schemas. Use `Runner` with `messages` parameter for history.
   - **Decision**: Convert MCP tools to OpenAI function format, use `Runner.run()` with messages array
   - **Code Pattern**:
     ```python
     from agents import Agent, Runner, OpenAIChatCompletionsModel

     model = OpenAIChatCompletionsModel(model="gpt-4", api_key=os.getenv("OPENAI_API_KEY"))

     agent = Agent(
         model=model,
         system_prompt="You are a helpful task management assistant...",
         functions=[add_task_func, list_tasks_func, ...]  # MCP tool wrappers
     )

     runner = Runner(agent=agent)
     result = await runner.run(messages=[{"role": "user", "content": "..."}])
     ```

3. **Stateless Conversation Flow with PostgreSQL**
   - **Question**: How to load conversation history and maintain stateless architecture?
   - **Findings**: Query messages by conversation_id before each agent run, build messages array, store new messages immediately after agent response
   - **Decision**: Load history from DB → Build messages array → Run agent → Store response → Return (no caching)
   - **Flow**:
     1. Extract conversation_id from request (or create new)
     2. `SELECT * FROM messages WHERE conversation_id=? ORDER BY created_at`
     3. Build `[{"role": msg.role, "content": msg.content} for msg in history]`
     4. Append new user message to array
     5. Save user message to DB
     6. `await runner.run(messages=message_array)`
     7. Save assistant response to DB
     8. Return response (server forgets everything)

4. **JWT Authentication with FastAPI**
   - **Question**: Middleware vs Depends for JWT verification? How to extract user_id?
   - **Findings**: Use middleware for global verification, Depends for per-endpoint user_id extraction. Decode with `jwt.decode()` using HS256 algorithm.
   - **Decision**: Middleware for token validation, Depends for user_id validation against path parameter
   - **Code Pattern**:
     ```python
     from fastapi import Depends, HTTPException, Security
     from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
     import jwt

     security = HTTPBearer()

     async def verify_jwt(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
         try:
             payload = jwt.decode(
                 credentials.credentials,
                 os.getenv("BETTER_AUTH_SECRET"),
                 algorithms=["HS256"]
             )
             return payload
         except jwt.ExpiredSignatureError:
             raise HTTPException(401, "Token expired")
         except jwt.InvalidTokenError:
             raise HTTPException(401, "Invalid token")

     async def validate_user_id(user_id: str, token: dict = Depends(verify_jwt)):
         token_user_id = token.get("sub") or token.get("user_id")
         if token_user_id != user_id:
             raise HTTPException(403, "User ID mismatch")
         return user_id
     ```

5. **Better Auth + ChatKit Integration**
   - **Question**: How to pass JWT from Better Auth to backend API in ChatKit?
   - **Findings**: Store JWT in React state after Better Auth login, pass in Authorization header via ChatKit's `fetch` override or custom API client
   - **Decision**: Use Better Auth React hooks for session management, custom fetch wrapper for API calls
   - **Code Pattern**:
     ```typescript
     import { useSession } from 'better-auth/react'

     const { data: session } = useSession()

     const handleMessage = async (message: string, conversationId?: number) => {
       const response = await fetch(`${API_URL}/api/${session.user.id}/chat`, {
         method: 'POST',
         headers: {
           'Authorization': `Bearer ${session.token}`,
           'Content-Type': 'application/json'
         },
         body: JSON.stringify({ message, conversation_id: conversationId })
       })
       return response.json()
     }
     ```

6. **Testing Strategy for Async + AI Systems**
   - **Question**: How to mock OpenAI API calls? In-memory SQLite vs real Neon for tests?
   - **Findings**: Use `pytest-mock` or `unittest.mock` for OpenAI client. SQLite in-memory for unit tests (fast), test DB for integration tests (realistic)
   - **Decision**: Mock OpenAI in unit tests, use SQLite in-memory for unit, separate test Neon DB for integration
   - **Fixture Pattern**:
     ```python
     import pytest
     from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

     @pytest.fixture
     async def db_session():
         engine = create_async_engine("sqlite+aiosqlite:///:memory:")
         async with engine.begin() as conn:
             await conn.run_sync(Base.metadata.create_all)
         async with AsyncSession(engine) as session:
             yield session

     @pytest.fixture
     def mock_openai(mocker):
         mock = mocker.patch("agents.Runner.run")
         mock.return_value = {"response": "Task created!", "tool_calls": ["add_task"]}
         return mock
     ```

7. **ChatKit Domain Allowlist Workflow**
   - **Question**: When to configure domain allowlist - before or after deployment?
   - **Findings**: Deploy frontend to Vercel first to get domain, then add domain to OpenAI platform settings, get domain key, set NEXT_PUBLIC_OPENAI_DOMAIN_KEY, redeploy
   - **Decision**: Post-deployment configuration (deploy → configure OpenAI → set env → redeploy)
   - **Steps**:
     1. Deploy Next.js app to Vercel (get `your-app.vercel.app`)
     2. Go to OpenAI Platform → Settings → Domain Allowlist
     3. Add `your-app.vercel.app`
     4. Copy generated domain key
     5. Set `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` in Vercel env
     6. Redeploy (trigger new build to use env var)

8. **CORS Configuration for FastAPI + Vercel**
   - **Question**: How to parse CORS_ORIGINS env and configure middleware?
   - **Findings**: Split comma-separated string, use `CORSMiddleware` with `allow_origins`, `allow_credentials=True`, explicit methods/headers
   - **Decision**: Parse env at startup, configure middleware with explicit settings
   - **Code Pattern**:
     ```python
     from fastapi.middleware.cors import CORSMiddleware

     origins = os.getenv("CORS_ORIGINS", "").split(",")
     origins = [origin.strip() for origin in origins if origin.strip()]

     app.add_middleware(
         CORSMiddleware,
         allow_origins=origins,
         allow_credentials=True,
         allow_methods=["POST", "GET", "OPTIONS"],
         allow_headers=["Authorization", "Content-Type"]
     )
     ```

### Research Summary

All technical unknowns resolved. Key patterns documented:
- MCP SDK: stdio server with async tools, JSON Schema validation
- OpenAI Agents: Function calling with conversation history
- Stateless flow: DB query → build messages → run agent → save → forget
- Auth: Middleware for JWT, Depends for user_id validation
- Testing: Mock OpenAI, SQLite for unit, test DB for integration
- ChatKit: Post-deployment domain allowlist configuration

**Output**: Documented patterns ready for Phase 1 design.

---

## Phase 1: Data Model, Contracts & Quickstart

### Database Schema (data-model.md)

**File**: `specs/001-ai-todo-chatbot/data-model.md`

#### Task Table

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    completed BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    INDEX idx_tasks_user_id (user_id),
    CHECK (char_length(title) >= 1 AND char_length(title) <= 200),
    CHECK (description IS NULL OR char_length(description) <= 1000)
);
```

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, max_length=255)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### Conversation Table

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    INDEX idx_conversations_user_id (user_id)
);
```

**SQLModel Definition**:
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### Message Table

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    INDEX idx_messages_user_id (user_id),
    INDEX idx_messages_conversation_id (conversation_id)
);
```

**SQLModel Definition**:
```python
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, max_length=255)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Relationships**:
- Conversation → Messages (1:many) via `conversation_id` FK
- All tables → User (via `user_id` string, external to DB - managed by Better Auth)

**Migrations**: Alembic autogenerate from SQLModel schemas

### API Contracts (contracts/)

**File**: `specs/001-ai-todo-chatbot/contracts/chat-api.yaml`

```yaml
openapi: 3.0.3
info:
  title: AI Todo Chatbot API
  version: 1.0.0
  description: Stateless conversational task management API

servers:
  - url: http://localhost:8000
    description: Local development
  - url: https://api.production.com
    description: Production

paths:
  /api/{user_id}/chat:
    post:
      summary: Send chat message
      description: Process user message with AI agent and MCP tools
      operationId: chat
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
          description: User identifier (must match JWT claim)
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - message
              properties:
                conversation_id:
                  type: integer
                  description: Existing conversation ID (optional, creates new if omitted)
                  example: 123
                message:
                  type: string
                  description: User's natural language message
                  example: "Add a task to buy groceries"
                  minLength: 1
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                required:
                  - conversation_id
                  - response
                  - tool_calls
                properties:
                  conversation_id:
                    type: integer
                    description: Conversation ID for this exchange
                    example: 123
                  response:
                    type: string
                    description: AI agent's natural language response
                    example: "I've added 'Buy groceries' to your task list!"
                  tool_calls:
                    type: array
                    items:
                      type: string
                    description: List of MCP tools invoked
                    example: ["add_task"]
        '400':
          description: Bad request (validation error)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '401':
          description: Unauthorized (missing or invalid JWT)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '403':
          description: Forbidden (user_id mismatch)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '404':
          description: Not found (conversation doesn't exist)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '500':
          description: Internal server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: Better Auth JWT token

  schemas:
    Error:
      type: object
      required:
        - error
        - message
      properties:
        error:
          type: string
          example: "Unauthorized"
        message:
          type: string
          example: "Invalid or expired JWT token"
        code:
          type: string
          example: "INVALID_TOKEN"
        conversation_id:
          type: integer
          description: Conversation ID if applicable
```

### Quickstart Guide (quickstart.md)

**File**: `specs/001-ai-todo-chatbot/quickstart.md`

```markdown
# AI Todo Chatbot - Quickstart Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- Neon PostgreSQL account (free tier works)
- OpenAI API key
- Better Auth instance (or local setup)

## Backend Setup

### 1. Install Dependencies

\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

### 2. Environment Configuration

Create `.env` from `.env.example`:

\`\`\`bash
DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname
BETTER_AUTH_SECRET=your-secret-key
OPENAI_API_KEY=sk-...
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
CORS_ALLOW_CREDENTIALS=true
\`\`\`

### 3. Database Migrations

\`\`\`bash
alembic upgrade head
\`\`\`

### 4. Run Backend

\`\`\`bash
uvicorn src.main:app --reload --port 8000
\`\`\`

API available at `http://localhost:8000`

### 5. Run Tests

\`\`\`bash
pytest --cov=src --cov-report=html --cov-fail-under=80
\`\`\`

## Frontend Setup

### 1. Install Dependencies

\`\`\`bash
cd frontend
npm install
\`\`\`

### 2. Environment Configuration

Create `.env.local` from `.env.local.example`:

\`\`\`bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key
BETTER_AUTH_SECRET=your-secret-key  # Must match backend
\`\`\`

### 3. Run Frontend

\`\`\`bash
npm run dev
\`\`\`

App available at `http://localhost:3000`

## Testing the Chat Flow

1. Open `http://localhost:3000/login`
2. Sign in with Better Auth
3. Navigate to `/chat`
4. Try commands:
   - "Add a task to buy groceries"
   - "Show me all my tasks"
   - "Mark task 1 as complete"

## Deployment

### Backend (Any Python Host)

1. Set environment variables
2. Run migrations: `alembic upgrade head`
3. Start with: `uvicorn src.main:app --host 0.0.0.0 --port 8000`

### Frontend (Vercel)

1. Connect GitHub repo to Vercel
2. Deploy (get domain like `your-app.vercel.app`)
3. Add domain to OpenAI Platform → Settings → Domain Allowlist
4. Copy domain key
5. Set `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` in Vercel env
6. Redeploy

## Troubleshooting

**CORS Errors**: Ensure frontend URL in `CORS_ORIGINS` backend env
**401 Unauthorized**: Check JWT token format and BETTER_AUTH_SECRET match
**ChatKit not loading**: Verify domain allowlist configuration
**Database errors**: Check DATABASE_URL connection string and migrations
\`\`\`

---

## Architecture Diagrams

### System Architecture

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────────────────────────────┐
│  Next.js Frontend (Vercel)              │
│  ┌────────────────────────────────────┐ │
│  │ OpenAI ChatKit Component           │ │
│  │ - Domain allowlisted               │ │
│  │ - JWT from Better Auth             │ │
│  └────────────────────────────────────┘ │
└────────┬────────────────────────────────┘
         │ POST /api/{user_id}/chat
         │ Authorization: Bearer <JWT>
         ▼
┌──────────────────────────────────────────────┐
│  FastAPI Backend (Stateless)                 │
│  ┌───────────────────────────────────────┐  │
│  │ JWT Verification Middleware           │  │
│  │ - Validate token                      │  │
│  │ - Extract user_id                     │  │
│  │ - Match against path param            │  │
│  └───────────────────────────────────────┘  │
│                   │                          │
│                   ▼                          │
│  ┌───────────────────────────────────────┐  │
│  │ Chat Endpoint Handler                 │  │
│  │ 1. Load conversation from DB          │  │
│  │ 2. Build message history array        │  │
│  │ 3. Save user message                  │  │
│  └───────────────┬───────────────────────┘  │
│                  │                           │
│                  ▼                           │
│  ┌───────────────────────────────────────┐  │
│  │ OpenAI Agent Runner                   │  │
│  │ - System prompt                       │  │
│  │ - Conversation history                │  │
│  │ - Function calling enabled            │  │
│  └───────────────┬───────────────────────┘  │
│                  │                           │
│                  ▼                           │
│  ┌───────────────────────────────────────┐  │
│  │ MCP Server (Official Python SDK)      │  │
│  │ ┌─────────────────────────────────┐   │  │
│  │ │ add_task                        │   │  │
│  │ │ list_tasks                      │   │  │
│  │ │ complete_task                   │   │  │
│  │ │ delete_task                     │   │  │
│  │ │ update_task                     │   │  │
│  │ └─────────────┬───────────────────┘   │  │
│  └───────────────┼───────────────────────┘  │
│                  │                           │
│                  ▼                           │
│  ┌───────────────────────────────────────┐  │
│  │ Database Layer (SQLModel + Async)     │  │
│  │ - User isolation (user_id filter)     │  │
│  │ - Session per request                 │  │
│  └───────────────┬───────────────────────┘  │
└──────────────────┼──────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│  Neon PostgreSQL (Serverless)                │
│  ┌─────────────┐ ┌──────────────┐ ┌──────┐  │
│  │   tasks     │ │conversations │ │ msgs │  │
│  │ (user_id)   │ │  (user_id)   │ │(u_id)│  │
│  └─────────────┘ └──────────────┘ └──────┘  │
└──────────────────────────────────────────────┘
```

### 11-Step Stateless Conversation Flow

```
1. [Client] POST /api/{user_id}/chat
   Body: {conversation_id?: 123, message: "Add task"}
   Headers: Authorization: Bearer <JWT>

2. [Middleware] Verify JWT
   - Decode with BETTER_AUTH_SECRET (HS256)
   - Extract user_id from token (sub or user_id claim)
   - Compare with path parameter
   - ❌ Mismatch → 403 Forbidden
   - ✅ Match → Continue

3. [Handler] Get/Create Conversation
   - If conversation_id provided:
     Query: SELECT * FROM conversations WHERE id=? AND user_id=?
     ❌ Not found → 404
   - Else:
     INSERT INTO conversations (user_id) VALUES (?) RETURNING id

4. [Handler] Load Message History
   Query: SELECT role, content FROM messages
          WHERE conversation_id=? ORDER BY created_at ASC

5. [Handler] Build Messages Array
   messages = [
     {"role": msg.role, "content": msg.content}
     for msg in history
   ] + [{"role": "user", "content": request.message}]

6. [Handler] Save User Message
   INSERT INTO messages (user_id, conversation_id, role, content)
   VALUES (user_id, conversation_id, 'user', request.message)
   COMMIT

7. [Agent Runner] Execute Agent
   response = await runner.run(messages=messages)
   - Agent analyzes message
   - Determines tool to invoke (add_task, list_tasks, etc.)
   - Calls MCP tool with parameters

8. [MCP Tool] Execute Tool Logic
   Example: add_task
   - Create async DB session
   - Validate input (user_id, title length)
   - INSERT INTO tasks (user_id, title, ...) VALUES (...)
   - COMMIT
   - Return {"task_id": 1, "status": "created", "title": "..."}
   - Close session

9. [Agent Runner] Format Response
   - Agent receives tool result
   - Generates natural language response
   - Returns: (response_text, [tool_names])

10. [Handler] Save Assistant Message
    INSERT INTO messages (user_id, conversation_id, role, content)
    VALUES (user_id, conversation_id, 'assistant', response_text)
    COMMIT

    UPDATE conversations SET updated_at=NOW() WHERE id=conversation_id

11. [Handler] Return Response
    {
      "conversation_id": 123,
      "response": "I've added 'Buy groceries' to your task list!",
      "tool_calls": ["add_task"]
    }

    ⚡ Server holds NO state - ready for next request
```

### MCP Tool Execution Sequence

```
User Message: "Add a task to buy groceries"
         │
         ▼
[OpenAI Agent] Analyzes intent
         │
         ├─ Trigger words detected: "add", "task"
         │
         ▼
[Agent] Decides to call: add_task
         │
         ├─ Parameters extracted:
         │  {
         │    "user_id": "user_123",
         │    "title": "Buy groceries",
         │    "description": null
         │  }
         │
         ▼
[MCP Tool: add_task]
         │
         ├─ 1. Create async DB session
         │
         ├─ 2. Validate input
         │     - user_id not empty ✓
         │     - title 1-200 chars ✓
         │
         ├─ 3. Execute query
         │     INSERT INTO tasks (user_id, title, completed)
         │     VALUES ('user_123', 'Buy groceries', false)
         │     RETURNING id
         │
         ├─ 4. Commit transaction
         │
         ├─ 5. Close session
         │
         ▼
[Tool Result]
{
  "task_id": 42,
  "status": "created",
  "title": "Buy groceries"
}
         │
         ▼
[Agent] Receives result
         │
         ├─ Formats friendly response
         │
         ▼
[Agent Response]
"I've added 'Buy groceries' to your task list! It's task #42."
```

---

## Agent Behavior Specification

### Trigger Word Mapping Table

| User Intent | Trigger Words | MCP Tool Invoked | Example Message |
|-------------|---------------|------------------|-----------------|
| **Create Task** | add, create, remember, need to, remind me | `add_task` | "Add a task to buy groceries" |
| **View All Tasks** | show, see, list, display, what are, tell me | `list_tasks(status="all")` | "Show me all my tasks" |
| **View Pending** | pending, incomplete, not done, what's left, todo | `list_tasks(status="pending")` | "What's pending?" |
| **View Completed** | completed, done, finished, what did I, accomplished | `list_tasks(status="completed")` | "What have I completed?" |
| **Complete Task** | complete, done, finished, mark as done, did, finish | `complete_task` | "Mark task 3 as complete" |
| **Delete Task** | delete, remove, cancel, forget, get rid of | `delete_task` (may require `list_tasks` first) | "Delete the meeting task" |
| **Update Task** | change, update, rename, modify, edit | `update_task` | "Change task 1 to 'Call mom tonight'" |

### Example Conversations for 8 Natural Language Commands

**Command 1: Add Task**
```
User: "Add a task to buy groceries"
Agent: Invokes add_task(user_id="user_123", title="Buy groceries")
Response: "I've added 'Buy groceries' to your task list! It's task #1."
```

**Command 2: Show All Tasks**
```
User: "Show me all my tasks"
Agent: Invokes list_tasks(user_id="user_123", status="all")
Response: "Here are all your tasks:
1. Buy groceries (pending)
2. Call mom (pending)
3. Pay bills (completed)"
```

**Command 3: Show Pending Tasks**
```
User: "What's pending?"
Agent: Invokes list_tasks(user_id="user_123", status="pending")
Response: "You have 2 pending tasks:
1. Buy groceries
2. Call mom"
```

**Command 4: Complete Task by ID**
```
User: "Mark task 3 as complete"
Agent: Invokes complete_task(user_id="user_123", task_id=3)
Response: "Great! I've marked 'Pay bills' as complete. ✓"
```

**Command 5: Delete Task (Requires Search)**
```
User: "Delete the meeting task"
Agent:
  Step 1: Invokes list_tasks(user_id="user_123", status="all")
  Step 2: Finds task with title containing "meeting" (task_id=5)
  Step 3: Invokes delete_task(user_id="user_123", task_id=5)
Response: "I've deleted 'Team meeting' from your task list."
```

**Command 6: Update Task**
```
User: "Change task 1 to 'Call mom tonight'"
Agent: Invokes update_task(user_id="user_123", task_id=1, title="Call mom tonight")
Response: "Done! I've updated task 1 to 'Call mom tonight'."
```

**Command 7: Add Task (Alternative Phrasing)**
```
User: "I need to remember to pay bills"
Agent: Invokes add_task(user_id="user_123", title="Pay bills")
Response: "Got it! I've added 'Pay bills' to your list."
```

**Command 8: Show Completed Tasks**
```
User: "What have I completed?"
Agent: Invokes list_tasks(user_id="user_123", status="completed")
Response: "You've completed 1 task:
✓ Pay bills (completed on 2026-01-13)"
```

### Error Response Templates

**Task Not Found**
```
User: "Complete task 999"
Agent: Invokes complete_task → returns {"error": "Task not found"}
Response: "I couldn't find task #999. Could you check the task ID?
You can say 'show me all my tasks' to see your list."
```

**Invalid Task ID**
```
User: "Mark task abc as done"
Agent: Validates input → detects non-numeric ID
Response: "That doesn't look like a valid task ID. Task IDs are numbers like 1, 2, 3...
Try 'show me all my tasks' to see the IDs."
```

**Empty Task List**
```
User: "Show me my tasks"
Agent: Invokes list_tasks → returns []
Response: "You don't have any tasks yet! Want to add one?
Just say something like 'Add a task to buy groceries'."
```

**Ambiguous Delete Request**
```
User: "Delete task meeting"
Agent: Invokes list_tasks → finds multiple matches
Response: "I found 2 tasks with 'meeting':
1. Team meeting
2. Client meeting
Which one would you like to delete? You can say 'delete task 1' or 'delete task 2'."
```

**Database Error**
```
User: "Add a task to review code"
Agent: Invokes add_task → database connection fails
Response: "I'm having trouble accessing your tasks right now. Please try again in a moment.
If the problem persists, let me know!"
```

### Confirmation Templates

**Task Created**
- "I've added '[TITLE]' to your task list!"
- "Got it! '[TITLE]' is now on your list."
- "Done! I've added '[TITLE]' for you."

**Task Completed**
- "Great! I've marked '[TITLE]' as complete. ✓"
- "Nice work! '[TITLE]' is now done. ✓"
- "Excellent! I've completed '[TITLE]' for you."

**Task Deleted**
- "I've deleted '[TITLE]' from your task list."
- "Done! '[TITLE]' has been removed."
- "Got it, I've removed '[TITLE]'."

**Task Updated**
- "Done! I've updated task [ID] to '[NEW_TITLE]'."
- "Changed! Task [ID] is now '[NEW_TITLE]'."
- "Updated! '[OLD_TITLE]' is now '[NEW_TITLE]'."

**List Empty Response**
- "You don't have any [pending/completed] tasks right now."
- "Your [pending/completed] list is empty!"
- "All clear! No [pending/completed] tasks."

### System Prompt

```
You are a helpful task management assistant. Your role is to help users manage their todo list through natural conversation.

AVAILABLE TOOLS:
- add_task: Create a new task with title and optional description
- list_tasks: Show tasks filtered by status (all/pending/completed)
- complete_task: Mark a task as complete by ID
- delete_task: Remove a task by ID
- update_task: Modify task title or description by ID

BEHAVIOR GUIDELINES:
1. Always confirm actions with friendly, natural responses
2. When tasks are created, mention the task title in your response
3. When listing tasks, format them clearly with numbers and status
4. If a task is not found, suggest viewing the full list
5. For ambiguous requests, ask clarifying questions
6. For delete/update operations with descriptions (not IDs), search tasks first
7. Keep responses concise and friendly
8. Use emojis sparingly (✓ for completion is fine)
9. If user_id is missing or invalid, return an error immediately

ERROR HANDLING:
- Task not found → Suggest checking task list
- Invalid input → Explain expected format with example
- Database errors → Acknowledge issue, suggest retry
- Multiple matches → Ask user to clarify with task ID

TRIGGER WORD MAPPING:
- add/create/remember → add_task
- show/list/see/display → list_tasks
- done/complete/finished/did → complete_task
- delete/remove/cancel/forget → delete_task
- change/update/rename/modify → update_task
```

---

## Component 7: Configuration & Deployment

### Environment Files

**Backend `.env.example`**:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://username:password@host:5432/database_name

# Authentication
BETTER_AUTH_SECRET=your-secret-key-min-32-chars

# OpenAI
OPENAI_API_KEY=sk-...

# CORS
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
CORS_ALLOW_CREDENTIALS=true

# Optional
LOG_LEVEL=INFO
ENVIRONMENT=development
```

**Frontend `.env.local.example`**:
```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# OpenAI ChatKit
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-from-openai-platform

# Authentication (must match backend)
BETTER_AUTH_SECRET=your-secret-key-min-32-chars

# Optional
NEXT_PUBLIC_APP_NAME=AI Todo Chatbot
```

### Docker Compose Configuration

**File**: `docker-compose.yml` (Repository Root)

```yaml
version: '3.8'

services:
  # PostgreSQL Database (for local development only)
  # Production uses Neon PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: todo-chatbot-db
    environment:
      POSTGRES_USER: todouser
      POSTGRES_PASSWORD: todopass
      POSTGRES_DB: tododb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U todouser"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: todo-chatbot-backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://todouser:todopass@postgres:5432/tododb
      BETTER_AUTH_SECRET: ${BETTER_AUTH_SECRET}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      CORS_ORIGINS: http://localhost:3000
      CORS_ALLOW_CREDENTIALS: "true"
      LOG_LEVEL: INFO
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend/src:/app/src
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: todo-chatbot-frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
      NEXT_PUBLIC_OPENAI_DOMAIN_KEY: ${NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
      BETTER_AUTH_SECRET: ${BETTER_AUTH_SECRET}
    depends_on:
      - backend
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
    command: npm run dev

volumes:
  postgres_data:
```

**Backend Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run database migrations on startup (optional)
# CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000

# Default command (for development)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile**:
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build for production (production build)
# RUN npm run build
# CMD ["npm", "start"]

# Development mode (default)
CMD ["npm", "run", "dev"]
```

### README.md

**File**: `README.md` (Repository Root)

```markdown
# AI Todo Chatbot

Conversational AI-powered task management system using OpenAI Agents SDK, MCP tools, FastAPI backend, and Next.js ChatKit frontend.

## Features

- ✅ Natural language task management (add, list, complete, delete, update)
- 🤖 OpenAI AI agent with 5 MCP tools
- 🔒 JWT-based authentication with Better Auth
- 🗄️ Stateless architecture with PostgreSQL persistence
- 🎨 Modern ChatKit UI (Next.js 16)
- ✨ Multi-turn conversational context
- 🧪 80%+ test coverage

## Prerequisites

- **Python 3.11+** (backend)
- **Node.js 18+** (frontend)
- **Docker & Docker Compose** (optional, for local development)
- **Neon PostgreSQL account** (free tier) or local PostgreSQL
- **OpenAI API key**
- **Better Auth instance** (or self-hosted)

## Quick Start with Docker

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd ai-todo-chatbot
   ```

2. **Set environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your secrets (BETTER_AUTH_SECRET, OPENAI_API_KEY, etc.)
   ```

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Manual Setup (Without Docker)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your DATABASE_URL, OPENAI_API_KEY, etc.
   ```

5. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

6. **Start backend server**:
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment**:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with NEXT_PUBLIC_API_URL, NEXT_PUBLIC_OPENAI_DOMAIN_KEY, etc.
   ```

4. **Start development server**:
   ```bash
   npm run dev
   ```

## Database Setup

### Using Neon PostgreSQL (Recommended for Production)

1. Create account at https://neon.tech
2. Create new project
3. Copy connection string
4. Set `DATABASE_URL` in backend `.env`
5. Run migrations: `alembic upgrade head`

### Using Local PostgreSQL

1. Install PostgreSQL 15+
2. Create database: `createdb tododb`
3. Set `DATABASE_URL=postgresql+asyncpg://user:pass@localhost/tododb`
4. Run migrations: `alembic upgrade head`

## Testing

### Backend Tests

```bash
cd backend
pytest --cov=src --cov-report=html --cov-fail-under=80
```

View coverage report: `open htmlcov/index.html`

### Frontend Tests

```bash
cd frontend
npm test
```

## Deployment

### Backend Deployment (Railway, Render, Fly.io)

1. Connect repository
2. Set environment variables (DATABASE_URL, OPENAI_API_KEY, etc.)
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### Frontend Deployment (Vercel)

1. Connect GitHub repository to Vercel
2. Deploy (get domain like `your-app.vercel.app`)
3. **Configure ChatKit Domain Allowlist**:
   - Go to OpenAI Platform → Settings → Domain Allowlist
   - Add `your-app.vercel.app`
   - Copy generated domain key
4. Set environment variables in Vercel:
   - `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` (from OpenAI platform)
   - `NEXT_PUBLIC_API_URL` (your backend URL)
   - `BETTER_AUTH_SECRET` (must match backend)
5. Redeploy

## Architecture

```
User Browser
    ↓ (HTTPS)
Next.js Frontend (Vercel)
    ↓ (POST /api/{user_id}/chat + JWT)
FastAPI Backend (Stateless)
    ↓
OpenAI Agent (with conversation history)
    ↓
MCP Server (5 tools)
    ↓
Neon PostgreSQL (tasks, conversations, messages)
```

## Environment Variables

### Backend Required
- `DATABASE_URL`: PostgreSQL connection string
- `BETTER_AUTH_SECRET`: JWT signing secret (min 32 chars)
- `OPENAI_API_KEY`: OpenAI API key
- `CORS_ORIGINS`: Comma-separated allowed origins
- `CORS_ALLOW_CREDENTIALS`: Set to `true`

### Frontend Required
- `NEXT_PUBLIC_API_URL`: Backend API base URL
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`: ChatKit domain key
- `BETTER_AUTH_SECRET`: Must match backend

## Troubleshooting

**CORS Errors**: Ensure frontend URL is in backend `CORS_ORIGINS` env var

**401 Unauthorized**: Check JWT token format and `BETTER_AUTH_SECRET` match between services

**ChatKit not loading**: Verify domain is added to OpenAI Platform allowlist and `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` is set

**Database connection errors**: Verify `DATABASE_URL` format and credentials

**Tests failing**: Ensure test database is accessible and migrations are applied

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - see LICENSE file for details
```

---

## Next Steps

This plan completes Phase 0 (Research) and Phase 1 (Design).

**Ready for Phase 2**: Run `/sp.tasks` to generate implementation tasks based on this plan.

**Phase 2 artifacts** (created by `/sp.tasks`):
- `tasks.md` - Detailed implementation tasks organized by user story
- Task breakdown with dependencies and parallel execution opportunities
- Test-first approach with acceptance criteria

**Implementation order** (after `/sp.tasks`):
1. Setup phase - Project structure and dependencies
2. Foundational phase - Database models, MCP server, JWT middleware (blocking)
3. User Story 1 (P1) - Add and list tasks via chat
4. User Story 2 (P1) - View and filter tasks
5. User Story 3 (P2) - Complete tasks
6. User Story 6 (P2) - Multi-turn conversations
7. User Story 4 (P3) - Delete tasks
8. User Story 5 (P3) - Update tasks
9. Polish phase - Documentation, deployment guides

All constitutional requirements validated ✅. Zero violations. System ready for implementation.

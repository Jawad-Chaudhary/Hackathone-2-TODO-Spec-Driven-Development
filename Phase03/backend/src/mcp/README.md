# MCP Server for AI Todo Chatbot

## Overview

This directory contains the MCP (Model Context Protocol) server implementation using the **Official Python MCP SDK**. The server exposes 5 stateless tools for task management, all enforcing user isolation.

## Architecture

- **Stateless Design**: Each tool call creates its own database session
- **User Isolation**: All database queries filter by `user_id` to prevent unauthorized access
- **Stdio Transport**: Server communicates via stdio for process-based invocation
- **Official SDK**: Uses `mcp>=1.25.0` with `@server.call_tool()` decorator pattern

## File Structure

```
backend/src/mcp/
├── __init__.py              # Package exports
├── server.py                # Main MCP server with tool registration
├── README.md                # This file
└── tools/
    ├── __init__.py
    ├── add_task.py          # Create new tasks
    ├── list_tasks.py        # List user's tasks with filtering
    ├── complete_task.py     # Mark tasks as completed
    ├── delete_task.py       # Delete tasks
    └── update_task.py       # Update task title/description
```

## Tools

### 1. add_task (T-013)

Creates a new task for a user.

**Input:**
```json
{
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"  // optional
}
```

**Output:**
```json
{
  "status": "success",
  "task": {
    "id": 1,
    "user_id": "user123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2025-01-14T12:00:00",
    "updated_at": "2025-01-14T12:00:00"
  }
}
```

**Validations:**
- `user_id`: required, non-empty string
- `title`: required, 1-200 characters
- `description`: optional, max 1000 characters

---

### 2. list_tasks (T-014)

Lists all tasks for a user with optional status filtering.

**Input:**
```json
{
  "user_id": "user123",
  "status": "all"  // "all", "pending", or "completed"
}
```

**Output:**
```json
{
  "status": "success",
  "tasks": [
    {
      "id": 1,
      "user_id": "user123",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2025-01-14T12:00:00",
      "updated_at": "2025-01-14T12:00:00"
    }
  ],
  "count": 1
}
```

**Validations:**
- `user_id`: required, non-empty string
- `status`: optional, must be "all", "pending", or "completed" (default: "all")

**Ordering:** Results sorted by `created_at` descending (newest first)

---

### 3. complete_task (T-015)

Marks a task as completed.

**Input:**
```json
{
  "user_id": "user123",
  "task_id": 1
}
```

**Output:**
```json
{
  "status": "success",
  "task": {
    "id": 1,
    "user_id": "user123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": true,
    "created_at": "2025-01-14T12:00:00",
    "updated_at": "2025-01-14T13:30:00"
  }
}
```

**Validations:**
- `user_id`: required, non-empty string
- `task_id`: required, must exist and belong to `user_id`
- **Ownership enforced**: Returns 404 if task doesn't exist or belongs to another user

---

### 4. delete_task (T-016)

Deletes a task.

**Input:**
```json
{
  "user_id": "user123",
  "task_id": 1
}
```

**Output:**
```json
{
  "status": "success",
  "message": "Task 1 deleted successfully"
}
```

**Validations:**
- `user_id`: required, non-empty string
- `task_id`: required, must exist and belong to `user_id`
- **Ownership enforced**: Returns 404 if task doesn't exist or belongs to another user

---

### 5. update_task (T-017)

Updates a task's title and/or description.

**Input:**
```json
{
  "user_id": "user123",
  "task_id": 1,
  "title": "Buy groceries and supplies",  // optional
  "description": "Milk, eggs, bread, cleaning supplies"  // optional
}
```

**Output:**
```json
{
  "status": "success",
  "task": {
    "id": 1,
    "user_id": "user123",
    "title": "Buy groceries and supplies",
    "description": "Milk, eggs, bread, cleaning supplies",
    "completed": false,
    "created_at": "2025-01-14T12:00:00",
    "updated_at": "2025-01-14T14:30:00"
  }
}
```

**Validations:**
- `user_id`: required, non-empty string
- `task_id`: required, must exist and belong to `user_id`
- At least one field (`title` or `description`) must be provided
- `title`: if provided, 1-200 characters
- `description`: if provided, max 1000 characters
- **Ownership enforced**: Returns 404 if task doesn't exist or belongs to another user

---

## Error Handling (T-018)

All tools return consistent error responses:

```json
{
  "error": "Description of what went wrong",
  "status": "error"
}
```

**Error Categories:**

1. **Validation Errors (400-equivalent):**
   - Missing required fields
   - Invalid field lengths
   - Invalid enum values

2. **Not Found / Access Denied (404-equivalent):**
   - Task doesn't exist
   - Task belongs to another user (ownership violation)

3. **Database Errors (500-equivalent):**
   - Connection failures
   - Query execution errors

## Running the Server

### Standalone Mode

```bash
cd backend
python -m src.mcp.server
```

The server will start and communicate via stdio, ready to receive MCP protocol messages.

### Integration with OpenAI Agent

The server is designed to be invoked by the OpenAI Agent (Task T-019) which will:
1. Start the MCP server as a subprocess
2. Register all 5 tools as OpenAI functions
3. Route tool calls through the MCP protocol

## Security Features

### User Isolation

Every tool enforces user isolation by:
1. Requiring `user_id` in all inputs
2. Filtering database queries with `WHERE user_id = ?`
3. Returning 404 for tasks belonging to other users (prevents enumeration)

**Example from `complete_task`:**
```python
stmt = select(Task).where(
    Task.id == task_id,
    Task.user_id == user_id  # Ownership check in query
)
```

### Input Validation

All tools validate inputs before database operations:
- Required field presence
- String length constraints
- Enum value validation
- Type checking

### Stateless Architecture

- No in-memory session state
- Each tool call creates its own async database session
- Sessions automatically closed after use
- Enables horizontal scaling

## Database Schema

The tools operate on the `tasks` table defined in `src/models/task.py`:

```python
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, max_length=255)  # Indexed for performance
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Indexes:**
- `user_id`: Speeds up filtering by user
- Primary key on `id`

## Environment Variables

The MCP server requires:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
```

Set in `.env` file or environment. Never hardcode credentials.

## Testing

Unit tests for MCP tools should:
1. Mock the database session
2. Test all validation paths
3. Verify user isolation enforcement
4. Check error responses
5. Validate JSON response schemas

Example test structure:
```python
@pytest.mark.asyncio
async def test_add_task_success():
    arguments = {
        "user_id": "user123",
        "title": "Test task",
        "description": "Test description"
    }
    result = await _add_task(arguments)
    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert data["task"]["title"] == "Test task"
```

## Task References

- **T-012**: MCP server initialization with stdio transport
- **T-013**: `add_task` tool implementation
- **T-014**: `list_tasks` tool implementation
- **T-015**: `complete_task` tool implementation
- **T-016**: `delete_task` tool implementation
- **T-017**: `update_task` tool implementation
- **T-018**: Error handling for all tools

## Dependencies

```
mcp>=1.25.0              # Official Python MCP SDK
sqlmodel==0.0.14         # ORM for database operations
sqlalchemy[asyncio]>=2.0.25  # Async database engine
asyncpg>=0.30.0          # PostgreSQL async driver
```

## Next Steps

After MCP server implementation:
1. **T-019**: Initialize OpenAI Agent
2. **T-020**: Register MCP tools as OpenAI functions
3. **T-021**: Implement agent execution with conversation history
4. **T-022**: Create FastAPI chat endpoint
5. Integration testing with full stack

## References

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Official Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- Project spec: `specs/001-ai-todo-chatbot/spec.md`
- Implementation plan: `specs/001-ai-todo-chatbot/plan.md`
- Task breakdown: `specs/001-ai-todo-chatbot/tasks.md`

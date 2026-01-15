# OpenAI Agent Module

This module implements the OpenAI Agent component for natural language task management.

## Components

### 1. `agent.py` - TodoAgent Class

**Purpose**: Wraps OpenAI client with task management system prompt and tool schemas.

**Key Features**:
- System prompt with trigger word mapping
- 5 MCP tool schemas (add_task, list_tasks, complete_task, delete_task, update_task)
- Async chat method for processing messages

**Usage**:
```python
from agent import TodoAgent

agent = TodoAgent()  # Uses OPENAI_API_KEY from env

messages = [{"role": "user", "content": "Add a task to buy groceries"}]
response, tool_calls = await agent.chat(messages, user_id="user_123")
```

### 2. `runner.py` - AgentRunner Class

**Purpose**: Coordinates agent execution with MCP tool invocation and user_id injection.

**Key Features**:
- Injects user_id into all tool call arguments
- Executes MCP tools when agent requests them
- Handles tool results and generates final responses
- Error handling for failed tool executions

**Usage**:
```python
from agent import AgentRunner, TodoAgent

# Define MCP tool executor
async def tool_executor(name: str, args: dict) -> dict:
    # Execute MCP tools
    if name == "add_task":
        return {"task_id": 1, "status": "created"}
    # ... handle other tools

agent = TodoAgent()
runner = AgentRunner(agent, tool_executor)

messages = [{"role": "user", "content": "Show my tasks"}]
response, tools = await runner.run(messages, user_id="user_123")
```

**Simplified API**:
```python
# Single message execution
response, tools = await runner.run_simple(
    "Add task to buy groceries",
    user_id="user_123"
)
```

### 3. `__init__.py` - Module Exports

Exports:
- `TodoAgent` - Main agent class
- `AgentRunner` - Runner with tool execution
- `create_runner` - Factory function
- `SYSTEM_PROMPT` - Agent behavior prompt
- `TOOL_SCHEMAS` - OpenAI function schemas

## Trigger Word Mapping

The agent is trained to recognize these trigger words:

| Intent | Trigger Words | Tool Called |
|--------|--------------|-------------|
| Add Task | add, create, remember, need to | `add_task` |
| List All | show, list, see, display | `list_tasks(status="all")` |
| List Pending | pending, incomplete, todo | `list_tasks(status="pending")` |
| List Completed | completed, done, finished | `list_tasks(status="completed")` |
| Complete Task | complete, done, mark as done | `complete_task` |
| Delete Task | delete, remove, cancel, forget | `delete_task` |
| Update Task | change, update, rename, modify | `update_task` |

## Tool Schemas

All 5 MCP tools are defined with JSON Schema validation:

1. **add_task**: Create new task with title and optional description
2. **list_tasks**: Retrieve tasks filtered by status (all/pending/completed)
3. **complete_task**: Mark task as complete by ID
4. **delete_task**: Remove task by ID
5. **update_task**: Modify task title or description by ID

Each schema includes:
- Parameter types and descriptions
- Validation rules (min/max length, required fields)
- user_id field (automatically injected by runner)

## Integration with Chat API

The agent module is designed to integrate with the FastAPI chat endpoint:

```python
from agent import create_runner
from mcp import execute_mcp_tool  # Your MCP tool executor

# Initialize runner once at startup
agent_runner = create_runner(tool_executor=execute_mcp_tool)

# In chat endpoint
@app.post("/api/{user_id}/chat")
async def chat(user_id: str, request: ChatRequest):
    # Load conversation history from DB
    conversation, messages = await load_history(user_id, request.conversation_id)

    # Add new user message
    messages.append({"role": "user", "content": request.message})

    # Run agent
    response, tool_calls = await agent_runner.run(messages, user_id)

    # Save messages to DB
    await save_messages(conversation.id, messages, response)

    return ChatResponse(
        conversation_id=conversation.id,
        response=response,
        tool_calls=tool_calls
    )
```

## Testing

To test the agent module independently:

```python
import asyncio
from agent import create_runner

async def mock_tool_executor(name: str, args: dict) -> dict:
    print(f"Tool called: {name} with args: {args}")
    return {"status": "success", "message": "Mock result"}

async def test():
    runner = create_runner(tool_executor=mock_tool_executor)

    response, tools = await runner.run_simple(
        "Add a task to buy groceries",
        user_id="test_user"
    )

    print(f"Response: {response}")
    print(f"Tools used: {tools}")

asyncio.run(test())
```

## Environment Variables

Required:
- `OPENAI_API_KEY` - OpenAI API key for chat completions

Optional:
- Can pass `api_key` directly to `TodoAgent()` constructor

## Error Handling

The agent handles:
- Missing API key (raises ValueError)
- Tool execution failures (returns error in tool result)
- Invalid tool arguments (OpenAI validates against schema)
- Network errors (propagated from OpenAI client)

## Next Steps

This module completes Tasks T-019, T-020, T-021 from the implementation plan:
- ✓ T-019: Initialize OpenAI Agent with system prompt
- ✓ T-020: Register all 5 MCP tools as OpenAI functions
- ✓ T-021: Create agent runner with conversation history

**Integration Points**:
1. Connect to MCP tools (T-013 to T-017)
2. Integrate with FastAPI chat endpoint (T-026)
3. Add conversation history loading (T-027)
4. Implement behavior tests (T-022)

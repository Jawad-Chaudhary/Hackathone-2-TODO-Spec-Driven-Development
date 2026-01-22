# OpenAI Agent Integration

This package provides OpenAI Agents SDK integration for natural language task management.

## Quick Start

```python
from app.agent import run_agent

# Execute agent with conversation history
result = await run_agent(
    user_id=123,
    messages=[
        {"role": "user", "content": "Add a task to buy groceries"}
    ]
)

print(result["response"])  # "I've added 'Buy groceries' to your tasks."
print(result["tool_calls"])  # ["add_task"]
print(result["success"])  # True
```

## Architecture

### Components

1. **config.py** - Agent configuration
   - System prompt defining assistant behavior
   - OpenAI client initialization
   - Tool definitions (OpenAI function format)

2. **runner.py** - Agent execution engine
   - Conversation history management
   - Tool call execution
   - Error handling
   - Response formatting

### Tool Integration

The agent has access to 5 MCP tools:

| Tool | Purpose | Parameters |
|------|---------|------------|
| `add_task` | Create new task | user_id, title, description? |
| `list_tasks` | Retrieve tasks | user_id, status? |
| `complete_task` | Mark as completed | user_id, task_id |
| `delete_task` | Remove task | user_id, task_id |
| `update_task` | Modify task | user_id, task_id, title?, description? |

## Configuration

### Environment Variables

```bash
OPENAI_API_KEY=sk-your-key-here  # Required
```

### Model Settings

- **Model**: `gpt-4o` (configurable in config.py)
- **Temperature**: `0.7` (balanced creativity/accuracy)
- **Max Iterations**: `5` (prevents infinite loops)

## Usage Examples

### Add Task
```python
messages = [
    {"role": "user", "content": "Add task: Buy milk"}
]
result = await run_agent(user_id=1, messages=messages)
# Tool called: add_task(user_id=1, title="Buy milk")
```

### List Tasks with Filter
```python
messages = [
    {"role": "user", "content": "Show me my pending tasks"}
]
result = await run_agent(user_id=1, messages=messages)
# Tool called: list_tasks(user_id=1, status="pending")
```

### Complete Task
```python
messages = [
    {"role": "user", "content": "Mark task 5 as done"}
]
result = await run_agent(user_id=1, messages=messages)
# Tool called: complete_task(user_id=1, task_id=5)
```

### Multi-turn Conversation
```python
messages = [
    {"role": "user", "content": "Add task: Buy milk"},
    {"role": "assistant", "content": "I've added 'Buy milk' to your tasks."},
    {"role": "user", "content": "Add another: Buy bread"}
]
result = await run_agent(user_id=1, messages=messages)
# Agent maintains context from previous turns
```

### Ambiguous Command
```python
messages = [
    {"role": "user", "content": "complete task"}
]
result = await run_agent(user_id=1, messages=messages)
# Response: "Which task would you like to complete? Please provide the task number."
# No tool calls - agent asks for clarification
```

## Error Handling

The runner handles various error types:

### OpenAI API Errors
- `APITimeoutError` - Request timeout
- `RateLimitError` - Rate limit exceeded
- `AuthenticationError` - Invalid API key
- `APIError` - General API errors

### Validation Errors
- `ValueError` - Invalid user_id or messages format

### Tool Execution Errors
- Tool failures are caught and communicated to the agent
- Agent continues execution and informs user

### Example
```python
try:
    result = await run_agent(user_id=1, messages=messages)
    if result["success"]:
        print(result["response"])
    else:
        print(f"Error: {result['error']}")
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Response Format

```python
{
    "response": str,          # Agent's text response
    "tool_calls": List[str],  # List of tool names called
    "success": bool,          # Operation success status
    "error": str | None       # Error message if failed
}
```

## Testing

### Run Tests
```bash
pytest tests/integration/test_agent_integration.py -v
```

### Test Coverage
- Add task via natural language ✓
- List tasks with filtering ✓
- Complete task ✓
- Handle ambiguous commands ✓
- Handle tool execution errors ✓
- Maintain conversation history ✓
- Validate inputs ✓
- Prevent infinite loops ✓

## Security

### User Isolation
- All tool calls include authenticated user_id
- Database queries filter by user_id
- No cross-user data access possible

### Input Validation
- user_id must be positive integer
- messages must be non-empty list
- Tool arguments validated by OpenAI schema

### API Key Security
- Never hardcode API keys
- Load from environment variables
- Validate at initialization

## Performance

- Average response time: < 2 seconds (depends on OpenAI API)
- Test execution: < 3 seconds (9 tests, mocked)
- Max iterations: 5 (prevents runaway loops)

## Best Practices

1. **Always provide conversation history**
   ```python
   # Good
   result = await run_agent(user_id=1, messages=full_history)

   # Bad - loses context
   result = await run_agent(user_id=1, messages=[latest_message])
   ```

2. **Handle errors gracefully**
   ```python
   result = await run_agent(user_id=1, messages=messages)
   if not result["success"]:
       log.error(f"Agent failed: {result['error']}")
       return fallback_response()
   ```

3. **Use async properly**
   ```python
   # Good
   result = await run_agent(user_id=1, messages=messages)

   # Bad - blocks event loop
   result = run_agent(user_id=1, messages=messages)  # Missing await
   ```

4. **Pass authenticated user_id**
   ```python
   # Extract from JWT token, not from user input
   user_id = verify_jwt_token(request.headers["Authorization"])
   result = await run_agent(user_id=user_id, messages=messages)
   ```

## Troubleshooting

### "OPENAI_API_KEY not found"
- Check .env file has OPENAI_API_KEY set
- Verify .env is loaded (use python-dotenv)

### "Rate limit exceeded"
- Wait a moment and retry
- Consider implementing exponential backoff
- Check OpenAI dashboard for rate limits

### "Maximum iterations reached"
- Agent got stuck in tool call loop
- Usually means user request was too complex
- Ask user to break request into smaller steps

### Tool execution fails
- Check database connectivity
- Verify user_id is valid
- Check tool function logs for details

## Development

### Adding New Tools

1. Create tool function in `app/mcp/tools/`
2. Add to `TOOL_FUNCTIONS` dict in `runner.py`
3. Add tool definition to `get_agent_tools()` in `config.py`
4. Write integration test

Example:
```python
# In config.py
{
    "type": "function",
    "function": {
        "name": "my_new_tool",
        "description": "What this tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer"},
                "param": {"type": "string"}
            },
            "required": ["user_id", "param"]
        }
    }
}

# In runner.py
TOOL_FUNCTIONS = {
    "my_new_tool": my_new_tool,
    # ... existing tools
}
```

### Customizing System Prompt

Edit `SYSTEM_PROMPT` in `config.py`:
```python
SYSTEM_PROMPT = """Your custom instructions here..."""
```

### Adjusting Model Settings

Edit constants in `config.py`:
```python
DEFAULT_MODEL = "gpt-4o-mini"  # Use cheaper model
DEFAULT_TEMPERATURE = 0.3  # More deterministic
```

## References

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [MCP Tools](../mcp/tools/)

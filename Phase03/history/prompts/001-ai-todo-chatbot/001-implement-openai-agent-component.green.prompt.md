---
id: 001
title: Implement OpenAI Agent Component
stage: green
date: 2026-01-14
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-ai-todo-chatbot
branch: 001-ai-todo-chatbot
user: jawad
command: Implementation request
labels: ["openai-agent", "mcp-tools", "natural-language", "task-management"]
links:
  spec: specs/001-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/agent/__init__.py
  - backend/src/agent/agent.py
  - backend/src/agent/runner.py
  - backend/src/agent/README.md
tests:
  - Import verification test passed (all components loadable)
---

## Prompt

Implement the OpenAI Agent component for natural language task management.

**Context:**
- Working directory: D:\C-O-D-E\Quater 4\Off-Class\Hackathone-2-TODO-Spec-Driven-Development\Phase03\backend
- OpenAI SDK installed: openai>=1.62.0
- MCP tools will be available (add_task, list_tasks, complete_task, delete_task, update_task)

**Requirements from specs/001-ai-todo-chatbot/tasks.md (Tasks T019-T022):**

Create OpenAI Agent with:

1. **System Prompt** - Agent Behavior Specification with trigger word mapping:
   - "add", "create", "remember", "need to" → call add_task
   - "show", "list", "see", "what", "display" → call list_tasks
   - "done", "complete", "finished", "did" → call complete_task
   - "delete", "remove", "cancel", "forget" → call delete_task
   - "change", "update", "rename", "modify" → call update_task

2. **Function Schemas** - 5 tool schemas matching MCP tools:
   - Each with name, description, parameters (user_id, task_id, title, description, status)
   - JSON Schema format with required fields

3. **TodoAgent Class** - Wraps OpenAI client:
   - Initialize with api_key from environment
   - Method: `async def chat(messages: list[dict], user_id: str) -> tuple[str, list]`
   - Returns: (response_text, tool_calls)

4. **AgentRunner** - Coordinates agent + tool execution:
   - `async def run(messages: list[dict], user_id: str) -> tuple[str, list]`
   - Injects user_id into all tool calls
   - Executes MCP tools when agent requests them
   - Returns final response

**File Structure:**
```
backend/src/agent/
├── __init__.py
├── agent.py    # TodoAgent class with system prompt and schemas
└── runner.py   # AgentRunner with user_id injection
```

**Code Standards:**
- Task ID comments: `# [Task]: T-XXX`
- Full type hints
- Async/await for OpenAI calls
- User-friendly error handling

Create all 3 files with complete implementation. The runner must inject user_id into all tool call arguments.

## Response snapshot

Successfully implemented the OpenAI Agent component with three main files:

**1. agent.py (TodoAgent Class)**:
- Comprehensive system prompt (2265 chars) with trigger word mapping
- 5 complete MCP tool schemas in OpenAI function format
- TodoAgent class with AsyncOpenAI client wrapper
- async chat() method returning (response_text, tool_calls)
- Error handling for missing API key
- Uses GPT-4 Optimized model (gpt-4o)

**2. runner.py (AgentRunner Class)**:
- AgentRunner class coordinating agent + tool execution
- Automatic user_id injection into all tool call arguments
- Two-phase execution: initial chat → tool execution → follow-up chat
- Error handling for failed tool executions
- Simplified run_simple() method for single messages
- Factory function create_runner() for easy initialization

**3. __init__.py**:
- Clean module exports (TodoAgent, AgentRunner, create_runner, SYSTEM_PROMPT, TOOL_SCHEMAS)
- Module-level documentation

**4. README.md**:
- Complete usage documentation
- Trigger word mapping table
- Integration examples
- Testing guidance

**Key Design Decisions**:
1. **User ID Injection**: Runner automatically injects user_id into all tool calls, ensuring security at the orchestration layer
2. **Two-Phase Execution**: Agent decides tools → tools execute → agent formats results into natural language
3. **Error Resilience**: Tool execution failures don't crash the flow; errors are returned as tool results
4. **Clean Separation**: Agent handles intent recognition, Runner handles orchestration and security

**Verification**:
- All files compile without syntax errors
- Import test confirms all components loadable
- 5 tools correctly defined: add_task, list_tasks, complete_task, delete_task, update_task
- System prompt length: 2265 characters

## Outcome

- ✅ Impact: Core agent component implemented, ready for integration with MCP tools and FastAPI chat endpoint
- 🧪 Tests: Import verification passed; behavior tests (T-022) pending
- 📁 Files: 4 files created (agent.py, runner.py, __init__.py, README.md)
- 🔁 Next prompts: Integrate with MCP tools (T-013 to T-017), implement chat endpoint (T-026), write agent behavior tests (T-022)
- 🧠 Reflection: Clean architecture with strong separation of concerns. Agent focuses on intent recognition, Runner handles security (user_id injection) and orchestration. Ready for stateless integration.

## Evaluation notes (flywheel)

- Failure modes observed: None during implementation; potential issues: OpenAI API rate limits, invalid tool schemas, missing user_id in arguments (mitigated by automatic injection)
- Graders run and results (PASS/FAIL): PASS - Import test successful, all components loadable
- Prompt variant (if applicable): N/A - Initial implementation
- Next experiment (smallest change to try): Test with mock MCP tools to verify user_id injection and two-phase execution flow

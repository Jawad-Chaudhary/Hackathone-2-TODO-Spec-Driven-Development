# [Task]: T-019, T-020, T-021
# [From]: specs/001-ai-todo-chatbot/tasks.md
"""
OpenAI Agent module for natural language task management.

This module provides the TodoAgent and AgentRunner classes for
processing natural language commands and executing MCP tools.

Usage:
    from agent import TodoAgent, AgentRunner, create_runner

    # Create agent
    agent = TodoAgent()

    # Create runner with MCP tool executor
    runner = create_runner(tool_executor=my_tool_executor)

    # Process message
    response, tools = await runner.run_simple(
        "Add task to buy groceries",
        user_id="user_123"
    )
"""

from .agent import TodoAgent, SYSTEM_PROMPT, TOOL_SCHEMAS
from .runner import AgentRunner, create_runner

__all__ = [
    "TodoAgent",
    "AgentRunner",
    "create_runner",
    "SYSTEM_PROMPT",
    "TOOL_SCHEMAS"
]

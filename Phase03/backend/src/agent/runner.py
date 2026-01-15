# [Task]: T-021
# [From]: specs/001-ai-todo-chatbot/tasks.md
"""
Agent runner with user_id injection and MCP tool execution.

This module provides the AgentRunner class that coordinates between
the OpenAI agent and MCP tool execution, ensuring user_id is injected
into all tool calls for proper user isolation.
"""

import json
from typing import Any, Callable

from .agent import TodoAgent


class AgentRunner:
    """
    Coordinates agent execution with MCP tool invocation.

    This class wraps the TodoAgent and handles:
    1. Running the agent with conversation history
    2. Injecting user_id into all tool call arguments
    3. Executing MCP tools when the agent requests them
    4. Building the final response with tool results
    """

    def __init__(self, agent: TodoAgent, tool_executor: Callable) -> None:
        """
        Initialize the AgentRunner.

        Args:
            agent: TodoAgent instance for chat processing
            tool_executor: Async callable that executes MCP tools
                          Signature: async def tool_executor(name: str, args: dict) -> dict
        """
        self.agent = agent
        self.tool_executor = tool_executor

    async def run(
        self,
        messages: list[dict],
        user_id: str
    ) -> tuple[str, list[str]]:
        """
        Run the agent with conversation history and execute tools.

        This method:
        1. Calls the agent with message history
        2. Injects user_id into all tool call arguments
        3. Executes requested MCP tools
        4. Builds follow-up messages with tool results
        5. Calls agent again to generate final response
        6. Returns the response and list of executed tool names

        Args:
            messages: Conversation history
                     Format: [{"role": "user"|"assistant", "content": "..."}]
            user_id: User identifier for tool execution and isolation

        Returns:
            Tuple of (response_text, tool_names)
            - response_text: Final natural language response from agent
            - tool_names: List of tool names that were executed

        Example:
            >>> runner = AgentRunner(agent, mcp_tool_executor)
            >>> response, tools = await runner.run(
            ...     [{"role": "user", "content": "Add task to buy groceries"}],
            ...     user_id="user_123"
            ... )
            >>> print(response)
            "I've added 'Buy groceries' to your task list!"
            >>> print(tools)
            ["add_task"]
        """
        # Step 1: Call agent to analyze user intent and determine tool calls
        response_text, tool_calls = await self.agent.chat(messages, user_id)

        # If no tools were called, return the direct response
        if not tool_calls:
            return response_text, []

        # Step 2: Inject user_id into all tool call arguments
        tool_names = []
        tool_results = []

        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["arguments"]
            tool_id = tool_call["id"]

            # Ensure user_id is in arguments (inject if missing or override if present)
            tool_args["user_id"] = user_id

            tool_names.append(tool_name)

            # Step 3: Execute the MCP tool
            try:
                result = await self.tool_executor(tool_name, tool_args)
                tool_results.append({
                    "tool_call_id": tool_id,
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(result)
                })
            except Exception as e:
                # Handle tool execution errors gracefully
                error_result = {
                    "error": str(e),
                    "status": "failed"
                }
                tool_results.append({
                    "tool_call_id": tool_id,
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(error_result)
                })

        # Step 4: Build follow-up messages with tool results
        # Add the assistant's tool call message
        assistant_message = {
            "role": "assistant",
            "content": response_text or None,
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": json.dumps(tc["arguments"])
                    }
                }
                for tc in tool_calls
            ]
        }

        # Add tool result messages
        follow_up_messages = messages + [assistant_message] + tool_results

        # Step 5: Call agent again with tool results to generate final response
        final_response, _ = await self.agent.chat(follow_up_messages, user_id)

        return final_response, tool_names

    async def run_simple(
        self,
        message: str,
        user_id: str,
        conversation_history: list[dict] | None = None
    ) -> tuple[str, list[str]]:
        """
        Simplified run method for single message execution.

        This is a convenience wrapper around run() for common use cases
        where you just want to process a single user message.

        Args:
            message: User's message text
            user_id: User identifier
            conversation_history: Optional previous messages
                                 Format: [{"role": "user"|"assistant", "content": "..."}]

        Returns:
            Tuple of (response_text, tool_names)

        Example:
            >>> runner = AgentRunner(agent, mcp_tool_executor)
            >>> response, tools = await runner.run_simple(
            ...     "Add task to buy groceries",
            ...     user_id="user_123"
            ... )
        """
        messages = conversation_history or []
        messages.append({"role": "user", "content": message})
        return await self.run(messages, user_id)


def create_runner(
    api_key: str | None = None,
    tool_executor: Callable | None = None
) -> AgentRunner:
    """
    Factory function to create a configured AgentRunner.

    Args:
        api_key: OpenAI API key (defaults to env var)
        tool_executor: Tool execution function (required)

    Returns:
        Configured AgentRunner instance

    Example:
        >>> async def my_tool_executor(name: str, args: dict) -> dict:
        ...     # Execute MCP tools
        ...     return {"status": "success"}
        >>> runner = create_runner(tool_executor=my_tool_executor)
    """
    if tool_executor is None:
        raise ValueError("tool_executor is required")

    agent = TodoAgent(api_key=api_key)
    return AgentRunner(agent, tool_executor)

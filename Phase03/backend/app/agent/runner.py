"""
OpenAI Agent runner module.

This module handles the execution of the OpenAI agent with conversation
history, tool calling, and error handling.
"""

import json
import logging
from typing import List, Dict, Any, Tuple
from openai import AsyncOpenAI, APITimeoutError, RateLimitError, AuthenticationError, APIError

from app.agent.config import get_openai_client, SYSTEM_PROMPT, get_agent_tools, DEFAULT_MODEL, DEFAULT_TEMPERATURE
from app.mcp.tools.add_task import add_task
from app.mcp.tools.list_tasks import list_tasks
from app.mcp.tools.complete_task import complete_task
from app.mcp.tools.delete_task import delete_task
from app.mcp.tools.update_task import update_task

logger = logging.getLogger(__name__)

# Map tool names to their implementation functions
TOOL_FUNCTIONS = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "complete_task": complete_task,
    "delete_task": delete_task,
    "update_task": update_task,
}


async def run_agent(
    user_id: str,
    messages: List[Dict[str, str]],
    client: AsyncOpenAI | None = None,
    max_iterations: int = 5
) -> Dict[str, Any]:
    """
    Run the OpenAI agent with conversation history and tool execution.

    This function:
    1. Loads the conversation history
    2. Calls OpenAI API with messages and available tools
    3. Executes any tool calls requested by the agent
    4. Returns the agent's response and tool call information

    Args:
        user_id: ID of the user running the agent (for tool execution)
        messages: List of conversation messages in OpenAI format
                 [{"role": "user", "content": "..."}, ...]
        client: Optional OpenAI client (if None, creates new one)
        max_iterations: Maximum number of tool execution iterations (default: 5)

    Returns:
        Dictionary containing:
        {
            "response": str,          # Agent's text response
            "tool_calls": List[str],  # List of tool names that were called
            "success": bool,          # Whether the operation succeeded
            "error": str | None       # Error message if operation failed
        }

    Raises:
        ValueError: If messages format is invalid or user_id is invalid
        APITimeoutError: If OpenAI API times out
        RateLimitError: If OpenAI API rate limit is exceeded
        AuthenticationError: If OpenAI API key is invalid
        APIError: For other OpenAI API errors
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str) or len(user_id) == 0:
        raise ValueError("user_id must be a non-empty string")

    if not messages or not isinstance(messages, list):
        raise ValueError("messages must be a non-empty list")

    # Initialize client if not provided
    if client is None:
        client = get_openai_client()

    # Get tool definitions
    tools = get_agent_tools()

    # Prepare messages with system prompt
    full_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *messages
    ]

    tool_calls_made: List[str] = []
    iterations = 0

    try:
        while iterations < max_iterations:
            iterations += 1
            logger.info(f"Agent iteration {iterations}/{max_iterations} - Using model: {DEFAULT_MODEL}")

            # Call OpenAI API
            try:
                response = await client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=full_messages,
                    tools=tools,
                    temperature=DEFAULT_TEMPERATURE,
                )
            except APITimeoutError as e:
                logger.error(f"OpenAI API timeout: {e}")
                raise  # Re-raise the original exception
            except RateLimitError as e:
                logger.error(f"OpenAI API rate limit exceeded: {e}")
                raise  # Re-raise the original exception
            except AuthenticationError as e:
                logger.error(f"OpenAI API authentication failed: {e}")
                raise  # Re-raise the original exception
            except APIError as e:
                logger.error(f"OpenAI API error: {e}")
                raise  # Re-raise the original exception

            message = response.choices[0].message
            full_messages.append(message)

            # Check if agent wants to call tools
            if not message.tool_calls:
                # No more tool calls - return final response
                final_response = message.content or ""
                logger.info(f"Agent completed after {iterations} iteration(s)")
                return {
                    "response": final_response,
                    "tool_calls": tool_calls_made,
                    "success": True,
                    "error": None
                }

            # Execute tool calls
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_calls_made.append(tool_name)

                try:
                    # Parse tool arguments
                    tool_args = json.loads(tool_call.function.arguments)
                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                    # Get tool function
                    tool_func = TOOL_FUNCTIONS.get(tool_name)
                    if not tool_func:
                        error_msg = f"Unknown tool: {tool_name}"
                        logger.error(error_msg)
                        tool_result = {"success": False, "error": error_msg}
                    else:
                        # Automatically inject user_id into all tool calls from authenticated context
                        # This prevents the AI from making up user IDs
                        tool_args["user_id"] = user_id

                        logger.info(f"Injected user_id {user_id} into {tool_name} call")

                        # Execute tool
                        tool_result = await tool_func(**tool_args)

                    # Add tool result to messages
                    full_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result)
                    })

                except json.JSONDecodeError as e:
                    error_msg = f"Failed to parse tool arguments: {e}"
                    logger.error(error_msg)
                    full_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"success": False, "error": error_msg})
                    })
                except Exception as e:
                    error_msg = f"Tool execution failed: {str(e)}"
                    logger.error(f"Tool {tool_name} failed: {e}")
                    full_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"success": False, "error": error_msg})
                    })

        # Max iterations reached
        logger.warning(f"Agent reached max iterations ({max_iterations})")
        return {
            "response": "I apologize, but I wasn't able to complete your request. Please try rephrasing or breaking it into smaller steps.",
            "tool_calls": tool_calls_made,
            "success": False,
            "error": "Maximum iterations reached"
        }

    except (APITimeoutError, RateLimitError, AuthenticationError, APIError):
        # Re-raise OpenAI-specific errors
        raise
    except Exception as e:
        logger.error(f"Unexpected error in agent runner: {e}")
        return {
            "response": "I encountered an unexpected error. Please try again.",
            "tool_calls": tool_calls_made,
            "success": False,
            "error": str(e)
        }

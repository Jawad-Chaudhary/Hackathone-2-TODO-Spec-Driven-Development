"""
OpenAI Agent runner for chat conversations.

This module provides the agent execution logic using OpenAI's API
with MCP tools for task management. The agent is stateless and receives
full conversation history on each invocation.
"""

import os
import logging
from typing import List, Dict, Any, Tuple
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Tool definitions for OpenAI function calling (MCP tools)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user's todo list",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title",
                        "maxLength": 200
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional task description",
                        "maxLength": 1000
                    }
                },
                "required": ["user_id", "title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "Retrieve user's tasks with optional filtering",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status",
                        "default": "all"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "Task ID to complete"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update task details (title, description, or completion status)",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "Task ID to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title",
                        "maxLength": 200
                    },
                    "description": {
                        "type": "string",
                        "description": "New task description",
                        "maxLength": 1000
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "New completion status"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task from the user's todo list",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "Task ID to delete"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        }
    }
]


SYSTEM_PROMPT = """You are a helpful task management assistant. You help users manage their todo list efficiently.

Your capabilities:
- Create new tasks with add_task
- List tasks with list_tasks (can filter by status: all, pending, completed)
- Mark tasks as completed with complete_task
- Update task details with update_task
- Delete tasks with delete_task

Guidelines:
- Always confirm actions with friendly, concise responses
- If a user's request is ambiguous, ask for clarification
- When listing tasks, present them in a clear, organized format
- Be proactive in suggesting task management best practices
- Use the user_id from the conversation context for all tool calls
"""


async def run_agent(
    messages: List[Dict[str, str]],
    user_id: str,
    max_iterations: int = 5
) -> Tuple[str, Dict[str, Any]]:
    """
    Run the OpenAI agent with conversation history and MCP tools.

    This function is stateless - all conversation state is passed in via messages.
    It supports multiple tool calls through iterative execution.

    Args:
        messages: Conversation history in OpenAI format [{"role": "user|assistant", "content": "..."}]
        user_id: User identifier for tool calls
        max_iterations: Maximum number of agent iterations (prevents infinite loops)

    Returns:
        Tuple of (response_text, tool_calls_summary)
        - response_text: The assistant's final response
        - tool_calls_summary: Dict with tool names and their results

    Raises:
        Exception: If OpenAI API call fails
    """
    logger.info(f"Running agent for user {user_id} with {len(messages)} messages")

    # Prepare messages with system prompt
    chat_messages: List[ChatCompletionMessageParam] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # Add conversation history
    for msg in messages:
        chat_messages.append({
            "role": msg["role"],  # type: ignore
            "content": msg["content"]
        })

    tool_calls_summary: Dict[str, Any] = {}
    iteration = 0

    try:
        while iteration < max_iterations:
            iteration += 1
            logger.debug(f"Agent iteration {iteration}")

            # Call OpenAI API
            response = await openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective model for task management
                messages=chat_messages,
                tools=TOOLS,
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message

            # If no tool calls, return the response
            if not assistant_message.tool_calls:
                logger.info("Agent completed without tool calls")
                return assistant_message.content or "I'm here to help with your tasks!", tool_calls_summary

            # Process tool calls
            chat_messages.append(assistant_message)  # type: ignore

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = eval(tool_call.function.arguments)  # Parse JSON string

                logger.info(f"Tool call: {tool_name} with args: {tool_args}")

                # Inject user_id into tool arguments
                tool_args["user_id"] = user_id

                # Execute MCP tool
                from app.mcp.server import mcp_server
                tool_result = await mcp_server.execute_tool(tool_name, **tool_args)

                # Record tool call
                tool_calls_summary[tool_name] = tool_args

                # Add tool result to conversation
                chat_messages.append({
                    "role": "tool",
                    "content": str(tool_result),
                    "tool_call_id": tool_call.id
                })

        # If we hit max iterations, return the last response
        logger.warning(f"Agent hit max iterations ({max_iterations})")
        return "I've processed your request, but please let me know if you need anything else!", tool_calls_summary

    except Exception as e:
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        raise Exception(f"Agent execution failed: {str(e)}")

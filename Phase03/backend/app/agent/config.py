"""
OpenAI Agent configuration module.

This module initializes the OpenAI client (configured for Gemini) and defines
the agent configuration including system prompt and tool definitions.
"""

import os
import logging
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

from openai import AsyncOpenAI

# Load environment variables early - use explicit path
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

# System prompt for the task assistant agent
SYSTEM_PROMPT = """You are a helpful todo assistant. You help users manage their tasks through natural language.

Available operations:
- Add task: Create a new task with title and optional description
- List tasks: View all tasks, or filter by pending/completed status
- Complete task: Mark a task as completed
- Delete task: Remove a task permanently
- Update task: Modify task title and/or description

Always confirm actions and provide clear, friendly feedback. When users request operations:
1. Extract the necessary information from their request
2. Call the appropriate tool with the correct parameters
3. Confirm the result in a natural, conversational way

If a request is ambiguous or missing required information, ask clarifying questions before taking action."""

# Model configuration - Using Gemini 2.5 Flash Lite via OpenAI-compatible API
DEFAULT_MODEL = "gemini-2.5-flash-lite"
DEFAULT_TEMPERATURE = 0.7


def get_openai_client() -> AsyncOpenAI:
    """
    Initialize and return OpenAI async client configured for Gemini.

    This uses Gemini's OpenAI-compatible API endpoint with the GEMINI_API_KEY.

    Returns:
        AsyncOpenAI: Configured OpenAI client pointing to Gemini API

    Raises:
        ValueError: If GEMINI_API_KEY is not set in environment
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment")
        raise ValueError("GEMINI_API_KEY must be set in environment variables")

    logger.info("OpenAI client initialized for Gemini 2.0 Flash")
    return AsyncOpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai"
    )


def get_agent_tools() -> List[Dict[str, Any]]:
    """
    Get OpenAI function tool definitions for all MCP tools.

    Returns:
        List of tool definitions in OpenAI function calling format
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task for the user. Use this when the user wants to add, create, or make a new task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title or name of the task (required, max 200 characters)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional detailed description of the task"
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "Retrieve and list all tasks for the user. Supports filtering by status (all, pending, or completed).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter tasks by status: 'all' (default), 'pending', or 'completed'"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a specific task as completed. Use this when the user indicates they finished, completed, or are done with a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to mark as completed"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Permanently delete a task. Use this when the user wants to remove, delete, or get rid of a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to delete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update a task's title and/or description. Use this when the user wants to modify, change, edit, or update a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New task title (optional if description is provided)"
                        },
                        "description": {
                            "type": "string",
                            "description": "New task description (optional if title is provided)"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        }
    ]

    logger.debug(f"Registered {len(tools)} agent tools")
    return tools

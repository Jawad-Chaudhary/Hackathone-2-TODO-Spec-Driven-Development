# [Task]: T-019, T-020
# [From]: specs/001-ai-todo-chatbot/tasks.md
"""
Gemini Agent with system prompt and MCP tool schemas.

This module defines the TodoAgent class that wraps the Gemini API client
(via OpenAI SDK compatibility layer) with a predefined system prompt
for task management behavior and function schemas matching the 5 MCP tools.
"""

import os
import json
from typing import Optional
from openai import AsyncOpenAI


# System prompt defining agent behavior and trigger word mapping
SYSTEM_PROMPT = """You are a helpful task management assistant. Your role is to help users manage their todo list through natural conversation.

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
- When users say "add", "create", "remember", "need to", or "remind me" → call add_task
- When users say "show", "list", "see", "display", "what are", or "tell me" → call list_tasks
- When users say "pending", "incomplete", "not done", "what's left", or "todo" → call list_tasks with status="pending"
- When users say "completed", "done", "finished", "what did I", or "accomplished" → call list_tasks with status="completed"
- When users say "complete", "done", "finished", "mark as done", "did", or "finish" → call complete_task
- When users say "delete", "remove", "cancel", "forget", or "get rid of" → call delete_task
- When users say "change", "update", "rename", "modify", or "edit" → call update_task

CONFIRMATION TEMPLATES:
- Task Created: "I've added '[TITLE]' to your task list!"
- Task Completed: "Great! I've marked '[TITLE]' as complete. ✓"
- Task Deleted: "I've deleted '[TITLE]' from your task list."
- Task Updated: "Done! I've updated task [ID] to '[NEW_TITLE]'."
- List Empty: "You don't have any tasks yet! Want to add one?"
"""


# MCP tool schemas in OpenAI function format
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task with title and optional description. Use when users want to add, create, or remember something.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique identifier for the user (will be injected automatically)"
                    },
                    "title": {
                        "type": "string",
                        "description": "The task title (1-200 characters)",
                        "minLength": 1,
                        "maxLength": 200
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional task description (max 1000 characters)",
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
            "description": "Retrieve tasks for a user, optionally filtered by status. Use when users want to see, show, list, or display their tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique identifier for the user (will be injected automatically)"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status: 'all' (default), 'pending' (incomplete), or 'completed' (done)",
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
            "description": "Mark a task as complete by its ID. Use when users say they're done, finished, or completed a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique identifier for the user (will be injected automatically)"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to mark as complete",
                        "minimum": 1
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
            "description": "Delete a task by its ID. Use when users want to remove, cancel, forget, or get rid of a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique identifier for the user (will be injected automatically)"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete",
                        "minimum": 1
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
            "description": "Update a task's title or description by its ID. Use when users want to change, update, rename, modify, or edit a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique identifier for the user (will be injected automatically)"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to update",
                        "minimum": 1
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title (1-200 characters)",
                        "minLength": 1,
                        "maxLength": 200
                    },
                    "description": {
                        "type": "string",
                        "description": "New task description (max 1000 characters)",
                        "maxLength": 1000
                    }
                },
                "required": ["user_id", "task_id"]
            }
        }
    }
]


class TodoAgent:
    """
    Gemini Agent wrapper for task management.

    This class initializes a Gemini API client (via OpenAI SDK compatibility)
    with the system prompt and tool schemas for natural language task management.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the TodoAgent with Gemini client.

        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)

        Raises:
            ValueError: If API key is not provided and not in environment
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided or set in environment")

        # Configure AsyncOpenAI client to use Gemini's OpenAI-compatible endpoint
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        )
        self.system_prompt = SYSTEM_PROMPT
        self.tools = TOOL_SCHEMAS
        self.model = "gemini-2.5-flash-lite"  # Gemini 2.5 Flash Lite model

    async def chat(
        self,
        messages: list[dict],
        user_id: str
    ) -> tuple[str, list[dict]]:
        """
        Process a chat message with the agent using Gemini API.

        Args:
            messages: List of message dicts with 'role' and 'content'
                     Format: [{"role": "user", "content": "..."}]
            user_id: User identifier for tool execution context

        Returns:
            Tuple of (response_text, tool_calls)
            - response_text: Agent's natural language response
            - tool_calls: List of tool call dicts with name and arguments

        Example:
            >>> agent = TodoAgent()
            >>> response, tools = await agent.chat(
            ...     [{"role": "user", "content": "Add a task to buy groceries"}],
            ...     user_id="user_123"
            ... )
            >>> print(response)
            "I've added 'Buy groceries' to your task list!"
            >>> print(tools)
            [{"name": "add_task", "arguments": {"user_id": "user_123", "title": "Buy groceries"}}]
        """
        # Build messages with system prompt
        full_messages = [
            {"role": "system", "content": self.system_prompt}
        ] + messages

        # Call Gemini via OpenAI-compatible endpoint with function calling enabled
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            tools=self.tools,
            tool_choice="auto",  # Let model decide when to use tools
            temperature=0.7,
            max_tokens=500
        )

        message = response.choices[0].message

        # Extract response text
        response_text = message.content or ""

        # Extract tool calls
        tool_calls = []
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_calls.append({
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments)
                })

        return response_text, tool_calls

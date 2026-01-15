# [Task]: T-012
# [From]: specs/001-ai-todo-chatbot/tasks.md

"""
MCP Server Package for AI Todo Chatbot

This package implements the Model Context Protocol (MCP) server using the
official Python MCP SDK. It exposes 5 tools for task management:
- add_task: Create new tasks
- list_tasks: List user's tasks with optional status filter
- complete_task: Mark tasks as completed
- delete_task: Delete tasks
- update_task: Update task title/description

All tools enforce user isolation by filtering on user_id.
"""

from .server import server

__all__ = ["server"]

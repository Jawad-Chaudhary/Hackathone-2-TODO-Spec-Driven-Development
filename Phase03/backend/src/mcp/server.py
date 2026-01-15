# [Task]: T-012
# [From]: specs/001-ai-todo-chatbot/tasks.md

"""
MCP Server Implementation with Official Python MCP SDK

This module initializes the MCP server with stdio transport and registers
all 5 task management tools. The server follows the Model Context Protocol
specification and provides stateless tool execution.

Tools registered:
- add_task: Create new tasks
- list_tasks: List user's tasks with status filter
- complete_task: Mark tasks as completed
- delete_task: Delete tasks
- update_task: Update task title/description

All tools enforce user isolation by filtering operations on user_id.
"""

import json
import asyncio
from datetime import datetime
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.session import async_session
from ..models.task import Task


# Initialize MCP server with unique name
server = Server("todo-mcp-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available MCP tools.

    Returns:
        list[Tool]: List of tool definitions with names, descriptions, and input schemas
    """
    return [
        Tool(
            name="add_task",
            description="Create a new task for a user. Requires user_id, title (1-200 chars), and optional description (max 1000 chars).",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID who owns the task"
                    },
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 200,
                        "description": "Task title (1-200 characters)"
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 1000,
                        "description": "Optional task description (max 1000 characters)"
                    }
                },
                "required": ["user_id", "title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List all tasks for a user with optional status filter. Status can be 'all', 'pending', or 'completed'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID whose tasks to list"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status (default: all)",
                        "default": "all"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed. Requires user_id and task_id. Only the task owner can complete it.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID who owns the task"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to complete"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a task. Requires user_id and task_id. Only the task owner can delete it.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID who owns the task"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to delete"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        ),
        Tool(
            name="update_task",
            description="Update a task's title and/or description. Requires user_id, task_id, and at least one field to update. Only the task owner can update it.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID who owns the task"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 200,
                        "description": "New task title (1-200 characters)"
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 1000,
                        "description": "New task description (max 1000 characters)"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Handle tool execution requests.

    This function routes tool calls to the appropriate implementation based on
    the tool name. All tools are stateless and create their own database sessions.

    Args:
        name: Name of the tool to execute
        arguments: Tool-specific arguments as a dictionary

    Returns:
        list[TextContent]: Tool response as JSON text content
    """
    try:
        if name == "add_task":
            return await _add_task(arguments)
        elif name == "list_tasks":
            return await _list_tasks(arguments)
        elif name == "complete_task":
            return await _complete_task(arguments)
        elif name == "delete_task":
            return await _delete_task(arguments)
        elif name == "update_task":
            return await _update_task(arguments)
        else:
            error_result = {
                "error": f"Unknown tool: {name}",
                "status": "error"
            }
            return [TextContent(type="text", text=json.dumps(error_result))]
    except Exception as e:
        error_result = {
            "error": f"Internal server error: {str(e)}",
            "status": "error"
        }
        return [TextContent(type="text", text=json.dumps(error_result))]


async def _add_task(arguments: dict[str, Any]) -> list[TextContent]:
    """
    [Task]: T-013

    Create a new task.

    Args:
        arguments: Dict with user_id, title, and optional description

    Returns:
        list[TextContent]: JSON response with created task or error
    """
    # Validate required fields
    user_id = arguments.get("user_id")
    title = arguments.get("title")

    if not user_id:
        return [TextContent(type="text", text=json.dumps({
            "error": "user_id is required",
            "status": "error"
        }))]

    if not title:
        return [TextContent(type="text", text=json.dumps({
            "error": "title is required",
            "status": "error"
        }))]

    # Validate title length
    if len(title) < 1 or len(title) > 200:
        return [TextContent(type="text", text=json.dumps({
            "error": "title must be between 1 and 200 characters",
            "status": "error"
        }))]

    # Validate description if provided
    description = arguments.get("description")
    if description and len(description) > 1000:
        return [TextContent(type="text", text=json.dumps({
            "error": "description must not exceed 1000 characters",
            "status": "error"
        }))]

    # Create database session and insert task
    try:
        async with async_session() as session:
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)

            result = {
                "status": "success",
                "task": {
                    "id": task.id,
                    "user_id": task.user_id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
            }
            return [TextContent(type="text", text=json.dumps(result))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({
            "error": f"Database error: {str(e)}",
            "status": "error"
        }))]


async def _list_tasks(arguments: dict[str, Any]) -> list[TextContent]:
    """
    [Task]: T-014

    List tasks for a user with optional status filter.

    Args:
        arguments: Dict with user_id and optional status filter

    Returns:
        list[TextContent]: JSON response with task array or error
    """
    # Validate required fields
    user_id = arguments.get("user_id")

    if not user_id:
        return [TextContent(type="text", text=json.dumps({
            "error": "user_id is required",
            "status": "error"
        }))]

    status = arguments.get("status", "all")

    # Validate status filter
    if status not in ["all", "pending", "completed"]:
        return [TextContent(type="text", text=json.dumps({
            "error": "status must be 'all', 'pending', or 'completed'",
            "status": "error"
        }))]

    # Query database with user isolation
    try:
        async with async_session() as session:
            stmt = select(Task).where(Task.user_id == user_id)

            # Apply status filter
            if status == "pending":
                stmt = stmt.where(Task.completed == False)
            elif status == "completed":
                stmt = stmt.where(Task.completed == True)

            # Order by created_at descending (newest first)
            stmt = stmt.order_by(Task.created_at.desc())

            result = await session.execute(stmt)
            tasks = result.scalars().all()

            task_list = [
                {
                    "id": task.id,
                    "user_id": task.user_id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                for task in tasks
            ]

            response = {
                "status": "success",
                "tasks": task_list,
                "count": len(task_list)
            }
            return [TextContent(type="text", text=json.dumps(response))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({
            "error": f"Database error: {str(e)}",
            "status": "error"
        }))]


async def _complete_task(arguments: dict[str, Any]) -> list[TextContent]:
    """
    [Task]: T-015

    Mark a task as completed.

    Args:
        arguments: Dict with user_id and task_id

    Returns:
        list[TextContent]: JSON response with updated task or error
    """
    # Validate required fields
    user_id = arguments.get("user_id")
    task_id = arguments.get("task_id")

    if not user_id:
        return [TextContent(type="text", text=json.dumps({
            "error": "user_id is required",
            "status": "error"
        }))]

    if not task_id:
        return [TextContent(type="text", text=json.dumps({
            "error": "task_id is required",
            "status": "error"
        }))]

    # Query and update with user isolation
    try:
        async with async_session() as session:
            stmt = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            result = await session.execute(stmt)
            task = result.scalar_one_or_none()

            if not task:
                return [TextContent(type="text", text=json.dumps({
                    "error": "Task not found or access denied",
                    "status": "error"
                }))]

            # Update task
            task.completed = True
            task.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(task)

            response = {
                "status": "success",
                "task": {
                    "id": task.id,
                    "user_id": task.user_id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
            }
            return [TextContent(type="text", text=json.dumps(response))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({
            "error": f"Database error: {str(e)}",
            "status": "error"
        }))]


async def _delete_task(arguments: dict[str, Any]) -> list[TextContent]:
    """
    [Task]: T-016

    Delete a task.

    Args:
        arguments: Dict with user_id and task_id

    Returns:
        list[TextContent]: JSON response with status or error
    """
    # Validate required fields
    user_id = arguments.get("user_id")
    task_id = arguments.get("task_id")

    if not user_id:
        return [TextContent(type="text", text=json.dumps({
            "error": "user_id is required",
            "status": "error"
        }))]

    if not task_id:
        return [TextContent(type="text", text=json.dumps({
            "error": "task_id is required",
            "status": "error"
        }))]

    # Query and delete with user isolation
    try:
        async with async_session() as session:
            stmt = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            result = await session.execute(stmt)
            task = result.scalar_one_or_none()

            if not task:
                return [TextContent(type="text", text=json.dumps({
                    "error": "Task not found or access denied",
                    "status": "error"
                }))]

            # Delete task
            await session.delete(task)
            await session.commit()

            response = {
                "status": "success",
                "message": f"Task {task_id} deleted successfully"
            }
            return [TextContent(type="text", text=json.dumps(response))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({
            "error": f"Database error: {str(e)}",
            "status": "error"
        }))]


async def _update_task(arguments: dict[str, Any]) -> list[TextContent]:
    """
    [Task]: T-017

    Update a task's title and/or description.

    Args:
        arguments: Dict with user_id, task_id, and optional title/description

    Returns:
        list[TextContent]: JSON response with updated task or error
    """
    # Validate required fields
    user_id = arguments.get("user_id")
    task_id = arguments.get("task_id")

    if not user_id:
        return [TextContent(type="text", text=json.dumps({
            "error": "user_id is required",
            "status": "error"
        }))]

    if not task_id:
        return [TextContent(type="text", text=json.dumps({
            "error": "task_id is required",
            "status": "error"
        }))]

    # Get update fields
    title = arguments.get("title")
    description = arguments.get("description")

    # Validate at least one field to update
    if title is None and description is None:
        return [TextContent(type="text", text=json.dumps({
            "error": "At least one field (title or description) must be provided",
            "status": "error"
        }))]

    # Validate title if provided
    if title is not None and (len(title) < 1 or len(title) > 200):
        return [TextContent(type="text", text=json.dumps({
            "error": "title must be between 1 and 200 characters",
            "status": "error"
        }))]

    # Validate description if provided
    if description is not None and len(description) > 1000:
        return [TextContent(type="text", text=json.dumps({
            "error": "description must not exceed 1000 characters",
            "status": "error"
        }))]

    # Query and update with user isolation
    try:
        async with async_session() as session:
            stmt = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            result = await session.execute(stmt)
            task = result.scalar_one_or_none()

            if not task:
                return [TextContent(type="text", text=json.dumps({
                    "error": "Task not found or access denied",
                    "status": "error"
                }))]

            # Update fields
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description

            task.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(task)

            response = {
                "status": "success",
                "task": {
                    "id": task.id,
                    "user_id": task.user_id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
            }
            return [TextContent(type="text", text=json.dumps(response))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({
            "error": f"Database error: {str(e)}",
            "status": "error"
        }))]


async def main() -> None:
    """
    Main entry point for the MCP server.

    Initializes the server with stdio transport and runs it to handle
    incoming MCP protocol messages.
    """
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())

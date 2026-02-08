"""
MCP Server implementation for todo task management.

This module provides the MCP server boilerplate and tool registration
utilities following the official Python MCP SDK patterns.
"""

import logging
from typing import List, Callable, Any, Dict

# Configure logging
logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP Server for managing todo task tools.

    This server registers and manages MCP tools for task operations:
    - add_task: Create a new task
    - list_tasks: Retrieve tasks with filtering
    - complete_task: Mark a task as completed
    - delete_task: Remove a task
    - update_task: Modify task details
    """

    def __init__(self):
        """Initialize the MCP server with empty tool registry."""
        self.tools: Dict[str, Callable] = {}
        logger.info("MCP Server initialized")

    def register_tool(self, name: str, tool_function: Callable) -> None:
        """
        Register a tool with the MCP server.

        Args:
            name: Unique tool identifier
            tool_function: Callable that implements the tool logic

        Raises:
            ValueError: If tool name already registered
        """
        if name in self.tools:
            raise ValueError(f"Tool '{name}' is already registered")

        self.tools[name] = tool_function
        logger.info(f"Registered tool: {name}")

    def get_tool(self, name: str) -> Callable:
        """
        Retrieve a registered tool by name.

        Args:
            name: Tool identifier

        Returns:
            Tool function callable

        Raises:
            KeyError: If tool not found
        """
        if name not in self.tools:
            raise KeyError(f"Tool '{name}' not found")

        return self.tools[name]

    def list_tools(self) -> List[str]:
        """
        Get list of all registered tool names.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())

    async def execute_tool(self, name: str, **kwargs: Any) -> Any:
        """
        Execute a registered tool with provided arguments.

        Args:
            name: Tool identifier
            **kwargs: Tool-specific arguments

        Returns:
            Tool execution result

        Raises:
            KeyError: If tool not found
            Exception: Any exception raised by the tool
        """
        tool = self.get_tool(name)

        logger.info(f"Executing tool: {name} with args: {kwargs}")

        try:
            result = await tool(**kwargs)
            logger.info(f"Tool {name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool {name} execution failed: {e}")
            raise


# Global MCP server instance
mcp_server = MCPServer()


def get_mcp_server() -> MCPServer:
    """
    Get the global MCP server instance.

    Returns:
        Global MCPServer instance
    """
    return mcp_server


def register_all_tools() -> None:
    """
    Register all 5 MCP tools with the server.

    This function should be called on application startup to make
    all tools available to the AI agent.
    """
    from app.mcp.tools.add_task import add_task
    from app.mcp.tools.list_tasks import list_tasks
    from app.mcp.tools.complete_task import complete_task
    from app.mcp.tools.delete_task import delete_task
    from app.mcp.tools.update_task import update_task

    mcp_server.register_tool("add_task", add_task)
    mcp_server.register_tool("list_tasks", list_tasks)
    mcp_server.register_tool("complete_task", complete_task)
    mcp_server.register_tool("delete_task", delete_task)
    mcp_server.register_tool("update_task", update_task)

    logger.info("All 5 MCP tools registered successfully")

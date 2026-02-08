"""
Integration tests for MCP server.

Tests:
- Tool registration
- Tool discovery
- All 5 tools are registered
"""

import pytest
from app.mcp.server import MCPServer, register_all_tools, get_mcp_server


def test_mcp_server_initialization():
    """Test MCP server initializes with empty tool registry."""
    server = MCPServer()

    assert server.tools == {}
    assert server.list_tools() == []


def test_register_single_tool():
    """Test registering a single tool."""
    server = MCPServer()

    async def dummy_tool(arg1: str):
        return {"result": arg1}

    server.register_tool("dummy", dummy_tool)

    assert "dummy" in server.tools
    assert server.list_tools() == ["dummy"]
    assert server.get_tool("dummy") == dummy_tool


def test_register_duplicate_tool_raises_error():
    """Test that registering duplicate tool name raises ValueError."""
    server = MCPServer()

    async def tool1():
        pass

    async def tool2():
        pass

    server.register_tool("test_tool", tool1)

    with pytest.raises(ValueError, match="already registered"):
        server.register_tool("test_tool", tool2)


def test_get_nonexistent_tool_raises_error():
    """Test that getting non-existent tool raises KeyError."""
    server = MCPServer()

    with pytest.raises(KeyError, match="not found"):
        server.get_tool("nonexistent")


def test_register_all_tools():
    """Test that register_all_tools registers all 5 MCP tools."""
    # Get fresh server instance
    server = MCPServer()

    # Import and register
    from app.mcp.tools.add_task import add_task
    from app.mcp.tools.list_tasks import list_tasks
    from app.mcp.tools.complete_task import complete_task
    from app.mcp.tools.delete_task import delete_task
    from app.mcp.tools.update_task import update_task

    server.register_tool("add_task", add_task)
    server.register_tool("list_tasks", list_tasks)
    server.register_tool("complete_task", complete_task)
    server.register_tool("delete_task", delete_task)
    server.register_tool("update_task", update_task)

    # Verify all 5 tools are registered
    tools = server.list_tools()
    assert len(tools) == 5
    assert "add_task" in tools
    assert "list_tasks" in tools
    assert "complete_task" in tools
    assert "delete_task" in tools
    assert "update_task" in tools


def test_get_mcp_server_returns_singleton():
    """Test that get_mcp_server returns the same instance."""
    server1 = get_mcp_server()
    server2 = get_mcp_server()

    assert server1 is server2


@pytest.mark.asyncio
async def test_execute_tool():
    """Test executing a registered tool."""
    server = MCPServer()

    async def test_tool(value: int):
        return {"doubled": value * 2}

    server.register_tool("doubler", test_tool)

    result = await server.execute_tool("doubler", value=5)

    assert result == {"doubled": 10}


@pytest.mark.asyncio
async def test_execute_nonexistent_tool():
    """Test executing non-existent tool raises KeyError."""
    server = MCPServer()

    with pytest.raises(KeyError, match="not found"):
        await server.execute_tool("nonexistent", arg=1)


@pytest.mark.asyncio
async def test_execute_tool_with_error():
    """Test that tool errors are propagated."""
    server = MCPServer()

    async def failing_tool():
        raise ValueError("Tool failed")

    server.register_tool("failer", failing_tool)

    with pytest.raises(ValueError, match="Tool failed"):
        await server.execute_tool("failer")

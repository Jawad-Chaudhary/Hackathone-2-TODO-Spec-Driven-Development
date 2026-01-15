#!/usr/bin/env python3
# [Task]: T-012 through T-018 Verification Script
# [From]: specs/001-ai-todo-chatbot/tasks.md

"""
MCP Server Verification Script

This script validates that all MCP server components are correctly implemented:
- All 8 files exist
- All files have correct task references
- Server can be imported without errors
- All 5 tools are registered
"""

import sys
from pathlib import Path


def verify_files():
    """Verify all required files exist."""
    print("Verifying MCP file structure...")

    required_files = [
        "src/mcp/__init__.py",
        "src/mcp/server.py",
        "src/mcp/tools/__init__.py",
        "src/mcp/tools/add_task.py",
        "src/mcp/tools/list_tasks.py",
        "src/mcp/tools/complete_task.py",
        "src/mcp/tools/delete_task.py",
        "src/mcp/tools/update_task.py",
    ]

    backend_dir = Path(__file__).parent
    missing_files = []

    for file_path in required_files:
        full_path = backend_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)
            print(f"  ✗ Missing: {file_path}")
        else:
            print(f"  ✓ Found: {file_path}")

    if missing_files:
        print(f"\n❌ FAILED: {len(missing_files)} file(s) missing")
        return False

    print("\n✅ All required files exist")
    return True


def verify_task_references():
    """Verify task reference comments in files."""
    print("\nVerifying task references...")

    task_files = {
        "src/mcp/server.py": "T-012",
        "src/mcp/tools/add_task.py": "T-013",
        "src/mcp/tools/list_tasks.py": "T-014",
        "src/mcp/tools/complete_task.py": "T-015",
        "src/mcp/tools/delete_task.py": "T-016",
        "src/mcp/tools/update_task.py": "T-017",
    }

    backend_dir = Path(__file__).parent
    missing_refs = []

    for file_path, expected_task in task_files.items():
        full_path = backend_dir / file_path
        content = full_path.read_text()
        if f"[Task]: {expected_task}" not in content and f"# {expected_task}" not in content:
            missing_refs.append((file_path, expected_task))
            print(f"  ✗ {file_path}: Missing task reference {expected_task}")
        else:
            print(f"  ✓ {file_path}: Has task reference {expected_task}")

    if missing_refs:
        print(f"\n❌ FAILED: {len(missing_refs)} task reference(s) missing")
        return False

    print("\n✅ All task references present")
    return True


def verify_imports():
    """Verify server can be imported."""
    print("\nVerifying server imports...")

    try:
        # Add src to path
        backend_dir = Path(__file__).parent
        sys.path.insert(0, str(backend_dir))

        # Try importing the server
        from src.mcp import server

        print("  ✓ Server module imported successfully")

        # Check server instance
        if not hasattr(server, 'server'):
            print("  ✗ Server instance not found")
            return False

        print("  ✓ Server instance exists")

        # Check for required methods
        server_obj = server.server
        if not hasattr(server_obj, 'list_tools'):
            print("  ✗ list_tools decorator not found")
            return False

        print("  ✓ list_tools decorator found")

        if not hasattr(server_obj, 'call_tool'):
            print("  ✗ call_tool decorator not found")
            return False

        print("  ✓ call_tool decorator found")

        print("\n✅ Server imports and structure valid")
        return True

    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        print("\n❌ FAILED: Server cannot be imported")
        return False
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        print("\n❌ FAILED: Server validation error")
        return False


def verify_tool_names():
    """Verify all 5 tools are implemented in server.py."""
    print("\nVerifying tool implementations...")

    backend_dir = Path(__file__).parent
    server_file = backend_dir / "src/mcp/server.py"
    content = server_file.read_text()

    required_tools = [
        "add_task",
        "list_tasks",
        "complete_task",
        "delete_task",
        "update_task"
    ]

    missing_tools = []

    for tool_name in required_tools:
        # Check if tool is in list_tools
        if f'name="{tool_name}"' not in content and f"name='{tool_name}'" not in content:
            missing_tools.append(tool_name)
            print(f"  ✗ Tool not found in list_tools: {tool_name}")
        else:
            print(f"  ✓ Tool found in list_tools: {tool_name}")

        # Check if tool has implementation function
        if f"async def _{tool_name}" not in content:
            missing_tools.append(f"_{tool_name} (implementation)")
            print(f"  ✗ Implementation function not found: _{tool_name}")
        else:
            print(f"  ✓ Implementation function found: _{tool_name}")

    if missing_tools:
        print(f"\n❌ FAILED: {len(missing_tools)} tool(s) or implementation(s) missing")
        return False

    print("\n✅ All 5 tools implemented")
    return True


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("MCP Server Implementation Verification")
    print("Tasks: T-012 through T-018")
    print("=" * 60)
    print()

    results = []

    # Run all checks
    results.append(("File Structure", verify_files()))
    results.append(("Task References", verify_task_references()))
    results.append(("Tool Implementations", verify_tool_names()))
    results.append(("Server Imports", verify_imports()))

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    for check_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check_name}")

    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL CHECKS PASSED")
        print("=" * 60)
        print("\nMCP server is ready for integration!")
        print("\nNext steps:")
        print("  1. T-019: Initialize OpenAI Agent")
        print("  2. T-020: Register MCP tools as OpenAI functions")
        print("  3. T-021: Implement agent execution")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("=" * 60)
        print("\nPlease review the errors above and fix issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

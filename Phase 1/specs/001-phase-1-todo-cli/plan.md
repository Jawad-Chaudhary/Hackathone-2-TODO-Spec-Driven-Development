# Implementation Plan: Phase 1 - Python Console Todo App

**Branch**: `001-phase-1-todo-cli` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase-1-todo-cli/spec.md`

## Summary

Build a Python 3.13+ console application for task management with in-memory storage. The application provides CRUD operations (Create, Read, Update, Delete, Mark Complete) through a text-based menu interface using only Python standard library modules. All data is stored in memory and lost on exit. The architecture prioritizes simplicity, testability, and strict adherence to TDD workflow with 80%+ test coverage.

**Primary Approach**: Single-file CLI application with dataclass-based Task model, global in-memory storage, function-based architecture, and `input()`-based menu system (not argparse for menu, but for potential command-line args).

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Python standard library only (`dataclasses`, `datetime`, `uuid`, `typing`)
**Storage**: In-memory (global `list[Task]` variable)
**Testing**: `unittest` (standard library)
**Target Platform**: Cross-platform CLI (Windows, macOS, Linux)
**Project Type**: Single-file console application
**Performance Goals**: All operations complete in <1 second for lists up to 100 tasks
**Constraints**:
- No external dependencies beyond Python stdlib
- No file I/O or database persistence
- Single-user, single-session only
- All functions ≤20 lines
- 80%+ test coverage required

**Scale/Scope**:
- Single Python module (~300-500 lines)
- 5 core CRUD functions + 5 UI handlers + main loop
- Support up to 100 tasks in memory without performance degradation

## Constitution Check

*GATE: Must pass before implementation. Re-checked after code completion.*

✅ **Principle I: Simplicity First**
- Single-file architecture with in-memory list storage
- No databases, no file I/O, no complex state management
- Functions are straightforward CRUD operations

✅ **Principle II: Python Standard Library Only**
- Uses only: `dataclasses`, `datetime`, `uuid`, `typing`, `unittest`
- No pip packages or external dependencies
- UV for environment only (not for installing packages)

✅ **Principle III: Test-Driven Development**
- Plan includes test strategy with unit + integration tests
- TDD workflow: write tests → RED → implement → GREEN → refactor
- Target: 80%+ coverage with `coverage.py` (optional tool for measurement)

✅ **Principle IV: Type Safety**
- All functions use type hints for parameters and return values
- Task model defined as `@dataclass` with typed fields
- Plan specifies exact type signatures for all functions

✅ **Principle V: Clean Code Standards**
- All functions designed to be ≤20 lines
- Single responsibility: each function does one thing
- Descriptive names (no abbreviations)
- Docstrings required (Google style)
- Only one global variable: `TASKS: list[Task] = []`

✅ **Principle VI: Spec-Driven Development**
- This plan directly maps all 20 functional requirements (FR-001 to FR-020)
- Tasks.md will trace to this plan and spec.md
- No features implemented without spec reference

**Status**: All constitution principles satisfied. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/001-phase-1-todo-cli/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (architecture + design)
├── tasks.md             # Task breakdown (created by /sp.tasks)
└── checklists/
    └── requirements.md  # Spec quality checklist (completed)
```

### Source Code (repository root)

```text
src/
└── todo_app.py          # Single-file application (all code in one file)

tests/
├── test_todo_app.py     # Comprehensive test suite
└── __init__.py

README.md                # Usage instructions and examples
```

**Structure Decision**: Single-file architecture chosen for maximum simplicity per Constitution Principle I. All code (Task model, CRUD functions, UI handlers, main loop) resides in `src/todo_app.py`. This eliminates module complexity and makes the codebase immediately understandable for Phase 1 learning objectives.

## Complexity Tracking

No violations - constitution fully satisfied with simplest possible approach.

---

## Architecture Overview

### High-Level Component Diagram

```text
┌─────────────────────────────────────────────────────┐
│                   USER (Terminal)                    │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              MAIN LOOP (main function)               │
│  - Display menu                                      │
│  - Get user selection                                │
│  - Route to handler                                  │
│  - Handle errors                                     │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
┌────────────┐ ┌──────────┐ ┌────────────┐
│ UI LAYER   │ │ UI LAYER │ │  UI LAYER  │
│ handle_add │ │ handle_  │ │  handle_   │
│            │ │ view     │ │  delete    │
└─────┬──────┘ └────┬─────┘ └─────┬──────┘
      │             │              │
      ▼             ▼              ▼
┌─────────────────────────────────────────────────────┐
│                 CORE LOGIC LAYER                     │
│  add_task()     view_tasks()    update_task()       │
│  delete_task()  toggle_complete() find_task_by_id() │
│                                                      │
│  - Validation                                        │
│  - Business rules                                    │
│  - Data manipulation                                 │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│            DATA LAYER (In-Memory Storage)            │
│                                                      │
│  TASKS: list[Task] = []  (global variable)          │
│                                                      │
│  Task @dataclass:                                    │
│    - id: UUID                                        │
│    - title: str                                      │
│    - description: str                                │
│    - completed: bool                                 │
│    - created_at: datetime                            │
└─────────────────────────────────────────────────────┘
```

### Data Flow

```text
1. User Input → Main Loop → UI Handler → Core Function → Data Layer
2. Data Layer → Core Function → UI Handler → Main Loop → Display Output
3. Error → Core Function (raise ValueError) → Main Loop (catch) → Display Error
```

---

## Data Model

### Task Dataclass

```python
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Task:
    """
    Represents a single todo task.

    Attributes:
        id: Unique identifier (UUID4), auto-generated, immutable
        title: Short descriptive text (required, trimmed)
        description: Optional detailed text (can be empty)
        completed: Completion status (defaults to False)
        created_at: Task creation timestamp (auto-captured, immutable)
    """
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate and normalize title after initialization."""
        # Trim whitespace from title (FR-004)
        self.title = self.title.strip()
        # Validate title is non-empty after trimming
        if not self.title:
            raise ValueError("Error: Title cannot be empty")
```

**Constraints**:
- `id`: Immutable after creation, unique per task
- `title`: Required, non-empty after trimming whitespace
- `description`: Optional, can be empty string
- `completed`: Defaults to `False`, toggleable
- `created_at`: Immutable after creation, auto-set to current time

---

## Core Functions

### 1. add_task

```python
def add_task(title: str, description: str = "") -> Task:
    """
    Create and store a new task with the given title and optional description.

    Args:
        title: Task title (will be trimmed, must be non-empty after trim)
        description: Optional task description (defaults to empty string)

    Returns:
        The newly created Task object

    Raises:
        ValueError: If title is empty or whitespace-only after trimming

    Test Criteria:
        - Creates task with valid title
        - Creates task with title + description
        - Trims leading/trailing whitespace from title
        - Raises ValueError for empty title
        - Raises ValueError for whitespace-only title
        - Assigns unique UUID to each task
        - Sets created_at to current timestamp
        - Sets completed to False by default
        - Adds task to global TASKS list
    """
    # Title will be trimmed and validated in Task.__post_init__
    task = Task(title=title, description=description)
    TASKS.append(task)
    return task
```

### 2. find_task_by_id

```python
def find_task_by_id(task_id_input: str) -> Task:
    """
    Find a task by full UUID or 8-character prefix.

    Args:
        task_id_input: Full UUID string (36 chars) or 8-char hex prefix

    Returns:
        The matching Task object

    Raises:
        ValueError: If task_id_input format is invalid (not UUID or 8-char hex)
        ValueError: If no task found with the given ID
        ValueError: If 8-char prefix matches multiple tasks (ambiguous)

    Test Criteria:
        - Finds task by full UUID (36 chars with hyphens)
        - Finds task by 8-character prefix
        - Raises ValueError for invalid format (not hex or wrong length)
        - Raises ValueError for non-existent task
        - Raises ValueError if prefix matches multiple tasks
        - Case-insensitive matching for hex characters
    """
    task_id_input = task_id_input.strip().lower()

    # Validate format: full UUID or 8-char hex
    if len(task_id_input) == 36:
        # Full UUID with hyphens
        try:
            target_uuid = UUID(task_id_input)
        except ValueError:
            raise ValueError("Error: Invalid task ID format")
    elif len(task_id_input) == 8:
        # 8-character hex prefix
        if not all(c in '0123456789abcdef' for c in task_id_input):
            raise ValueError("Error: Invalid task ID format")
        # Find matching task(s) by prefix
        matches = [t for t in TASKS if str(t.id).startswith(task_id_input)]
        if len(matches) == 0:
            raise ValueError(f"Error: Task not found with ID {task_id_input}")
        if len(matches) > 1:
            raise ValueError(f"Error: Ambiguous ID prefix {task_id_input}")
        return matches[0]
    else:
        raise ValueError("Error: Invalid task ID format")

    # Search by full UUID
    for task in TASKS:
        if task.id == target_uuid:
            return task
    raise ValueError(f"Error: Task not found with ID {task_id_input}")
```

### 3. view_tasks

```python
def view_tasks() -> list[Task]:
    """
    Retrieve all tasks in creation order.

    Returns:
        List of all Task objects (may be empty)

    Test Criteria:
        - Returns empty list when no tasks exist
        - Returns all tasks in creation order (FIFO)
        - Does not modify task data
        - Returns copy or original list (implementation detail)
    """
    return TASKS.copy()  # Return copy to prevent external modification
```

### 4. update_task

```python
def update_task(task_id_input: str, new_title: str | None,
                new_description: str | None) -> Task:
    """
    Update a task's title and/or description.

    Args:
        task_id_input: Full UUID or 8-char prefix
        new_title: New title or None to keep existing
        new_description: New description or None to keep existing

    Returns:
        The updated Task object

    Raises:
        ValueError: If task not found
        ValueError: If new_title is empty/whitespace after trimming
        ValueError: If task_id_input format is invalid

    Test Criteria:
        - Updates only title when new_title provided, new_description is None
        - Updates only description when new_description provided, new_title is None
        - Updates both when both provided
        - Keeps existing values when both are None (no-op)
        - Raises ValueError if new_title is empty after trimming
        - Trims whitespace from new_title before validation
        - Raises ValueError if task not found
        - Does not modify created_at or id
    """
    task = find_task_by_id(task_id_input)  # Validates ID and finds task

    if new_title is not None:
        trimmed_title = new_title.strip()
        if not trimmed_title:
            raise ValueError("Error: Title cannot be empty")
        task.title = trimmed_title

    if new_description is not None:
        task.description = new_description

    return task
```

### 5. delete_task

```python
def delete_task(task_id_input: str) -> Task:
    """
    Delete a task by ID and return the deleted task.

    Args:
        task_id_input: Full UUID or 8-char prefix

    Returns:
        The deleted Task object

    Raises:
        ValueError: If task not found
        ValueError: If task_id_input format is invalid

    Test Criteria:
        - Removes task from TASKS list
        - Returns the deleted task object
        - Raises ValueError if task not found
        - Does not affect other tasks
        - Decreases len(TASKS) by 1
    """
    task = find_task_by_id(task_id_input)  # Validates ID and finds task
    TASKS.remove(task)
    return task
```

### 6. toggle_complete

```python
def toggle_complete(task_id_input: str) -> Task:
    """
    Toggle a task's completion status (True ↔ False).

    Args:
        task_id_input: Full UUID or 8-char prefix

    Returns:
        The updated Task object with toggled status

    Raises:
        ValueError: If task not found
        ValueError: If task_id_input format is invalid

    Test Criteria:
        - Changes completed from False to True
        - Changes completed from True to False
        - Returns the updated task
        - Raises ValueError if task not found
        - Does not modify other task fields
    """
    task = find_task_by_id(task_id_input)  # Validates ID and finds task
    task.completed = not task.completed
    return task
```

---

## UI Functions

### 1. display_menu

```python
def display_menu() -> None:
    """
    Display the main menu with 6 numbered options.

    Output format (FR-001):
        ===== TODO APP MENU =====
        1. Add Task
        2. View Tasks
        3. Update Task
        4. Delete Task
        5. Mark Complete/Incomplete
        6. Exit
        =========================
    """
    print("\n===== TODO APP MENU =====")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Complete/Incomplete")
    print("6. Exit")
    print("=========================")
```

### 2. display_tasks

```python
def display_tasks(tasks: list[Task]) -> None:
    """
    Display all tasks in a formatted table.

    Args:
        tasks: List of Task objects to display

    Output format (FR-008):
        - Empty list: "No tasks found. Your todo list is empty."
        - Non-empty: Table with columns ID, Title, Description, Status, Created
        - ID: First 8 chars of UUID
        - Description: Truncated to 50 chars + "..." if longer
        - Status: [✓] for complete, [ ] for incomplete
        - Created: YYYY-MM-DD HH:MM format

    Example:
        ID       | Title         | Description              | Status | Created
        ---------|---------------|--------------------------|--------|------------------
        a1b2c3d4 | Buy groceries | Get milk, eggs, bread    | [ ]    | 2025-12-30 14:30
        e5f6g7h8 | Finish report | Complete Q4 analysis...  | [✓]    | 2025-12-30 15:45
    """
    if not tasks:
        print("\nNo tasks found. Your todo list is empty.")
        return

    print(f"\n{'ID':<10} | {'Title':<20} | {'Description':<53} | {'Status':<6} | {'Created':<16}")
    print("-" * 115)

    for task in tasks:
        task_id_short = str(task.id)[:8]
        status = "[✓]" if task.completed else "[ ]"
        created_str = task.created_at.strftime("%Y-%m-%d %H:%M")

        # Truncate description to 50 chars + "..." if longer
        desc_display = task.description
        if len(desc_display) > 50:
            desc_display = desc_display[:50] + "..."

        print(f"{task_id_short:<10} | {task.title:<20} | {desc_display:<53} | {status:<6} | {created_str:<16}")
```

### 3. handle_add

```python
def handle_add() -> None:
    """
    Handle the "Add Task" menu option with user prompts.

    Prompts:
        - "Enter task title: "
        - "Enter task description (optional, press Enter to skip): "

    Output:
        - Success: "Success: Task added with ID [UUID]"
        - Error: Caught by main loop and displayed
    """
    title = input("Enter task title: ")
    description = input("Enter task description (optional, press Enter to skip): ")

    task = add_task(title, description)  # May raise ValueError
    print(f"Success: Task added with ID {task.id}")
```

### 4. handle_view

```python
def handle_view() -> None:
    """
    Handle the "View Tasks" menu option.

    Retrieves all tasks and displays them using display_tasks().
    """
    tasks = view_tasks()
    display_tasks(tasks)
```

### 5. handle_update

```python
def handle_update() -> None:
    """
    Handle the "Update Task" menu option with sequential prompts.

    Prompts (FR-011):
        - "Enter task ID: "
        - "Enter new title (press Enter to keep current): "
        - "Enter new description (press Enter to keep current): "

    Logic:
        - Empty input (just Enter) = keep existing value (None passed to update_task)
        - Non-empty input = new value

    Output:
        - Success: "Success: Task [ID] updated"
        - Error: Caught by main loop and displayed
    """
    task_id_input = input("Enter task ID: ")

    new_title_input = input("Enter new title (press Enter to keep current): ")
    new_title = new_title_input if new_title_input else None

    new_desc_input = input("Enter new description (press Enter to keep current): ")
    new_desc = new_desc_input if new_desc_input else None

    task = update_task(task_id_input, new_title, new_desc)  # May raise ValueError
    print(f"Success: Task {str(task.id)[:8]} updated")
```

### 6. handle_delete

```python
def handle_delete() -> None:
    """
    Handle the "Delete Task" menu option.

    Prompts:
        - "Enter task ID to delete: "

    Output:
        - Success: "Success: Task [ID] deleted"
        - Error: Caught by main loop and displayed
    """
    task_id_input = input("Enter task ID to delete: ")
    task = delete_task(task_id_input)  # May raise ValueError
    print(f"Success: Task {str(task.id)[:8]} deleted")
```

### 7. handle_toggle

```python
def handle_toggle() -> None:
    """
    Handle the "Mark Complete/Incomplete" menu option.

    Prompts:
        - "Enter task ID: "

    Output:
        - Success: "Success: Task [ID] marked as complete" or "...as incomplete"
        - Error: Caught by main loop and displayed
    """
    task_id_input = input("Enter task ID: ")
    task = toggle_complete(task_id_input)  # May raise ValueError
    status_word = "complete" if task.completed else "incomplete"
    print(f"Success: Task {str(task.id)[:8]} marked as {status_word}")
```

---

## Main Loop

### main function

```python
def main() -> None:
    """
    Main application loop.

    Flow:
        1. Display welcome message
        2. Loop until user selects Exit (option 6):
            a. Display menu
            b. Get user selection
            c. Validate selection (1-6)
            d. Route to appropriate handler
            e. Catch and display errors
        3. Display goodbye message
        4. Exit with code 0

    Error Handling:
        - Invalid menu selection: Display error, re-prompt
        - ValueError from core functions: Display error message, re-prompt
        - Any other exception: Display generic error, re-prompt (shouldn't happen)
    """
    print("Welcome to TODO App - Phase 1")
    print("All data is stored in memory and will be lost when you exit.\n")

    while True:
        display_menu()
        choice = input("\nEnter your choice (1-6): ").strip()

        try:
            if choice == "1":
                handle_add()
            elif choice == "2":
                handle_view()
            elif choice == "3":
                handle_update()
            elif choice == "4":
                handle_delete()
            elif choice == "5":
                handle_toggle()
            elif choice == "6":
                print("\nGoodbye! Your tasks have been discarded.")
                break  # Exit loop
            else:
                print("Error: Invalid choice. Please enter a number between 1 and 6.")
        except ValueError as e:
            # Display error from core functions (e.g., "Error: Task not found")
            print(f"\n{e}")
        except Exception as e:
            # Catch-all for unexpected errors (should not happen in normal operation)
            print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()
```

---

## Global State

```python
# Global in-memory storage (only allowed global variable per Constitution)
TASKS: list[Task] = []
```

**Rationale**: Single global variable is the simplest approach for in-memory storage. Alternative (passing tasks list to every function) adds unnecessary complexity for Phase 1 scope. This is explicitly allowed by Constitution Principle V.

---

## Error Handling Strategy

### Error Types

1. **Business Logic Errors** (raised as `ValueError`):
   - Empty title (after trimming)
   - Invalid task ID format
   - Task not found
   - Ambiguous task ID prefix

2. **User Input Errors** (handled in main loop):
   - Invalid menu selection (1-6)
   - Caught by try/except in main()

3. **Unexpected Errors** (logged but shouldn't occur):
   - Generic catch-all in main loop

### Error Message Format

All error messages follow spec requirements (FR-018):
- `"Error: Title cannot be empty"` (FR-004)
- `"Error: Invalid task ID format"` (FR-015)
- `"Error: Task not found with ID {id}"` (FR-014)
- `"Error: Invalid choice. Please enter a number between 1 and 6."` (FR-002)

---

## Testing Strategy

### Test Structure

```python
# tests/test_todo_app.py
import unittest
from datetime import datetime
from uuid import UUID
from src.todo_app import (
    Task, TASKS, add_task, find_task_by_id, view_tasks,
    update_task, delete_task, toggle_complete
)

class TestTaskDataclass(unittest.TestCase):
    """Test Task dataclass initialization and validation."""

    def setUp(self):
        global TASKS
        TASKS.clear()  # Reset global state before each test

    def test_task_creation_with_title(self):
        task = Task(title="Test Task")
        self.assertIsInstance(task.id, UUID)
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "")
        self.assertFalse(task.completed)
        self.assertIsInstance(task.created_at, datetime)

    def test_task_title_trimming(self):
        task = Task(title="  Spaced Title  ")
        self.assertEqual(task.title, "Spaced Title")

    def test_task_empty_title_raises_error(self):
        with self.assertRaises(ValueError):
            Task(title="")

    def test_task_whitespace_only_title_raises_error(self):
        with self.assertRaises(ValueError):
            Task(title="   ")


class TestAddTask(unittest.TestCase):
    """Test add_task function."""

    def setUp(self):
        global TASKS
        TASKS.clear()

    def test_add_task_with_title_only(self):
        task = add_task("Buy milk")
        self.assertEqual(task.title, "Buy milk")
        self.assertEqual(task.description, "")
        self.assertEqual(len(TASKS), 1)

    def test_add_task_with_title_and_description(self):
        task = add_task("Buy milk", "2% organic")
        self.assertEqual(task.title, "Buy milk")
        self.assertEqual(task.description, "2% organic")

    def test_add_task_trims_title(self):
        task = add_task("  Spaced  ")
        self.assertEqual(task.title, "Spaced")

    def test_add_task_empty_title_raises_error(self):
        with self.assertRaises(ValueError) as cm:
            add_task("")
        self.assertIn("Title cannot be empty", str(cm.exception))


class TestFindTaskById(unittest.TestCase):
    """Test find_task_by_id function."""

    def setUp(self):
        global TASKS
        TASKS.clear()
        self.task1 = add_task("Task 1")
        self.task2 = add_task("Task 2")

    def test_find_by_full_uuid(self):
        found = find_task_by_id(str(self.task1.id))
        self.assertEqual(found.id, self.task1.id)

    def test_find_by_8char_prefix(self):
        prefix = str(self.task1.id)[:8]
        found = find_task_by_id(prefix)
        self.assertEqual(found.id, self.task1.id)

    def test_find_invalid_format_raises_error(self):
        with self.assertRaises(ValueError) as cm:
            find_task_by_id("not-a-uuid")
        self.assertIn("Invalid task ID format", str(cm.exception))

    def test_find_nonexistent_raises_error(self):
        with self.assertRaises(ValueError) as cm:
            find_task_by_id("12345678")  # 8 hex chars but no match
        self.assertIn("Task not found", str(cm.exception))


class TestViewTasks(unittest.TestCase):
    """Test view_tasks function."""

    def setUp(self):
        global TASKS
        TASKS.clear()

    def test_view_empty_list(self):
        tasks = view_tasks()
        self.assertEqual(tasks, [])

    def test_view_multiple_tasks(self):
        task1 = add_task("Task 1")
        task2 = add_task("Task 2")
        tasks = view_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].id, task1.id)
        self.assertEqual(tasks[1].id, task2.id)


class TestUpdateTask(unittest.TestCase):
    """Test update_task function."""

    def setUp(self):
        global TASKS
        TASKS.clear()
        self.task = add_task("Original Title", "Original Description")

    def test_update_title_only(self):
        task_id = str(self.task.id)[:8]
        updated = update_task(task_id, "New Title", None)
        self.assertEqual(updated.title, "New Title")
        self.assertEqual(updated.description, "Original Description")

    def test_update_description_only(self):
        task_id = str(self.task.id)[:8]
        updated = update_task(task_id, None, "New Description")
        self.assertEqual(updated.title, "Original Title")
        self.assertEqual(updated.description, "New Description")

    def test_update_both_fields(self):
        task_id = str(self.task.id)[:8]
        updated = update_task(task_id, "New Title", "New Description")
        self.assertEqual(updated.title, "New Title")
        self.assertEqual(updated.description, "New Description")

    def test_update_empty_title_raises_error(self):
        task_id = str(self.task.id)[:8]
        with self.assertRaises(ValueError) as cm:
            update_task(task_id, "  ", None)
        self.assertIn("Title cannot be empty", str(cm.exception))


class TestDeleteTask(unittest.TestCase):
    """Test delete_task function."""

    def setUp(self):
        global TASKS
        TASKS.clear()
        self.task = add_task("To be deleted")

    def test_delete_existing_task(self):
        task_id = str(self.task.id)[:8]
        deleted = delete_task(task_id)
        self.assertEqual(deleted.id, self.task.id)
        self.assertEqual(len(TASKS), 0)

    def test_delete_nonexistent_raises_error(self):
        with self.assertRaises(ValueError):
            delete_task("12345678")


class TestToggleComplete(unittest.TestCase):
    """Test toggle_complete function."""

    def setUp(self):
        global TASKS
        TASKS.clear()
        self.task = add_task("Toggle me")

    def test_toggle_incomplete_to_complete(self):
        task_id = str(self.task.id)[:8]
        self.assertFalse(self.task.completed)
        toggled = toggle_complete(task_id)
        self.assertTrue(toggled.completed)

    def test_toggle_complete_to_incomplete(self):
        task_id = str(self.task.id)[:8]
        toggle_complete(task_id)  # Make it complete
        toggled = toggle_complete(task_id)  # Toggle back
        self.assertFalse(toggled.completed)


class TestIntegrationWorkflow(unittest.TestCase):
    """Integration tests for full CRUD workflows."""

    def setUp(self):
        global TASKS
        TASKS.clear()

    def test_full_crud_cycle(self):
        # Create
        task = add_task("Integration Test", "Full cycle")
        self.assertEqual(len(TASKS), 1)

        # Read
        tasks = view_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "Integration Test")

        # Update
        task_id = str(task.id)[:8]
        update_task(task_id, "Updated Title", None)
        self.assertEqual(TASKS[0].title, "Updated Title")

        # Toggle
        toggle_complete(task_id)
        self.assertTrue(TASKS[0].completed)

        # Delete
        delete_task(task_id)
        self.assertEqual(len(TASKS), 0)


if __name__ == "__main__":
    unittest.main()
```

### Coverage Goals

- **Target**: 80%+ (Constitution requirement)
- **Measured with**: `coverage.py` (optional external tool) or manual calculation
- **Run command**: `python -m coverage run -m unittest discover tests/`
- **Report**: `python -m coverage report -m`

### Manual Testing Checklist

- [ ] All menu options display correctly
- [ ] Add task with title only
- [ ] Add task with title + description
- [ ] Add task with whitespace-only title (should error)
- [ ] View empty task list
- [ ] View task list with 1, 5, 10 tasks
- [ ] Update task title only (press Enter for description)
- [ ] Update task description only (press Enter for title)
- [ ] Update both title and description
- [ ] Delete task by 8-char ID
- [ ] Delete task by full UUID
- [ ] Delete non-existent task (should error)
- [ ] Toggle task from incomplete to complete
- [ ] Toggle task from complete to incomplete
- [ ] Invalid menu selection (0, 7, 'abc')
- [ ] Exit app and verify data is lost

---

## Implementation Notes

### Function Execution Order

1. **Initialization**: Global `TASKS = []` at module level
2. **Main entry**: `if __name__ == "__main__": main()`
3. **Menu loop**: Continuous until user selects Exit (6)
4. **Handler → Core → Data**: Each menu option flows through layers

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Single-file architecture | Simplicity (Constitution I); everything in one place for Phase 1 learning |
| Global `TASKS` variable | Simplest in-memory storage; explicitly allowed by Constitution V |
| `input()` for menu, not argparse | Menu-driven CLI more natural than subcommands for this use case |
| Dataclass for Task | Type safety + automatic `__init__` + immutability support |
| `ValueError` for business logic errors | Standard Python exception for validation failures |
| UUID4 for task IDs | Guaranteed uniqueness without counter management |
| 8-char prefix support | UX improvement while maintaining spec compliance (FR-015) |
| No persistence | Explicit Phase 1 scope boundary (Constitution constraint) |

### Potential Gotchas

1. **Global state in tests**: Must `TASKS.clear()` in `setUp()` to isolate tests
2. **UUID prefix collisions**: Unlikely with UUID4 but technically possible; handled by "ambiguous ID" error
3. **Datetime precision**: `created_at` includes seconds; display format truncates to minutes
4. **Empty input vs. whitespace**: Empty = keep existing (None); explicit whitespace = validation error for title
5. **Description truncation**: Display-only; full description still stored in memory

---

## File Organization Summary

```text
Phase 1 Todo App
├── src/
│   └── todo_app.py           # ~400-500 lines
│       ├── Imports (dataclasses, datetime, uuid, typing)
│       ├── Task dataclass (~15 lines)
│       ├── Global TASKS (~1 line)
│       ├── Core functions (~100 lines total)
│       │   ├── add_task
│       │   ├── find_task_by_id
│       │   ├── view_tasks
│       │   ├── update_task
│       │   ├── delete_task
│       │   └── toggle_complete
│       ├── UI functions (~150 lines total)
│       │   ├── display_menu
│       │   ├── display_tasks
│       │   ├── handle_add
│       │   ├── handle_view
│       │   ├── handle_update
│       │   ├── handle_delete
│       │   └── handle_toggle
│       └── main function (~30 lines)
│
├── tests/
│   ├── __init__.py
│   └── test_todo_app.py      # ~300-400 lines
│       ├── TestTaskDataclass
│       ├── TestAddTask
│       ├── TestFindTaskById
│       ├── TestViewTasks
│       ├── TestUpdateTask
│       ├── TestDeleteTask
│       ├── TestToggleComplete
│       └── TestIntegrationWorkflow
│
├── specs/001-phase-1-todo-cli/
│   ├── spec.md
│   ├── plan.md (this file)
│   └── tasks.md (next step: /sp.tasks)
│
└── README.md                 # Usage instructions
```

---

## Next Steps

1. **Review this plan** against spec.md and constitution.md
2. **Run `/sp.tasks`** to generate `tasks.md` with atomic, testable tasks
3. **TDD Phase**: Implement following Red-Green-Refactor workflow
   - Write tests first (from tasks.md test cases)
   - Run tests (verify RED)
   - Implement minimum code
   - Run tests (verify GREEN)
   - Refactor while keeping tests green

---

**Plan Status**: Complete and ready for task breakdown ✅
**Next Command**: `/sp.tasks` to generate atomic implementation tasks

# Phase 1 - Python Console Todo App

A simple command-line todo application with in-memory storage built using Test-Driven Development (TDD) principles.

## Requirements

- **Python 3.13+**: Required for language features and type hints
- **UV Package Manager** (optional): For virtual environment management

## Setup

### 1. Create Virtual Environment

Using UV (recommended):
```bash
uv venv
```

Or using standard Python:
```bash
python -m venv .venv
```

### 2. Activate Virtual Environment

On Windows:
```bash
.venv\Scripts\activate
```

On macOS/Linux:
```bash
source .venv/bin/activate
```

## Usage

Run the application:
```bash
python src/todo_app.py
```

The application presents a menu-driven interface with the following options:

1. **Add Task**: Create a new task with title and optional description
2. **View Tasks**: Display all tasks in a formatted table
3. **Update Task**: Modify title and/or description of an existing task
4. **Delete Task**: Remove a task from the list
5. **Mark Complete/Incomplete**: Toggle task completion status
6. **Exit**: Quit the application

## Features

- ✅ Create tasks with title and description
- ✅ View all tasks in a formatted table showing:
  - 8-character Task ID
  - Title
  - Description (truncated to 50 characters if longer)
  - Completion status ([✓] or [ ])
  - Creation timestamp (YYYY-MM-DD HH:MM)
- ✅ Update task title and/or description (Enter to keep current)
- ✅ Delete tasks by ID
- ✅ Toggle completion status
- ✅ Input validation (empty titles rejected, whitespace trimmed)
- ✅ UUID-based task identification (full UUID or 8-char prefix supported)
- ✅ Error handling with clear messages

## ⚠️ Important Warning

**All data is stored in memory only**. Your tasks will be lost when you exit the application. This is intentional for Phase 1 - data persistence will be added in future phases.

## Testing

Run the test suite:
```bash
python -m unittest discover tests/ -v
```

Expected output:
```
Ran 23 tests in 0.002s

OK
```

### Test Coverage

The application includes comprehensive unit and integration tests:
- Task dataclass validation (4 tests)
- add_task() function (4 tests)
- view_tasks() function (2 tests)
- find_task_by_id() function (4 tests)
- update_task() function (4 tests)
- delete_task() function (2 tests)
- toggle_complete() function (2 tests)
- Full CRUD integration workflow (1 test)

## Project Structure

```
.
├── src/
│   └── todo_app.py          # Main application (all code in one file)
├── tests/
│   ├── __init__.py
│   └── test_todo_app.py     # Comprehensive test suite
├── specs/
│   └── 001-phase-1-todo-cli/
│       ├── spec.md          # Feature specification
│       ├── plan.md          # Technical implementation plan
│       └── tasks.md         # Task breakdown
└── README.md                # This file
```

## Example Usage

```
$ python src/todo_app.py

Welcome to TODO App - Phase 1
All data is stored in memory and will be lost when you exit.

===== TODO APP MENU =====
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Complete/Incomplete
6. Exit
=========================

Enter your choice (1-6): 1
Enter task title: Buy groceries
Enter task description (optional, press Enter to skip): Get milk, eggs, bread
Success: Task added with ID a1b2c3d4-e5f6-7890-abcd-ef1234567890

Enter your choice (1-6): 2

ID         | Title                | Description                                             | Status | Created
-----------------------------------------------------------------------------------------------------------------------
a1b2c3d4   | Buy groceries        | Get milk, eggs, bread                                   | [ ]    | 2025-12-30 14:30

Enter your choice (1-6): 5
Enter task ID: a1b2c3d4
Success: Task a1b2c3d4 marked as complete

Enter your choice (1-6): 6

Goodbye! Your tasks have been discarded.
```

## Implementation Details

- **Single-file architecture**: All code in `src/todo_app.py` (~350 lines)
- **Python standard library only**: No external dependencies
- **Type-safe**: Full type hints on all functions
- **TDD workflow**: Tests written first, then implementation
- **Clean code**: All functions ≤20 lines, clear naming, comprehensive docstrings
- **Constitution-compliant**: Follows all 6 project principles

## Technical Stack

- **Language**: Python 3.13+
- **Dependencies**: Python standard library only
  - `dataclasses` - Task model
  - `datetime` - Timestamps
  - `uuid` - Unique task IDs
  - `typing` - Type hints
  - `unittest` - Testing framework
- **Storage**: In-memory (list)
- **Interface**: CLI menu-driven

## Future Enhancements (Out of Scope for Phase 1)

- File-based persistence
- Database storage
- Search and filtering
- Task priorities and due dates
- Multi-user support
- Web interface

## License

This project is created for educational purposes as part of a Spec-Driven Development (SDD) learning exercise.

## Contact

For questions or issues, please refer to the project specification documents in `specs/001-phase-1-todo-cli/`.

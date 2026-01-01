# Task: T-002 - Create Task Dataclass with Validation
# From: specs/001-phase-1-todo-cli/plan.md lines 169-201

"""
Phase 1 - Python Console Todo App

A simple command-line todo application with in-memory storage.
All data is lost when the program exits.
"""

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


# Global in-memory storage (only allowed global variable per Constitution)
TASKS: list[Task] = []


# Task: T-004 - Implement add_task() Function
# From: specs/001-phase-1-todo-cli/plan.md lines 213-246

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
    """
    # Title will be trimmed and validated in Task.__post_init__
    task = Task(title=title, description=description)
    TASKS.append(task)
    return task


# Task: T-006 - Implement view_tasks() Function
# From: specs/001-phase-1-todo-cli/plan.md lines 304-321

def view_tasks() -> list[Task]:
    """
    Retrieve all tasks in creation order.

    Returns:
        List of all Task objects (may be empty)
    """
    return TASKS.copy()  # Return copy to prevent external modification


# Task: T-008 - Implement find_task_by_id() Function
# From: specs/001-phase-1-todo-cli/plan.md lines 248-302

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


# Task: T-010 - Implement update_task() Function
# From: specs/001-phase-1-todo-cli/plan.md lines 324-366

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


# Task: T-012 - Implement delete_task() Function
# From: specs/001-phase-1-todo-cli/plan.md lines 369-395

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
    """
    task = find_task_by_id(task_id_input)  # Validates ID and finds task
    TASKS.remove(task)
    return task


# Task: T-014 - Implement toggle_complete() Function
# From: specs/001-phase-1-todo-cli/plan.md lines 397-424

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
    """
    task = find_task_by_id(task_id_input)  # Validates ID and finds task
    task.completed = not task.completed
    return task


# ==============================================================================
# UI LAYER
# ==============================================================================

# Task: T-016 - Implement display_menu() Function

def display_menu() -> None:
    """Display the main menu with 6 numbered options."""
    print("\n===== TODO APP MENU =====")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Complete/Incomplete")
    print("6. Exit")
    print("=========================")


# Task: T-017 - Implement display_tasks() Function

def display_tasks(tasks: list[Task]) -> None:
    """Display all tasks in a formatted table."""
    if not tasks:
        print("\nNo tasks found. Your todo list is empty.")
        return

    print(f"\n{'ID':<10} | {'Title':<20} | {'Description':<53} | {'Status':<6} | {'Created':<16}")
    print("-" * 115)

    for task in tasks:
        task_id_short = str(task.id)[:8]
        status = "[✓]" if task.completed else "[ ]"
        created_str = task.created_at.strftime("%Y-%m-%d %H:%M")
        desc_display = task.description
        if len(desc_display) > 50:
            desc_display = desc_display[:50] + "..."
        print(f"{task_id_short:<10} | {task.title:<20} | {desc_display:<53} | {status:<6} | {created_str:<16}")


# Task: T-018 - Implement handle_add() Function

def handle_add() -> None:
    """Handle the 'Add Task' menu option."""
    title = input("Enter task title: ")
    description = input("Enter task description (optional, press Enter to skip): ")
    task = add_task(title, description)
    print(f"Success: Task added with ID {task.id}")


# Task: T-019 - Implement handle_view() Function

def handle_view() -> None:
    """Handle the 'View Tasks' menu option."""
    tasks = view_tasks()
    display_tasks(tasks)


# Task: T-020 - Implement handle_update() Function

def handle_update() -> None:
    """Handle the 'Update Task' menu option."""
    task_id_input = input("Enter task ID: ")
    new_title_input = input("Enter new title (press Enter to keep current): ")
    new_title = new_title_input if new_title_input else None
    new_desc_input = input("Enter new description (press Enter to keep current): ")
    new_desc = new_desc_input if new_desc_input else None
    task = update_task(task_id_input, new_title, new_desc)
    print(f"Success: Task {str(task.id)[:8]} updated")


# Task: T-021 - Implement handle_delete() Function

def handle_delete() -> None:
    """Handle the 'Delete Task' menu option."""
    task_id_input = input("Enter task ID to delete: ")
    task = delete_task(task_id_input)
    print(f"Success: Task {str(task.id)[:8]} deleted")


# Task: T-022 - Implement handle_toggle() Function

def handle_toggle() -> None:
    """Handle the 'Mark Complete/Incomplete' menu option."""
    task_id_input = input("Enter task ID: ")
    task = toggle_complete(task_id_input)
    status_word = "complete" if task.completed else "incomplete"
    print(f"Success: Task {str(task.id)[:8]} marked as {status_word}")


# ==============================================================================
# MAIN LOOP
# ==============================================================================

# Task: T-023 - Implement main() Function

def main() -> None:
    """Main application loop."""
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
                break
            else:
                print("Error: Invalid choice. Please enter a number between 1 and 6.")
        except ValueError as e:
            print(f"\n{e}")
        except Exception as e:
            print(f"\nUnexpected error: {e}")


# Task: T-024 - Add Entry Point

if __name__ == "__main__":
    main()

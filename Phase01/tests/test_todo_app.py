# Task: T-003 - Write Unit Tests for Task Dataclass
# From: specs/001-phase-1-todo-cli/plan.md lines 723-748

"""
Test suite for Phase 1 - Python Console Todo App
"""

import unittest
from datetime import datetime
from uuid import UUID
import sys
sys.path.insert(0, '../src')
from src.todo_app import (Task, TASKS, add_task, view_tasks, find_task_by_id,
                           update_task, delete_task, toggle_complete)


class TestTaskDataclass(unittest.TestCase):
    """Test Task dataclass initialization and validation."""

    def setUp(self):
        """Reset global state before each test."""
        global TASKS
        TASKS.clear()

    def test_task_creation_with_title(self):
        """Test creating a task with a valid title."""
        task = Task(title="Test Task")
        self.assertIsInstance(task.id, UUID)
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "")
        self.assertFalse(task.completed)
        self.assertIsInstance(task.created_at, datetime)

    def test_task_title_trimming(self):
        """Test that title whitespace is trimmed."""
        task = Task(title="  Spaced Title  ")
        self.assertEqual(task.title, "Spaced Title")

    def test_task_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            Task(title="")
        self.assertIn("Title cannot be empty", str(cm.exception))

    def test_task_whitespace_only_title_raises_error(self):
        """Test that whitespace-only title raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            Task(title="   ")
        self.assertIn("Title cannot be empty", str(cm.exception))


# Task: T-005 - Write Unit Tests for add_task()
# From: specs/001-phase-1-todo-cli/plan.md lines 751-777

class TestAddTask(unittest.TestCase):
    """Test add_task function."""

    def setUp(self):
        """Reset global state before each test."""
        global TASKS
        TASKS.clear()

    def test_add_task_with_title_only(self):
        """Test adding a task with title only."""
        task = add_task("Buy milk")
        self.assertEqual(task.title, "Buy milk")
        self.assertEqual(task.description, "")
        self.assertEqual(len(TASKS), 1)
        self.assertIs(TASKS[0], task)

    def test_add_task_with_title_and_description(self):
        """Test adding a task with title and description."""
        task = add_task("Buy milk", "2% organic")
        self.assertEqual(task.title, "Buy milk")
        self.assertEqual(task.description, "2% organic")
        self.assertEqual(len(TASKS), 1)

    def test_add_task_trims_title(self):
        """Test that add_task trims title whitespace."""
        task = add_task("  Spaced  ")
        self.assertEqual(task.title, "Spaced")

    def test_add_task_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            add_task("")
        self.assertIn("Title cannot be empty", str(cm.exception))


# Task: T-007 - Write Unit Tests for view_tasks()

class TestViewTasks(unittest.TestCase):
    """Test view_tasks function."""

    def setUp(self):
        """Reset global state before each test."""
        global TASKS
        TASKS.clear()

    def test_view_empty_list(self):
        """Test viewing empty task list."""
        tasks = view_tasks()
        self.assertEqual(tasks, [])

    def test_view_multiple_tasks(self):
        """Test viewing multiple tasks in creation order."""
        task1 = add_task("Task 1")
        task2 = add_task("Task 2")
        tasks = view_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].id, task1.id)
        self.assertEqual(tasks[1].id, task2.id)


# Task: T-009 - Write Unit Tests for find_task_by_id()

class TestFindTaskById(unittest.TestCase):
    """Test find_task_by_id function."""

    def setUp(self):
        """Reset global state before each test."""
        global TASKS
        TASKS.clear()
        self.task1 = add_task("Task 1")
        self.task2 = add_task("Task 2")

    def test_find_by_full_uuid(self):
        """Test finding task by full UUID."""
        found = find_task_by_id(str(self.task1.id))
        self.assertEqual(found.id, self.task1.id)

    def test_find_by_8char_prefix(self):
        """Test finding task by 8-character prefix."""
        prefix = str(self.task1.id)[:8]
        found = find_task_by_id(prefix)
        self.assertEqual(found.id, self.task1.id)

    def test_find_invalid_format_raises_error(self):
        """Test that invalid ID format raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            find_task_by_id("not-a-uuid")
        self.assertIn("Invalid task ID format", str(cm.exception))

    def test_find_nonexistent_raises_error(self):
        """Test that non-existent ID raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            find_task_by_id("12345678")
        self.assertIn("Task not found", str(cm.exception))


# Task: T-011 - Write Unit Tests for update_task()

class TestUpdateTask(unittest.TestCase):
    """Test update_task function."""

    def setUp(self):
        """Reset global state before each test."""
        global TASKS
        TASKS.clear()
        self.task = add_task("Original Title", "Original Description")

    def test_update_title_only(self):
        """Test updating title only."""
        task_id = str(self.task.id)[:8]
        updated = update_task(task_id, "New Title", None)
        self.assertEqual(updated.title, "New Title")
        self.assertEqual(updated.description, "Original Description")

    def test_update_description_only(self):
        """Test updating description only."""
        task_id = str(self.task.id)[:8]
        updated = update_task(task_id, None, "New Description")
        self.assertEqual(updated.title, "Original Title")
        self.assertEqual(updated.description, "New Description")

    def test_update_both_fields(self):
        """Test updating both title and description."""
        task_id = str(self.task.id)[:8]
        updated = update_task(task_id, "New Title", "New Description")
        self.assertEqual(updated.title, "New Title")
        self.assertEqual(updated.description, "New Description")

    def test_update_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        task_id = str(self.task.id)[:8]
        with self.assertRaises(ValueError) as cm:
            update_task(task_id, "  ", None)
        self.assertIn("Title cannot be empty", str(cm.exception))


# Task: T-013 - Write Unit Tests for delete_task()

class TestDeleteTask(unittest.TestCase):
    """Test delete_task function."""

    def setUp(self):
        """Reset global state before each test."""
        global TASKS
        TASKS.clear()
        self.task = add_task("To be deleted")

    def test_delete_existing_task(self):
        """Test deleting an existing task."""
        task_id = str(self.task.id)[:8]
        deleted = delete_task(task_id)
        self.assertEqual(deleted.id, self.task.id)
        self.assertEqual(len(TASKS), 0)

    def test_delete_nonexistent_raises_error(self):
        """Test that deleting non-existent task raises ValueError."""
        with self.assertRaises(ValueError):
            delete_task("12345678")


# Task: T-015 - Write Unit Tests for toggle_complete()

class TestToggleComplete(unittest.TestCase):
    """Test toggle_complete function."""

    def setUp(self):
        """Reset global state before each test."""
        global TASKS
        TASKS.clear()
        self.task = add_task("Toggle me")

    def test_toggle_incomplete_to_complete(self):
        """Test toggling from incomplete to complete."""
        task_id = str(self.task.id)[:8]
        self.assertFalse(self.task.completed)
        toggled = toggle_complete(task_id)
        self.assertTrue(toggled.completed)

    def test_toggle_complete_to_incomplete(self):
        """Test toggling from complete to incomplete."""
        task_id = str(self.task.id)[:8]
        toggle_complete(task_id)
        toggled = toggle_complete(task_id)
        self.assertFalse(toggled.completed)


# Task: T-025 - Write Integration Test

class TestIntegrationWorkflow(unittest.TestCase):
    """Integration tests for full CRUD workflows."""

    def setUp(self):
        """Reset global state before each test."""
        global TASKS
        TASKS.clear()

    def test_full_crud_cycle(self):
        """Test full CRUD lifecycle: create → view → update → toggle → delete."""
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

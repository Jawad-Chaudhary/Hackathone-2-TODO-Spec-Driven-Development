# Tasks: Phase 1 - Python Console Todo App

**Input**: Design documents from `/specs/001-phase-1-todo-cli/`
**Prerequisites**: plan.md (complete), spec.md (complete)

**Organization**: Tasks are organized by logical implementation order following TDD workflow. Each task is atomic, independently testable, and traceable to spec/plan.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup & Data Model

**Purpose**: Project structure and foundational Task entity

- [X] T-001 Create project structure with src/ and tests/ directories per plan.md
- [X] T-002 [P] [US1] Create Task dataclass with validation in src/todo_app.py
  - **From**: plan.md lines 169-201 (Task dataclass section)
  - **Description**: Implement the Task dataclass with fields (id, title, description, completed, created_at) and `__post_init__` validation for title trimming and empty check
  - **Preconditions**: Project structure exists (T-001)
  - **Artifacts**: src/todo_app.py (~20 lines)
  - **Implementation**:
    ```python
    from dataclasses import dataclass, field
    from datetime import datetime
    from uuid import UUID, uuid4

    @dataclass
    class Task:
        """Represents a single todo task."""
        id: UUID = field(default_factory=uuid4)
        title: str = ""
        description: str = ""
        completed: bool = False
        created_at: datetime = field(default_factory=datetime.now)

        def __post_init__(self) -> None:
            """Validate and normalize title after initialization."""
            self.title = self.title.strip()
            if not self.title:
                raise ValueError("Error: Title cannot be empty")
    ```
  - **Test Criteria**:
    - ✓ Task created with valid title has UUID, title, empty description, False completed, datetime
    - ✓ Title with whitespace "  Spaced  " trims to "Spaced"
    - ✓ Empty title "" raises ValueError with "Title cannot be empty"
    - ✓ Whitespace-only title "   " raises ValueError
  - **Estimated time**: 20 mins

- [X] T-003 [P] Write unit tests for Task dataclass in tests/test_todo_app.py
  - **From**: plan.md lines 723-748 (TestTaskDataclass section)
  - **Description**: Create TestTaskDataclass class with 4 test methods covering creation, trimming, and validation
  - **Preconditions**: Task dataclass exists (T-002)
  - **Artifacts**: tests/test_todo_app.py (~30 lines)
  - **Implementation**: Implement test_task_creation_with_title, test_task_title_trimming, test_task_empty_title_raises_error, test_task_whitespace_only_title_raises_error
  - **Test Criteria**:
    - ✓ All 4 tests written and FAIL before T-002 implementation (RED phase)
    - ✓ All 4 tests PASS after T-002 implementation (GREEN phase)
  - **Estimated time**: 25 mins

---

## Phase 2: Core CRUD Functions

**Purpose**: Business logic layer (no UI yet)

### User Story 1: Add Task

- [X] T-004 [US1] Implement add_task() function in src/todo_app.py
  - **From**: plan.md lines 213-246 (add_task section), spec.md FR-003, FR-004, FR-007
  - **Description**: Create add_task(title, description="") that validates via Task dataclass, appends to global TASKS list, and returns the new Task
  - **Preconditions**: Task dataclass and global TASKS list exist (T-002)
  - **Artifacts**: src/todo_app.py (~5 lines)
  - **Implementation**:
    ```python
    # Global storage
    TASKS: list[Task] = []

    def add_task(title: str, description: str = "") -> Task:
        """Create and store a new task."""
        task = Task(title=title, description=description)
        TASKS.append(task)
        return task
    ```
  - **Test Criteria**:
    - ✓ Creates task with title only, adds to TASKS, returns Task
    - ✓ Creates task with title + description
    - ✓ Trims title whitespace before validation
    - ✓ Raises ValueError for empty title
    - ✓ Raises ValueError for whitespace-only title
    - ✓ Assigns unique UUID
    - ✓ Sets created_at timestamp
    - ✓ Sets completed to False
  - **Estimated time**: 15 mins

- [X] T-005 [P] Write unit tests for add_task() in tests/test_todo_app.py
  - **From**: plan.md lines 751-777 (TestAddTask section)
  - **Description**: Create TestAddTask class with setUp() to clear TASKS and 4 test methods
  - **Preconditions**: add_task() exists (T-004)
  - **Artifacts**: tests/test_todo_app.py (~30 lines)
  - **Implementation**: Implement test_add_task_with_title_only, test_add_task_with_title_and_description, test_add_task_trims_title, test_add_task_empty_title_raises_error
  - **Test Criteria**:
    - ✓ setUp() clears global TASKS before each test
    - ✓ All tests written and pass
  - **Estimated time**: 25 mins

### User Story 2: View Tasks

- [X] T-006 [P] [US2] Implement view_tasks() function in src/todo_app.py
  - **From**: plan.md lines 304-321 (view_tasks section), spec.md FR-008, FR-009
  - **Description**: Create view_tasks() that returns a copy of the global TASKS list to prevent external modification
  - **Preconditions**: Global TASKS exists (T-004)
  - **Artifacts**: src/todo_app.py (~3 lines)
  - **Implementation**:
    ```python
    def view_tasks() -> list[Task]:
        """Retrieve all tasks in creation order."""
        return TASKS.copy()
    ```
  - **Test Criteria**:
    - ✓ Returns empty list when no tasks exist
    - ✓ Returns all tasks in FIFO order
    - ✓ Does not modify task data
    - ✓ Returns copy (modifications don't affect TASKS)
  - **Estimated time**: 10 mins

- [X] T-007 [P] Write unit tests for view_tasks() in tests/test_todo_app.py
  - **From**: plan.md lines 808-826 (TestViewTasks section)
  - **Description**: Create TestViewTasks class with 2 test methods
  - **Preconditions**: view_tasks() and add_task() exist (T-004, T-006)
  - **Artifacts**: tests/test_todo_app.py (~20 lines)
  - **Implementation**: Implement test_view_empty_list, test_view_multiple_tasks
  - **Test Criteria**:
    - ✓ Tests verify empty list and creation order
  - **Estimated time**: 15 mins

### User Story 4: Update Task (depends on find)

- [X] T-008 [US4] Implement find_task_by_id() function in src/todo_app.py
  - **From**: plan.md lines 248-302 (find_task_by_id section), spec.md FR-014, FR-015
  - **Description**: Create find_task_by_id(task_id_input) supporting both full UUID (36 chars) and 8-char hex prefix with validation and ambiguity detection
  - **Preconditions**: Global TASKS exists (T-004)
  - **Artifacts**: src/todo_app.py (~35 lines)
  - **Implementation**: Validate format (36 chars = UUID, 8 chars = hex prefix), search TASKS, raise ValueError for invalid format/not found/ambiguous
  - **Test Criteria**:
    - ✓ Finds by full UUID (36 chars with hyphens)
    - ✓ Finds by 8-char prefix
    - ✓ Raises ValueError for invalid format
    - ✓ Raises ValueError for non-existent task
    - ✓ Raises ValueError for ambiguous prefix (multiple matches)
    - ✓ Case-insensitive hex matching
  - **Estimated time**: 40 mins

- [X] T-009 [P] Write unit tests for find_task_by_id() in tests/test_todo_app.py
  - **From**: plan.md lines 779-806 (TestFindTaskById section)
  - **Description**: Create TestFindTaskById class with setUp creating 2 tasks and 4 test methods
  - **Preconditions**: find_task_by_id() exists (T-008)
  - **Artifacts**: tests/test_todo_app.py (~35 lines)
  - **Implementation**: Implement test_find_by_full_uuid, test_find_by_8char_prefix, test_find_invalid_format_raises_error, test_find_nonexistent_raises_error
  - **Test Criteria**:
    - ✓ All 4 test scenarios pass
  - **Estimated time**: 30 mins

- [X] T-010 [US4] Implement update_task() function in src/todo_app.py
  - **From**: plan.md lines 324-366 (update_task section), spec.md FR-011, FR-012
  - **Description**: Create update_task(task_id_input, new_title, new_description) that allows partial updates with None to keep existing values
  - **Preconditions**: find_task_by_id() exists (T-008)
  - **Artifacts**: src/todo_app.py (~15 lines)
  - **Implementation**: Use find_task_by_id(), update only non-None fields with title trimming/validation
  - **Test Criteria**:
    - ✓ Updates title only when new_title provided, new_description is None
    - ✓ Updates description only when new_description provided, new_title is None
    - ✓ Updates both when both provided
    - ✓ No-op when both None
    - ✓ Raises ValueError if new_title empty after trim
    - ✓ Does not modify created_at or id
  - **Estimated time**: 20 mins

- [X] T-011 [P] Write unit tests for update_task() in tests/test_todo_app.py
  - **From**: plan.md lines 828-859 (TestUpdateTask section)
  - **Description**: Create TestUpdateTask class with setUp creating 1 task and 4 test methods
  - **Preconditions**: update_task() exists (T-010)
  - **Artifacts**: tests/test_todo_app.py (~40 lines)
  - **Implementation**: Implement test_update_title_only, test_update_description_only, test_update_both_fields, test_update_empty_title_raises_error
  - **Test Criteria**:
    - ✓ All partial update scenarios tested
  - **Estimated time**: 30 mins

### User Story 5: Delete Task

- [X] T-012 [P] [US5] Implement delete_task() function in src/todo_app.py
  - **From**: plan.md lines 369-395 (delete_task section), spec.md FR-013, FR-014
  - **Description**: Create delete_task(task_id_input) that finds and removes task from TASKS list
  - **Preconditions**: find_task_by_id() exists (T-008)
  - **Artifacts**: src/todo_app.py (~5 lines)
  - **Implementation**:
    ```python
    def delete_task(task_id_input: str) -> Task:
        """Delete a task by ID and return the deleted task."""
        task = find_task_by_id(task_id_input)
        TASKS.remove(task)
        return task
    ```
  - **Test Criteria**:
    - ✓ Removes task from TASKS
    - ✓ Returns deleted task object
    - ✓ Raises ValueError if not found
    - ✓ Does not affect other tasks
    - ✓ Decreases len(TASKS) by 1
  - **Estimated time**: 10 mins

- [X] T-013 [P] Write unit tests for delete_task() in tests/test_todo_app.py
  - **From**: plan.md lines 861-878 (TestDeleteTask section)
  - **Description**: Create TestDeleteTask class with 2 test methods
  - **Preconditions**: delete_task() exists (T-012)
  - **Artifacts**: tests/test_todo_app.py (~20 lines)
  - **Implementation**: Implement test_delete_existing_task, test_delete_nonexistent_raises_error
  - **Test Criteria**:
    - ✓ Deletion and error scenarios tested
  - **Estimated time**: 15 mins

### User Story 3: Toggle Complete

- [X] T-014 [P] [US3] Implement toggle_complete() function in src/todo_app.py
  - **From**: plan.md lines 397-424 (toggle_complete section), spec.md FR-010
  - **Description**: Create toggle_complete(task_id_input) that flips the completed boolean
  - **Preconditions**: find_task_by_id() exists (T-008)
  - **Artifacts**: src/todo_app.py (~5 lines)
  - **Implementation**:
    ```python
    def toggle_complete(task_id_input: str) -> Task:
        """Toggle a task's completion status."""
        task = find_task_by_id(task_id_input)
        task.completed = not task.completed
        return task
    ```
  - **Test Criteria**:
    - ✓ Changes False to True
    - ✓ Changes True to False
    - ✓ Returns updated task
    - ✓ Raises ValueError if not found
    - ✓ Does not modify other fields
  - **Estimated time**: 10 mins

- [X] T-015 [P] Write unit tests for toggle_complete() in tests/test_todo_app.py
  - **From**: plan.md lines 880-899 (TestToggleComplete section)
  - **Description**: Create TestToggleComplete class with 2 test methods
  - **Preconditions**: toggle_complete() exists (T-014)
  - **Artifacts**: tests/test_todo_app.py (~20 lines)
  - **Implementation**: Implement test_toggle_incomplete_to_complete, test_toggle_complete_to_incomplete
  - **Test Criteria**:
    - ✓ Both toggle directions tested
  - **Estimated time**: 15 mins

---

## Phase 3: UI Layer

**Purpose**: User-facing handlers and display functions

### Display Functions

- [X] T-016 [P] [US2] Implement display_menu() function in src/todo_app.py
  - **From**: plan.md lines 430-455 (display_menu section), spec.md FR-001
  - **Description**: Create display_menu() that prints the 6-option main menu
  - **Preconditions**: None (pure display)
  - **Artifacts**: src/todo_app.py (~10 lines)
  - **Implementation**: Print formatted menu with borders and numbered options 1-6
  - **Test Criteria**:
    - ✓ Displays correct menu text
    - ✓ Shows all 6 options
    - ✓ Properly formatted with borders
  - **Estimated time**: 10 mins

- [X] T-017 [P] [US2] Implement display_tasks() function in src/todo_app.py
  - **From**: plan.md lines 457-499 (display_tasks section), spec.md FR-008, FR-009
  - **Description**: Create display_tasks(tasks) that shows formatted table with ID (8 chars), Title, Description (50 chars max), Status ([✓]/[ ]), Created (YYYY-MM-DD HH:MM)
  - **Preconditions**: Task dataclass exists (T-002)
  - **Artifacts**: src/todo_app.py (~25 lines)
  - **Implementation**: Handle empty list message, format table with columns, truncate description to 50 chars + "...", format datetime
  - **Test Criteria**:
    - ✓ Empty list shows "No tasks found. Your todo list is empty."
    - ✓ Non-empty shows table with headers
    - ✓ ID truncated to 8 chars
    - ✓ Description truncated to 50 chars + "..." if longer
    - ✓ Status shows [✓] or [ ]
    - ✓ Created shows YYYY-MM-DD HH:MM format
  - **Estimated time**: 30 mins

### Input Handlers

- [X] T-018 [P] [US1] Implement handle_add() function in src/todo_app.py
  - **From**: plan.md lines 501-521 (handle_add section), spec.md US1
  - **Description**: Create handle_add() that prompts for title and description, calls add_task(), displays success message
  - **Preconditions**: add_task() exists (T-004)
  - **Artifacts**: src/todo_app.py (~8 lines)
  - **Implementation**: Prompt "Enter task title: ", prompt "Enter task description (optional, press Enter to skip): ", call add_task(), print success with UUID
  - **Test Criteria**:
    - ✓ Prompts user correctly
    - ✓ Calls add_task() with inputs
    - ✓ Displays "Success: Task added with ID [UUID]"
    - ✓ Errors caught by main loop (not here)
  - **Estimated time**: 15 mins

- [X] T-019 [P] [US2] Implement handle_view() function in src/todo_app.py
  - **From**: plan.md lines 523-534 (handle_view section), spec.md US2
  - **Description**: Create handle_view() that calls view_tasks() and display_tasks()
  - **Preconditions**: view_tasks() and display_tasks() exist (T-006, T-017)
  - **Artifacts**: src/todo_app.py (~4 lines)
  - **Implementation**:
    ```python
    def handle_view() -> None:
        """Handle the View Tasks menu option."""
        tasks = view_tasks()
        display_tasks(tasks)
    ```
  - **Test Criteria**:
    - ✓ Retrieves tasks
    - ✓ Displays tasks
  - **Estimated time**: 5 mins

- [X] T-020 [P] [US4] Implement handle_update() function in src/todo_app.py
  - **From**: plan.md lines 536-566 (handle_update section), spec.md US4, FR-011
  - **Description**: Create handle_update() with sequential prompts for ID, new title (Enter to keep), new description (Enter to keep)
  - **Preconditions**: update_task() exists (T-010)
  - **Artifacts**: src/todo_app.py (~12 lines)
  - **Implementation**: Prompt for ID, prompt for new title with Enter hint, prompt for new description with Enter hint, convert empty strings to None, call update_task(), display success
  - **Test Criteria**:
    - ✓ Prompts sequentially
    - ✓ Empty input (Enter) passes None to update_task
    - ✓ Non-empty input passes value
    - ✓ Displays "Success: Task [8-char ID] updated"
  - **Estimated time**: 20 mins

- [X] T-021 [P] [US5] Implement handle_delete() function in src/todo_app.py
  - **From**: plan.md lines 568-585 (handle_delete section), spec.md US5
  - **Description**: Create handle_delete() that prompts for ID, calls delete_task(), displays success
  - **Preconditions**: delete_task() exists (T-012)
  - **Artifacts**: src/todo_app.py (~6 lines)
  - **Implementation**: Prompt "Enter task ID to delete: ", call delete_task(), display "Success: Task [8-char ID] deleted"
  - **Test Criteria**:
    - ✓ Prompts for ID
    - ✓ Calls delete_task()
    - ✓ Displays success with ID
  - **Estimated time**: 10 mins

- [X] T-022 [P] [US3] Implement handle_toggle() function in src/todo_app.py
  - **From**: plan.md lines 587-605 (handle_toggle section), spec.md US3
  - **Description**: Create handle_toggle() that prompts for ID, calls toggle_complete(), displays success with status
  - **Preconditions**: toggle_complete() exists (T-014)
  - **Artifacts**: src/todo_app.py (~8 lines)
  - **Implementation**: Prompt "Enter task ID: ", call toggle_complete(), determine status word (complete/incomplete), display "Success: Task [8-char ID] marked as [status]"
  - **Test Criteria**:
    - ✓ Prompts for ID
    - ✓ Calls toggle_complete()
    - ✓ Displays correct status in message
  - **Estimated time**: 15 mins

---

## Phase 4: Main Loop & Integration

**Purpose**: Application entry point and menu routing

- [X] T-023 Implement main() function in src/todo_app.py
  - **From**: plan.md lines 612-667 (main function section), spec.md FR-001, FR-002, FR-016, FR-018, FR-019
  - **Description**: Create main() loop with welcome message, menu display, input handling, routing to handlers, error catching, and exit
  - **Preconditions**: All handlers and display_menu exist (T-016 through T-022)
  - **Artifacts**: src/todo_app.py (~35 lines)
  - **Implementation**:
    - Print welcome and data warning
    - While loop until choice == "6"
    - Display menu, get input
    - Route 1-6 to handlers
    - Catch ValueError and generic exceptions
    - Display error messages
    - Exit with goodbye message
  - **Test Criteria**:
    - ✓ Displays welcome message
    - ✓ Loops until Exit (6)
    - ✓ Routes to correct handler for each choice
    - ✓ Invalid choice shows "Error: Invalid choice. Please enter a number between 1 and 6."
    - ✓ ValueError from core functions caught and displayed
    - ✓ Exit displays "Goodbye! Your tasks have been discarded."
    - ✓ Exits with code 0
  - **Estimated time**: 40 mins

- [X] T-024 Add if __name__ == "__main__": main() entry point in src/todo_app.py
  - **From**: plan.md lines 665-667
  - **Description**: Add standard Python entry point at bottom of file
  - **Preconditions**: main() exists (T-023)
  - **Artifacts**: src/todo_app.py (~3 lines)
  - **Implementation**:
    ```python
    if __name__ == "__main__":
        main()
    ```
  - **Test Criteria**:
    - ✓ File runs with python src/todo_app.py
  - **Estimated time**: 2 mins

---

## Phase 5: Integration Testing & Documentation

**Purpose**: End-to-end validation and user documentation

- [X] T-025 Write integration test for full CRUD workflow in tests/test_todo_app.py
  - **From**: plan.md lines 901-930 (TestIntegrationWorkflow section)
  - **Description**: Create TestIntegrationWorkflow class with test_full_crud_cycle covering create → read → update → toggle → delete sequence
  - **Preconditions**: All core functions exist (T-004 through T-014)
  - **Artifacts**: tests/test_todo_app.py (~30 lines)
  - **Implementation**: Single test method executing add_task → view_tasks → update_task → toggle_complete → delete_task with assertions at each step
  - **Test Criteria**:
    - ✓ Full lifecycle tested in one workflow
    - ✓ All operations succeed
    - ✓ Final state is clean (empty TASKS)
  - **Estimated time**: 25 mins

- [X] T-026 Run all tests and verify 80%+ coverage
  - **From**: plan.md lines 936-941 (Coverage Goals section), constitution.md Principle III
  - **Description**: Execute full test suite with unittest and verify all tests pass
  - **Preconditions**: All tests written (T-003, T-005, T-007, T-009, T-011, T-013, T-015, T-025)
  - **Artifacts**: None (validation only)
  - **Implementation**: Run `python -m unittest discover tests/` and verify exit code 0
  - **Test Criteria**:
    - ✓ All unit tests pass
    - ✓ Integration test passes
    - ✓ No test failures or errors
    - ✓ Coverage meets 80%+ threshold (manual check or coverage.py)
  - **Estimated time**: 15 mins

- [X] T-027 [P] Create README.md with setup and usage instructions
  - **From**: plan.md line 1039 (README.md section), spec.md Assumptions 10
  - **Description**: Write user-facing README with Python/UV requirements, setup steps, running instructions, feature overview, and data warning
  - **Preconditions**: Application complete (T-024)
  - **Artifacts**: README.md (~50 lines)
  - **Implementation**:
    - ## Requirements: Python 3.13+, UV
    - ## Setup: `uv venv`, `source .venv/bin/activate` (or Windows equivalent)
    - ## Usage: `python src/todo_app.py`
    - ## Features: List 5 CRUD operations
    - ## Warning: Data lost on exit
    - ## Testing: How to run tests
  - **Test Criteria**:
    - ✓ Setup instructions are clear and complete
    - ✓ Usage examples included
    - ✓ Data persistence warning prominent
  - **Estimated time**: 30 mins

- [X] T-028 Manual testing checklist validation
  - **From**: plan.md lines 943-961 (Manual Testing Checklist)
  - **Description**: Manually execute all 16 test scenarios from the checklist to validate end-to-end functionality
  - **Preconditions**: Application complete (T-024)
  - **Artifacts**: None (validation only)
  - **Implementation**: Follow checklist: menu display, add variations, view variations, update variations, delete variations, toggle variations, invalid inputs, exit
  - **Test Criteria**:
    - ✓ All 16 scenarios pass
    - ✓ No crashes or unexpected behavior
    - ✓ All error messages match spec requirements
  - **Estimated time**: 45 mins

---

## Dependencies & Execution Order

### Critical Path (Sequential):
1. **T-001** (Project structure) → **T-002** (Task dataclass) → **T-004** (add_task) → **T-008** (find_task_by_id) → **T-010/T-012/T-014** (update/delete/toggle) → **T-016/T-017** (display functions) → **T-018-T-022** (handlers) → **T-023** (main) → **T-024** (entry point)

### Test Path (Parallel with implementation):
- **T-003** (Task tests) after T-002
- **T-005** (add_task tests) after T-004
- **T-007** (view_tasks tests) after T-006
- **T-009** (find_task_by_id tests) after T-008
- **T-011** (update_task tests) after T-010
- **T-013** (delete_task tests) after T-012
- **T-015** (toggle_complete tests) after T-014
- **T-025** (integration test) after all core functions complete

### Parallel Opportunities:
- Once T-004 (add_task) complete: **T-006** (view_tasks) can run in parallel
- Once T-008 (find_task_by_id) complete: **T-010, T-012, T-014** can run in parallel
- Once T-017 (display_tasks) complete: **T-018-T-022** (all handlers) can run in parallel
- **T-027** (README) can run in parallel with T-023-T-028

### TDD Workflow for Each Function:
1. Write test (RED) → Verify test fails
2. Implement function (GREEN) → Verify test passes
3. Refactor if needed → Keep tests green

---

## Implementation Strategy

### Recommended Order (Single Developer):
1. **Phase 1**: T-001, T-002, T-003 (Setup + Task dataclass + tests)
2. **Phase 2 - US1**: T-004, T-005 (Add task function + tests) → **Checkpoint: Can create tasks**
3. **Phase 2 - US2**: T-006, T-007 (View tasks function + tests) → **Checkpoint: Can view tasks**
4. **Phase 2 - Find**: T-008, T-009 (Find function + tests) → **Checkpoint: Can find tasks**
5. **Phase 2 - US4**: T-010, T-011 (Update function + tests) → **Checkpoint: Can update**
6. **Phase 2 - US5**: T-012, T-013 (Delete function + tests) → **Checkpoint: Can delete**
7. **Phase 2 - US3**: T-014, T-015 (Toggle function + tests) → **Checkpoint: All CRUD complete**
8. **Phase 3 - Display**: T-016, T-017 (Menu + task display)
9. **Phase 3 - Handlers**: T-018 (add handler) → T-019 (view handler) → T-020 (update handler) → T-021 (delete handler) → T-022 (toggle handler)
10. **Phase 4**: T-023, T-024 (Main loop + entry point) → **Checkpoint: Application runnable**
11. **Phase 5**: T-025 (integration test), T-026 (coverage check), T-027 (README), T-028 (manual testing)

### Parallel Team Strategy (2-3 Developers):
- **Developer A**: T-001 → T-002/T-003 → T-004/T-005 → T-018 → T-023
- **Developer B**: (Wait for T-004) → T-006/T-007 → T-008/T-009 → T-016/T-017 → T-019
- **Developer C**: (Wait for T-008) → T-010/T-011 → T-012/T-013 → T-014/T-015 → T-020/T-021/T-022
- **All**: T-024, T-025, T-026, T-027, T-028 (final integration)

---

## Summary

- **Total Tasks**: 28 atomic tasks
- **Estimated Total Time**: ~8-10 hours (single developer, including TDD cycles)
- **User Stories Covered**: All 5 (US1: Add, US2: View, US3: Toggle, US4: Update, US5: Delete)
- **Functional Requirements Covered**: All 20 (FR-001 to FR-020)
- **Constitution Compliance**:
  - ✓ TDD workflow enforced (test before implementation)
  - ✓ Type safety (all functions typed)
  - ✓ Clean code (≤20 lines per function)
  - ✓ 80%+ coverage target
  - ✓ Spec-driven (all tasks trace to spec/plan)
- **Deliverables**: src/todo_app.py (~400-500 lines), tests/test_todo_app.py (~300-400 lines), README.md

**Next**: Begin with T-001 (project structure) and follow TDD workflow (RED → GREEN → REFACTOR) for each function.

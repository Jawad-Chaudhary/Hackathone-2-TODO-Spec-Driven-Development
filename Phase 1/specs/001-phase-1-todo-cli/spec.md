# Feature Specification: Phase 1 - Python Console Todo App

**Feature Branch**: `001-phase-1-todo-cli`
**Created**: 2025-12-30
**Status**: Draft
**Input**: User description: "Create a detailed specification for Phase 1: Python Console Todo App with CRUD operations (Add, View, Update, Delete, Mark Complete) using in-memory storage, CLI interface, and strict TDD workflow."

## Clarifications

### Session 2025-12-30

- Q: Should users enter the full UUID (36 chars) or truncated 8-character version for task operations? → A: Allow both full UUID and 8-character prefix (match what's displayed in view)
- Q: When updating a task, what is the user flow for partial updates? → A: Prompt for both fields sequentially; allow pressing Enter to keep existing value
- Q: Should titles with leading/trailing whitespace be trimmed, rejected, or stored as-is? → A: Automatically trim leading/trailing whitespace before validation and storage
- Q: Should the task description be displayed in the "View Tasks" list? → A: Show description in list view (truncated if too long, e.g., 50 chars max)
- Q: What format should be used for displaying the creation timestamp? → A: Human-readable format (YYYY-MM-DD HH:MM)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add New Task (Priority: P1)

As a user, I want to add a new task with a title and optional description, so that I can track things I need to do.

**Why this priority**: This is the foundational capability - without creating tasks, the application has no purpose. This must work first.

**Independent Test**: Can be fully tested by launching the app, selecting "Add Task", entering a title, and verifying the task appears in the list with a unique ID and "incomplete" status. Delivers immediate value as users can start capturing their todos.

**Acceptance Scenarios**:

1. **Given** the main menu is displayed, **When** I select "Add Task" and enter only a title "Buy groceries", **Then** a new task is created with a unique ID, the title "Buy groceries", an empty description, status "incomplete", and the current timestamp
2. **Given** the main menu is displayed, **When** I select "Add Task" and enter title "Finish report" with description "Complete Q4 analysis", **Then** a new task is created with both title and description populated
3. **Given** the "Add Task" prompt is displayed, **When** I enter an empty title, **Then** the system displays an error "Error: Title cannot be empty" and prompts me to enter a valid title
4. **Given** the "Add Task" prompt is displayed, **When** I enter a title with leading/trailing whitespace "  Buy milk  ", **Then** the system automatically trims it and creates a task with title "Buy milk" (no surrounding spaces)
5. **Given** the "Add Task" prompt is displayed, **When** I enter only whitespace "   ", **Then** the system trims it to empty string and displays "Error: Title cannot be empty"
6. **Given** I have successfully added a task, **When** the operation completes, **Then** the system displays "Success: Task added with ID [UUID]" and returns to the main menu

---

### User Story 2 - View All Tasks (Priority: P1)

As a user, I want to view all my tasks in a clear list format, so that I can see what I need to do and track my progress.

**Why this priority**: Equally critical as adding tasks - users need to see what they've created. Together with "Add Task", this forms the minimal viable product.

**Independent Test**: Can be tested independently by pre-populating the in-memory storage with test tasks, then selecting "View Tasks" and verifying the display format shows IDs, titles, descriptions, completion status, and timestamps correctly.

**Acceptance Scenarios**:

1. **Given** there are no tasks in the system, **When** I select "View Tasks", **Then** the system displays "No tasks found. Your todo list is empty."
2. **Given** there are 3 tasks (2 incomplete, 1 complete), **When** I select "View Tasks", **Then** the system displays all 3 tasks with columns for ID (first 8 chars), Title, Description (truncated to 50 chars if longer), Status ([✓] or [ ]), and Created Date in a formatted table
3. **Given** a task exists with description longer than 50 characters, **When** I view the task list, **Then** the description is truncated to 50 characters followed by "..." (e.g., "This is a very long description that exceeds fi...")
4. **Given** tasks exist with varying title and description lengths, **When** I view the task list, **Then** the display format remains consistent and readable with proper alignment
5. **Given** I have viewed the task list, **When** the display completes, **Then** the system returns to the main menu

---

### User Story 3 - Mark Task Complete/Incomplete (Priority: P2)

As a user, I want to toggle the completion status of a task, so that I can track which tasks I've finished.

**Why this priority**: Core todo functionality, but depends on having tasks already created and viewable. Provides immediate satisfaction and progress tracking.

**Independent Test**: Can be tested by creating a task (or using pre-populated data), marking it complete, viewing the list to verify the status indicator changed, then toggling it back to incomplete.

**Acceptance Scenarios**:

1. **Given** an incomplete task exists with ID "abc123", **When** I select "Mark Complete" and enter ID "abc123", **Then** the task status changes to complete and displays "Success: Task abc123 marked as complete"
2. **Given** a complete task exists with ID "def456", **When** I select "Mark Complete" and enter ID "def456", **Then** the task status toggles to incomplete and displays "Success: Task def456 marked as incomplete"
3. **Given** the "Mark Complete" prompt is displayed, **When** I enter a non-existent ID "xyz999", **Then** the system displays "Error: Task not found with ID xyz999" and returns to the main menu
4. **Given** the "Mark Complete" prompt is displayed, **When** I enter an invalid ID format "not-a-uuid", **Then** the system displays "Error: Invalid task ID format" and returns to the main menu

---

### User Story 4 - Update Task Details (Priority: P3)

As a user, I want to update the title and/or description of an existing task, so that I can correct mistakes or add more information as my understanding evolves.

**Why this priority**: Important for usability but not critical for MVP. Users can work around this by deleting and recreating tasks if needed.

**Independent Test**: Can be tested by creating a task with initial values, then updating either title only, description only, or both, and verifying the changes are reflected in the task list.

**Acceptance Scenarios**:

1. **Given** a task exists with ID "abc123", title "Old Title", and description "Old Description", **When** I select "Update Task", enter ID "abc123", provide new title "New Title", and press Enter to skip description update, **Then** the task title updates to "New Title" while description remains "Old Description"
2. **Given** a task exists with ID "def456", title "Current Title", and description "Old Description", **When** I update by pressing Enter to skip title update and providing new description "New Description", **Then** the description updates to "New Description" while title remains "Current Title"
3. **Given** a task exists, **When** I provide both new title and new description at their respective prompts, **Then** both fields are updated and system displays "Success: Task [ID] updated"
4. **Given** the "Update Task" prompt is displayed, **When** I enter a non-existent task ID, **Then** the system displays "Error: Task not found" and returns to the main menu
5. **Given** the update prompt asks for a new title, **When** I provide an empty string (not just pressing Enter to skip), **Then** the system displays "Error: Title cannot be empty" and does not update the task
6. **Given** I am updating a task, **When** I press Enter at both the title and description prompts (skipping both), **Then** no changes are made and system displays "Success: Task [ID] updated" (or "No changes made")

---

### User Story 5 - Delete Task (Priority: P3)

As a user, I want to delete a task I no longer need, so that my task list stays focused and uncluttered.

**Why this priority**: Nice-to-have for cleanup, but lowest priority since incomplete tasks don't negatively impact the core experience. Can be deferred if time is limited.

**Independent Test**: Can be tested by creating a task, deleting it by ID, then verifying it no longer appears in the task list.

**Acceptance Scenarios**:

1. **Given** a task exists with ID "abc123", **When** I select "Delete Task" and enter ID "abc123", **Then** the task is removed from the system and displays "Success: Task abc123 deleted"
2. **Given** the "Delete Task" prompt is displayed, **When** I enter a non-existent task ID "xyz999", **Then** the system displays "Error: Task not found with ID xyz999" and no tasks are deleted
3. **Given** I have deleted a task, **When** I view the task list, **Then** the deleted task does not appear
4. **Given** the task list has 5 tasks, **When** I delete one task, **Then** the remaining 4 tasks are still accessible and unchanged

---

### Edge Cases

- **Empty title validation**: What happens when a user tries to create or update a task with an empty or whitespace-only title? System must automatically trim leading/trailing whitespace first, then validate. If the trimmed result is empty, reject with "Error: Title cannot be empty".
- **Invalid UUID input**: How does the system handle non-UUID input for task IDs (e.g., "1", "task", random text)? System must validate that input is either a full UUID (36 chars with hyphens) or 8-character hexadecimal prefix, and reject invalid formats with "Error: Invalid task ID format".
- **Non-existent task operations**: What happens when a user tries to update, delete, or toggle completion for a task ID that doesn't exist? System must check existence before operations and inform user clearly.
- **Empty task list operations**: How does the system handle viewing, updating, deleting when no tasks exist? View should show friendly "empty list" message; operations should fail gracefully.
- **Large task lists**: What happens when the user creates 100+ tasks? Display should remain functional (consider pagination or scrolling in implementation, but this is out of scope for Phase 1 spec).
- **Special characters in input**: How does the system handle titles/descriptions with special characters (quotes, newlines, emojis)? System should accept and display them correctly.
- **Missing description display**: How should the task list display tasks with no description? Show empty/blank in the description column to maintain table alignment.
- **Concurrent operations** (out of scope): Single-user CLI means no concurrency concerns for Phase 1.
- **Data persistence across sessions** (out of scope): Explicitly excluded - data lost on exit is expected behavior.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a main menu with 6 numbered options: (1) Add Task, (2) View Tasks, (3) Update Task, (4) Delete Task, (5) Mark Complete/Incomplete, (6) Exit
- **FR-002**: System MUST accept menu selections via numeric input (1-6) and reject invalid selections with clear error messages
- **FR-003**: System MUST generate unique task identifiers using UUID format for each new task
- **FR-004**: System MUST automatically trim leading and trailing whitespace from titles before validation. After trimming, system MUST require a non-empty title when creating a task and reject empty or whitespace-only titles with error "Error: Title cannot be empty"
- **FR-005**: System MUST accept optional descriptions for tasks (can be empty)
- **FR-006**: System MUST automatically capture the task creation timestamp using the current system date/time
- **FR-007**: System MUST initialize all new tasks with completion status set to "incomplete" (false)
- **FR-008**: System MUST display all tasks in a formatted list showing: truncated task ID (first 8 characters), title, description (truncated to 50 characters with "..." if longer, or empty if no description), completion status indicator ([✓] for complete, [ ] for incomplete), and creation date/time in format "YYYY-MM-DD HH:MM"
- **FR-009**: System MUST display a user-friendly message when the task list is empty ("No tasks found. Your todo list is empty.")
- **FR-010**: System MUST allow users to toggle task completion status by providing the task ID
- **FR-011**: System MUST allow users to update task title and/or description by prompting for task ID, then sequentially prompting for new title and new description. Users can press Enter (empty input) to skip updating a field and keep its existing value
- **FR-012**: System MUST preserve unchanged fields when updating a task. Empty input (pressing Enter) means "keep existing value"; explicit empty string input for title must be rejected as invalid
- **FR-013**: System MUST allow users to delete tasks by providing the task ID
- **FR-014**: System MUST validate task ID existence before performing update, delete, or toggle operations
- **FR-015**: System MUST accept task IDs in two formats: full UUID (36 characters with hyphens) or 8-character prefix (matching the truncated display). System MUST validate input matches one of these formats and reject invalid formats with error message "Error: Invalid task ID format"
- **FR-016**: System MUST return to the main menu after each operation completes (success or error)
- **FR-017**: System MUST display clear success messages after successful operations: "Success: Task added with ID [UUID]", "Success: Task [ID] updated", "Success: Task [ID] deleted", "Success: Task [ID] marked as complete/incomplete"
- **FR-018**: System MUST display clear error messages for all error conditions (invalid input, task not found, empty title, etc.)
- **FR-019**: System MUST exit cleanly when user selects option 6 (Exit) without errors or warnings
- **FR-020**: System MUST store all tasks in memory during program execution and accept that data is lost when the program exits

### Key Entities

- **Task**: Represents a single todo item. Key attributes:
  - **ID**: Unique identifier (UUID) automatically generated on creation, immutable
  - **Title**: Short descriptive text, required (after trimming whitespace), user-provided, modifiable
  - **Description**: Detailed text, optional, user-provided, modifiable
  - **Completed**: Boolean status indicating whether task is done, defaults to false, toggleable
  - **Created At**: Timestamp of task creation, automatically captured on creation, immutable, displayed in format "YYYY-MM-DD HH:MM"

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add a new task in under 15 seconds (from menu selection to confirmation message)
- **SC-002**: Users can view their complete task list in under 3 seconds regardless of list size (up to 100 tasks)
- **SC-003**: 100% of valid task operations (add, view, update, delete, toggle) complete successfully with clear confirmation messages
- **SC-004**: 100% of invalid operations (empty title, non-existent ID, invalid ID format) are rejected with specific, actionable error messages
- **SC-005**: Task list display is readable and properly formatted for lists containing 1, 10, or 50 tasks
- **SC-006**: Users can complete a full CRUD cycle (create → view → update → view → delete → view) in under 2 minutes
- **SC-007**: Zero unhandled exceptions or crashes during normal operation and expected error scenarios
- **SC-008**: Application exits cleanly with exit code 0 when user selects "Exit" option
- **SC-009**: All task data persists correctly in memory throughout the program session (multiple operations without data loss)
- **SC-010**: 100% of functional requirements (FR-001 through FR-020) are testable and pass automated tests

## Assumptions

1. **Python Environment**: Users have Python 3.13+ installed and accessible via command line
2. **UV Package Manager**: Users have UV installed for environment management
3. **Single User Session**: Only one user operates the CLI at a time; no concurrency or multi-user concerns
4. **Terminal Capabilities**: User's terminal supports standard ASCII characters and basic formatting (newlines, spacing)
5. **English Language**: All UI text (menus, prompts, messages) is in English
6. **Reasonable Input Lengths**: Titles and descriptions are reasonable length (under 500 characters); no specific length limits enforced in Phase 1
7. **Standard Input Method**: Users interact via keyboard input only (no mouse, no GUI)
8. **UUID Uniqueness**: Python's uuid module provides sufficient uniqueness guarantees for task IDs in a single-user, single-session context
9. **Date/Time Accuracy**: System clock is accurate for timestamping task creation
10. **No Persistence Required**: Users understand and accept that closing the application loses all data (documented in README)
11. **No Search/Filter**: Users can manually scan the task list to find specific tasks; advanced search deferred to future phases
12. **No Task Ordering**: Tasks are displayed in creation order (first created appears first); custom sorting deferred to future phases

## Out of Scope

The following are explicitly excluded from Phase 1:

- **Persistence**: No file I/O, databases, or data storage across sessions
- **Authentication/Authorization**: No user accounts, passwords, or access control
- **Multi-user Support**: No concurrent users, no user sessions, no user-specific task lists
- **Web Interface**: Command-line only; no web UI, REST API, or HTTP server
- **External Dependencies**: No third-party libraries beyond Python standard library
- **Advanced Task Features**: No priorities, tags, categories, due dates, or reminders
- **Search and Filtering**: No keyword search, status filters, or date range queries
- **Task Relationships**: No subtasks, dependencies, or task hierarchies
- **Import/Export**: No CSV, JSON, or other file format support
- **Undo/Redo**: No operation history or rollback capability
- **Task Archiving**: No separate archive or completed task management
- **Internationalization**: English-only interface
- **Custom Configuration**: No user preferences, themes, or settings
- **Performance Optimization**: No caching, indexing, or optimization for large datasets (100+ tasks acceptable)
- **Audit Logging**: No operation history or change tracking
- **Data Validation Beyond Basic**: No email validation, URL validation, or complex business rules
- **Notifications**: No reminders, alerts, or push notifications
- **Collaboration**: No sharing, commenting, or assignment features

## Dependencies

- **Python 3.13+**: Required for language features and standard library
- **UV Package Manager**: Required for environment management (but not for installing dependencies)
- **Operating System**: Windows, macOS, or Linux with Python support
- **Terminal Emulator**: Any standard terminal/console application

## Constraints

- **In-memory Storage Only**: All task data stored in Python data structures (list/dict); lost on program exit
- **Single User**: No authentication, authorization, or multi-user considerations
- **Standard Library Only**: No external dependencies (no pip packages beyond Python standard library)
- **Command-line Interface**: Text-based menu system using argparse or input() functions
- **Test-Driven Development**: All features must be developed using Red-Green-Refactor TDD workflow
- **Code Quality**: Must follow constitution standards (type hints, docstrings, max 20-line functions, 80%+ coverage)
- **Spec-Driven**: All implementation must trace to requirements in this specification

## Open Questions

None - all critical decisions have been addressed with reasonable defaults documented in Assumptions section.

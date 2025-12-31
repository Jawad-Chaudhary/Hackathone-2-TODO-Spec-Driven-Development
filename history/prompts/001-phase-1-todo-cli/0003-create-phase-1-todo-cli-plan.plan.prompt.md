---
id: 0003
title: Create Phase 1 Todo CLI Plan
stage: plan
date: 2025-12-30
surface: agent
model: claude-sonnet-4-5
feature: 001-phase-1-todo-cli
branch: 001-phase-1-todo-cli
user: system
command: /sp.plan
labels: ["plan", "architecture", "design", "phase-1", "todo-cli"]
links:
  spec: specs/001-phase-1-todo-cli/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase-1-todo-cli/plan.md
tests:
  - none (planning document, tests defined in plan for implementation)
---

## Prompt

Create a concise technical plan for Phase 1: Python Console Todo App using constitution and specification.

Requirements: Architecture (components, data flow), Data Model (Task dataclass), Core Functions (6 functions with signatures, validation, errors), UI Functions (7 handlers), Main Loop (menu, routing, error handling), File Structure (single file), Error Handling Strategy, Testing Strategy, Implementation Notes.

For each function: typed signature, docstring, pseudocode/implementation, error handling, test criteria.

## Response snapshot

Created comprehensive technical plan (~1059 lines) for Phase 1 Python Console Todo App with complete architecture, design, and implementation specifications.

**Architecture**:
- 3-layer design: Main Loop → UI Handlers → Core Functions → Data Layer
- Single-file architecture (`src/todo_app.py`)
- Global in-memory storage (`TASKS: list[Task] = []`)
- Component diagram showing data flow

**Data Model**:
- `Task` dataclass with 5 fields: id (UUID), title (str), description (str), completed (bool), created_at (datetime)
- `__post_init__` validation for title trimming and empty check
- Complete field constraints and rationale

**Core Functions (6 functions, ~100 lines total)**:
1. `add_task(title, description)` - Create and store task
2. `find_task_by_id(task_id_input)` - Find by full UUID or 8-char prefix
3. `view_tasks()` - Retrieve all tasks in creation order
4. `update_task(id, new_title, new_description)` - Update fields (None = keep existing)
5. `delete_task(id)` - Remove task from list
6. `toggle_complete(id)` - Toggle completion status

**UI Functions (7 functions, ~150 lines total)**:
1. `display_menu()` - Show 6 numbered options
2. `display_tasks(tasks)` - Formatted table with truncation
3. `handle_add()` - Prompt for title + description
4. `handle_view()` - Call view_tasks + display
5. `handle_update()` - Sequential prompts (Enter = keep)
6. `handle_delete()` - Prompt for ID
7. `handle_toggle()` - Prompt for ID

**Main Loop**:
- Welcome message + data warning
- Menu loop until Exit (6)
- Try/except for ValueError (business logic) and generic errors
- Goodbye message + clean exit (code 0)

**Error Handling**:
- Business logic: `ValueError` with specific messages (FR-018 compliance)
- Invalid menu: Display error, re-prompt
- All error messages match spec requirements

**Testing Strategy**:
- 8 test classes covering all functions + integration workflow
- ~300-400 lines of test code
- Target: 80%+ coverage (Constitution requirement)
- Manual testing checklist with 16 scenarios

**Constitution Compliance**:
- ✅ Principle I: Simplicity First (single-file, in-memory list)
- ✅ Principle II: Stdlib Only (dataclasses, datetime, uuid, typing, unittest)
- ✅ Principle III: TDD (test strategy included, Red-Green-Refactor workflow)
- ✅ Principle IV: Type Safety (all functions typed, Task dataclass)
- ✅ Principle V: Clean Code (≤20 lines per function, docstrings, single global)
- ✅ Principle VI: Spec-Driven (maps all 20 FRs, traceable to spec)

**Key Design Decisions**:
- Single file: Simplicity for Phase 1 learning
- Global TASKS: Simplest storage, explicitly allowed
- `input()` menu: More natural than argparse subcommands
- UUID4: Guaranteed uniqueness without counter
- 8-char prefix: UX improvement (FR-015)

**File Organization**:
- `src/todo_app.py` (~400-500 lines)
- `tests/test_todo_app.py` (~300-400 lines)
- `README.md` (usage instructions)

## Outcome

- ✅ Impact: Complete architecture and design ready for implementation. All 20 FRs mapped to functions. All constitution principles validated.
- 🧪 Tests: Comprehensive test strategy defined with 8 test classes and manual checklist. Target 80%+ coverage.
- 📁 Files: Created specs/001-phase-1-todo-cli/plan.md (1059 lines, 6 core functions, 7 UI functions, main loop)
- 🔁 Next prompts: `/sp.tasks` to break down into atomic, testable tasks
- 🧠 Reflection: Plan strikes balance between detail (complete function signatures + pseudocode) and conciseness (single-file architecture). All functions designed to be ≤20 lines per Constitution. 8-char UUID prefix support adds UX while maintaining spec compliance.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan complete with all required components
- Graders run and results (PASS/FAIL): Constitution Check - 6/6 principles PASS. Spec traceability - 20/20 FRs mapped.
- Prompt variant (if applicable): N/A (baseline plan)
- Next experiment (smallest change to try): During implementation, validate that ≤20 line constraint is achievable for `find_task_by_id` (most complex function at ~27 lines in pseudocode - may need refactoring into helper)

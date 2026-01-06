---
id: 0004
title: Generate Phase 1 Todo CLI Tasks
stage: tasks
date: 2025-12-30
surface: agent
model: claude-sonnet-4-5
feature: 001-phase-1-todo-cli
branch: 001-phase-1-todo-cli
user: system
command: /sp.tasks
labels: ["tasks", "task-breakdown", "tdd", "atomic-tasks", "phase-1", "todo-cli"]
links:
  spec: specs/001-phase-1-todo-cli/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase-1-todo-cli/tasks.md
tests:
  - none (task breakdown document, tests defined within tasks for implementation)
---

## Prompt

# Phase 1 — Atomic Task Breakdown (short)

**From:** `specs/phase-1/specify.md`, `specs/phase-1/plan.md`

## Guidelines
* 15–60 min per task
* Independently testable with clear outputs
* Reference relevant spec/plan sections

## Tasks
* **T-001** — Create `Task` dataclass
* **T-002** — Implement `add_task()`
* **T-003** — Implement `view_tasks()` + `display_tasks()`
* **T-004** — Implement `find_task_by_id()`
* **T-005** — Implement `update_task()`
* **T-006** — Implement `delete_task()`
* **T-007** — Implement `toggle_complete()`
* **T-008** — Implement `display_menu()`
* **T-009** — Implement input handlers (`handle_add/update/delete/toggle`)
* **T-010** — Implement main loop + error handling
* **T-011** — Write README (setup & usage)
* **T-012** — Final testing & polish

## Task template (include for each)
* **Header:** Task ID, Title, From (spec/plan refs)
* **Details:** Description, Preconditions, Artifacts (files), Implementation (pseudo/code), Test criteria (✓ list), Estimated time (mins)

## Response snapshot

Generated comprehensive task breakdown document (28 atomic tasks, ~450 lines) for Phase 1 Python Console Todo App implementation following TDD workflow.

**Task Organization**:
- Reorganized user-provided 12-task structure into 28 detailed atomic tasks
- Organized into 5 phases: Setup & Data Model, Core CRUD Functions, UI Layer, Main Loop & Integration, Integration Testing & Documentation
- Each task includes: ID, user story label, description, spec/plan references, preconditions, artifacts, implementation code/pseudocode, test criteria checklist, time estimate

**Phase 1: Setup & Data Model (3 tasks)**:
- T-001: Create project structure (src/, tests/)
- T-002: [US1] Create Task dataclass with __post_init__ validation (20 mins)
- T-003: Write TestTaskDataclass unit tests (4 test methods, 25 mins)

**Phase 2: Core CRUD Functions (12 tasks)**:
Organized by user story with tests following each implementation:
- T-004/T-005: add_task() implementation + TestAddTask (15 + 25 mins)
- T-006/T-007: view_tasks() implementation + TestViewTasks (10 + 15 mins)
- T-008/T-009: find_task_by_id() implementation + TestFindTaskById (40 + 30 mins, most complex)
- T-010/T-011: update_task() implementation + TestUpdateTask (20 + 30 mins)
- T-012/T-013: delete_task() implementation + TestDeleteTask (10 + 15 mins)
- T-014/T-015: toggle_complete() implementation + TestToggleComplete (10 + 15 mins)

**Phase 3: UI Layer (7 tasks)**:
- T-016: [US2] display_menu() (10 mins)
- T-017: [US2] display_tasks() with formatting/truncation (30 mins)
- T-018: [US1] handle_add() with prompts (15 mins)
- T-019: [US2] handle_view() (5 mins)
- T-020: [US4] handle_update() with sequential prompts (20 mins)
- T-021: [US5] handle_delete() (10 mins)
- T-022: [US3] handle_toggle() (15 mins)

**Phase 4: Main Loop & Integration (2 tasks)**:
- T-023: main() function with menu loop, routing, error handling (40 mins)
- T-024: Add if __name__ == "__main__": main() entry point (2 mins)

**Phase 5: Integration Testing & Documentation (4 tasks)**:
- T-025: TestIntegrationWorkflow class (full CRUD cycle, 25 mins)
- T-026: Run all tests and verify 80%+ coverage (15 mins)
- T-027: Create README.md with setup/usage (30 mins)
- T-028: Manual testing checklist validation (16 scenarios, 45 mins)

**TDD Workflow Enforced**:
- Each implementation task paired with test task
- Tests written FIRST (RED phase)
- Implementation follows (GREEN phase)
- Test criteria checklist for every task (✓ format)

**Task Details for Each**:
- **From**: Specific plan.md line references and spec.md FR numbers
- **Description**: Clear statement of what to build
- **Preconditions**: Dependency tasks that must complete first
- **Artifacts**: Exact file paths and line counts
- **Implementation**: Complete code snippets or detailed pseudocode
- **Test Criteria**: Checklist of ✓ acceptance points
- **Estimated Time**: 2-45 minute ranges per task

**Dependencies & Execution Order**:
- **Critical Path**: T-001 → T-002 → T-004 → T-008 → T-010/T-012/T-014 → T-016/T-017 → T-018-T-022 → T-023 → T-024
- **Test Path**: Tests written immediately after their corresponding implementation
- **Parallel Opportunities**: T-006 after T-004, T-010/T-012/T-014 after T-008, T-018-T-022 after T-017
- **TDD Cycle**: Write test (RED) → Implement (GREEN) → Refactor

**Implementation Strategies**:
- **Single Developer**: Sequential order with checkpoints (8-10 hours total)
- **Parallel Team (2-3)**: Developer A (setup + add + main), Developer B (view + find + display), Developer C (update + delete + toggle + handlers)

**User Story Coverage**:
- US1 (Add Task): T-002, T-004, T-005, T-018
- US2 (View Tasks): T-006, T-007, T-016, T-017, T-019
- US3 (Toggle Complete): T-014, T-015, T-022
- US4 (Update Task): T-010, T-011, T-020
- US5 (Delete Task): T-012, T-013, T-021

**Spec/Plan Traceability**:
- All 20 functional requirements (FR-001 to FR-020) mapped to tasks
- All 6 core functions from plan.md covered
- All 7 UI functions from plan.md covered
- All 5 user stories from spec.md addressed

## Outcome

- ✅ Impact: Complete atomic task breakdown ready for implementation. All 28 tasks are independently testable with clear acceptance criteria. Full TDD workflow enforced with test-first approach. All 5 user stories and 20 functional requirements covered.
- 🧪 Tests: Test strategy embedded in tasks - 8 test classes defined (TestTaskDataclass, TestAddTask, TestViewTasks, TestFindTaskById, TestUpdateTask, TestDeleteTask, TestToggleComplete, TestIntegrationWorkflow) targeting 80%+ coverage
- 📁 Files: Created specs/001-phase-1-todo-cli/tasks.md (28 tasks, 450+ lines, estimated 8-10 hours total implementation time)
- 🔁 Next prompts: Begin implementation with T-001 (project structure), then follow TDD workflow: `/sp.red` (write tests) → verify RED → `/sp.green` (implement) → verify GREEN → `/sp.refactor` (cleanup)
- 🧠 Reflection: Task breakdown successfully decomposed user's 12 high-level tasks into 28 detailed atomic units. Each task has complete implementation guidance (code snippets, test criteria, time estimates). Reorganized into logical phases while preserving user story independence. TDD workflow explicitly encoded in task ordering (test before implementation). Find function (T-008/T-009) correctly identified as most complex (40+30 mins) due to dual UUID format support.

## Evaluation notes (flywheel)

- Failure modes observed: None - all tasks generated with complete details and proper dependencies
- Graders run and results (PASS/FAIL): Task atomicity check - 28/28 tasks are 15-60 min range (PASS). Spec traceability - 20/20 FRs mapped to tasks (PASS). TDD compliance - 8/8 test classes defined before implementation (PASS). User story independence - 5/5 stories can be implemented/tested independently (PASS).
- Prompt variant (if applicable): N/A (baseline tasks generation)
- Next experiment (smallest change to try): During implementation of T-008 (find_task_by_id), validate that the 40-minute estimate is accurate for dual UUID format support with prefix ambiguity detection. May need to split into two subtasks if complexity exceeds estimate.

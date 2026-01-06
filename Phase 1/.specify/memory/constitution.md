<!--
Sync Impact Report:
Version: 1.0.0 (Initial constitution for Phase 1)
Modified principles: N/A (new constitution)
Added sections:
  - Core Principles (6 principles: Simplicity First, Python Standard Library Only, Test-Driven Development, Type Safety, Clean Code Standards, Spec-Driven Development)
  - Technical Constraints
  - Success Criteria
  - Governance
Templates requiring updates:
  ✅ Constitution created (first version)
  ⚠ Pending: Plan template review for Phase 1 alignment
  ⚠ Pending: Spec template review for Phase 1 alignment
  ⚠ Pending: Tasks template review for Phase 1 alignment
Follow-up TODOs: Review dependent templates after Phase 1 completion
-->

# Phase 1 Todo App Constitution

## WHY: Mission and Purpose

**Phase 1 Mission**: Build a solid foundation for a todo application that demonstrates clean architecture, testable code, and spec-driven development principles. This phase establishes the core CRUD operations and architectural patterns that will evolve through subsequent phases (database persistence → web API → containerization → cloud-native AI).

**Success Definition**: A working Python console application with complete task management capabilities, comprehensive test coverage, and code quality that serves as a reference implementation for future phases.

## Core Principles

### I. Simplicity First

**MUST** prioritize the simplest solution that meets Phase 1 requirements. In-memory storage using Python data structures (lists, dictionaries) is the only acceptable approach. **MUST NOT** introduce databases, file persistence, or complex state management patterns. Architecture decisions must optimize for clarity and maintainability, not premature optimization for future phases.

**Rationale**: Phase 1 is a learning foundation. Complexity should be introduced incrementally in later phases. Simple code is easier to test, understand, and evolve.

### II. Python Standard Library Only

**MUST** use Python 3.13+ with UV package manager. **MUST NOT** add external dependencies beyond the Python standard library. All functionality (CLI argument parsing, data structures, datetime handling) must use built-in modules (`argparse`, `dataclasses`, `datetime`, `uuid`, etc.).

**Rationale**: Eliminates dependency management complexity, ensures reproducibility, and demonstrates Python language proficiency. UV is allowed for environment management but not for installing third-party packages.

### III. Test-Driven Development (NON-NEGOTIABLE)

**MUST** follow strict TDD workflow:
1. Write test cases (derived from spec acceptance criteria)
2. User/reviewer approves test coverage
3. Run tests → verify RED (failing)
4. Implement minimum code to pass
5. Run tests → verify GREEN (passing)
6. Refactor with tests as safety net

**MUST** achieve minimum 80% code coverage. **MUST** include both unit tests (individual functions) and integration tests (end-to-end CRUD workflows).

**Rationale**: TDD ensures requirements are testable, reduces debugging time, and creates living documentation. Red-Green-Refactor builds confidence in code correctness.

### IV. Type Safety

**MUST** use type hints for all function signatures (parameters and return types). **MUST** define dataclasses or TypedDicts for structured data (Task model). **SHOULD** run type checking with `mypy` (standard library alternative: runtime validation).

**Rationale**: Type hints improve IDE support, catch bugs early, and serve as inline documentation. Critical for maintaining code quality as the project evolves.

### V. Clean Code Standards

**MUST** follow these non-negotiable standards:
- **No global variables** except the in-memory task storage (e.g., `TASKS: list[Task] = []`)
- **Docstrings required** for all public functions (Google or NumPy style)
- **Function length**: Maximum 20 lines (extract helpers if longer)
- **Single Responsibility Principle**: Each function does one thing
- **Descriptive names**: No abbreviations (`create_task` not `crt_tsk`)
- **Error handling**: Explicit error messages for invalid operations

**Rationale**: Clean code is maintainable code. These rules prevent technical debt and make code review efficient.

### VI. Spec-Driven Development

**MUST** create `spec.md` → `plan.md` → `tasks.md` before writing implementation code. **MUST** trace every code change to a task in `tasks.md`, which traces to a requirement in `spec.md`. **MUST NOT** add features not specified in the spec.

**Rationale**: Spec-driven workflow prevents scope creep, ensures alignment with requirements, and creates audit trail for decision-making.

## Technical Constraints

### Phase 1 Scope: INCLUDED
- Command-line interface using `argparse`
- In-memory storage (global list/dict)
- Task model with fields: `id` (UUID), `title` (str), `description` (str), `completed` (bool), `created_at` (datetime)
- CRUD operations: Create, Read (list all), Update, Delete
- Mark task as complete/incomplete
- Input validation (non-empty titles, valid IDs)

### Phase 1 Scope: EXCLUDED (Out of Scope)
- **Persistence**: No file I/O, no databases (reserved for Phase 2)
- **Authentication/Authorization**: Single-user only, no user management
- **Web UI**: CLI only (web interface in Phase 3)
- **External dependencies**: No third-party libraries
- **Multi-user support**: No concurrency, no user sessions
- **Advanced features**: Search, filtering, tags, priorities (defer to later phases if needed)

### Technology Stack
- **Language**: Python 3.13+
- **Package Manager**: UV (for environment, not dependencies)
- **Testing**: `unittest` (standard library)
- **Type Checking**: Type hints (manual verification or `mypy` if available)
- **CLI Framework**: `argparse` (standard library)

## Success Criteria

### Functional Requirements
✅ All CRUD operations working via CLI commands
✅ Tasks persist in memory during program execution
✅ Valid input handled correctly
✅ Invalid input rejected with clear error messages
✅ Complete/incomplete toggle functional

### Code Quality Requirements
✅ 80%+ test coverage (measured by `coverage.py` or manual review)
✅ All functions have type hints and docstrings
✅ No `mypy` errors (if type checking enabled)
✅ Code passes peer review for clean code standards
✅ No global variables except task storage

### Process Requirements
✅ Complete `spec.md` approved before planning
✅ Complete `plan.md` approved before task breakdown
✅ Complete `tasks.md` with test cases before implementation
✅ TDD workflow followed (documented in commit history)
✅ All tasks traced to spec requirements

### Deliverables Checklist
- [ ] `specs/phase-1-todo-cli/spec.md` (feature specification)
- [ ] `specs/phase-1-todo-cli/plan.md` (architecture plan)
- [ ] `specs/phase-1-todo-cli/tasks.md` (task breakdown with test cases)
- [ ] `src/todo_app.py` (main application code)
- [ ] `src/models.py` (Task dataclass definition)
- [ ] `tests/test_todo_app.py` (comprehensive test suite)
- [ ] `README.md` (usage instructions and examples)

## Development Workflow

### 1. Spec Phase
- Create `specs/phase-1-todo-cli/spec.md` using spec template
- Define user stories, acceptance criteria, and constraints
- Get approval before proceeding to planning

### 2. Plan Phase
- Create `specs/phase-1-todo-cli/plan.md` using plan template
- Design data model, CLI interface, function architecture
- Identify architectural decisions (document in ADRs if significant)
- Get approval before task breakdown

### 3. Task Phase
- Create `specs/phase-1-todo-cli/tasks.md` using tasks template
- Break plan into atomic, testable tasks
- Write test cases for each task
- Get test approval before implementation

### 4. Red-Green-Refactor Phase
- **RED**: Write tests → verify they fail
- **GREEN**: Implement minimum code → verify tests pass
- **REFACTOR**: Clean up code while keeping tests green
- Commit after each green cycle with descriptive messages

### 5. Review Phase
- Self-review against constitution principles
- Verify all success criteria met
- Run full test suite and type checking
- Create PR (if using Git workflow)

## Governance

### Constitutional Authority
This constitution **SUPERSEDES** all other development practices for Phase 1. Any code, design decision, or process not aligned with these principles **MUST** be rejected during review.

### Amendment Process
1. Propose amendment with clear rationale and impact analysis
2. Update constitution version following semantic versioning:
   - **MAJOR**: Backward-incompatible principle changes (e.g., removing TDD requirement)
   - **MINOR**: New principles added (e.g., adding security principle)
   - **PATCH**: Clarifications and typo fixes
3. Propagate changes to dependent templates (spec, plan, tasks)
4. Document amendment in Sync Impact Report (HTML comment at top of file)

### Compliance Verification
- **Every PR/commit**: Verify alignment with Core Principles
- **Code reviews**: Use constitution as checklist
- **Complexity justification**: Any deviation from "Simplicity First" requires written rationale
- **Spec traceability**: Reject code without corresponding spec/task reference

### Version Control
Use Git for version control with conventional commits:
- `feat:` for new features
- `fix:` for bug fixes
- `test:` for test additions
- `refactor:` for code improvements
- `docs:` for documentation updates

### Quality Gates (Must Pass Before Submission)
1. All tests passing (`python -m unittest discover tests/`)
2. Type hints present (manual inspection or `mypy --strict`)
3. Docstrings complete (manual inspection)
4. Constitution compliance verified (self-review checklist)
5. README updated with usage examples

---

**Version**: 1.0.0 | **Ratified**: 2025-12-30 | **Last Amended**: 2025-12-30

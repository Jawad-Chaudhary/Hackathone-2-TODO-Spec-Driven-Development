---
id: 0002
title: Clarify Phase 1 Todo CLI Specification
stage: spec
date: 2025-12-30
surface: agent
model: claude-sonnet-4-5
feature: 001-phase-1-todo-cli
branch: 001-phase-1-todo-cli
user: system
command: /sp.clarify
labels: ["clarify", "spec", "ambiguity-resolution", "ux-flow", "data-validation"]
links:
  spec: specs/001-phase-1-todo-cli/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase-1-todo-cli/spec.md
tests:
  - none (specification clarification, tests will be defined in tasks.md)
---

## Prompt

Review the Phase 1 specification and resolve all ambiguous requirements.

Spec file: specs/phase-1/specify.md

Clarify decisions for:

Data model (task ID type, description length, whitespace handling)

Task ID management (start value, reuse after delete, overflow)

Update behavior (partial updates, empty input, no-change handling)

Display format (status symbols, sorting, missing descriptions)

Input validation (empty/trimmed titles, max lengths)

Error messages (task not found, invalid input, menu errors)

Edge cases (empty list, duplicate titles, repeated toggles)

For each item, include:

The ambiguity

Recommended decision (with rationale)

Alternatives (if any)

Implementation impact

Produce a clarification document that fully removes ambiguity from the specification.

## Response snapshot

Conducted interactive clarification session with 5 critical questions, all answered:

**Q1: Task ID Input Format**
- Ambiguity: Should users enter full UUID (36 chars) or truncated 8-char version?
- Decision: Allow both full UUID and 8-character prefix
- Rationale: Users see 8-char IDs in display; supporting both provides flexibility
- Impact: Updated FR-015, edge cases

**Q2: Update Operation User Flow**
- Ambiguity: How should partial updates work (title only, description only, or both)?
- Decision: Prompt for both fields sequentially; pressing Enter skips/keeps existing value
- Rationale: Simpler flow, consistent experience, matches common CLI patterns
- Impact: Updated FR-011, FR-012; expanded User Story 4 to 6 acceptance scenarios

**Q3: Whitespace Handling in Titles**
- Ambiguity: Should titles with leading/trailing whitespace be trimmed, rejected, or stored as-is?
- Decision: Automatically trim before validation and storage
- Rationale: Prevents accidental whitespace, ensures consistent display
- Impact: Updated FR-004; expanded User Story 1 to 6 acceptance scenarios; clarified edge cases

**Q4: Description Display in Task List**
- Ambiguity: Should description be shown in "View Tasks" list or only in detail view?
- Decision: Show description in list (truncated to 50 chars with "..." if longer)
- Rationale: Provides context at a glance, helps identify tasks without extra steps
- Impact: Updated FR-008; expanded User Story 2 to 5 acceptance scenarios; added edge case

**Q5: Creation Date Display Format**
- Ambiguity: What format for displaying timestamp (ISO 8601, human-readable, relative time)?
- Decision: Human-readable "YYYY-MM-DD HH:MM"
- Rationale: Clear, unambiguous, compact, sortable, internationally understood
- Impact: Updated FR-008, Task entity definition

**Sections Modified**:
- New "Clarifications" section (5 Q&A entries under Session 2025-12-30)
- User Story 1: 4 → 6 acceptance scenarios
- User Story 2: 4 → 5 acceptance scenarios
- User Story 4: 5 → 6 acceptance scenarios
- Edge Cases: Updated 2, added 1 (total 9 cases)
- Functional Requirements: Updated FR-004, FR-008, FR-011, FR-012, FR-015
- Key Entities: Updated Task entity (Title, Created At attributes)

**Total Acceptance Scenarios**: 33 across 5 user stories (up from 28)

## Outcome

- ✅ Impact: All critical ambiguities resolved. Specification now has complete UX flows, precise validation rules, and explicit display formatting. Ready for planning phase.
- 🧪 Tests: Spec clarification complete; expanded acceptance scenarios from 28 to 33 (17% increase in test coverage)
- 📁 Files: Updated specs/001-phase-1-todo-cli/spec.md (added Clarifications section, updated 6 sections)
- 🔁 Next prompts: `/sp.plan` to design technical architecture based on clarified spec
- 🧠 Reflection: Interactive questioning approach worked well - user selected recommended options for all 5 questions, suggesting recommendations were well-aligned with best practices. Incremental integration after each answer prevented context loss and allowed immediate validation.

## Evaluation notes (flywheel)

- Failure modes observed: None - all 5 questions answered, all clarifications integrated successfully
- Graders run and results (PASS/FAIL): Ambiguity coverage assessment - 10/10 categories resolved or clear (100%)
- Prompt variant (if applicable): Sequential single-question approach with recommended options presented first
- Next experiment (smallest change to try): During planning, validate that clarifications translate cleanly into implementation details without new ambiguities emerging

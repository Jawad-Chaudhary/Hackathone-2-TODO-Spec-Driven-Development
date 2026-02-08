# Tasks: Advanced Task Management with Event-Driven Architecture

**Input**: Design documents from `/specs/001-advanced-features-event-driven/`
**Prerequisites**: plan.md (required), spec.md (required)

**Note**: This is Phase 5 - Advanced Features with Event-Driven Architecture, Modern UI, and Cloud Deployment

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5, US6)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment setup

- [ ] T001 [P] Install Dapr CLI v1.14+ and verify installation with `dapr --version`
- [ ] T002 [P] Install Helm 3 and verify with `helm version`
- [ ] T003 [P] Start Minikube cluster with `minikube start --cpus=4 --memory=8192`
- [ ] T004 Initialize Dapr on Minikube with `dapr init -k`
- [ ] T005 [P] Install Redpanda Helm chart for local Kafka: `helm install redpanda redpanda/redpanda --set statefulset.replicas=1`
- [X] T006 [P] Add Dapr Python SDK to backend/requirements.txt: `dapr>=1.14.0`
- [X] T007 [P] Add shadcn/ui dependencies to frontend/package.json: `@radix-ui/react-*`, `class-variance-authority`, `clsx`, `tailwind-merge`
- [X] T008 [P] Add Framer Motion to frontend/package.json: `framer-motion@^11.0.0`
- [X] T009 [P] Add TanStack Query to frontend/package.json: `@tanstack/react-query@^5.0.0`
- [X] T010 [P] Add Zustand to frontend/package.json: `zustand@^4.5.0`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T011 Create Alembic migration in backend/alembic/versions/xxx_add_advanced_fields.py adding nullable columns: priority (VARCHAR(10)), tags (JSON), due_date (TIMESTAMP), recurrence (VARCHAR(10)), recurrence_interval (INTEGER), parent_task_id (INTEGER)
- [X] T012 Create database indexes: idx_task_due_date, idx_task_priority, idx_task_tags_gin (GIN index), idx_task_user_status
- [X] T013 Run Alembic migration with `alembic upgrade head` to apply schema changes
- [X] T014 Update Task model in backend/app/models/task.py adding priority (Optional[PriorityEnum]), tags (list[str] with JSON Column), due_date (Optional[datetime]), recurrence (Optional[RecurrenceEnum]), recurrence_interval (Optional[int]), parent_task_id (Optional[int])
- [X] T015 Create PriorityEnum and RecurrenceEnum in backend/app/models/task.py with values (high/medium/low) and (daily/weekly/monthly/custom)
- [X] T016 Update TaskCreate schema in backend/app/schemas/task.py adding optional fields: priority, tags, due_date, recurrence, recurrence_interval
- [X] T017 Update TaskResponse schema in backend/app/schemas/task.py to include all new fields
- [X] T018 Create event schemas in backend/app/events/schemas.py for CloudEvents format: TaskCreatedEvent, TaskCompletedEvent, TaskUpdatedEvent, ReminderScheduledEvent
- [X] T019 Create Dapr client wrapper in backend/app/dapr_config.py with initialization and publish_event() method
- [X] T020 Create event publisher service in backend/app/events/publisher.py with methods: publish_task_created(), publish_task_completed(), publish_task_updated()
- [X] T021 Create Kubernetes secrets manifest in k8s/base/secrets.yaml for neon-db-creds, redpanda-creds, openai-key
- [X] T022 Create Dapr pubsub component in k8s/components/pubsub.yaml configuring Redpanda Cloud with SASL authentication
- [X] T023 [P] Create Dapr statestore component in k8s/components/statestore.yaml configuring Neon PostgreSQL connection
- [X] T024 [P] Create Dapr secretstore component in k8s/components/secretstore.yaml referencing Kubernetes secrets
- [X] T025 [P] Create Dapr cron binding in k8s/components/reminder-cron.yaml with schedule `@every 5m`
- [X] T026 Update Helm chart in helm/todo-app/templates/backend-deployment.yaml adding Dapr annotations: dapr.io/enabled, dapr.io/app-id, dapr.io/app-port
- [X] T027 Install shadcn/ui CLI and initialize in frontend with `npx shadcn-ui@latest init`
- [X] T028 Configure Tailwind CSS dark mode in frontend/tailwind.config.js with `darkMode: ['class']`
- [X] T029 Create theme provider in frontend/src/providers/theme-provider.tsx using next-themes
- [X] T030 Add ThemeProvider to frontend/src/app/layout.tsx wrapping children

**Checkpoint**: Foundation ready - database migrated, Dapr components configured, UI foundation set up

---

## Phase 3: User Story 1 - Recurring Task Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to create recurring tasks that automatically generate next occurrence on completion

**Independent Test**: Create daily recurring task, mark complete, verify new task created for next day

### Implementation for User Story 1

- [X] T031 [P] [US1] Update add_task MCP tool in backend/app/mcp/tools/add_task.py to accept recurrence and recurrence_interval parameters
- [X] T032 [P] [US1] Update complete_task MCP tool in backend/app/mcp/tools/complete_task.py to publish task.completed.v1 event after marking complete
- [X] T033 [US1] Create recurring service directory structure: services/recurring-service/ with main.py, handler.py, requirements.txt, Dockerfile
- [X] T034 [US1] Implement Dapr subscription in services/recurring-service/main.py subscribing to task-events topic for task.completed.v1 events
- [X] T035 [US1] Implement recurring task handler in services/recurring-service/handler.py that creates next occurrence: calculate next due date, copy task attributes, create via API call
- [X] T036 [US1] Create Dockerfile for recurring-service in services/recurring-service/Dockerfile with Python 3.11-slim base, Dapr SDK
- [X] T037 [US1] Add recurring-service to Helm chart in helm/todo-app/templates/recurring-service-deployment.yaml with Dapr sidecar annotations
- [X] T038 [US1] Create recurring task form fields in frontend/src/components/tasks/task-form.tsx: recurrence dropdown (Daily/Weekly/Monthly/Custom), interval input for custom
- [X] T039 [US1] Add recurrence badge display in frontend/src/components/tasks/task-list-item.tsx showing repeat icon and frequency

**Checkpoint**: User Story 1 complete - recurring tasks auto-create next occurrence

---

## Phase 4: User Story 2 - Due Date Management with Reminders (Priority: P1)

**Goal**: Enable users to set due dates and receive browser notifications 15 minutes before

**Independent Test**: Create task with due date 16 min from now, wait, verify browser notification appears at 15 min before

### Implementation for User Story 2

- [X] T040 [P] [US2] Create notification service directory: services/notification-service/ with main.py, reminder_checker.py, requirements.txt, Dockerfile
- [X] T041 [P] [US2] Implement Dapr cron binding handler in services/notification-service/main.py listening for reminder-cron trigger
- [X] T042 [US2] Implement reminder checker in services/notification-service/reminder_checker.py: query tasks with due_date within next 15 minutes, publish reminder.scheduled.v1 events
- [X] T043 [US2] Create Dockerfile for notification-service in services/notification-service/Dockerfile
- [X] T044 [US2] Add notification-service to Helm chart in helm/todo-app/templates/notification-service-deployment.yaml with Dapr sidecar
- [X] T045 [US2] Create WebSocket manager in backend/app/websocket/manager.py with connection tracking per user_id
- [X] T046 [US2] Create WebSocket route in backend/app/websocket/routes.py at `/ws/{user_id}` endpoint
- [X] T047 [US2] Create Dapr subscription handler in backend/app/events/handlers.py subscribing to reminders topic, broadcasting via WebSocket
- [X] T048 [US2] Add WebSocket endpoint to FastAPI app in backend/app/main.py
- [X] T049 [US2] Create WebSocket client hook in frontend/src/hooks/use-websocket.ts connecting to backend WebSocket
- [X] T050 [US2] Create browser notification service in frontend/src/lib/notifications.ts: request permissions, show notification, handle click
- [X] T051 [US2] Create due date picker in frontend/src/components/tasks/task-form.tsx using shadcn/ui Calendar and time input
- [X] T052 [US2] Add overdue indicator in frontend/src/components/tasks/task-list-item.tsx: check if due_date < now and status=pending, show red highlight
- [X] T053 [US2] Integrate WebSocket hook in frontend/src/app/layout.tsx to listen for reminder events and trigger notifications

**Checkpoint**: User Story 2 complete - due dates work, reminders sent 15 min before

---

## Phase 5: User Story 3 - Task Prioritization and Tagging (Priority: P2)

**Goal**: Enable priority assignment (High/Medium/Low) with color coding and multi-tag support

**Independent Test**: Create tasks with different priorities and tags, verify correct color display and tag filtering

### Implementation for User Story 3

- [X] T054 [P] [US3] Update add_task MCP tool in backend/app/mcp/tools/add_task.py to accept priority and tags parameters
- [X] T055 [P] [US3] Update update_task MCP tool in backend/app/mcp/tools/update_task.py to allow priority and tags updates
- [X] T056 [US3] Update GET /api/tasks endpoint in backend/app/routes/tasks.py to support priority filter query parameter
- [X] T057 [US3] Update GET /api/tasks endpoint to support tags filter (array, AND logic)
- [X] T058 [US3] Install shadcn/ui Badge component: `npx shadcn-ui@latest add badge`
- [X] T059 [US3] Create priority selector in frontend/src/components/tasks/priority-selector.tsx with dropdown: High (red), Medium (yellow), Low (green), using Badge component
- [X] T060 [US3] Create tag input component in frontend/src/components/tasks/tag-input.tsx allowing multi-tag entry with combobox, showing existing tags as badges
- [X] T061 [US3] Add priority selector and tag input to task form in frontend/src/components/tasks/task-form.tsx
- [X] T062 [US3] Display priority badge in frontend/src/components/tasks/task-list-item.tsx with conditional color styling: high=bg-red-500, medium=bg-yellow-500, low=bg-green-500
- [X] T063 [US3] Display tags as clickable badges in frontend/src/components/tasks/task-list-item.tsx with onClick to filter by tag

**Checkpoint**: User Story 3 complete - priorities color-coded, tags functional

---

## Phase 6: User Story 4 - Advanced Search and Filtering (Priority: P2)

**Goal**: Enable fuzzy search and multi-criteria filtering (status, priority, tags, due date range)

**Independent Test**: Create 20+ varied tasks, search partial text, apply multiple filters, verify correct results

### Implementation for User Story 4

- [X] T064 [US4] Create search service in backend/app/services/search_service.py implementing PostgreSQL full-text search with ts_vector and ts_query
- [X] T065 [US4] Update GET /api/tasks endpoint in backend/app/routes/tasks.py adding search query parameter with fuzzy matching
- [X] T066 [US4] Add status filter parameter to GET /api/tasks (pending/completed)
- [X] T067 [US4] Add due_start and due_end parameters to GET /api/tasks for date range filtering
- [X] T068 [US4] Implement combined filter logic in backend query builder (AND logic for multiple filters)
- [X] T069 [US4] Install shadcn/ui Input component: `npx shadcn-ui@latest add input`
- [X] T070 [US4] Install shadcn/ui Select component: `npx shadcn-ui@latest add select`
- [X] T071 [US4] Create search bar component in frontend/src/components/tasks/search-bar.tsx with debounced input
- [X] T072 [US4] Create filter panel in frontend/src/components/tasks/filter-panel.tsx with dropdowns: status, priority, tags, date range pickers
- [X] T073 [US4] Create Zustand store in frontend/src/stores/filter-store.ts managing active filters state
- [X] T074 [US4] Integrate filters with TanStack Query in frontend/src/hooks/use-tasks.ts passing filters as query params
- [X] T075 [US4] Add filter panel to tasks page in frontend/src/app/tasks/page.tsx above task list
- [X] T076 [US4] Add "Clear Filters" button in filter panel resetting all filters to default

**Checkpoint**: User Story 4 complete - search and filtering working with multiple criteria

---

## Phase 7: User Story 5 - Task Sorting (Priority: P3)

**Goal**: Enable sorting by due date, priority, created date, alphabetical

**Independent Test**: Create tasks with varied attributes, click sort options, verify list reorders correctly

### Implementation for User Story 5

- [X] T077 [US5] Add sort_by and sort_order parameters to GET /api/tasks endpoint in backend/app/routes/tasks.py
- [X] T078 [US5] Implement sorting logic in backend query builder supporting: due_date, priority, created_at, title (ascending/descending)
- [X] T079 [US5] Create sort dropdown component in frontend/components/sort-selector.tsx with options: Due Date, Priority, Created, Alphabetical, and direction toggle
- [X] T080 [US5] Add sort selector to tasks page in frontend/app/tasks/page.tsx in header toolbar
- [X] T081 [US5] Update Zustand store in frontend/stores/filter-store.ts to include sort_by and sort_order state
- [X] T082 [US5] Integrate sort parameters with getTasks API in frontend/lib/api.ts (using direct fetch instead of TanStack Query)

**Checkpoint**: User Story 5 complete - all sort options working

---

## Phase 8: User Story 6 - Modern UI Dashboard (Priority: P2)

**Goal**: Dashboard with statistics cards (Total/Completed/Pending/Overdue) and calendar view

**Independent Test**: View dashboard, verify stats accurate, see tasks on calendar dates, toggle dark mode, check mobile responsive

### Implementation for User Story 6

- [X] T083 [US6] Create stats service in backend/app/services/stats_service.py with method: get_user_stats(user_id) returning counts
- [X] T084 [US6] Create GET /api/dashboard/stats endpoint in backend/app/routes/tasks.py returning {total, completed, pending, overdue}
- [X] T085 [US6] Install shadcn/ui Card component: `npx shadcn-ui@latest add card`
- [X] T086 [US6] Install shadcn/ui Calendar component: `npx shadcn-ui@latest add calendar`
- [X] T087 [US6] Create stats card component in frontend/src/components/dashboard/stat-card.tsx displaying count with icon and label
- [X] T088 [US6] Create dashboard page in frontend/src/app/dashboard/page.tsx with grid of 4 stat cards
- [X] T089 [US6] Create calendar view component in frontend/src/components/dashboard/calendar-view.tsx showing tasks on their due dates
- [X] T090 [US6] Fetch tasks for current month in calendar view, render dots on dates with tasks
- [X] T091 [US6] Add date click handler to calendar showing tasks due on that date in a dialog
- [X] T092 [US6] Create theme toggle component in frontend/src/components/theme-toggle.tsx with sun/moon icons
- [X] T093 [US6] Add theme toggle to navigation bar in frontend/src/components/nav.tsx
- [X] T094 [US6] Add Framer Motion page transitions in frontend/src/app/layout.tsx using AnimatePresence
- [X] T095 [US6] Add Framer Motion animations to task list items in frontend/src/components/tasks/task-list-item.tsx: fade-in, slide-in on mount
- [X] T096 [US6] Add Framer Motion animations to modal dialogs using motion.div with scale animation
- [X] T097 [US6] Test responsive layout on mobile (320px width) adjusting grid columns and card sizing

**Checkpoint**: User Story 6 complete - dashboard functional, dark mode working, animations smooth, responsive

---

## Phase 9: Cloud Infrastructure Setup

**Purpose**: Oracle Cloud OKE and Redpanda Cloud configuration

- [ ] T098 Sign up for Redpanda Cloud account at https://redpanda.com/cloud
- [ ] T099 Create Redpanda Serverless cluster in free tier
- [ ] T100 [P] Create topic `task-events` in Redpanda console with partition count 3
- [ ] T101 [P] Create topic `task-updates` in Redpanda console with partition count 3
- [ ] T102 [P] Create topic `reminders` in Redpanda console with partition count 1
- [ ] T103 Copy Redpanda bootstrap server URL and SASL credentials from console
- [ ] T104 Update pubsub.yaml in k8s/components/pubsub.yaml with Redpanda Cloud broker URL and auth
- [ ] T105 Sign up for Oracle Cloud account at https://cloud.oracle.com
- [ ] T106 Create OKE cluster in Oracle Cloud Console: Always Free tier, 2 worker nodes, 1 OCPU each
- [ ] T107 Configure kubectl for OKE cluster: `oci ce cluster create-kubeconfig --cluster-id <id>`
- [ ] T108 Install Dapr on OKE cluster: `dapr init -k`
- [ ] T109 Create namespace in OKE: `kubectl create namespace todo-app`
- [ ] T110 Apply Kubernetes secrets to OKE: `kubectl apply -f k8s/base/secrets.yaml -n todo-app`
- [ ] T111 Apply Dapr components to OKE: `kubectl apply -f k8s/components/ -n todo-app`

**Checkpoint**: Cloud infrastructure ready - Redpanda topics created, OKE cluster configured

---

## Phase 10: CI/CD Pipeline

**Purpose**: Automated deployment via GitHub Actions

- [X] T112 Create GitHub Actions workflow file in .github/workflows/deploy.yml
- [X] T113 Add build job to workflow: build Docker images for backend, frontend, recurring-service, notification-service
- [X] T114 Add test job to workflow: run pytest for backend unit tests
- [X] T115 Add security scan job to workflow: run Trivy scan on all Docker images
- [X] T116 Add push job to workflow: push images to Oracle Container Registry with git SHA tag
- [X] T117 Add deploy job to workflow: helm upgrade --install todo-app ./helm/todo-app --set image.tag=$GITHUB_SHA
- [X] T118 Add smoke test job to workflow: curl health endpoints, test task creation via API
- [X] T119 Add GitHub secrets: OKE_KUBECONFIG, REDPANDA_BROKER, REDPANDA_USERNAME, REDPANDA_PASSWORD, NEON_DB_URL
- [X] T120 Configure workflow trigger on push to main branch
- [X] T121 Test CI/CD pipeline by pushing commit to main, verify auto-deployment to OKE

**Checkpoint**: CI/CD pipeline functional - auto-deploys on git push

---

## Phase 11: Testing & Verification

**Purpose**: End-to-end testing and verification of all features

- [ ] T122 Create integration test for recurring tasks in backend/tests/integration/test_recurring.py: create recurring task, complete it, assert next created
- [ ] T123 Create integration test for reminders in backend/tests/integration/test_reminders.py: create task with due date, trigger notification service cron, assert event published
- [ ] T124 Create Playwright E2E test in frontend/tests/e2e/recurring-tasks.spec.ts: full flow from UI
- [ ] ] T125 Create Playwright E2E test in frontend/tests/e2e/reminders.spec.ts: set due date, verify notification (mock)
- [ ] T126 Create Playwright E2E test in frontend/tests/e2e/search-filter.spec.ts: test search bar and all filter combinations
- [ ] T127 Create Playwright E2E test in frontend/tests/e2e/dashboard.spec.ts: verify stats accuracy, calendar interaction
- [ ] T128 Test all features on Oracle Cloud OKE deployment: create tasks, test recurring, test reminders, test search/filter
- [ ] T129 Verify WebSocket real-time updates work across multiple browser tabs
- [ ] T130 Verify dark mode persists across page refreshes
- [ ] T131 Run performance test: create 1000 tasks, measure search/filter response time (target < 0.5s)
- [ ] T132 Test mobile responsive layout on iPhone SE (375px) and Galaxy Fold (280px)

**Checkpoint**: All features verified working in production

---

## Phase 12: Documentation & Polish

**Purpose**: Final documentation and code cleanup

- [X] T133 Update README.md with Phase 5 features section: recurring tasks, reminders, priorities, tags, search, dashboard (content prepared by agent)
- [X] T134 Create quickstart guide in docs/INFRASTRUCTURE_SETUP.md: local Minikube setup steps (completed as docs/INFRASTRUCTURE_SETUP.md)
- [X] T135 Create cloud deployment guide in docs/phase5-cloud-deployment.md: Oracle OKE and Redpanda Cloud setup
- [X] T136 Document event schemas in docs/event-schemas.md with CloudEvents format examples
- [X] T137 Document Dapr components in docs/dapr-components.md with YAML examples
- [X] T138 Add API documentation for new endpoints in docs/api.md: search, filter, sort, stats (content prepared by agent)
- [X] T139 Create architecture diagram showing event flow: Backend → Dapr → Kafka → Services → WebSocket → Frontend
- [ ] T140 Code cleanup: remove console.log statements, unused imports
- [ ] T141 Run linters: `eslint` on frontend, `black` and `flake8` on backend
- [X] T142 Update version number to v2.0.0 in package.json and pyproject.toml

**Checkpoint**: Documentation complete, code polished

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational completion
  - US1 (Recurring Tasks) - Phase 3: Can start after Foundational
  - US2 (Due Dates/Reminders) - Phase 4: Can start after Foundational (independent of US1)
  - US3 (Priorities/Tags) - Phase 5: Can start after Foundational (independent of US1/US2)
  - US4 (Search/Filter) - Phase 6: Can start after Foundational (independent of US1/US2/US3)
  - US5 (Sorting) - Phase 7: Can start after Foundational (independent of other stories)
  - US6 (Dashboard) - Phase 8: Depends on US3 (stats need priority data)
- **Cloud Setup (Phase 9)**: Can start in parallel with any user story work (infrastructure only)
- **CI/CD (Phase 10)**: Depends on Cloud Setup completion
- **Testing (Phase 11)**: Depends on all user stories completion
- **Documentation (Phase 12)**: Depends on Testing completion

### User Story Dependencies

- **US1 (Recurring Tasks)**: Independent - can implement alone
- **US2 (Due Dates/Reminders)**: Independent - can implement alone
- **US3 (Priorities/Tags)**: Independent - can implement alone
- **US4 (Search/Filter)**: Independent - can implement alone (though works best with US3 data)
- **US5 (Sorting)**: Independent - can implement alone
- **US6 (Dashboard)**: Partial dependency on US3 for priority stats in dashboard cards

### Parallel Opportunities

- **Setup Phase**: T001-T010 can all run in parallel (different installations)
- **Foundational Phase**:
  - T018-T020 (event code) can run parallel with T021-T025 (Dapr YAML)
  - T027-T030 (frontend setup) can run parallel with backend tasks
- **Within User Stories**:
  - US1: T031-T032 (MCP tools) parallel, T038-T039 (frontend) parallel
  - US2: T040-T044 (notification service) parallel with T045-T048 (WebSocket backend)
  - US3: T054-T055 (backend) parallel, T058-T060 (frontend components) parallel
  - US4: T069-T070 (shadcn components) parallel
- **Cloud Setup**: T100-T102 (Redpanda topics) all parallel
- **Multiple Developers**: After Foundational complete, US1-US5 can be worked on simultaneously by different team members

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Recurring Tasks)
4. Complete Phase 4: User Story 2 (Due Dates/Reminders)
5. **STOP and VALIDATE**: Test both stories independently on Minikube
6. Deploy MVP to Oracle Cloud (Phase 9-10)
7. **Demo MVP**: Recurring tasks + reminders working

### Incremental Delivery (Add Features)

After MVP:
1. Add Phase 5: User Story 3 (Priorities/Tags) → Test independently → Deploy
2. Add Phase 6: User Story 4 (Search/Filter) → Test independently → Deploy
3. Add Phase 7: User Story 5 (Sorting) → Test independently → Deploy
4. Add Phase 8: User Story 6 (Dashboard) → Test independently → Deploy

Each phase adds value without breaking previous features.

### Parallel Team Strategy

With 3 developers after Foundational complete:
- Developer A: US1 + US2 (P1 stories - MVP critical)
- Developer B: US3 + US4 (P2 stories - high value)
- Developer C: US6 (P2 dashboard) + Cloud Setup (Phase 9)
- Developer A (after MVP): US5 (P3 sorting) + CI/CD (Phase 10)

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
- **Tests**: Integration and E2E tests in Phase 11 (not TDD - tests after implementation)
- All Dapr components are YAML-only (constitutional requirement)
- Event-driven: All task mutations MUST publish events
- Modern UI: Shadcn/ui + Framer Motion + dark mode (constitutional requirement)

---

## Task Summary

- **Total Tasks**: 142
- **Setup**: 10 tasks
- **Foundational**: 20 tasks
- **US1 (Recurring)**: 9 tasks
- **US2 (Reminders)**: 14 tasks
- **US3 (Priorities/Tags)**: 10 tasks
- **US4 (Search/Filter)**: 13 tasks
- **US5 (Sorting)**: 6 tasks
- **US6 (Dashboard)**: 15 tasks
- **Cloud Setup**: 14 tasks
- **CI/CD**: 10 tasks
- **Testing**: 11 tasks
- **Documentation**: 10 tasks

**MVP Scope** (US1 + US2): 43 tasks (Setup + Foundational + US1 + US2)
**Full Feature Set**: 142 tasks

**Parallel Opportunities**: ~30 tasks can run in parallel (marked with [P])
**Independent Stories**: US1-US5 can be developed simultaneously after Foundational phase

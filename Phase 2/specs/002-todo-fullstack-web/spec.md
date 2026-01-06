# Feature Specification: Todo Full-Stack Web Application

**Feature Branch**: `002-todo-fullstack-web`
**Created**: 2026-01-03
**Status**: Draft
**Input**: User description: "Create a detailed specification for Todo Full-Stack Web Application"

## Clarifications

### Session 2026-01-03

- Q: Email Verification Requirement → A: Skip email verification for Phase II (users can immediately use the app after signup)
- Q: UI Component Library Choice → A: Pure Tailwind CSS with custom components (no third-party component library)
- Q: Deployment Architecture → A: Separate Vercel projects for frontend and backend (independent deployments)
- Q: JWT Refresh Token Strategy → A: Require re-login after token expiration (no refresh tokens in Phase II)
- Q: Testing Strategy for Phase II → A: Manual testing only with documented test cases (no automated tests in Phase II)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration and Authentication (Priority: P1)

A new user visits the web application and needs to create an account to start managing their personal todo list. This is the foundation for all other features as it enables user isolation and secure access.

**Why this priority**: Without authentication, users cannot have personalized, persistent task lists. This is the entry point for all other functionality and must work before any other feature is valuable.

**Independent Test**: Can be fully tested by creating a new account, logging in, logging out, and attempting to access protected routes without authentication. Delivers value by securing the application and enabling multi-user support.

**Acceptance Scenarios**:

1. **Given** a user visits the application for the first time, **When** they click "Sign Up" and enter valid email and password, **Then** their account is created, they receive a JWT token, and are redirected to the task list page
2. **Given** an existing user account, **When** the user enters correct credentials and clicks "Sign In", **Then** they receive a JWT token and are redirected to their task list
3. **Given** an authenticated user, **When** they click "Logout", **Then** their session is cleared and they are redirected to the sign-in page
4. **Given** an unauthenticated user, **When** they attempt to access the task list page, **Then** they are redirected to the sign-in page
5. **Given** a user attempts to sign up, **When** they enter an email that already exists, **Then** they see an error message "Email already registered"
6. **Given** a user attempts to sign in, **When** they enter invalid credentials, **Then** they see an error message "Invalid email or password"

---

### User Story 2 - Create and View Tasks (Priority: P2)

An authenticated user wants to add new tasks to their todo list and view all their existing tasks. This is the core value proposition of the application.

**Why this priority**: This is the primary use case - users need to create and see their tasks. Without this, the app has no practical value even though authentication works.

**Independent Test**: Can be tested independently by logging in as an authenticated user, adding multiple tasks with different titles and descriptions, and verifying they appear in the task list. Page refresh should persist tasks.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the task list page, **When** they enter a task title and optional description and click "Add Task", **Then** the new task appears at the top of the list with status "incomplete"
2. **Given** an authenticated user with existing tasks, **When** they view the task list page, **Then** they see only their own tasks sorted by creation date (newest first)
3. **Given** an authenticated user creates a task, **When** they refresh the browser page, **Then** all their tasks are still visible (persisted to database)
4. **Given** a user with no tasks, **When** they view the task list page, **Then** they see an empty state message "No tasks yet. Create your first task to get started!"
5. **Given** a user attempts to create a task, **When** they leave the title field empty, **Then** they see a validation error "Task title is required"
6. **Given** a user attempts to create a task, **When** they enter a title longer than 200 characters, **Then** they see a validation error "Title must be 200 characters or less"
7. **Given** a user with tasks, **When** they view the task list, **Then** each task displays title, description (if provided), completion status, and creation date

---

### User Story 3 - Mark Tasks as Complete (Priority: P3)

An authenticated user wants to mark tasks as complete or incomplete to track their progress. This provides the satisfaction of checking off completed items.

**Why this priority**: While important for task management, users can still add and view tasks without this feature. It enhances the user experience but isn't blocking for basic functionality.

**Independent Test**: Can be tested by creating several tasks, toggling their completion status, and verifying the UI reflects the change and persists to the database.

**Acceptance Scenarios**:

1. **Given** an authenticated user with incomplete tasks, **When** they click the checkbox/toggle next to a task, **Then** the task is marked as complete and visually distinguished (e.g., strikethrough text, different color)
2. **Given** an authenticated user with a complete task, **When** they click the checkbox/toggle next to the task, **Then** the task is marked as incomplete and returns to normal styling
3. **Given** a user toggles task completion, **When** they refresh the page, **Then** the completion status persists correctly
4. **Given** a user marks a task complete, **When** the status update request is sent to the backend, **Then** the UI updates immediately without waiting for server response (optimistic update)

---

### User Story 4 - Update Task Details (Priority: P4)

An authenticated user wants to edit the title or description of an existing task to correct mistakes or update information.

**Why this priority**: Users can work around this by deleting and recreating tasks, so it's not critical for MVP. However, it significantly improves user experience.

**Independent Test**: Can be tested by creating a task, editing its title and description, and verifying changes persist to the database.

**Acceptance Scenarios**:

1. **Given** an authenticated user views a task, **When** they click an "Edit" button, **Then** the task enters edit mode with editable title and description fields
2. **Given** a task in edit mode, **When** the user modifies the title or description and clicks "Save", **Then** the changes are saved to the database and the UI updates immediately
3. **Given** a task in edit mode, **When** the user clicks "Cancel", **Then** the task returns to view mode without saving changes
4. **Given** a user edits a task title, **When** they leave it empty, **Then** they see a validation error "Task title is required"
5. **Given** a user edits a task, **When** they enter a title longer than 200 characters, **Then** they see a validation error "Title must be 200 characters or less"

---

### User Story 5 - Delete Tasks (Priority: P5)

An authenticated user wants to permanently remove tasks they no longer need from their list.

**Why this priority**: While useful for list management, users can tolerate having old tasks in their list. This is a nice-to-have feature that can be added after core functionality works.

**Independent Test**: Can be tested by creating tasks, deleting them, and verifying they are removed from both UI and database.

**Acceptance Scenarios**:

1. **Given** an authenticated user views a task, **When** they click a "Delete" button, **Then** they see a confirmation dialog "Are you sure you want to delete this task?"
2. **Given** a delete confirmation dialog, **When** the user clicks "Confirm", **Then** the task is permanently removed from the database and disappears from the UI
3. **Given** a delete confirmation dialog, **When** the user clicks "Cancel", **Then** the dialog closes and the task remains in the list
4. **Given** a user deletes a task, **When** they refresh the page, **Then** the deleted task does not reappear

---

### Edge Cases

- What happens when a user's JWT token expires while they are viewing tasks? (System should detect 401 response and redirect to sign-in page)
- What happens when two users have the same email address from different authentication providers? (Assume email is unique across the system; Better Auth handles this)
- What happens when the database connection is lost during task creation? (Backend returns 500 error, frontend shows "Unable to save task. Please try again.")
- What happens when a user tries to access another user's task by guessing the task ID in the URL? (Backend returns 404 Not Found to prevent information disclosure)
- What happens when a user submits a task with special characters or HTML in the title/description? (Frontend and backend sanitize input to prevent XSS; display as plain text)
- What happens when a user creates a task while offline? (Show error message "No internet connection. Please check your connection and try again.")
- What happens when concurrent requests try to update the same task? (Last write wins; database uses timestamp-based updates)
- What happens when a user's session expires mid-operation? (Backend returns 401, frontend catches this and redirects to sign-in with message "Session expired. Please sign in again.")

## Requirements *(mandatory)*

### Functional Requirements

**Authentication & Authorization:**

- **FR-001**: System MUST allow users to register with email and password
- **FR-002**: System MUST validate email format and password strength (minimum 8 characters)
- **FR-003**: System MUST hash passwords before storing (Better Auth handles this)
- **FR-004**: System MUST generate JWT tokens upon successful authentication
- **FR-005**: System MUST include JWT token in all API requests via Authorization header
- **FR-006**: System MUST validate JWT token signature and expiration for all protected endpoints
- **FR-007**: System MUST return 401 Unauthorized for invalid or missing tokens
- **FR-008**: Users MUST only be able to access their own tasks (user isolation enforced by backend)
- **FR-009**: System MUST allow users to log out and clear their session
- **FR-010**: JWT tokens MUST expire after 7 days (configurable in Better Auth)

**Task Management:**

- **FR-011**: System MUST allow authenticated users to create tasks with a title (required) and description (optional)
- **FR-012**: System MUST validate task title is not empty and does not exceed 200 characters
- **FR-013**: System MUST validate task description does not exceed 1000 characters
- **FR-014**: System MUST persist all tasks to the database
- **FR-015**: System MUST display only the authenticated user's tasks, filtered by user_id from JWT token
- **FR-016**: System MUST display tasks sorted by creation date (newest first)
- **FR-017**: System MUST allow users to mark tasks as complete or incomplete
- **FR-018**: System MUST allow users to edit task title and description
- **FR-019**: System MUST allow users to delete tasks with confirmation
- **FR-020**: System MUST update task modified timestamp when any field is changed
- **FR-021**: System MUST show empty state message when user has no tasks
- **FR-022**: System MUST visually distinguish completed tasks from incomplete tasks

**Data Integrity:**

- **FR-023**: All database operations MUST be atomic (transaction-based where applicable)
- **FR-024**: Backend MUST validate all input data using Pydantic models before processing
- **FR-025**: Frontend MUST validate all input data before submission
- **FR-026**: System MUST sanitize user input to prevent XSS attacks
- **FR-027**: Backend MUST use parameterized queries to prevent SQL injection (SQLModel handles this)
- **FR-028**: System MUST maintain referential integrity between users and tasks (foreign key constraints)

**Security:**

- **FR-029**: System MUST store BETTER_AUTH_SECRET in environment variables (never hardcoded)
- **FR-030**: Backend MUST validate BETTER_AUTH_SECRET matches frontend secret for JWT verification
- **FR-031**: System MUST configure CORS to allow only authorized origins (frontend URLs)
- **FR-032**: System MUST use HTTPS in production deployments
- **FR-033**: Backend MUST validate all environment variables on startup and fail fast if missing
- **FR-034**: System MUST return 404 (not 403) for unauthorized access attempts to prevent information disclosure
- **FR-035**: System MUST log authentication failures for security monitoring

### Key Entities

- **User**: Represents an application user with unique email address. Managed by Better Auth. Has one-to-many relationship with Tasks.
  - Attributes: id (string), email (unique), name, created_at timestamp
  - Relationships: owns multiple Tasks

- **Task**: Represents a todo item belonging to a single user.
  - Attributes: id (integer auto-increment), title (required, max 200 chars), description (optional, max 1000 chars), completed (boolean, default false), created_at timestamp, updated_at timestamp
  - Relationships: belongs to one User via user_id foreign key
  - Indexes: user_id (for efficient user filtering), completed (for status filtering)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete account registration in under 1 minute
- **SC-002**: Users can create a new task and see it appear in the list in under 5 seconds
- **SC-003**: Task list page loads all user tasks in under 2 seconds
- **SC-004**: 95% of task CRUD operations complete in under 500ms (API response time)
- **SC-005**: Users can successfully toggle task completion status without page refresh
- **SC-006**: 100% of user data is isolated - users can only see their own tasks, verified through security testing
- **SC-007**: Application functions correctly on mobile (320px width), tablet (768px), and desktop (1024px+) screen sizes
- **SC-008**: Users receive immediate visual feedback for all actions (loading states, success/error messages)
- **SC-009**: 90% of users successfully create their first task on first attempt without errors
- **SC-010**: System maintains data integrity - all task changes persist correctly after page refresh
- **SC-011**: Authentication failure rate is less than 1% for valid credentials (no false negatives)
- **SC-012**: Zero unauthorized data access incidents (user isolation is perfect)

### Assumptions

1. **Email Uniqueness**: We assume Better Auth enforces email uniqueness across the system
2. **Token Expiration**: JWT tokens expire after 7 days by default (Better Auth configuration)
3. **Password Security**: Better Auth handles password hashing using industry-standard algorithms (bcrypt or argon2)
4. **Database Availability**: Neon PostgreSQL provides 99.9% uptime on free tier
5. **CORS Configuration**: Development uses localhost:3000, production uses deployed Vercel URL
6. **Browser Support**: Application targets modern browsers (Chrome, Firefox, Safari, Edge - last 2 versions)
7. **Network Connectivity**: Users have stable internet connection (no offline support in Phase II)
8. **Concurrent Users**: System is designed for up to 1000 concurrent users on free tier infrastructure
9. **Data Retention**: User data and tasks are retained indefinitely unless user deletes their account
10. **Error Handling**: All API errors return JSON responses with user-friendly messages
11. **Deployment Strategy**: Frontend and backend deployed as separate Vercel projects with independent configuration and scaling
12. **Testing Approach**: Quality assurance performed through manual testing of documented acceptance scenarios; automated tests deferred to future phases

### Out of Scope (Phase II)

The following features are explicitly excluded from Phase II and will be considered for future phases:

- **Email verification** (Future) - Users can immediately use app after signup without verifying email
- **Third-party UI component libraries** (Phase II) - Use pure Tailwind CSS with custom components (no shadcn/ui, Material UI, Headless UI, etc.)
- **Refresh tokens** (Future) - Users must re-login after JWT token expires (7 days); no automatic token refresh
- **Automated testing** (Future) - Manual testing only in Phase II; unit tests, integration tests, and E2E tests deferred to future phases
- **Priorities and tags** (Phase V) - Task organization beyond completion status
- **Search and filter** (Phase V) - Finding tasks by keyword or filtering by status
- **Recurring tasks** (Phase V) - Tasks that repeat on a schedule
- **Due dates and reminders** (Phase V) - Time-based task management
- **Real-time sync** (Phase V) - Live updates across multiple devices
- **Task sharing/collaboration** (Future) - Multiple users working on same tasks
- **Rich text editing** (Future) - Formatting in task descriptions
- **File attachments** (Future) - Attaching documents to tasks
- **Subtasks** (Future) - Breaking tasks into smaller steps
- **Task history/audit log** (Future) - Tracking changes over time
- **Mobile native apps** (Future) - iOS/Android applications
- **Email notifications** (Future) - Alerts for task updates
- **Third-party integrations** (Future) - Calendar sync, Slack, etc.
- **Custom user settings** (Future) - Theme customization, preferences
- **Account recovery** (Future) - Password reset via email (assumes Better Auth provides this)

## Environment Configuration

### Required Environment Variables

The application requires specific environment variables for both frontend and backend to function correctly. These MUST be configured before deployment.

**Frontend Environment Variables:**

**Development (.env.local):**
```bash
# Better Auth Configuration
BETTER_AUTH_SECRET=<64-character-secret-generated-with-openssl>
BETTER_AUTH_URL=http://localhost:3000

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Production (.env.production):**
```bash
# Better Auth Configuration
BETTER_AUTH_SECRET=<production-64-character-secret>
BETTER_AUTH_URL=https://your-app.vercel.app

# API Configuration
NEXT_PUBLIC_API_URL=https://your-api.vercel.app
```

**Backend Environment Variables:**

**Development (.env):**
```bash
# Database
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Authentication - MUST match frontend secret
BETTER_AUTH_SECRET=<same-64-character-secret-as-frontend>

# CORS Configuration - comma-separated, no spaces
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Environment
ENVIRONMENT=development

# Logging
LOG_LEVEL=DEBUG
```

**Production (.env.production):**
```bash
# Database
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Authentication - MUST match frontend secret
BETTER_AUTH_SECRET=<same-production-secret-as-frontend>

# CORS Configuration - comma-separated, no spaces
CORS_ORIGINS=https://your-app.vercel.app,https://your-app-staging.vercel.app

# Environment
ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO
```

### Environment Variable Generation

**Generate BETTER_AUTH_SECRET:**
```bash
openssl rand -base64 48
```

**CRITICAL REQUIREMENTS:**
1. `BETTER_AUTH_SECRET` MUST be identical in frontend and backend .env files
2. `BETTER_AUTH_SECRET` MUST be at least 32 characters (recommend 64)
3. `CORS_ORIGINS` MUST include all frontend deployment URLs (production, staging, preview)
4. `CORS_ORIGINS` format: comma-separated list with NO spaces
5. Never commit `.env` files to version control (add to `.gitignore`)
6. Create `.env.example` files with dummy values as templates

### Startup Validation Requirements

**Backend Validation** (FastAPI must validate on startup):
- `DATABASE_URL` exists and is valid PostgreSQL connection string
- `BETTER_AUTH_SECRET` exists and is at least 32 characters
- `CORS_ORIGINS` exists and contains at least one valid origin
- Application MUST fail fast with clear error messages if validation fails

**Frontend Validation** (Next.js must validate on startup):
- `NEXT_PUBLIC_API_URL` exists and is valid URL
- `BETTER_AUTH_SECRET` exists and is at least 32 characters
- Application MUST fail fast with clear error messages if validation fails

### Example CORS Configuration

**Development:**
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Production:**
```bash
CORS_ORIGINS=https://todo-app.vercel.app,https://todo-app-staging.vercel.app,https://todo-app-preview-xyz.vercel.app
```

**Important Notes:**
- Include all Vercel preview deployment URLs if testing with preview branches
- Update CORS origins whenever new deployment URLs are added
- Backend will reject requests from origins not in the CORS_ORIGINS list

## Database Schema

### Tables

**users table** (Managed by Better Auth):
- `id`: string (primary key)
- `email`: string (unique, not null)
- `name`: string (nullable)
- `created_at`: timestamp (default: current timestamp)

**tasks table**:
- `id`: integer (primary key, auto-increment)
- `user_id`: string (foreign key � users.id, not null, on delete cascade)
- `title`: string (max 200 characters, not null)
- `description`: text (max 1000 characters, nullable)
- `completed`: boolean (default: false, not null)
- `created_at`: timestamp (default: current timestamp, not null)
- `updated_at`: timestamp (default: current timestamp, auto-update on modification, not null)

### Indexes

- **tasks.user_id**: B-tree index for efficient filtering by user (critical for user isolation queries)
- **tasks.completed**: B-tree index for filtering by completion status (optional performance optimization)
- **tasks.created_at**: B-tree index for sorting by creation date (performance optimization for default sort)

### Constraints

- **Primary Keys**: users.id, tasks.id
- **Foreign Keys**: tasks.user_id references users.id (on delete cascade - when user deleted, all their tasks deleted)
- **Unique Constraints**: users.email (enforced by Better Auth)
- **Not Null Constraints**: users.id, users.email, tasks.id, tasks.user_id, tasks.title, tasks.completed, tasks.created_at, tasks.updated_at
- **Check Constraints**:
  - tasks.title length > 0 AND length <= 200
  - tasks.description length <= 1000 (if not null)

### Data Relationships

```
users (1) ----< (many) tasks
  |
    One user owns many tasks
    Each task belongs to exactly one user
    Cascade delete: deleting user deletes all their tasks
```

## API Contract Overview

**Pattern**: `VERB /api/{user_id}/<resource>`

**Authentication**: All task endpoints require `Authorization: Bearer <jwt-token>` header

**Key Endpoints**:
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/signin` - Authenticate existing user
- `POST /api/auth/logout` - End user session
- `GET /api/{user_id}/tasks` - Retrieve all user tasks
- `POST /api/{user_id}/tasks` - Create new task
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task

**Note**: `{user_id}` in URL is for routing only; backend MUST validate user_id from JWT token matches requested resource.

**Status Codes**:
- `200 OK` - Successful GET/PUT/DELETE
- `201 Created` - Successful POST
- `400 Bad Request` - Client error (malformed request)
- `401 Unauthorized` - Missing or invalid JWT token
- `404 Not Found` - Resource not found OR user not authorized (prevents information disclosure)
- `422 Unprocessable Entity` - Validation error (Pydantic)
- `500 Internal Server Error` - Server error (log stack trace, return generic message)

**Response Format**: All responses are JSON with consistent structure:
```json
{
  "data": { ... },      // Success response
  "error": "message"    // Error response
}
```

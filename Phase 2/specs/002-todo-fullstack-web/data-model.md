# Data Model: Todo Full-Stack Web Application

**Feature**: `002-todo-fullstack-web` | **Date**: 2026-01-03
**Related Artifacts**: [spec.md](./spec.md), [plan.md](./plan.md), [research.md](./research.md)

## Overview

This document defines the database schema, entities, relationships, and constraints for the Todo Full-Stack Web Application. The data model supports user authentication via Better Auth and task management with strict user isolation.

**Database**: Neon PostgreSQL (serverless)
**ORM**: SQLModel (Pydantic + SQLAlchemy)
**Migration Strategy**: `SQLModel.metadata.create_all()` for Phase II (Alembic deferred to future phases)

---

## Entity-Relationship Diagram

```
┌─────────────────────────────────────────────┐
│               users                         │
│  (Managed by Better Auth)                   │
├─────────────────────────────────────────────┤
│  id: string (PK)                            │
│  email: string (UNIQUE, NOT NULL)           │
│  name: string (NULLABLE)                    │
│  created_at: timestamp                      │
└───────────┬─────────────────────────────────┘
            │ 1
            │
            │ owns
            │
            │ many
            ▼
┌─────────────────────────────────────────────┐
│               tasks                         │
├─────────────────────────────────────────────┤
│  id: integer (PK, AUTO_INCREMENT)           │
│  user_id: string (FK → users.id, NOT NULL)  │
│  title: string (NOT NULL, MAX 200)          │
│  description: text (NULLABLE, MAX 1000)     │
│  completed: boolean (NOT NULL, DEFAULT false)│
│  created_at: timestamp (NOT NULL)           │
│  updated_at: timestamp (NOT NULL)           │
└─────────────────────────────────────────────┘

Indexes:
- idx_user_id: B-tree on user_id (user isolation queries)
- idx_user_completed: B-tree on (user_id, completed) (filtered queries)
- idx_created_at: B-tree on created_at (sorting)

Constraints:
- FK: tasks.user_id → users.id (ON DELETE CASCADE)
- CHECK: length(title) > 0 AND length(title) <= 200
- CHECK: description IS NULL OR length(description) <= 1000
```

---

## Entities

### 1. User Entity

**Management**: Fully managed by Better Auth library. No custom implementation required.

**Purpose**: Represents an authenticated application user. Better Auth handles registration, password hashing, email verification (disabled in Phase II), and session management.

**Attributes**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | string (UUID or Better Auth ID format) | PRIMARY KEY, NOT NULL | Unique user identifier |
| `email` | string (varchar) | UNIQUE, NOT NULL | User email address (login credential) |
| `name` | string (varchar) | NULLABLE | User display name (optional) |
| `created_at` | timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

**Managed By**: Better Auth library (no SQLModel definition needed in our codebase)

**Better Auth Schema**: Better Auth automatically creates and manages the users table via its internal migration system.

**Relationships**:
- **One-to-many** with Task: One user owns many tasks

**Business Rules**:
- Email must be unique across all users
- Password must be at least 8 characters (enforced by Better Auth)
- Email format validation handled by Better Auth
- No email verification required in Phase II (users can immediately login after signup)

---

### 2. Task Entity

**Purpose**: Represents a todo item belonging to a specific user. Core entity for task management functionality.

**SQLModel Definition**:

```python
# app/models/task.py
from sqlmodel import Field, SQLModel, Index
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """Task entity for todo items."""
    __tablename__ = "tasks"
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_user_completed", "user_id", "completed"),
        Index("idx_created_at", "created_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

**Attributes**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | integer | PRIMARY KEY, AUTO_INCREMENT | Unique task identifier |
| `user_id` | string | FOREIGN KEY → users.id, NOT NULL, INDEX | Owner of the task (user isolation) |
| `title` | varchar(200) | NOT NULL, LENGTH 1-200 | Task title (required) |
| `description` | text | NULLABLE, MAX LENGTH 1000 | Optional detailed description |
| `completed` | boolean | NOT NULL, DEFAULT false | Completion status |
| `created_at` | timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Last modification timestamp |

**Relationships**:
- **Many-to-one** with User: Each task belongs to exactly one user

**Business Rules**:
- Title is required and cannot be empty
- Title max length is 200 characters (validation in frontend and backend)
- Description is optional (can be null)
- Description max length is 1000 characters when provided
- Completed defaults to false (new tasks are incomplete)
- updated_at automatically updates when any field changes
- Deleting a user cascades to delete all their tasks (data cleanup)

**State Transitions**:

```
┌─────────────┐
│ Task Created│
│completed=false│
└──────┬──────┘
       │
       ▼
┌─────────────┐         ┌─────────────┐
│ Incomplete  │◄───────►│  Complete   │
│completed=false│  toggle  │completed=true│
└─────────────┘         └─────────────┘
       │                      │
       └──────────┬───────────┘
                  ▼
            ┌──────────┐
            │ Deleted  │
            └──────────┘
```

---

## Relationships

### User → Tasks (One-to-Many)

**Type**: One-to-many
**Cardinality**: 1 user : 0..* tasks
**Foreign Key**: tasks.user_id → users.id
**Delete Behavior**: CASCADE (deleting user deletes all their tasks)

**Rationale**:
- Each task belongs to exactly one user (no shared tasks in Phase II)
- Users can have unlimited tasks (practical limit: ~100k per user on Neon free tier)
- Cascade delete ensures no orphaned tasks when user account deleted
- Enforces data privacy and user isolation principle

**Query Patterns**:

```python
# Get all tasks for a user (most common query)
tasks = session.exec(
    select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
).all()

# Get incomplete tasks for a user
incomplete_tasks = session.exec(
    select(Task)
    .where(Task.user_id == user_id, Task.completed == False)
    .order_by(Task.created_at.desc())
).all()

# Get complete tasks for a user
complete_tasks = session.exec(
    select(Task)
    .where(Task.user_id == user_id, Task.completed == True)
    .order_by(Task.created_at.desc())
).all()
```

---

## Indexes

Indexes are critical for query performance, especially for user isolation queries that filter by `user_id`.

### Index 1: idx_user_id

**Type**: B-tree
**Columns**: `user_id`
**Purpose**: Optimize user isolation queries (most frequent query pattern)

**Covers Queries**:
```sql
SELECT * FROM tasks WHERE user_id = 'user_123';
```

**Estimated Performance**:
- Without index: O(n) full table scan
- With index: O(log n) index seek
- Expected improvement: 100x faster for 10k tasks

---

### Index 2: idx_user_completed (Composite)

**Type**: B-tree
**Columns**: `user_id`, `completed`
**Purpose**: Optimize filtered queries (e.g., "show only incomplete tasks")

**Covers Queries**:
```sql
SELECT * FROM tasks WHERE user_id = 'user_123' AND completed = false;
```

**Estimated Performance**:
- Without index: O(n) table scan after user_id filter
- With index: O(log n) index seek
- Expected improvement: 50x faster for users with mixed completed/incomplete tasks

---

### Index 3: idx_created_at

**Type**: B-tree
**Columns**: `created_at`
**Purpose**: Optimize sorting by creation date (default sort order)

**Covers Queries**:
```sql
SELECT * FROM tasks WHERE user_id = 'user_123' ORDER BY created_at DESC;
```

**Note**: PostgreSQL query planner will use `idx_user_id` for filtering, then sort in memory. This index is optional but improves performance for large result sets.

---

## Constraints

### Primary Keys

- `users.id` (string, managed by Better Auth)
- `tasks.id` (integer, auto-increment)

**Rationale**: Unique identifiers for each entity. Integer primary key for tasks provides sequential ordering and efficient indexing.

---

### Foreign Keys

**Constraint**: `tasks.user_id → users.id`

**On Delete**: `CASCADE`
**On Update**: `CASCADE` (default)

**Purpose**: Referential integrity. Ensures every task belongs to an existing user.

**Behavior**:
- Inserting task with non-existent user_id: **FAILS** with foreign key violation
- Deleting user: **CASCADES** to delete all their tasks automatically
- Updating user.id: **CASCADES** to update tasks.user_id (rare, Better Auth doesn't change user IDs)

**Rationale**:
- Cascade delete ensures no orphaned tasks (data cleanup)
- Prevents referential integrity violations
- Simplifies user account deletion logic (no manual task cleanup needed)

---

### Unique Constraints

**Constraint**: `users.email UNIQUE`

**Purpose**: Ensures one account per email address

**Managed By**: Better Auth

**Rationale**: Email is the login credential; duplicates would cause authentication ambiguity.

---

### Check Constraints

**Constraint 1**: `CHECK (length(title) > 0 AND length(title) <= 200)`

**Purpose**: Validates task title is not empty and within length limit

**Enforcement**: Database level (PostgreSQL)

**Rationale**:
- Prevents empty titles (usability: tasks must have descriptive titles)
- Enforces constitutional simplicity (max 200 chars keeps UI readable)

---

**Constraint 2**: `CHECK (description IS NULL OR length(description) <= 1000)`

**Purpose**: Validates optional description length

**Enforcement**: Database level (PostgreSQL)

**Rationale**:
- Allows null descriptions (optional field)
- Prevents excessively long descriptions (performance and UX)

---

### Not Null Constraints

**Applied To**:
- `tasks.user_id` - Every task must belong to a user
- `tasks.title` - Every task must have a title
- `tasks.completed` - Completion status must be explicit (true/false)
- `tasks.created_at` - Creation timestamp required for auditing and sorting
- `tasks.updated_at` - Modification timestamp required for auditing

**Rationale**: Ensures data integrity and prevents ambiguous states.

---

## Default Values

| Column | Default Value | Rationale |
|--------|---------------|-----------|
| `tasks.id` | AUTO_INCREMENT | Database-generated unique identifier |
| `tasks.completed` | `false` | New tasks start as incomplete |
| `tasks.created_at` | `CURRENT_TIMESTAMP` | Automatically set on insert |
| `tasks.updated_at` | `CURRENT_TIMESTAMP` | Automatically set on insert and update |

---

## Data Validation

### Backend Validation (Pydantic Schemas)

```python
# app/schemas/task.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None

    @validator('title')
    def title_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip() if v else v

class TaskResponse(BaseModel):
    """Schema for task API responses."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode for SQLModel compatibility
```

### Frontend Validation (TypeScript)

```typescript
// lib/types.ts
export interface Task {
  id: number
  user_id: string
  title: string
  description: string | null
  completed: boolean
  created_at: string  // ISO 8601 timestamp
  updated_at: string
}

export interface TaskCreate {
  title: string
  description?: string
}

export interface TaskUpdate {
  title?: string
  description?: string
  completed?: boolean
}

// Validation functions
export function validateTaskTitle(title: string): string | null {
  if (!title.trim()) {
    return "Title cannot be empty"
  }
  if (title.length > 200) {
    return "Title must be 200 characters or less"
  }
  return null
}

export function validateTaskDescription(description: string): string | null {
  if (description.length > 1000) {
    return "Description must be 1000 characters or less"
  }
  return null
}
```

---

## Migration Strategy

### Phase II Approach: SQLModel.metadata.create_all()

**Implementation**:

```python
# app/database.py
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.models.task import Task  # Import to register with SQLModel

async def create_db_and_tables():
    """Create all database tables defined by SQLModel."""
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=settings.ENVIRONMENT == "development"
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

**Call on Startup**:

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    await create_db_and_tables()
    yield
    # Shutdown: Cleanup (none needed)

app = FastAPI(lifespan=lifespan)
```

**Rationale**:
- Simple approach for greenfield project (no existing schema to migrate)
- No Alembic overhead (deferred to future phases when schema changes become frequent)
- Tables created automatically on first deployment
- Idempotent: Safe to run multiple times (no error if tables already exist)

### Future: Alembic Migrations (Phase III+)

**When to adopt**:
- Multiple developers making schema changes
- Need for rollback capability
- Schema changes in production requiring zero-downtime deployments

**Migration**:
1. Install Alembic: `uv add alembic`
2. Initialize: `alembic init migrations`
3. Auto-generate initial migration from current schema: `alembic revision --autogenerate -m "initial"`
4. Apply migrations: `alembic upgrade head`

---

## Data Security & Privacy

### User Isolation Enforcement

**Critical Requirement**: Users must NEVER access other users' data.

**Enforcement Points**:

1. **Database Level**: All queries filter by `user_id from JWT token
2. **API Level**: Route handlers validate `user_id` in URL matches authenticated user
3. **Frontend Level**: UI only displays current user's data

**Example (Backend Route)**:

```python
@router.get("/api/{user_id}/tasks", response_model=list[TaskResponse])
async def get_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user),  # From JWT
    session: AsyncSession = Depends(get_session)
):
    # CRITICAL: Validate user_id in URL matches authenticated user
    if user_id != current_user_id:
        raise HTTPException(status_code=404, detail="Not found")  # Return 404, not 403

    # Query with authenticated user_id (NEVER use user_id from URL for filtering)
    tasks = await session.exec(
        select(Task).where(Task.user_id == current_user_id)
    ).all()

    return tasks
```

**Why 404 instead of 403?**
- Prevents information disclosure (403 reveals resource exists but user lacks access)
- Constitutional requirement: Security First principle

---

### Data Retention

**Policy**: User data and tasks retained indefinitely unless user deletes account.

**Account Deletion**:
- Deleting user account cascades to delete all tasks (referential integrity)
- Better Auth handles user record deletion
- No soft deletes in Phase II (hard delete only)

**Future Considerations** (Out of Scope):
- Soft delete with `deleted_at` timestamp
- Data export before account deletion (GDPR compliance)
- Retention policies (auto-delete after X days of inactivity)

---

## Performance Considerations

### Query Optimization

**Most Frequent Query**: Get all tasks for a user
```sql
SELECT * FROM tasks WHERE user_id = 'user_123' ORDER BY created_at DESC;
```

**Optimization**:
- `idx_user_id` provides O(log n) seek on user_id
- PostgreSQL sorts in memory (acceptable for <1000 tasks per user)
- Consider `idx_created_at` if users have >10k tasks

**Expected Performance**:
- 100 tasks: < 10ms
- 1,000 tasks: < 50ms
- 10,000 tasks: < 200ms (still under 500ms target)

---

### Database Connection Pooling

**Configuration**:
```python
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=5,       # Base connections
    max_overflow=10,   # Additional under load
    pool_pre_ping=True # Health check before use
)
```

**Rationale**:
- Neon free tier supports up to 100 connections
- pool_size=5 sufficient for typical load (<100 req/s)
- max_overflow=10 handles traffic spikes
- pool_pre_ping prevents stale connection errors

---

## Testing Data Model

### Manual Testing Checklist

**User Isolation Tests**:
1. Create User A and User B
2. User A creates Task 1
3. User B attempts to access Task 1 (should return 404)
4. User A can access Task 1 (should return task)

**Referential Integrity Tests**:
1. Create user and tasks
2. Delete user
3. Verify tasks are also deleted (cascade)

**Constraint Tests**:
1. Attempt to create task with empty title (should fail)
2. Attempt to create task with 201-character title (should fail)
3. Create task with 1001-character description (should fail)
4. Create task with null description (should succeed)

---

## Summary

**Entities**: 2 (User, Task)
**Relationships**: 1 (User → Task, one-to-many)
**Indexes**: 3 (user_id, user_id+completed, created_at)
**Constraints**: Foreign key with cascade delete, check constraints on title/description lengths
**Migration**: SQLModel.metadata.create_all() for Phase II

**Data Model Status**: ✅ Complete and ready for implementation

**Next Step**: Generate API contracts in [contracts/](./contracts/)

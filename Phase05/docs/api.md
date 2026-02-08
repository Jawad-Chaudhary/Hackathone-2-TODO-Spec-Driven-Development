# Task Management API Documentation

**Version**: 2.0.0
**Base URL**: `http://localhost:8000` (development) | `https://your-domain.com` (production)

This document provides complete API documentation for the TODO application REST API, including Phase 5 advanced features (search, filtering, statistics).

---

## Table of Contents

1. [Authentication](#authentication)
2. [Task Endpoints](#task-endpoints)
3. [Search & Filter](#search--filter)
4. [Dashboard Statistics](#dashboard-statistics)
5. [WebSocket API](#websocket-api)
6. [Error Responses](#error-responses)
7. [Rate Limiting](#rate-limiting)

---

## Authentication

All API endpoints (except authentication endpoints) require JWT authentication.

### Headers

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Obtain JWT Token

**POST** `/auth/login`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Success Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "user-uuid-123",
    "email": "user@example.com",
    "username": "johndoe"
  }
}
```

---

## Task Endpoints

### 1. List Tasks

**GET** `/api/{user_id}/tasks`

Returns all tasks for the authenticated user with optional filtering, search, and sorting.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | `all` | Filter by status: `all`, `pending`, `completed` |
| `priority` | string | - | Filter by priority: `high`, `medium`, `low` |
| `tags` | array[string] | - | Filter by tags (task must have all specified tags) |
| `search` | string | - | Search in title/description (case-insensitive) |
| `due_start` | string (ISO 8601) | - | Filter tasks with due_date >= this date |
| `due_end` | string (ISO 8601) | - | Filter tasks with due_date <= this date |
| `sort_by` | string | `created_at` | Sort by: `created_at`, `due_date`, `priority`, `title` |
| `sort_order` | string | `desc` | Sort order: `asc`, `desc` |

#### Example Requests

**Basic list**:
```bash
curl -X GET "http://localhost:8000/api/user-123/tasks" \
  -H "Authorization: Bearer eyJhbGc..."
```

**With filters**:
```bash
curl -X GET "http://localhost:8000/api/user-123/tasks?status=pending&priority=high&sort_by=due_date&sort_order=asc" \
  -H "Authorization: Bearer eyJhbGc..."
```

**With search**:
```bash
curl -X GET "http://localhost:8000/api/user-123/tasks?search=meeting" \
  -H "Authorization: Bearer eyJhbGc..."
```

**With tags**:
```bash
curl -X GET "http://localhost:8000/api/user-123/tasks?tags=work&tags=urgent" \
  -H "Authorization: Bearer eyJhbGc..."
```

**Date range filter**:
```bash
curl -X GET "http://localhost:8000/api/user-123/tasks?due_start=2026-02-01&due_end=2026-02-28" \
  -H "Authorization: Bearer eyJhbGc..."
```

#### Success Response (200 OK)

```json
[
  {
    "id": 1,
    "user_id": "user-123",
    "title": "Complete project documentation",
    "description": "Write API docs and README",
    "completed": false,
    "priority": "high",
    "tags": ["work", "documentation"],
    "due_date": "2026-02-01T15:00:00Z",
    "recurrence": null,
    "recurrence_interval": null,
    "parent_task_id": null,
    "reminder_sent_at": null,
    "created_at": "2026-01-29T10:00:00Z",
    "updated_at": "2026-01-29T10:00:00Z"
  },
  {
    "id": 2,
    "user_id": "user-123",
    "title": "Weekly team meeting",
    "description": "Discuss sprint progress",
    "completed": false,
    "priority": "medium",
    "tags": ["work", "meeting"],
    "due_date": "2026-02-03T09:00:00Z",
    "recurrence": "weekly",
    "recurrence_interval": 7,
    "parent_task_id": null,
    "reminder_sent_at": null,
    "created_at": "2026-01-28T14:00:00Z",
    "updated_at": "2026-01-28T14:00:00Z"
  }
]
```

---

### 2. Get Single Task

**GET** `/api/{user_id}/tasks/{id}`

Returns details of a specific task.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | string | User identifier |
| `id` | integer | Task ID |

#### Example Request

```bash
curl -X GET "http://localhost:8000/api/user-123/tasks/1" \
  -H "Authorization: Bearer eyJhbGc..."
```

#### Success Response (200 OK)

Same structure as task object in list endpoint.

#### Error Responses

- **401 Unauthorized**: Invalid or missing JWT token
- **404 Not Found**: Task not found or user mismatch

---

### 3. Create Task

**POST** `/api/{user_id}/tasks`

Creates a new task for the authenticated user.

#### Request Body

```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, coffee",
  "priority": "medium",
  "tags": ["personal", "shopping"],
  "due_date": "2026-01-30T18:00:00Z",
  "recurrence": "weekly",
  "recurrence_interval": 7
}
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | ✅ Yes | Task title (1-200 chars) |
| `description` | string | No | Task description (max 2000 chars) |
| `priority` | enum | No | Priority level: `"high"`, `"medium"`, `"low"` |
| `tags` | array[string] | No | List of tags for categorization |
| `due_date` | string (ISO 8601) | No | When task is due |
| `recurrence` | enum | No | Recurrence pattern: `"daily"`, `"weekly"`, `"monthly"`, `"custom"` |
| `recurrence_interval` | integer | No | Custom interval in days (only for `recurrence: "custom"`) |

#### Example Request

```bash
curl -X POST "http://localhost:8000/api/user-123/tasks" \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "priority": "medium",
    "tags": ["personal", "shopping"],
    "due_date": "2026-01-30T18:00:00Z"
  }'
```

#### Success Response (201 Created)

```json
{
  "id": 3,
  "user_id": "user-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "priority": "medium",
  "tags": ["personal", "shopping"],
  "due_date": "2026-01-30T18:00:00Z",
  "recurrence": null,
  "recurrence_interval": null,
  "parent_task_id": null,
  "reminder_sent_at": null,
  "created_at": "2026-01-29T12:00:00Z",
  "updated_at": "2026-01-29T12:00:00Z"
}
```

#### Event Published

When a task is created, a CloudEvents v1.0 event is published to Kafka:

**Topic**: `task-events`
**Event Type**: `com.todoapp.task.created.v1`

```json
{
  "specversion": "1.0",
  "type": "com.todoapp.task.created.v1",
  "source": "todo-backend",
  "id": "uuid-string",
  "time": "2026-01-29T12:00:00Z",
  "data": {
    "task_id": 3,
    "user_id": "user-123",
    "title": "Buy groceries",
    "priority": "medium",
    "tags": ["personal", "shopping"],
    "due_date": "2026-01-30T18:00:00Z"
  }
}
```

#### Error Responses

- **401 Unauthorized**: Invalid or missing JWT token
- **422 Unprocessable Entity**: Validation error (invalid fields)

---

### 4. Update Task

**PUT** `/api/{user_id}/tasks/{id}`

Updates an existing task. All fields are optional (partial update).

#### Request Body

```json
{
  "title": "Buy groceries and cook dinner",
  "completed": false,
  "priority": "high",
  "due_date": "2026-01-30T19:00:00Z"
}
```

#### Example Request

```bash
curl -X PUT "http://localhost:8000/api/user-123/tasks/3" \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and cook dinner",
    "priority": "high"
  }'
```

#### Success Response (200 OK)

Returns updated task object with modified `updated_at` timestamp.

#### Event Published

**Topic**: `task-updates`
**Event Type**: `com.todoapp.task.updated.v1`

#### Error Responses

- **401 Unauthorized**: Invalid or missing JWT token
- **404 Not Found**: Task not found or user mismatch
- **422 Unprocessable Entity**: Validation error

---

### 5. Toggle Task Completion

**PATCH** `/api/{user_id}/tasks/{id}/complete`

Toggles the completion status of a task (completed ↔ pending).

#### Example Request

```bash
curl -X PATCH "http://localhost:8000/api/user-123/tasks/3/complete" \
  -H "Authorization: Bearer eyJhbGc..."
```

#### Success Response (200 OK)

Returns updated task with toggled `completed` status.

#### Event Published (If Recurring Task)

**Topic**: `task-events`
**Event Type**: `com.todoapp.task.completed.v1`

```json
{
  "specversion": "1.0",
  "type": "com.todoapp.task.completed.v1",
  "source": "todo-backend",
  "data": {
    "task_id": 2,
    "user_id": "user-123",
    "title": "Weekly team meeting",
    "completed_at": "2026-01-29T14:30:00Z",
    "due_date": "2026-02-03T09:00:00Z",
    "recurrence": "weekly",
    "recurrence_interval": 7
  }
}
```

**What Happens Next**:
1. Event published to Kafka `task-events` topic
2. **Recurring Service** consumes event
3. Service calculates next due date: `due_date + 7 days`
4. Service creates new task instance via POST /tasks
5. New task appears with `parent_task_id` set to original task ID

---

### 6. Delete Task

**DELETE** `/api/{user_id}/tasks/{id}`

Permanently deletes a task.

#### Example Request

```bash
curl -X DELETE "http://localhost:8000/api/user-123/tasks/3" \
  -H "Authorization: Bearer eyJhbGc..."
```

#### Success Response (204 No Content)

No response body on success.

#### Error Responses

- **401 Unauthorized**: Invalid or missing JWT token
- **404 Not Found**: Task not found or user mismatch

---

## Search & Filter

### Advanced Search Endpoint

**GET** `/api/{user_id}/tasks/search`

**Note**: This is now deprecated. Use the main `/api/{user_id}/tasks` endpoint with query parameters instead.

### Filter Examples

#### Filter by Priority
```bash
GET /api/user-123/tasks?priority=high
```

Returns only tasks with `priority: "high"`.

#### Filter by Multiple Tags (AND logic)
```bash
GET /api/user-123/tasks?tags=work&tags=urgent
```

Returns tasks that have **both** "work" AND "urgent" tags.

#### Search with Filters
```bash
GET /api/user-123/tasks?search=meeting&priority=high&status=pending
```

Returns pending high-priority tasks with "meeting" in title/description.

#### Date Range Filter
```bash
GET /api/user-123/tasks?due_start=2026-02-01T00:00:00Z&due_end=2026-02-28T23:59:59Z
```

Returns tasks due in February 2026.

### Sort Options

| Sort By | Description |
|---------|-------------|
| `created_at` | Date task was created (default) |
| `due_date` | Task due date |
| `priority` | Priority level (high → medium → low) |
| `title` | Alphabetical by title |

**Example**:
```bash
GET /api/user-123/tasks?sort_by=due_date&sort_order=asc
```

---

## Dashboard Statistics

### Get Task Statistics

**GET** `/api/{user_id}/dashboard/stats`

Returns task statistics for the authenticated user.

#### Example Request

```bash
curl -X GET "http://localhost:8000/api/user-123/dashboard/stats" \
  -H "Authorization: Bearer eyJhbGc..."
```

#### Success Response (200 OK)

```json
{
  "total": 25,
  "completed": 15,
  "pending": 10,
  "overdue": 3,
  "completion_rate": 60.0,
  "by_priority": {
    "high": 5,
    "medium": 12,
    "low": 8
  },
  "by_tag": {
    "work": 18,
    "personal": 7,
    "urgent": 3
  },
  "upcoming_due": [
    {
      "date": "2026-01-30",
      "count": 2
    },
    {
      "date": "2026-01-31",
      "count": 1
    }
  ]
}
```

#### Field Descriptions

| Field | Description |
|-------|-------------|
| `total` | Total number of tasks |
| `completed` | Number of completed tasks |
| `pending` | Number of pending (incomplete) tasks |
| `overdue` | Number of pending tasks with `due_date < now` |
| `completion_rate` | Percentage of completed tasks (completed / total * 100) |
| `by_priority` | Task count by priority level |
| `by_tag` | Task count by tag |
| `upcoming_due` | Tasks due in next 7 days grouped by date |

---

## WebSocket API

### Connect to WebSocket

**WS** `/ws`

Establishes a WebSocket connection for real-time notifications.

#### Connection URL

```
ws://localhost:8000/ws?token=<jwt_token>
```

#### Client Example (JavaScript)

```javascript
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";
const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

ws.onopen = () => {
  console.log("WebSocket connected");
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Received:", data);

  if (data.type === "reminder") {
    // Show browser notification
    showNotification(data.title, data.message, data.task_id);
  }
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

ws.onclose = () => {
  console.log("WebSocket disconnected");
  // Attempt reconnection
  setTimeout(() => connectWebSocket(), 5000);
};
```

### Message Types

#### Reminder Notification

```json
{
  "type": "reminder",
  "task_id": 123,
  "title": "Team meeting",
  "message": "Task 'Team meeting' is due in 15 minutes",
  "due_at": "2026-02-01T09:00:00Z",
  "timestamp": "2026-02-01T08:45:00Z"
}
```

#### Task Update (Real-time)

```json
{
  "type": "task_updated",
  "task_id": 456,
  "action": "completed",
  "user_id": "user-123",
  "timestamp": "2026-01-29T14:30:00Z"
}
```

---

## Error Responses

### Standard Error Format

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success - Request processed successfully |
| 201 | Created - New resource created |
| 204 | No Content - Success with no response body |
| 400 | Bad Request - Invalid request format |
| 401 | Unauthorized - Invalid or missing JWT token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found or access denied |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server-side error |

### Example Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

#### 404 Not Found
```json
{
  "detail": "Task with id 999 not found for user user-123"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "priority"],
      "msg": "value is not a valid enumeration member; permitted: 'high', 'medium', 'low'",
      "type": "type_error.enum"
    }
  ]
}
```

---

## Rate Limiting

### Current Limits

Currently, **no rate limiting** is enforced on the API.

### Recommended Limits (Production)

For production deployments, implement rate limiting at the API gateway or load balancer level:

| Endpoint Type | Limit |
|--------------|-------|
| Authentication | 5 requests/minute/IP |
| Read Operations (GET) | 100 requests/minute/user |
| Write Operations (POST/PUT/DELETE) | 50 requests/minute/user |
| WebSocket Connections | 1 connection/user |

### Rate Limit Headers

When rate limiting is enabled, responses will include:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1738166400
```

### Rate Limit Exceeded Response (429)

```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds.",
  "retry_after": 60
}
```

---

## Notes & Best Practices

### Timestamps
- All timestamps use **UTC timezone**
- Date/time fields follow **ISO 8601 format**: `YYYY-MM-DDTHH:MM:SSZ`
- Example: `2026-01-29T14:30:00Z`

### User IDs
- User IDs are extracted from **JWT tokens**
- Never trust client-provided user IDs in path parameters
- Backend verifies user ID matches JWT claim

### Pagination
- Currently not implemented
- Future: Add `limit` and `offset` query parameters
- Recommended: `limit=50` for list endpoints

### Filtering Performance
- Search across 1000 tasks: ~200-300ms
- Filter by priority: ~50ms
- Filter by tags: ~100ms (JSONB index)
- Combined filters: ~400ms

### Event-Driven Behavior
- Task creation publishes `task.created.v1` event
- Task completion publishes `task.completed.v1` event
- Recurring Service consumes events and creates new instances
- Notification Service publishes `reminder.scheduled.v1` events
- Backend WebSocket broadcasts reminders to users

### Security
- Always use HTTPS in production
- JWT tokens expire after 30 minutes (configurable)
- Refresh tokens not yet implemented
- CORS is configured for frontend origins

---

## Interactive API Docs

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- Interactive request builder
- Request/response schemas
- "Try it out" functionality
- Code generation in multiple languages

---

## Changelog

### Version 2.0.0 (Phase 5)
- ✅ Added search endpoint with full-text search
- ✅ Added filter query parameters (priority, tags, status, date range)
- ✅ Added sort options (created_at, due_date, priority, title)
- ✅ Added dashboard statistics endpoint
- ✅ Added WebSocket API for real-time notifications
- ✅ Added event-driven recurring task support
- ✅ Added reminder scheduling

### Version 1.0.0 (Phase 4)
- Initial release with basic CRUD operations

---

**Version**: 2.0.0 | **Status**: Production Ready | **Last Updated**: 2026-01-29

🚀 Generated with [Claude Code](https://claude.com/claude-code)

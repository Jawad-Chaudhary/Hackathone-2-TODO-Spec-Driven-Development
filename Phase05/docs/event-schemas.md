# Event Schemas Documentation

**Task**: T136 | **Purpose**: CloudEvents v1.0 format event schemas for Phase 5 event-driven architecture

This document defines all event schemas used in the TODO application's event-driven architecture. All events follow the [CloudEvents v1.0 specification](https://cloudevents.io/).

---

## CloudEvents v1.0 Format

All events published to Kafka (via Dapr Pub/Sub) use CloudEvents v1.0 format:

```json
{
  "specversion": "1.0",
  "type": "com.todoapp.task.created.v1",
  "source": "todo-backend",
  "id": "uuid-string",
  "time": "2026-01-29T10:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    // Event-specific payload
  }
}
```

### Required CloudEvents Attributes

- **specversion**: Always "1.0"
- **type**: Event type in reverse-DNS format (e.g., `com.todoapp.task.created.v1`)
- **source**: Service that published the event (e.g., `todo-backend`)
- **id**: Unique identifier (UUID v4)

### Optional CloudEvents Attributes

- **time**: ISO 8601 timestamp when event occurred
- **datacontenttype**: MIME type of `data` field (always `application/json`)
- **subject**: Resource identifier (e.g., `tasks/123`)

---

## Event Types

### 1. Task Created Event

**Type**: `com.todoapp.task.created.v1`
**Topic**: `task-events`
**Publisher**: `todo-backend`
**Subscribers**: None (logged for analytics)

**Purpose**: Published when a new task is created by a user.

#### Schema

```json
{
  "specversion": "1.0",
  "type": "com.todoapp.task.created.v1",
  "source": "todo-backend",
  "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
  "time": "2026-01-29T10:00:00Z",
  "subject": "tasks/123",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "user_id": "user-uuid-456",
    "title": "Complete project proposal",
    "description": "Finalize Q1 proposal with budget breakdown",
    "priority": "high",
    "tags": ["work", "deadline"],
    "due_date": "2026-02-01T17:00:00Z",
    "recurrence": "weekly",
    "recurrence_interval": null,
    "created_at": "2026-01-29T10:00:00Z"
  }
}
```

#### Data Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | integer | Yes | Unique task identifier |
| `user_id` | string | Yes | User who created the task |
| `title` | string | Yes | Task title (max 200 chars) |
| `description` | string | No | Task description (max 2000 chars) |
| `priority` | enum | No | Priority level: `"high"`, `"medium"`, `"low"` |
| `tags` | array[string] | No | Task tags/labels |
| `due_date` | string (ISO 8601) | No | When task is due |
| `recurrence` | enum | No | Recurrence pattern: `"daily"`, `"weekly"`, `"monthly"`, `"custom"` |
| `recurrence_interval` | integer | No | Custom interval in days (only for `recurrence: "custom"`) |
| `created_at` | string (ISO 8601) | Yes | When task was created |

---

### 2. Task Completed Event

**Type**: `com.todoapp.task.completed.v1`
**Topic**: `task-events`
**Publisher**: `todo-backend`
**Subscribers**: `todo-recurring-service` (creates next recurring task instance)

**Purpose**: Published when a user marks a task as completed. Triggers recurring task creation if the task has a recurrence pattern.

#### Schema

```json
{
  "specversion": "1.0",
  "type": "com.todoapp.task.completed.v1",
  "source": "todo-backend",
  "id": "b1ffdc88-8d1c-5fg9-cc7e-7cc0ce491b22",
  "time": "2026-01-29T14:30:00Z",
  "subject": "tasks/123",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "user_id": "user-uuid-456",
    "title": "Complete project proposal",
    "completed_at": "2026-01-29T14:30:00Z",
    "due_date": "2026-02-01T17:00:00Z",
    "recurrence": "weekly",
    "recurrence_interval": null,
    "parent_task_id": null
  }
}
```

#### Data Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | integer | Yes | Unique task identifier |
| `user_id` | string | Yes | User who completed the task |
| `title` | string | Yes | Task title (copied to new recurring instance) |
| `completed_at` | string (ISO 8601) | Yes | When task was marked complete |
| `due_date` | string (ISO 8601) | No | Original due date (used to calculate next due date) |
| `recurrence` | enum | No | Recurrence pattern (triggers recurring-service if present) |
| `recurrence_interval` | integer | No | Custom interval for next task |
| `parent_task_id` | integer | No | ID of original recurring task (null for first instance) |

---

### 3. Task Updated Event

**Type**: `com.todoapp.task.updated.v1`
**Topic**: `task-updates`
**Publisher**: `todo-backend`
**Subscribers**: None (logged for analytics)

**Purpose**: Published when a task's details are modified (title, description, priority, tags, due date).

#### Schema

```json
{
  "specversion": "1.0",
  "type": "com.todoapp.task.updated.v1",
  "source": "todo-backend",
  "id": "c2gged99-9e2d-6hi0-dd8f-8dd1df502c33",
  "time": "2026-01-29T15:45:00Z",
  "subject": "tasks/123",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "user_id": "user-uuid-456",
    "updated_fields": ["priority", "due_date"],
    "updated_at": "2026-01-29T15:45:00Z"
  }
}
```

#### Data Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | integer | Yes | Unique task identifier |
| `user_id` | string | Yes | User who updated the task |
| `updated_fields` | array[string] | Yes | List of fields that were changed |
| `updated_at` | string (ISO 8601) | Yes | When task was updated |

---

### 4. Reminder Scheduled Event

**Type**: `com.todoapp.reminder.scheduled.v1`
**Topic**: `reminders`
**Publisher**: `todo-notification-service`
**Subscribers**: `todo-backend` (broadcasts to user via WebSocket)

**Purpose**: Published when a task reminder is scheduled (due date within 15 minutes). Sent to user via WebSocket notification.

#### Schema

```json
{
  "specversion": "1.0",
  "type": "com.todoapp.reminder.scheduled.v1",
  "source": "todo-notification-service",
  "id": "d3hhfe00-0f3e-7jj1-ee9g-9ee2eg613d44",
  "time": "2026-02-01T16:45:00Z",
  "subject": "tasks/123",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "user_id": "user-uuid-456",
    "title": "Complete project proposal",
    "due_at": "2026-02-01T17:00:00Z",
    "minutes_until_due": 15,
    "message": "Task 'Complete project proposal' is due in 15 minutes"
  }
}
```

#### Data Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | integer | Yes | Unique task identifier |
| `user_id` | string | Yes | User to notify |
| `title` | string | Yes | Task title for notification |
| `due_at` | string (ISO 8601) | Yes | When task is due |
| `minutes_until_due` | integer | Yes | Minutes remaining until due (0-15) |
| `message` | string | Yes | Notification message text |

---

## Event Flow Diagrams

### Recurring Task Creation Flow

```
┌─────────────┐   task.completed.v1   ┌────────────────────────┐
│             │  ─────────────────────>│                        │
│ todo-backend│                        │ Dapr Pub/Sub (Kafka)   │
│             │<──────────────────────│ Topic: task-events     │
└─────────────┘                        └────────────────────────┘
                                                  │
                                                  │ subscribe
                                                  v
                                       ┌────────────────────────┐
                                       │ todo-recurring-service │
                                       │                        │
                                       │ 1. Check recurrence    │
                                       │ 2. Calculate next date │
                                       │ 3. POST /tasks (create)│
                                       └────────────────────────┘
```

### Reminder Notification Flow

```
┌──────────────────────┐   Cron: @every 5m   ┌────────────────────────┐
│ Dapr Cron Binding    │ ──────────────────>│ todo-notification-svc  │
│ (reminder-cron)      │                     │                        │
└──────────────────────┘                     │ 1. Query tasks due soon│
                                             │ 2. Publish reminders   │
                                             └────────────────────────┘
                                                        │
                                                        │ reminder.scheduled.v1
                                                        v
                                             ┌────────────────────────┐
                                             │ Dapr Pub/Sub (Kafka)   │
                                             │ Topic: reminders       │
                                             └────────────────────────┘
                                                        │
                                                        │ subscribe
                                                        v
                                             ┌────────────────────────┐
                                             │ todo-backend           │
                                             │                        │
                                             │ WebSocket → User       │
                                             │ Browser notification   │
                                             └────────────────────────┘
```

---

## Implementation Examples

### Publishing an Event (Python Backend)

```python
from app.events.publisher import EventPublisher
from app.events.schemas import TaskCreatedEvent

# Create event data
event = TaskCreatedEvent(
    task_id=task.id,
    user_id=str(task.user_id),
    title=task.title,
    description=task.description,
    priority=task.priority,
    tags=task.tags or [],
    due_date=task.due_date.isoformat() if task.due_date else None,
    recurrence=task.recurrence,
    recurrence_interval=task.recurrence_interval,
    created_at=task.created_at.isoformat()
)

# Publish to Kafka via Dapr
await EventPublisher.publish_task_created(event)
```

### Subscribing to Events (Python Backend)

```python
from fastapi import FastAPI, Request
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub="pubsub", topic="task-events")
async def handle_task_events(request: Request):
    """Dapr subscription handler for task-events topic"""
    event = await request.json()

    # CloudEvents envelope
    event_type = event.get("type")
    data = event.get("data")

    if event_type == "com.todoapp.task.completed.v1":
        await process_recurring_task(data)

    return {"status": "SUCCESS"}
```

### WebSocket Notification (TypeScript Frontend)

```typescript
// Receive reminder via WebSocket
useEffect(() => {
  connect(userId);

  window.addEventListener("task-reminder", (event: CustomEvent) => {
    const { task_id, title, due_at } = event.detail;

    // Show browser notification
    showNotification("Task Reminder", `${title} is due soon`, task_id);
  });
}, [userId]);
```

---

## Event Topics

| Topic | Events | Subscribers |
|-------|--------|-------------|
| `task-events` | `task.created.v1`, `task.completed.v1` | `todo-recurring-service` |
| `task-updates` | `task.updated.v1` | None (analytics only) |
| `reminders` | `reminder.scheduled.v1` | `todo-backend` (WebSocket) |

---

## Event Versioning

Events use semantic versioning in the `type` field:

- **v1**: Initial version
- **v2**: Breaking changes (new required fields, removed fields)
- **v1.1**: Backward-compatible additions (new optional fields)

Example:
```
com.todoapp.task.created.v1   → Initial version
com.todoapp.task.created.v2   → Breaking change (requires migration)
```

Subscribers **MUST** handle both old and new versions during transitions:

```python
if event_type == "com.todoapp.task.completed.v1":
    await handle_v1(data)
elif event_type == "com.todoapp.task.completed.v2":
    await handle_v2(data)
```

---

## Testing Events

### Local Testing with Dapr CLI

```bash
# Publish test event
dapr publish --publish-app-id todo-backend \
  --pubsub pubsub \
  --topic task-events \
  --data '{
    "specversion": "1.0",
    "type": "com.todoapp.task.created.v1",
    "source": "test-cli",
    "id": "test-123",
    "data": {
      "task_id": 999,
      "user_id": "test-user",
      "title": "Test Task",
      "created_at": "2026-01-29T10:00:00Z"
    }
  }'
```

### Monitoring Events in Redpanda

```bash
# Connect to Redpanda
kubectl port-forward -n redpanda svc/redpanda 9092:9092

# Consume events (requires rpk CLI)
rpk topic consume task-events --brokers localhost:9092
```

---

## References

- [CloudEvents v1.0 Specification](https://cloudevents.io/)
- [Dapr Pub/Sub Documentation](https://docs.dapr.io/developing-applications/building-blocks/pubsub/)
- [Kafka Topic Best Practices](https://kafka.apache.org/documentation/)
- [Backend Event Publisher: backend/app/events/publisher.py](../backend/app/events/publisher.py)
- [Event Schemas: backend/app/events/schemas.py](../backend/app/events/schemas.py)

---

**Status**: Event schemas documentation complete for Phase 5

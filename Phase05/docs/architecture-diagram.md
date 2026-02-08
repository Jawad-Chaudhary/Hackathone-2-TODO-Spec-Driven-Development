# Architecture Diagram: Event-Driven TODO Application

**Task**: T139 | **Purpose**: Visual architecture showing event flow from Backend → Dapr → Kafka → Services → WebSocket → Frontend

This document provides comprehensive architecture diagrams for Phase 5's event-driven system.

---

## High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                              USER BROWSER                                      │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                      Next.js Frontend (React 19)                        │  │
│  │                                                                         │  │
│  │  • Task Management UI (create, edit, delete, complete)                 │  │
│  │  • Real-time notifications (WebSocket)                                 │  │
│  │  • Search, filter, sort (Zustand state)                                │  │
│  │  • Browser notifications API                                           │  │
│  │  • Framer Motion animations                                            │  │
│  └────────────┬────────────────────────────────────────┬───────────────────┘  │
└───────────────┼────────────────────────────────────────┼──────────────────────┘
                │                                        │
                │ HTTP/REST (CRUD)                       │ WebSocket (notifications)
                │                                        │
                v                                        v
┌──────────────────────────────────────────────────────────────────────────────┐
│                       Kubernetes Cluster (Minikube / OKE)                    │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      todo-backend (FastAPI)                            │ │
│  │                                                                        │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │ │
│  │  │ REST API Endpoints                                              │  │ │
│  │  │  • POST /tasks         → Create task                            │  │ │
│  │  │  • GET  /tasks         → List tasks (filter, search, sort)      │  │ │
│  │  │  • PATCH /tasks/{id}   → Update task                            │  │ │
│  │  │  • DELETE /tasks/{id}  → Delete task                            │  │ │
│  │  │  • GET  /stats         → Task statistics                        │  │ │
│  │  └─────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                        │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │ │
│  │  │ WebSocket Server (port 8000)                                    │  │ │
│  │  │  • /ws endpoint for real-time notifications                     │  │ │
│  │  │  • Broadcasts task reminders to connected users                 │  │ │
│  │  └─────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                        │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │ │
│  │  │ Event Publishers (Dapr Client)                                  │  │ │
│  │  │  • publish_task_created()   → task-events topic                 │  │ │
│  │  │  • publish_task_completed() → task-events topic                 │  │ │
│  │  │  • publish_task_updated()   → task-updates topic                │  │ │
│  │  └─────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                        │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │ │
│  │  │ Event Subscribers (Dapr Subscription)                           │  │ │
│  │  │  • @subscribe(topic="reminders")                                │  │ │
│  │  │    → handle_reminder_event() → WebSocket broadcast              │  │ │
│  │  └─────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                        │ │
│  │  [Dapr Sidecar: app-id="todo-backend"]                                │ │
│  └────────────┬───────────────────────────────────────┬──────────────────┘ │
│               │                                       │                    │
│               │ Pub/Sub                               │ State/Secrets      │
│               │                                       │                    │
│               v                                       v                    │
│  ┌────────────────────────────┐      ┌─────────────────────────────────┐  │
│  │   Dapr Pub/Sub Component   │      │  Dapr State/Secret Components   │  │
│  │   (pubsub.kafka)           │      │  • statestore (PostgreSQL)      │  │
│  │                            │      │  • secretstore (K8s Secrets)    │  │
│  └────────────┬───────────────┘      └─────────────────────────────────┘  │
│               │                                                            │
│               │ Kafka Protocol (SASL/TLS)                                 │
│               │                                                            │
│               v                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │             Redpanda (Kafka-compatible Message Broker)              │  │
│  │                                                                     │  │
│  │  Topics:                                                            │  │
│  │  • task-events    (3 partitions, 1 replica)                        │  │
│  │  • task-updates   (3 partitions, 1 replica)                        │  │
│  │  • reminders      (1 partition,  1 replica)                        │  │
│  └────────────┬────────────────────────────────────┬──────────────────┘  │
│               │                                    │                     │
│               │ Subscribe                          │ Subscribe           │
│               │ task-events                        │ reminders           │
│               v                                    │                     │
│  ┌─────────────────────────────────────────────┐  │                     │
│  │  todo-recurring-service (FastAPI)           │  │                     │
│  │                                             │  │                     │
│  │  ┌───────────────────────────────────────┐  │  │                     │
│  │  │ Event Handler                         │  │  │                     │
│  │  │  @subscribe(topic="task-events")      │  │  │                     │
│  │  │  • Listen for task.completed.v1       │  │  │                     │
│  │  │  • Check if task has recurrence       │  │  │                     │
│  │  │  • Calculate next due date            │  │  │                     │
│  │  │  • POST /tasks (create next instance) │  │  │                     │
│  │  └───────────────────────────────────────┘  │  │                     │
│  │                                             │  │                     │
│  │  [Dapr Sidecar: app-id="todo-recurring-    │  │                     │
│  │   service"]                                 │  │                     │
│  └─────────────────────────────────────────────┘  │                     │
│                                                    │                     │
│  ┌─────────────────────────────────────────────────┼──────────────────┐  │
│  │  todo-notification-service (FastAPI)            │                  │  │
│  │                                                  │                  │  │
│  │  ┌────────────────────────────────────────────┐ │                  │  │
│  │  │ Cron Binding Handler                       │ │                  │  │
│  │  │  @app.post("/reminder-cron")               │ │                  │  │
│  │  │  • Triggered every 5 minutes by Dapr cron  │ │                  │  │
│  │  │  • Query tasks due within 15 minutes       │ │                  │  │
│  │  │  • Publish reminder.scheduled.v1 events    │─┼──────────────────┘  │
│  │  └────────────────────────────────────────────┘ │                     │
│  │                                                  │                     │
│  │  [Dapr Sidecar: app-id="todo-notification-      │                     │
│  │   service"]                                      │                     │
│  │  [Dapr Cron Binding: @every 5m]                 │                     │
│  └─────────────────────────────────────────────────┘                     │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    Neon PostgreSQL Database                        │  │
│  │                                                                    │  │
│  │  Tables:                                                           │  │
│  │  • users         (id, username, email, password_hash)             │  │
│  │  • tasks         (id, user_id, title, description, completed,     │  │
│  │                   priority, tags, due_date, recurrence,            │  │
│  │                   recurrence_interval, parent_task_id,             │  │
│  │                   reminder_sent_at, created_at, updated_at)        │  │
│  │  • dapr_state    (Dapr state store table)                         │  │
│  │  • dapr_metadata (Dapr metadata table)                            │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Event Flow Diagrams

### 1. Task Creation Flow

```
User              Frontend          Backend           Dapr           Kafka
 │                   │                 │                │              │
 │  Fill form        │                 │                │              │
 │  Click "Create"   │                 │                │              │
 │──────────────────>│                 │                │              │
 │                   │  POST /tasks    │                │              │
 │                   │────────────────>│                │              │
 │                   │                 │  Save to DB    │              │
 │                   │                 │  (INSERT)      │              │
 │                   │                 │                │              │
 │                   │                 │  Publish event │              │
 │                   │                 │  (task.created)│              │
 │                   │                 │───────────────>│ Produce msg  │
 │                   │                 │                │─────────────>│
 │                   │  201 Created    │                │              │
 │                   │<────────────────│                │              │
 │  Task appears     │                 │                │              │
 │  in list          │                 │                │              │
 │<──────────────────│                 │                │              │
```

**Events Published**:
- **Type**: `com.todoapp.task.created.v1`
- **Topic**: `task-events`
- **Data**: `{ task_id, user_id, title, description, priority, tags, due_date, recurrence, created_at }`

**Purpose**: Log task creation for analytics, audit trail

---

### 2. Recurring Task Flow (Weekly Task Completion)

```
User              Frontend        Backend       Dapr        Kafka      Recurring
                                                                       Service
 │                   │              │             │           │           │
 │  Check task       │              │             │           │           │
 │  as complete      │              │             │           │           │
 │──────────────────>│              │             │           │           │
 │                   │ PATCH /tasks │             │           │           │
 │                   │    /{id}     │             │           │           │
 │                   │─────────────>│             │           │           │
 │                   │              │  Update DB  │           │           │
 │                   │              │  completed= │           │           │
 │                   │              │  true       │           │           │
 │                   │              │             │           │           │
 │                   │              │  Publish    │           │           │
 │                   │              │  task.      │           │           │
 │                   │              │  completed  │           │           │
 │                   │              │────────────>│  Produce  │           │
 │                   │              │             │──────────>│           │
 │                   │              │             │           │           │
 │                   │              │             │           │  Consume  │
 │                   │              │             │           │  event    │
 │                   │              │             │           │──────────>│
 │                   │              │             │           │           │
 │                   │              │             │           │           │  Check
 │                   │              │             │           │           │  recurrence
 │                   │              │             │           │           │  = "weekly"
 │                   │              │             │           │           │
 │                   │              │             │           │           │  Calculate
 │                   │              │             │           │           │  next_due =
 │                   │              │             │           │           │  due + 7 days
 │                   │              │             │           │           │
 │                   │              │             │           │           │
 │                   │              │<────────────────────────────────────│
 │                   │              │  POST /tasks (create next instance) │
 │                   │              │             │           │           │
 │                   │              │  Save new   │           │           │
 │                   │              │  task with  │           │           │
 │                   │              │  next_due   │           │           │
 │                   │              │  parent_id  │           │           │
 │                   │  200 OK      │             │           │           │
 │                   │<─────────────│             │           │           │
 │  Strikethrough    │              │             │           │           │
 │  appears          │              │             │           │           │
 │<──────────────────│              │             │           │           │
 │                   │              │             │           │           │
 │  (5s later)       │              │             │           │           │
 │  New task with    │              │             │           │           │
 │  next week's due  │              │             │           │           │
 │  date appears     │              │             │           │           │
 │<──────────────────│ (refetch)    │             │           │           │
```

**Events Published**:
- **Type**: `com.todoapp.task.completed.v1`
- **Topic**: `task-events`
- **Data**: `{ task_id, user_id, title, completed_at, due_date, recurrence, recurrence_interval, parent_task_id }`

**Subscriber Actions**:
1. **todo-recurring-service** receives event
2. Checks if `recurrence` field is present
3. Calculates next due date based on recurrence pattern:
   - `daily`: due_date + 1 day
   - `weekly`: due_date + 7 days
   - `monthly`: due_date + 1 month
   - `custom`: due_date + recurrence_interval days
4. Creates new task via `POST /tasks` with:
   - Same title, description, priority, tags
   - New due_date (calculated)
   - Same recurrence pattern
   - `parent_task_id` set to original task ID

---

### 3. Reminder Notification Flow

```
Dapr Cron      Notification    Dapr      Kafka      Backend      WebSocket     Frontend
Binding        Service                                            Connection
  │               │              │          │           │             │            │
  │  @every 5m    │              │          │           │             │            │
  │──────────────>│              │          │           │             │            │
  │               │              │          │           │             │            │
  │               │  Query tasks │          │           │             │            │
  │               │  WHERE       │          │           │             │            │
  │               │  due_date    │          │           │             │            │
  │               │  BETWEEN now │          │           │             │            │
  │               │  AND now+15m │          │           │             │            │
  │               │  (from DB)   │          │           │             │            │
  │               │              │          │           │             │            │
  │               │  Found 2     │          │           │             │            │
  │               │  tasks       │          │           │             │            │
  │               │              │          │           │             │            │
  │               │  For each    │          │           │             │            │
  │               │  task:       │          │           │             │            │
  │               │  Publish     │          │           │             │            │
  │               │  reminder    │          │           │             │            │
  │               │─────────────>│ Produce  │           │             │            │
  │               │              │─────────>│           │             │            │
  │               │              │          │           │             │            │
  │               │              │          │  Consume  │             │            │
  │               │              │          │──────────>│             │            │
  │               │              │          │           │             │            │
  │               │              │          │           │  Broadcast  │            │
  │               │              │          │           │  via WS     │            │
  │               │              │          │           │────────────>│            │
  │               │              │          │           │             │            │
  │               │              │          │           │             │  Custom    │
  │               │              │          │           │             │  Event:    │
  │               │              │          │           │             │  task-     │
  │               │              │          │           │             │  reminder  │
  │               │              │          │           │             │───────────>│
  │               │              │          │           │             │            │
  │               │              │          │           │             │            │ Browser
  │               │              │          │           │             │            │ Notification
  │               │              │          │           │             │            │ appears
  │               │              │          │           │             │            │
  │               │  Update DB:  │          │           │             │            │
  │               │  reminder_   │          │           │             │            │
  │               │  sent_at =   │          │           │             │            │
  │               │  NOW()       │          │           │             │            │
```

**Events Published**:
- **Type**: `com.todoapp.reminder.scheduled.v1`
- **Topic**: `reminders`
- **Data**: `{ task_id, user_id, title, due_at, minutes_until_due, message }`

**Flow Steps**:
1. **Dapr Cron Binding** triggers every 5 minutes
2. **Notification Service** queries database for tasks due in next 15 minutes
3. For each task, publishes `reminder.scheduled.v1` event to `reminders` topic
4. **Backend** subscribes to `reminders` topic
5. **Backend** broadcasts notification to user's WebSocket connection
6. **Frontend** receives WebSocket message and shows browser notification
7. **Notification Service** marks task as `reminder_sent_at = NOW()` to avoid duplicates

---

## Component Interaction Matrix

| Component | Publishes Events | Subscribes to Events | Uses State Store | Uses Secrets | WebSocket Server |
|-----------|-----------------|---------------------|-----------------|--------------|------------------|
| **todo-backend** | task.created.v1, task.completed.v1, task.updated.v1 | reminders | Yes | Yes | Yes (port 8000) |
| **todo-recurring-service** | None | task-events (task.completed.v1) | Yes | Yes | No |
| **todo-notification-service** | reminder.scheduled.v1 | None | Yes | Yes | No |
| **Frontend (Next.js)** | None | None (WebSocket client) | No | No | No (client) |

---

## Data Flow: Complete User Story

**Scenario**: User creates a weekly recurring task "Team standup" due Friday 9 AM

### Step 1: Task Creation (Frontend → Backend)
```
POST /tasks
{
  "title": "Team standup",
  "description": "Weekly team sync meeting",
  "priority": "medium",
  "tags": ["meeting"],
  "due_date": "2026-01-31T09:00:00Z",
  "recurrence": "weekly"
}
```

### Step 2: Backend Saves Task
```sql
INSERT INTO tasks (user_id, title, description, priority, tags, due_date, recurrence, created_at)
VALUES ('user-123', 'Team standup', 'Weekly team sync meeting', 'medium', '["meeting"]', '2026-01-31T09:00:00Z', 'weekly', NOW());
```

### Step 3: Backend Publishes Event
```json
{
  "specversion": "1.0",
  "type": "com.todoapp.task.created.v1",
  "source": "todo-backend",
  "subject": "tasks/456",
  "data": {
    "task_id": 456,
    "user_id": "user-123",
    "title": "Team standup",
    "recurrence": "weekly",
    "due_date": "2026-01-31T09:00:00Z"
  }
}
```
→ Published to `task-events` topic

### Step 4: Reminder Scheduled (Friday 8:45 AM)
Dapr Cron triggers notification service:
```sql
SELECT * FROM tasks
WHERE due_date BETWEEN '2026-01-31T08:45:00Z' AND '2026-01-31T09:00:00Z'
  AND completed = false
  AND reminder_sent_at IS NULL;
```

Notification service publishes:
```json
{
  "type": "com.todoapp.reminder.scheduled.v1",
  "data": {
    "task_id": 456,
    "user_id": "user-123",
    "title": "Team standup",
    "due_at": "2026-01-31T09:00:00Z",
    "minutes_until_due": 15,
    "message": "Task 'Team standup' is due in 15 minutes"
  }
}
```
→ Published to `reminders` topic

### Step 5: WebSocket Notification (Frontend)
Backend subscribes to `reminders`, broadcasts to WebSocket:
```javascript
// Frontend receives
{
  type: "reminder",
  task_id: 456,
  title: "Team standup",
  due_date: "2026-01-31T09:00:00Z"
}

// Shows browser notification
new Notification("Task Reminder", {
  body: "Team standup is due in 15 minutes"
});
```

### Step 6: User Completes Task (Friday 9:05 AM)
```
PATCH /tasks/456
{ "completed": true }
```

Backend publishes:
```json
{
  "type": "com.todoapp.task.completed.v1",
  "data": {
    "task_id": 456,
    "user_id": "user-123",
    "title": "Team standup",
    "completed_at": "2026-01-31T09:05:00Z",
    "due_date": "2026-01-31T09:00:00Z",
    "recurrence": "weekly"
  }
}
```
→ Published to `task-events` topic

### Step 7: Recurring Service Creates Next Instance
Recurring service receives event, calculates:
```
next_due_date = due_date + 7 days = "2026-02-07T09:00:00Z"
```

Creates new task:
```
POST /tasks
{
  "title": "Team standup",
  "description": "Weekly team sync meeting",
  "priority": "medium",
  "tags": ["meeting"],
  "due_date": "2026-02-07T09:00:00Z",
  "recurrence": "weekly",
  "parent_task_id": 456
}
```

New task (ID 457) appears in UI with next Friday's due date!

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 16 + React 19 | UI framework |
| **State Management** | Zustand | Filter/sort state |
| **Animations** | Framer Motion | Page transitions, list animations |
| **Backend** | FastAPI (Python 3.12) | REST API |
| **Database** | Neon PostgreSQL | Persistent storage |
| **ORM** | SQLModel + Alembic | Database models, migrations |
| **Message Broker** | Redpanda (Kafka-compatible) | Event streaming |
| **Service Mesh** | Dapr v1.14 | Pub/Sub, State, Secrets, Cron |
| **Container Orchestration** | Kubernetes (Minikube/OKE) | Service deployment |
| **Package Manager** | Helm 3 | Kubernetes deployments |
| **Real-time** | WebSocket (FastAPI) | Live notifications |
| **CI/CD** | GitHub Actions | Automated testing, deployment |

---

## Deployment Topology

### Local Development (Minikube)
```
localhost:3000  →  Next.js Frontend (dev server)
localhost:8000  →  Backend API + WebSocket (uvicorn)
localhost:9092  →  Redpanda (Kafka) port-forwarded
Minikube        →  Dapr control plane + components
```

### Production (Oracle OKE)
```
Load Balancer (OCI)
  ├─ frontend-service   (NodePort 3000 → 80)
  └─ backend-service    (ClusterIP 8000)
      ├─ Dapr sidecar (todo-backend)
      ├─ Recurring service (ClusterIP 8001)
      │   └─ Dapr sidecar (todo-recurring-service)
      └─ Notification service (ClusterIP 8002)
          └─ Dapr sidecar (todo-notification-service)

External Services:
  • Neon PostgreSQL (neon.tech)
  • Redpanda Cloud (cloud.redpanda.com)
  • GitHub Container Registry (ghcr.io)
```

---

## Performance Characteristics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Task Creation Latency** | < 500ms (p95) | Time from POST /tasks to event published |
| **Recurring Task Creation** | < 2s | Time from completion to new task created |
| **Reminder Notification** | < 1s | Time from Kafka event to WebSocket delivery |
| **WebSocket Latency** | < 100ms | Roundtrip ping/pong |
| **Search Response** | < 300ms | GET /tasks with filters (1000 tasks) |
| **Event Throughput** | 100 events/sec | Kafka producer rate |

---

## Security Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        SECURITY LAYERS                       │
└──────────────────────────────────────────────────────────────┘

1. Frontend Authentication
   ├─ Better Auth (JWT tokens in httpOnly cookies)
   ├─ Protected routes (redirect to /auth/signin)
   └─ Session validation on page load

2. Backend Authorization
   ├─ JWT token validation (verify signature, expiry)
   ├─ User ID extraction from token claims
   └─ Row-level security (WHERE user_id = current_user)

3. Network Security
   ├─ Kubernetes Network Policies (namespace isolation)
   ├─ TLS in transit (HTTPS, Kafka SASL/SSL)
   └─ Secrets encryption at rest (K8s Secret Store)

4. Database Security
   ├─ Connection pooling (SQLModel AsyncEngine)
   ├─ Prepared statements (SQLAlchemy - SQL injection prevention)
   └─ Neon database encryption at rest

5. Kafka Security
   ├─ SASL/SCRAM authentication
   ├─ TLS encryption in transit
   └─ Topic ACLs (Redpanda Cloud)
```

---

## References

- [Dapr Architecture](https://docs.dapr.io/concepts/overview/)
- [CloudEvents Specification](https://cloudevents.io/)
- [Kafka Event Streaming](https://kafka.apache.org/documentation/)
- [WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)
- [Event Schemas Documentation](./event-schemas.md)
- [Dapr Components Documentation](./dapr-components.md)

---

**Status**: Architecture diagrams complete for Phase 5

# Dapr Components Documentation

**Task**: T137 | **Purpose**: Dapr component configurations for Phase 5 event-driven architecture

This document describes all Dapr components used in the TODO application, including Pub/Sub, State Store, Secret Store, and Cron Binding configurations.

---

## Overview

Dapr (Distributed Application Runtime) provides building blocks for microservices communication. The TODO app uses 4 key components:

1. **Pub/Sub** - Event-driven messaging via Kafka (Redpanda)
2. **State Store** - Distributed state management via PostgreSQL
3. **Secret Store** - Kubernetes secrets management
4. **Cron Binding** - Scheduled reminder checks every 5 minutes

All components are defined as Kubernetes Custom Resources (CRDs) in the `k8s/components/` directory.

---

## Component 1: Pub/Sub (Kafka/Redpanda)

**File**: `k8s/components/pubsub.yaml`
**Type**: `pubsub.kafka`
**Purpose**: Event-driven messaging for task events and reminders

### Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  # Kafka brokers from Redpanda Cloud
  - name: brokers
    secretKeyRef:
      name: redpanda-creds
      key: brokers

  # SASL authentication for Redpanda Cloud
  - name: authType
    value: "password"
  - name: saslUsername
    secretKeyRef:
      name: redpanda-creds
      key: username
  - name: saslPassword
    secretKeyRef:
      name: redpanda-creds
      key: password
  - name: saslMechanism
    secretKeyRef:
      name: redpanda-creds
      key: mechanism

  # Consumer group configuration
  - name: consumerGroup
    value: "todo-app-group"

  # Performance tuning
  - name: maxMessageBytes
    value: "1024"
  - name: version
    value: "2.0.0"

  # TLS configuration (Redpanda Cloud requires TLS)
  - name: enableTLS
    value: "true"

scopes:
- todo-backend
- todo-recurring-service
- todo-notification-service
```

### Metadata Fields

| Field | Description | Example |
|-------|-------------|---------|
| `brokers` | Kafka broker addresses (from secret) | `seed-12345.redpanda.com:9092` |
| `authType` | Authentication mechanism | `password` (SASL/PLAIN or SCRAM) |
| `saslUsername` | SASL username (from secret) | `redpanda-user` |
| `saslPassword` | SASL password (from secret) | `<sensitive>` |
| `saslMechanism` | SASL mechanism | `SCRAM-SHA-256` |
| `consumerGroup` | Kafka consumer group ID | `todo-app-group` |
| `maxMessageBytes` | Max message size in bytes | `1024` (1KB - CloudEvents are small) |
| `version` | Kafka protocol version | `2.0.0` |
| `enableTLS` | Enable TLS encryption | `true` |

### Topics Used

| Topic | Purpose | Publishers | Subscribers |
|-------|---------|------------|-------------|
| `task-events` | Task lifecycle events | `todo-backend` | `todo-recurring-service` |
| `task-updates` | Task modification events | `todo-backend` | None (analytics) |
| `reminders` | Task reminders | `todo-notification-service` | `todo-backend` |

### Scoped Applications

The component is scoped to 3 services:
- **todo-backend**: Publishes `task.created`, `task.completed`, `task.updated`; subscribes to `reminders`
- **todo-recurring-service**: Subscribes to `task.completed` to create recurring instances
- **todo-notification-service**: Publishes `reminder.scheduled` for due tasks

### Publishing Events (Backend Example)

```python
from dapr.clients import DaprClient

async def publish_task_completed(task_id: int, user_id: str):
    with DaprClient() as dapr:
        event_data = {
            "task_id": task_id,
            "user_id": user_id,
            "completed_at": "2026-01-29T10:00:00Z"
        }

        # Publish to task-events topic via pubsub component
        dapr.publish_event(
            pubsub_name="pubsub",
            topic_name="task-events",
            data=event_data,
            data_content_type="application/json"
        )
```

### Subscribing to Events (Recurring Service Example)

```python
from fastapi import FastAPI, Request
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub="pubsub", topic="task-events")
async def handle_task_completed(request: Request):
    """Dapr subscription handler"""
    event = await request.json()

    if event.get("type") == "com.todoapp.task.completed.v1":
        data = event.get("data")
        await process_recurring_task(data)

    return {"status": "SUCCESS"}
```

---

## Component 2: State Store (PostgreSQL)

**File**: `k8s/components/statestore.yaml`
**Type**: `state.postgresql`
**Purpose**: Distributed state management for Dapr actors and services

### Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-app
spec:
  type: state.postgresql
  version: v1
  metadata:
  # PostgreSQL connection string from secret
  - name: connectionString
    secretKeyRef:
      name: neon-db-creds
      key: connectionString

  # Table configuration
  - name: tableName
    value: "dapr_state"
  - name: metadataTableName
    value: "dapr_metadata"

  # Performance and reliability
  - name: actorStateStore
    value: "true"
  - name: cleanupIntervalInSeconds
    value: "3600"  # Cleanup stale data every hour

scopes:
- todo-backend
- todo-recurring-service
- todo-notification-service
```

### Metadata Fields

| Field | Description | Example |
|-------|-------------|---------|
| `connectionString` | PostgreSQL connection URL (from secret) | `postgresql://user:pass@host/db` |
| `tableName` | Table for storing state | `dapr_state` |
| `metadataTableName` | Table for metadata | `dapr_metadata` |
| `actorStateStore` | Enable Dapr Actors support | `true` |
| `cleanupIntervalInSeconds` | Cleanup interval for stale data | `3600` (1 hour) |

### State Tables

Dapr automatically creates two tables in the PostgreSQL database:

#### `dapr_state` Table

| Column | Type | Description |
|--------|------|-------------|
| `key` | TEXT | Unique state key |
| `value` | JSONB | State value (JSON) |
| `etag` | TEXT | Optimistic concurrency control tag |
| `update_time` | TIMESTAMP | Last update timestamp |

#### `dapr_metadata` Table

| Column | Type | Description |
|--------|------|-------------|
| `key` | TEXT | Metadata key |
| `value` | TEXT | Metadata value |

### Using State Store (Example)

```python
from dapr.clients import DaprClient

async def save_user_preferences(user_id: str, preferences: dict):
    with DaprClient() as dapr:
        # Save state with key "user-prefs-{user_id}"
        dapr.save_state(
            store_name="statestore",
            key=f"user-prefs-{user_id}",
            value=preferences
        )

async def get_user_preferences(user_id: str) -> dict:
    with DaprClient() as dapr:
        # Get state by key
        state = dapr.get_state(
            store_name="statestore",
            key=f"user-prefs-{user_id}"
        )
        return state.data
```

---

## Component 3: Secret Store (Kubernetes Secrets)

**File**: `k8s/components/secretstore.yaml`
**Type**: `secretstores.kubernetes`
**Purpose**: Access Kubernetes secrets from Dapr applications

### Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
  namespace: todo-app
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
  - name: vaultValueType
    value: "map"
  - name: defaultNamespace
    value: "todo-app"

scopes:
- todo-backend
- todo-recurring-service
- todo-notification-service
```

### Metadata Fields

| Field | Description | Example |
|-------|-------------|---------|
| `vaultValueType` | Secret value type | `map` (key-value pairs) |
| `defaultNamespace` | Kubernetes namespace for secrets | `todo-app` |

### Referenced Secrets

The secret store allows services to access these Kubernetes secrets:

#### `neon-db-creds` Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: neon-db-creds
  namespace: todo-app
type: Opaque
stringData:
  connectionString: "postgresql://user:pass@host.neon.tech/db"
```

#### `redpanda-creds` Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: redpanda-creds
  namespace: todo-app
type: Opaque
stringData:
  brokers: "seed-12345.redpanda.com:9092"
  username: "redpanda-user"
  password: "<sensitive>"
  mechanism: "SCRAM-SHA-256"
```

#### `openai-key` Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: openai-key
  namespace: todo-app
type: Opaque
stringData:
  apiKey: "sk-proj-..."
```

### Using Secret Store (Example)

```python
from dapr.clients import DaprClient

async def get_database_url() -> str:
    with DaprClient() as dapr:
        # Get secret from Kubernetes
        secret = dapr.get_secret(
            store_name="secretstore",
            key="neon-db-creds",
            metadata={"namespace": "todo-app"}
        )
        return secret.secrets["connectionString"]
```

---

## Component 4: Cron Binding (Reminder Scheduler)

**File**: `k8s/components/reminder-cron.yaml`
**Type**: `bindings.cron`
**Purpose**: Trigger reminder checks every 5 minutes

### Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
  namespace: todo-app
spec:
  type: bindings.cron
  version: v1
  metadata:
  # Run every 5 minutes to check for upcoming due dates
  - name: schedule
    value: "@every 5m"
  - name: direction
    value: "input"

scopes:
- todo-notification-service
```

### Metadata Fields

| Field | Description | Example |
|-------|-------------|---------|
| `schedule` | Cron schedule expression | `@every 5m` (every 5 minutes) |
| `direction` | Binding direction | `input` (triggers service) |

### Schedule Formats

| Format | Description | Example |
|--------|-------------|---------|
| `@every <duration>` | Every X duration | `@every 5m`, `@every 1h` |
| `<min> <hour> <day> <month> <weekday>` | Cron expression | `0 9 * * *` (9 AM daily) |
| `@hourly` | Every hour | `@hourly` |
| `@daily` | Every day at midnight | `@daily` |

### Cron Handler (Notification Service)

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/reminder-cron")
async def handle_reminder_cron(request: Request):
    """
    Triggered every 5 minutes by Dapr cron binding.
    Checks for tasks due within 15 minutes and publishes reminders.
    """
    await check_and_send_reminders()
    return {"status": "success"}
```

### Reminder Check Logic

```python
from datetime import datetime, timedelta
from sqlmodel import select

async def check_and_send_reminders():
    """Query tasks due within 15 minutes and publish reminders"""
    now = datetime.utcnow()
    reminder_window = now + timedelta(minutes=15)

    # Query tasks due soon (not completed, not already reminded)
    query = select(Task).where(
        Task.due_date >= now,
        Task.due_date <= reminder_window,
        Task.completed == False,
        Task.reminder_sent_at == None
    )

    async with AsyncSession(engine) as session:
        result = await session.execute(query)
        tasks = result.scalars().all()

        for task in tasks:
            # Publish reminder event
            await publish_reminder(task)

            # Mark as reminded
            task.reminder_sent_at = now
            await session.commit()
```

---

## Deployment

### Apply Components to Kubernetes

```bash
# Create namespace
kubectl create namespace todo-app

# Apply secrets
kubectl apply -f k8s/base/secrets.yaml -n todo-app

# Apply Dapr components
kubectl apply -f k8s/components/ -n todo-app

# Verify components
dapr components -k -n todo-app
```

### Expected Output

```
NAMESPACE  NAME            TYPE                  VERSION  SCOPES
todo-app   pubsub          pubsub.kafka          v1       todo-backend, todo-recurring-service, todo-notification-service
todo-app   statestore      state.postgresql      v1       todo-backend, todo-recurring-service, todo-notification-service
todo-app   secretstore     secretstores.k8s      v1       todo-backend, todo-recurring-service, todo-notification-service
todo-app   reminder-cron   bindings.cron         v1       todo-notification-service
```

---

## Troubleshooting

### Component Not Loading

**Symptoms**: Service logs show "component not found"

**Solution**:
```bash
# Check component status
kubectl get components -n todo-app

# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd -n todo-app

# Verify component scopes match Dapr app-id
# Helm deployment: dapr.io/app-id: "todo-backend"
# Component scopes must include: "todo-backend"
```

### Pub/Sub Connection Failed

**Symptoms**: "Failed to connect to Kafka broker"

**Solution**:
```bash
# Verify Redpanda credentials secret
kubectl get secret redpanda-creds -n todo-app -o yaml

# Test connection from pod
kubectl run -it --rm kafka-test --image=edenhill/kcat:1.7.1 --restart=Never -- \
  -b seed-12345.redpanda.com:9092 \
  -X security.protocol=SASL_SSL \
  -X sasl.mechanism=SCRAM-SHA-256 \
  -X sasl.username=<username> \
  -X sasl.password=<password> \
  -L
```

### State Store Migration Needed

**Symptoms**: "Table dapr_state does not exist"

**Solution**:
```bash
# Dapr automatically creates tables on first use
# But you can manually create them:

psql $DATABASE_URL -c "
CREATE TABLE IF NOT EXISTS dapr_state (
  key TEXT PRIMARY KEY,
  value JSONB NOT NULL,
  etag TEXT,
  update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dapr_metadata (
  key TEXT PRIMARY KEY,
  value TEXT
);
"
```

### Cron Not Triggering

**Symptoms**: Reminder endpoint never called

**Solution**:
```bash
# Check Dapr sidecar logs for cron errors
kubectl logs <notification-pod> -c daprd -n todo-app | grep cron

# Verify endpoint is registered
# Dapr expects POST /reminder-cron endpoint

# Test manually
curl -X POST http://localhost:8080/reminder-cron
```

---

## Component Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Kubernetes Cluster                      │
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │ todo-backend │   │ recurring-   │   │ notification-│       │
│  │              │   │   service    │   │   service    │       │
│  │ (Dapr app-id)│   │ (Dapr app-id)│   │ (Dapr app-id)│       │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘       │
│         │ Dapr sidecar     │ Dapr sidecar     │ Dapr sidecar  │
│         │                  │                  │               │
│  ┌──────▼──────────────────▼──────────────────▼───────┐       │
│  │         Dapr Control Plane (dapr-system)           │       │
│  └──────┬──────────────┬───────────────┬───────────────┘       │
│         │              │               │                       │
│         │              │               │                       │
│    ┌────▼─────┐  ┌────▼─────┐  ┌──────▼──────┐  ┌──────────┐ │
│    │ pubsub   │  │statestore│  │ secretstore │  │ reminder-│ │
│    │ (Kafka)  │  │  (PG)    │  │    (K8s)    │  │   cron   │ │
│    └────┬─────┘  └────┬─────┘  └──────┬──────┘  └──────────┘ │
│         │             │               │                       │
└─────────┼─────────────┼───────────────┼───────────────────────┘
          │             │               │
     ┌────▼─────┐  ┌────▼─────┐  ┌──────▼──────┐
     │ Redpanda │  │   Neon   │  │ K8s Secrets │
     │  Cloud   │  │PostgreSQL│  │             │
     │  (Kafka) │  │          │  │             │
     └──────────┘  └──────────┘  └─────────────┘
```

---

## References

- [Dapr Documentation](https://docs.dapr.io/)
- [Dapr Pub/Sub Spec](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-kafka/)
- [Dapr State Management](https://docs.dapr.io/reference/components-reference/supported-state-stores/setup-postgresql/)
- [Dapr Bindings](https://docs.dapr.io/reference/components-reference/supported-bindings/cron/)
- [CloudEvents Specification](https://cloudevents.io/)

---

**Status**: Dapr components documentation complete for Phase 5

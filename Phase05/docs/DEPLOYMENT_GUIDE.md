# Todo App - Complete Deployment Guide

**Version**: 2.0.0
**Phase**: 5 - Advanced Features with Event-Driven Architecture
**Last Updated**: 2026-01-30

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Deployment Options](#deployment-options)
- [Option 1: Local Development (Minikube)](#option-1-local-development-minikube)
- [Option 2: Cloud Deployment (Oracle OKE)](#option-2-cloud-deployment-oracle-oke)
- [Option 3: CI/CD with GitHub Actions](#option-3-cicd-with-github-actions)
- [Post-Deployment Configuration](#post-deployment-configuration)
- [Troubleshooting](#troubleshooting)
- [Monitoring & Observability](#monitoring--observability)

---

## Overview

This guide covers three deployment approaches for the Todo App:

1. **Local Development (Minikube)** - Complete local Kubernetes environment for development and testing
2. **Cloud Deployment (Oracle OKE)** - Production deployment to Oracle Cloud Infrastructure
3. **CI/CD Pipeline (GitHub Actions)** - Automated deployment pipeline

### Architecture Overview

```
┌─────────────┐   REST/WebSocket   ┌──────────────┐
│   Frontend  │ ←────────────────→ │   Backend    │
│  Next.js 16 │                    │  FastAPI     │
└─────────────┘                    └───────┬──────┘
                                           │
                                           │ Dapr Pub/Sub
                                           │
                                    ┌──────▼───────┐
                                    │   Redpanda   │
                                    │   (Kafka)    │
                                    └──────┬───────┘
                                           │
                        ┌──────────────────┼──────────────────┐
                        │                  │                  │
                ┌───────▼────────┐  ┌──────▼──────┐  ┌───────▼────────┐
                │   Recurring    │  │ Notification │  │   WebSocket    │
                │   Service      │  │   Service    │  │   Broadcast    │
                └────────────────┘  └──────────────┘  └────────────────┘
```

**Components:**
- **Frontend**: Next.js 16 with React 19, TailwindCSS, Framer Motion
- **Backend**: FastAPI with SQLModel ORM, JWT authentication, WebSocket support
- **Recurring Service**: Handles automatic task recurrence via Kafka events
- **Notification Service**: Sends reminders via cron-triggered checks
- **Message Broker**: Redpanda (Kafka-compatible) for event streaming
- **Service Mesh**: Dapr v1.14 for pub/sub, state, secrets, cron
- **Database**: Neon PostgreSQL (serverless)

---

## Prerequisites

### Required Tools

1. **Docker** (20.10+)
   ```bash
   docker --version
   ```

2. **kubectl** (1.28+)
   ```bash
   kubectl version --client
   ```

3. **Helm** (3.13+)
   ```bash
   helm version
   ```

4. **Dapr CLI** (1.14+)
   ```bash
   dapr --version
   ```
   Install: `wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash`

5. **Minikube** (for local deployment)
   ```bash
   minikube version
   ```
   Install: https://minikube.sigs.k8s.io/docs/start/

6. **OCI CLI** (for Oracle OKE deployment)
   ```bash
   oci --version
   ```
   Install: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm

### Required Accounts

- **GitHub Account** - For CI/CD pipeline and container registry (ghcr.io)
- **Neon Database** - For PostgreSQL database (https://neon.tech)
- **Redpanda Cloud** (for cloud deployment) - For managed Kafka (https://redpanda.com)
- **Oracle Cloud** (optional) - For OKE deployment (https://cloud.oracle.com)

---

## Deployment Options

### Quick Comparison

| Feature | Local (Minikube) | Cloud (OKE) | CI/CD |
|---------|-----------------|-------------|-------|
| **Setup Time** | 15-20 min | 45-60 min | 10 min (after cloud setup) |
| **Cost** | Free | ~$50-100/month | Free (GitHub Actions) |
| **Use Case** | Development, Testing | Production | Automated deployments |
| **Scalability** | Limited (1 node) | High (auto-scaling) | N/A |
| **Availability** | Local only | High (99.9%) | N/A |
| **Kafka** | Local Redpanda | Redpanda Cloud | Configured via secrets |

---

## Option 1: Local Development (Minikube)

### Step 1: Prerequisites

Ensure all required tools are installed:
```bash
# Check all prerequisites
minikube version
kubectl version --client
helm version
dapr --version
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Database (use Neon free tier or local PostgreSQL)
DATABASE_URL="postgresql://user:password@host:5432/todo"

# Authentication secrets (generate random strings)
JWT_SECRET="your-jwt-secret-change-this"
BETTER_AUTH_SECRET="your-auth-secret-change-this"

# Optional: OpenAI API key for AI features
OPENAI_API_KEY="sk-proj-your-key-here"
```

**Generate secure secrets:**
```bash
# Generate random secrets
openssl rand -base64 32  # For JWT_SECRET
openssl rand -base64 32  # For BETTER_AUTH_SECRET
```

### Step 3: Run Automated Setup Script

We provide a fully automated setup script:

```bash
# Make script executable
chmod +x scripts/deployment/minikube-setup.sh

# Run setup
./scripts/deployment/minikube-setup.sh
```

The script will:
1. ✅ Check prerequisites (Minikube, kubectl, Helm, Dapr)
2. ✅ Start Minikube cluster (4 CPUs, 8GB RAM)
3. ✅ Initialize Dapr on Kubernetes
4. ✅ Install Redpanda (local Kafka)
5. ✅ Create Kafka topics (task-events, reminders)
6. ✅ Build Docker images (4 services)
7. ✅ Create Kubernetes secrets
8. ✅ Apply Dapr components
9. ✅ Deploy with Helm
10. ✅ Display access information

**Estimated time:** 15-20 minutes (depending on internet speed)

### Step 4: Access Application

After successful deployment, you'll see:

```
✓ Deployment Complete!

Access your Todo App:
  Frontend:    http://192.168.49.2:30080
  Backend API: http://192.168.49.2:30800
  API Docs:    http://192.168.49.2:30800/docs

Or use Minikube service command:
  minikube service todo-app-frontend -n todo-app
  minikube service todo-app-backend -n todo-app
```

**Open the frontend:**
```bash
# Opens browser automatically
minikube service todo-app-frontend -n todo-app
```

### Step 5: Verify Deployment

**Check pod status:**
```bash
kubectl get pods -n todo-app
```

Expected output:
```
NAME                                      READY   STATUS    RESTARTS   AGE
todo-app-backend-xxxxx                    2/2     Running   0          2m
todo-app-frontend-xxxxx                   2/2     Running   0          2m
todo-app-recurring-service-xxxxx          2/2     Running   0          2m
todo-app-notification-service-xxxxx       2/2     Running   0          2m
```

**Check services:**
```bash
kubectl get svc -n todo-app
```

**View logs:**
```bash
# Backend logs
kubectl logs -n todo-app -l app=backend -f

# Frontend logs
kubectl logs -n todo-app -l app=frontend -f

# Recurring service logs
kubectl logs -n todo-app -l app=recurring-service -f
```

**Check Dapr dashboard:**
```bash
dapr dashboard -k
```

Opens dashboard at http://localhost:8080

### Step 6: Test Features

1. **Sign up / Sign in** at http://localhost:3000
2. **Create a task** with:
   - Title: "Test recurring task"
   - Due date: Tomorrow at 3:00 PM
   - Priority: High
   - Tags: work, test
   - Recurrence: Daily
3. **Mark task complete** - New task should appear within 5-10 seconds
4. **Check reminder** - Wait for notification 15 minutes before due time
5. **Test search** - Search for "test" in search bar
6. **View dashboard** - Check statistics and calendar view

### Troubleshooting Local Deployment

**Problem: Pods stuck in ImagePullBackOff**
```bash
# Check image pull status
kubectl describe pod <pod-name> -n todo-app

# Verify images exist in Minikube's Docker
eval $(minikube docker-env)
docker images | grep todo-app
```

**Problem: Redpanda pods not starting**
```bash
# Check Redpanda logs
kubectl logs -n redpanda <redpanda-pod-name>

# Verify Redpanda service
kubectl get svc -n redpanda
```

**Problem: Database connection errors**
```bash
# Check database URL secret
kubectl get secret todo-secrets -n todo-app -o jsonpath='{.data.database-url}' | base64 -d

# Test database connection from pod
kubectl exec -it <backend-pod-name> -n todo-app -c backend -- python -c "
from sqlmodel import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
print('Connection successful!')
"
```

---

## Option 2: Cloud Deployment (Oracle OKE)

### Step 1: Set Up Oracle Cloud Account

1. **Sign up** for Oracle Cloud: https://cloud.oracle.com
   - New accounts get $300 free credits
   - Always Free tier available

2. **Create a compartment**:
   - Go to: Identity & Security > Compartments
   - Click "Create Compartment"
   - Name: `todo-app-compartment`
   - Copy the OCID (starts with `ocid1.compartment.oc1...`)

### Step 2: Create OKE Cluster

**Option A: Using OCI Console (Recommended)**

1. Navigate to: Developer Services > Kubernetes Clusters (OKE)
2. Click "Create Cluster"
3. Choose "Quick Create" workflow
4. Configure:
   - **Name**: `todo-app-cluster`
   - **Kubernetes version**: 1.28 or later
   - **Node pool**:
     - Shape: VM.Standard.E4.Flex
     - OCPUs: 2 per node
     - Memory: 16 GB per node
     - Node count: 3
   - **Networking**: Use default VCN and subnets
5. Click "Create Cluster" (takes 10-15 minutes)

**Option B: Using OCI CLI**

```bash
# Set variables
export COMPARTMENT_OCID="ocid1.compartment.oc1..."
export OCI_REGION="us-ashburn-1"

# Create VCN (if not exists)
oci network vcn create \
  --compartment-id "$COMPARTMENT_OCID" \
  --cidr-block "10.0.0.0/16" \
  --display-name "todo-app-vcn"

# Create OKE cluster
oci ce cluster create \
  --compartment-id "$COMPARTMENT_OCID" \
  --name "todo-app-cluster" \
  --kubernetes-version "v1.28.2" \
  --vcn-id "<vcn-ocid>"
```

### Step 3: Set Up Redpanda Cloud

1. **Sign up** for Redpanda Cloud: https://redpanda.com
   - Free tier: 10 GB storage, 10 MB/s throughput

2. **Create cluster**:
   - Click "Create Cluster"
   - Choose region close to your OKE cluster (e.g., AWS us-east-1)
   - Plan: BYOC (Bring Your Own Cloud) or Dedicated

3. **Create topics**:
   ```bash
   # In Redpanda console, create:
   - task-events (partitions: 3, retention: 7 days)
   - reminders (partitions: 1, retention: 1 day)
   ```

4. **Get connection details**:
   - Go to: Cluster > Connect
   - Copy **Bootstrap servers** (e.g., `broker.cloud.redpanda.com:9092`)
   - Copy **SASL credentials** (if using authentication)

### Step 4: Configure Environment Variables

Create a `.env.cloud` file:

```bash
# Oracle Cloud
export OCI_REGION="us-ashburn-1"
export COMPARTMENT_OCID="ocid1.compartment.oc1..."
export OKE_CLUSTER_NAME="todo-app-cluster"

# Redpanda Cloud
export REDPANDA_BROKERS="broker.cloud.redpanda.com:9092"

# Database (Neon PostgreSQL)
export DATABASE_URL="postgresql://user:password@ep-example.us-east-1.aws.neon.tech/todo"

# Authentication Secrets
export JWT_SECRET="$(openssl rand -base64 32)"
export BETTER_AUTH_SECRET="$(openssl rand -base64 32)"

# Optional
export OPENAI_API_KEY="sk-proj-your-key-here"

# Container Registry
export REGISTRY="ghcr.io"
export REGISTRY_USERNAME="your-github-username"
export IMAGE_TAG="v2.0.0"
```

**Load environment:**
```bash
source .env.cloud
```

### Step 5: Run Cloud Deployment Script

```bash
# Make script executable
chmod +x scripts/deployment/oracle-oke-setup.sh

# Run deployment
./scripts/deployment/oracle-oke-setup.sh
```

The script will:
1. ✅ Validate prerequisites and configuration
2. ✅ Configure kubectl for OKE
3. ✅ Install Dapr on Kubernetes
4. ✅ Create namespace and secrets
5. ✅ Apply Dapr components (with Redpanda Cloud brokers)
6. ✅ Deploy application with Helm
7. ✅ Wait for pods to be ready
8. ✅ Display LoadBalancer IPs

**Estimated time:** 10-15 minutes

### Step 6: Access Cloud Application

After deployment completes:

```bash
# Get LoadBalancer IPs
kubectl get svc -n todo-app

# Expected output:
NAME                   TYPE           EXTERNAL-IP      PORT(S)
todo-app-frontend      LoadBalancer   140.238.x.x      80:30080/TCP
todo-app-backend       LoadBalancer   140.238.y.y      80:30800/TCP
```

**Access application:**
- Frontend: http://140.238.x.x
- Backend API: http://140.238.y.y
- API Docs: http://140.238.y.y/docs

### Step 7: Configure DNS (Optional)

**Using Oracle DNS:**
1. Go to: Networking > DNS Zone Management
2. Create zone: `yourdomain.com`
3. Add A records:
   - `todo.yourdomain.com` → Frontend LoadBalancer IP
   - `api.yourdomain.com` → Backend LoadBalancer IP

**Using Cloudflare:**
1. Add A records in Cloudflare dashboard
2. Enable proxy (orange cloud) for HTTPS

### Step 8: Enable HTTPS (Optional)

Install cert-manager for automatic TLS certificates:

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

---

## Option 3: CI/CD with GitHub Actions

### Step 1: Fork Repository

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/todo-app.git
   cd todo-app/Phase05
   ```

### Step 2: Configure GitHub Secrets

Go to: Repository Settings > Secrets and variables > Actions

**Required Secrets:**

```yaml
# Oracle Cloud (if using OKE)
OKE_KUBECONFIG: <base64-encoded-kubeconfig>
COMPARTMENT_OCID: ocid1.compartment.oc1...

# Database
DATABASE_URL: postgresql://user:password@host:5432/todo

# Authentication
JWT_SECRET: <random-string>
BETTER_AUTH_SECRET: <random-string>

# Optional
OPENAI_API_KEY: sk-proj-...

# Kafka
KAFKA_BROKERS: broker.cloud.redpanda.com:9092
```

**How to get OKE_KUBECONFIG:**
```bash
# Generate kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file ~/.kube/oke-config \
  --region us-ashburn-1

# Base64 encode
cat ~/.kube/oke-config | base64 -w 0

# Copy output and add to GitHub Secrets
```

### Step 3: Push to Trigger Deployment

The CI/CD pipeline triggers on:
- Push to `main` branch
- Push to `001-advanced-features-event-driven` branch
- Manual workflow dispatch

```bash
# Make changes
git add .
git commit -m "feat: add new feature"
git push origin main
```

### Step 4: Monitor Pipeline

1. Go to: Actions tab in GitHub repository
2. Click on the running workflow
3. Monitor job progress:
   - **Test** (3-5 min): Backend tests, frontend lint, build
   - **Build** (10-15 min): Build 4 Docker images, security scan
   - **Deploy** (5-10 min): Deploy to Kubernetes cluster
   - **Cleanup** (1-2 min): Delete old container images

### Step 5: Manual Deployment

For manual deployment to specific environment:

1. Go to: Actions > Deploy Todo App to Cloud
2. Click "Run workflow"
3. Select:
   - Branch: `main`
   - Environment: `staging` or `production`
4. Click "Run workflow"

### Pipeline Architecture

```
┌─────────────┐
│    Push     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Test     │  ← Run pytest, ESLint, build frontend
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Build    │  ← Build 4 Docker images, security scan
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Deploy    │  ← Deploy to OKE with Helm
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Cleanup   │  ← Delete old images (keep 5 latest)
└─────────────┘
```

---

## Post-Deployment Configuration

### 1. Verify All Services

```bash
# Check all pods
kubectl get pods -n todo-app

# Check Dapr sidecars
kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'

# Expected: Each pod should have 2 containers (app + daprd)
```

### 2. Test Event-Driven Features

**Test Recurring Tasks:**
```bash
# Create a recurring task via API
curl -X POST http://<backend-url>/api/<user-id>/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily standup",
    "due_date": "2026-02-01T10:00:00Z",
    "recurrence": "daily",
    "priority": "medium"
  }'

# Mark task complete
curl -X PUT http://<backend-url>/api/<user-id>/tasks/<task-id>/complete

# Check logs to see new task creation
kubectl logs -n todo-app -l app=recurring-service -f
```

**Test Reminders:**
```bash
# Create task with due date 15 minutes from now
# Wait and check notification service logs
kubectl logs -n todo-app -l app=notification-service -f
```

### 3. Configure Monitoring (Optional)

**Install Prometheus + Grafana:**
```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

Open: http://localhost:3000 (default: admin/prom-operator)

**Import Dapr dashboard:**
1. Download: https://github.com/dapr/dapr/blob/master/grafana/grafana-dapr-dashboard.json
2. Import in Grafana: Dashboards > Import > Upload JSON

### 4. Set Up Alerting

**Create PrometheusRule:**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: todo-app-alerts
  namespace: todo-app
spec:
  groups:
  - name: todo-app
    interval: 30s
    rules:
    - alert: HighErrorRate
      expr: sum(rate(http_requests_total{status=~"5.."}[5m])) > 0.05
      for: 5m
      annotations:
        summary: "High error rate detected"
    - alert: PodDown
      expr: kube_pod_status_phase{namespace="todo-app",phase!="Running"} > 0
      for: 5m
      annotations:
        summary: "Pod is not running"
```

---

## Troubleshooting

### Common Issues

#### 1. Pods Stuck in Pending State

**Symptom:**
```bash
kubectl get pods -n todo-app
# todo-app-backend-xxx   0/2   Pending   0   5m
```

**Diagnosis:**
```bash
kubectl describe pod <pod-name> -n todo-app
```

**Solutions:**
- **Insufficient resources**: Scale down or increase cluster capacity
- **ImagePullBackOff**: Check image name and registry credentials
- **PVC not bound**: Check storage class exists

#### 2. Dapr Sidecar Not Injected

**Symptom:** Pods show 1/1 READY instead of 2/2

**Diagnosis:**
```bash
kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'
```

**Solutions:**
- Verify Dapr installation: `dapr status -k`
- Check deployment annotations:
  ```yaml
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "todo-backend"
    dapr.io/app-port: "8000"
  ```

#### 3. Database Connection Errors

**Symptom:** Backend logs show `sqlalchemy.exc.OperationalError`

**Diagnosis:**
```bash
# Check secret
kubectl get secret todo-secrets -n todo-app -o jsonpath='{.data.database-url}' | base64 -d

# Test connection
kubectl exec -it <backend-pod> -n todo-app -c backend -- python -c "
from sqlmodel import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    print('Connection successful!')
"
```

**Solutions:**
- Verify DATABASE_URL format: `postgresql://user:password@host:5432/dbname`
- Check database allows connections from cluster IPs
- Verify Neon database is not sleeping (free tier)

#### 4. Kafka Connection Errors

**Symptom:** Services can't connect to Kafka

**Diagnosis:**
```bash
# Check pubsub component
kubectl get component pubsub -n todo-app -o yaml

# Test from pod
kubectl exec -it <backend-pod> -n todo-app -c backend -- python -c "
from dapr.clients import DaprClient
with DaprClient() as client:
    print('Dapr client connected')
"
```

**Solutions:**
- Verify REDPANDA_BROKERS format: `broker.example.com:9092`
- Check Redpanda Cloud connectivity
- Verify Dapr pubsub component is applied
- Check topics exist

#### 5. LoadBalancer Stuck in Pending

**Symptom:**
```bash
kubectl get svc -n todo-app
# EXTERNAL-IP shows <pending>
```

**Solutions:**
- **Oracle OKE**: Check service limits for load balancers
- **GKE**: Enable Cloud Load Balancing API
- **Minikube**: Use `minikube tunnel` in separate terminal

### Debug Commands

```bash
# Check all resources
kubectl get all -n todo-app

# Describe pod for events
kubectl describe pod <pod-name> -n todo-app

# View logs (last 100 lines)
kubectl logs <pod-name> -n todo-app -c <container-name> --tail=100

# View Dapr sidecar logs
kubectl logs <pod-name> -n todo-app -c daprd

# Execute command in pod
kubectl exec -it <pod-name> -n todo-app -c <container-name> -- bash

# Check Dapr components
kubectl get components -n todo-app

# Check Dapr status
dapr status -k

# Port forward to service
kubectl port-forward svc/todo-app-backend -n todo-app 8000:80
```

---

## Monitoring & Observability

### Application Metrics

**Dapr Metrics (Prometheus format):**
- Available at: `http://<pod-ip>:9090/metrics`
- Metrics include:
  - `dapr_http_server_request_count`
  - `dapr_grpc_io_server_completed_rpcs`
  - `dapr_component_pubsub_ingress_count`
  - `dapr_component_pubsub_egress_count`

**Custom Application Metrics:**
- Add Prometheus client to backend:
  ```python
  from prometheus_client import Counter, Histogram

  task_created = Counter('tasks_created_total', 'Total tasks created')
  task_completed = Counter('tasks_completed_total', 'Total tasks completed')
  ```

### Logging

**Centralized Logging with Loki:**
```bash
# Install Loki stack
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set grafana.enabled=true \
  --set prometheus.enabled=true \
  --set promtail.enabled=true
```

**View logs in Grafana:**
1. Open Grafana: `kubectl port-forward -n monitoring svc/loki-grafana 3000:80`
2. Add Loki data source: http://loki:3100
3. Explore logs: `{namespace="todo-app"}`

### Tracing

**Enable Dapr Tracing:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: tracing
  namespace: todo-app
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin.default.svc.cluster.local:9411/api/v2/spans"
```

**Install Zipkin:**
```bash
kubectl create deployment zipkin --image openzipkin/zipkin
kubectl expose deployment zipkin --type ClusterIP --port 9411

# Access Zipkin UI
kubectl port-forward svc/zipkin 9411:9411
```

Open: http://localhost:9411

### Health Checks

**Liveness and Readiness Probes:**
Already configured in Helm templates:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

**Test health endpoint:**
```bash
curl http://<backend-url>/health
# Expected: {"status": "healthy", "database": "connected"}
```

---

## Next Steps

1. **Set up custom domain** - Configure DNS and TLS certificates
2. **Enable monitoring** - Install Prometheus + Grafana
3. **Set up alerts** - Configure alerting rules
4. **Backup database** - Set up automated backups for Neon DB
5. **Scale services** - Increase replicas for high availability
6. **CI/CD enhancements** - Add staging/production environments
7. **Performance testing** - Load test with k6 or Locust

---

## Additional Resources

- **Project README**: [README.md](../README.md)
- **Architecture Diagram**: [architecture-diagram.md](./architecture-diagram.md)
- **Event Schemas**: [event-schemas.md](./event-schemas.md)
- **Dapr Components**: [dapr-components.md](./dapr-components.md)
- **GitHub Secrets Setup**: [GITHUB_SECRETS.md](./GITHUB_SECRETS.md)
- **CI/CD Architecture**: [CICD_ARCHITECTURE.md](./CICD_ARCHITECTURE.md)

---

**Support:**
- Issues: https://github.com/your-username/todo-app/issues
- Documentation: ./docs/
- Dapr Docs: https://docs.dapr.io
- Kubernetes Docs: https://kubernetes.io/docs

---

🚀 Generated with [Claude Code](https://claude.com/claude-code)

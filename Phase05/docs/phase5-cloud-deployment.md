# Phase 5 Cloud Deployment Guide

**Estimated Time**: 45 minutes
**Prerequisites**: Oracle Cloud account, Redpanda Cloud account, Neon DB, GitHub account

This guide walks you through deploying the TODO application with event-driven architecture to Oracle Cloud Infrastructure (OKE) and Redpanda Cloud.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Redpanda Cloud Setup (T098-T104)](#redpanda-cloud-setup)
3. [Oracle Cloud OKE Setup (T105-T111)](#oracle-cloud-oke-setup)
4. [Kubernetes Secrets Configuration (T110)](#kubernetes-secrets-configuration)
5. [Dapr Components Deployment (T111)](#dapr-components-deployment)
6. [Application Deployment via Helm](#application-deployment-via-helm)
7. [GitHub Actions CI/CD Setup (T112-T121)](#github-actions-cicd-setup)
8. [DNS & Ingress Configuration](#dns--ingress-configuration)
9. [Monitoring & Observability](#monitoring--observability)
10. [Troubleshooting Common Issues](#troubleshooting-common-issues)
11. [Scaling & Production Best Practices](#scaling--production-best-practices)

---

## Prerequisites

### Required Accounts
- ✅ **Oracle Cloud** account ([cloud.oracle.com](https://cloud.oracle.com)) - Always Free tier eligible
- ✅ **Redpanda Cloud** account ([redpanda.com/cloud](https://redpanda.com/cloud)) - Serverless tier free
- ✅ **Neon PostgreSQL** database ([neon.tech](https://neon.tech)) - Free tier with 0.5 GB storage
- ✅ **GitHub** account for CI/CD pipeline

### Required CLI Tools
Install these tools on your local machine:

```bash
# kubectl (Kubernetes CLI)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# OCI CLI (Oracle Cloud CLI)
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Helm (Kubernetes package manager)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# GitHub CLI (optional but recommended)
brew install gh  # macOS
# or
sudo apt install gh  # Ubuntu
```

### Verify Installations
```bash
kubectl version --client
oci --version
helm version
dapr --version
gh --version
```

---

## Redpanda Cloud Setup

**Tasks**: T098-T104 | **Time**: ~10 minutes

### Step 1: Sign Up for Redpanda Cloud (T098)

1. Navigate to [https://redpanda.com/cloud](https://redpanda.com/cloud)
2. Click "Start Free" or "Sign Up"
3. Create account with email/password or GitHub OAuth
4. Verify email if required

### Step 2: Create Serverless Cluster (T099)

1. After login, click "Create Cluster"
2. Select **"Serverless"** tier (FREE - no credit card required)
3. Configure cluster:
   - **Name**: `todo-app-cluster`
   - **Cloud Provider**: AWS (recommended for free tier)
   - **Region**: Choose closest to Oracle OKE region (e.g., `us-east-1`)
4. Click "Create Cluster"
5. Wait 2-3 minutes for cluster provisioning

**Checkpoint**: You should see cluster status: "Ready"

### Step 3: Create Kafka Topics (T100-T102)

In the Redpanda console, navigate to "Topics" tab:

#### Topic 1: task-events (T100)
```yaml
Name: task-events
Partitions: 3
Replication factor: 1 (serverless default)
Retention: 7 days
```

#### Topic 2: task-updates (T101)
```yaml
Name: task-updates
Partitions: 3
Replication factor: 1
Retention: 7 days
```

#### Topic 3: reminders (T102)
```yaml
Name: reminders
Partitions: 1
Replication factor: 1
Retention: 24 hours
```

**CLI Alternative**:
```bash
# Install rpk (Redpanda CLI)
brew install redpanda-data/tap/redpanda

# Create topics
rpk topic create task-events -p 3 -X brokers=<bootstrap-server>
rpk topic create task-updates -p 3 -X brokers=<bootstrap-server>
rpk topic create reminders -p 1 -X brokers=<bootstrap-server>
```

### Step 4: Get Connection Credentials (T103)

1. In Redpanda console, go to "Security" → "Users & ACLs"
2. Click "Create User"
3. Username: `todo-app-user`
4. Create user and save credentials:
   - **Username**: `todo-app-user`
   - **Password**: (auto-generated, SAVE THIS)
   - **Mechanism**: `SCRAM-SHA-256`

5. Copy **Bootstrap Server URL**:
   - Format: `seed-12345-a1b2c3.redpanda.cloud:9092`
   - Find this in "Overview" → "Connection Details"

**Save these values**:
```bash
REDPANDA_BROKERS="seed-12345-a1b2c3.redpanda.cloud:9092"
REDPANDA_USERNAME="todo-app-user"
REDPANDA_PASSWORD="<generated-password>"
REDPANDA_MECHANISM="SCRAM-SHA-256"
```

### Step 5: Test Connection (T104)

```bash
# Test connectivity with rpk
rpk topic list \
  -X brokers=$REDPANDA_BROKERS \
  -X security.protocol=SASL_SSL \
  -X sasl.mechanism=$REDPANDA_MECHANISM \
  -X sasl.username=$REDPANDA_USERNAME \
  -X sasl.password=$REDPANDA_PASSWORD
```

**Expected Output**:
```
NAME          PARTITIONS  REPLICAS
task-events   3           1
task-updates  3           1
reminders     1           1
```

**Checkpoint**: ✅ Redpanda Cloud setup complete. You have 3 topics and valid SASL credentials.

---

## Oracle Cloud OKE Setup

**Tasks**: T105-T111 | **Time**: ~20 minutes

### Step 1: Sign Up for Oracle Cloud (T105)

1. Navigate to [https://cloud.oracle.com](https://cloud.oracle.com)
2. Click "Sign up for Oracle Cloud" (Always Free tier)
3. Complete registration:
   - Email, password, country
   - Credit card required for verification (not charged for Always Free resources)
4. Verify email and complete account setup

### Step 2: Configure OCI CLI (T106-T107)

```bash
# Configure OCI CLI
oci setup config

# Follow prompts to enter:
# - User OCID (find in Profile → User Settings)
# - Tenancy OCID (find in Profile → Tenancy)
# - Region (e.g., us-ashburn-1)
# - Generate API key pair (hit Enter to use defaults)

# Test configuration
oci iam region list
```

### Step 3: Create OKE Cluster (T106)

#### Option A: Via Oracle Cloud Console (Recommended)

1. Login to Oracle Cloud console
2. Navigate: **Menu** → **Developer Services** → **Kubernetes Clusters (OKE)**
3. Click **"Create Cluster"**
4. Select **"Quick Create"** (easier setup)
5. Configure cluster:
   - **Name**: `todo-app-cluster`
   - **Kubernetes version**: Latest (1.28+)
   - **Visibility Type**: Public Endpoint
   - **Shape**: `VM.Standard.E2.1.Micro` (Always Free eligible)
   - **Number of nodes**: 2
   - **Choose VCN**: Create new VCN with public subnet
6. Click **"Next"** → **"Create Cluster"**
7. Wait 10-15 minutes for cluster creation

#### Option B: Via OCI CLI

```bash
# Set variables
COMPARTMENT_ID="<your-compartment-ocid>"
VCN_ID="<your-vcn-ocid>"  # Or create new VCN first

# Create OKE cluster
oci ce cluster create \
  --compartment-id $COMPARTMENT_ID \
  --name todo-app-cluster \
  --kubernetes-version v1.28.2 \
  --vcn-id $VCN_ID
```

**Checkpoint**: Cluster status should be "Active" (green checkmark)

### Step 4: Configure kubectl for OKE (T107)

```bash
# Get cluster OCID from console or CLI
CLUSTER_ID="<your-cluster-ocid>"

# Generate kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id $CLUSTER_ID \
  --file $HOME/.kube/config \
  --region us-ashburn-1 \
  --token-version 2.0.0

# Verify connectivity
kubectl cluster-info
kubectl get nodes
```

**Expected Output**:
```
NAME                                STATUS   ROLES    AGE   VERSION
oke-c4rmqpqx5eq-nytdxajqpfa-0       Ready    <none>   5m    v1.28.2
oke-c4rmqpqx5eq-nytdxajqpfa-1       Ready    <none>   5m    v1.28.2
```

### Step 5: Install Dapr on OKE (T108)

```bash
# Initialize Dapr on Kubernetes
dapr init -k

# Verify Dapr components
kubectl get pods -n dapr-system
```

**Expected Output**:
```
NAME                                     READY   STATUS    RESTARTS   AGE
dapr-dashboard-xxx                       1/1     Running   0          2m
dapr-operator-xxx                        1/1     Running   0          2m
dapr-placement-server-xxx                1/1     Running   0          2m
dapr-sentry-xxx                          1/1     Running   0          2m
dapr-sidecar-injector-xxx                1/1     Running   0          2m
```

### Step 6: Create Application Namespace (T109)

```bash
# Create namespace
kubectl create namespace todo-app

# Label for Dapr sidecar injection
kubectl label namespace todo-app dapr-injection=enabled

# Verify namespace
kubectl get namespace todo-app --show-labels
```

**Checkpoint**: ✅ OKE cluster ready with Dapr installed and todo-app namespace created.

---

## Kubernetes Secrets Configuration

**Task**: T110 | **Time**: ~5 minutes

### Create Secrets with Actual Values

Replace placeholder values with your actual credentials:

```bash
# 1. Neon Database Credentials
kubectl create secret generic neon-db-creds \
  --from-literal=connectionString="postgresql://user:password@ep-cool-cloud-123456.us-east-2.aws.neon.tech/neondb?sslmode=require" \
  -n todo-app

# 2. Redpanda Cloud Credentials
kubectl create secret generic redpanda-creds \
  --from-literal=brokers="seed-12345-a1b2c3.redpanda.cloud:9092" \
  --from-literal=username="todo-app-user" \
  --from-literal=password="<your-redpanda-password>" \
  --from-literal=mechanism="SCRAM-SHA-256" \
  -n todo-app

# 3. OpenAI/Gemini API Key
kubectl create secret generic openai-key \
  --from-literal=apiKey="sk-proj-..." \
  -n todo-app

# 4. Authentication Secrets
JWT_SECRET=$(openssl rand -hex 32)
BETTER_AUTH_SECRET=$(openssl rand -hex 32)

kubectl create secret generic auth-secrets \
  --from-literal=jwtSecret="$JWT_SECRET" \
  --from-literal=betterAuthSecret="$BETTER_AUTH_SECRET" \
  -n todo-app
```

### Verify Secrets

```bash
kubectl get secrets -n todo-app
```

**Expected Output**:
```
NAME                TYPE     DATA   AGE
neon-db-creds       Opaque   1      30s
redpanda-creds      Opaque   4      25s
openai-key          Opaque   1      20s
auth-secrets        Opaque   2      15s
```

**Security Note**: These secrets are base64-encoded but NOT encrypted at rest. For production, use:
- **Sealed Secrets** ([sealed-secrets](https://github.com/bitnami-labs/sealed-secrets))
- **External Secrets Operator** ([external-secrets](https://external-secrets.io/))
- **Oracle Vault** integration

---

## Dapr Components Deployment

**Task**: T111 | **Time**: ~3 minutes

Apply all 4 Dapr components from the repository:

```bash
# Navigate to project root
cd Phase05

# Apply Dapr components
kubectl apply -f k8s/components/ -n todo-app

# Verify components
dapr components -k -n todo-app
```

**Expected Output**:
```
NAMESPACE  NAME            TYPE                   VERSION  SCOPES
todo-app   pubsub          pubsub.kafka           v1       todo-backend, todo-recurring-service, todo-notification-service
todo-app   statestore      state.postgresql       v1       todo-backend, todo-recurring-service, todo-notification-service
todo-app   secretstore     secretstores.k8s       v1       todo-backend, todo-recurring-service, todo-notification-service
todo-app   reminder-cron   bindings.cron          v1       todo-notification-service
```

### Component Details

1. **pubsub.yaml** - Kafka (Redpanda) with SASL/TLS authentication
2. **statestore.yaml** - PostgreSQL state store using Neon DB
3. **secretstore.yaml** - Kubernetes secrets integration
4. **reminder-cron.yaml** - Cron binding triggering every 5 minutes

**Troubleshooting**: If components don't load, check:
```bash
kubectl logs -n dapr-system -l app=dapr-operator
```

---

## Application Deployment via Helm

**Time**: ~10 minutes

### Step 1: Build Docker Images

If deploying from local:

```bash
# Backend
cd backend
docker build -t ghcr.io/<your-username>/todo-backend:v2.0.0 .
docker push ghcr.io/<your-username>/todo-backend:v2.0.0

# Frontend
cd ../frontend
docker build -t ghcr.io/<your-username>/todo-frontend:v2.0.0 .
docker push ghcr.io/<your-username>/todo-frontend:v2.0.0

# Recurring Service
cd ../services/recurring-service
docker build -t ghcr.io/<your-username>/todo-recurring-service:v2.0.0 .
docker push ghcr.io/<your-username>/todo-recurring-service:v2.0.0

# Notification Service
cd ../services/notification-service
docker build -t ghcr.io/<your-username>/todo-notification-service:v2.0.0 .
docker push ghcr.io/<your-username>/todo-notification-service:v2.0.0
```

**Or** use GitHub Actions CI/CD (recommended - see next section).

### Step 2: Create Production Values

Create `helm/todo-app/values-production.yaml`:

```yaml
namespace:
  name: todo-app

backend:
  enabled: true
  replicaCount: 2
  image:
    repository: ghcr.io/<your-username>/todo-backend
    tag: v2.0.0
  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "512Mi"
      cpu: "500m"

frontend:
  enabled: true
  replicaCount: 2
  image:
    repository: ghcr.io/<your-username>/todo-frontend
    tag: v2.0.0

ingress:
  enabled: true
  host: todo.yourdomain.com
  tls:
    enabled: true
```

### Step 3: Deploy with Helm

```bash
cd Phase05

helm upgrade --install todo-app ./helm/todo-app \
  --namespace todo-app \
  --values helm/todo-app/values-production.yaml \
  --wait \
  --timeout 10m
```

### Step 4: Verify Deployment

```bash
# Check pods
kubectl get pods -n todo-app

# Expected output:
# NAME                                          READY   STATUS    RESTARTS   AGE
# todo-backend-7d4c8bf7b-xxxxx                  2/2     Running   0          2m
# todo-backend-7d4c8bf7b-yyyyy                  2/2     Running   0          2m
# todo-frontend-6b9f7c8d5-xxxxx                 1/1     Running   0          2m
# todo-frontend-6b9f7c8d5-yyyyy                 1/1     Running   0          2m
# todo-recurring-service-5d7b9c6f4-xxxxx        2/2     Running   0          2m
# todo-notification-service-8f4d7b9c6-xxxxx     2/2     Running   0          2m

# Check services
kubectl get svc -n todo-app

# Check Dapr sidecars
kubectl logs -n todo-app <backend-pod> -c daprd
```

**Checkpoint**: ✅ All pods should be Running with 2/2 containers (app + Dapr sidecar)

---

## GitHub Actions CI/CD Setup

**Tasks**: T112-T121 | **Time**: ~15 minutes

The repository includes a complete CI/CD pipeline in `.github/workflows/deploy.yml`.

### Required GitHub Secrets

Add these 12 secrets to your GitHub repository:

**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

#### Oracle Cloud (OCI) Secrets:
```
OCI_AUTH_TOKEN         = <your-oci-auth-token>
OCI_TENANCY_OCID       = ocid1.tenancy.oc1..xxx
OCI_USER_OCID          = ocid1.user.oc1..xxx
OCI_REGION             = us-ashburn-1
OKE_CLUSTER_ID         = ocid1.cluster.oc1..xxx
```

**Generate OCI Auth Token**:
1. Oracle Cloud Console → Profile → User Settings
2. Auth Tokens → Generate Token
3. Save token (shown only once)

#### Redpanda Cloud Secrets:
```
REDPANDA_BROKERS       = seed-12345-a1b2c3.redpanda.cloud:9092
REDPANDA_USERNAME      = todo-app-user
REDPANDA_PASSWORD      = <your-redpanda-password>
```

#### Database & Auth Secrets:
```
NEON_DB_URL           = postgresql://user:pass@ep-xxx.neon.tech/neondb
JWT_SECRET            = <generate-with-openssl-rand-hex-32>
BETTER_AUTH_SECRET    = <generate-with-openssl-rand-hex-32>
OPENAI_API_KEY        = sk-proj-xxx
```

### Pipeline Workflow

The pipeline triggers on:
- **Push to main** branch
- **Pull request** to main (build + test only)

**Stages**:
1. **Test** (15 min) - Pytest + ESLint
2. **Build** (30 min) - 4 Docker images (matrix strategy)
3. **Security Scan** (20 min) - Trivy vulnerability scanning
4. **Push to GHCR** (20 min) - GitHub Container Registry
5. **Deploy to OKE** (15 min) - Helm upgrade
6. **Smoke Tests** (10 min) - Health checks
7. **Notify** - Slack notification (optional)

### Trigger Deployment

```bash
# Method 1: Push to main
git push origin main

# Method 2: Manual trigger (if workflow_dispatch enabled)
gh workflow run deploy.yml

# View logs
gh run list
gh run view <run-id> --log
```

**See Also**: `docs/GITHUB_SECRETS.md` and `docs/CICD_ARCHITECTURE.md`

---

## DNS & Ingress Configuration

**Time**: ~10 minutes

### Step 1: Get Load Balancer IP

```bash
kubectl get svc -n ingress-nginx ingress-nginx-controller
```

Copy the `EXTERNAL-IP` value.

### Step 2: Configure DNS A Record

In your DNS provider (e.g., Cloudflare, Route53):

```
Type: A
Name: todo
Value: <EXTERNAL-IP-from-step-1>
TTL: 300
```

### Step 3: Install NGINX Ingress Controller

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/oci-load-balancer-shape"="flexible" \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/oci-load-balancer-shape-flex-min"="10" \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/oci-load-balancer-shape-flex-max"="100"
```

### Step 4: Install Cert-Manager (SSL/TLS)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create Let's Encrypt issuer
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

### Step 5: Update Ingress with TLS

Edit `helm/todo-app/templates/ingress.yaml` to include:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/websocket-services: "backend-service"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - todo.yourdomain.com
    secretName: todo-tls-cert
  rules:
  - host: todo.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 3000
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
```

**Checkpoint**: Visit https://todo.yourdomain.com - you should see the TODO app!

---

## Monitoring & Observability

### View Application Logs

```bash
# Backend logs
kubectl logs -n todo-app -l app=backend -c backend --tail=100 -f

# Dapr sidecar logs
kubectl logs -n todo-app -l app=backend -c daprd --tail=100 -f

# Frontend logs
kubectl logs -n todo-app -l app=frontend --tail=100 -f

# Recurring service logs
kubectl logs -n todo-app -l app=recurring-service -c recurring-service --tail=100 -f
```

### Check Dapr Component Status

```bash
# List components
dapr components -k -n todo-app

# Check component logs
kubectl logs -n dapr-system -l app=dapr-operator --tail=100
```

### Monitor Redpanda Metrics

1. Login to Redpanda Cloud console
2. Navigate to **Metrics** tab
3. View:
   - Messages per second
   - Consumer lag
   - Topic throughput

### Monitor Neon Database

1. Login to Neon console ([neon.tech](https://neon.tech))
2. Select your database
3. View **Monitoring** tab:
   - Active connections
   - Query performance
   - Storage usage

### Kubernetes Resource Monitoring

```bash
# Pod resource usage
kubectl top pods -n todo-app

# Node resource usage
kubectl top nodes

# Event logs
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

### Optional: Prometheus + Grafana

```bash
# Install Prometheus + Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Open http://localhost:3000 (admin/prom-operator)
```

---

## Troubleshooting Common Issues

### Issue 1: Pods Not Starting (ImagePullBackOff)

**Symptoms**:
```bash
kubectl get pods -n todo-app
# STATUS: ImagePullBackOff
```

**Diagnosis**:
```bash
kubectl describe pod <pod-name> -n todo-app
# Check "Events" section for error message
```

**Solutions**:
- Verify image exists: `docker pull <image-name>`
- Check image repository is public or authenticate:
  ```bash
  kubectl create secret docker-registry ghcr-secret \
    --docker-server=ghcr.io \
    --docker-username=<your-username> \
    --docker-password=<github-pat> \
    -n todo-app
  ```
- Update deployment to use imagePullSecrets

### Issue 2: Dapr Component Not Loading

**Symptoms**:
```bash
dapr components -k -n todo-app
# Component missing or error state
```

**Diagnosis**:
```bash
kubectl logs -n dapr-system -l app=dapr-operator
kubectl describe component pubsub -n todo-app
```

**Solutions**:

**A. Secret Not Found**:
```bash
# Verify secrets exist
kubectl get secrets -n todo-app

# Check secret keys match component
kubectl get secret redpanda-creds -n todo-app -o yaml
```

**B. Kafka Connection Failed**:
```bash
# Test from within cluster
kubectl run -it --rm kafka-test --image=edenhill/kcat:1.7.1 --restart=Never -- \
  -b $REDPANDA_BROKERS \
  -X security.protocol=SASL_SSL \
  -X sasl.mechanism=SCRAM-SHA-256 \
  -X sasl.username=$REDPANDA_USERNAME \
  -X sasl.password=$REDPANDA_PASSWORD \
  -L
```

**C. SASL Authentication Failed**:
- Verify SASL credentials are correct
- Check mechanism is `SCRAM-SHA-256` (not `PLAIN`)
- Ensure TLS is enabled: `enableTLS: "true"`

### Issue 3: Database Connection Timeout

**Symptoms**:
```
sqlalchemy.exc.OperationalError: could not connect to server: Connection timed out
```

**Solutions**:

**A. Check Neon IP Allowlist**:
1. Neon console → Database → Settings → Security
2. Add OKE node IPs to allowlist
3. Or enable "Allow all IPs" (not recommended for production)

**B. Verify Connection String**:
```bash
# Get connection string from secret
kubectl get secret neon-db-creds -n todo-app -o jsonpath='{.data.connectionString}' | base64 -d
```

**C. Test Connection from Pod**:
```bash
kubectl run -it --rm psql-test --image=postgres:15 --restart=Never -- \
  psql $NEON_DB_URL -c "SELECT version();"
```

### Issue 4: WebSocket Connection Refused

**Symptoms**:
```
WebSocket connection failed: 502 Bad Gateway
```

**Solutions**:

**A. Add Ingress WebSocket Annotations**:
```yaml
annotations:
  nginx.ingress.kubernetes.io/websocket-services: "backend-service"
  nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
  nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
```

**B. Verify Backend WebSocket Endpoint**:
```bash
kubectl logs -n todo-app -l app=backend -c backend | grep "WebSocket"
```

### Issue 5: Recurring Tasks Not Creating

**Symptoms**:
Complete a recurring task, but no new instance appears.

**Diagnosis**:
```bash
# Check if event published
kubectl logs -n todo-app -l app=backend -c backend | grep "task.completed"

# Check if recurring service received event
kubectl logs -n todo-app -l app=recurring-service -c recurring-service | grep "task.completed"

# Check Dapr pubsub subscription
kubectl get subscription -n todo-app
```

**Solutions**:

**A. Verify Dapr Subscription**:
```bash
# Should see subscription endpoint
curl http://localhost:3500/dapr/subscribe
```

**B. Check Kafka Topic Has Messages**:
```bash
# Use Redpanda console or rpk
rpk topic consume task-events --brokers=$REDPANDA_BROKERS
```

**C. Check Service Scopes Match**:
```yaml
# In pubsub.yaml
scopes:
- todo-backend          # Must match Dapr app-id
- todo-recurring-service
```

### Issue 6: Reminders Not Triggering

**Symptoms**:
Task due in 10 minutes, but no notification received.

**Diagnosis**:
```bash
# Check cron binding is loaded
dapr components -k -n todo-app | grep reminder-cron

# Check if cron is triggering
kubectl logs -n todo-app -l app=notification-service -c notification-service | grep "reminder-cron"

# Check database query results
kubectl exec -it -n todo-app <notification-pod> -- \
  python -c "import asyncio; from reminder_checker import check_and_send_reminders; asyncio.run(check_and_send_reminders())"
```

**Solutions**:

**A. Verify Cron Binding Endpoint**:
```bash
# POST endpoint must exist at /reminder-cron
curl -X POST http://<notification-service-ip>:8002/reminder-cron
```

**B. Check Database Query**:
```sql
SELECT * FROM tasks
WHERE due_date BETWEEN NOW() AND NOW() + INTERVAL '15 minutes'
  AND completed = false
  AND reminder_sent_at IS NULL;
```

---

## Scaling & Production Best Practices

### Horizontal Pod Autoscaling (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: todo-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

Apply HPA:
```bash
kubectl apply -f hpa.yaml
kubectl get hpa -n todo-app
```

### Resource Tuning

Based on actual usage, adjust resource requests/limits:

```yaml
# For backend (adjust based on metrics)
resources:
  requests:
    memory: "512Mi"  # Minimum needed
    cpu: "300m"      # 0.3 CPU cores
  limits:
    memory: "1Gi"    # Maximum allowed
    cpu: "1000m"     # 1 CPU core
```

**Monitor with**:
```bash
kubectl top pods -n todo-app
```

### Backup & Disaster Recovery

#### Database Backups (Neon)
- Neon automatically backs up every 24 hours
- Point-in-time restore available (up to 7 days)
- Manual snapshot: Neon console → Database → Backups → Create snapshot

#### Kubernetes Resources
```bash
# Backup all resources
kubectl get all -n todo-app -o yaml > backup-$(date +%Y%m%d).yaml

# Backup secrets (encrypted)
kubectl get secrets -n todo-app -o yaml > secrets-backup.yaml
# Store encrypted in secure location
```

#### Application Data
- Regular PostgreSQL dumps:
  ```bash
  pg_dump $NEON_DB_URL > backup-$(date +%Y%m%d).sql
  ```

### Cost Optimization (Always Free Tier)

**Oracle Cloud Always Free Limits**:
- 2 AMD Compute instances (VM.Standard.E2.1.Micro)
- 2 Block Volumes (100 GB total)
- 10 GB Object Storage
- 10 GB Archive Storage

**Optimization Tips**:
1. Use 2 nodes max (Always Free limit)
2. Set resource requests/limits to stay within VM capacity
3. Use Neon free tier (0.5 GB storage, 1 active branch)
4. Use Redpanda Serverless free tier
5. Enable HPA to scale down during low usage

**Monitor Costs**:
- Oracle Cloud Console → Billing → Cost Analysis
- Set up budget alerts

### Security Hardening

#### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
  namespace: todo-app
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 53  # DNS
```

#### Pod Security Standards
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: todo-app
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

#### Image Scanning
- Enable Trivy in CI/CD (already configured)
- Scan on schedule:
  ```bash
  trivy image ghcr.io/<username>/todo-backend:v2.0.0
  ```

---

## Summary

**Completed Tasks**:
- ✅ T098-T104: Redpanda Cloud setup
- ✅ T105-T111: Oracle Cloud OKE setup
- ✅ T112-T121: CI/CD pipeline (reference only)

**Total Deployment Time**: ~45 minutes

**Architecture**:
- 📊 **Kubernetes**: 2-node OKE cluster (Always Free)
- 🚀 **Services**: Backend, Frontend, Recurring, Notification (4 microservices)
- 📨 **Messaging**: Redpanda Cloud Kafka (Serverless)
- 🗄️ **Database**: Neon PostgreSQL (Serverless)
- 🔄 **Service Mesh**: Dapr v1.14 (pub/sub, state, secrets, cron)
- 🔐 **Security**: SASL/TLS, Network Policies, Pod Security Standards
- 📈 **Monitoring**: Prometheus + Grafana (optional)

**Next Steps**:
1. Test the application: https://todo.yourdomain.com
2. Run smoke tests (see `docs/cloud-testing-checklist.md`)
3. Monitor metrics and logs
4. Set up alerts for production

**References**:
- [Architecture Diagram](./architecture-diagram.md)
- [Event Schemas](./event-schemas.md)
- [Dapr Components](./dapr-components.md)
- [GitHub Secrets](./GITHUB_SECRETS.md)
- [CI/CD Architecture](./CICD_ARCHITECTURE.md)

---

**Status**: Cloud deployment guide complete | **Version**: 2.0.0 | **Last Updated**: 2026-01-29

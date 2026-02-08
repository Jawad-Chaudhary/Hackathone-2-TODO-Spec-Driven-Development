# Infrastructure Setup Guide

**Tasks**: T001-T005 | **Purpose**: Local Kubernetes + Dapr + Kafka Setup

This guide walks you through setting up the complete local development infrastructure for Phase 5 event-driven architecture.

---

## Prerequisites

- **OS**: Windows 10/11, macOS, or Linux
- **RAM**: 8GB minimum (16GB recommended)
- **CPU**: 4 cores minimum
- **Disk**: 20GB free space
- **Tools**: Docker Desktop, PowerShell/Terminal

---

## Step 1: Install Dapr CLI (T001)

### Windows (PowerShell as Administrator):

```powershell
# Install via PowerShell
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Verify installation
dapr --version
# Expected: CLI version: 1.14.0 or higher
```

### macOS (via Homebrew):

```bash
# Install Dapr CLI
brew install dapr/tap/dapr-cli

# Verify
dapr --version
```

### Linux:

```bash
# Download and install
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Verify
dapr --version
```

**Checkpoint**: Run `dapr --version` and confirm version ≥ 1.14.0

---

## Step 2: Install Helm 3 (T002)

### Windows (via Chocolatey):

```powershell
# Install Chocolatey if not already installed
# See: https://chocolatey.org/install

# Install Helm
choco install kubernetes-helm

# Verify
helm version
# Expected: version.BuildInfo{Version:"v3.14.0" or higher}
```

### macOS (via Homebrew):

```bash
# Install Helm
brew install helm

# Verify
helm version
```

### Linux:

```bash
# Download and install
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify
helm version
```

**Checkpoint**: Run `helm version` and confirm version ≥ v3.14.0

---

## Step 3: Start Minikube Cluster (T003)

### Prerequisites:

**Install Docker Desktop** (required for Minikube):
- Windows/Mac: https://www.docker.com/products/docker-desktop/
- Linux: Follow Docker Engine installation

**Install Minikube**:

```bash
# Windows (Chocolatey)
choco install minikube

# macOS (Homebrew)
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### Start Minikube with Recommended Resources:

```bash
# Start cluster with 4 CPUs and 8GB RAM
minikube start --cpus=4 --memory=8192 --driver=docker

# Wait for cluster to be ready (2-5 minutes)
# Expected output:
# ✅  Done! kubectl is now configured to use "minikube" cluster
```

### Verify Cluster:

```bash
# Check cluster status
minikube status
# Expected:
# minikube
# type: Control Plane
# host: Running
# kubelet: Running
# apiserver: Running

# Check nodes
kubectl get nodes
# Expected:
# NAME       STATUS   ROLES           AGE   VERSION
# minikube   Ready    control-plane   1m    v1.30.0
```

**Checkpoint**: Minikube cluster running with 4 CPUs and 8GB RAM

---

## Step 4: Initialize Dapr on Minikube (T004)

### Install Dapr into Kubernetes Cluster:

```bash
# Initialize Dapr in Kubernetes mode
dapr init -k

# This will install:
# - Dapr Operator
# - Dapr Sidecar Injector
# - Dapr Placement
# - Dapr Sentry (mTLS)

# Wait for installation (2-3 minutes)
# Expected output:
# ✅  Success! Dapr has been installed to namespace dapr-system
```

### Verify Dapr Installation:

```bash
# Check Dapr system pods
kubectl get pods -n dapr-system

# Expected output (all Running):
# NAME                                     READY   STATUS    AGE
# dapr-dashboard-xxxxx                     1/1     Running   1m
# dapr-operator-xxxxx                      1/1     Running   1m
# dapr-placement-server-0                  1/1     Running   1m
# dapr-sentry-xxxxx                        1/1     Running   1m
# dapr-sidecar-injector-xxxxx              1/1     Running   1m

# Check Dapr version
dapr status -k
# Expected:
# NAME                   NAMESPACE    HEALTHY  STATUS   VERSION  AGE
# dapr-operator          dapr-system  True     Running  1.14.0   1m
# dapr-sentry            dapr-system  True     Running  1.14.0   1m
# dapr-placement-server  dapr-system  True     Running  1.14.0   1m
# dapr-sidecar-injector  dapr-system  True     Running  1.14.0   1m
# dapr-dashboard         dapr-system  True     Running  0.14.0   1m
```

### Access Dapr Dashboard (Optional):

```bash
# Forward Dapr dashboard to localhost:9999
dapr dashboard -k

# Open browser: http://localhost:9999
# You'll see Dapr Components, Applications, etc.
```

**Checkpoint**: All Dapr system pods Running in `dapr-system` namespace

---

## Step 5: Install Redpanda Helm Chart (T005)

### Add Redpanda Helm Repository:

```bash
# Add Redpanda Helm repo
helm repo add redpanda https://charts.redpanda.com

# Update repos
helm repo update

# Verify repo added
helm search repo redpanda
# Expected:
# NAME                    CHART VERSION  APP VERSION  DESCRIPTION
# redpanda/redpanda       5.9.x          v24.x.x      Redpanda is a streaming data...
```

### Install Redpanda with Single Replica (Local Development):

```bash
# Create namespace for Redpanda
kubectl create namespace redpanda

# Install Redpanda Helm chart
helm install redpanda redpanda/redpanda \
  --namespace redpanda \
  --set statefulset.replicas=1 \
  --set resources.cpu.cores=1 \
  --set resources.memory.container.max=2Gi \
  --set storage.persistentVolume.size=10Gi \
  --set auth.sasl.enabled=false \
  --set tls.enabled=false \
  --wait \
  --timeout=10m

# Wait for deployment (5-10 minutes)
# Expected output:
# NAME: redpanda
# STATUS: deployed
```

### Verify Redpanda Installation:

```bash
# Check Redpanda pods
kubectl get pods -n redpanda

# Expected output:
# NAME         READY   STATUS    AGE
# redpanda-0   2/2     Running   5m

# Check Redpanda service
kubectl get svc -n redpanda

# Expected:
# NAME                TYPE        CLUSTER-IP      PORT(S)
# redpanda            ClusterIP   10.96.x.x       9092,8082,8081,9644
# redpanda-external   NodePort    10.96.x.x       9092:30092/TCP
```

### Create Kafka Topics:

```bash
# Port-forward to Redpanda
kubectl port-forward -n redpanda svc/redpanda 9092:9092 &

# Install rpk CLI (Redpanda CLI)
# Windows (Chocolatey):
choco install rpk

# macOS (Homebrew):
brew install redpanda-data/tap/redpanda

# Linux:
curl -LO https://github.com/redpanda-data/redpanda/releases/latest/download/rpk-linux-amd64.zip
unzip rpk-linux-amd64.zip -d /usr/local/bin/

# Create topics
rpk topic create task-events --brokers localhost:9092 --partitions 3
rpk topic create task-updates --brokers localhost:9092 --partitions 3
rpk topic create reminders --brokers localhost:9092 --partitions 1

# Verify topics
rpk topic list --brokers localhost:9092
# Expected:o 
# NAME           PARTITIONS  REPLICAS
# task-events    3           1
# task-updates   3           1
# reminders      1           1
```

**Checkpoint**: Redpanda running with 3 topics created

---

## Verification Checklist

After completing all steps, verify your setup:

```bash
# 1. Dapr CLI installed
dapr --version
# ✅ v1.14.0+

# 2. Helm installed
helm version
# ✅ v3.14.0+

# 3. Minikube running
minikube status
# ✅ Running

# 4. Dapr in Kubernetes
dapr status -k
# ✅ All components Running

# 5. Redpanda running
kubectl get pods -n redpanda
# ✅ redpanda-0 2/2 Running

# 6. Topics created
rpk topic list --brokers localhost:9092
# ✅ task-events, task-updates, reminders
```

---

## Common Issues & Solutions

### Issue 1: Minikube won't start

**Error**: `Exiting due to MK_USAGE: Docker driver not running`

**Solution**:
```bash
# Ensure Docker Desktop is running
docker ps

# If Docker not running, start Docker Desktop application
# Then retry:
minikube start --cpus=4 --memory=8192 --driver=docker
```

---

### Issue 2: Insufficient memory

**Error**: `Requested memory allocation (8192MB) exceeds your system limits`

**Solution**:
```bash
# Start with less memory (minimum 6GB)
minikube start --cpus=2 --memory=6144 --driver=docker

# Or increase Docker Desktop memory allocation:
# Docker Desktop → Settings → Resources → Memory → Set to 10GB
```

---

### Issue 3: Dapr init fails

**Error**: `error installing Dapr: context deadline exceeded`

**Solution**:
```bash
# Delete and retry
dapr uninstall -k
dapr init -k --wait --timeout 600

# Check internet connection (Dapr downloads images)
```

---

### Issue 4: Redpanda pod CrashLoopBackOff

**Error**: Pod status shows `CrashLoopBackOff`

**Solution**:
```bash
# Check pod logs
kubectl logs redpanda-0 -n redpanda -c redpanda

# Common fix: Increase resources
helm upgrade redpanda redpanda/redpanda \
  --namespace redpanda \
  --set resources.memory.container.max=3Gi \
  --reuse-values

# Or restart with clean state
helm uninstall redpanda -n redpanda
kubectl delete pvc data-redpanda-0 -n redpanda
# Then reinstall (see Step 5)
```

---

### Issue 5: kubectl not found

**Error**: `kubectl: command not found`

**Solution**:
```bash
# Minikube includes kubectl
minikube kubectl -- get pods

# Or install kubectl separately:
# Windows: choco install kubernetes-cli
# macOS: brew install kubectl
# Linux: sudo snap install kubectl --classic
```

---

## Next Steps

After infrastructure is ready:

1. **Apply Dapr Components**:
   ```bash
   kubectl apply -f k8s/components/ -n todo-app
   ```

2. **Deploy Services**:
   ```bash
   helm install todo-app ./helm/todo-app -n todo-app --create-namespace
   ```

3. **Test Event Flow**:
   ```bash
   # Complete a recurring task
   # Check logs for event publishing
   kubectl logs -l app=recurring-service -n todo-app
   ```

---

## Resource Cleanup (When Done)

```bash
# Stop Minikube (preserves cluster state)
minikube stop

# Delete Minikube cluster (removes everything)
minikube delete

# Uninstall Dapr
dapr uninstall -k

# Remove Helm releases
helm uninstall redpanda -n redpanda
helm uninstall todo-app -n todo-app
```

---

## Summary

**Total Setup Time**: 20-30 minutes (first time)

**System Resources**:
- Minikube: 4 CPUs, 8GB RAM
- Redpanda: 1 CPU, 2GB RAM
- Dapr: ~500MB RAM
- **Total**: ~11GB RAM

**Ports Used**:
- 9092: Kafka broker (Redpanda)
- 8080: Dapr HTTP (per service)
- 50001: Dapr gRPC (per service)
- 9999: Dapr Dashboard

**What You Have Now**:
- ✅ Local Kubernetes cluster (Minikube)
- ✅ Dapr runtime with sidecar injection
- ✅ Kafka-compatible message broker (Redpanda)
- ✅ 3 Kafka topics for events
- ✅ Ready for microservices deployment

---

## References

- [Dapr Documentation](https://docs.dapr.io/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Redpanda Documentation](https://docs.redpanda.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

---

**Status**: Infrastructure setup guide complete for T001-T005

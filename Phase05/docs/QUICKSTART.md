# Todo App - Quick Start Guide

Get your Todo App running in **15 minutes** with this streamlined guide.

---

## 🚀 Choose Your Path

### Path 1: Local Development (Minikube) - **Recommended for Testing**

**Time:** 15-20 minutes | **Cost:** Free

Perfect for development, testing, and learning Kubernetes.

### Path 2: Cloud Deployment (Oracle OKE) - **Recommended for Production**

**Time:** 45-60 minutes | **Cost:** ~$50-100/month

Production-ready deployment with auto-scaling and high availability.

### Path 3: CI/CD with GitHub Actions - **Recommended for Teams**

**Time:** 10 minutes (after cloud setup) | **Cost:** Free

Automated deployments on every git push.

---

## Path 1: Local Development (Minikube)

### Prerequisites (5 minutes)

Install required tools:

```bash
# macOS
brew install minikube kubectl helm
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Windows (with Chocolatey)
choco install minikube kubernetes-cli kubernetes-helm
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### Setup Database (2 minutes)

1. **Sign up for Neon** (free tier): https://neon.tech
2. **Create database**: Click "Create Project" > Name: "todo-app"
3. **Copy connection string**:
   ```
   postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/todo
   ```

### Configure Environment (1 minute)

Create `.env` file in project root:

```bash
DATABASE_URL="postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/todo"
JWT_SECRET="$(openssl rand -base64 32)"
BETTER_AUTH_SECRET="$(openssl rand -base64 32)"
```

### Deploy (10 minutes)

Run the automated setup script:

```bash
chmod +x scripts/deployment/minikube-setup.sh
./scripts/deployment/minikube-setup.sh
```

The script handles everything:
- ✅ Start Minikube cluster
- ✅ Install Dapr
- ✅ Install Redpanda (Kafka)
- ✅ Build Docker images
- ✅ Deploy application

### Access Application (30 seconds)

```bash
# Opens browser automatically
minikube service todo-app-frontend -n todo-app
```

Or visit: http://192.168.49.2:30080

**Done!** 🎉

---

## Path 2: Cloud Deployment (Oracle OKE)

### Prerequisites (10 minutes)

1. **Oracle Cloud Account**: https://cloud.oracle.com (Free $300 credits)
2. **Redpanda Cloud Account**: https://redpanda.com (Free tier available)
3. **Neon Database**: https://neon.tech (Free tier)

Install tools:

```bash
# Install OCI CLI
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Install kubectl, helm, dapr
brew install kubectl helm
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

### Create OKE Cluster (15 minutes)

**Option A: Using Console (Easy)**

1. Go to: OCI Console > Developer Services > Kubernetes Clusters (OKE)
2. Click "Create Cluster" > Choose "Quick Create"
3. Configure:
   - **Name**: `todo-app-cluster`
   - **Kubernetes version**: 1.28+
   - **Node pool**: 3 nodes, VM.Standard.E4.Flex (2 OCPUs, 16GB RAM)
4. Click "Create Cluster" (takes 10-15 minutes)

**Option B: Using CLI (Fast)**

```bash
# Set compartment OCID (get from OCI Console)
export COMPARTMENT_OCID="ocid1.compartment.oc1..."

# Create cluster
oci ce cluster create \
  --compartment-id "$COMPARTMENT_OCID" \
  --name "todo-app-cluster" \
  --kubernetes-version "v1.28.2"
```

### Setup Redpanda Cloud (5 minutes)

1. **Create cluster**: https://cloud.redpanda.com
2. **Create topics**:
   - `task-events` (3 partitions, 7 days retention)
   - `reminders` (1 partition, 1 day retention)
3. **Copy bootstrap servers**: `broker.cloud.redpanda.com:9092`

### Configure Environment (2 minutes)

```bash
# Get OKE cluster OCID from console or CLI
export COMPARTMENT_OCID="ocid1.compartment.oc1..."
export OKE_CLUSTER_NAME="todo-app-cluster"
export REDPANDA_BROKERS="broker.cloud.redpanda.com:9092"
export DATABASE_URL="postgresql://user:password@ep-xxx.neon.tech/todo"
export JWT_SECRET="$(openssl rand -base64 32)"
export BETTER_AUTH_SECRET="$(openssl rand -base64 32)"
export REGISTRY_USERNAME="your-github-username"
```

### Deploy (10 minutes)

```bash
chmod +x scripts/deployment/oracle-oke-setup.sh
./scripts/deployment/oracle-oke-setup.sh
```

### Access Application (1 minute)

Get LoadBalancer IPs:

```bash
kubectl get svc -n todo-app
```

Visit: http://<EXTERNAL-IP>

**Done!** 🚀

---

## Path 3: CI/CD with GitHub Actions

### Prerequisites (2 minutes)

- GitHub account
- Cloud cluster (OKE/GKE/AKS) already set up
- kubectl configured for your cluster

### Setup GitHub Secrets (5 minutes)

Go to: Repository Settings > Secrets and variables > Actions

Add these secrets:

```yaml
# Get kubeconfig and encode
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file ~/.kube/oke-config \
  --region us-ashburn-1

# Base64 encode for GitHub secret
cat ~/.kube/oke-config | base64 -w 0
```

Add to GitHub Secrets:

- `OKE_KUBECONFIG`: (base64 encoded kubeconfig)
- `DATABASE_URL`: (Neon PostgreSQL URL)
- `JWT_SECRET`: (random string)
- `BETTER_AUTH_SECRET`: (random string)
- `KAFKA_BROKERS`: (Redpanda Cloud brokers)
- `COMPARTMENT_OCID`: (Oracle compartment OCID)

### Trigger Deployment (1 minute)

Push to main branch:

```bash
git add .
git commit -m "feat: deploy to production"
git push origin main
```

Or manually trigger:
1. Go to: Actions > Deploy Todo App to Cloud
2. Click "Run workflow"
3. Select branch: `main`
4. Click "Run workflow"

### Monitor Deployment (5 minutes)

Watch the pipeline:
1. Go to: Actions tab
2. Click on the running workflow
3. Monitor: Test → Build → Deploy → Cleanup

**Done!** ✅

---

## Verification Checklist

After deployment, verify everything works:

### 1. Check Pods Status

```bash
kubectl get pods -n todo-app

# Expected: All pods show 2/2 READY
# todo-app-backend-xxx              2/2   Running
# todo-app-frontend-xxx             2/2   Running
# todo-app-recurring-service-xxx    2/2   Running
# todo-app-notification-service-xxx 2/2   Running
```

### 2. Test Frontend

- [ ] Sign up with email/password
- [ ] Sign in successfully
- [ ] Dashboard loads with stats

### 3. Test Task Creation

- [ ] Create task with title
- [ ] Set due date (tomorrow, 3:00 PM)
- [ ] Set priority (High)
- [ ] Add tags (work, test)
- [ ] Task appears in list

### 4. Test Recurring Tasks

- [ ] Create task with "Daily" recurrence
- [ ] Mark task complete
- [ ] New task appears within 10 seconds
- [ ] Check logs: `kubectl logs -n todo-app -l app=recurring-service -f`

### 5. Test Search & Filter

- [ ] Search for task by title
- [ ] Filter by priority
- [ ] Filter by tags
- [ ] Filter by due date

### 6. Test Dashboard

- [ ] View total tasks count
- [ ] View completed tasks count
- [ ] View calendar with tasks
- [ ] View priority distribution chart

### 7. Check Dapr Sidecars

```bash
# Verify Dapr sidecars are running
kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'

# Expected: Each pod shows 2 containers (app + daprd)
```

### 8. Check Kafka Events

```bash
# View recurring service logs for event processing
kubectl logs -n todo-app -l app=recurring-service -f

# Expected: See CloudEvents being received and published
# INFO: Received event: task.completed.v1
# INFO: Published event: task.created.v1
```

---

## Common Issues & Quick Fixes

### Issue: Pods stuck in ImagePullBackOff

**Fix:**
```bash
# For Minikube: Ensure images are built in Minikube's Docker
eval $(minikube docker-env)
./scripts/deployment/minikube-setup.sh

# For cloud: Check GitHub Container Registry permissions
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### Issue: Database connection errors

**Fix:**
```bash
# Verify DATABASE_URL format
kubectl get secret todo-secrets -n todo-app -o jsonpath='{.data.database-url}' | base64 -d

# Should be: postgresql://user:password@host:5432/dbname
```

### Issue: LoadBalancer stuck in Pending

**Fix:**
```bash
# For Minikube: Use NodePort instead
minikube service todo-app-frontend -n todo-app

# For cloud: Check service limits and quotas
kubectl describe svc todo-app-frontend -n todo-app
```

### Issue: Recurring tasks not working

**Fix:**
```bash
# Check Kafka connectivity
kubectl logs -n todo-app -l app=recurring-service --tail=50

# Verify Dapr pubsub component
kubectl get component pubsub -n todo-app -o yaml

# Check Redpanda brokers configuration
```

### Issue: Reminders not working

**Fix:**
```bash
# Check notification service logs
kubectl logs -n todo-app -l app=notification-service -f

# Verify cron binding
kubectl get component reminder-cron -n todo-app -o yaml

# Should trigger every 5 minutes: @every 5m
```

---

## Next Steps

After successful deployment:

### 1. Configure Domain (Optional)

**Add DNS A records:**
- `todo.yourdomain.com` → Frontend IP
- `api.yourdomain.com` → Backend IP

### 2. Enable HTTPS (Recommended)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create Let's Encrypt issuer
# See: docs/DEPLOYMENT_GUIDE.md#enable-https
```

### 3. Set Up Monitoring (Recommended)

```bash
# Install Prometheus + Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

### 4. Scale for Production

```bash
# Increase replicas
kubectl scale deployment todo-app-backend -n todo-app --replicas=3

# Enable auto-scaling
kubectl autoscale deployment todo-app-backend -n todo-app \
  --cpu-percent=70 \
  --min=2 \
  --max=10
```

---

## Getting Help

### Documentation

- **Full Deployment Guide**: [docs/DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **Architecture Overview**: [docs/architecture-diagram.md](./architecture-diagram.md)
- **Event Schemas**: [docs/event-schemas.md](./event-schemas.md)
- **Phase 5 Progress**: [docs/PHASE5_PROGRESS.md](./PHASE5_PROGRESS.md)

### Debug Commands

```bash
# Check pod status
kubectl get pods -n todo-app

# View logs (last 100 lines)
kubectl logs -n todo-app <pod-name> -c <container-name> --tail=100

# Describe pod for events
kubectl describe pod <pod-name> -n todo-app

# Check Dapr components
kubectl get components -n todo-app

# Access Dapr dashboard
dapr dashboard -k
```

### Common Kubectl Commands

```bash
# Get all resources
kubectl get all -n todo-app

# Restart deployment
kubectl rollout restart deployment/todo-app-backend -n todo-app

# Port forward to service
kubectl port-forward svc/todo-app-backend -n todo-app 8000:80

# Execute command in pod
kubectl exec -it <pod-name> -n todo-app -c backend -- bash

# Delete and redeploy
helm uninstall todo-app -n todo-app
./scripts/deployment/minikube-setup.sh  # or oracle-oke-setup.sh
```

---

## Resources

- **Kubernetes Docs**: https://kubernetes.io/docs
- **Dapr Docs**: https://docs.dapr.io
- **Helm Docs**: https://helm.sh/docs
- **Oracle OKE Docs**: https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm
- **Redpanda Docs**: https://docs.redpanda.com
- **Neon Docs**: https://neon.tech/docs

---

## Support

- **GitHub Issues**: https://github.com/your-username/todo-app/issues
- **Project README**: [README.md](../README.md)
- **Full Documentation**: [docs/](./docs/)

---

**Time to first task:** 15-20 minutes ⏱️
**Time to production:** 45-60 minutes 🚀
**Time to CI/CD:** 10 minutes ⚡

🎉 Happy deploying!

---

🚀 Generated with [Claude Code](https://claude.com/claude-code)

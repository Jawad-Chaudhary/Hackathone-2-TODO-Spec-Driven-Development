# Phase 4 Deployment Guide - Todo Application

Complete guide for deploying the Todo application with AI chatbot to local Kubernetes (Minikube).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Docker Setup](#docker-setup)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Helm Deployment](#helm-deployment)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [AI DevOps Tools](#ai-devops-tools)

---

## Prerequisites

### Required Software

1. **Docker Desktop** (with Kubernetes enabled)
   - Download: https://www.docker.com/products/docker-desktop/
   - Version: Latest stable

2. **Minikube**
   - Install: https://minikube.sigs.k8s.io/docs/start/
   - Version: v1.30+

3. **kubectl**
   - Install: https://kubernetes.io/docs/tasks/tools/
   - Version: v1.28+

4. **Helm**
   - Install: https://helm.sh/docs/intro/install/
   - Version: v3.12+

5. **Node.js & Python**
   - Node.js 22+
   - Python 3.13+

### Required Secrets

You'll need the following credentials before deployment:

- **Neon PostgreSQL Database URL**
  - Format: `postgresql://user:password@host/database?sslmode=require`
  - Get from: https://neon.tech/

- **OpenAI API Key**
  - Get from: https://platform.openai.com/api-keys

- **JWT Secret**
  - Generate: `openssl rand -base64 32`

- **Better Auth Secret**
  - Generate: `openssl rand -base64 32`

- **OpenAI Domain Key** (for ChatKit)
  - Get from: https://platform.openai.com/

---

## Quick Start

### 1. Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable ingress addon (optional)
minikube addons enable ingress

# Verify Minikube is running
minikube status
```

### 2. Configure Docker Environment

```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify you're using Minikube's Docker
docker ps
```

### 3. Build Docker Images

```bash
# Build backend image
cd backend
docker build -t todo-backend:latest .
cd ..

# Build frontend image
cd frontend
docker build -t todo-frontend:latest .
cd ..

# Verify images are built in Minikube
docker images | grep todo
```

### 4. Update Secrets

Edit `k8s/secrets.yaml` or `helm/todo-app/values.yaml` with your actual credentials:

```bash
# For raw Kubernetes
nano k8s/secrets.yaml

# OR for Helm
nano helm/todo-app/values.yaml
```

Replace all `REPLACE_WITH_YOUR_*` placeholders with actual values.

### 5. Deploy with Helm (Recommended)

```bash
# Deploy using Helm
helm install todo-app ./helm/todo-app

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=todo-backend -n todo-app --timeout=300s
kubectl wait --for=condition=ready pod -l app=todo-frontend -n todo-app --timeout=300s
```

### 6. Access the Application

```bash
# Get frontend URL (Minikube)
minikube service todo-frontend-service -n todo-app

# Or use port-forward
kubectl port-forward svc/todo-frontend-service -n todo-app 3000:3000
```

Open http://localhost:3000 in your browser.

---

## Docker Setup

### Local Testing with Docker Compose

Before deploying to Kubernetes, test locally with Docker Compose:

```bash
# Create .env file with your secrets
cat > .env << EOF
DATABASE_URL=your_neon_database_url
OPENAI_API_KEY=your_openai_api_key
JWT_SECRET=your_jwt_secret
BETTER_AUTH_SECRET=your_better_auth_secret
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_openai_domain_key
EOF

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Test endpoints
curl http://localhost:8000/health  # Backend health
curl http://localhost:3000          # Frontend

# Stop services
docker-compose down
```

### Building Individual Images

```bash
# Backend
cd backend
docker build -t todo-backend:latest .
docker run -p 8000:8000 --env-file ../.env todo-backend:latest

# Frontend
cd frontend
docker build -t todo-frontend:latest .
docker run -p 3000:3000 --env-file ../.env todo-frontend:latest
```

---

## Kubernetes Deployment

### Option 1: Raw Kubernetes Manifests

```bash
# Apply manifests in order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# Verify deployment
kubectl get all -n todo-app

# Check pods
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app
```

### Accessing Services

```bash
# Backend (internal only - ClusterIP)
kubectl port-forward svc/todo-backend-service -n todo-app 8000:8000

# Frontend (LoadBalancer)
minikube service todo-frontend-service -n todo-app

# Or use kubectl port-forward
kubectl port-forward svc/todo-frontend-service -n todo-app 3000:3000
```

### Checking Logs

```bash
# Backend logs
kubectl logs -f deployment/todo-backend -n todo-app

# Frontend logs
kubectl logs -f deployment/todo-frontend -n todo-app

# All pods in namespace
kubectl logs -f -l app=todo-backend -n todo-app
kubectl logs -f -l app=todo-frontend -n todo-app
```

### Updating Deployment

```bash
# After rebuilding images
kubectl rollout restart deployment/todo-backend -n todo-app
kubectl rollout restart deployment/todo-frontend -n todo-app

# Check rollout status
kubectl rollout status deployment/todo-backend -n todo-app
kubectl rollout status deployment/todo-frontend -n todo-app
```

---

## Helm Deployment

### Installing the Chart

```bash
# Install with default values
helm install todo-app ./helm/todo-app

# Install with custom values
helm install todo-app ./helm/todo-app -f custom-values.yaml

# Install in specific namespace
helm install todo-app ./helm/todo-app --namespace todo-app --create-namespace
```

### Customizing Values

Create a `custom-values.yaml` file:

```yaml
# custom-values.yaml
backend:
  replicaCount: 3  # Scale to 3 replicas
  resources:
    limits:
      memory: "1Gi"

frontend:
  replicaCount: 3
  service:
    type: NodePort  # Use NodePort instead of LoadBalancer

secrets:
  databaseUrl: "postgresql://user:password@host/database"
  openaiApiKey: "sk-..."
  jwtSecret: "your-secret"
  betterAuthSecret: "your-secret"
  openaiDomainKey: "your-key"
```

Deploy with custom values:

```bash
helm install todo-app ./helm/todo-app -f custom-values.yaml
```

### Managing Helm Releases

```bash
# List releases
helm list -n todo-app

# Get release status
helm status todo-app -n todo-app

# Upgrade release
helm upgrade todo-app ./helm/todo-app

# Rollback to previous version
helm rollback todo-app 1

# Uninstall release
helm uninstall todo-app -n todo-app
```

### Validating Helm Chart

```bash
# Lint the chart
helm lint ./helm/todo-app

# Dry-run installation
helm install todo-app ./helm/todo-app --dry-run --debug

# Template rendering
helm template todo-app ./helm/todo-app > rendered-manifests.yaml
```

---

## Verification

### Health Checks

```bash
# Backend health endpoint
kubectl exec -it deployment/todo-backend -n todo-app -- \
  curl http://localhost:8000/health

# Expected response: {"status":"healthy"}

# Frontend accessibility
kubectl exec -it deployment/todo-frontend -n todo-app -- \
  curl http://localhost:3000/

# Expected response: HTML content
```

### Database Connectivity

```bash
# Check backend can connect to database
kubectl logs -n todo-app deployment/todo-backend | grep -i database

# Expected: No connection errors
```

### Service Discovery

```bash
# Check if services are resolving
kubectl run -it --rm debug --image=alpine --restart=Never -n todo-app -- sh

# Inside the pod:
nslookup todo-backend-service
nslookup todo-frontend-service
curl http://todo-backend-service:8000/health
```

### Testing the Application

1. **Access Frontend**: http://localhost:3000
2. **Sign Up/Login**: Create a test user
3. **Create Todo**: Use the UI to create a todo
4. **Test Chatbot**: Go to `/chat` and try:
   - "Add a task: Buy groceries"
   - "Show my tasks"
   - "Mark task 1 as complete"
5. **Check Persistence**: Refresh page and verify data persists

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n todo-app

# Describe pod for events
kubectl describe pod <pod-name> -n todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Common issues:
# - ImagePullBackOff: Image not in Minikube Docker
# - CrashLoopBackOff: Check logs for errors
# - Pending: Resource constraints or PVC issues
```

### Image Pull Errors

```bash
# Ensure you're using Minikube's Docker daemon
eval $(minikube docker-env)

# Rebuild images
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

# Verify images exist
docker images | grep todo

# Ensure imagePullPolicy is set to Never in manifests
```

### Health Check Failures

```bash
# Check readiness probe
kubectl describe pod <pod-name> -n todo-app | grep -A 10 Readiness

# Check liveness probe
kubectl describe pod <pod-name> -n todo-app | grep -A 10 Liveness

# Test health endpoint manually
kubectl exec -it <pod-name> -n todo-app -- curl http://localhost:8000/health
```

### Database Connection Issues

```bash
# Check if DATABASE_URL secret is set correctly
kubectl get secret todo-secrets -n todo-app -o jsonpath='{.data.database-url}' | base64 -d

# Test database connectivity from pod
kubectl exec -it deployment/todo-backend -n todo-app -- python -c "
from sqlmodel import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
print('Database connection successful!')
"
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n todo-app

# Ensure selectors match pod labels
kubectl get pods -n todo-app --show-labels
kubectl get svc todo-frontend-service -n todo-app -o yaml | grep -A 5 selector

# Test service from within cluster
kubectl run -it --rm debug --image=alpine --restart=Never -n todo-app -- \
  wget -qO- http://todo-backend-service:8000/health
```

### Resource Limits

```bash
# Check resource usage
kubectl top pods -n todo-app
kubectl top nodes

# Increase Minikube resources if needed
minikube stop
minikube start --cpus=6 --memory=12288

# Adjust resource limits in values.yaml
```

### Viewing Full Logs

```bash
# All backend logs
kubectl logs -n todo-app deployment/todo-backend --all-containers=true

# Follow logs with timestamps
kubectl logs -f -n todo-app deployment/todo-backend --timestamps=true

# Previous pod logs (if crashed)
kubectl logs -n todo-app <pod-name> --previous
```

---

## AI DevOps Tools

### kubectl-ai

AI-powered Kubernetes management using natural language:

```bash
# Install kubectl-ai
kubectl krew install ai

# Set OpenAI API key
export OPENAI_API_KEY=your_api_key

# Example commands
kubectl ai "show me all pods in todo-app namespace"
kubectl ai "create a deployment with 3 replicas of nginx"
kubectl ai "scale todo-backend to 5 replicas in todo-app namespace"
kubectl ai "show me pods that are not running"
kubectl ai "delete all failed pods in todo-app namespace"
```

### kagent

Kubernetes-native AI agent for cluster operations:

```bash
# Install kagent
curl -sfL https://raw.githubusercontent.com/yourusername/kagent/main/install.sh | sh

# Configure
export KAGENT_OPENAI_KEY=your_api_key

# Example commands
kagent analyze namespace todo-app
kagent optimize deployment todo-backend -n todo-app
kagent troubleshoot pod <pod-name> -n todo-app
kagent suggest improvements
```

### Docker AI Agent (Gordon)

AI assistant for Docker operations:

```bash
# Install Gordon
docker extension install docker/gordon-extension:latest

# Enable Gordon in Docker Desktop
# Settings > Extensions > Gordon

# Example queries in Docker Desktop terminal:
# "Show me all running containers"
# "Build an image from current directory"
# "Create a container with port mapping 3000:3000"
# "Clean up unused images"
```

---

## Additional Resources

### Monitoring and Observability

```bash
# Enable metrics-server
minikube addons enable metrics-server

# View resource usage
kubectl top pods -n todo-app
kubectl top nodes

# Port-forward for local monitoring
kubectl port-forward -n kube-system service/metrics-server 443:443
```

### Cleanup

```bash
# Delete Helm release
helm uninstall todo-app -n todo-app

# OR delete raw manifests
kubectl delete -f k8s/

# Delete namespace
kubectl delete namespace todo-app

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

### Next Steps

1. **Phase 5**: Deploy to Cloud Kubernetes (AKS/EKS/GKE)
2. **CI/CD**: Set up GitHub Actions for automated deployments
3. **Monitoring**: Add Prometheus and Grafana
4. **Ingress**: Configure ingress for production domains
5. **SSL/TLS**: Add certificate management with cert-manager
6. **Autoscaling**: Configure HPA (Horizontal Pod Autoscaler)

---

## Support

For issues and questions:
- Check troubleshooting section above
- Review Kubernetes events: `kubectl get events -n todo-app`
- Review pod logs: `kubectl logs -n todo-app <pod-name>`
- Consult hackathon documentation

**Phase 4 Deliverables Checklist:**
- ✅ Dockerfiles for frontend and backend
- ✅ docker-compose.yml for local testing
- ✅ Kubernetes manifests (namespace, secrets, deployments, services)
- ✅ Helm charts with configurable values
- ✅ Deployment on local Kubernetes (Minikube)
- ✅ AI DevOps tools documentation (kubectl-ai, kagent, Gordon)
- ✅ Comprehensive deployment guide

Good luck with your hackathon submission!

#!/bin/bash
# Minikube Local Deployment Setup Script
# Phase 5 - Todo App with Event-Driven Architecture
#
# This script sets up a complete local Kubernetes environment with:
# - Minikube cluster
# - Dapr runtime
# - Redpanda (Kafka)
# - Todo App services

set -e  # Exit on error

echo "🚀 Todo App - Minikube Local Deployment Setup"
echo "=============================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running on Windows (WSL)
if grep -qi microsoft /proc/version; then
    print_warning "Detected WSL environment"
    print_warning "Make sure Docker Desktop is running on Windows"
fi

# Step 1: Check prerequisites
echo "Step 1: Checking prerequisites..."
echo "-----------------------------------"

# Check Minikube
if ! command -v minikube &> /dev/null; then
    print_error "Minikube is not installed"
    echo "Install from: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi
print_success "Minikube found: $(minikube version --short)"

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed"
    echo "Install from: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi
print_success "kubectl found: $(kubectl version --client --short 2>/dev/null || kubectl version --client)"

# Check Helm
if ! command -v helm &> /dev/null; then
    print_error "Helm is not installed"
    echo "Install from: https://helm.sh/docs/intro/install/"
    exit 1
fi
print_success "Helm found: $(helm version --short)"

# Check Dapr CLI
if ! command -v dapr &> /dev/null; then
    print_error "Dapr CLI is not installed"
    echo "Install with: wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash"
    exit 1
fi
print_success "Dapr CLI found: $(dapr version | grep 'CLI version' | awk '{print $3}')"

echo ""

# Step 2: Start Minikube
echo "Step 2: Starting Minikube cluster..."
echo "--------------------------------------"

# Check if Minikube is already running
if minikube status &> /dev/null; then
    print_warning "Minikube is already running"
    read -p "Do you want to restart it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        minikube delete
        minikube start --cpus=4 --memory=8192 --driver=docker
    fi
else
    minikube start --cpus=4 --memory=8192 --driver=docker
fi

print_success "Minikube cluster is running"
kubectl cluster-info
echo ""

# Step 3: Initialize Dapr on Kubernetes
echo "Step 3: Installing Dapr on Kubernetes..."
echo "------------------------------------------"

if kubectl get namespace dapr-system &> /dev/null; then
    print_warning "Dapr is already installed"
else
    dapr init -k --wait
    print_success "Dapr installed successfully"
fi

# Verify Dapr installation
dapr status -k
echo ""

# Step 4: Install Redpanda (Kafka)
echo "Step 4: Installing Redpanda (Kafka)..."
echo "----------------------------------------"

# Add Redpanda Helm repo
if ! helm repo list | grep -q redpanda; then
    helm repo add redpanda https://charts.redpanda.com/
    helm repo update
fi

# Create redpanda namespace
kubectl create namespace redpanda --dry-run=client -o yaml | kubectl apply -f -

# Install Redpanda
if helm list -n redpanda | grep -q redpanda; then
    print_warning "Redpanda is already installed"
else
    helm install redpanda redpanda/redpanda \
        --namespace redpanda \
        --set statefulset.replicas=1 \
        --set resources.cpu.cores=1 \
        --set resources.memory.container.max=2Gi \
        --set storage.persistentVolume.size=10Gi \
        --wait \
        --timeout 5m

    print_success "Redpanda installed successfully"
fi

# Wait for Redpanda to be ready
echo "Waiting for Redpanda pods to be ready..."
kubectl wait --for=condition=ready pod \
    --selector=app.kubernetes.io/name=redpanda \
    --namespace=redpanda \
    --timeout=300s

print_success "Redpanda is ready"
echo ""

# Step 5: Create Kafka topics
echo "Step 5: Creating Kafka topics..."
echo "----------------------------------"

# Get Redpanda pod name
REDPANDA_POD=$(kubectl get pod -n redpanda -l app.kubernetes.io/name=redpanda -o jsonpath='{.items[0].metadata.name}')

# Create topics
kubectl exec -n redpanda $REDPANDA_POD -- rpk topic create task-events --brokers=localhost:9092 || print_warning "Topic task-events may already exist"
kubectl exec -n redpanda $REDPANDA_POD -- rpk topic create reminders --brokers=localhost:9092 || print_warning "Topic reminders may already exist"

print_success "Kafka topics created"
echo ""

# Step 6: Build Docker images (using Minikube's Docker daemon)
echo "Step 6: Building Docker images..."
echo "-----------------------------------"

print_warning "Setting up Minikube Docker environment..."
eval $(minikube docker-env)

# Build backend
echo "Building backend image..."
docker build -t todo-app-backend:latest ./backend

# Build frontend
echo "Building frontend image..."
docker build -t todo-app-frontend:latest ./frontend

# Build recurring service
echo "Building recurring-service image..."
docker build -t todo-app-recurring-service:latest ./services/recurring-service

# Build notification service
echo "Building notification-service image..."
docker build -t todo-app-notification-service:latest ./services/notification-service

print_success "All Docker images built successfully"
echo ""

# Step 7: Create namespace and secrets
echo "Step 7: Creating Kubernetes resources..."
echo "------------------------------------------"

# Create namespace
kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -

# Create secrets (you'll need to update these with real values)
kubectl create secret generic todo-secrets \
    --from-literal=database-url="${DATABASE_URL:-postgresql://user:password@localhost:5432/todo}" \
    --from-literal=jwt-secret="${JWT_SECRET:-your-jwt-secret-change-in-production}" \
    --from-literal=better-auth-secret="${BETTER_AUTH_SECRET:-your-auth-secret-change-in-production}" \
    --from-literal=openai-api-key="${OPENAI_API_KEY:-sk-proj-your-key-here}" \
    --namespace todo-app \
    --dry-run=client -o yaml | kubectl apply -f -

print_success "Namespace and secrets created"
echo ""

# Step 8: Apply Dapr components
echo "Step 8: Applying Dapr components..."
echo "-------------------------------------"

kubectl apply -f k8s/components/ -n todo-app

print_success "Dapr components applied"
echo ""

# Step 9: Deploy application with Helm
echo "Step 9: Deploying Todo App with Helm..."
echo "-----------------------------------------"

helm upgrade --install todo-app ./helm/todo-app \
    --namespace todo-app \
    --set backend.image.repository=todo-app-backend \
    --set backend.image.tag=latest \
    --set backend.image.pullPolicy=Never \
    --set frontend.image.repository=todo-app-frontend \
    --set frontend.image.tag=latest \
    --set frontend.image.pullPolicy=Never \
    --set recurringService.image.repository=todo-app-recurring-service \
    --set recurringService.image.tag=latest \
    --set recurringService.image.pullPolicy=Never \
    --set notificationService.image.repository=todo-app-notification-service \
    --set notificationService.image.tag=latest \
    --set notificationService.image.pullPolicy=Never \
    --wait \
    --timeout 10m

print_success "Todo App deployed successfully"
echo ""

# Step 10: Verify deployment
echo "Step 10: Verifying deployment..."
echo "----------------------------------"

echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod \
    --selector=app.kubernetes.io/instance=todo-app \
    --namespace=todo-app \
    --timeout=300s || print_warning "Some pods may still be starting..."

echo ""
echo "Deployment Status:"
kubectl get pods -n todo-app
echo ""
kubectl get services -n todo-app
echo ""

# Step 11: Access information
echo "Step 11: Access Information"
echo "=============================="
echo ""

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Get NodePort for frontend
FRONTEND_PORT=$(kubectl get svc todo-app-frontend -n todo-app -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "N/A")

# Get NodePort for backend
BACKEND_PORT=$(kubectl get svc todo-app-backend -n todo-app -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "N/A")

print_success "Deployment Complete!"
echo ""
echo "Access your Todo App:"
echo "  Frontend:    http://$MINIKUBE_IP:$FRONTEND_PORT"
echo "  Backend API: http://$MINIKUBE_IP:$BACKEND_PORT"
echo "  API Docs:    http://$MINIKUBE_IP:$BACKEND_PORT/docs"
echo ""
echo "Or use Minikube service command:"
echo "  minikube service todo-app-frontend -n todo-app"
echo "  minikube service todo-app-backend -n todo-app"
echo ""
echo "To view logs:"
echo "  kubectl logs -n todo-app -l app=backend -f"
echo "  kubectl logs -n todo-app -l app=frontend -f"
echo ""
echo "To check Dapr sidecars:"
echo "  dapr dashboard -k"
echo ""
print_warning "Remember to update secrets in k8s/base/secrets.yaml with production values!"
echo ""
print_success "Setup complete! 🎉"

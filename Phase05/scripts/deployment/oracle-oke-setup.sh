#!/bin/bash
# Oracle OKE Cloud Deployment Setup Script
# Phase 5 - Todo App with Event-Driven Architecture
#
# This script deploys the Todo App to Oracle Cloud Infrastructure (OCI)
# Oracle Kubernetes Engine (OKE) with Redpanda Cloud for Kafka

set -e  # Exit on error

echo "☁️  Todo App - Oracle OKE Cloud Deployment"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Configuration variables (override with environment variables)
OCI_REGION="${OCI_REGION:-us-ashburn-1}"
OKE_CLUSTER_NAME="${OKE_CLUSTER_NAME:-todo-app-cluster}"
COMPARTMENT_OCID="${COMPARTMENT_OCID:-}"
REDPANDA_BROKERS="${REDPANDA_BROKERS:-}"
DATABASE_URL="${DATABASE_URL:-}"
JWT_SECRET="${JWT_SECRET:-}"
BETTER_AUTH_SECRET="${BETTER_AUTH_SECRET:-}"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
NAMESPACE="todo-app"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-ghcr.io}"
REGISTRY_USERNAME="${REGISTRY_USERNAME:-}"

echo "Step 1: Validating Prerequisites"
echo "---------------------------------"

# Check OCI CLI
if ! command -v oci &> /dev/null; then
    print_error "OCI CLI is not installed"
    echo "Install from: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm"
    exit 1
fi
print_success "OCI CLI found: $(oci --version 2>&1 | head -n 1)"

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

# Validate required environment variables
echo "Step 2: Validating Configuration"
echo "----------------------------------"

MISSING_CONFIG=false

if [ -z "$COMPARTMENT_OCID" ]; then
    print_error "COMPARTMENT_OCID is not set"
    MISSING_CONFIG=true
fi

if [ -z "$REDPANDA_BROKERS" ]; then
    print_error "REDPANDA_BROKERS is not set (e.g., broker.example.com:9092)"
    MISSING_CONFIG=true
fi

if [ -z "$DATABASE_URL" ]; then
    print_error "DATABASE_URL is not set"
    MISSING_CONFIG=true
fi

if [ -z "$JWT_SECRET" ]; then
    print_error "JWT_SECRET is not set"
    MISSING_CONFIG=true
fi

if [ -z "$BETTER_AUTH_SECRET" ]; then
    print_error "BETTER_AUTH_SECRET is not set"
    MISSING_CONFIG=true
fi

if [ -z "$REGISTRY_USERNAME" ]; then
    print_warning "REGISTRY_USERNAME is not set - using current GitHub username"
    REGISTRY_USERNAME=$(git config user.name | tr '[:upper:]' '[:lower:]')
fi

if [ "$MISSING_CONFIG" = true ]; then
    echo ""
    print_error "Missing required configuration variables"
    echo ""
    echo "Required environment variables:"
    echo "  export COMPARTMENT_OCID='ocid1.compartment.oc1..xxx'"
    echo "  export REDPANDA_BROKERS='broker.cloud.redpanda.com:9092'"
    echo "  export DATABASE_URL='postgresql://user:password@host:5432/todo'"
    echo "  export JWT_SECRET='your-jwt-secret'"
    echo "  export BETTER_AUTH_SECRET='your-auth-secret'"
    echo ""
    echo "Optional variables:"
    echo "  export OCI_REGION='us-ashburn-1'  # default"
    echo "  export OKE_CLUSTER_NAME='todo-app-cluster'  # default"
    echo "  export OPENAI_API_KEY='sk-proj-xxx'"
    echo "  export IMAGE_TAG='v2.0.0'  # default: latest"
    echo ""
    exit 1
fi

print_success "All required configuration variables are set"
echo ""

# Display configuration
print_info "Deployment Configuration:"
echo "  Region: $OCI_REGION"
echo "  Cluster: $OKE_CLUSTER_NAME"
echo "  Namespace: $NAMESPACE"
echo "  Image Tag: $IMAGE_TAG"
echo "  Registry: $REGISTRY/$REGISTRY_USERNAME"
echo ""

read -p "Continue with these settings? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

echo ""

# Step 3: Configure kubectl for OKE
echo "Step 3: Configuring kubectl for OKE"
echo "-------------------------------------"

print_info "Setting up kubeconfig for OKE cluster..."

# Get cluster OCID
CLUSTER_OCID=$(oci ce cluster list \
    --compartment-id "$COMPARTMENT_OCID" \
    --name "$OKE_CLUSTER_NAME" \
    --query "data[0].id" \
    --raw-output 2>/dev/null || echo "")

if [ -z "$CLUSTER_OCID" ]; then
    print_error "OKE cluster '$OKE_CLUSTER_NAME' not found"
    echo ""
    echo "To create an OKE cluster:"
    echo "1. Go to OCI Console: https://cloud.oracle.com"
    echo "2. Navigate to: Developer Services > Kubernetes Clusters (OKE)"
    echo "3. Click 'Create Cluster' and choose 'Quick Create'"
    echo "4. Set cluster name to: $OKE_CLUSTER_NAME"
    echo "5. Choose Kubernetes version 1.28+"
    echo "6. Node pool: 3 nodes, VM.Standard.E4.Flex (2 OCPUs, 16GB RAM)"
    echo ""
    exit 1
fi

print_success "Found OKE cluster: $CLUSTER_OCID"

# Generate kubeconfig
oci ce cluster create-kubeconfig \
    --cluster-id "$CLUSTER_OCID" \
    --file "$HOME/.kube/config" \
    --region "$OCI_REGION" \
    --overwrite

print_success "Kubeconfig configured"

# Test cluster connection
kubectl cluster-info
print_success "Connected to OKE cluster"
echo ""

# Step 4: Install Dapr on Kubernetes
echo "Step 4: Installing Dapr on Kubernetes"
echo "---------------------------------------"

if kubectl get namespace dapr-system &> /dev/null; then
    print_warning "Dapr is already installed"
else
    print_info "Installing Dapr..."
    dapr init -k --wait
    print_success "Dapr installed successfully"
fi

# Verify Dapr installation
dapr status -k
echo ""

# Step 5: Create namespace
echo "Step 5: Creating Kubernetes namespace"
echo "---------------------------------------"

kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
print_success "Namespace '$NAMESPACE' created/updated"
echo ""

# Step 6: Create Kubernetes secrets
echo "Step 6: Creating Kubernetes secrets"
echo "-------------------------------------"

print_info "Creating todo-secrets secret..."

kubectl create secret generic todo-secrets \
    --from-literal=database-url="$DATABASE_URL" \
    --from-literal=jwt-secret="$JWT_SECRET" \
    --from-literal=better-auth-secret="$BETTER_AUTH_SECRET" \
    --from-literal=openai-api-key="${OPENAI_API_KEY:-sk-proj-placeholder}" \
    --namespace "$NAMESPACE" \
    --dry-run=client -o yaml | kubectl apply -f -

print_success "Secrets created"
echo ""

# Step 7: Update Dapr pubsub component for Redpanda Cloud
echo "Step 7: Applying Dapr components"
echo "----------------------------------"

print_info "Updating Dapr pubsub component with Redpanda Cloud brokers..."

# Create temporary pubsub component file
cat > /tmp/pubsub-cloud.yaml <<EOF
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: $NAMESPACE
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "$REDPANDA_BROKERS"
  - name: authType
    value: "none"
  - name: consumerGroup
    value: "todo-app-group"
  - name: maxMessageBytes
    value: "1024"
  - name: version
    value: "2.0.0"
  - name: enableTLS
    value: "true"
scopes:
- todo-backend
- todo-recurring-service
- todo-notification-service
EOF

kubectl apply -f /tmp/pubsub-cloud.yaml

# Apply other Dapr components from k8s/components/
if [ -d "k8s/components" ]; then
    kubectl apply -f k8s/components/statestore.yaml -n "$NAMESPACE" || print_warning "statestore.yaml not found"
    kubectl apply -f k8s/components/secretstore.yaml -n "$NAMESPACE" || print_warning "secretstore.yaml not found"
    kubectl apply -f k8s/components/reminder-cron.yaml -n "$NAMESPACE" || print_warning "reminder-cron.yaml not found"
fi

print_success "Dapr components applied"
echo ""

# Step 8: Deploy application with Helm
echo "Step 8: Deploying Todo App with Helm"
echo "--------------------------------------"

print_info "Deploying application..."

helm upgrade --install todo-app ./helm/todo-app \
    --namespace "$NAMESPACE" \
    --set backend.image.repository="$REGISTRY/$REGISTRY_USERNAME/todo-app-backend" \
    --set backend.image.tag="$IMAGE_TAG" \
    --set backend.image.pullPolicy=Always \
    --set frontend.image.repository="$REGISTRY/$REGISTRY_USERNAME/todo-app-frontend" \
    --set frontend.image.tag="$IMAGE_TAG" \
    --set frontend.image.pullPolicy=Always \
    --set recurringService.image.repository="$REGISTRY/$REGISTRY_USERNAME/todo-app-recurring-service" \
    --set recurringService.image.tag="$IMAGE_TAG" \
    --set recurringService.image.pullPolicy=Always \
    --set notificationService.image.repository="$REGISTRY/$REGISTRY_USERNAME/todo-app-notification-service" \
    --set notificationService.image.tag="$IMAGE_TAG" \
    --set notificationService.image.pullPolicy=Always \
    --set env.databaseUrl="$DATABASE_URL" \
    --set env.jwtSecret="$JWT_SECRET" \
    --set env.betterAuthSecret="$BETTER_AUTH_SECRET" \
    --set env.openaiApiKey="${OPENAI_API_KEY:-}" \
    --set kafka.brokers="$REDPANDA_BROKERS" \
    --wait \
    --timeout 10m

print_success "Todo App deployed successfully"
echo ""

# Step 9: Verify deployment
echo "Step 9: Verifying deployment"
echo "------------------------------"

print_info "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod \
    --selector=app.kubernetes.io/instance=todo-app \
    --namespace="$NAMESPACE" \
    --timeout=300s || print_warning "Some pods may still be starting..."

echo ""
echo "Deployment Status:"
kubectl get pods -n "$NAMESPACE"
echo ""
kubectl get services -n "$NAMESPACE"
echo ""

# Step 10: Get access information
echo "Step 10: Access Information"
echo "============================"
echo ""

# Get LoadBalancer IPs
FRONTEND_LB=$(kubectl get svc todo-app-frontend -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Pending...")
BACKEND_LB=$(kubectl get svc todo-app-backend -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Pending...")

print_success "Deployment Complete!"
echo ""
echo "Access your Todo App:"
echo "  Frontend:    http://$FRONTEND_LB"
echo "  Backend API: http://$BACKEND_LB"
echo "  API Docs:    http://$BACKEND_LB/docs"
echo ""

if [ "$FRONTEND_LB" = "Pending..." ] || [ "$BACKEND_LB" = "Pending..." ]; then
    print_warning "LoadBalancer IPs are still being provisioned"
    echo "Run this command to check status:"
    echo "  kubectl get svc -n $NAMESPACE --watch"
    echo ""
fi

echo "To view logs:"
echo "  kubectl logs -n $NAMESPACE -l app=backend -f"
echo "  kubectl logs -n $NAMESPACE -l app=frontend -f"
echo ""
echo "To check Dapr sidecars:"
echo "  dapr dashboard -k"
echo ""
echo "To scale services:"
echo "  kubectl scale deployment todo-app-backend -n $NAMESPACE --replicas=3"
echo ""
print_success "Setup complete! 🎉"

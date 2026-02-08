# Oracle Cloud (OKE) Deployment Guide
## Quick Start for Hackathon Submission

This guide shows how to deploy the Todo App to Oracle Kubernetes Engine (OKE) after the local deployment is complete.

---

## 📋 Prerequisites Status

### ✅ Already Completed
- [x] Local Minikube deployment working
- [x] Docker images built and tested
- [x] Helm charts configured
- [x] Dapr components ready
- [x] Deployment scripts prepared
- [x] OCI CLI installation in progress

### 🔄 Next Steps for Oracle Cloud
- [ ] Complete OCI CLI installation
- [ ] Configure Oracle Cloud credentials
- [ ] Create OKE cluster (or connect to existing)
- [ ] Push images to Oracle Container Registry
- [ ] Run deployment script

---

## 🚀 Quick Deployment Steps

### Step 1: Complete OCI CLI Installation

The installation is currently running. Once complete, verify:

```bash
# Check OCI CLI version
oci --version

# Should show: Oracle Cloud Infrastructure CLI 3.x.x
```

If not in PATH, add manually:
```bash
# Windows (PowerShell)
$env:PATH += ";C:\Users\jawad\lib\oracle-cli\bin"

# Or restart terminal
```

### Step 2: Configure Oracle Cloud Credentials

Run the OCI configuration wizard:

```bash
oci setup config
```

You'll need:
1. **User OCID**: From OCI Console → Profile → User Settings
2. **Tenancy OCID**: From OCI Console → Profile → Tenancy
3. **Region**: e.g., `us-ashburn-1`
4. **API Key**: Will be generated automatically

**Quick Access**:
- OCI Console: https://cloud.oracle.com
- Navigate to: Profile (top right) → User Settings
- Copy OCIDs from there

### Step 3: Set Environment Variables

Create `.env.oracle` file:

```bash
# Copy from template
cp .env.deployment .env.oracle

# Edit with your Oracle Cloud values
nano .env.oracle
```

Required variables:
```bash
# Oracle Cloud
export COMPARTMENT_OCID="ocid1.compartment.oc1..aaaaaaaxxxxx"
export OCI_REGION="us-ashburn-1"
export OKE_CLUSTER_NAME="todo-app-cluster"

# Database (already configured)
export DATABASE_URL="postgresql://neondb_owner:...@...neon.tech/neondb?sslmode=require"

# Secrets (already configured)
export JWT_SECRET="your-jwt-secret"
export BETTER_AUTH_SECRET="your-auth-secret"
export OPENAI_API_KEY="sk-proj-..." # Optional

# Kafka (for cloud deployment)
export REDPANDA_BROKERS="broker.cloud.redpanda.com:9092"  # Or use in-memory

# Container Registry
export REGISTRY="iad.ocir.io"  # Oracle Container Registry
export REGISTRY_USERNAME="your-tenancy/your-username"
```

### Step 4: Create OKE Cluster (If Needed)

**Option A: Use OCI Console (Recommended)**

1. Go to: https://cloud.oracle.com
2. Navigate to: **Developer Services** → **Kubernetes Clusters (OKE)**
3. Click **Create Cluster**
4. Choose **Quick Create**
5. Configure:
   - Name: `todo-app-cluster`
   - Kubernetes Version: `1.28+`
   - Node Pool:
     - Shape: `VM.Standard.E4.Flex`
     - OCPUs: 2
     - Memory: 16GB
     - Nodes: 3
6. Click **Create**
7. Wait 10-15 minutes for provisioning

**Option B: Use OCI CLI**

```bash
# List available shapes
oci ce node-pool-options get \
  --node-pool-option-id all \
  --compartment-id $COMPARTMENT_OCID

# Create cluster (example)
oci ce cluster create \
  --compartment-id $COMPARTMENT_OCID \
  --name todo-app-cluster \
  --kubernetes-version v1.28.2 \
  --vcn-id $VCN_OCID \
  --endpoint-subnet-id $SUBNET_OCID \
  --service-lb-subnet-ids '["'$LB_SUBNET_OCID'"]'
```

### Step 5: Run Automated Deployment

Once cluster is ready:

```bash
# Source environment variables
source .env.oracle

# Run deployment script
./scripts/deployment/oracle-oke-setup.sh
```

The script will automatically:
1. ✅ Validate prerequisites
2. ✅ Configure kubectl for OKE
3. ✅ Install Dapr on Kubernetes
4. ✅ Create namespace and secrets
5. ✅ Apply Dapr components
6. ✅ Deploy with Helm
7. ✅ Verify deployment
8. ✅ Display access URLs

**Estimated Time**: 15-20 minutes

---

## 🐳 Alternative: Docker Hub Deployment

If Oracle Container Registry setup is complex, you can use Docker Hub:

### Step 1: Login to Docker Hub

```bash
docker login
# Enter your Docker Hub credentials
```

### Step 2: Tag and Push Images

```bash
# Set your Docker Hub username
DOCKER_USER="your-dockerhub-username"

# Tag images
docker tag todo-backend:latest $DOCKER_USER/todo-backend:latest
docker tag todo-frontend:latest $DOCKER_USER/todo-frontend:latest
docker tag notification-service:latest $DOCKER_USER/notification-service:latest
docker tag recurring-service:latest $DOCKER_USER/recurring-service:latest

# Push to Docker Hub
docker push $DOCKER_USER/todo-backend:latest
docker push $DOCKER_USER/todo-frontend:latest
docker push $DOCKER_USER/notification-service:latest
docker push $DOCKER_USER/recurring-service:latest
```

### Step 3: Deploy to OKE

```bash
# Configure kubectl for OKE
oci ce cluster create-kubeconfig \
  --cluster-id $CLUSTER_OCID \
  --file $HOME/.kube/config \
  --region $OCI_REGION

# Install Dapr
dapr init -k --wait

# Deploy with Helm
helm upgrade --install todo-app ./helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  --set backend.image.repository=$DOCKER_USER/todo-backend \
  --set frontend.image.repository=$DOCKER_USER/todo-frontend \
  --set recurringService.image.repository=$DOCKER_USER/recurring-service \
  --set notificationService.image.repository=$DOCKER_USER/notification-service \
  --set backend.image.pullPolicy=Always \
  --set database.url="$DATABASE_URL" \
  --set auth.jwtSecret="$JWT_SECRET" \
  --set auth.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --wait
```

---

## 📊 Verification Steps

### Check Deployment Status

```bash
# Get all pods
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# View logs
kubectl logs -n todo-app -l app=backend -f
```

### Access Application

```bash
# Get LoadBalancer IPs
kubectl get svc -n todo-app

# Frontend LoadBalancer
export FRONTEND_IP=$(kubectl get svc todo-frontend-service -n todo-app -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Access application
echo "Frontend: http://$FRONTEND_IP:3000"
```

---

## 🔧 Troubleshooting

### Issue: OCI CLI Not Found

```bash
# Add to PATH (Windows PowerShell)
$env:PATH += ";C:\Users\jawad\lib\oracle-cli\bin"

# Or use full path
C:\Users\jawad\lib\oracle-cli\bin\oci --version
```

### Issue: Cannot Connect to OKE Cluster

```bash
# Reconfigure kubectl
oci ce cluster create-kubeconfig \
  --cluster-id $CLUSTER_OCID \
  --file $HOME/.kube/config \
  --region $OCI_REGION \
  --overwrite

# Test connection
kubectl cluster-info
```

### Issue: Pods Not Starting

```bash
# Describe pod to see events
kubectl describe pod <pod-name> -n todo-app

# Check image pull policy
kubectl get deployment -n todo-app -o yaml | grep imagePullPolicy

# Common fix: Use Docker Hub instead of private registry
```

### Issue: LoadBalancer Pending

```bash
# Check OCI load balancer provisioning
oci lb load-balancer list --compartment-id $COMPARTMENT_OCID

# May take 5-10 minutes to provision
kubectl get svc -n todo-app --watch
```

---

## 💰 Cost Considerations

### Oracle Cloud Free Tier

Oracle offers **Always Free** resources:
- 2 AMD-based Compute VMs
- 4 ARM-based Ampere A1 cores
- 24 GB RAM
- 200 GB block storage
- 10 GB object storage

**Recommendation**: Use Always Free resources for hackathon demo.

### OKE Cluster Costs

- **Control Plane**: Free
- **Worker Nodes**: Based on compute shape
  - VM.Standard.E4.Flex: ~$0.015/hour per OCPU
  - For 3 nodes × 2 OCPUs: ~$0.09/hour (~$2.16/day)

**Tip**: Terminate cluster after hackathon to avoid charges.

---

## 📚 Additional Resources

### Oracle Cloud Documentation
- [OKE Quickstart](https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengquickstart.htm)
- [OCI CLI Installation](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm)
- [Container Registry](https://docs.oracle.com/en-us/iaas/Content/Registry/Concepts/registryoverview.htm)

### Dapr on OKE
- [Dapr on Kubernetes](https://docs.dapr.io/operations/hosting/kubernetes/)
- [Dapr Components](https://docs.dapr.io/reference/components-reference/)

### Helm Charts
- [Helm Documentation](https://helm.sh/docs/)
- [Best Practices](https://helm.sh/docs/chart_best_practices/)

---

## ✅ Deployment Checklist

### Pre-Flight Check
- [ ] OCI CLI installed and configured
- [ ] Oracle Cloud account active
- [ ] OKE cluster created and accessible
- [ ] Docker images tagged and ready
- [ ] Environment variables set
- [ ] Kubectl configured for OKE

### Deployment
- [ ] Dapr installed on OKE
- [ ] Namespace created
- [ ] Secrets applied
- [ ] Dapr components deployed
- [ ] Application deployed via Helm
- [ ] LoadBalancer IPs assigned
- [ ] Health checks passing

### Post-Deployment
- [ ] Frontend accessible via LoadBalancer
- [ ] Backend API responding
- [ ] Database connected
- [ ] Dapr sidecars healthy
- [ ] Logs monitoring setup
- [ ] Documentation updated

---

## 🎯 Quick Reference

### Essential Commands

```bash
# OCI CLI
oci --version
oci setup config
oci ce cluster list --compartment-id $COMPARTMENT_OCID

# Kubectl
kubectl config use-context <oke-cluster-context>
kubectl get nodes
kubectl get pods -n todo-app
kubectl logs -f <pod-name> -n todo-app

# Dapr
dapr status -k
dapr dashboard -k

# Helm
helm list -n todo-app
helm upgrade todo-app ./helm/todo-app -n todo-app
helm rollback todo-app -n todo-app
```

### Environment Variables Template

```bash
# Save as .env.oracle
export COMPARTMENT_OCID="ocid1.compartment.oc1..xxx"
export OCI_REGION="us-ashburn-1"
export OKE_CLUSTER_NAME="todo-app-cluster"
export DATABASE_URL="postgresql://..."
export JWT_SECRET="..."
export BETTER_AUTH_SECRET="..."
export OPENAI_API_KEY="sk-proj-..."
export REGISTRY="iad.ocir.io"
export REGISTRY_USERNAME="tenancy/username"
```

---

## 📞 Support

For issues or questions:
1. Check `DEPLOYMENT.md` for detailed documentation
2. Review Oracle Cloud documentation
3. Check Dapr troubleshooting guides
4. Verify all environment variables are set correctly

---

**Last Updated**: February 4, 2026
**Status**: Ready for Oracle Cloud deployment
**Local Deployment**: ✅ Complete and working

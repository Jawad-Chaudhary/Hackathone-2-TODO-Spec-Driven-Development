# GitHub Secrets Configuration Guide

This guide explains how to configure GitHub Secrets for the CI/CD pipeline.

---

## Overview

The GitHub Actions workflow (`.github/workflows/deploy.yml`) requires specific secrets to deploy your application to cloud platforms. This guide covers secret setup for:

- Oracle Cloud Infrastructure (OKE)
- Google Cloud Platform (GKE)
- Microsoft Azure (AKS)

---

## Accessing GitHub Secrets

1. Navigate to your repository on GitHub
2. Click **Settings** (requires admin access)
3. In the left sidebar, expand **Secrets and variables**
4. Click **Actions**
5. Click **New repository secret**

---

## Required Secrets for All Platforms

These secrets are required regardless of which cloud provider you use:

### 1. DATABASE_URL

**Description**: PostgreSQL connection string for Neon database

**How to get:**
1. Sign up at https://neon.tech
2. Create a new project: "todo-app"
3. Go to Dashboard > Connection Details
4. Copy the connection string

**Format:**
```
postgresql://username:password@ep-cool-name-12345.us-east-1.aws.neon.tech/todo?sslmode=require
```

**Add to GitHub:**
- **Name**: `DATABASE_URL`
- **Value**: (paste connection string)

---

### 2. JWT_SECRET

**Description**: Secret key for JWT token signing

**How to generate:**
```bash
openssl rand -base64 32
```

**Add to GitHub:**
- **Name**: `JWT_SECRET`
- **Value**: (paste generated secret)

**Example output:**
```
3Kx9fN2mP8QwR5vY7zL1jH4gD6bC0aX8nM3kT9sW2eR5
```

---

### 3. BETTER_AUTH_SECRET

**Description**: Secret key for Better Auth session encryption

**How to generate:**
```bash
openssl rand -base64 32
```

**Add to GitHub:**
- **Name**: `BETTER_AUTH_SECRET`
- **Value**: (paste generated secret)

---

### 4. KAFKA_BROKERS

**Description**: Kafka bootstrap servers (Redpanda Cloud)

**How to get:**
1. Sign up at https://redpanda.com
2. Create a cluster
3. Go to: Cluster > Connect
4. Copy **Bootstrap servers**

**Format:**
```
broker-1.cloud.redpanda.com:9092,broker-2.cloud.redpanda.com:9092
```

**Add to GitHub:**
- **Name**: `KAFKA_BROKERS`
- **Value**: (paste bootstrap servers)

---

### 5. OPENAI_API_KEY (Optional)

**Description**: OpenAI API key for AI features

**How to get:**
1. Sign up at https://platform.openai.com
2. Go to: API Keys
3. Click **Create new secret key**
4. Copy the key (starts with `sk-proj-`)

**Add to GitHub:**
- **Name**: `OPENAI_API_KEY`
- **Value**: (paste API key)

---

## Oracle Cloud (OKE) Secrets

Required if deploying to Oracle Kubernetes Engine.

### 1. OKE_KUBECONFIG

**Description**: Base64-encoded kubeconfig file for OKE cluster

**How to get:**

#### Step 1: Create kubeconfig
```bash
# Set your cluster OCID (get from OCI Console)
export CLUSTER_OCID="ocid1.cluster.oc1.iad.xxx"
export OCI_REGION="us-ashburn-1"

# Generate kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id "$CLUSTER_OCID" \
  --file ~/.kube/oke-config \
  --region "$OCI_REGION" \
  --token-version 2.0.0
```

#### Step 2: Base64 encode
```bash
# Linux/macOS
cat ~/.kube/oke-config | base64 -w 0

# macOS (alternative)
cat ~/.kube/oke-config | base64

# Windows (PowerShell)
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$HOME\.kube\oke-config"))
```

#### Step 3: Add to GitHub
- **Name**: `OKE_KUBECONFIG`
- **Value**: (paste base64 encoded string)

**Important**: The value should be one long line with no line breaks.

---

### 2. COMPARTMENT_OCID

**Description**: Oracle Cloud compartment identifier

**How to get:**
1. Login to OCI Console: https://cloud.oracle.com
2. Navigate to: **Identity & Security** > **Compartments**
3. Find your compartment (e.g., "todo-app-compartment")
4. Click on the compartment name
5. Copy the **OCID** (starts with `ocid1.compartment.oc1..`)

**Add to GitHub:**
- **Name**: `COMPARTMENT_OCID`
- **Value**: (paste OCID)

**Example:**
```
ocid1.compartment.oc1..aaaaaaaay7pq2z3nxpxqrqxqz7wq8z9z8z7z6z5z4z3z2z1z
```

---

## Google Cloud (GKE) Secrets

Required if deploying to Google Kubernetes Engine.

### 1. GKE_SA_KEY

**Description**: Google Cloud service account key (JSON)

**How to get:**

#### Step 1: Create service account
```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions" \
  --project="$PROJECT_ID"

# Grant permissions
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/container.developer"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
```

#### Step 2: Create key
```bash
gcloud iam service-accounts keys create ~/gke-key.json \
  --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com
```

#### Step 3: Add to GitHub
- **Name**: `GKE_SA_KEY`
- **Value**: (paste entire contents of `~/gke-key.json`)

**Important**: Paste the entire JSON file, including `{` and `}`.

---

### 2. GKE_CLUSTER_NAME

**Description**: Name of your GKE cluster

**Add to GitHub:**
- **Name**: `GKE_CLUSTER_NAME`
- **Value**: `todo-app-cluster` (or your cluster name)

---

### 3. GKE_ZONE

**Description**: GCP zone where cluster is located

**Add to GitHub:**
- **Name**: `GKE_ZONE`
- **Value**: `us-central1-a` (or your zone)

---

## Azure (AKS) Secrets

Required if deploying to Azure Kubernetes Service.

### 1. AZURE_CREDENTIALS

**Description**: Azure service principal credentials (JSON)

**How to get:**

#### Step 1: Create service principal
```bash
# Login to Azure
az login

# Set subscription
export SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Create service principal
az ad sp create-for-rbac \
  --name "github-actions-todo-app" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID \
  --sdk-auth
```

#### Step 2: Copy output
The command outputs JSON like:
```json
{
  "clientId": "xxx",
  "clientSecret": "xxx",
  "subscriptionId": "xxx",
  "tenantId": "xxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

#### Step 3: Add to GitHub
- **Name**: `AZURE_CREDENTIALS`
- **Value**: (paste entire JSON output)

---

### 2. AKS_RESOURCE_GROUP

**Description**: Azure resource group name

**Add to GitHub:**
- **Name**: `AKS_RESOURCE_GROUP`
- **Value**: `todo-app-rg` (or your resource group name)

---

### 3. AKS_CLUSTER_NAME

**Description**: Name of your AKS cluster

**Add to GitHub:**
- **Name**: `AKS_CLUSTER_NAME`
- **Value**: `todo-app-cluster` (or your cluster name)

---

## Secret Summary Table

| Secret Name | Required For | Description |
|-------------|-------------|-------------|
| `DATABASE_URL` | All platforms | Neon PostgreSQL connection string |
| `JWT_SECRET` | All platforms | JWT signing secret |
| `BETTER_AUTH_SECRET` | All platforms | Auth session encryption secret |
| `KAFKA_BROKERS` | All platforms | Redpanda Cloud bootstrap servers |
| `OPENAI_API_KEY` | All platforms (optional) | OpenAI API key for AI features |
| `OKE_KUBECONFIG` | Oracle OKE | Base64-encoded kubeconfig |
| `COMPARTMENT_OCID` | Oracle OKE | OCI compartment identifier |
| `GKE_SA_KEY` | Google GKE | Service account JSON key |
| `GKE_CLUSTER_NAME` | Google GKE | GKE cluster name |
| `GKE_ZONE` | Google GKE | GCP zone |
| `AZURE_CREDENTIALS` | Azure AKS | Service principal JSON |
| `AKS_RESOURCE_GROUP` | Azure AKS | Azure resource group |
| `AKS_CLUSTER_NAME` | Azure AKS | AKS cluster name |

---

## Verification

After adding all secrets, verify they are correctly configured:

### 1. Check Secrets List

In GitHub repository:
1. Go to: **Settings** > **Secrets and variables** > **Actions**
2. Verify all required secrets are listed
3. Secret values are hidden (cannot be viewed after creation)

### 2. Test with Manual Workflow Run

1. Go to: **Actions** tab
2. Select **Deploy Todo App to Cloud**
3. Click **Run workflow**
4. Select branch: `main`
5. Click **Run workflow**
6. Watch for errors in the workflow logs

### 3. Common Verification Errors

**Error: `No such secret: DATABASE_URL`**
- Solution: Add the missing secret

**Error: `Invalid kubeconfig`**
- Solution: Re-encode kubeconfig and ensure no line breaks

**Error: `Authentication failed`**
- Solution: Regenerate service account key/credentials

**Error: `Cluster not found`**
- Solution: Verify cluster name and region/zone match

---

## Security Best Practices

### 1. Rotate Secrets Regularly

```bash
# Generate new JWT secret
openssl rand -base64 32

# Update in GitHub Secrets
# Update in Kubernetes: kubectl create secret ... --dry-run=client -o yaml | kubectl apply -f -
```

### 2. Use Separate Secrets for Environments

Create environment-specific secrets:
- `DATABASE_URL_STAGING`
- `DATABASE_URL_PRODUCTION`

Modify workflow to use based on environment:
```yaml
env:
  DATABASE_URL: ${{ github.ref == 'refs/heads/main' && secrets.DATABASE_URL_PRODUCTION || secrets.DATABASE_URL_STAGING }}
```

### 3. Limit Secret Scope

- Use separate service accounts per environment
- Grant minimum required permissions
- Enable audit logging for secret access

### 4. Never Commit Secrets

Add to `.gitignore`:
```
.env
.env.*
*.key
*.pem
kubeconfig*
gke-key.json
```

### 5. Use Secret Scanning

Enable GitHub secret scanning:
1. Go to: **Settings** > **Code security and analysis**
2. Enable **Secret scanning**
3. Enable **Push protection**

---

## Troubleshooting

### Issue: Secret value contains line breaks

**Solution:**
```bash
# Remove line breaks when base64 encoding
cat file | base64 -w 0  # Linux
cat file | base64 | tr -d '\n'  # macOS
```

### Issue: JSON secret is invalid

**Solution:**
- Ensure JSON is valid: https://jsonlint.com
- Copy entire JSON output including `{` and `}`
- No trailing commas or comments

### Issue: kubeconfig not working

**Solution:**
```bash
# Test kubeconfig locally first
export KUBECONFIG=~/.kube/oke-config
kubectl cluster-info

# If working, encode and add to GitHub
cat ~/.kube/oke-config | base64 -w 0
```

### Issue: Database connection fails

**Solution:**
- Verify connection string format includes `?sslmode=require`
- Test connection locally: `psql $DATABASE_URL`
- Check Neon database is not paused (free tier)
- Verify IP allowlist in Neon (set to "Allow all")

---

## Quick Setup Script

Use this script to generate all required secrets:

```bash
#!/bin/bash
# generate-secrets.sh

echo "Generating secrets for GitHub Actions..."
echo ""

echo "JWT_SECRET:"
openssl rand -base64 32
echo ""

echo "BETTER_AUTH_SECRET:"
openssl rand -base64 32
echo ""

echo "DATABASE_URL:"
echo "Get from: https://neon.tech > Dashboard > Connection Details"
echo ""

echo "KAFKA_BROKERS:"
echo "Get from: https://cloud.redpanda.com > Cluster > Connect"
echo ""

echo "OKE_KUBECONFIG (base64):"
if [ -f ~/.kube/oke-config ]; then
  cat ~/.kube/oke-config | base64 -w 0
  echo ""
else
  echo "File not found. Generate with:"
  echo "oci ce cluster create-kubeconfig --cluster-id <id> --file ~/.kube/oke-config"
fi
echo ""

echo "COMPARTMENT_OCID:"
echo "Get from: OCI Console > Identity & Security > Compartments"
echo ""

echo "Done! Copy these values to GitHub Secrets."
```

Run:
```bash
chmod +x generate-secrets.sh
./generate-secrets.sh
```

---

## Additional Resources

- **GitHub Secrets Documentation**: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **Oracle OKE kubeconfig**: https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengdownloadkubeconfigfile.htm
- **GKE Service Accounts**: https://cloud.google.com/kubernetes-engine/docs/how-to/iam
- **Azure Service Principals**: https://learn.microsoft.com/en-us/azure/aks/kubernetes-service-principal

---

🔒 Keep your secrets safe and rotate them regularly!

---

🚀 Generated with [Claude Code](https://claude.com/claude-code)

# Todo App Deployment Guide

Complete guide for deploying the Todo Full-Stack Web Application to production.

**Frontend**: Vercel
**Backend**: Railway
**Database**: Neon PostgreSQL (already configured)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Deployment (Railway)](#backend-deployment-railway)
3. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
4. [Environment Variables](#environment-variables)
5. [Post-Deployment Testing](#post-deployment-testing)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- [ ] GitHub account (for code repository)
- [ ] Railway account (https://railway.app)
- [ ] Vercel account (https://vercel.com)
- [ ] Neon PostgreSQL account (already have database)

### Required Tools
- [ ] Git installed and configured
- [ ] Node.js 18+ installed (for local testing)
- [ ] Python 3.11+ installed (for local testing)

### Required Information
Before deploying, gather:
- [ ] Neon PostgreSQL connection string (from dashboard)
- [ ] Better Auth Secret (72 characters, shared between frontend/backend)
- [ ] GitHub repository URL

---

## Backend Deployment (Railway)

### Step 1: Prepare Backend for Deployment

#### 1.1 Create Railway Configuration File

Create `railway.toml` in the `backend` directory:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

#### 1.2 Verify `requirements.txt`

Ensure `backend/requirements.txt` contains:

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlmodel==0.0.14
asyncpg==0.31.0
python-dotenv==1.0.0
pyjwt==2.8.0
python-multipart==0.0.9
passlib[bcrypt]==1.7.4
```

### Step 2: Deploy to Railway

#### 2.1 Push Code to GitHub

```bash
# From project root
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

#### 2.2 Create Railway Project

1. Go to https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will detect the Python app automatically

#### 2.3 Configure Railway Service

1. Click on the deployed service
2. Go to **Settings** tab
3. Set **Root Directory**: `Phase 2/backend`
4. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 2.4 Add Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.aws.neon.tech/neondb?sslmode=require

# Authentication (MUST match frontend)
BETTER_AUTH_SECRET=your-72-character-secret-here

# CORS - Add your Vercel domain here after frontend deployment
CORS_ORIGINS=https://your-app.vercel.app

# Environment
ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO
```

**Important Notes**:
- Replace `DATABASE_URL` with your actual Neon PostgreSQL connection string
- Generate `BETTER_AUTH_SECRET` with: `openssl rand -base64 48`
- After deploying frontend, update `CORS_ORIGINS` with your Vercel domain

#### 2.5 Get Railway Backend URL

1. Go to **Settings** tab
2. Click **Generate Domain**
3. Copy the domain (e.g., `your-app.up.railway.app`)
4. **Save this URL** - you'll need it for frontend deployment

### Step 3: Verify Backend Deployment

Test the backend API:

```bash
# Check health endpoint
curl https://your-app.up.railway.app/

# Expected response: {"message":"Todo API is running"}
```

---

## Frontend Deployment (Vercel)

### Step 1: Prepare Frontend for Deployment

#### 1.1 Update API URL Configuration

No changes needed - environment variables will be set in Vercel dashboard.

#### 1.2 Verify Build

Test the production build locally:

```bash
cd frontend
npm run build
```

Ensure build completes without errors.

### Step 2: Deploy to Vercel

#### 2.1 Deploy via Vercel Dashboard

1. Go to https://vercel.com/new
2. Click **"Import Git Repository"**
3. Select your GitHub repository
4. Click **Import**

#### 2.2 Configure Vercel Project Settings

**Framework Preset**: Next.js
**Root Directory**: `Phase 2/frontend`
**Build Command**: `npm run build`
**Output Directory**: `.next` (default)
**Install Command**: `npm install`

#### 2.3 Add Environment Variables

In Vercel dashboard, go to **Settings** > **Environment Variables** and add:

```bash
# Better Auth Secret (MUST match backend)
BETTER_AUTH_SECRET=your-72-character-secret-here-same-as-backend

# Better Auth URL (your Vercel domain)
BETTER_AUTH_URL=https://your-app.vercel.app

# API URL (your Railway backend URL)
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app
```

**Important Notes**:
- `BETTER_AUTH_SECRET` MUST be identical to backend
- Replace `BETTER_AUTH_URL` with your actual Vercel domain
- Replace `NEXT_PUBLIC_API_URL` with your Railway backend URL

#### 2.4 Deploy

1. Click **Deploy**
2. Wait for deployment to complete (2-3 minutes)
3. Copy your Vercel domain (e.g., `your-app.vercel.app`)

### Step 3: Update Backend CORS

After getting your Vercel domain:

1. Go back to **Railway dashboard**
2. Go to **Variables** tab
3. Update `CORS_ORIGINS`:

```bash
CORS_ORIGINS=https://your-app.vercel.app
```

4. Save changes (Railway will automatically redeploy)

---

## Environment Variables

### Complete Environment Variables Checklist

#### Backend (Railway)

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Neon PostgreSQL connection string | `postgresql+asyncpg://user:pass@ep-xxx.aws.neon.tech/neondb?sslmode=require` | ✅ Yes |
| `BETTER_AUTH_SECRET` | Shared secret for JWT (72 chars) | Generated with `openssl rand -base64 48` | ✅ Yes |
| `CORS_ORIGINS` | Allowed frontend domains | `https://your-app.vercel.app` | ✅ Yes |
| `ENVIRONMENT` | Environment name | `production` | ✅ Yes |
| `LOG_LEVEL` | Logging level | `INFO` | Optional |

#### Frontend (Vercel)

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `BETTER_AUTH_SECRET` | Shared secret for JWT (MUST match backend) | Same as backend | ✅ Yes |
| `BETTER_AUTH_URL` | Frontend base URL | `https://your-app.vercel.app` | ✅ Yes |
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://your-app.up.railway.app` | ✅ Yes |

### Generating Secrets

```bash
# Generate Better Auth Secret (run once, use for both frontend and backend)
openssl rand -base64 48
```

**CRITICAL**: The `BETTER_AUTH_SECRET` must be exactly the same in both frontend and backend, or authentication will fail.

---

## Post-Deployment Testing

### 1. Test Backend API

```bash
# Health check
curl https://your-app.up.railway.app/

# Expected: {"message":"Todo API is running"}
```

### 2. Test Frontend

1. Open your Vercel domain in browser: `https://your-app.vercel.app`
2. You should be redirected to `/auth/signin`

### 3. Test Full Authentication Flow

#### Step 1: Sign Up
1. Click **Sign Up**
2. Enter email, name, password
3. Should redirect to `/tasks`

#### Step 2: Create Task
1. Enter task title and description
2. Click **Add Task**
3. Task should appear in list

#### Step 3: Update Task
1. Click **Edit** on a task
2. Change title
3. Click **Save**
4. Changes should persist

#### Step 4: Mark Complete
1. Check the checkbox on a task
2. Task should show as completed

#### Step 5: Delete Task
1. Click **Delete** on a task
2. Confirm deletion
3. Task should be removed

#### Step 6: Sign Out and Sign In
1. Click **Sign Out**
2. Should redirect to `/auth/signin`
3. Sign in with same credentials
4. Tasks should still be there

### 4. Test User Isolation

1. Open incognito window
2. Sign up as different user
3. Create tasks
4. Verify you only see your own tasks (not other user's tasks)

---

## Troubleshooting

### Backend Issues

#### Error: "Database connection failed"
**Solution**: Check your `DATABASE_URL` in Railway variables
- Ensure connection string is from Neon dashboard
- Must use `postgresql+asyncpg://` prefix
- Must include `?sslmode=require` at the end

#### Error: "CORS policy blocked"
**Solution**: Update `CORS_ORIGINS` in Railway
```bash
CORS_ORIGINS=https://your-app.vercel.app
```
- No trailing slash
- Use HTTPS in production
- No spaces between multiple origins

#### Error: "Port binding failed"
**Solution**: Ensure start command uses `$PORT`
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend Issues

#### Error: "Failed to fetch"
**Solution**: Check `NEXT_PUBLIC_API_URL` in Vercel
- Must be your Railway backend URL
- Must include `https://`
- No trailing slash

#### Error: "Authentication failed"
**Solution**: Verify `BETTER_AUTH_SECRET` matches
- Check Railway backend variables
- Check Vercel frontend variables
- Must be exactly the same (72 characters)

#### Error: "Redirect loop"
**Solution**: Check `BETTER_AUTH_URL` in Vercel
- Must be your Vercel frontend URL
- Must include `https://`
- No trailing slash

#### Build Error: "Module not found"
**Solution**: Clear Vercel cache and redeploy
1. Go to Vercel dashboard
2. Settings > General
3. Click **Clear Build Cache**
4. Go to Deployments
5. Click **Redeploy**

### Database Issues

#### Error: "Table does not exist"
**Solution**: Database tables should auto-create on first request
- Make sure `DATABASE_URL` is correct
- Check Railway logs for errors
- Tables are created automatically by SQLModel

---

## Production URLs

After deployment, update this section with your actual URLs:

- **Frontend (Vercel)**: https://your-app.vercel.app
- **Backend (Railway)**: https://your-app.up.railway.app
- **Database (Neon)**: Already configured

---

## Security Checklist

Before going live:

- [ ] Different `BETTER_AUTH_SECRET` than development (72 chars minimum)
- [ ] `CORS_ORIGINS` set to only your frontend domain
- [ ] `DATABASE_URL` connection string uses SSL (`?sslmode=require`)
- [ ] `LOG_LEVEL` set to `INFO` or `WARNING` in production
- [ ] No secrets committed to git (check `.env` files are in `.gitignore`)
- [ ] Environment variables set in platform dashboards (not in code)

---

## Cost Estimates

### Railway (Backend)
- **Free Tier**: $5 credit/month (should cover small usage)
- **Starter Plan**: $5/month after free tier
- **Expected Cost**: $0-5/month for small apps

### Vercel (Frontend)
- **Hobby Plan**: FREE
- **Unlimited deployments**
- **100GB bandwidth/month**
- **Expected Cost**: $0/month

### Neon PostgreSQL (Database)
- **Free Tier**: 0.5GB storage, 1 project
- **Expected Cost**: $0/month for development

**Total Expected Cost**: $0-5/month

---

## Deployment Checklist

### Pre-Deployment
- [x] Code pushed to GitHub
- [x] Environment example files created
- [x] Build tested locally
- [x] Unnecessary files removed

### Backend (Railway)
- [ ] Railway project created
- [ ] Root directory set to `Phase 2/backend`
- [ ] Environment variables configured
- [ ] Domain generated
- [ ] Health check passes

### Frontend (Vercel)
- [ ] Vercel project created
- [ ] Root directory set to `Phase 2/frontend`
- [ ] Environment variables configured
- [ ] Build successful
- [ ] Domain assigned

### Post-Deployment
- [ ] Backend CORS updated with Vercel domain
- [ ] Full authentication flow tested
- [ ] CRUD operations tested
- [ ] User isolation verified
- [ ] Production URLs documented

---

## Support

If you encounter issues:

1. Check Railway logs: Railway Dashboard > Deployments > View Logs
2. Check Vercel logs: Vercel Dashboard > Deployments > Functions
3. Check browser console: F12 > Console tab
4. Verify environment variables match exactly

---

**Deployment Date**: _____________
**Deployed By**: _____________
**Frontend URL**: _____________
**Backend URL**: _____________

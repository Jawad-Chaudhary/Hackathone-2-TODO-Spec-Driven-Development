# Backend Deployment Guide - Render

This guide walks you through deploying your FastAPI backend to Render.

---

## Prerequisites

- ✅ Render account (free tier works fine)
- ✅ GitHub repository with your code
- ✅ Neon PostgreSQL database (already set up)
- ✅ Backend code tested locally

---

## Step 1: Prepare Your Repository

### 1.1 Ensure Required Files Exist

Your backend directory should have:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   └── ... (other files)
├── requirements.txt
├── pyproject.toml
├── render.yaml (optional, for infrastructure as code)
└── .env.example
```

### 1.2 Verify `requirements.txt`

Make sure your `requirements.txt` includes all dependencies:

```txt
fastapi>=0.100.0
sqlmodel>=0.0.14
pydantic>=2.0
pydantic-settings>=2.0
pyjwt>=2.8
uvicorn[standard]>=0.27
asyncpg>=0.29
python-dotenv>=1.0
```

### 1.3 Create `.env.example` (If Not Exists)

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@host/database

# Authentication Configuration
BETTER_AUTH_SECRET=your-secret-key-here

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app

# Environment
ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO
```

---

## Step 2: Push to GitHub

```bash
# From your project root
git add .
git commit -m "Prepare backend for Render deployment"
git push origin main
```

---

## Step 3: Create Web Service on Render

### 3.1 Go to Render Dashboard

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**

### 3.2 Connect Repository

1. Connect your GitHub account (if not already connected)
2. Select your repository
3. Click **"Connect"**

### 3.3 Configure Web Service

Fill in the following settings:

| Setting | Value |
|---------|-------|
| **Name** | `todo-backend` (or your preferred name) |
| **Region** | Choose closest to your users |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` (or upgrade as needed) |

**Important Notes:**
- ✅ Set **Root Directory** to `backend` so Render runs commands from the backend folder
- ✅ Use `$PORT` environment variable - Render assigns this automatically
- ✅ Use `--host 0.0.0.0` to bind to all interfaces

---

## Step 4: Configure Environment Variables

In the Render dashboard, scroll down to **"Environment Variables"** and add:

### 4.1 Required Environment Variables

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://[user]:[pass]@[host]/[db]` | Get from Neon dashboard |
| `BETTER_AUTH_SECRET` | Your secret key | **MUST match frontend exactly** |
| `CORS_ORIGINS` | `http://localhost:3000,https://your-app.vercel.app` | Add all frontend URLs |
| `ENVIRONMENT` | `production` | Sets production mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `PYTHON_VERSION` | `3.13` | Optional: specify Python version |

### 4.2 Get Your Neon Database URL

1. Go to https://console.neon.tech/
2. Select your project
3. Go to **"Connection Details"**
4. Copy the connection string
5. **Important**: Replace `postgresql://` with `postgresql+asyncpg://`

Example:
```
Original: postgresql://user:pass@host.aws.neon.tech/db
Modified: postgresql+asyncpg://user:pass@host.aws.neon.tech/db
```

### 4.3 Generate BETTER_AUTH_SECRET (If Needed)

```bash
# Run locally to generate a secure secret
openssl rand -base64 48
```

**⚠️ CRITICAL**: This secret **must be identical** in both backend and frontend!

---

## Step 5: Deploy

1. Click **"Create Web Service"** at the bottom
2. Render will start building and deploying
3. Watch the deployment logs in real-time

### Expected Deployment Process:

```
==> Cloning from https://github.com/your-repo...
==> Checking out commit abc123...
==> Running build command: pip install -r requirements.txt...
==> Build successful
==> Starting service with: uvicorn app.main:app --host 0.0.0.0 --port $PORT
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000
```

---

## Step 6: Verify Deployment

### 6.1 Check Health Endpoint

Once deployed, Render will give you a URL like: `https://todo-backend-xxxx.onrender.com`

Test the health endpoint:
```bash
curl https://todo-backend-xxxx.onrender.com/health
```

Expected response:
```json
{"status": "healthy"}
```

### 6.2 Check API Documentation

Visit: `https://todo-backend-xxxx.onrender.com/docs`

You should see the Swagger UI with all your endpoints.

### 6.3 Test Root Endpoint

```bash
curl https://todo-backend-xxxx.onrender.com/
```

Expected response:
```json
{
  "message": "Todo Backend API",
  "status": "running"
}
```

---

## Step 7: Update Frontend Configuration

Update your frontend to use the new backend URL:

**File: `frontend/.env.local`**
```bash
# Add or update this line
NEXT_PUBLIC_API_URL=https://todo-backend-xxxx.onrender.com
```

**Update CORS_ORIGINS in Backend**

Go back to Render dashboard → Your service → Environment → Edit `CORS_ORIGINS`:
```
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app,https://your-frontend-preview.vercel.app
```

Click **"Save Changes"** - Render will automatically redeploy.

---

## Troubleshooting

### Issue 1: Build Fails

**Error**: `Could not find a version that satisfies the requirement...`

**Solution**: Check `requirements.txt` has correct package versions:
```bash
# Regenerate requirements.txt locally
cd backend
uv pip compile pyproject.toml -o requirements.txt
git add requirements.txt
git commit -m "Update requirements.txt"
git push
```

### Issue 2: Database Connection Error

**Error**: `could not connect to server`

**Solution**:
1. Verify `DATABASE_URL` is correct
2. Ensure it uses `postgresql+asyncpg://` prefix
3. Check Neon database is running (not suspended)
4. Verify IP whitelist in Neon (Render IPs should be allowed)

### Issue 3: Application Won't Start

**Error**: `Address already in use` or Port binding error

**Solution**: Ensure start command uses `$PORT`:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Issue 4: CORS Errors from Frontend

**Error**: `Access to fetch blocked by CORS policy`

**Solution**:
1. Add your frontend URL to `CORS_ORIGINS`
2. Include both production and preview URLs for Vercel
3. Redeploy backend after updating

### Issue 5: 401 Unauthorized on All Requests

**Solution**: Verify `BETTER_AUTH_SECRET` matches between frontend and backend **exactly**.

---

## Render.yaml (Infrastructure as Code) - Optional

You already have a `render.yaml` file. To use it:

1. Go to Render Dashboard → **"New +"** → **"Blueprint"**
2. Connect your repository
3. Render will automatically detect and use `render.yaml`

**Current `render.yaml` configuration:**
```yaml
services:
  - type: web
    name: todo-backend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: BETTER_AUTH_SECRET
        sync: false
      - key: CORS_ORIGINS
        sync: false
      - key: ENVIRONMENT
        value: production
      - key: LOG_LEVEL
        value: INFO
```

---

## Monitoring & Logs

### View Logs

1. Go to your service in Render dashboard
2. Click **"Logs"** tab
3. See real-time application logs

### Check Metrics

1. Click **"Metrics"** tab
2. Monitor CPU, Memory, Request count

### Set Up Alerts (Optional)

1. Go to service settings
2. Add notification webhooks for:
   - Service down
   - High CPU/Memory usage
   - Failed deployments

---

## Production Best Practices

### 1. Health Checks
Render automatically monitors `/` endpoint. Your app returns proper status codes.

### 2. Auto-Deploy
Enabled by default - pushes to `main` branch trigger deployments.

### 3. Zero-Downtime Deploys
Render handles this automatically on paid plans.

### 4. Environment Variables
- ✅ Never commit `.env` to git
- ✅ Use Render's encrypted environment variables
- ✅ Rotate secrets periodically

### 5. Database Backups
Neon provides automatic backups - verify they're enabled.

### 6. Scaling
- Free tier: 1 instance, 512 MB RAM
- Upgrade to scale horizontally (multiple instances)

---

## Cost Optimization

### Free Tier Limits
- ✅ 750 hours/month (enough for 1 service)
- ✅ Sleeps after 15 min inactivity
- ✅ Cold start ~30 seconds

### Upgrade Considerations
- Multiple services or need for always-on: **$7/month (Starter)**
- Better performance: **$25/month (Standard)**

---

## Useful Commands

### Restart Service
```bash
# Via Render Dashboard
Settings → Manual Deploy → "Clear build cache & deploy"
```

### View Environment Variables
```bash
# Cannot view via CLI - use dashboard
```

### Rollback Deployment
1. Go to "Events" tab
2. Find previous successful deploy
3. Click "Rollback to this version"

---

## Deployment Checklist

- [ ] Repository pushed to GitHub
- [ ] `requirements.txt` includes all dependencies
- [ ] `.env.example` created (don't commit `.env`)
- [ ] Render web service created
- [ ] Root directory set to `backend`
- [ ] Environment variables configured
- [ ] Database URL uses `postgresql+asyncpg://`
- [ ] `BETTER_AUTH_SECRET` matches frontend
- [ ] CORS origins include frontend URLs
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] API docs accessible at `/docs`
- [ ] Frontend updated with backend URL

---

## Next Steps

1. ✅ Deploy frontend to Vercel
2. ✅ Update frontend `.env` with Render backend URL
3. ✅ Test full authentication flow
4. ✅ Set up custom domain (optional)
5. ✅ Enable SSL (automatic on Render)

---

## Support

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/deployment/

---

## Summary

Your backend is now:
- ✅ Deployed to Render
- ✅ Connected to Neon PostgreSQL
- ✅ Auto-deploying on git push
- ✅ SSL enabled by default
- ✅ Health monitored automatically

**Your Backend URL**: `https://todo-backend-xxxx.onrender.com`

Use this URL in your frontend configuration! 🚀

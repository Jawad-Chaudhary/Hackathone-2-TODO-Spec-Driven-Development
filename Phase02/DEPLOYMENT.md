# [Task T079] Deployment Guide - Todo Full-Stack Web Application

## Overview

This guide walks you through deploying the Todo application to Vercel, including both the Next.js frontend and FastAPI backend.

## Prerequisites

- Vercel account (https://vercel.com)
- GitHub/GitLab/Bitbucket repository with your code
- Neon PostgreSQL database (https://neon.tech)
- Generated `BETTER_AUTH_SECRET` (64+ characters)

---

## Part 1: Environment Variables Setup

### Generate BETTER_AUTH_SECRET

```bash
# Generate a secure 64-character secret
openssl rand -base64 48
```

Copy this value - you'll use it for BOTH frontend and backend.

### Backend Environment Variables

Create these environment variables in Vercel (Backend project):

| Variable | Example Value | Description |
|----------|---------------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host/db` | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | `<your-64-char-secret>` | JWT signing secret (MUST match frontend) |
| `CORS_ORIGINS` | `https://your-app.vercel.app` | Comma-separated allowed origins |
| `ENVIRONMENT` | `production` | Environment name |
| `LOG_LEVEL` | `INFO` | Logging level |

### Frontend Environment Variables

Create these environment variables in Vercel (Frontend project):

| Variable | Example Value | Description |
|----------|---------------|-------------|
| `BETTER_AUTH_SECRET` | `<your-64-char-secret>` | JWT signing secret (MUST match backend) |
| `BETTER_AUTH_URL` | `https://your-app.vercel.app` | Frontend base URL |
| `NEXT_PUBLIC_API_URL` | `https://your-api.vercel.app` | Backend API URL |

---

## Part 2: Deploy Backend (FastAPI on Vercel)

### Step 1: Create `vercel.json` in Backend Directory

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ]
}
```

### Step 2: Create `requirements.txt` from pyproject.toml

```bash
cd backend
uv pip compile pyproject.toml -o requirements.txt
```

### Step 3: Deploy to Vercel

1. Go to https://vercel.com/new
2. Import your repository
3. Select `backend/` as root directory
4. Framework Preset: Other
5. Build Command: (leave empty)
6. Output Directory: (leave empty)
7. Add environment variables (see table above)
8. Click "Deploy"

### Step 4: Note Your Backend URL

After deployment, copy the URL (e.g., `https://your-api.vercel.app`)

---

## Part 3: Deploy Frontend (Next.js on Vercel)

### Step 1: Deploy to Vercel

1. Go to https://vercel.com/new
2. Import your repository
3. Select `frontend/` as root directory
4. Framework Preset: Next.js
5. Build Command: `npm run build` (or `pnpm build`)
6. Output Directory: `.next`
7. Add environment variables:
   - `BETTER_AUTH_SECRET` (same as backend)
   - `BETTER_AUTH_URL` → your frontend URL (will be shown after deploy)
   - `NEXT_PUBLIC_API_URL` → your backend URL from Step 4
8. Click "Deploy"

### Step 2: Update Environment Variables

After first deployment:
1. Go to Project Settings → Environment Variables
2. Update `BETTER_AUTH_URL` with your actual frontend URL
3. Redeploy from Deployments tab

---

## Part 4: Update Backend CORS (T083)

After frontend is deployed, update backend CORS_ORIGINS:

1. Go to backend Vercel project
2. Settings → Environment Variables
3. Update `CORS_ORIGINS` to include your frontend URL:
   ```
   https://your-app.vercel.app,https://*.vercel.app
   ```
4. Redeploy backend from Deployments tab

---

## Part 5: Database Setup

### Neon PostgreSQL Configuration

1. Create Neon database: https://console.neon.tech
2. Copy connection string (format: `postgresql://user:pass@host/dbname`)
3. Convert to async format:
   ```
   postgresql+asyncpg://user:pass@host/dbname
   ```
4. Add to backend `DATABASE_URL` environment variable
5. Tables will be created automatically on first backend startup

### Verify Database

After backend deployment, check logs:
```
✅ Database tables created successfully
```

---

## Part 6: End-to-End Testing (T084)

### Manual Testing Checklist

Test all user stories in production:

#### US1 - Authentication
- [ ] Sign up with new account
- [ ] JWT token stored in httpOnly cookie
- [ ] Sign in with valid credentials
- [ ] Sign out (session cleared)
- [ ] Access /tasks without auth → redirects to signin
- [ ] Duplicate email → error message

#### US2 - Create and View Tasks
- [ ] Create task with title and description
- [ ] Task appears in list (newest first)
- [ ] Refresh page → tasks persist
- [ ] View empty state
- [ ] Create task with empty title → validation error
- [ ] Create task with 201-char title → validation error

#### US3 - Mark Tasks Complete
- [ ] Toggle task completion (checkbox)
- [ ] Strikethrough styling on completed tasks
- [ ] Refresh page → completion status persists
- [ ] Optimistic UI update (instant feedback)

#### US4 - Edit Tasks
- [ ] Click Edit → form appears with existing data
- [ ] Modify and save → database updated
- [ ] Cancel edit → changes discarded
- [ ] Edit with empty title → validation error

#### US5 - Delete Tasks
- [ ] Click Delete → confirmation modal appears
- [ ] Confirm → task removed from database
- [ ] Cancel → task remains
- [ ] Refresh → deleted task does not reappear

### Cross-Cutting Tests
- [ ] CORS works (no errors in browser console)
- [ ] Health check: `curl https://your-api.vercel.app/health`
- [ ] Error boundary catches React errors
- [ ] Responsive design works (test on mobile/tablet/desktop)
- [ ] Loading states display correctly
- [ ] User isolation (create 2 accounts, verify can't see each other's tasks)

---

## Troubleshooting

### Issue: CORS errors in browser console

**Solution**:
- Verify `CORS_ORIGINS` in backend includes exact frontend URL
- Redeploy backend after changing CORS_ORIGINS
- Check for trailing slashes (use `https://app.vercel.app` not `https://app.vercel.app/`)

### Issue: 401 Unauthorized on API requests

**Solution**:
- Verify `BETTER_AUTH_SECRET` matches EXACTLY in frontend and backend
- Redeploy both frontend and backend
- Clear browser cookies and sign in again

### Issue: Database connection error

**Solution**:
- Verify `DATABASE_URL` format: `postgresql+asyncpg://...`
- Check Neon database is active (not paused)
- Verify IP allowlist in Neon (should allow all IPs for Vercel)

### Issue: Build fails on Vercel

**Frontend**:
- Check `package.json` has all dependencies
- Run `npm install` locally to verify
- Check build logs for TypeScript errors

**Backend**:
- Verify `requirements.txt` exists with all dependencies
- Check `vercel.json` is configured correctly
- Verify Python version compatibility (3.13+)

---

## Monitoring & Maintenance

### Health Checks

Monitor backend health:
```bash
curl https://your-api.vercel.app/health
# Expected: {"status": "healthy"}
```

### Logs

View logs in Vercel:
1. Go to project → Deployments
2. Click deployment
3. View Function Logs (backend) or Build Logs (frontend)

### Environment Variable Updates

To update environment variables:
1. Go to Project Settings → Environment Variables
2. Edit variable
3. Redeploy from Deployments tab (required for changes to take effect)

---

## Security Checklist

- [X] `BETTER_AUTH_SECRET` is 64+ characters
- [X] `DATABASE_URL` stored securely (not in code)
- [X] CORS configured with exact allowed origins
- [X] HTTPS enforced (Vercel provides this automatically)
- [X] JWT tokens in httpOnly cookies (XSS protection)
- [X] User isolation verified (each user sees only their tasks)
- [X] Environment variables never committed to Git

---

## Rollback Procedure

If deployment fails:
1. Go to Vercel project → Deployments
2. Find previous working deployment
3. Click "..." → Promote to Production
4. Previous version is now live

---

## Additional Resources

- Vercel Documentation: https://vercel.com/docs
- Next.js Deployment: https://nextjs.org/docs/deployment
- FastAPI on Vercel: https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python
- Neon Documentation: https://neon.tech/docs
- Better Auth: https://better-auth.com/docs

---

**Deployment Complete!** Your Todo application is now live in production.

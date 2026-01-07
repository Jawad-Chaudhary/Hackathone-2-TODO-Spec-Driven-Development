# Quick Deployment Guide

Fast track deployment instructions for the Todo App.

**Backend**: Render (Free Tier)
**Frontend**: Vercel (Free Tier)
**Database**: Neon PostgreSQL

---

## Prerequisites (5 minutes)

1. Create accounts:
   - **Render**: https://render.com (sign in with GitHub)
   - **Vercel**: https://vercel.com (sign in with GitHub)

2. Get your Neon database URL:
   - Open Neon dashboard: https://console.neon.tech
   - Copy connection string (should start with `postgresql+asyncpg://`)

3. Generate shared secret (run this once):
   ```bash
   openssl rand -base64 48
   ```
   Copy the output - you'll use it for both frontend and backend.

---

## Step 1: Deploy Backend to Render (10 minutes)

### 1.1 Create Render Web Service

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repository

### 1.2 Configure Render Service

Fill in these settings:

- **Name**: `todo-api` (or any name you prefer)
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: `Phase 2/backend`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Instance Type**: `Free`

### 1.3 Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these:

```bash
DATABASE_URL=your-neon-connection-string-here
BETTER_AUTH_SECRET=your-secret-from-prerequisites-here
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=production
LOG_LEVEL=INFO
PYTHON_VERSION=3.11.0
```

**Important**:
- Replace `DATABASE_URL` with your Neon connection string
- Replace `BETTER_AUTH_SECRET` with the secret you generated
- We'll update `CORS_ORIGINS` after deploying frontend

### 1.4 Deploy

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment (free tier takes longer)
3. Copy your Render URL (e.g., `https://todo-api.onrender.com`)

### 1.5 Verify Backend

1. Open your Render URL in browser: `https://todo-api.onrender.com/`
2. Should see: `{"message":"Todo API is running"}`

✅ **Backend deployed!** Save your Render URL.

**Note**: Free tier sleeps after 15 minutes of inactivity. First request after sleep takes ~30 seconds to wake up.

---

## Step 2: Deploy Frontend to Vercel (10 minutes)

### 2.1 Create Vercel Project

1. Go to https://vercel.com/new
2. Click **"Import Git Repository"**
3. Select your repository
4. Click **Import**

### 2.2 Configure Vercel

**Framework Preset**: Next.js (auto-detected)
**Root Directory**: `Phase 2/frontend`

Click **Environment Variables** and add:

```bash
BETTER_AUTH_SECRET=your-secret-from-prerequisites-here
BETTER_AUTH_URL=https://your-app.vercel.app
NEXT_PUBLIC_API_URL=https://your-render-url-here
```

**Important**:
- `BETTER_AUTH_SECRET` must be EXACTLY the same as backend
- Replace `your-render-url-here` with your Render backend URL
- Vercel will show you the domain after clicking Deploy

### 2.3 Deploy

1. Click **Deploy**
2. Wait 2-3 minutes
3. Copy your Vercel domain (e.g., `your-app.vercel.app`)

### 2.4 Update BETTER_AUTH_URL

1. Go to **Settings** > **Environment Variables**
2. Edit `BETTER_AUTH_URL`
3. Replace with your actual Vercel domain: `https://your-app.vercel.app`
4. Click **Save**
5. Go to **Deployments** > **Redeploy**

✅ **Frontend deployed!** Save your Vercel URL.

---

## Step 3: Update Backend CORS (2 minutes)

Now that you have your Vercel domain:

1. Go back to **Render dashboard**
2. Click on your service
3. Go to **Environment** tab
4. Edit `CORS_ORIGINS`
5. Replace with your Vercel domain: `https://your-app.vercel.app`
6. Click **Save Changes**
7. Render will automatically redeploy

✅ **CORS configured!**

---

## Step 4: Test Your App (5 minutes)

1. Open your Vercel URL: `https://your-app.vercel.app`
2. Should redirect to `/auth/signin`

### Test Flow:

1. **Sign Up**:
   - Click "Sign Up"
   - Enter email, name, password
   - Should redirect to `/tasks`

2. **Create Task**:
   - Enter task title
   - Click "Add Task"
   - Task appears in list

3. **Edit Task**:
   - Click "Edit" button
   - Change title
   - Click "Save"
   - Changes appear immediately

4. **Complete Task**:
   - Click checkbox
   - Task shows as completed

5. **Delete Task**:
   - Click "Delete" button
   - Confirm deletion

6. **Sign Out & Sign In**:
   - Click "Sign Out"
   - Sign in again
   - Tasks should still be there

✅ **Deployment complete!**

---

## Quick Reference

### Your URLs

- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-render-url.onrender.com
- **Database**: Already configured in Neon

### Environment Variables Summary

**Backend (Render)**:
```
DATABASE_URL=postgresql+asyncpg://...
BETTER_AUTH_SECRET=<72-char-secret>
CORS_ORIGINS=https://your-app.vercel.app
ENVIRONMENT=production
LOG_LEVEL=INFO
PYTHON_VERSION=3.11.0
```

**Frontend (Vercel)**:
```
BETTER_AUTH_SECRET=<same-72-char-secret>
BETTER_AUTH_URL=https://your-app.vercel.app
NEXT_PUBLIC_API_URL=https://your-render-url.onrender.com
```

---

## Common Issues

### "CORS policy blocked"
→ Update `CORS_ORIGINS` in Render with your Vercel domain

### "Authentication failed"
→ Make sure `BETTER_AUTH_SECRET` is exactly the same in both Render and Vercel

### "Failed to fetch"
→ Check `NEXT_PUBLIC_API_URL` in Vercel points to your Render domain

### "Database connection failed"
→ Verify `DATABASE_URL` in Render is your Neon connection string

### "Backend is slow on first request"
→ This is normal on Render free tier - it sleeps after 15 minutes of inactivity

---

## Alternative: Railway (If You Have Credits)

If you prefer Railway instead of Render:

### Railway Quick Setup

1. Go to https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select your repository
4. **Settings** tab:
   - Root Directory: `Phase 2/backend`
   - Generate Domain
5. **Variables** tab: (same environment variables as Render)
6. Start command in `railway.toml` already configured

**Railway is faster but free tier is limited to $5/month credit.**

---

## Need Help?

Check logs:
- **Render**: Dashboard > Logs tab
- **Vercel**: Dashboard > Deployments > Functions
- **Browser**: F12 > Console tab

For detailed instructions, see `DEPLOYMENT_GUIDE.md`

---

## Cost Comparison

| Service | Free Tier | Limits | Speed |
|---------|-----------|--------|-------|
| **Render** | ✅ Free forever | 750 hours/month, sleeps after 15min | Medium (wakes in ~30s) |
| **Railway** | $5 credit/month | Limited to $5/month | Fast (always on) |
| **Vercel** | ✅ Free forever | 100GB bandwidth/month | Fast |

**Recommended**: Use Render for backend (free) + Vercel for frontend (free) = **$0/month**

---

**Total Deployment Time**: ~25 minutes

**Cost**: $0/month (using free tiers)

**Performance**: Backend sleeps after 15 minutes (Render free tier), wakes in ~30 seconds on first request

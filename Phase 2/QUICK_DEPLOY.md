# Quick Deployment Guide

Fast track deployment instructions for the Todo App.

---

## Prerequisites (5 minutes)

1. Create accounts:
   - Railway: https://railway.app (sign in with GitHub)
   - Vercel: https://vercel.com (sign in with GitHub)

2. Get your Neon database URL:
   - Open Neon dashboard: https://console.neon.tech
   - Copy connection string (should start with `postgresql+asyncpg://`)

3. Generate shared secret (run this once):
   ```bash
   openssl rand -base64 48
   ```
   Copy the output - you'll use it for both frontend and backend.

---

## Step 1: Deploy Backend to Railway (10 minutes)

### 1.1 Create Railway Project

1. Go to https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select your repository
4. Wait for initial deployment

### 1.2 Configure Railway

1. Click on your service
2. Go to **Settings** tab
3. Set **Root Directory**: `Phase 2/backend`
4. Click **Generate Domain** (save this URL!)

### 1.3 Add Environment Variables

Go to **Variables** tab and add these (click **+ New Variable** for each):

```bash
DATABASE_URL=your-neon-connection-string-here
BETTER_AUTH_SECRET=your-secret-from-step-3-here
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Important**:
- Replace `DATABASE_URL` with your Neon connection string
- Replace `BETTER_AUTH_SECRET` with the secret you generated
- We'll update `CORS_ORIGINS` after deploying frontend

### 1.4 Verify Backend

1. Copy your Railway domain (e.g., `your-app.up.railway.app`)
2. Open in browser: `https://your-app.up.railway.app/`
3. Should see: `{"message":"Todo API is running"}`

✅ **Backend deployed!** Save your Railway URL.

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
BETTER_AUTH_SECRET=your-secret-from-step-3-here
BETTER_AUTH_URL=https://your-app.vercel.app
NEXT_PUBLIC_API_URL=https://your-railway-url-here
```

**Important**:
- `BETTER_AUTH_SECRET` must be EXACTLY the same as backend
- Replace `your-railway-url-here` with your Railway backend URL
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

1. Go back to **Railway dashboard**
2. Click on your service
3. Go to **Variables** tab
4. Edit `CORS_ORIGINS`
5. Replace with your Vercel domain: `https://your-app.vercel.app`
6. Click **Save** (Railway auto-redeploys)

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
- **Backend**: https://your-app.up.railway.app
- **Database**: Already configured in Neon

### Environment Variables Summary

**Backend (Railway)**:
```
DATABASE_URL=postgresql+asyncpg://...
BETTER_AUTH_SECRET=<72-char-secret>
CORS_ORIGINS=https://your-app.vercel.app
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Frontend (Vercel)**:
```
BETTER_AUTH_SECRET=<same-72-char-secret>
BETTER_AUTH_URL=https://your-app.vercel.app
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app
```

---

## Common Issues

### "CORS policy blocked"
→ Update `CORS_ORIGINS` in Railway with your Vercel domain

### "Authentication failed"
→ Make sure `BETTER_AUTH_SECRET` is exactly the same in both Railway and Vercel

### "Failed to fetch"
→ Check `NEXT_PUBLIC_API_URL` in Vercel points to your Railway domain

### "Database connection failed"
→ Verify `DATABASE_URL` in Railway is your Neon connection string

---

## Need Help?

Check logs:
- **Railway**: Dashboard > Deployments > View Logs
- **Vercel**: Dashboard > Deployments > Functions
- **Browser**: F12 > Console tab

For detailed instructions, see `DEPLOYMENT_GUIDE.md`

---

**Total Deployment Time**: ~25 minutes

**Cost**: $0/month (using free tiers)

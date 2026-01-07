# Render Deployment - Quick Reference

## 🚀 5-Minute Deployment

### 1. Push to GitHub
```bash
git add .
git commit -m "Deploy to Render"
git push origin main
```

### 2. Create Web Service on Render

**Dashboard**: https://dashboard.render.com/

| Setting | Value |
|---------|-------|
| Service Type | Web Service |
| Repository | Your GitHub repo |
| Name | `todo-backend` |
| Root Directory | `backend` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | Free |

### 3. Set Environment Variables

```bash
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@host.neon.tech/db
BETTER_AUTH_SECRET=your-48-char-secret-from-openssl
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app

# Optional
ENVIRONMENT=production
LOG_LEVEL=INFO
PYTHON_VERSION=3.13
```

### 4. Deploy & Verify

**Health Check**: `https://your-app.onrender.com/health`

Expected: `{"status": "healthy"}`

---

## ⚡ Using render.yaml (Blueprint)

1. Ensure `backend/render.yaml` exists in your repo
2. Go to Render → **New +** → **Blueprint**
3. Connect repository
4. Render auto-configures from `render.yaml`
5. Add environment variables manually (DATABASE_URL, secrets)
6. Click **Apply**

---

## ⚠️ Common Issues

### Build Fails
```bash
# Regenerate requirements.txt
cd backend
uv pip compile pyproject.toml -o requirements.txt
```

### Database Connection Error
- Verify URL format: `postgresql+asyncpg://` (not `postgresql://`)
- Check Neon database is active

### CORS Errors
- Add frontend URL to `CORS_ORIGINS`
- Include both production and preview URLs
- Format: `https://app.vercel.app,https://app-preview.vercel.app`

### 401 Errors Everywhere
- `BETTER_AUTH_SECRET` must match frontend **exactly**

---

## 📋 Environment Variables Checklist

- [ ] `DATABASE_URL` - Neon connection string with `+asyncpg`
- [ ] `BETTER_AUTH_SECRET` - 48+ character secret (matches frontend)
- [ ] `CORS_ORIGINS` - All frontend URLs (comma-separated, no spaces)
- [ ] `ENVIRONMENT` - Set to `production`
- [ ] `LOG_LEVEL` - Set to `INFO` or `DEBUG`

---

## 🔗 After Deployment

1. Copy your Render URL: `https://todo-backend-xxxx.onrender.com`
2. Update frontend `.env.local`:
   ```bash
   NEXT_PUBLIC_API_URL=https://todo-backend-xxxx.onrender.com
   ```
3. Redeploy frontend to Vercel

---

## 📚 Full Guide

See `RENDER_DEPLOYMENT.md` for detailed instructions, troubleshooting, and best practices.

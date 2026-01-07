# [Task T080] Quick Start Guide - Todo Full-Stack Web Application

## Overview

Get the Todo application running locally in under 10 minutes.

---

## Prerequisites

Install these before starting:

- **Node.js 20+** (https://nodejs.org)
- **Python 3.13+** (https://www.python.org)
- **UV** (Python package manager): `pip install uv`
- **Neon PostgreSQL** account (https://neon.tech) - Free tier works

---

## Step 1: Clone & Setup

```bash
# Navigate to Phase 2 directory
cd "Phase 2"

# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ../backend
uv sync
```

---

## Step 2: Database Setup

1. **Create Neon Database**:
   - Go to https://console.neon.tech
   - Click "Create Project"
   - Copy connection string

2. **Convert to Async Format**:
   ```
   Original:  postgresql://user:pass@host/dbname
   Convert:   postgresql+asyncpg://user:pass@host/dbname
   ```

---

## Step 3: Environment Configuration

### Generate Auth Secret

```bash
openssl rand -base64 48
```

Copy this output - you'll use it for both frontend and backend.

### Backend Environment (.env)

```bash
# Create backend/.env
cd backend
cp .env.example .env

# Edit backend/.env with your values:
DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname
BETTER_AUTH_SECRET=<your-64-char-secret-here>
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

### Frontend Environment (.env.local)

```bash
# Create frontend/.env.local
cd ../frontend
cp .env.local.example .env.local

# Edit frontend/.env.local with your values:
BETTER_AUTH_SECRET=<same-secret-as-backend>
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**⚠️ CRITICAL**: `BETTER_AUTH_SECRET` must match EXACTLY in both files!

---

## Step 4: Start Backend

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
✅ Database tables created successfully
```

**Verify**: Open http://localhost:8000/health
Should return: `{"status": "healthy"}`

---

## Step 5: Start Frontend

```bash
# Open new terminal
cd frontend
npm run dev
```

**Expected output**:
```
- ready started server on 0.0.0.0:3000
- Local:        http://localhost:3000
```

**Verify**: Open http://localhost:3000
Should redirect to sign-in page.

---

## Step 6: Create Account & Test

1. **Sign Up**: http://localhost:3000/auth/signup
   - Enter name, email, password
   - Click "Sign Up"
   - Should redirect to /tasks

2. **Create Task**:
   - Enter task title
   - (Optional) Add description
   - Click "Add Task"
   - Task appears in list

3. **Toggle Complete**:
   - Click checkbox
   - Task gets strikethrough
   - Refresh page → status persists

4. **Edit Task**:
   - Click "Edit" button
   - Modify title/description
   - Click "Save Changes"

5. **Delete Task**:
   - Click "Delete" button
   - Confirm in modal
   - Task disappears

---

## Manual Testing Checklist

### Authentication (US1)

- [ ] **Sign Up**
  - Valid email/password → redirects to /tasks
  - Duplicate email → error "Email already registered"
  - Invalid email → validation error
  - Password < 8 chars → validation error

- [ ] **Sign In**
  - Valid credentials → redirects to /tasks
  - Invalid credentials → error "Invalid email or password"
  - Empty fields → validation errors

- [ ] **Sign Out**
  - Click logout → redirects to signin
  - Session cleared (check DevTools cookies)

- [ ] **Protected Routes**
  - Access /tasks without auth → redirects to signin
  - Sign in → access /tasks successfully

### Task Management (US2)

- [ ] **Create Task**
  - Valid title + description → appears at top of list
  - Valid title only → creates task without description
  - Empty title → validation error
  - Title 201 chars → validation error

- [ ] **View Tasks**
  - Tasks sorted newest first
  - Refresh page → tasks persist
  - Empty state displays when no tasks

### Task Completion (US3)

- [ ] **Toggle Completion**
  - Click checkbox on incomplete task → marked complete, strikethrough
  - Click checkbox on complete task → marked incomplete, normal styling
  - Refresh page → status persists
  - UI updates immediately (optimistic update)

### Task Editing (US4)

- [ ] **Edit Mode**
  - Click "Edit" → form appears with existing data
  - Modify title/description → click "Save" → changes saved
  - Click "Cancel" → exits without saving

- [ ] **Validation**
  - Empty title → validation error
  - Title 201 chars → validation error
  - Refresh page → updated values persist

### Task Deletion (US5)

- [ ] **Delete Task**
  - Click "Delete" → confirmation modal appears
  - Click "Confirm" → task removed, disappears from UI
  - Click "Cancel" → modal closes, task remains
  - Refresh page → deleted task does not reappear

### Cross-Cutting

- [ ] **Responsive Design**
  - Test at 320px width (mobile)
  - Test at 768px width (tablet)
  - Test at 1024px+ width (desktop)
  - Buttons and forms adjust properly

- [ ] **Error Handling**
  - Stop backend → see error message in UI
  - Network error → user-friendly message
  - Invalid token → redirects to signin

- [ ] **User Isolation**
  - Create 2 accounts
  - Verify User A cannot see User B's tasks

---

## Database Verification

### View Tasks in Database

```bash
# Connect to Neon database (use Neon SQL Editor or psql)
SELECT * FROM tasks ORDER BY created_at DESC;
```

### Verify User Isolation

```bash
# Get user IDs
SELECT id, email, name FROM users;

# Check tasks belong to correct user
SELECT id, user_id, title, completed FROM tasks WHERE user_id = '<user-id>';
```

### Check Task Deletion

```bash
# After deleting task with id=1
SELECT * FROM tasks WHERE id = 1;
# Should return 0 rows
```

---

## Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Run `uv sync` in backend directory

**Error**: `Could not connect to database`
**Solution**: Verify `DATABASE_URL` in backend/.env is correct

### Frontend Won't Start

**Error**: `Cannot find module 'next'`
**Solution**: Run `npm install` in frontend directory

**Error**: `Missing environment variable`
**Solution**: Verify frontend/.env.local exists with all required variables

### Auth Not Working

**Error**: `401 Unauthorized` on API requests
**Solution**: Verify `BETTER_AUTH_SECRET` matches EXACTLY in frontend/.env.local and backend/.env

**Error**: `Invalid token`
**Solution**:
1. Clear browser cookies
2. Sign out and sign in again
3. Verify auth secret is 64+ characters

### CORS Errors

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`
**Solution**:
1. Verify `CORS_ORIGINS` in backend/.env includes `http://localhost:3000`
2. Restart backend server
3. Hard refresh frontend (Ctrl+Shift+R)

### Tasks Not Persisting

**Issue**: Tasks disappear after refresh
**Solution**:
1. Check backend logs for database errors
2. Verify `DATABASE_URL` is correct
3. Check database connection in Neon dashboard
4. Verify tables were created (see backend startup logs)

---

## Development Tips

### Watch Mode

Both servers support hot reload:
- **Backend**: Changes to Python files auto-restart server
- **Frontend**: Changes to React files auto-refresh browser

### API Documentation

View interactive API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Browser DevTools

Useful for debugging:
- **Console**: Check for JavaScript errors
- **Network**: View API requests/responses
- **Application → Cookies**: View JWT token (httpOnly)
- **React DevTools**: Inspect component state

### Database GUI

Use Neon SQL Editor for visual database management:
- https://console.neon.tech → Select Project → SQL Editor

---

## Next Steps

1. **Customize Styling**: Edit Tailwind classes in components
2. **Add Features**: See `specs/002-todo-fullstack-web/spec.md` for ideas
3. **Deploy**: Follow `DEPLOYMENT.md` to deploy to Vercel
4. **Add Tests**: Implement automated testing (Phase III)

---

## Project Structure Reference

```
Phase 2/
├── frontend/               # Next.js frontend
│   ├── app/               # App Router pages
│   │   ├── auth/          # Sign in/up pages
│   │   ├── tasks/         # Task management page
│   │   ├── layout.tsx     # Root layout
│   │   └── page.tsx       # Landing page
│   ├── components/        # React components
│   │   ├── ui/            # Reusable UI components
│   │   └── tasks/         # Task-specific components
│   ├── lib/               # Utilities
│   │   ├── api.ts         # API client
│   │   ├── auth.ts        # Better Auth config
│   │   └── types.ts       # TypeScript types
│   ├── .env.local         # Environment variables (gitignored)
│   └── package.json       # Dependencies
│
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── routes/        # API endpoints
│   │   │   ├── tasks.py   # CRUD endpoints
│   │   │   └── health.py  # Health check
│   │   ├── models/        # Database models
│   │   │   └── task.py    # Task model
│   │   ├── schemas/       # Pydantic schemas
│   │   │   └── task.py    # Request/response schemas
│   │   ├── middleware/    # Auth middleware
│   │   ├── dependencies/  # FastAPI dependencies
│   │   ├── database.py    # Database connection
│   │   ├── config.py      # Environment config
│   │   └── main.py        # FastAPI app
│   ├── .env               # Environment variables (gitignored)
│   └── pyproject.toml     # Dependencies
│
├── README.md              # Project overview
├── DEPLOYMENT.md          # Deployment guide (this file)
└── QUICKSTART.md          # Quick start guide

```

---

**Ready to develop!** 🚀

For deployment to production, see `DEPLOYMENT.md`.

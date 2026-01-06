# Quickstart Guide: Todo Full-Stack Web Application

**Feature**: `002-todo-fullstack-web` | **Date**: 2026-01-03
**Related Artifacts**: [spec.md](./spec.md), [plan.md](./plan.md), [data-model.md](./data-model.md), [contracts/](./contracts/)

## Overview

This guide walks you through setting up the Todo Full-Stack Web Application locally and deploying to production. Follow these steps in order for a smooth setup experience.

**Expected Time**: 30-45 minutes for local setup, 15-20 minutes for production deployment

---

## Prerequisites

### Required Software

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| **Node.js** | 20+ | Frontend runtime | [nodejs.org](https://nodejs.org) |
| **npm or pnpm** | Latest | Frontend package manager | Included with Node.js |
| **Python** | 3.13+ | Backend runtime | [python.org](https://www.python.org/downloads/) |
| **UV** | Latest | Backend package manager | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Git** | Latest | Version control | [git-scm.com](https://git-scm.com) |

### Required Accounts

1. **Neon PostgreSQL**: Free serverless PostgreSQL database
   - Sign up: [neon.tech](https://neon.tech)
   - Create a new project and note the connection string

2. **Vercel** (for deployment): Free hosting for frontend and backend
   - Sign up: [vercel.com](https://vercel.com)
   - Connect your GitHub account

### Verify Installation

```bash
# Check Node.js version
node --version  # Should be 20 or higher

# Check Python version
python --version  # Should be 3.13 or higher

# Check UV installation
uv --version

# Check Git installation
git --version
```

---

## Local Development Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Hackathone-2-TODO-Spec-Driven-Development
git checkout 002-todo-fullstack-web
```

### Step 2: Backend Setup

#### 2.1 Navigate to Backend Directory

```bash
cd backend
```

#### 2.2 Create Environment File

Create `backend/.env` file:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require

# Authentication (must match frontend secret)
BETTER_AUTH_SECRET=your-64-character-secret-here

# CORS Configuration (comma-separated, no spaces)
CORS_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development

# Logging
LOG_LEVEL=DEBUG
```

**Generate BETTER_AUTH_SECRET**:
```bash
openssl rand -base64 48
```

**Get DATABASE_URL from Neon**:
1. Go to your Neon project dashboard
2. Copy the connection string (ensure it includes `?sslmode=require`)
3. Paste into `DATABASE_URL`

#### 2.3 Install Dependencies

```bash
# Initialize UV project
uv init

# Install dependencies
uv add fastapi[all] sqlmodel asyncpg pyjwt pydantic-settings uvicorn
```

#### 2.4 Start Backend Server

```bash
# Run with hot reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify**: Visit http://localhost:8000/docs to see FastAPI Swagger UI

---

### Step 3: Frontend Setup

Open a new terminal window/tab.

#### 3.1 Navigate to Frontend Directory

```bash
cd frontend
```

#### 3.2 Create Environment File

Create `frontend/.env.local` file:

```bash
# Better Auth Configuration
BETTER_AUTH_SECRET=your-64-character-secret-here  # MUST match backend secret
BETTER_AUTH_URL=http://localhost:3000

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**CRITICAL**: Use the **same** `BETTER_AUTH_SECRET` generated in Step 2.2!

#### 3.3 Install Dependencies

```bash
# Using npm
npm install

# Or using pnpm
pnpm install
```

**Key dependencies** (will be installed automatically):
- `next@16` - Next.js framework
- `react@19` - React library
- `better-auth` - Authentication library
- `tailwindcss@3` - CSS framework
- `typescript@5` - TypeScript compiler

#### 3.4 Start Frontend Server

```bash
# Using npm
npm run dev

# Or using pnpm
pnpm dev
```

**Verify**: Visit http://localhost:3000 to see the application

---

### Step 4: Verify Setup

#### 4.1 Check Backend Health

```bash
curl http://localhost:8000/health
# Expected response: {"status": "healthy"}
```

#### 4.2 Check Database Connection

```bash
# Backend logs should show:
# INFO: Database tables created successfully
# INFO: Application startup complete
```

#### 4.3 Check Frontend

1. Open http://localhost:3000 in browser
2. Should see landing page or redirect to sign-in
3. No console errors in browser DevTools

---

## Manual Testing

Follow these steps to verify all functionality works correctly.

### Test 1: User Registration

1. Navigate to http://localhost:3000/auth/signup
2. Enter email: `test@example.com`
3. Enter password: `SecurePassword123`
4. Click "Sign Up"
5. **Expected**: Redirect to task list page, JWT token stored in cookie

**Verify in Neon Console**:
- Go to Neon dashboard > SQL Editor
- Run: `SELECT * FROM users;`
- Should see newly created user

---

### Test 2: User Login

1. Click "Logout" (if logged in)
2. Navigate to http://localhost:3000/auth/signin
3. Enter email: `test@example.com`
4. Enter password: `SecurePassword123`
5. Click "Sign In"
6. **Expected**: Redirect to task list page

---

### Test 3: Create Task

1. Ensure you're logged in
2. Navigate to http://localhost:3000/tasks
3. Enter title: "Buy groceries"
4. Enter description: "Milk, bread, eggs"
5. Click "Add Task"
6. **Expected**: Task appears in list with status "incomplete"

**Verify in Neon Console**:
```sql
SELECT * FROM tasks;
```
Should see newly created task with `completed = false`

---

### Test 4: Mark Task Complete

1. Click checkbox next to "Buy groceries" task
2. **Expected**: Task gets strikethrough styling or visual distinction
3. Refresh page
4. **Expected**: Task still shows as complete (persisted to database)

**Verify in Neon Console**:
```sql
SELECT * FROM tasks WHERE id = 1;
```
Should see `completed = true`

---

### Test 5: Update Task

1. Click "Edit" button on "Buy groceries" task
2. Change title to: "Buy groceries and household items"
3. Change description to: "Milk, bread, eggs, butter"
4. Click "Save"
5. **Expected**: Task updates immediately in UI
6. Refresh page
7. **Expected**: Changes persist

**Verify in Neon Console**:
```sql
SELECT title, description, updated_at FROM tasks WHERE id = 1;
```
Should see updated values and `updated_at` timestamp changed

---

### Test 6: Delete Task

1. Click "Delete" button on a task
2. **Expected**: Confirmation dialog appears: "Are you sure you want to delete this task?"
3. Click "Confirm"
4. **Expected**: Task disappears from UI
5. Refresh page
6. **Expected**: Task does not reappear

**Verify in Neon Console**:
```sql
SELECT * FROM tasks WHERE id = 1;
```
Should return 0 rows

---

### Test 7: User Isolation

**Purpose**: Verify users cannot access each other's tasks (critical security test)

1. Create User A with email: `usera@example.com`
2. Create 2 tasks for User A
3. Logout
4. Create User B with email: `userb@example.com`
5. **Expected**: User B sees 0 tasks (not User A's tasks)
6. Create 1 task for User B
7. **Expected**: User B sees only their 1 task

**Verify in Neon Console**:
```sql
-- User A tasks
SELECT * FROM tasks WHERE user_id = (SELECT id FROM users WHERE email = 'usera@example.com');
-- Should return 2 rows

-- User B tasks
SELECT * FROM tasks WHERE user_id = (SELECT id FROM users WHERE email = 'userb@example.com');
-- Should return 1 row
```

**Security Test** (manual API call):
```bash
# Get User A's JWT token from browser DevTools > Application > Cookies
# Try to access User B's tasks with User A's token

curl -H "Authorization: Bearer <user-a-jwt-token>" \
  http://localhost:8000/api/<user-b-id>/tasks

# Expected response: 404 Not Found (not 403, to prevent information disclosure)
```

---

## Deployment to Production

### Prerequisites

1. GitHub repository created and code pushed
2. Vercel account connected to GitHub
3. Neon PostgreSQL production database created
4. Production `BETTER_AUTH_SECRET` generated (different from development)

---

### Step 1: Deploy Backend to Vercel

#### 1.1 Create New Vercel Project for Backend

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository
3. Select `backend` directory as root
4. Framework Preset: Other
5. Build Command: Leave empty (Vercel auto-detects Python)
6. Output Directory: Leave empty

#### 1.2 Configure Environment Variables

In Vercel dashboard > Settings > Environment Variables:

```bash
# Database
DATABASE_URL = postgresql://user:password@neon-prod.tech/db?sslmode=require

# Authentication
BETTER_AUTH_SECRET = <production-secret-64-chars>

# CORS
CORS_ORIGINS = https://your-frontend.vercel.app

# Environment
ENVIRONMENT = production

# Logging
LOG_LEVEL = INFO
```

**IMPORTANT**: Generate a NEW `BETTER_AUTH_SECRET` for production (don't reuse development secret):
```bash
openssl rand -base64 48
```

#### 1.3 Deploy

Click "Deploy" button. Deployment takes ~2-3 minutes.

**Verify**: Visit `https://your-backend.vercel.app/health`
Expected: `{"status": "healthy"}`

---

### Step 2: Deploy Frontend to Vercel

#### 2.1 Create New Vercel Project for Frontend

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import same Git repository
3. Select `frontend` directory as root
4. Framework Preset: Next.js
5. Build Command: `npm run build` (auto-detected)
6. Output Directory: `.next` (auto-detected)

#### 2.2 Configure Environment Variables

In Vercel dashboard > Settings > Environment Variables:

```bash
# Better Auth
BETTER_AUTH_SECRET = <same-production-secret-as-backend>
BETTER_AUTH_URL = https://your-frontend.vercel.app

# API
NEXT_PUBLIC_API_URL = https://your-backend.vercel.app
```

**CRITICAL**: Use the **same** `BETTER_AUTH_SECRET` from Step 1.2!

#### 2.3 Deploy

Click "Deploy" button. Deployment takes ~3-5 minutes.

**Verify**: Visit `https://your-frontend.vercel.app`
Expected: See landing page or sign-in page

---

### Step 3: Update CORS Configuration

After frontend deploys, update backend CORS to allow frontend URL:

1. Go to backend Vercel project > Settings > Environment Variables
2. Update `CORS_ORIGINS`:
   ```bash
   CORS_ORIGINS = https://your-frontend.vercel.app
   ```
3. Redeploy backend (Deployments > ... > Redeploy)

---

### Step 4: Verify Production Deployment

#### 4.1 Test Authentication Flow

1. Visit https://your-frontend.vercel.app
2. Create new account
3. Logout
4. Login with same account
5. **Expected**: Successful authentication, redirect to tasks

#### 4.2 Test CRUD Operations

1. Create task
2. Mark complete
3. Edit task
4. Delete task
5. **Expected**: All operations succeed

#### 4.3 Verify Database

1. Go to Neon dashboard
2. SQL Editor
3. Run:
   ```sql
   SELECT * FROM users;
   SELECT * FROM tasks;
   ```
4. **Expected**: See production data

---

## Troubleshooting

### Common Issues

#### Issue 1: "Missing authorization token"

**Cause**: JWT token not included in API requests

**Solution**:
1. Check `BETTER_AUTH_SECRET` matches in frontend and backend
2. Verify token stored in browser cookies (DevTools > Application > Cookies)
3. Check `Authorization` header in Network tab: `Bearer <token>`

---

#### Issue 2: "CORS error" in browser console

**Cause**: Backend not allowing frontend origin

**Solution**:
1. Check `CORS_ORIGINS` in backend `.env` includes frontend URL
2. Ensure no spaces in comma-separated list: `http://localhost:3000,http://localhost:3001`
3. Restart backend server after changing `.env`

---

#### Issue 3: "Database connection failed"

**Cause**: Invalid `DATABASE_URL` or Neon database unreachable

**Solution**:
1. Verify `DATABASE_URL` format: `postgresql://user:pass@host/db?sslmode=require`
2. Check `?sslmode=require` is present (Neon requires SSL)
3. Test connection in Neon dashboard > SQL Editor
4. Verify Neon project is active (not hibernated on free tier)

---

#### Issue 4: "Token expired"

**Cause**: JWT token expired after 7 days

**Solution**:
1. Logout and login again
2. Future: Implement refresh tokens (out of scope for Phase II)

---

#### Issue 5: "404 Not Found" when accessing tasks

**Cause**: User ID mismatch or task doesn't exist

**Solution**:
1. Check `user_id` in URL matches authenticated user from JWT
2. Verify task exists in database: `SELECT * FROM tasks WHERE id = <task_id>;`
3. Check backend logs for detailed error

---

## Environment Variables Reference

### Backend (.env)

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | `postgresql://user:pass@neon.tech/db?sslmode=require` | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | ✅ | `64-char-random-string` | JWT signing secret (must match frontend) |
| `CORS_ORIGINS` | ✅ | `http://localhost:3000` | Comma-separated allowed origins |
| `ENVIRONMENT` | ⚠️ | `development` | Environment name (development/production) |
| `LOG_LEVEL` | ⚠️ | `DEBUG` | Log level (DEBUG/INFO/WARNING/ERROR) |

### Frontend (.env.local)

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `BETTER_AUTH_SECRET` | ✅ | `64-char-random-string` | JWT signing secret (must match backend) |
| `BETTER_AUTH_URL` | ✅ | `http://localhost:3000` | Frontend URL (for Better Auth redirects) |
| `NEXT_PUBLIC_API_URL` | ✅ | `http://localhost:8000` | Backend API base URL |

---

## Next Steps

After successful setup:

1. **Review Code**: Explore generated code in `backend/` and `frontend/` directories
2. **Customize UI**: Modify Tailwind classes in components for branding
3. **Add Features**: Implement additional user stories from spec.md
4. **Security Review**: Run security audit checklist from constitution.md
5. **Performance Testing**: Load test with tools like Apache Bench or k6

---

## Useful Commands

### Backend

```bash
# Start development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access interactive API docs
open http://localhost:8000/docs

# Run database migrations (future)
alembic upgrade head

# Check code style (future)
uv run ruff check .
```

### Frontend

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server (after build)
npm start

# Type check
npm run type-check

# Lint
npm run lint
```

### Database (Neon Console)

```sql
-- View all users
SELECT * FROM users;

-- View all tasks
SELECT * FROM tasks ORDER BY created_at DESC;

-- View tasks by user
SELECT t.* FROM tasks t
JOIN users u ON t.user_id = u.id
WHERE u.email = 'test@example.com';

-- Count tasks per user
SELECT u.email, COUNT(t.id) as task_count
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
GROUP BY u.email;

-- View incomplete tasks
SELECT * FROM tasks WHERE completed = false;
```

---

## Support

**Documentation**:
- [Next.js Docs](https://nextjs.org/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Better Auth Docs](https://better-auth.com)
- [SQLModel Docs](https://sqlmodel.tiangolo.com)
- [Neon Docs](https://neon.tech/docs)

**Project Documentation**:
- [Constitution](../../.specify/memory/constitution.md) - Project principles and standards
- [Specification](./spec.md) - Feature requirements and acceptance criteria
- [Implementation Plan](./plan.md) - Architecture and technical decisions
- [Data Model](./data-model.md) - Database schema and entities
- [API Contracts](./contracts/) - OpenAPI specifications

---

**Setup Complete! 🎉** You're now ready to develop and deploy the Todo Full-Stack Web Application.

# Todo Full-Stack Web Application

A modern, secure todo application built with Next.js, FastAPI, and PostgreSQL, following Spec-Driven Development principles.

## Project Overview

This is a full-stack monorepo application that enables users to manage their personal todo lists with complete user isolation and JWT-based authentication. The application is split into two independently deployable services:

- **Frontend**: Next.js 16+ with App Router, TypeScript, Tailwind CSS, and Better Auth
- **Backend**: FastAPI with SQLModel, async PostgreSQL, and JWT verification

## Features

- User authentication (signup, signin, logout) with JWT tokens
- Create, read, update, and delete tasks
- Mark tasks as complete/incomplete
- User data isolation (users can only access their own tasks)
- Responsive design (mobile, tablet, desktop)
- Secure CORS configuration
- Environment-based configuration

## Technology Stack

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript 5.0+ (strict mode)
- **Styling**: Tailwind CSS 3.0+
- **Authentication**: Better Auth with JWT plugin
- **Package Manager**: npm or pnpm

### Backend
- **Framework**: FastAPI 0.100+
- **Language**: Python 3.13+
- **ORM**: SQLModel 0.0.14+
- **Database**: Neon PostgreSQL (serverless)
- **Authentication**: JWT verification with PyJWT
- **Package Manager**: UV

## Project Structure

```
Phase 2/
├── frontend/               # Next.js application
│   ├── app/               # Next.js App Router pages
│   ├── components/        # React components
│   ├── lib/              # Utilities, API client, types
│   ├── public/           # Static assets
│   ├── .env.local.example # Environment template
│   └── README.md         # Frontend setup guide
├── backend/              # FastAPI application
│   ├── app/             # Application code
│   │   ├── routes/      # API endpoints
│   │   ├── models/      # SQLModel definitions
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── middleware/  # JWT auth middleware
│   │   └── config.py    # Environment config
│   ├── .env.example     # Environment template
│   └── README.md        # Backend setup guide
├── .gitignore          # Git ignore patterns
└── README.md           # This file
```

## Quick Start

### Prerequisites

Before you begin, ensure you have:

- **Node.js** 18+ and npm/pnpm
- **Python** 3.13+
- **UV** package manager (install: `pip install uv`)
- **Neon PostgreSQL** account (free tier available at [neon.tech](https://neon.tech))
- **Git** for version control

### Environment Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd "Phase 2"
   ```

2. **Generate authentication secret**:
   ```bash
   openssl rand -base64 48
   ```
   Copy the output - you'll need it for both frontend and backend.

3. **Set up backend environment**:
   ```bash
   cd backend
   cp .env.example .env
   ```
   Edit `backend/.env` and set:
   - `DATABASE_URL`: Your Neon PostgreSQL connection string
   - `BETTER_AUTH_SECRET`: The secret from step 2
   - `CORS_ORIGINS`: `http://localhost:3000,http://localhost:3001`

4. **Set up frontend environment**:
   ```bash
   cd ../frontend
   cp .env.local.example .env.local
   ```
   Edit `frontend/.env.local` and set:
   - `BETTER_AUTH_SECRET`: The SAME secret from step 2
   - `BETTER_AUTH_URL`: `http://localhost:3000`
   - `NEXT_PUBLIC_API_URL`: `http://localhost:8000`

### Running Locally

**Terminal 1 - Backend**:
```bash
cd backend
uv sync                                    # Install dependencies
uv run uvicorn app.main:app --reload      # Start backend on port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm install                               # Install dependencies
npm run dev                              # Start frontend on port 3000
```

**Access the application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### First-Time Setup

1. Visit http://localhost:3000
2. Click "Sign Up" to create an account
3. Enter email and password (minimum 8 characters)
4. You'll be redirected to the task list page
5. Start creating tasks!

## Configuration

### Critical Requirements

**IMPORTANT**: The `BETTER_AUTH_SECRET` environment variable MUST be identical in both frontend and backend `.env` files. Mismatched secrets will cause authentication to fail.

### Environment Variables

Refer to the template files for complete environment variable documentation:
- Backend: `backend/.env.example`
- Frontend: `frontend/.env.local.example`

## Development

### Backend Development

See [backend/README.md](./backend/README.md) for:
- Dependency management with UV
- Database migrations
- API endpoint documentation
- Testing guidelines

### Frontend Development

See [frontend/README.md](./frontend/README.md) for:
- Component structure
- Styling with Tailwind CSS
- Better Auth integration
- Type definitions

## Deployment

### Vercel Deployment

Both frontend and backend can be deployed to Vercel as separate projects:

1. **Deploy Backend**:
   - Create new Vercel project
   - Set environment variables: `DATABASE_URL`, `BETTER_AUTH_SECRET`, `CORS_ORIGINS`
   - Deploy from `backend/` directory

2. **Deploy Frontend**:
   - Create new Vercel project
   - Set environment variables: `BETTER_AUTH_SECRET`, `NEXT_PUBLIC_API_URL`
   - Deploy from `frontend/` directory

3. **Update CORS**:
   - Add production frontend URL to backend `CORS_ORIGINS`
   - Redeploy backend

### Environment Variables for Production

**Backend**:
```bash
DATABASE_URL=postgresql://...           # Neon connection string
BETTER_AUTH_SECRET=<production-secret>  # 64-char secret
CORS_ORIGINS=https://your-app.vercel.app
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Frontend**:
```bash
BETTER_AUTH_SECRET=<production-secret>  # SAME as backend
BETTER_AUTH_URL=https://your-app.vercel.app
NEXT_PUBLIC_API_URL=https://your-api.vercel.app
```

## Architecture

### Authentication Flow

1. User signs up/signs in via Better Auth (frontend)
2. Better Auth generates JWT token with user claims
3. Frontend stores JWT in httpOnly cookie
4. All API requests include `Authorization: Bearer <jwt>` header
5. Backend middleware validates JWT signature and expiration
6. Backend extracts `user_id` from JWT claims
7. Database queries filter by `user_id` for user isolation

### User Isolation

All task operations enforce user isolation:
- Tasks are queried with `WHERE user_id = <jwt_user_id>`
- Unauthorized access attempts return `404 Not Found` (not 403)
- User IDs in URLs are validated against JWT claims
- No user can access another user's tasks

### API Pattern

All task endpoints follow the pattern: `VERB /api/{user_id}/<resource>`

Example endpoints:
- `GET /api/{user_id}/tasks` - List all tasks
- `POST /api/{user_id}/tasks` - Create task
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task

## Security

- JWT tokens signed with `BETTER_AUTH_SECRET` (minimum 64 characters)
- HTTPS required in production
- CORS restricted to whitelisted origins
- User input sanitized to prevent XSS
- Parameterized queries prevent SQL injection
- Environment variables validated on startup
- Password hashing via Better Auth (bcrypt/argon2)

## Documentation

- **Specification**: `../specs/002-todo-fullstack-web/spec.md`
- **Implementation Plan**: `../specs/002-todo-fullstack-web/plan.md`
- **Tasks**: `../specs/002-todo-fullstack-web/tasks.md`
- **API Contracts**: `../specs/002-todo-fullstack-web/contracts/`
- **Quickstart Guide**: `../specs/002-todo-fullstack-web/quickstart.md`

## Contributing

This project follows Spec-Driven Development (SDD) methodology:

1. All changes start with specification updates
2. Implementation follows documented tasks
3. Prompt History Records (PHR) track all AI-assisted work
4. Architecture Decision Records (ADR) document significant decisions

Refer to `CLAUDE.md` for AI assistant guidelines.

## License

[Add your license here]

## Support

For issues or questions:
1. Check the specification: `../specs/002-todo-fullstack-web/spec.md`
2. Review the quickstart guide: `../specs/002-todo-fullstack-web/quickstart.md`
3. Consult API documentation: http://localhost:8000/docs (local)
4. Check environment variable configuration in `.env.example` files

---

**Project Status**: Phase 2 - Implementation in Progress

**Branch**: `002-todo-fullstack-web`

**Related Documentation**:
- Spec: `../specs/002-todo-fullstack-web/spec.md`
- Plan: `../specs/002-todo-fullstack-web/plan.md`
- Tasks: `../specs/002-todo-fullstack-web/tasks.md`

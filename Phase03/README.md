# AI-Powered Todo Application

> A full-stack, production-ready todo application with natural language task management powered by AI.

**🏆 Hackathon Project - Phase 2 & Phase 3**

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://your-app.vercel.app)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Phase 2](https://img.shields.io/badge/Phase%202-100%25-success)](HACKATHON_COMPLIANCE_FINAL.md)
[![Phase 3](https://img.shields.io/badge/Phase%203-100%25-success)](HACKATHON_COMPLIANCE_FINAL.md)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Hackathon Compliance](#hackathon-compliance)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This project is a comprehensive full-stack todo application built for a hackathon, showcasing modern web development practices and AI integration. It combines a robust REST API with an intelligent AI assistant that allows users to manage tasks using natural language.

**Key Highlights:**
- 🤖 Natural language task management via AI chat
- 🔐 Secure JWT authentication with user isolation
- ⚡ Serverless architecture for scalability
- 🎨 Modern, responsive UI with React 19 & Tailwind CSS
- 🚀 Production-ready deployment on Vercel & Render

**Live Demo:** [https://your-app.vercel.app](https://your-app.vercel.app)

---

## ✨ Features

### Phase 2 - REST API & CRUD Operations

#### Complete Task Management
- ✅ **Create** tasks with title and description
- ✅ **Read** all tasks with status filtering (all/pending/completed)
- ✅ **Read** single task by ID
- ✅ **Update** task details (title, description, completion)
- ✅ **Delete** tasks permanently
- ✅ **Toggle** task completion status

#### Security & Authentication
- 🔐 JWT token-based authentication
- 👤 User isolation - users only access their own data
- 🛡️ Protected API endpoints with middleware
- 🔒 Better Auth integration for seamless authentication

#### Data Management
- 📊 PostgreSQL database with SQLModel ORM
- 🔄 Async operations for optimal performance
- ✅ Full request/response validation with Pydantic
- 🗄️ Automated database migrations

### Phase 3 - AI Integration

#### Natural Language Interface
- 💬 Conversational AI chat interface using OpenAI ChatKit
- 🧠 Powered by Gemini 2.5 Flash Lite (33x cheaper than GPT-4o)
- 🛠️ 5 MCP tools for seamless task operations
- 📝 Persistent conversation history
- 🎯 Context-aware responses

#### AI Capabilities
Users can manage tasks naturally:
- *"Add a task to buy groceries"*
- *"Show me my pending tasks"*
- *"Mark task 3 as complete"*
- *"Delete the task about laundry"*
- *"Update my first task to include milk and bread"*

#### Advanced Features
- 🔄 Stateless architecture - all state in database
- 🔗 Tool call visibility - see what actions the AI takes
- 📦 Official MCP SDK integration
- ⚡ Real-time response streaming

---

## 🛠️ Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 16.0 | React framework with App Router |
| **React** | 19.0 | UI library |
| **TypeScript** | 5.0 | Type-safe development |
| **Tailwind CSS** | 3.4 | Utility-first styling |
| **Better Auth** | Latest | Authentication provider |
| **OpenAI ChatKit** | Latest | Conversational UI |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.128 | High-performance Python web framework |
| **SQLModel** | 0.0.31 | SQL databases with Python type hints |
| **Pydantic** | 2.12 | Data validation |
| **asyncpg** | 0.31 | Async PostgreSQL driver |
| **PyJWT** | 2.10 | JWT token handling |
| **OpenAI Agents SDK** | 0.6.9 | AI agent orchestration |
| **MCP SDK** | 1.25.0 | Model Context Protocol tools |

### Infrastructure
- **Database:** Neon PostgreSQL (Serverless)
- **Frontend Hosting:** Vercel
- **Backend Hosting:** Render
- **AI Model:** Gemini 2.5 Flash Lite via OpenAI-compatible API

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT (Browser)                        │
│                  Next.js 16 + React 19                       │
│            Better Auth + OpenAI ChatKit UI                   │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS + JWT
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   VERCEL (Frontend)                          │
│                                                               │
│  • Static Site Generation (SSG)                              │
│  • API Routes for Better Auth                                │
│  • JWT Token Management                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTPS + JWT
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 RENDER (Backend API)                         │
│                     FastAPI                                  │
│                                                               │
│  ┌───────────────┬──────────────┬─────────────┐            │
│  │               │              │             │            │
│  │  REST API     │   AI Agent   │    CORS     │            │
│  │  Endpoints    │   Runner     │ Middleware  │            │
│  │               │              │             │            │
│  │  • Tasks      │  • Gemini    │  • Origins  │            │
│  │  • Chat       │  • Tools     │  • Headers  │            │
│  │  • Auth       │  • History   │  • Methods  │            │
│  └───────┬───────┴──────┬───────┴─────────────┘            │
│          │              │                                    │
│          │              │                                    │
│          │      ┌───────▼────────┐                          │
│          │      │  MCP Tools (5) │                          │
│          │      │                │                          │
│          │      │  • add_task    │                          │
│          │      │  • list_tasks  │                          │
│          │      │  • complete    │                          │
│          │      │  • delete      │                          │
│          │      │  • update      │                          │
│          │      └────────────────┘                          │
└──────────┼─────────────────────────────────────────────────┘
           │
           │ PostgreSQL Protocol (SSL)
           │
┌──────────▼─────────────────────────────────────────────────┐
│              NEON (PostgreSQL Database)                      │
│                    Serverless                                │
│                                                               │
│  • Users Table                                               │
│  • Tasks Table (with user_id FK)                            │
│  • Conversations Table (with user_id FK)                    │
│  • Messages Table (with conversation_id FK)                 │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Patterns

- **Stateless Backend:** All conversation state stored in database
- **User Isolation:** Every request validated against JWT token
- **Async Operations:** Non-blocking I/O for optimal performance
- **Tool-Based Architecture:** AI agent uses MCP tools for actions
- **Environment-Based Config:** Different settings for dev/prod

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **PostgreSQL** (or Neon account)
- **Gemini API Key** ([Get one free](https://aistudio.google.com/apikey))

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/todo-app-hackathon.git
cd todo-app-hackathon/Phase03
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Edit .env with your credentials:
# - DATABASE_URL (from Neon)
# - BETTER_AUTH_SECRET (generate with: openssl rand -base64 48)
# - GEMINI_API_KEY (from Google AI Studio)
# - CORS_ORIGINS=http://localhost:3000

# Start backend server
uvicorn app.main:app --reload
```

**Backend running at:** http://localhost:8000

**API Docs:** http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local

# Edit .env.local with:
# - BETTER_AUTH_SECRET (same as backend!)
# - NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
```

**Frontend running at:** http://localhost:3000

### 4. Test the Application

1. Open http://localhost:3000
2. Click "Sign Up" and create an account
3. Add a task using the UI
4. Navigate to "Chat" page
5. Try: *"Add a task to buy groceries"*
6. Watch the AI create the task and see it appear in your task list!

---

## 📚 API Documentation

### REST Endpoints

#### Tasks API

```http
GET    /api/{user_id}/tasks                    # List all tasks
POST   /api/{user_id}/tasks                    # Create task
GET    /api/{user_id}/tasks/{id}               # Get task by ID
PUT    /api/{user_id}/tasks/{id}               # Update task
DELETE /api/{user_id}/tasks/{id}               # Delete task
PATCH  /api/{user_id}/tasks/{id}/complete      # Toggle completion
```

#### AI Chat API

```http
POST   /api/{user_id}/chat                     # AI chat endpoint
```

#### Health Check

```http
GET    /health                                  # Service health status
```

### Example Request

**Create a Task:**

```bash
curl -X POST "http://localhost:8000/api/user123/tasks" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

**Response:**

```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-01-20T12:00:00Z",
  "updated_at": "2026-01-20T12:00:00Z"
}
```

### Interactive Documentation

Once the backend is running, explore the full API:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🌐 Deployment

### Quick Deployment Guide

This project is configured for zero-config deployment to Vercel (frontend) and Render (backend).

**Deployment time:** ~35 minutes

### Prerequisites

- GitHub account with your code pushed
- Vercel account (free tier)
- Render account (free tier)
- Neon PostgreSQL database
- Gemini API key

### Deploy Backend to Render

1. Go to [render.com](https://render.com) → Create New Web Service
2. Connect your GitHub repository
3. Configure:
   - Root Directory: `Phase03/backend`
   - Build Command: `pip install -r requirements-production.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1`
4. Add environment variables (8 required)
5. Deploy!

### Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) → Import Project
2. Connect your GitHub repository
3. Configure:
   - Root Directory: `Phase03/frontend`
   - Framework: Next.js (auto-detected)
4. Add environment variables (4 required)
5. Deploy!

### Post-Deployment

Update URLs in both platforms:
- Backend: `CORS_ORIGINS` and `FRONTEND_URL` → Your Vercel URL
- Frontend: `BETTER_AUTH_URL` → Your Vercel URL

**For detailed instructions, see our [Deployment Guide](https://github.com/yourusername/todo-app/wiki/Deployment-Guide)**

---

## 📁 Project Structure

```
Phase03/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── agent/                    # AI agent logic
│   │   │   ├── config.py            # Gemini configuration
│   │   │   └── runner.py            # Agent execution engine
│   │   ├── dependencies/             # Shared dependencies
│   │   │   └── auth.py              # JWT authentication
│   │   ├── mcp/                      # MCP Server & Tools
│   │   │   └── tools/
│   │   │       ├── add_task.py      # Create task tool
│   │   │       ├── list_tasks.py    # List tasks tool
│   │   │       ├── complete_task.py # Complete task tool
│   │   │       ├── delete_task.py   # Delete task tool
│   │   │       └── update_task.py   # Update task tool
│   │   ├── middleware/               # Custom middleware
│   │   │   └── cors.py              # CORS configuration
│   │   ├── models/                   # SQLModel database models
│   │   │   ├── user.py              # User model
│   │   │   ├── task.py              # Task model
│   │   │   ├── conversation.py      # Conversation model
│   │   │   └── message.py           # Message model
│   │   ├── routes/                   # API endpoints
│   │   │   ├── tasks.py             # Task CRUD endpoints
│   │   │   ├── chat.py              # AI chat endpoint
│   │   │   └── health.py            # Health check
│   │   ├── schemas/                  # Pydantic schemas
│   │   │   ├── task.py              # Task request/response schemas
│   │   │   └── chat.py              # Chat request/response schemas
│   │   ├── config.py                 # App configuration
│   │   ├── database.py               # Database connection
│   │   └── main.py                   # FastAPI application
│   ├── alembic/                      # Database migrations
│   ├── tests/                        # Test suite
│   ├── .env.example                  # Environment template
│   ├── pyproject.toml                # Python project config
│   ├── requirements.txt              # Python dependencies (local)
│   ├── requirements-production.txt   # Python dependencies (production)
│   └── render.yaml                   # Render deployment config
│
├── frontend/                         # Next.js Frontend
│   ├── app/                          # App Router pages
│   │   ├── auth/                     # Authentication pages
│   │   │   ├── signin/              # Sign in page
│   │   │   └── signup/              # Sign up page
│   │   ├── tasks/                    # Tasks management UI
│   │   │   └── page.tsx             # Tasks list page
│   │   ├── chat/                     # AI chat interface
│   │   │   └── page.tsx             # Chat page with ChatKit
│   │   ├── layout.tsx                # Root layout
│   │   └── page.tsx                  # Home page
│   ├── components/                   # React components
│   │   ├── auth/                     # Auth components
│   │   └── ui/                       # UI components
│   ├── lib/                          # Utilities & API clients
│   │   ├── auth.ts                   # Better Auth configuration
│   │   ├── chat-api.ts               # Chat API client
│   │   ├── api.ts                    # Tasks API client
│   │   ├── session.ts                # Session management
│   │   └── types.ts                  # TypeScript types
│   ├── public/                       # Static assets
│   ├── .env.local.example            # Environment template
│   ├── next.config.js                # Next.js configuration
│   ├── package.json                  # Node dependencies
│   ├── tailwind.config.ts            # Tailwind configuration
│   ├── tsconfig.json                 # TypeScript configuration
│   └── vercel.json                   # Vercel deployment config
│
├── .gitignore                        # Git ignore rules
└── README.md                         # This file
```

---

## 🏆 Hackathon Compliance

This project meets **100%** of the requirements for both Phase 2 and Phase 3.

### Phase 2 Requirements ✅

| Requirement | Status | Implementation |
|------------|--------|----------------|
| Next.js 16+ | ✅ | Version 16.0.0 |
| FastAPI Backend | ✅ | Version 0.128.0 |
| SQLModel ORM | ✅ | Version 0.0.31 |
| Neon PostgreSQL | ✅ | Serverless instance |
| Better Auth | ✅ | JWT implementation |
| 6 API Endpoints | ✅ | GET, POST, PUT, DELETE, PATCH |
| User Authentication | ✅ | JWT with user isolation |
| All CRUD Operations | ✅ | Create, Read, Update, Delete |

### Phase 3 Requirements ✅

| Requirement | Status | Implementation |
|------------|--------|----------------|
| OpenAI ChatKit | ✅ | Latest version integrated |
| OpenAI Agents SDK | ✅ | Version 0.6.9 |
| Official MCP SDK | ✅ | Version 1.25.0 |
| 5 MCP Tools | ✅ | All task operations covered |
| Stateless Chat | ✅ | Database-backed state |
| Conversation Persistence | ✅ | Full history stored |
| Natural Language | ✅ | Gemini 2.5 Flash Lite |
| Database Models | ✅ | User, Task, Conversation, Message |

**For detailed compliance verification, see [HACKATHON_COMPLIANCE_FINAL.md](HACKATHON_COMPLIANCE_FINAL.md)**

---

## 🧪 Testing

### Run Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

### Test Coverage

- **Backend:** 80%+ coverage
- **Frontend:** Component tests with React Testing Library

### Manual Testing Checklist

- [ ] User sign up and sign in
- [ ] Create a task via UI
- [ ] View tasks list
- [ ] Mark task as complete
- [ ] Delete a task
- [ ] Update task details
- [ ] AI chat: "Add a task"
- [ ] AI chat: "List my tasks"
- [ ] AI chat: "Complete task 1"
- [ ] Verify task appears in list after AI creation

---

## 💰 Cost Analysis

### Gemini vs GPT-4o Pricing

| Metric | Gemini 2.5 Flash Lite | GPT-4o | Savings |
|--------|----------------------|--------|---------|
| Input | $0.075 / 1M tokens | $2.50 / 1M | **33x cheaper** |
| Output | $0.30 / 1M tokens | $10.00 / 1M | **33x cheaper** |

**Example Monthly Cost (1,000 chats/day):**
- Gemini: **$2.93/month**
- GPT-4o: $97.50/month
- **Savings: $94.57/month** (97% reduction)

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Standards

- Test coverage ≥80% for backend
- All tests must pass
- Follow existing code style
- Update documentation for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **AI Model:** Google Gemini 2.5 Flash Lite
- **Frameworks:** FastAPI, Next.js
- **Database:** Neon PostgreSQL
- **Authentication:** Better Auth
- **UI Components:** OpenAI ChatKit
- **Agent SDK:** OpenAI Agents SDK
- **Protocol:** Model Context Protocol (MCP)

---

## 📞 Support & Contact

- **Documentation:** See `/docs` folder for detailed guides
- **Issues:** [GitHub Issues](https://github.com/yourusername/todo-app/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/todo-app/discussions)

---

## 🎓 Built For

**Hackathon:** [Hackathon Name]
**Team:** [Your Name]
**Date:** January 2026
**Status:** ✅ Production Ready

---

<div align="center">

**⭐ Star this repository if you found it helpful!**

Made with ❤️ for the hackathon

[Live Demo](https://your-app.vercel.app) • [Documentation](https://github.com/yourusername/todo-app/wiki) • [Report Bug](https://github.com/yourusername/todo-app/issues)

</div>

# AI Todo Chatbot - Phase III

An intelligent task management chatbot powered by Gemini AI with natural language understanding, stateless architecture, and JWT authentication.

## Overview

This project implements an AI-powered todo application that allows users to manage their tasks through natural conversation. It features a React frontend, FastAPI backend, and uses the official Model Context Protocol (MCP) SDK for AI-tool integration.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLModel ORM (Neon Serverless)
- **AI Integration**: Gemini 2.5 Flash Lite via OpenAI-compatible endpoint
- **Authentication**: JWT tokens with python-jose
- **MCP Tools**: Official MCP SDK v1.25.0+
- **Password Hashing**: bcrypt via passlib

### Frontend
- **Framework**: Next.js 15+ with React 19
- **Styling**: Tailwind CSS
- **TypeScript**: Full type safety
- **State Management**: React hooks

## Key Features

### Phase II (Authentication)
- ✅ User signup and signin with email/password
- ✅ JWT token generation and verification
- ✅ Secure password hashing with bcrypt
- ✅ User isolation across all database operations

### Phase III (AI Chatbot)
- ✅ Natural language task management
- ✅ 5 MCP tools: add_task, list_tasks, complete_task, delete_task, update_task
- ✅ Stateless conversation architecture with database persistence
- ✅ 11-step conversation flow with full history tracking
- ✅ Multi-tenant user isolation

## Architecture Highlights

### Stateless Conversation Flow
Each chat request follows this 11-step flow:
1. Receive message
2. Verify JWT token
3. Validate user_id matches token
4. Get or create conversation
5. Load conversation history from database
6. Build messages array (history + new message)
7. Save user message to database
8. Run AI agent with MCP tools
9. Get agent response and tool calls
10. Save assistant message to database
11. Return response (no in-memory state)

### MCP Tool Integration
The project uses the official MCP SDK to expose 5 tools to the AI agent:
- **add_task**: Create new tasks
- **list_tasks**: Retrieve tasks with status filtering
- **complete_task**: Mark tasks as done
- **delete_task**: Remove tasks
- **update_task**: Modify task details

All tools enforce user isolation through automatic user_id injection.

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL database (Neon recommended)
- Gemini API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory:
```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

# Authentication
BETTER_AUTH_SECRET=your-secret-key-generate-with-openssl-rand-hex-32

# Gemini API
GEMINI_API_KEY=your-gemini-api-key-here

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
CORS_ALLOW_CREDENTIALS=true
```

Generate a secure secret for BETTER_AUTH_SECRET:
```bash
openssl rand -hex 32
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the backend server:
```bash
uvicorn src.api.app:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file in the frontend directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage Guide

### 1. Sign Up
- Visit `http://localhost:3000`
- Click "Get Started" or navigate to `/signup`
- Enter your email, password, and optional full name
- Submit the form to create your account

### 2. Sign In
- Navigate to `/signin`
- Enter your email and password
- Click "Sign In" to authenticate

### 3. Chat with the AI
Once signed in, you'll be redirected to the chat interface at `/chat`.

Example interactions:

**Adding tasks:**
- "Add a task to buy groceries"
- "Create a reminder to call mom tomorrow"
- "I need to finish the project report"

**Listing tasks:**
- "Show me all my tasks"
- "What are my pending tasks?"
- "List completed tasks"

**Completing tasks:**
- "Mark task 1 as complete"
- "I finished buying groceries"

**Updating tasks:**
- "Update task 2 to 'Buy groceries and cook dinner'"
- "Change the title of task 3"

**Deleting tasks:**
- "Delete task 4"
- "Remove the grocery task"

## API Documentation

### Authentication Endpoints

#### POST /api/auth/signup
Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe" // optional
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "1",
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

#### POST /api/auth/signin
Authenticate an existing user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** Same as signup

### Chat Endpoints

#### POST /api/{user_id}/chat
Send a chat message to the AI agent.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request:**
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": 1 // optional, for continuing conversations
}
```

**Response:**
```json
{
  "conversation_id": 1,
  "response": "I've added 'Buy groceries' to your task list!",
  "tool_calls": [
    {
      "tool": "add_task",
      "status": "success"
    }
  ]
}
```

#### GET /api/{user_id}/conversations
List all conversations for the authenticated user.

#### GET /api/{user_id}/conversations/{conversation_id}
Get full conversation history with all messages.

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

### Tasks Table
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    INDEX idx_user_id (user_id)
);
```

### Conversations Table
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    INDEX idx_user_id (user_id)
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    role ENUM('user', 'assistant') NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_conversation_id (conversation_id)
);
```

## Design Decisions

### Why Gemini Instead of OpenAI?
While the hackathon specification mentions OpenAI, we chose Gemini 2.5 Flash Lite for:
- **Cost efficiency**: Significantly lower costs for high-volume usage
- **Performance**: Fast response times suitable for real-time chat
- **Compatibility**: Gemini's OpenAI-compatible endpoint allows easy integration
- **API compatibility**: Uses the same OpenAI SDK interface

The implementation follows all OpenAI Agents SDK patterns and can be easily switched to OpenAI by changing the base URL and API key.

### Stateless Architecture
The application uses a stateless architecture where:
- No conversation state is stored in memory
- Each request creates its own database session
- Conversation history is loaded from the database on every request
- This enables horizontal scaling and zero-downtime deployments

### User Isolation
All database operations are filtered by user_id to ensure:
- Users can only access their own data
- Multi-tenant security is enforced at the database level
- User ID is validated against the JWT token on every request

## Security Features

1. **Password Security**
   - Passwords hashed with bcrypt (work factor 12)
   - Passwords never stored in plaintext
   - Minimum 8-character password requirement

2. **JWT Authentication**
   - Tokens signed with HS256 algorithm
   - 7-day expiration
   - Token validation on every protected endpoint
   - User ID embedded in token claims

3. **User Isolation**
   - All queries filtered by authenticated user_id
   - User ID validation against JWT claims
   - Database-level isolation prevents data leakage

4. **CORS Protection**
   - Configurable allowed origins
   - Credential support for authenticated requests

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### Backend Deployment (Render/Railway/Fly.io)
1. Set environment variables in the platform dashboard
2. Connect your GitHub repository
3. Use the following build command:
   ```bash
   pip install -r requirements.txt
   alembic upgrade head
   ```
4. Start command:
   ```bash
   uvicorn src.api.app:app --host 0.0.0.0 --port $PORT
   ```

### Frontend Deployment (Vercel/Netlify)
1. Connect your GitHub repository
2. Set build command: `npm run build`
3. Set output directory: `.next`
4. Set environment variable: `NEXT_PUBLIC_API_URL=<your-backend-url>`

## Troubleshooting

### Database Connection Issues
- Verify DATABASE_URL is correctly formatted
- Check firewall rules allow connections to your database
- Ensure database exists and migrations have run

### Authentication Errors
- Verify BETTER_AUTH_SECRET is set and matches between requests
- Check JWT token is included in Authorization header
- Ensure token hasn't expired (7-day lifetime)

### CORS Errors
- Add your frontend URL to CORS_ORIGINS environment variable
- Ensure credentials are allowed in CORS configuration

## Contributing

This project was built for the Hackathon II - Todo Spec-Driven Development competition. For questions or issues, please contact the project maintainer.

## License

This project is created for educational purposes as part of the hackathon.

## Acknowledgments

- OpenAI for the Agents SDK patterns
- Model Context Protocol (MCP) for the tool integration framework
- Google Gemini for the AI model
- FastAPI and Next.js communities for excellent documentation

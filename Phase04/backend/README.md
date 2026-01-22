# Todo Backend API

Full-stack Todo application backend with JWT authentication, MCP server integration, and OpenAI agent capabilities.

## Features

- FastAPI REST API with async support
- JWT authentication with Better Auth
- PostgreSQL database with SQLModel ORM
- MCP (Model Context Protocol) server for AI agent tools
- OpenAI Agents SDK integration
- Stateless conversation management
- Comprehensive test coverage

## Environment Configuration

### Required Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host/database

# Authentication
BETTER_AUTH_SECRET=your-64-character-secret-here

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development

# OpenAI (for agent functionality)
OPENAI_API_KEY=sk-your-openai-api-key-here
```

## CORS Configuration

### Development vs Production

The application uses environment-aware CORS configuration:

#### Development Mode (`ENVIRONMENT=development`)
- Allows `http://localhost:3000` (default)
- Allows `FRONTEND_URL` from environment
- Automatically deduplicates origins

#### Production Mode (`ENVIRONMENT=production`)
- Only allows `FRONTEND_URL` from environment
- No localhost access
- Strict origin whitelist

### CORS Settings

**Allowed Methods:**
- GET
- POST
- PUT
- DELETE
- OPTIONS

**Allowed Headers:**
- Content-Type
- Authorization

**Credentials:** Enabled (required for JWT authentication)

### Environment Variable Configuration

**`FRONTEND_URL`** (Required)
- Development: `http://localhost:3000`
- Production: `https://your-app.vercel.app`
- Used as the primary allowed origin in production

**`CORS_ORIGINS`** (Legacy, still supported)
- Comma-separated list of allowed origins
- Example: `http://localhost:3000,http://localhost:3001`

### Security Considerations

1. **No Wildcard Origins:** Never use `*` in production - only explicit URLs
2. **HTTPS in Production:** Always use HTTPS URLs for production frontend
3. **Credentials Required:** JWT tokens require `allow_credentials=true`
4. **Restricted Methods:** Only necessary HTTP methods are allowed
5. **Explicit Headers:** Only Content-Type and Authorization headers allowed

### Configuration Examples

**Local Development:**
```bash
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
```

**Staging:**
```bash
FRONTEND_URL=https://your-app-staging.vercel.app
ENVIRONMENT=production
```

**Production:**
```bash
FRONTEND_URL=https://your-app.vercel.app
ENVIRONMENT=production
```

### Testing CORS

Run the integration tests:
```bash
pytest backend/tests/integration/test_cors.py -v
```

### Troubleshooting CORS Issues

**Symptom:** "CORS policy: No 'Access-Control-Allow-Origin' header"
- **Solution:** Verify `FRONTEND_URL` matches your frontend's actual URL exactly
- Check that `ENVIRONMENT` is set correctly
- Ensure protocol (http/https) matches

**Symptom:** "CORS policy: The value of the 'Access-Control-Allow-Credentials' header"
- **Solution:** This is expected behavior - credentials are required for JWT auth
- Ensure frontend sends `credentials: 'include'` in fetch requests

**Symptom:** OPTIONS preflight request fails
- **Solution:** OPTIONS is allowed by default
- Check that Authorization header is in allowed headers list

## Installation

### Using uv (Recommended)

```bash
cd backend
uv sync
```

### Using pip

```bash
cd backend
pip install -r requirements.txt
```

## Running the Server

### Development

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Production

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Testing

### Run All Tests

```bash
pytest backend/tests -v
```

### Run Specific Test Suites

```bash
# Unit tests
pytest backend/tests/unit -v

# Integration tests
pytest backend/tests/integration -v

# CORS tests
pytest backend/tests/integration/test_cors.py -v
```

### Coverage Report

```bash
pytest backend/tests --cov=app --cov-report=html
```

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check with database status

### Tasks API
- `POST /api/{user_id}/tasks` - Create task
- `GET /api/{user_id}/tasks` - List tasks
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task

All task endpoints require JWT authentication via `Authorization: Bearer <token>` header.

## Architecture

### Middleware Stack
1. CORS Middleware (environment-aware origin filtering)
2. JWT Authentication (via dependency injection)

### Database Models
- User (managed by Better Auth)
- Task (user-isolated todo items)
- Conversation (chat history)
- Message (conversation messages)

### MCP Tools
- `add_task` - Create new task
- `list_tasks` - List user's tasks
- `complete_task` - Mark task as complete
- `update_task` - Update task details
- `delete_task` - Delete task

## Security

### Authentication
- JWT tokens issued by Better Auth frontend
- Token verification on all protected endpoints
- User ID isolation (users can only access their own data)

### CORS
- Environment-based origin whitelisting
- No wildcard origins in production
- Credentials support for authentication

### Database
- User isolation enforced at query level
- All queries filtered by authenticated user_id
- Async connection pooling

## Deployment

### Render.com

1. Create new Web Service
2. Connect repository
3. Set environment variables from `.env.example`
4. Deploy

See `RENDER_DEPLOYMENT.md` for detailed instructions.

### Railway

1. Create new project
2. Connect repository
3. Set environment variables
4. Deploy

## Development Guidelines

### Adding New Endpoints

1. Define Pydantic schemas in `app/schemas/`
2. Create route handler in `app/routes/`
3. Add JWT dependency: `current_user: str = Depends(verify_jwt)`
4. Enforce user isolation: `WHERE user_id = current_user`
5. Write integration tests

### Adding MCP Tools

1. Create tool function in `app/mcp/tools/`
2. Register tool in `app/mcp/server.py`
3. Write unit tests in `backend/tests/unit/`
4. Test with MCP inspector

## License

MIT

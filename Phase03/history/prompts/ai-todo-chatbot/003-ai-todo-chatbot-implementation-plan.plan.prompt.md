---
id: 003
title: AI Todo Chatbot Implementation Plan
stage: plan
date: 2026-01-13
surface: agent
model: claude-sonnet-4-5
feature: ai-todo-chatbot
branch: 001-ai-todo-chatbot
user: system
command: /sp.plan
labels: ["plan", "architecture", "mcp-tools", "fastapi", "openai-agents", "chatkit", "database-design"]
links:
  spec: specs/001-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-todo-chatbot/plan.md
tests:
  - none
---

## Prompt

Generate detailed technical plan for AI Todo Chatbot including all 7 components: Database Layer (SQLModel with Neon PostgreSQL), MCP Server (Official Python SDK with 5 tools), OpenAI Agent Integration, Stateless FastAPI endpoint, ChatKit Frontend (Next.js 16), Testing Suite (pytest/httpx), Configuration & Deployment. Include architecture diagrams, 11-step stateless flow, MCP tool patterns, JWT authentication, CORS configuration, and complete code patterns for all integrations.

## Response snapshot

Created comprehensive 960-line implementation plan covering:

**Phase 0 - Research** (8 technical investigations):
1. MCP SDK Python patterns (stdio server, async tools, JSON schemas)
2. OpenAI Agents SDK integration (function calling, conversation history)
3. Stateless conversation flow with PostgreSQL
4. JWT authentication (middleware + Depends pattern)
5. Better Auth + ChatKit integration
6. Testing strategy (mocking, fixtures, coverage)
7. ChatKit domain allowlist workflow
8. CORS configuration for FastAPI + Vercel

**Phase 1 - Design**:
- Complete database schema (Task, Conversation, Message) with SQLModel definitions
- OpenAPI 3.0 contract for POST /api/{user_id}/chat endpoint
- Quickstart guide with setup, testing, deployment instructions

**Project Structure**:
- Backend: src/models, src/mcp/tools, src/agent, src/api, src/database
- Frontend: app/chat, lib/auth, lib/api, components/ChatInterface
- Tests: unit, integration, e2e with conftest fixtures

**Architecture Diagrams**:
- System architecture (ChatKit → FastAPI → OpenAI Agent → MCP → PostgreSQL)
- 11-step stateless conversation flow with detailed steps
- MCP tool execution sequence

**Constitution Check**: ✅ All 6 principles validated, zero violations

**Code Patterns Documented**:
- MCP server initialization with `@server.call_tool()` decorator
- OpenAI Agent setup with function registration
- JWT verification with FastAPI Security + Depends
- Better Auth session management in React
- Pytest fixtures for async DB + OpenAI mocking
- CORS middleware configuration

Plan provides complete technical blueprint ready for `/sp.tasks` command.

## Outcome

- ✅ Impact: Complete Phase 0 (Research) and Phase 1 (Design) with all technical patterns documented and ready for implementation
- 🧪 Tests: Testing strategy defined (pytest fixtures, mocking patterns, 80% coverage enforcement)
- 📁 Files: Created plan.md (35.9KB), contracts directory prepared for OpenAPI specs
- 🔁 Next prompts: /sp.tasks to generate detailed implementation tasks organized by user story
- 🧠 Reflection: All implementation questions answered with code patterns. Constitution check passed. System architecture validated. Ready for task breakdown.

## Evaluation notes (flywheel)

- Failure modes observed: None - comprehensive plan covers all components with concrete patterns
- Graders run and results (PASS/FAIL): PASS - All constitutional principles satisfied, complete technical context, no ambiguities remaining
- Prompt variant (if applicable): comprehensive-plan-with-research-and-patterns-v1
- Next experiment (smallest change to try): Generate tasks.md with test-first approach, organize by user story priorities

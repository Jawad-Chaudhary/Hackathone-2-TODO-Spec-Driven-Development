# MCP Server Quick Reference

## Running the Server

```bash
cd backend
python -m src.mcp.server
```

## Tool Schemas (JSON)

### add_task
```json
{
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"  // optional
}
```

### list_tasks
```json
{
  "user_id": "user123",
  "status": "all"  // "all" | "pending" | "completed"
}
```

### complete_task
```json
{
  "user_id": "user123",
  "task_id": 1
}
```

### delete_task
```json
{
  "user_id": "user123",
  "task_id": 1
}
```

### update_task
```json
{
  "user_id": "user123",
  "task_id": 1,
  "title": "Updated title",  // optional
  "description": "Updated description"  // optional
}
```

## Success Response Format

```json
{
  "status": "success",
  "task": { /* task object */ }
}
```

## Error Response Format

```json
{
  "error": "Error description",
  "status": "error"
}
```

## Validation Rules

- **user_id**: Required, non-empty string
- **title**: 1-200 characters
- **description**: Max 1000 characters
- **status**: "all", "pending", or "completed"
- **task_id**: Must exist and belong to user_id

## Security

- All operations enforce user isolation
- Ownership checked in database queries
- Generic error messages prevent enumeration
- No secrets in code (use .env)

## Environment

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
```

## Next Steps

1. T-019: Initialize OpenAI Agent
2. T-020: Register MCP tools as OpenAI functions
3. T-021: Implement agent execution
4. T-022: Create FastAPI chat endpoint

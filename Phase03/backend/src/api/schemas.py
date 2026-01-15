# [Task]: T-025
# [From]: specs/001-ai-todo-chatbot/tasks.md

"""
API Request/Response Schemas

Pydantic models for validating and serializing API data.
"""

from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """
    Request schema for chat endpoint.

    Fields:
        message: User message content (1-2000 characters)
        conversation_id: Optional ID of existing conversation
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User message content",
        examples=["Add a task to buy groceries"]
    )
    conversation_id: Optional[int] = Field(
        default=None,
        description="ID of existing conversation (creates new if omitted)",
        examples=[123]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Add a task to buy groceries",
                    "conversation_id": None
                },
                {
                    "message": "Show me my pending tasks",
                    "conversation_id": 42
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """
    Response schema for chat endpoint.

    Fields:
        conversation_id: ID of the conversation
        response: AI assistant's text response
        tool_calls: List of tool calls made by the agent
    """
    conversation_id: int = Field(
        ...,
        description="ID of the conversation",
        examples=[123]
    )
    response: str = Field(
        ...,
        description="AI assistant's response message",
        examples=["I've added 'buy groceries' to your task list."]
    )
    tool_calls: list[dict] = Field(
        default_factory=list,
        description="List of tool calls made during processing",
        examples=[
            [{"tool": "add_task", "status": "success"}]
        ]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "conversation_id": 123,
                    "response": "I've added 'buy groceries' to your task list.",
                    "tool_calls": [
                        {"tool": "add_task", "status": "success"}
                    ]
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """
    Error response schema for all endpoints.

    Fields:
        error: Short error message
        details: Optional detailed error information
    """
    error: str = Field(
        ...,
        description="Short error message",
        examples=["Unauthorized"]
    )
    details: Optional[str] = Field(
        default=None,
        description="Detailed error information",
        examples=["Token has expired"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "Unauthorized",
                    "details": "Token has expired"
                },
                {
                    "error": "Forbidden",
                    "details": "User ID mismatch"
                },
                {
                    "error": "Not Found",
                    "details": "Conversation not found"
                }
            ]
        }
    }

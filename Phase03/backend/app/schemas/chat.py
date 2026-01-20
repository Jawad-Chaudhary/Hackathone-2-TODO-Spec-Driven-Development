"""
Chat API request and response schemas.

This module defines Pydantic models for the chat endpoint:
- ChatRequest: Input schema for chat messages
- ChatResponse: Output schema with agent response and metadata
- ToolCall: Tool call information from OpenAI agent
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """
    Request schema for chat endpoint.

    Attributes:
        message: User's message text (required)
        conversation_id: Optional UUID to continue existing conversation
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User's message text"
    )
    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Existing conversation ID to continue (creates new if not provided)"
    )

    @field_validator('message')
    @classmethod
    def validate_message_not_empty(cls, v: str) -> str:
        """Ensure message is not just whitespace."""
        if not v.strip():
            raise ValueError("Message cannot be empty or whitespace only")
        return v.strip()


class ToolCallFunction(BaseModel):
    """Tool call function details."""
    name: str
    arguments: str


class ToolCall(BaseModel):
    """Tool call information from OpenAI agent."""
    id: str
    type: str
    function: ToolCallFunction


class ChatResponse(BaseModel):
    """
    Response schema for chat endpoint.

    Attributes:
        conversation_id: UUID of the conversation
        response: Assistant's response text
        tool_calls: Optional dict containing tool call information
    """
    conversation_id: UUID = Field(
        ...,
        description="Conversation UUID (existing or newly created)"
    )
    response: str = Field(
        ...,
        description="Assistant's response message"
    )
    tool_calls: Optional[List[ToolCall]] = Field(
        default=None,
        description="Tool calls made by assistant (if any)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "response": "I've added your task 'Buy groceries' to the list.",
                "tool_calls": [
                    {
                        "id": "call_0",
                        "type": "function",
                        "function": {
                            "name": "add_task",
                            "arguments": "{}"
                        }
                    }
                ]
            }
        }
    }

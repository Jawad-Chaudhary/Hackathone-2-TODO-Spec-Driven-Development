"""
Chat API endpoint for AI-powered conversations.

This module implements the stateless chat API that:
1. Loads or creates conversations
2. Persists user messages
3. Runs the AI agent with conversation history
4. Persists assistant responses
5. Updates conversation timestamps

All operations enforce user isolation through JWT authentication.
"""

import logging
from datetime import datetime
from typing import Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.dependencies.auth import get_current_user
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.agent.runner import run_agent

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["chat"])


async def ensure_user_exists(
    session: AsyncSession,
    user_id: str
) -> User:
    """
    Ensure a user exists in the database, creating if necessary.

    This is needed because Better Auth handles user creation on the frontend,
    but the backend needs a user record for foreign key constraints.

    Args:
        session: Database session
        user_id: User identifier from JWT token

    Returns:
        User model instance
    """
    # Check if user exists
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        # Create user with minimal info
        # Email can be updated later if needed
        user = User(
            id=user_id,
            email=f"{user_id}@placeholder.local",
            created_at=datetime.utcnow()
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        logger.info(f"Auto-created user: {user_id}")

    return user


async def load_or_create_conversation(
    session: AsyncSession,
    user_id: str,
    conversation_id: UUID | None
) -> Conversation:
    """
    Load existing conversation or create a new one.

    Args:
        session: Database session
        user_id: Authenticated user ID
        conversation_id: Optional conversation UUID to load

    Returns:
        Conversation object (existing or newly created)

    Raises:
        HTTPException: If conversation not found or doesn't belong to user
    """
    if conversation_id:
        # Load existing conversation
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id  # Enforce user isolation
        )
        result = await session.execute(stmt)
        conversation = result.scalar_one_or_none()

        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found or access denied"
            )

        logger.info(f"Loaded conversation {conversation_id} for user {user_id}")
        return conversation
    else:
        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

        logger.info(f"Created new conversation {conversation.id} for user {user_id}")
        return conversation


async def load_conversation_messages(
    session: AsyncSession,
    conversation_id: UUID
) -> list[Dict[str, str]]:
    """
    Load all messages for a conversation in chronological order.

    Args:
        session: Database session
        conversation_id: Conversation UUID

    Returns:
        List of message dicts in OpenAI format: [{"role": "user|assistant", "content": "..."}]
    """
    stmt = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at)

    result = await session.execute(stmt)
    db_messages = result.scalars().all()

    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in db_messages
    ]

    logger.debug(f"Loaded {len(messages)} messages for conversation {conversation_id}")
    return messages


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user)
) -> ChatResponse:
    """
    Chat endpoint for AI-powered task management conversations.

    Flow:
    0. Ensure user exists in database (auto-create if needed)
    1. Verify user_id matches JWT token (user isolation)
    2. Load or create conversation
    3. Persist user message to database
    4. Load conversation history
    5. Run AI agent with history
    6. Persist assistant response to database
    7. Update conversation timestamp
    8. Return response

    Args:
        user_id: User identifier from path parameter
        request: ChatRequest with message and optional conversation_id
        session: Database session (injected)
        current_user: Authenticated user ID from JWT (injected)

    Returns:
        ChatResponse with conversation_id, response, and optional tool_calls

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If user_id doesn't match JWT token
        HTTPException 404: If conversation_id not found or access denied
        HTTPException 500: If database or agent execution fails
    """
    # Enforce user_id matching (critical security check)
    if user_id != current_user:
        logger.warning(f"User {current_user} attempted to access user {user_id}'s chat")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch: cannot access another user's conversations"
        )

    try:
        # Step 0: Ensure user exists (auto-create if first time from Better Auth)
        await ensure_user_exists(session, user_id)

        # Step 1: Load or create conversation
        conversation = await load_or_create_conversation(
            session, user_id, request.conversation_id
        )

        # Step 2: Persist user message BEFORE agent invocation
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )
        session.add(user_message)
        await session.commit()
        logger.info(f"Persisted user message for conversation {conversation.id}")

        # Step 3: Load conversation history
        messages = await load_conversation_messages(session, conversation.id)

        # Step 4: Run agent with history
        try:
            # run_agent expects (user_id, messages) and returns dict with response, tool_calls, success, error
            agent_result = await run_agent(user_id, messages)

            if not agent_result["success"]:
                logger.error(f"Agent execution failed: {agent_result.get('error')}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"AI agent execution failed: {agent_result.get('error', 'Unknown error')}"
                )

            response_text = agent_result["response"]
            tool_calls_list = agent_result.get("tool_calls", [])

            # Convert tool name strings to ToolCall objects for frontend
            # Frontend expects: [{id: "1", type: "function", function: {name: "add_task", arguments: "{}"}}]
            tool_calls = None
            if tool_calls_list:
                tool_calls = [
                    {
                        "id": f"call_{i}",
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": "{}"
                        }
                    }
                    for i, tool_name in enumerate(tool_calls_list)
                ]

            logger.info(f"Agent completed successfully for user {user_id}")
        except HTTPException:
            raise
        except Exception as agent_error:
            logger.error(f"Agent execution failed: {agent_error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI agent execution failed: {str(agent_error)}"
            )

        # Step 5: Persist assistant response AFTER agent invocation
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
            tool_calls=tool_calls if tool_calls else None
        )
        session.add(assistant_message)

        # Step 6: Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)

        await session.commit()
        logger.info(f"Persisted assistant message for conversation {conversation.id}")

        # Step 7: Return response
        return ChatResponse(
            conversation_id=conversation.id,
            response=response_text,
            tool_calls=tool_calls if tool_calls else None
        )

    except HTTPException:
        # Re-raise HTTP exceptions (auth, not found, etc.)
        raise
    except Exception as e:
        # Catch-all for database or unexpected errors
        logger.error(f"Chat endpoint failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

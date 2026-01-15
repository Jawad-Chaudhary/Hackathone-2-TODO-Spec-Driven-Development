# [Task]: T-026, T-027, T-028
# [From]: specs/001-ai-todo-chatbot/tasks.md

"""
Chat API Routes

Implements the 11-step stateless conversation flow:
1. Receive message (FastAPI parameter)
2. Verify JWT token (middleware dependency)
3. Validate user_id matches token
4. Get or create conversation (database query)
5. Load conversation history from database
6. Build messages array: history + new user message
7. Save user message to database
8. Run agent with messages
9. Get agent response and tool calls
10. Save assistant message to database
11. Return response (no state retained in memory)
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Dict, Tuple
import json

from .schemas import ChatRequest, ChatResponse, ErrorResponse
from .middleware import verify_jwt
from ..database.session import get_db_session
from ..models.conversation import Conversation
from ..models.message import Message, MessageRole
from ..agent.runner import create_runner
from ..mcp.server import call_tool

# Router for chat endpoints
router = APIRouter(
    prefix="/api",
    tags=["chat"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)


async def load_conversation_history(
    session: AsyncSession,
    user_id: str,
    conversation_id: int | None
) -> Tuple[Conversation, list[dict]]:
    """
    Load or create conversation with message history (Steps 4-5).

    Args:
        session: Database session
        user_id: Authenticated user ID
        conversation_id: Optional existing conversation ID

    Returns:
        Tuple of (Conversation, messages list)

    Raises:
        HTTPException: 404 if conversation_id provided but not found
    """
    # Step 4: Get or create conversation
    if conversation_id:
        # Load existing conversation
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        result = await session.execute(stmt)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found or access denied"
            )
    else:
        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

    # Step 5: Load conversation history from database
    stmt = select(Message).where(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at)
    result = await session.execute(stmt)
    db_messages = result.scalars().all()

    # Convert to messages array for agent
    messages = [
        {"role": msg.role.value, "content": msg.content}
        for msg in db_messages
    ]

    return conversation, messages


async def run_agent_with_mcp_tools(
    messages: list[dict],
    user_id: str
) -> Tuple[str, list[dict]]:
    """
    Run the agent with MCP tool execution (Step 8-9).

    This function integrates the AgentRunner with the MCP server tools:
    1. Creates a tool_executor that wraps the MCP server's call_tool function
    2. Creates an AgentRunner instance
    3. Runs the agent with conversation history
    4. Returns response and tool_calls in the format expected by ChatResponse

    Args:
        messages: List of message dicts with role and content
        user_id: User ID for tool execution isolation

    Returns:
        Tuple of (response text, tool_calls list)
        - response text: Final natural language response from agent
        - tool_calls: List of dicts with {"tool": name, "status": "success"|"error"}
    """
    # Step 1: Create tool_executor that wraps MCP server's call_tool
    async def tool_executor(name: str, arguments: dict) -> dict:
        """
        Execute an MCP tool and parse the JSON response.

        Args:
            name: Tool name to execute
            arguments: Tool arguments dict

        Returns:
            dict: Parsed JSON result from the tool

        Raises:
            Exception: If tool execution fails or JSON parsing fails
        """
        # Call the MCP server's tool
        result_list = await call_tool(name, arguments)

        # Extract JSON from TextContent response
        # MCP server returns list[TextContent] where each has a .text field
        if not result_list:
            raise Exception(f"No response from tool {name}")

        # Parse the JSON text from the first TextContent
        result_text = result_list[0].text
        result_dict = json.loads(result_text)

        return result_dict

    # Step 2: Create AgentRunner instance
    runner = create_runner(tool_executor=tool_executor)

    # Step 3: Run the agent with messages and user_id
    response_text, tool_names = await runner.run(messages, user_id)

    # Step 4: Convert tool names to tool_calls format expected by ChatResponse
    # tool_names is list[str], we need list[dict] with {"tool": name, "status": ...}
    tool_calls = [
        {"tool": tool_name, "status": "success"}
        for tool_name in tool_names
    ]

    return response_text, tool_calls


@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    summary="Send chat message",
    description="Process a chat message with stateless conversation flow"
)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: AsyncSession = Depends(get_db_session),
    token_payload: Dict[str, str] = Depends(verify_jwt)
) -> ChatResponse:
    """
    Chat endpoint implementing 11-step stateless conversation flow.

    Steps:
    1. ✓ Receive message (FastAPI parameter)
    2. ✓ Verify JWT token (middleware dependency)
    3. ✓ Validate user_id matches token
    4. ✓ Get or create conversation
    5. ✓ Load conversation history
    6. ✓ Build messages array
    7. ✓ Save user message
    8. ✓ Run agent
    9. ✓ Get response and tool calls
    10. ✓ Save assistant message
    11. ✓ Return response

    Args:
        user_id: User ID from URL path
        request: ChatRequest with message and optional conversation_id
        session: Database session (dependency injected)
        token_payload: JWT payload (dependency injected)

    Returns:
        ChatResponse with conversation_id, response, and tool_calls

    Raises:
        HTTPException:
            - 401: Invalid or expired JWT token
            - 403: User ID mismatch between token and path
            - 404: Conversation not found
            - 500: Internal server error
    """
    try:
        # Step 1: Receive message (handled by FastAPI)
        # Step 2: Verify JWT token (handled by dependency)

        # Step 3: Validate user_id matches token
        token_user_id = token_payload.get("user_id")
        if user_id != token_user_id:
            raise HTTPException(
                status_code=403,
                detail="User ID mismatch: URL user_id does not match token"
            )

        # Steps 4-5: Load conversation and history
        conversation, messages = await load_conversation_history(
            session, user_id, request.conversation_id
        )

        # Step 6: Build messages array (history + new user message)
        # Note: We don't append to messages yet - we'll save to DB first

        # Step 7: Save user message to database
        user_msg = Message(
            user_id=user_id,
            conversation_id=conversation.id,
            role=MessageRole.user,
            content=request.message
        )
        session.add(user_msg)
        await session.commit()

        # Now append to messages array for agent
        messages.append({"role": "user", "content": request.message})

        # Steps 8-9: Run agent with messages and get response
        response_text, tool_calls = await run_agent_with_mcp_tools(messages, user_id)

        # Step 10: Save assistant message to database
        assistant_msg = Message(
            user_id=user_id,
            conversation_id=conversation.id,
            role=MessageRole.assistant,
            content=response_text
        )
        session.add(assistant_msg)
        await session.commit()

        # Update conversation timestamp
        conversation.updated_at = assistant_msg.created_at
        await session.commit()

        # Step 11: Return response (no state retained in memory)
        return ChatResponse(
            conversation_id=conversation.id,
            response=response_text,
            tool_calls=tool_calls
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An internal error occurred while processing your request"
        )


@router.get(
    "/{user_id}/conversations",
    summary="List user conversations",
    description="Get all conversations for authenticated user"
)
async def list_conversations(
    user_id: str,
    session: AsyncSession = Depends(get_db_session),
    token_payload: Dict[str, str] = Depends(verify_jwt)
) -> list[dict]:
    """
    List all conversations for the authenticated user.

    Args:
        user_id: User ID from URL path
        session: Database session
        token_payload: JWT payload

    Returns:
        List of conversation objects with id and timestamps

    Raises:
        HTTPException: 403 if user_id mismatch
    """
    # Validate user_id matches token
    token_user_id = token_payload.get("user_id")
    if user_id != token_user_id:
        raise HTTPException(
            status_code=403,
            detail="User ID mismatch"
        )

    # Query conversations
    stmt = select(Conversation).where(
        Conversation.user_id == user_id
    ).order_by(Conversation.updated_at.desc())
    result = await session.execute(stmt)
    conversations = result.scalars().all()

    return [
        {
            "id": conv.id,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat()
        }
        for conv in conversations
    ]


@router.get(
    "/{user_id}/conversations/{conversation_id}",
    summary="Get conversation history",
    description="Get all messages in a conversation"
)
async def get_conversation(
    user_id: str,
    conversation_id: int,
    session: AsyncSession = Depends(get_db_session),
    token_payload: Dict[str, str] = Depends(verify_jwt)
) -> dict:
    """
    Get full conversation with all messages.

    Args:
        user_id: User ID from URL path
        conversation_id: Conversation ID
        session: Database session
        token_payload: JWT payload

    Returns:
        Conversation object with messages array

    Raises:
        HTTPException: 403 if user_id mismatch, 404 if not found
    """
    # Validate user_id matches token
    token_user_id = token_payload.get("user_id")
    if user_id != token_user_id:
        raise HTTPException(
            status_code=403,
            detail="User ID mismatch"
        )

    # Load conversation and messages
    conversation, messages = await load_conversation_history(
        session, user_id, conversation_id
    )

    return {
        "id": conversation.id,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "messages": messages
    }

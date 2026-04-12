"""AI Chatbot Controller"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.data_contracts.api_request_response import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationResponse,
    ConversationListResponse,
)
from src.services.ai_service import ai_service
from src.middlewares.auth_middleware import AuthMiddleware, security_scheme
from src.database import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["AI Chatbot"])


@router.post(
    "/chat",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send message to plant care chatbot",
    description="Send a message to the AI plant care assistant and get a response"
)
async def chat(
    request: ChatMessageRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Send a message to the AI chatbot and get a response
    
    The chatbot is specialized in plant care advice, recommendations, and problem solving.
    
    - **message**: Your question or message for the plant care assistant
    - **conversation_id**: Optional. If provided, continues existing conversation. 
                         If null, starts new conversation.
    
    Returns conversation_id to continue conversation later.
    """
    try:
        # Authenticate user
        user = await AuthMiddleware.get_current_user(credentials)
        
        # Validate request
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        # Send message and get response
        response = await ai_service.chat(
            session,
            user_id=user.id,
            message=request.message.strip(),
            conversation_id=request.conversation_id
        )
        
        logger.info(f"✅ Chat response sent to user {user.id}")
        return response
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        error_detail = str(e)
        logger.error(f"❌ AI service error: {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=error_detail
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user's conversations",
    description="Get list of all conversations for the authenticated user"
)
async def get_conversations(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    limit: int = 50,
    session: AsyncSession = Depends(get_session)
):
    """
    Get list of all conversations for the authenticated user
    
    Conversations are sorted by most recent first.
    
    - **limit**: Maximum number of conversations to return (max 100)
    """
    try:
        # Authenticate user
        user = await AuthMiddleware.get_current_user(credentials)
        
        # Validate limit
        if limit < 1 or limit > 100:
            limit = 50
        
        # Get conversations
        conversations = await ai_service.list_conversations(session, user.id, limit=limit)
        
        return ConversationListResponse(
            conversations=conversations,
            total=len(conversations)
        )
        
    except Exception as e:
        logger.error(f"❌ Error fetching conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch conversations"
        )


@router.get(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_200_OK,
    summary="Get specific conversation",
    description="Get a specific conversation with all messages"
)
async def get_conversation(
    conversation_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Get a specific conversation with all its messages
    
    - **conversation_id**: ID of the conversation to retrieve
    """
    try:
        # Authenticate user
        user = await AuthMiddleware.get_current_user(credentials)
        
        # Handle "undefined" from frontend
        if conversation_id.lower() in ['undefined', 'null']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation ID"
            )
        
        # Get conversation
        conversation = await ai_service.get_conversation(session, user.id, conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return {
            "id": conversation.id,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role if isinstance(msg.role, str) else msg.role.value,
                    "message": msg.message,
                    "created_at": msg.created_at
                }
                for msg in conversation.messages
            ]
        }
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error fetching conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch conversation"
        )


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a conversation",
    description="Delete a conversation and all its messages"
)
async def delete_conversation(
    conversation_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a specific conversation and all its messages
    
    - **conversation_id**: ID of the conversation to delete
    """
    try:
        # Authenticate user
        user = await AuthMiddleware.get_current_user(credentials)
        
        # Delete conversation
        success = await ai_service.delete_conversation(session, user.id, conversation_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return {
            "message": "Conversation deleted successfully",
            "conversation_id": conversation_id
        }
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )

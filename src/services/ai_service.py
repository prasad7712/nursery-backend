"""AI Chat Service - Business logic for chatbot conversations"""
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from src.core.ai_core import get_ai_core
from src.plugins.database import db
from src.data_contracts.api_request_response import ChatMessageResponse, ConversationResponse

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI chat operations"""
    
    @staticmethod
    async def create_conversation(user_id: str) -> str:
        """
        Create a new conversation for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            Conversation ID
        """
        try:
            conversation = await db.client.aichatconversation.create(
                data={
                    'user_id': user_id,
                }
            )
            logger.info(f"✅ Created conversation {conversation.id} for user {user_id}")
            return conversation.id
        except Exception as e:
            logger.error(f"❌ Failed to create conversation: {e}")
            raise
    
    @staticmethod
    async def get_conversation(user_id: str, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a conversation with its messages
        
        Args:
            user_id: ID of the user (for authorization check)
            conversation_id: ID of the conversation
            
        Returns:
            Conversation dict with messages, or None if not found
        """
        try:
            conversation = await db.client.aichatconversation.find_unique(
                where={'id': conversation_id},
                include={'messages': True}
            )
            
            # Sort messages by created_at
            if conversation and conversation.messages:
                conversation.messages = sorted(conversation.messages, key=lambda x: x.created_at)
            
            if not conversation:
                logger.warning(f"Conversation {conversation_id} not found")
                return None
            
            # Verify user owns this conversation
            if conversation.user_id != user_id:
                logger.warning(f"User {user_id} attempted to access unauthorized conversation {conversation_id}")
                raise PermissionError("You don't have access to this conversation")
            
            return conversation
        except Exception as e:
            logger.error(f"❌ Failed to get conversation: {e}")
            raise
    
    @staticmethod
    async def list_conversations(user_id: str, limit: int = 50) -> List[ConversationResponse]:
        """
        List all conversations for a user, sorted by most recent first
        
        Args:
            user_id: ID of the user
            limit: Maximum number of conversations to return
            
        Returns:
            List of ConversationResponse objects
        """
        try:
            conversations = await db.client.aichatconversation.find_many(
                where={'user_id': user_id},
                take=limit
            )
            
            # Sort by updated_at descending
            conversations = sorted(conversations, key=lambda x: x.updated_at, reverse=True)
            
            return [
                ConversationResponse(
                    id=conv.id,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at
                )
                for conv in conversations
            ]
        except Exception as e:
            logger.error(f"❌ Failed to list conversations: {e}")
            raise
    
    @staticmethod
    async def chat(
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None
    ) -> ChatMessageResponse:
        """
        Send a message and get AI response
        
        This orchestrates:
        1. Create or get conversation
        2. Fetch conversation history
        3. Call Gemini API
        4. Save user message to DB
        5. Save AI response to DB
        6. Return response
        
        Args:
            user_id: ID of the user
            message: User's message
            conversation_id: Optional existing conversation ID
            
        Returns:
            ChatMessageResponse with AI response
        """
        try:
            logger.info(f"🔄 Starting chat for user {user_id}")
            
            # Create conversation if not provided
            if not conversation_id:
                logger.info("📝 Creating new conversation...")
                conversation_id = await AIService.create_conversation(user_id)
                logger.info(f"✅ Created new conversation: {conversation_id}")
            else:
                logger.info(f"🔍 Verifying authorization for conversation {conversation_id}")
                # Verify authorization
                existing = await AIService.get_conversation(user_id, conversation_id)
                if not existing:
                    raise ValueError(f"Conversation {conversation_id} not found")
                logger.info(f"✅ Authorized for conversation {conversation_id}")
            
            # Fetch conversation history (last 10 messages for context)
            logger.info(f"📚 Fetching conversation history from database...")
            conversation = await db.client.aichatconversation.find_unique(
                where={'id': conversation_id},
                include={'messages': True}
            )
            
            # Sort messages by created_at and limit to last 10
            if conversation and conversation.messages:
                conversation.messages = sorted(conversation.messages, key=lambda x: x.created_at)[-10:]
                logger.info(f"✅ Fetched {len(conversation.messages)} previous messages")
            
            # Convert message history to format for AI core
            history = [
                {'role': msg.role if isinstance(msg.role, str) else msg.role.value, 'message': msg.message}
                for msg in conversation.messages
            ]
            
            # Save user message to database
            logger.info(f"💾 Saving user message to database...")
            await db.client.aichatmessage.create(
                data={
                    'conversation_id': conversation_id,
                    'role': 'USER',
                    'message': message
                }
            )
            logger.info(f"✅ User message saved")
            
            # Get AI response
            logger.info(f"🤖 Calling Gemini AI API...")
            ai_core = get_ai_core()
            if not ai_core.is_available():
                # Log the actual error for debugging
                if ai_core.init_error:
                    logger.error(f"AI Core initialization error: {ai_core.init_error}")
                    raise RuntimeError(ai_core.init_error)
                else:
                    raise RuntimeError("AI service is not available. Check GEMINI_API_KEY.")
            
            ai_response = await ai_core.generate_response(message, history)
            logger.info(f"✅ AI response generated: {ai_response[:100]}...")
            
            # Save AI response to database
            logger.info(f"💾 Saving AI response to database...")
            await db.client.aichatmessage.create(
                data={
                    'conversation_id': conversation_id,
                    'role': 'ASSISTANT',
                    'message': ai_response
                }
            )
            logger.info(f"✅ AI response saved")
            
            # Update conversation timestamp
            logger.info(f"🕐 Updating conversation timestamp...")
            await db.client.aichatconversation.update(
                where={'id': conversation_id},
                data={'updated_at': datetime.now()}
            )
            logger.info(f"✅ Conversation updated")
            
            return ChatMessageResponse(
                message=message,
                response=ai_response,
                conversation_id=conversation_id,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"❌ Chat operation failed: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def delete_conversation(user_id: str, conversation_id: str) -> bool:
        """
        Delete a conversation (cascade deletes messages)
        
        Args:
            user_id: ID of the user
            conversation_id: ID of the conversation
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Verify user owns this conversation
            conversation = await db.client.aichatconversation.find_unique(
                where={'id': conversation_id}
            )
            
            if not conversation:
                logger.warning(f"Attempted to delete non-existent conversation {conversation_id}")
                return False
            
            if conversation.user_id != user_id:
                logger.warning(f"User {user_id} attempted to delete unauthorized conversation {conversation_id}")
                raise PermissionError("You don't have access to this conversation")
            
            # Delete conversation (cascade deletes messages)
            await db.client.aichatconversation.delete(
                where={'id': conversation_id}
            )
            logger.info(f"✅ Deleted conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete conversation: {e}")
            raise


# Create singleton instance
ai_service = AIService()

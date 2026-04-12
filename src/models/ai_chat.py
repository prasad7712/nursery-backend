"""AI chatbot conversation models"""
from datetime import datetime
from typing import List
from sqlalchemy import String, DateTime, Text, ForeignKey, Index, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, ChatMessageRoleEnum


class AIChatConversation(Base):
    """AI chat conversations with users"""
    __tablename__ = "ai_chat_conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    user_id: Mapped[str] = mapped_column("user_id", String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column("updated_at", DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="ai_conversations", lazy="joined")
    messages: Mapped[List["AIChatMessage"]] = relationship(
        "AIChatMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="select"
    )

    __table_args__ = (
        Index("idx_ai_chat_conversation_user_id", "user_id"),
        Index("idx_ai_chat_conversation_created_at", "created_at"),
    )


class AIChatMessage(Base):
    """Messages in AI chat conversations"""
    __tablename__ = "ai_chat_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    conversation_id: Mapped[str] = mapped_column("conversation_id", String(36), ForeignKey("ai_chat_conversations.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[ChatMessageRoleEnum] = mapped_column(Enum(ChatMessageRoleEnum, name="ChatMessageRole", native_enum=False, create_type=False), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    conversation: Mapped["AIChatConversation"] = relationship("AIChatConversation", back_populates="messages", lazy="joined")

    __table_args__ = (
        Index("idx_ai_chat_message_conversation_id", "conversation_id"),
        Index("idx_ai_chat_message_created_at", "created_at"),
    )

"""User and authentication models"""
from datetime import datetime
from typing import List
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Index, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, UserRoleEnum


class User(Base):
    """User model for authentication and application accounts"""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True, index=True)
    password_hash: Mapped[str] = mapped_column("password_hash", Text, nullable=False)
    first_name: Mapped[str | None] = mapped_column("first_name", String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column("last_name", String(100), nullable=True)
    role: Mapped[UserRoleEnum] = mapped_column(Enum(UserRoleEnum, name="UserRole", native_enum=False, create_type=False), default=UserRoleEnum.CUSTOMER, nullable=False)
    is_active: Mapped[bool] = mapped_column("is_active", Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updated_at", DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_logout_at: Mapped[datetime | None] = mapped_column("last_logout_at", DateTime(timezone=True), nullable=True)

    # Relationships
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", 
        back_populates="user", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    cart: Mapped["Cart | None"] = relationship(
        "Cart", 
        back_populates="user", 
        uselist=False,
        cascade="all, delete-orphan",
        lazy="select"
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order", 
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment", 
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    admin_logs: Mapped[List["AdminLog"]] = relationship(
        "AdminLog", 
        back_populates="admin",
        cascade="all, delete-orphan",
        lazy="select"
    )
    ai_conversations: Mapped[List["AIChatConversation"]] = relationship(
        "AIChatConversation", 
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )

    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_phone", "phone"),
    )


class RefreshToken(Base):
    """Refresh tokens for JWT authentication"""
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    user_id: Mapped[str] = mapped_column("user_id", String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(Text, nullable=False)
    token_hash: Mapped[str] = mapped_column("token_hash", String(255), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column("expires_at", DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    is_revoked: Mapped[bool] = mapped_column("is_revoked", Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens", lazy="joined")

    __table_args__ = (
        Index("idx_refresh_token_user_id", "user_id"),
        Index("idx_refresh_token_hash", "token_hash"),
    )

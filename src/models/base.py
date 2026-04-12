"""SQLAlchemy base configuration and enums"""
from enum import Enum
from sqlalchemy.orm import declarative_base

# Declarative base for all models
Base = declarative_base()


class UserRoleEnum(str, Enum):
    """User roles"""
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"


class OrderStatusEnum(str, Enum):
    """Order status values"""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class PaymentStatusEnum(str, Enum):
    """Payment status values"""
    PENDING = "PENDING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AdminActionTypeEnum(str, Enum):
    """Admin action types for audit logs"""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    STATUS_CHANGE = "STATUS_CHANGE"
    ROLE_CHANGE = "ROLE_CHANGE"
    DEACTIVATE = "DEACTIVATE"
    ACTIVATE = "ACTIVATE"


class ChatMessageRoleEnum(str, Enum):
    """Chat message sender roles"""
    USER = "USER"
    ASSISTANT = "ASSISTANT"

"""Payment models for Razorpay integration"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, DateTime, Text, ForeignKey, Index, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, PaymentStatusEnum
from src.utilities.id_generator import cuid


class Payment(Base):
    """Payment records for orders"""
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=cuid)
    order_id: Mapped[str] = mapped_column("orderId", String(50), ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id: Mapped[str] = mapped_column("userId", String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Razorpay fields
    razorpay_order_id: Mapped[str | None] = mapped_column("razorpayOrderId", String(255), nullable=True, index=True)
    razorpay_payment_id: Mapped[str | None] = mapped_column("razorpayPaymentId", String(255), nullable=True, index=True)
    razorpay_signature: Mapped[str | None] = mapped_column("razorpaySignature", String(255), nullable=True)
    
    # Payment details
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    status: Mapped[PaymentStatusEnum] = mapped_column(Enum(PaymentStatusEnum, name="PaymentStatus", native_enum=False, create_type=False), default=PaymentStatusEnum.PENDING, nullable=False, index=True)
    error_message: Mapped[str | None] = mapped_column("errorMessage", Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="payment", lazy="joined")
    user: Mapped["User"] = relationship("User", back_populates="payments", lazy="joined")

    __table_args__ = (
        Index("idx_payment_order_id", "orderId"),
        Index("idx_payment_user_id", "userId"),
        Index("idx_payment_status", "status"),
        Index("idx_payment_razorpay_order_id", "razorpayOrderId"),
        Index("idx_payment_razorpay_payment_id", "razorpayPaymentId"),
    )

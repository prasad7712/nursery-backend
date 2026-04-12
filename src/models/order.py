"""Order and order item models"""
from datetime import datetime
from typing import List
from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey, Index, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, OrderStatusEnum, PaymentStatusEnum
from src.utilities.id_generator import cuid


class Order(Base):
    """Customer orders"""
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=cuid)
    user_id: Mapped[str] = mapped_column("userId", String(36), ForeignKey("users.id"), nullable=False)
    status: Mapped[OrderStatusEnum] = mapped_column(Enum(OrderStatusEnum, name="OrderStatus", native_enum=False, create_type=False), default=OrderStatusEnum.PENDING, nullable=False, index=True)
    payment_status: Mapped[PaymentStatusEnum] = mapped_column("paymentStatus", Enum(PaymentStatusEnum, name="PaymentStatus", native_enum=False, create_type=False), default=PaymentStatusEnum.PENDING, nullable=False, index=True)
    payment_id: Mapped[str | None] = mapped_column("paymentId", String(50), nullable=True)
    total_amount: Mapped[float] = mapped_column("totalAmount", Float, nullable=False)
    shipping_address: Mapped[str | None] = mapped_column("shippingAddress", Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders", lazy="joined")
    payment: Mapped["Payment | None"] = relationship(
        "Payment",
        back_populates="order",
        uselist=False,
        lazy="select"
    )
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="select"
    )

    __table_args__ = (
        Index("idx_order_user_id", "userId"),
        Index("idx_order_status", "status"),
        Index("idx_order_payment_status", "paymentStatus"),
    )


class OrderItem(Base):
    """Individual items in an order"""
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=cuid)
    order_id: Mapped[str] = mapped_column("orderId", String(50), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[str] = mapped_column("productId", String(36), ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column("unitPrice", Float, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items", lazy="joined")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items", lazy="joined")

    __table_args__ = (
        Index("idx_order_item_order_id", "orderId"),
        Index("idx_order_item_product_id", "productId"),
    )

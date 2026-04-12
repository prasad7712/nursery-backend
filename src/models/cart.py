"""Shopping cart models"""
from datetime import datetime
from typing import List
from sqlalchemy import String, Integer, DateTime, ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base
from src.utilities.id_generator import cuid


class Cart(Base):
    """Shopping cart for users"""
    __tablename__ = "carts"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=cuid)
    user_id: Mapped[str] = mapped_column("userId", String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="cart", lazy="joined")
    items: Mapped[List["CartItem"]] = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
        lazy="select"
    )

    __table_args__ = (
        Index("idx_cart_user_id", "userId"),
    )


class CartItem(Base):
    """Items in shopping cart"""
    __tablename__ = "cart_items"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=cuid)
    cart_id: Mapped[str] = mapped_column("cartId", String(50), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[str] = mapped_column("productId", String(36), ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    cart: Mapped["Cart"] = relationship("Cart", back_populates="items", lazy="joined")
    product: Mapped["Product"] = relationship("Product", back_populates="cart_items", lazy="joined")

    __table_args__ = (
        PrimaryKeyConstraint("id"),
        Index("idx_cart_item_cart_id", "cartId"),
        Index("idx_cart_item_product_id", "productId"),
    )

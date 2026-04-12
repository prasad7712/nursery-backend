"""Admin and inventory models"""
from datetime import datetime
from typing import List
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Index, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, AdminActionTypeEnum
from src.utilities.id_generator import cuid


class AdminLog(Base):
    """Admin action audit logs"""
    __tablename__ = "admin_logs"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=cuid)
    admin_id: Mapped[str] = mapped_column("admin_id", String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action_type: Mapped[AdminActionTypeEnum] = mapped_column("action_type", Enum(AdminActionTypeEnum, name="AdminActionType", native_enum=False, create_type=False), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column("entity_type", String(100), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column("entity_id", String(100), nullable=False)
    old_values: Mapped[str | None] = mapped_column("old_values", Text, nullable=True)  # JSON
    new_values: Mapped[str | None] = mapped_column("new_values", Text, nullable=True)  # JSON
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column("ip_address", String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column("user_agent", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    admin: Mapped["User"] = relationship("User", back_populates="admin_logs", lazy="joined")

    __table_args__ = (
        Index("idx_admin_log_admin_id", "admin_id"),
        Index("idx_admin_log_action_type", "action_type"),
        Index("idx_admin_log_entity_type", "entity_type"),
        Index("idx_admin_log_created_at", "created_at"),
    )


class ProductInventory(Base):
    """Product inventory/stock management"""
    __tablename__ = "product_inventories"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=cuid)
    product_id: Mapped[str] = mapped_column("product_id", String(36), ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False)
    stock_level: Mapped[int] = mapped_column("stock_level", Integer, default=0, nullable=False)
    low_stock_threshold: Mapped[int] = mapped_column("low_stock_threshold", Integer, default=10, nullable=False)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updated_at", DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="inventory", lazy="joined")
    inventory_logs: Mapped[List["InventoryLog"]] = relationship(
        "InventoryLog",
        back_populates="inventory",
        cascade="all, delete-orphan",
        lazy="select"
    )

    __table_args__ = (
        Index("idx_product_inventory_product_id", "product_id"),
    )


class InventoryLog(Base):
    """Inventory change history"""
    __tablename__ = "inventory_logs"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=cuid)
    inventory_id: Mapped[str] = mapped_column("inventory_id", String(50), ForeignKey("product_inventories.id", ondelete="CASCADE"), nullable=False)
    change_type: Mapped[str] = mapped_column("change_type", String(50), nullable=False, index=True)  # ADD, REMOVE, ADJUST
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)  # can be negative
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column("created_by", String(36), nullable=True)  # admin user id
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    inventory: Mapped["ProductInventory"] = relationship("ProductInventory", back_populates="inventory_logs", lazy="joined")

    __table_args__ = (
        Index("idx_inventory_log_inventory_id", "inventory_id"),
        Index("idx_inventory_log_change_type", "change_type"),
        Index("idx_inventory_log_created_at", "created_at"),
    )

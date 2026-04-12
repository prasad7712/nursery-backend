"""Product catalog models"""
from datetime import datetime
from typing import List
from sqlalchemy import String, Float, Boolean, DateTime, Text, ForeignKey, Index, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base


class Category(Base):
    """Product categories"""
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updated_at", DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="select"
    )

    __table_args__ = (
        Index("idx_category_slug", "slug"),
    )


class Product(Base):
    """Products in the catalog"""
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    scientific_name: Mapped[str | None] = mapped_column("scientific_name", String(255), nullable=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    category_id: Mapped[str] = mapped_column("category_id", String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    cost_price: Mapped[float | None] = mapped_column("cost_price", Float, nullable=True)
    image_url: Mapped[str] = mapped_column("image_url", Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    care_instructions: Mapped[str] = mapped_column("care_instructions", Text, nullable=False)
    light_requirements: Mapped[str] = mapped_column("light_requirements", String(255), nullable=False)
    watering_frequency: Mapped[str] = mapped_column("watering_frequency", String(255), nullable=False)
    temperature_range: Mapped[str] = mapped_column("temperature_range", String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column("is_active", Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updated_at", DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="products", lazy="joined")
    diseases: Mapped[List["ProductDisease"]] = relationship(
        "ProductDisease",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="select"
    )
    cart_items: Mapped[List["CartItem"]] = relationship(
        "CartItem",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="select"
    )
    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="select"
    )
    inventory: Mapped["ProductInventory | None"] = relationship(
        "ProductInventory",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="select"
    )

    __table_args__ = (
        Index("idx_product_category_id", "category_id"),
        Index("idx_product_slug", "slug"),
        Index("idx_product_is_active", "is_active"),
    )


class ProductDisease(Base):
    """Common diseases for products"""
    __tablename__ = "product_diseases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    product_id: Mapped[str] = mapped_column("product_id", String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    disease_name: Mapped[str] = mapped_column("disease_name", String(255), nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="diseases", lazy="joined")

    __table_args__ = (
        Index("idx_product_disease_product_id", "product_id"),
    )

"""Admin API Request and Response Data Contracts"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator


# ==================== Dashboard Models ====================

class DashboardMetrics(BaseModel):
    """Dashboard metrics for admin overview"""
    total_users: int
    total_customers: int
    total_admins: int
    total_products: int
    total_orders: int
    total_revenue: float
    pending_orders: int
    low_stock_products: int
    
    class Config:
        from_attributes = True


class OrderMetrics(BaseModel):
    """Order-related metrics"""
    total_orders: int
    pending: int
    confirmed: int
    shipped: int
    delivered: int
    cancelled: int
    average_order_value: float
    total_revenue: float


class UserMetrics(BaseModel):
    """User-related metrics"""
    total_users: int
    active_users: int
    inactive_users: int
    total_admins: int
    new_users_this_month: int


class ProductMetrics(BaseModel):
    """Product-related metrics"""
    total_products: int
    active_products: int
    inactive_products: int
    low_stock_count: int
    total_inventory_value: float


# ==================== Product Management Models ====================

class AdminProductCreateRequest(BaseModel):
    """Create product request"""
    name: str = Field(..., min_length=1, max_length=200)
    scientific_name: Optional[str] = None
    category_id: str
    price: float = Field(..., gt=0)
    cost_price: Optional[float] = Field(None, gt=0)
    image_url: str
    description: str
    care_instructions: str
    light_requirements: str
    watering_frequency: str
    temperature_range: str
    is_active: bool = True


class AdminProductUpdateRequest(BaseModel):
    """Update product request"""
    name: Optional[str] = None
    scientific_name: Optional[str] = None
    category_id: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, gt=0)
    image_url: Optional[str] = None
    description: Optional[str] = None
    care_instructions: Optional[str] = None
    light_requirements: Optional[str] = None
    watering_frequency: Optional[str] = None
    temperature_range: Optional[str] = None
    is_active: Optional[bool] = None


class AdminProductResponse(BaseModel):
    """Product response for admin"""
    id: str
    name: str
    scientific_name: Optional[str]
    slug: str
    category_id: str
    price: float
    cost_price: Optional[float]
    image_url: str
    description: str
    care_instructions: str
    light_requirements: str
    watering_frequency: str
    temperature_range: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Category Management Models ====================

class AdminCategoryCreateRequest(BaseModel):
    """Create category request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str
    icon: Optional[str] = None


class AdminCategoryUpdateRequest(BaseModel):
    """Update category request"""
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None


class AdminCategoryResponse(BaseModel):
    """Category response for admin"""
    id: str
    name: str
    slug: str
    description: str
    icon: Optional[str]
    created_at: datetime
    updated_at: datetime
    product_count: Optional[int] = None
    
    class Config:
        from_attributes = True


# ==================== Order Management Models ====================

class AdminOrderStatusUpdateRequest(BaseModel):
    """Update order status request"""
    status: str = Field(..., pattern="^(PENDING|CONFIRMED|SHIPPED|DELIVERED|CANCELLED)$")
    note: Optional[str] = None


class AdminOrderResponse(BaseModel):
    """Order response for admin"""
    id: str
    user_id: str
    user_email: Optional[str]
    status: str
    payment_status: str
    total_amount: float
    shipping_address: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    items_count: Optional[int] = None
    
    class Config:
        from_attributes = True


# ==================== User Management Models ====================

class AdminUserStatusUpdateRequest(BaseModel):
    """Update user status request"""
    is_active: bool
    reason: Optional[str] = None


class AdminUserRoleChangeRequest(BaseModel):
    """Change user role request"""
    new_role: str = Field(..., pattern="^(admin|user|super_admin)$")
    reason: Optional[str] = None


class AdminUserUpdateRequest(BaseModel):
    """Update user request"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(ADMIN|CUSTOMER)$")
    is_active: Optional[bool] = None


class AdminUserResponse(BaseModel):
    """User response for admin"""
    id: str
    email: str
    phone: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    orders_count: Optional[int] = None
    
    class Config:
        from_attributes = True


# ==================== Inventory Management Models ====================

class AdminInventoryAdjustmentRequest(BaseModel):
    """Adjust inventory stock"""
    change_type: str = Field(..., pattern="^(ADD|REMOVE|ADJUST)$")
    quantity: int = Field(..., ne=0)
    reason: str = Field(..., min_length=1)
    note: Optional[str] = None


class AdjustInventoryRequest(BaseModel):
    """Adjust inventory stock"""
    change_type: str = Field(..., pattern="^(ADD|REMOVE|ADJUST)$")
    quantity: int = Field(..., ne=0)
    reason: str = Field(..., min_length=1)
    note: Optional[str] = None


class AdminInventoryResponse(BaseModel):
    """Inventory response for admin"""
    id: str
    product_id: str
    product_name: Optional[str]
    stock_level: int
    low_stock_threshold: int
    reorder_quantity: Optional[int] = None
    warehouse_location: Optional[str] = None
    last_restocked: Optional[datetime] = None
    is_low_stock: Optional[bool] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InventoryResponse(BaseModel):
    """Inventory response"""
    id: str
    product_id: str
    product_name: Optional[str]
    stock_level: int
    low_stock_threshold: int
    is_low_stock: Optional[bool] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InventoryLogResponse(BaseModel):
    """Inventory log response"""
    id: str
    inventory_id: str
    change_type: str
    quantity: int
    reason: str
    note: Optional[str]
    created_by: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Admin Log Models ====================

class AdminLogResponse(BaseModel):
    """Admin action log response"""
    id: str
    admin_id: str
    admin_email: Optional[str]
    action_type: str
    entity_type: str
    entity_id: str
    old_values: Optional[dict]
    new_values: Optional[dict]
    reason: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== List Response Models ====================

class AdminProductListResponse(BaseModel):
    """Product list response"""
    products: List[AdminProductResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class AdminCategoryListResponse(BaseModel):
    """Category list response"""
    categories: List[AdminCategoryResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class AdminOrderListResponse(BaseModel):
    """Order list response"""
    orders: List[AdminOrderResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class AdminUserListResponse(BaseModel):
    """User list response"""
    users: List[AdminUserResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class InventoryListResponse(BaseModel):
    """Inventory list response"""
    inventories: List[InventoryResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
    low_stock_count: int


class AdminInventoryListResponse(BaseModel):
    """Admin inventory list response"""
    inventories: List[AdminInventoryResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
    low_stock_count: Optional[int] = None


class AdminLogListResponse(BaseModel):
    """Admin log list response"""
    logs: List[AdminLogResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# ==================== Dashboard Models ====================

class AdminDashboardResponse(BaseModel):
    """Admin dashboard response with overall statistics"""
    users: dict = Field(..., description="User statistics: total, active, inactive")
    orders: dict = Field(..., description="Order statistics: total, by_status, by_payment_status")
    products: dict = Field(..., description="Product statistics: total, active, inactive")
    low_stock_count: int
    timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AdminLogsResponse(BaseModel):
    """Admin activity logs response"""
    logs: List[AdminLogResponse]
    total: int
    page: int
    per_page: int


# ==================== Shared Response Models ====================

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None

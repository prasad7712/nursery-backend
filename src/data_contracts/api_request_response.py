"""API Request and Response Data Contracts"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator


# ================ Auth Request Models ================

class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    phone: Optional[str] = None
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    
    @validator('password')
    def validate_password(cls, v):
        # Check byte length (bcrypt has 72 byte limit)
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password cannot exceed 72 bytes (bcrypt limitation)')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str = Field(..., max_length=72)
    
    @validator('password')
    def validate_password_bytes(cls, v):
        # Validate byte length (bcrypt has 72 byte limit)
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password cannot exceed 72 bytes (bcrypt limitation)')
        return v


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Change password request (authenticated)"""
    old_password: str = Field(..., max_length=72)
    new_password: str = Field(..., min_length=8, max_length=72)
    
    @validator('old_password', 'new_password', pre=True)
    def validate_password_bytes(cls, v):
        # Validate byte length (bcrypt has 72 byte limit)
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password cannot exceed 72 bytes (bcrypt limitation)')
        return v
    
    @validator('new_password')
    def validate_new_password_complexity(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


# ================ Auth Response Models ================

class UserResponse(BaseModel):
    """User data response"""
    id: str
    email: str
    phone: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(BaseModel):
    """Login response"""
    user: UserResponse
    tokens: TokenResponse


class RegisterResponse(BaseModel):
    """Registration response"""
    message: str
    user: UserResponse


# ================ Auth API Response Models (for API spec compliance) ================

class AuthUserResponse(BaseModel):
    """User response in auth API (camelCase for API spec)"""
    userId: str = Field(alias="id")
    email: str
    firstName: Optional[str] = Field(alias="first_name", default=None)
    lastName: Optional[str] = Field(alias="last_name", default=None)
    
    class Config:
        from_attributes = True
        populate_by_name = True


class RegisterApiResponse(BaseModel):
    """Register API response matching spec"""
    userId: str = Field(alias="id")
    email: str
    firstName: Optional[str] = Field(alias="first_name", default=None)
    lastName: Optional[str] = Field(alias="last_name", default=None)
    role: Optional[str] = "CUSTOMER"
    token: str  # access_token
    refresh_token: str
    
    class Config:
        from_attributes = True
        populate_by_name = True


class LoginApiResponse(BaseModel):
    """Login API response matching spec"""
    userId: str = Field(alias="id")
    email: str
    firstName: Optional[str] = Field(alias="first_name", default=None)
    lastName: Optional[str] = Field(alias="last_name", default=None)
    role: Optional[str] = "CUSTOMER"
    token: str  # access_token
    refresh_token: str
    
    class Config:
        from_attributes = True
        populate_by_name = True


class GetMeApiResponse(BaseModel):
    """Get current user API response matching spec"""
    userId: str = Field(alias="id")
    email: str
    firstName: Optional[str] = Field(alias="first_name", default=None)
    lastName: Optional[str] = Field(alias="last_name", default=None)
    
    class Config:
        from_attributes = True
        populate_by_name = True


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    success: bool = False


class RateLimitResponse(BaseModel):
    """Rate limit response"""
    error: str = "Rate limit exceeded"
    limit: int
    remaining: int
    reset: int
    success: bool = False


# ================ Health Check Response ================

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    cache: str
    timestamp: datetime


# ================ Product Request Models ================

class ProductFilterRequest(BaseModel):
    """Product filter and search request"""
    category_id: Optional[str] = None
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=100)


# ================ Product Response Models ================

class CategoryResponse(BaseModel):
    """Category response"""
    id: str
    name: str
    slug: str
    description: str
    icon: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    """Product listing response (simplified for list view)"""
    id: str
    name: str
    scientific_name: Optional[str]
    slug: str
    category_id: str
    price: float
    image_url: str
    description: str
    care_instructions: str
    light_requirements: str
    watering_frequency: str
    temperature_range: str
    common_diseases: list[str] = []
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductDetailResponse(BaseModel):
    """Product detail response (full product information)"""
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
    common_diseases: list[str] = []
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductsListResponse(BaseModel):
    """Products list response with pagination"""
    products: list[ProductResponse]
    total: int
    page: int
    per_page: int


class CategoriesListResponse(BaseModel):
    """Categories list response"""
    categories: list[CategoryResponse]
    total: int


# ==================== CART REQUEST/RESPONSE MODELS ====================

class CartItemAddRequest(BaseModel):
    """Add item to cart request"""
    product_id: str = Field(..., description="Product ID to add to cart")
    quantity: int = Field(default=1, ge=1, le=100, description="Quantity (1-100)")


class CartItemUpdateRequest(BaseModel):
    """Update cart item quantity request"""
    quantity: int = Field(..., ge=0, le=100, description="New quantity (0 to remove)")


class CartItemResponse(BaseModel):
    """Cart item in response (camelCase)"""
    id: str = Field(alias="id")
    productId: str = Field(alias="product_id")
    productName: str = Field(alias="product_name")
    productImage: Optional[str] = Field(None, alias="product_image")
    price: float = Field(alias="price")
    quantity: int = Field(alias="quantity")
    subtotal: float = Field(alias="subtotal")
    
    class Config:
        from_attributes = True
        populate_by_name = True


class CartResponse(BaseModel):
    """Cart response with items (camelCase)"""
    id: Optional[str] = Field(None, alias="id")
    userId: str = Field(alias="user_id")
    items: list[CartItemResponse] = Field(default_factory=list, alias="items")
    totalAmount: float = Field(alias="total_amount")
    totalItems: int = Field(alias="total_items")
    createdAt: Optional[datetime] = Field(None, alias="created_at")
    updatedAt: Optional[datetime] = Field(None, alias="updated_at")
    
    class Config:
        from_attributes = True
        populate_by_name = True


# ==================== ORDER REQUEST/RESPONSE MODELS ====================

class OrderItemResponse(BaseModel):
    """Order item in response (camelCase)"""
    id: str = Field(alias="id")
    productId: str = Field(alias="product_id")
    productName: str = Field(alias="product_name")
    productImage: Optional[str] = Field(None, alias="product_image")
    quantity: int = Field(alias="quantity")
    unitPrice: float = Field(alias="unit_price")
    subtotal: float = Field(alias="subtotal")
    
    class Config:
        from_attributes = True
        populate_by_name = True


class CreateOrderRequest(BaseModel):
    """Create order request"""
    shipping_address: str = Field(..., min_length=10, max_length=500, description="Delivery address")
    notes: Optional[str] = Field(None, max_length=500, description="Special instructions")
    
    @validator('shipping_address')
    def validate_address(cls, v):
        """Validate shipping address"""
        if len(v.strip()) < 10:
            raise ValueError("Address must be at least 10 characters")
        return v


class OrderResponse(BaseModel):
    """Order response with items (camelCase)"""
    id: str = Field(alias="id")
    userId: str = Field(alias="user_id")
    status: str = Field(alias="status")
    items: list[OrderItemResponse] = Field(alias="items")
    totalAmount: float = Field(alias="total_amount")
    shippingAddress: Optional[str] = Field(None, alias="shipping_address")
    notes: Optional[str] = Field(None, alias="notes")
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")
    
    class Config:
        from_attributes = True
        populate_by_name = True


class OrderListResponse(BaseModel):
    """Order list response with pagination"""
    orders: list[OrderResponse]
    total: int
    page: int
    per_page: int


# ==================== PAYMENT REQUEST/RESPONSE MODELS ====================

class CreatePaymentOrderRequest(BaseModel):
    """Create payment order request"""
    order_id: str = Field(..., description="Database order ID")
    amount: float = Field(..., gt=0, description="Payment amount in rupees")
    currency: str = Field("INR", description="Currency code")


class VerifyPaymentRequest(BaseModel):
    """Verify payment signature request"""
    razorpay_order_id: str = Field(..., description="Razorpay order ID")
    razorpay_payment_id: str = Field(..., description="Razorpay payment ID")
    razorpay_signature: str = Field(..., description="Razorpay payment signature")


class PaymentResponse(BaseModel):
    """Payment response (camelCase)"""
    id: Optional[str] = Field(None, description="Payment ID")
    orderId: Optional[str] = Field(None, alias="order_id", description="Order ID")
    userId: Optional[str] = Field(None, alias="user_id", description="User ID")
    amount: Optional[float] = Field(None, description="Payment amount")
    currency: Optional[str] = Field(None, description="Currency code")
    status: Optional[str] = Field(None, description="Payment status")
    razorpayOrderId: Optional[str] = Field(None, alias="razorpay_order_id", description="Razorpay Order ID")
    razorpayPaymentId: Optional[str] = Field(None, alias="razorpay_payment_id", description="Razorpay Payment ID")
    razorpaySignature: Optional[str] = Field(None, alias="razorpay_signature", description="Razorpay Signature")
    errorMessage: Optional[str] = Field(None, alias="error_message", description="Error message if payment failed")
    createdAt: Optional[datetime] = Field(None, alias="created_at", description="Payment creation timestamp")
    updatedAt: Optional[datetime] = Field(None, alias="updated_at", description="Payment update timestamp")
    
    # Special fields for API responses
    key_id: Optional[str] = Field(None, description="Razorpay Key ID for frontend")
    verified: Optional[bool] = Field(None, description="Whether payment is verified")
    message: Optional[str] = Field(None, description="Response message")
    demo_mode: Optional[bool] = Field(None, description="Whether in demo mode (for testing)")
    
    class Config:
        from_attributes = True
        populate_by_name = True


class PaymentListResponse(BaseModel):
    """Payment list response with pagination"""
    payments: list[PaymentResponse]
    total: int
    page: int
    per_page: int

# 🌱 Nursery Backend - E-Commerce API

A production-ready **FastAPI** backend for a nursery/plant e-commerce platform with comprehensive product management, shopping cart, order processing, payment integration, AI plant care chatbot, and advanced admin dashboard.

**Status:** 🚀 Phase 2A+ (Complete: Auth, Products, Cart, Orders, Payments, Admin, AI)  
**Version:** 1.0.0  
**Python:** 3.11+  
**License:** MIT

---

## 📖 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Docker Deployment](#docker-deployment)
- [Database](#database)
- [API Documentation](#api-documentation)
  - [Authentication](#authentication)
  - [Products & Categories](#products--categories)
  - [Shopping Cart](#shopping-cart)
  - [Orders](#orders)
  - [Payments](#payments)
  - [AI Chatbot](#ai-chatbot)
  - [Admin Dashboard](#admin-dashboard)
  - [Admin User Management](#admin-user-management)
  - [Admin Order Management](#admin-order-management)
  - [Admin Product Management](#admin-product-management)
  - [Admin Category Management](#admin-category-management)
  - [Admin Inventory Management](#admin-inventory-management)
- [Data Models](#data-models)
- [Authentication & Security](#authentication--security)
- [Testing](#testing)
- [Development Guide](#development-guide)
- [Troubleshooting](#troubleshooting)
- [Additional Resources](#additional-resources)

---

## Overview

**Nursery Backend** is a complete REST API solution built with FastAPI, SQLAlchemy, and PostgreSQL for managing a plant/nursery e-commerce platform. It combines modern async architecture with comprehensive business logic for handling users, products, shopping, orders, payments, and AI-assisted customer support.

### Core Capabilities

✅ **User Management** - Registration, JWT authentication, role-based access control  
✅ **Product Catalog** - Full CRUD with categories, detailed plant metadata, disease tracking  
✅ **Shopping Cart** - Persistent user carts with quantity management  
✅ **Order Management** - Complete lifecycle management with status tracking  
✅ **Payment Processing** - Razorpay integration with webhook verification  
✅ **AI Assistant** - Groq-powered plant care chatbot with conversation history  
✅ **Admin Suite** - Dashboard, user management, inventory control, activity logs  
✅ **Security** - Rate limiting, input validation, CORS, audit trails  

---

## Key Features

### 🔐 Authentication & User Management
- User registration with email validation
- Secure login with JWT access + refresh tokens
- Password management and secure hashing (bcrypt)
- Role-based access control (CUSTOMER, ADMIN)
- Account activation/deactivation
- Refresh token tracking and revocation
- Automatic admin account initialization

### 🛍️ Product Catalog
- Complete CRUD operations for products (admin-only)
- Product categories with icons and descriptions
- Plant-specific metadata:
  - Care instructions and light requirements
  - Watering frequency (Daily, Weekly, Bi-weekly, Monthly)
  - Temperature ranges for optimal growth
  - Scientific names for accuracy
- Disease tracking with product relationships
- Product inventory management with low-stock alerts
- Advanced search and filtering by name, category, price
- Pagination support for all list endpoints

### 🛒 Shopping Cart
- One persistent cart per user
- Add/remove products with quantity management
- Real-time cart updates and total calculations
- Cart item validation
- Clear entire cart on order creation

### 📦 Order Management
- Create orders directly from cart contents
- Complete order status workflow:
  - PENDING → CONFIRMED → SHIPPED → DELIVERED
- Shipping address and delivery notes
- Order item tracking with frozen pricing
- Order history per user with pagination
- Admin order status management
- Order filtering and search capabilities

### 💳 Payment Processing
- Razorpay payment gateway integration
- Create payment orders for checkout flow
- Payment verification with signature validation
- Payment status tracking:
  - PENDING → CONFIRMED/FAILED
- Webhook support for real-time payment updates
- Demo mode for development and testing
- Complete transaction audit trail
- Automatic payment order linking to orders

### 🤖 AI Plant Care Assistant
- Groq API integration for intelligent responses
- Specialized plant care advice and recommendations
- Conversation management with full history
- Start new conversations or continue existing ones
- Message-level tracking with timestamps
- Delete conversations and manage history
- Real-time response capability

### 👨‍💼 Admin Dashboard
**Statistics & Metrics:**
- Real-time user, order, and product metrics
- Revenue tracking and analysis
- Pending order counts
- Active user statistics
- Product performance data

**User Management:**
- List all users with advanced filtering
- Search by name, email, phone
- Filter by role and activation status
- Activate/deactivate user accounts
- View user detailed information

**Order Management:**
- View all orders with detailed information
- Filter by status, payment status, user
- Update order statuses
- Track payment information
- Admin order cancellation

**Inventory Management:**
- Monitor product stock levels
- Low-stock alerts with configurable thresholds
- Adjust quantities manually
- Track stock by product
- Bulk operations support

**Category Management:**
- Create and edit product categories
- Manage category icons and descriptions
- View products per category
- Category organization

**Activity Logging:**
- Complete audit trail of admin actions
- Timestamp and actor tracking
- Action type categorization
- Admin ID filtering
- Full change history

### 🔒 Security & Performance
- **Async Operations** - Non-blocking database queries for high throughput
- **Connection Pooling** - SQLAlchemy pool (20 connections, 0 overflow)
- **Health Checks** - Pre-ping verification and database health monitoring
- **Rate Limiting** - Configurable per-endpoint limits
- **CORS Support** - Flexible cross-origin request handling
- **Input Validation** - Pydantic v2 request/response contracts
- **Global Error Handling** - Comprehensive exception responses
- **Structured Logging** - Application and request logging
- **Password Security** - bcrypt hashing with configurable iterations

---

## 🛠️ Tech Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.115.0 | REST API framework with async support |
| **Server** | Uvicorn | 0.31.0 | ASGI server for running FastAPI |
| **Database ORM** | SQLAlchemy | 2.0+ | Async ORM for database operations |
| **Database Driver** | asyncpg | 0.29.0 | Async PostgreSQL driver |
| **Database** | PostgreSQL | 14+ | Primary data store |
| **Validation** | Pydantic | 2.6.0 | Request/response validation |
| **Authentication** | PyJWT | 3.3.0 | JWT token generation and verification |
| **Password Hashing** | passlib + bcrypt | 1.7.4 | Secure password storage |
| **Payment Gateway** | Razorpay | 1.4.1 | Payment processing integration |
| **AI API** | Groq | 0.9.0 | LLM for chatbot functionality |
| **Configuration** | python-dotenv | 1.0.1 | Environment variable management |
| **Testing** | pytest + pytest-asyncio | 8.3.4 | Async testing framework |
| **HTTP Client** | httpx | 0.24.1+ | Async HTTP client for testing |
| **Email Validation** | email-validator | 2.3.0 | Email format validation |

---

## System Architecture

### Application Layers

```
┌─────────────────────────────────────────┐
│     HTTP Clients (Mobile, Web, etc.)    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│    Controllers (HTTP Handlers)          │
│    ├─ auth_controller                   │
│    ├─ product_controller                │
│    ├─ cart_controller                   │
│    ├─ order_controller                  │
│    ├─ payment_controller                │
│    ├─ ai_controller                     │
│    └─ admin_*_controllers               │
└─────────────────┬───────────────────────┘
         (Middleware: Auth, Rate-Limit)
                  │
┌─────────────────▼───────────────────────┐
│    Services (Business Logic)            │
│    ├─ auth_service                      │
│    ├─ product_service                   │
│    ├─ cart_service                      │
│    ├─ order_service                     │
│    ├─ payment_service                   │
│    ├─ ai_service                        │
│    ├─ admin_service                     │
│    └─ analytics_service                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│    Core Functions (Domain Logic)        │
│    ├─ auth_core                         │
│    ├─ product_core                      │
│    ├─ cart_core                         │
│    ├─ order_core                        │
│    ├─ payment_core                      │
│    └─ ai_core                           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│    Data Access Layer (ORM)              │
│    └─ SQLAlchemy AsyncSession           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│    PostgreSQL Database                  │
└─────────────────────────────────────────┘
```

### Directory Structure

```
nursery-backend/
├── src/
│   ├── main.py                          # FastAPI app entry point
│   ├── database.py                      # SQLAlchemy setup & session management
│   │
│   ├── controllers/                     # HTTP request handlers
│   │   ├── auth_controller.py
│   │   ├── product_controller.py
│   │   ├── cart_controller.py
│   │   ├── order_controller.py
│   │   ├── payment_controller.py
│   │   ├── ai_controller.py
│   │   ├── dashboard_controller.py
│   │   ├── admin_dashboard_controller.py
│   │   ├── admin_user_controller.py
│   │   ├── admin_order_controller.py
│   │   ├── admin_product_controller.py
│   │   ├── admin_category_controller.py
│   │   ├── admin_inventory_controller.py
│   │   └── admin_setup_controller.py
│   │
│   ├── services/                        # Business logic layer
│   │   ├── auth_service.py
│   │   ├── product_service.py
│   │   ├── cart_service.py
│   │   ├── order_service.py
│   │   ├── payment_service.py
│   │   ├── ai_service.py
│   │   ├── admin_service.py
│   │   └── analytics_service.py
│   │
│   ├── core/                            # Domain-specific logic
│   │   ├── auth_core.py
│   │   ├── product_core.py
│   │   ├── cart_core.py
│   │   ├── order_core.py
│   │   ├── payment_core.py
│   │   └── ai_core.py
│   │
│   ├── models/                          # SQLAlchemy ORM models
│   │   ├── base.py                      # Base model & enums
│   │   ├── user.py                      # User & RefreshToken
│   │   ├── product.py                   # Product, Category
│   │   ├── cart.py                      # Cart, CartItem
│   │   ├── order.py                     # Order, OrderItem
│   │   ├── payment.py                   # Payment
│   │   ├── ai_chat.py                   # AIChatConversation, AIChatMessage
│   │   └── admin.py                     # ProductInventory, AdminLog
│   │
│   ├── data_contracts/                  # Pydantic request/response models
│   │   ├── api_request_response.py
│   │   └── admin_request_response.py
│   │
│   ├── middlewares/                     # Custom middleware
│   │   └── auth_middleware.py           # JWT authentication middleware
│   │
│   ├── utilities/                       # Helper utilities
│   │   ├── config_manager.py
│   │   ├── admin_init.py
│   │   ├── rate_limiter.py
│   │   └── id_generator.py
│   │
│   └── tests/                           # Test suites
│       ├── test_auth.py
│       ├── test_models.py
│       └── test_api.py
│
├── config/                              # Environment-specific configs
│   ├── dev_app_config.json
│   ├── qa_app_config.json
│   └── prod_app_config.json
│
├── prisma/                              # Prisma schema (legacy)
│   └── schema.prisma
│
├── sample_requests/                     # API request examples
│   ├── api_requests.http
│   └── admin_requests.http
│
├── docs/                                # Documentation
│   ├── PHASE_2A_BACKEND_FOUNDATION.md
│   ├── ADMIN_PANEL_API.md
│   └── DEPLOYMENT_CHECKLIST.md
│
├── requirements.txt                     # Python dependencies
├── pyproject.toml                       # Project metadata
├── Dockerfile                           # Container image definition
├── docker-compose.yml                   # Multi-container setup
├── run_app.py                           # Application launcher
├── pytest.ini                           # Test configuration
└── README.md                            # This file
```

---

## Prerequisites

### System Requirements
- **OS:** Windows, macOS, or Linux
- **RAM:** 2GB minimum, 4GB+ recommended
- **Disk:** 1GB+ available space

### Software Requirements
- **Python:** 3.11 or higher
- **pip:** Python package manager
- **PostgreSQL:** 14 or higher
- **Git:** Version control (optional)

### Optional

- **Node.js:** 18+ (for Prisma tools)
- **Docker** & **Docker Compose:** For containerized setup
- **PostgreSQL Client:** `psql` command-line tool
- **Postman/Insomnia:** API testing tools
- **VS Code:** Recommended code editor

### Account Requirements
- **Razorpay Account:** For payment integration (sandbox credentials for testing)
- **Groq API Key:** For AI chatbot functionality

---

## Installation & Setup

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd nursery-backend
```

### Step 2: Create & Activate Virtual Environment

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

### Step 4: Setup Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit with your values
# nano .env  (or use your editor)
```

**Required environment variables:**

```env
# Application
APP_NAME="Nursery Backend"
ENVIRONMENT=dev
DEBUG=true

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/nursery_db

# JWT Configuration
JWT_SECRET_KEY=<generate-with-python-command>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Payment (Razorpay)
RAZORPAY_KEY_ID=rzp_test_xxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxx
RAZORPAY_WEBHOOK_SECRET=webhook_secret

# AI (Groq)
GROQ_API_KEY=gsk_xxxxxxxxxxxxx

# Admin Account
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=Admin@123456

# Optional: Rate limiting
RATE_LIMIT_ENABLED=true
```

**Generate JWT Secret Key:**

```bash
# Option 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: OpenSSL
openssl rand -hex 32
```

### Step 5: Initialize Database

```bash
# Create database (from PostgreSQL terminal)
createdb nursery_db

# Or from psql
psql -U postgres
CREATE DATABASE nursery_db;
\q

# Run application (it will auto-create tables)
python run_app.py
```

### Step 6: Create Admin Account (First Run)

The admin account is automatically created on first application startup:
- Email: value of `ADMIN_EMAIL` from .env
- Password: value of `ADMIN_PASSWORD` from .env

---

## Configuration

### Database Configuration

```python
# src/database.py
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/nursery_db"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,           # Set True for SQL logging
    pool_size=20,         # Connection pool size
    max_overflow=0,       # Max overflow connections
    pool_pre_ping=True    # Health check before use
)
```

### JWT Configuration

```python
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
```

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Config Files

Environment-specific configuration in JSON files:

```json
{
  "app_name": "Nursery Backend",
  "version": "1.0.0",
  "debug": false,
  "database": {
    "pool_size": 20
  },
  "jwt": {
    "expire_minutes": 30
  },
  "rate_limit": {
    "enabled": true,
    "requests": 1000,
    "window_seconds": 3600
  }
}
```

---

## Running the Application

### Development Mode

```bash
# Using run_app.py (recommended)
python run_app.py

# Using uvicorn directly with reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level info
```

### Production Mode

```bash
# Set environment
export ENVIRONMENT=production
export DEBUG=false

# Run with Gunicorn + Uvicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 --log-level info
```

### Access Points

Once running:

- **API:** `http://localhost:8000`
- **Swagger UI (Interactive Docs):** `http://localhost:8000/docs`
- **ReDoc (API Documentation):** `http://localhost:8000/redoc`
- **OpenAPI Schema:** `http://localhost:8000/openapi.json`
- **Health Check:** `http://localhost:8000/health`

---

## Docker Deployment

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Scale application
docker-compose up -d --scale app=3

# Stop all services
docker-compose down

# Remove volumes (reset database)
docker-compose down -v
```

### Using Docker Build

```bash
# Build image
docker build -t nursery-backend:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db" \
  -e JWT_SECRET_KEY="your-secret" \
  -e RAZORPAY_KEY_ID="..." \
  -e RAZORPAY_KEY_SECRET="..." \
  nursery-backend:latest
```

### Docker Compose Services

```yaml
Services:
  - FastAPI Application (Port 8000)
  - PostgreSQL Database (Port 5432)
  - (Optional) Redis Cache (Port 6379)
```

---

## Database

### Schema Overview

**Core Tables:**

- **users** - User accounts with roles (CUSTOMER, ADMIN)
- **refresh_tokens** - JWT refresh token tracking
- **categories** - Product categories with metadata
- **products** - Product catalog with detailed attributes
- **product_diseases** - Plant diseases and associations
- **product_inventory** - Stock levels and thresholds
- **carts** - Per-user shopping carts
- **cart_items** - Items in shopping carts
- **orders** - Customer orders with status
- **order_items** - Items in completed orders
- **payments** - Razorpay payment tracking
- **ai_chat_conversations** - Chatbot conversation history
- **ai_chat_messages** - Messages within conversations
- **admin_logs** - Admin activity audit trail

### Initialize Database

```bash
# Auto-initialization on app startup
python run_app.py

# The app creates tables from SQLAlchemy models automatically
```

### View Database

```bash
# Using psql
psql -U user -d nursery_db
\dt                      # List tables
\d users                 # Show table structure
SELECT * FROM users;     # Query data
```

---

## API Documentation

### Base URL

```
http://localhost:8000
```

### Authentication

Protected endpoints require JWT token in header:

```http
Authorization: Bearer <access_token>
```

### Response Format

All responses follow this format:

```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful"
}
```

---

## API Endpoints

### Authentication

**Register User**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe"
}

Response: 201 Created
{
  "id": "uuid",
  "email": "user@example.com",
  "access_token": "...",
  "refresh_token": "..."
}
```

**Login**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}

Response: 200 OK
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Refresh Token**
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "..."
}

Response: 200 OK
{
  "access_token": "...",
  "token_type": "bearer"
}
```

**Get Current User**
```http
GET /api/v1/auth/me
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "role": "CUSTOMER"
}
```

**Change Password**
```http
POST /api/v1/auth/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "old_password": "OldPass123",
  "new_password": "NewPass123"
}

Response: 200 OK
```

**Logout**
```http
POST /api/v1/auth/logout
Authorization: Bearer <token>
Content-Type: application/json

{
  "refresh_token": "..."
}

Response: 200 OK
```

---

### Products & Categories

**List Products**
```http
GET /api/v1/products?page=1&per_page=10&category_id=cat123&search=monstera

Response: 200 OK
{
  "products": [...],
  "total": 45,
  "page": 1,
  "per_page": 10
}
```

**Get Product Details**
```http
GET /api/v1/products/{product_id}

Response: 200 OK
{
  "id": "prod123",
  "name": "Monstera Deliciosa",
  "scientific_name": "Monstera deliciosa",
  "price": 499.99,
  "description": "...",
  "care_instructions": "...",
  "light_requirements": "Bright Indirect",
  "watering_frequency": "Weekly",
  "temperature_range": "18-24°C",
  "image_url": "...",
  "category": {...},
  "common_diseases": [...]
}
```

**List Categories**
```http
GET /api/v1/categories

Response: 200 OK
{
  "categories": [
    {
      "id": "cat1",
      "name": "Indoor Plants",
      "slug": "indoor-plants",
      "description": "...",
      "icon": "🌿"
    }
  ],
  "total": 5
}
```

---

### Shopping Cart

**Get Cart**
```http
GET /api/v1/cart
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "cart123",
  "user_id": "user456",
  "items": [
    {
      "id": "item1",
      "product_id": "prod123",
      "product_name": "Monstera",
      "quantity": 2,
      "price": 499.99,
      "subtotal": 999.98
    }
  ],
  "total": 999.98,
  "item_count": 2
}
```

**Add to Cart**
```http
POST /api/v1/cart/add
Authorization: Bearer <token>
Content-Type: application/json

{
  "product_id": "prod123",
  "quantity": 2
}

Response: 200 OK
{
  "id": "cart123",
  "items": [...],
  "total": 999.98
}
```

**Update Cart Item**
```http
PUT /api/v1/cart/items/{item_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "quantity": 3
}

Response: 200 OK
```

**Remove from Cart**
```http
DELETE /api/v1/cart/items/{item_id}
Authorization: Bearer <token>

Response: 200 OK
```

**Clear Cart**
```http
DELETE /api/v1/cart
Authorization: Bearer <token>

Response: 200 OK
```

---

### Orders

**Create Order**
```http
POST /api/v1/orders
Authorization: Bearer <token>
Content-Type: application/json

{
  "shipping_address": "123 Main St, City, State 12345",
  "notes": "Please deliver after 6 PM"
}

Response: 201 Created
{
  "id": "order123",
  "user_id": "user456",
  "status": "PENDING",
  "total_amount": 999.98,
  "items": [...],
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Get User Orders**
```http
GET /api/v1/orders?page=1&per_page=10
Authorization: Bearer <token>

Response: 200 OK
{
  "orders": [...],
  "total": 5,
  "page": 1
}
```

**Get Order Details**
```http
GET /api/v1/orders/{order_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "order123",
  "status": "CONFIRMED",
  "items": [...]
}
```

---

### Payments

**Create Payment Order**
```http
POST /api/v1/payments/create-order
Authorization: Bearer <token>
Content-Type: application/json

{
  "order_id": "order123",
  "amount": 999.98
}

Response: 200 OK
{
  "razorpay_order_id": "order_rzp123",
  "amount": 999.98,
  "currency": "INR",
  "status": "PENDING"
}
```

**Verify Payment**
```http
POST /api/v1/payments/verify
Authorization: Bearer <token>
Content-Type: application/json

{
  "razorpay_order_id": "order_rzp123",
  "razorpay_payment_id": "pay_xxxxx",
  "razorpay_signature": "signature_xxxxx"
}

Response: 200 OK
{
  "status": "CONFIRMED",
  "message": "Payment verified successfully"
}
```

---

### AI Chatbot

**Send Message**
```http
POST /api/v1/ai/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "How often should I water my monstera?",
  "conversation_id": null
}

Response: 200 OK
{
  "conversation_id": "conv123",
  "message_id": "msg456",
  "response": "Monstera plants prefer...",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Get Conversations**
```http
GET /api/v1/ai/conversations?limit=50
Authorization: Bearer <token>

Response: 200 OK
{
  "conversations": [
    {
      "id": "conv123",
      "created_at": "2024-01-15T10:30:00Z",
      "message_count": 5
    }
  ]
}
```

**Get Conversation Details**
```http
GET /api/v1/ai/conversations/{conversation_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "conv123",
  "messages": [
    {
      "id": "msg1",
      "role": "user",
      "content": "...",
      "created_at": "..."
    },
    {
      "id": "msg2",
      "role": "assistant",
      "content": "...",
      "created_at": "..."
    }
  ]
}
```

**Delete Conversation**
```http
DELETE /api/v1/ai/conversations/{conversation_id}
Authorization: Bearer <token>

Response: 200 OK
```

---

### Admin Dashboard

**Get Dashboard Statistics**
```http
GET /api/v1/admin/dashboard/statistics
Authorization: Bearer <admin_token>

Response: 200 OK
{
  "total_users": 150,
  "active_users": 95,
  "total_orders": 380,
  "pending_orders": 12,
  "total_revenue": 95000.00,
  "average_order_value": 250.00
}
```

**Get Activity Logs**
```http
GET /api/v1/admin/dashboard/activity-logs?page=1&per_page=20
Authorization: Bearer <admin_token>

Response: 200 OK
{
  "logs": [
    {
      "id": "log123",
      "admin_id": "admin1",
      "action_type": "product_update",
      "resource_id": "prod456",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 450
}
```

---

### Admin User Management

**List Users**
```http
GET /api/v1/admin/users?page=1&per_page=20&search=john&role=CUSTOMER
Authorization: Bearer <admin_token>

Response: 200 OK
{
  "users": [
    {
      "id": "user123",
      "email": "john@example.com",
      "first_name": "John",
      "role": "CUSTOMER",
      "is_active": true,
      "created_at": "2024-01-10T..."
    }
  ],
  "total": 150
}
```

**Get User Details**
```http
GET /api/v1/admin/users/{user_id}
Authorization: Bearer <admin_token>

Response: 200 OK
{
  "id": "user123",
  "email": "john@example.com",
  "profile": {...},
  "orders": 5,
  "total_spent": 2500.00
}
```

**Update User Status**
```http
PUT /api/v1/admin/users/{user_id}/status
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "is_active": false
}

Response: 200 OK
```

---

### Admin Order Management

**List Orders**
```http
GET /api/v1/admin/orders?page=1&status=PENDING&payment_status=CONFIRMED
Authorization: Bearer <admin_token>

Response: 200 OK
{
  "orders": [
    {
      "id": "order123",
      "user_id": "user456",
      "status": "PENDING",
      "payment_status": "CONFIRMED",
      "total_amount": 999.98,
      "created_at": "..."
    }
  ],
  "total": 45
}
```

**Update Order Status**
```http
PUT /api/v1/admin/orders/{order_id}/status
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "status": "CONFIRMED"
}

Response: 200 OK
```

---

### Admin Product Management

**Create Product**
```http
POST /api/v1/admin/products
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "New Plant",
  "scientific_name": "Plant scientificus",
  "category_id": "cat123",
  "price": 299.99,
  "cost_price": 150.00,
  "image_url": "https://...",
  "description": "...",
  "care_instructions": "...",
  "light_requirements": "Bright Indirect",
  "watering_frequency": "Weekly",
  "temperature_range": "18-24°C"
}

Response: 201 Created
```

**Update Product**
```http
PUT /api/v1/admin/products/{product_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "price": 349.99,
  "description": "Updated description"
}

Response: 200 OK
```

**Delete Product**
```http
DELETE /api/v1/admin/products/{product_id}
Authorization: Bearer <admin_token>

Response: 200 OK
```

**Activate/Deactivate Product**
```http
POST /api/v1/admin/products/{product_id}/activate
Authorization: Bearer <admin_token>

Response: 200 OK
```

---

### Admin Category Management

**List Categories**
```http
GET /api/v1/admin/categories?page=1&per_page=20
Authorization: Bearer <admin_token>

Response: 200 OK
{
  "categories": [...],
  "total": 8
}
```

**Create Category**
```http
POST /api/v1/admin/categories
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Outdoor Plants",
  "slug": "outdoor-plants",
  "description": "...",
  "icon": "🌳"
}

Response: 201 Created
```

**Update Category**
```http
PUT /api/v1/admin/categories/{category_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Updated Name",
  "icon": "🌿"
}

Response: 200 OK
```

---

### Admin Inventory Management

**List Inventory**
```http
GET /api/v1/admin/inventory?page=1&low_stock_only=false
Authorization: Bearer <admin_token>

Response: 200 OK
{
  "inventory": [
    {
      "product_id": "prod123",
      "product_name": "Monstera",
      "quantity": 45,
      "low_stock_threshold": 10,
      "is_low_stock": false
    }
  ],
  "total": 50
}
```

**Adjust Stock**
```http
POST /api/v1/admin/inventory/{product_id}/adjust
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "quantity_change": -5,
  "reason": "Damaged items"
}

Response: 200 OK
```

---

## Data Models

### User Model

```python
class User(Base):
    id: str                  # UUID
    email: str              # Unique
    phone: str | None
    password_hash: str
    first_name: str | None
    last_name: str | None
    role: UserRoleEnum      # CUSTOMER | ADMIN
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    Relationships:
    - refresh_tokens: List[RefreshToken]
    - cart: Cart
    - orders: List[Order]
    - payments: List[Payment]
```

### Product Model

```python
class Product(Base):
    id: str
    name: str
    scientific_name: str | None
    slug: str               # Unique
    category_id: str
    price: float
    cost_price: float | None
    image_url: str
    description: str
    care_instructions: str
    light_requirements: str
    watering_frequency: str
    temperature_range: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### Order Model

```python
class Order(Base):
    id: str
    user_id: str
    status: OrderStatusEnum    # PENDING | CONFIRMED | SHIPPED | DELIVERED
    payment_status: PaymentStatusEnum
    payment_id: str | None
    total_amount: float
    shipping_address: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    
    Relationships:
    - user: User
    - items: List[OrderItem]
    - payment: Payment
```

### Cart Model

```python
class Cart(Base):
    id: str
    user_id: str            # Unique
    created_at: datetime
    updated_at: datetime
    
    Relationships:
    - user: User
    - items: List[CartItem]
```

### Payment Model

```python
class Payment(Base):
    id: str
    order_id: str           # Unique
    user_id: str
    razorpay_order_id: str | None
    razorpay_payment_id: str | None
    razorpay_signature: str | None
    amount: float
    currency: str           # Default: "INR"
    status: PaymentStatusEnum
    error_message: str | None
    created_at: datetime
    updated_at: datetime
```

### AI Chat Model

```python
class AIChatConversation(Base):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    Relationships:
    - messages: List[AIChatMessage]

class AIChatMessage(Base):
    id: str
    conversation_id: str
    role: str               # "user" | "assistant"
    content: str
    created_at: datetime
```

---

## Authentication & Security

### JWT Authentication

The application uses JWT (JSON Web Tokens) for stateless authentication:

1. **Token Generation**: Upon login/registration
   - Access token (short-lived, 30 minutes default)
   - Refresh token (long-lived, 7 days default)

2. **Token Storage**: Refresh tokens stored in database with:
   - Hash verification
   - Expiration tracking
   - Revocation capability

3. **Token Verification**: 
   - Signature validation using `JWT_SECRET_KEY`
   - Expiration time checking
   - User role verification for admin endpoints

### Password Security

- **Hashing Algorithm**: bcrypt with configurable iterations
- **Storage**: Password hashes only (never plain text)
- **Validation**: Minimum 8 characters with mixed case and digits

### Rate Limiting

Prevents API abuse with configurable limits:

```python
# Example: 100 requests per 60 seconds per IP
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW_SECONDS = 60
```

### CORS Configuration

```python
allow_origins = ["*"]           # Configure for specific domains
allow_methods = ["GET", "POST", "PUT", "DELETE"]
allow_headers = ["Authorization", "Content-Type"]
```

### Admin Authorization

- Only users with `role=ADMIN` can access admin endpoints
- Automatic role verification in middleware
- Activity logging for all admin actions

---

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest src/tests/test_auth.py

# With coverage
pytest --cov=src --cov-report=html

# Verbose output
pytest -v

# Specific test marker
pytest -m unit
pytest -m integration
```

### Test Configuration

See `pytest.ini`:

```ini
[pytest]
testpaths = src/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
```

### Sample Test Files

- `test_register.py` - User registration tests
- `test_models.py` - ORM model tests
- `test_api.py` - API endpoint tests

---

## Development Guide

### Code Style

- **PEP 8** compliance
- **Type hints** for all functions
- **Docstrings** for public APIs
- **Class-based services** for organization

### Adding New Features

1. **Define Models** (`src/models/`)
   - Add SQLAlchemy model
   - Include relationships

2. **Create Data Contracts** (`src/data_contracts/`)
   - Request validation
   - Response serialization

3. **Implement Service** (`src/services/`)
   - Business logic
   - Database operations

4. **Build Controller** (`src/controllers/`)
   - Route handlers
   - Parameter validation
   - Error handling

5. **Write Tests** (`src/tests/`)
   - Unit tests
   - Integration tests

6. **Update Documentation** (README, etc.)

### Common Patterns

**Service Method**
```python
async def get_user(self, session, user_id: str) -> User:
    """Retrieve user by ID"""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalars().first()
```

**Controller Endpoint**
```python
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    session: AsyncSession = Depends(get_session)
):
    try:
        user = await user_service.get_user(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(**user.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Troubleshooting

### Database Connection Error

**Error**: `sqlalchemy.exc.OperationalError`

**Solutions**:
```bash
# Verify PostgreSQL is running
psql -U user -h localhost

# Check DATABASE_URL in .env
# Verify credentials: host, port, database name

# Test connection
python -c "
import asyncio
from src.database import health_check
asyncio.run(health_check())
"
```

### JWT Token Invalid

**Error**: `Invalid token` or `Token expired`

**Solutions**:
```bash
# Generate new JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update JWT_SECRET_KEY in .env
# Restart application
# Clear browser cookies/tokens
```

### Port Already in Use

**Error**: `Address already in use [:8000]`

**Solutions**:
```bash
# Find process using port
lsof -i :8000              # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>              # macOS/Linux
taskkill /PID <PID> /F     # Windows

# Use different port
python run_app.py --port 8001
```

### Module Not Found

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solutions**:
```bash
# Activate virtual environment
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Async Error

**Error**: `RuntimeError: Event loop is closed`

**Solutions**:
```bash
# Ensure asyncio_mode = auto in pytest.ini
# Use pytest-asyncio plugin
pip install pytest-asyncio
```

### Razorpay integration issues

**Error**: `Razorpay API error`

**Solutions**:
```bash
# Verify credentials in .env
RAZORPAY_KEY_ID=rzp_test_xxxxx  # Should start with rzp_test_
RAZORPAY_KEY_SECRET=xxxxx

# Use sandbox API for testing
# Check payment status in Razorpay dashboard
```

### AI Chatbot errors

**Error**: `Groq API error`

**Solutions**:
```bash
# Verify API key
GROQ_API_KEY=gsk_xxxxxxxxxxxxx

# Check API quota/rate limits
# Verify model availability (e.g., "mixtral-8x7b-32768")
```

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async Guide](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic V2 Docs](https://docs.pydantic.dev/latest/)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [Razorpay API Docs](https://razorpay.com/docs/api/)
- [Groq API Documentation](https://groq.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

### Related Documentation Files

- [PHASE_2A_BACKEND_FOUNDATION.md](docs/PHASE_2A_BACKEND_FOUNDATION.md) - Detailed implementation guide
- [ADMIN_PANEL_API.md](docs/ADMIN_PANEL_API.md) - Admin API specifications
- [DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md) - Deployment preparation

---

## License

This project is licensed under the MIT License.

---

## Support & Contact

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check existing issues in repository
4. Create a new issue with detailed description

---

**Last Updated:** January 2026  
**Status:** Production Ready ✅

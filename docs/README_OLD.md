# 🌱 Nursery Backend - E-Commerce API

A production-ready **FastAPI** backend for a nursery/plant e-commerce platform with comprehensive product management, shopping cart, order processing, payment integration, AI plant care chatbot, and advanced admin dashboard.

**Status:** 🚀 Phase 2A+ (Cart, Orders, AI, Admin)  
**Version:** 1.0.0  
**Python:** 3.11+  
**License:** MIT

---

## 📖 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Docker Deployment](#docker-deployment)
- [Database Setup](#database-setup)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Testing](#testing)
- [Development Guide](#development-guide)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Overview

**Nursery Backend** is a comprehensive REST API built with FastAPI and PostgreSQL for managing a plant/nursery e-commerce platform. It features modern architecture with layered services, JWT authentication, Razorpay payment integration, and an AI-powered plant care chatbot using Groq.

### Core Capabilities

- 🔐 **Authentication & Authorization** - JWT-based with refresh tokens and role-based access control (RBAC)
- 🛍️ **Product Ecosystem** - Catalog with categories, plant-specific metadata, disease tracking
- 🛒 **Shopping Experience** - Persistent user carts with real-time quantity management
- 📦 **Order Management** - Full lifecycle from cart to delivery with status tracking
- 💳 **Payment Processing** - Razorpay integration with webhook verification
- 🤖 **AI Chatbot** - Groq-powered plant care assistant with conversation history
- 👨‍💼 **Admin Suite** - Dashboard with metrics, activity logs, user/order/product management
- 🔄 **Scalability** - Async database operations, connection pooling, optimized queries
- 🔒 **Security** - Rate limiting, input validation, CORS, activity audit trails

---

## Key Features

### Authentication & User Management
- User registration with email validation
- Secure login with JWT access tokens and refresh tokens
- Password changing with validation
- User role management (CUSTOMER, ADMIN)
- Account activation/deactivation
- Automatic admin account initialization on first startup

### Product Catalog
- CRUD operations for products (admin only)
- Product categories with organizing capabilities
- Plant-specific metadata:
  - Care instructions
  - Light requirements (Low, Medium, High, Full Sun)
  - Watering frequency (Daily, Weekly, Bi-weekly, Monthly)
  - Temperature ranges
  - Scientific names
- Disease tracking with product relationships
- Product inventory management with low-stock alerts
- Search and filter by category, name, price range
- Pagination support for large datasets

### Shopping Cart
- Persistent per-user shopping carts
- Add/remove products with quantity management
- Real-time cart updates
- Cart total calculations
- Automatic cart cleanup on order creation

### Order Management
- Create orders from cart contents
- Order status workflow: PENDING → CONFIRMED → SHIPPED → DELIVERED
- Shipping address and delivery notes
- Order item tracking with pricing snapshots
- Order history per user
- Admin order management with status updates
- Order filtering by status and user

### Payment Processing
- Razorpay payment gateway integration
- Create payment orders with Razorpay
- Payment verification with signature validation
- Payment status tracking: PENDING → CONFIRMED → FAILED
- Webhook support for payment status updates
- Demo/test mode for development
- Complete transaction audit trail
- Automatic payment order linking

### Admin Dashboard
- **Statistics Dashboard** - Real-time metrics:
  - Total users, active users, pending users
  - Total orders, pending orders, completed orders
  - Total revenue and average order value
  - Product inventory status
  
- **User Management** - List/search users with filtering by:
  - Name, email, phone
  - Role and activation status
  - Created date range
  
- **Order Management** - Track orders with:
  - Status filtering (PENDING, CONFIRMED, SHIPPED, DELIVERED)
  - Payment status tracking
  - User-based filtering
  - Date range queries
  - Status updates
  
- **Inventory Management** - Monitor stock with:
  - Low-stock alerts (configurable threshold)
  - Quantity adjustments
  - Stock history tracking
  - Per-product stock levels
  
- **Category Management** - Manage product categories:
  - Create/edit categories with icons
  - Bulk operations
  - Product count per category
  
- **Activity Logging** - Audit trail with:
  - Admin action tracking
  - Timestamp and actor information
  - Previous/new value comparisons
  - Filterable by admin, action type, date

### AI Plant Care Assistant
- Groq-powered conversational AI specialized in plant care advice
- Conversation management with history storage
- Create new conversations or continue existing ones
- Message-level tracking with timestamps
- Retrieve conversation history
- Delete conversations
- Real-time response streaming capability

### Performance & Security
- **Async Operations** - Non-blocking database queries for improved throughput
- **Connection Pooling** - SQLAlchemy connection pool (20 connections, 0 overflow)
- **Health Checks** - Pre-ping health verification
- **Rate Limiting** - Configurable per-endpoint limits
- **CORS Support** - Cross-origin requests from multiple origins
- **Input Validation** - Pydantic v2 for request/response contracts
- **Error Handling** - Global exception handlers with meaningful error messages
- **Logging** - Comprehensive application and request logging
- **Password Security** - bcrypt hashing with passlib

---

## 🛠️ Tech Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|
| **Framework** | FastAPI | 0.109.0 |
| **Server** | Uvicorn | 0.27.0 |
| **ORM** | Prisma | 0.13.0 |
| **Database** | MySQL | 8.0+ |
| **Cache** | Redis | 7+ |
| **Authentication** | JWT (PyJWT) | 3.3.0 |
| **Password Hashing** | bcrypt | 1.7.4 |
| **Validation** | Pydantic | 2.5.3 |
| **Payment Gateway** | Razorpay | 1.4.1 |
| **Testing** | pytest | 7.4.3 |
| **Containerization** | Docker | Latest |

---

## 📋 Prerequisites

Ensure you have the following installed on your system:

### Minimum Requirements
- **Python** 3.11 or higher
- **pip** (Python package manager)
- **MySQL** 8.0 or higher
- **Node.js** 18+ (for Prisma CLI)

### Optional but Recommended
- **Redis** 7+ (for caching feature)
- **Docker** & **Docker Compose** (for containerized setup)
- **Git** (for version control)

### System Requirements
- **RAM:** Minimum 2GB, Recommended 4GB+
- **Disk Space:** Minimum 1GB
- **OS:** Windows, macOS, or Linux

---

## 🚀 Quick Start

### For the Impatient (Using Docker)

```bash
# Clone repository
git clone <repository-url>
cd nursery-backend

# Copy environment file
cp .env.example .env

# Start all services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f app

# API will be available at http://localhost:8000
```

### For Local Development

```bash
# Clone repository
git clone <repository-url>
cd nursery-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your database credentials

# Initialize database
python scripts/setup_db.py

# Seed sample data (optional)
python scripts/seed_db.py

# Run the application
python run_app.py

# API will be available at http://localhost:8000
```

---

## 💾 Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd nursery-backend
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Generate Prisma client
prisma generate
```

### Step 4: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
# nano .env  (or use your favorite editor)
```

**Key configurations to set:**
```env
DATABASE_URL=mysql://root:password@127.0.0.1:3306/nursery_db
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_SECRET_KEY=<your-secure-random-key>
RAZORPAY_KEY_ID=<your-razorpay-key>
RAZORPAY_KEY_SECRET=<your-razorpay-secret>
```

### Step 5: Initialize Database

```bash
# Create database schema
python scripts/setup_db.py

# Expected output:
# ✓ Connected to MySQL database
# ✓ Tables created successfully
# ✅ Database initialized
```

### Step 6: (Optional) Seed Initial Data

```bash
# Populate with sample categories and products
python scripts/seed_db.py

# Expected output:
# ✅ Connected to database
# ✅ Categories created
# ✅ Products created
# ✅ Database seeded successfully
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Application Settings
APP_NAME=FastAPI Auth Service
APP_VERSION=1.0.0
ENVIRONMENT=dev                    # dev, qa, or production
DEBUG=True                         # Set to False in production

# Server Settings
HOST=0.0.0.0
PORT=8000

# Database Configuration
DATABASE_URL=mysql://root:password@127.0.0.1:3306/nursery_db

# JWT Securities
JWT_SECRET_KEY=<generate-strong-random-string>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis Configuration (Optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_ENABLED=False                # Set to True to enable caching

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100            # requests per window
RATE_LIMIT_WINDOW_SECONDS=60       # time window in seconds

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Admin Account (auto-created on first run)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=Admin@123
ADMIN_FIRST_NAME=Admin
ADMIN_LAST_NAME=User

# Payment Gateway (Razorpay)
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxx
RAZORPAY_WEBHOOK_SECRET=webhook_secret

# Demo Mode (auto-approve all payments for testing)
DEMO_MODE=true
```

### Config Files

The application uses config files for environment-specific settings:

- `config/dev_app_config.json` - Development configuration
- `config/qa_app_config.json` - QA configuration
- `config/prod_app_config.json` - Production configuration

---

## 🏃 Running the Application

### Development Mode

```bash
# Using run_app.py (recommended for development)
python run_app.py

# Output:
# 🚀 Starting FastAPI Auth Service...
# ✅ All services connected successfully
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Press CTRL+C to quit
```

### With Automatic Reload

```bash
# Using uvicorn directly with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level info
```

### Production Mode

```bash
# Using Gunicorn with Uvicorn workers
export ENVIRONMENT=production
export DEBUG=False
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --log-level info
```

### Access the Application

Once running, access:

- **🔗 API Base URL:** `http://localhost:8000`
- **📖 Interactive API Docs (Swagger UI):** `http://localhost:8000/docs`
- **📍 Alternative API Docs (ReDoc):** `http://localhost:8000/redoc`
- **📝 OpenAPI Schema:** `http://localhost:8000/openapi.json`

---

## 🐳 Docker Setup

### Using Docker Compose (Recommended)

The project includes a complete `docker-compose.yml` with MySQL, Redis, and the FastAPI application.

#### Start All Services

```bash
# Build and start containers
docker-compose up -d

# Expected output:
# Creating auth_mysql ... done
# Creating auth_redis ... done
# Creating auth_app ... done
```

#### View Logs

```bash
# View real-time application logs
docker-compose logs -f app

# View MySQL logs
docker-compose logs -f mysql

# View Redis logs
docker-compose logs -f redis
```

#### Stop Services

```bash
# Stop all running containers
docker-compose down

# Stop and remove volumes (resets database)
docker-compose down -v
```

#### Rebuild Containers

```bash
# Rebuild if you've changed dependencies
docker-compose up -d --build
```

### Docker Compose Configuration

The `docker-compose.yml` provides:

```yaml
Services:
  - MySQL 8.0 (Database)
    - Port: 3306
    - Default Database: auth_db
    - Credentials: root/root
  
  - Redis 7 (Cache)
    - Port: 6379
    - Persistence: Enabled
  
  - FastAPI Application
    - Port: 8000
    - Reload: Enabled for development
    - Auto-depends on MySQL and Redis health
```

### Build Custom Docker Image

```bash
# Build image
docker build -t nursery-backend:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="mysql://root:password@host:3306/nursery_db" \
  nursery-backend:latest
```

---

## 📊 Database Setup

### Database Schema Overview

The application uses Prisma ORM with the following main tables:

```sql
Tables:
  ├── users              - User accounts and authentication
  ├── categories         - Product categories
  ├── products           - Product catalog
  ├── product_diseases   - Plant disease information
  ├── cart              - User shopping carts
  ├── cart_items        - Items in shopping cart
  ├── orders            - Customer orders
  ├── order_items       - Items in orders
  └── refresh_tokens    - JWT refresh token tracking
```

### Initialize Database Manually

```bash
# Using the provided setup script
python scripts/setup_db.py

# Tables created:
# ✓ users
# ✓ categories
# ✓ products
# ✓ product_diseases
# ✓ cart
# ✓ cart_items
# ✓ orders
# ✓ order_items
# ✓ refresh_tokens
```

### Using Prisma Directly

```bash
# Generate Prisma client
prisma generate

# Migrate database
prisma migrate dev --name init

# View database in Prisma Studio
prisma studio
```

### Seed Sample Data

```bash
# Populate with sample categories and products
python scripts/seed_db.py

# Creates:
# - 5 product categories
# - 10+ sample products
# - Category icons and descriptions
```

---

## 🏗️ Project Architecture

### Directory Structure

```
nursery-backend/
├── src/                          # Main application source
│   ├── __init__.py
│   ├── main.py                  # Application entry point & route setup
│   │
│   ├── controllers/             # HTTP request handlers
│   │   ├── auth_controller.py
│   │   ├── product_controller.py
│   │   ├── cart_controller.py
│   │   ├── order_controller.py
│   │   ├── payment_controller.py
│   │   ├── admin_user_controller.py
│   │   ├── admin_order_controller.py
│   │   ├── admin_dashboard_controller.py
│   │   └── admin_inventory_controller.py
│   │
│   ├── services/                # Business logic layer
│   │   ├── auth_service.py
│   │   ├── product_service.py
│   │   ├── cart_service.py
│   │   ├── order_service.py
│   │   ├── payment_service.py
│   │   ├── admin_service.py
│   │   └── analytics_service.py
│   │
│   ├── core/                    # Core functionality modules
│   │   ├── auth_core.py
│   │   ├── cart_core.py
│   │   ├── order_core.py
│   │   ├── payment_core.py
│   │   └── product_core.py
│   │
│   ├── data_contracts/          # Request/Response models (Pydantic)
│   │   ├── api_request_response.py
│   │   └── admin_request_response.py
│   │
│   ├── middlewares/             # Custom middleware
│   │   └── auth_middleware.py   # JWT verification & authorization
│   │
│   ├── plugins/                 # External service integrations
│   │   └── database.py          # Prisma database connection
│   │
│   ├── utilities/               # Helper utilities
│   │   ├── config_manager.py    # Configuration loading
│   │   ├── cache_manager.py     # Redis caching
│   │   ├── security.py          # Password hashing & JWT utilities
│   │   ├── rate_limiter.py      # Rate limiting
│   │   ├── admin_init.py        # Admin initialization
│   │   └── admin_setup.py       # Admin setup utilities
│   │
│   └── tests/                   # Test suites
│       ├── unit/                # Unit tests
│       └── integration/         # Integration tests
│
├── scripts/                      # Utility scripts
│   ├── setup_db.py             # Initialize database schema
│   ├── seed_db.py              # Seed sample data
│   └── init_db.py              # Database initialization utilities
│
├── config/                       # Environment configurations
│   ├── dev_app_config.json
│   ├── qa_app_config.json
│   └── prod_app_config.json
│
├── prisma/                       # Database schema
│   ├── schema.prisma           # Prisma ORM schema
│   └── add_cart_orders.sql     # Additional SQL migrations
│
├── sample_requests/             # API request examples
│   ├── api_requests.http       # Regular API requests
│   └── admin_requests.http     # Admin API requests
│
├── docker-compose.yml           # Docker Compose configuration
├── Dockerfile                   # Docker image definition
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── run_app.py                   # Application runner
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

### Architecture Pattern: MVC + Services

The application follows a **Model-View-Controller** pattern with a **Services layer**:

```
HTTP Request
    ↓
Controllers (route handlers)
    ↓
Services (business logic)
    ↓
Core (core functionality)
    ↓
Prisma ORM (database layer)
    ↓
MySQL Database
```

**Layer Responsibilities:**

- **Controllers:** Handle HTTP requests/responses, input validation, authentication
- **Services:** Implement business logic, data transformation, service orchestration
- **Core:** Core domain functionality, algorithms, calculations
- **Data Contracts:** Pydantic models for request/response validation
- **Middleware:** Cross-cutting concerns (auth, rate limiting, CORS)
- **Utilities:** Reusable helper functions (caching, security, configuration)

---

## 📚 API Documentation

### Base URL

```
http://localhost:8000
```

### Interactive API Documentation

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Authentication

All protected endpoints require JWT token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

### API Endpoints Summary

#### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get tokens |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Logout user |
| PUT | `/auth/change-password` | Change password |

#### Products (`/api/v1/products`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | List all products with pagination |
| GET | `/products/{id}` | Get product details |
| GET | `/products/category/{category_id}` | Get products by category |
| GET | `/categories` | List all categories |

#### Cart (`/api/v1/cart`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cart` | Get user's shopping cart |
| POST | `/cart/add` | Add product to cart |
| PUT | `/cart/update/{item_id}` | Update cart item quantity |
| DELETE | `/cart/remove/{item_id}` | Remove item from cart |
| DELETE | `/cart/clear` | Clear entire cart |

#### Orders (`/api/v1/orders`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders` | Create order from cart |
| GET | `/orders` | Get user's orders |
| GET | `/orders/{id}` | Get order details |
| PUT | `/orders/{id}/cancel` | Cancel order |

#### Payments (`/api/v1/payments`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/payments/create-order` | Create Razorpay order |
| POST | `/payments/verify` | Verify payment |
| POST | `/webhooks/razorpay` | Razorpay webhook |

#### Admin Dashboard (`/api/v1/admin`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/dashboard/statistics` | Dashboard statistics |
| GET | `/admin/users` | List users |
| GET | `/admin/users/{id}` | Get user details |
| PUT | `/admin/users/{id}/status` | Update user status |
| GET | `/admin/orders` | List orders |
| POST | `/admin/products` | Create product |
| GET | `/admin/categories` | List categories |
| GET | `/admin/dashboard/activity-logs` | View activity logs |

### Example Requests

See [sample_requests/api_requests.http](sample_requests/api_requests.http) for complete request examples.

**Register User:**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Login:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Add to Cart:**
```http
POST /api/v1/cart/add
Authorization: Bearer <token>
Content-Type: application/json

{
  "product_id": "product-123",
  "quantity": 2
}
```

**Create Order:**
```http
POST /api/v1/orders
Authorization: Bearer <token>
Content-Type: application/json

{
  "shipping_address": "123 Main St, City, State 12345"
}
```

---

## 🔐 Environment Variables

### Required Variables

| Variable | Description | Example | Required |
|----------|-----------|---------|----------|
| `DATABASE_URL` | MySQL database connection string | `mysql://root:pass@localhost:3306/nursery_db` | ✅ |
| `JWT_SECRET_KEY` | Secret key for JWT signing | `your-secure-random-key` | ✅ |
| `RAZORPAY_KEY_ID` | Razorpay API key ID | `rzp_test_xxxx` | ✅ |
| `RAZORPAY_KEY_SECRET` | Razorpay API secret | `xxxxx` | ✅ |

### Optional Variables

| Variable | Description | Default | Optional |
|----------|-----------|---------|----------|
| `ENVIRONMENT` | Environment mode | `dev` | ✅ |
| `DEBUG` | Enable debug mode | `True` | ✅ |
| `PORT` | Server port | `8000` | ✅ |
| `HOST` | Server host | `0.0.0.0` | ✅ |
| `REDIS_ENABLED` | Enable Redis caching | `False` | ✅ |
| `REDIS_HOST` | Redis server host | `localhost` | ✅ |
| `REDIS_PORT` | Redis server port | `6379` | ✅ |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | `True` | ✅ |
| `RATE_LIMIT_REQUESTS` | Max requests per window | `100` | ✅ |
| `RATE_LIMIT_WINDOW_SECONDS` | Rate limit window | `60` | ✅ |

### Generate JWT Secret Key

```bash
# Option 1: Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: Using OpenSSL
openssl rand -hex 32
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Test Configuration

Test configuration is in `pytest.ini`:
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
- `test_phase1_api.py` - Phase 1 API tests
- `test_prisma_models.py` - Prisma model tests
- `quick_test.py` - Quick smoke tests

---

## 👨‍💻 Development Guide

### Code Structure Guidelines

1. **Controllers:** Handle HTTP layer
   - Validate input using Pydantic models
   - Call services for business logic
   - Format and return responses

2. **Services:** Implement business logic
   - Orchestrate multiple operations
   - Perform data transformations
   - Call core functions

3. **Core:** Domain-specific logic
   - Pure functions when possible
   - No side effects
   - Reusable algorithms

### Adding New Features

#### Example: Adding a New Product Attribute

1. **Update Database Schema** (`prisma/schema.prisma`)
   ```prisma
   model Product {
     // ... existing fields ...
     newAttribute String?
   }
   ```

2. **Update Request/Response Models** (`data_contracts/`)
   ```python
   class ProductResponse(BaseModel):
       # ... existing fields ...
       new_attribute: Optional[str] = None
   ```

3. **Update Services/Controllers**
   - Add logic to handle new attribute
   - Update controllers to accept/return new field

4. **Add Tests** (`src/tests/`)
   - Unit tests for business logic
   - Integration tests for API endpoints

### Code Style

- **Formatting:** Follow PEP 8
- **Type Hints:** Use type hints throughout
- **Docstrings:** Document all public functions
- **Comments:** Explain complex logic

```python
def process_payment(order_id: str, amount: float) -> PaymentResult:
    """
    Process payment for an order using Razorpay.
    
    Args:
        order_id: The order identifier
        amount: Payment amount in rupees
        
    Returns:
        PaymentResult with transaction details
        
    Raises:
        PaymentError: If payment processing fails
    """
    # Implementation here
    pass
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: Add new feature"

# Push and create pull request
git push origin feature/new-feature
```

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. Database Connection Error

**Error:** `sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError)`

**Solution:**
```bash
# Check MySQL is running
# Verify DATABASE_URL in .env
# Check credentials and host

# Test connection
mysql -h 127.0.0.1 -u root -p
```

#### 2. JWT Token Invalid

**Error:** `Invalid token` or `Token expired`

**Solution:**
```bash
# Generate new JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update JWT_SECRET_KEY in .env
# Restart application
```

#### 3. Redis Connection Failed

**Error:** `ConnectionError: Error 111 connecting to redis`

**Solution:**
```bash
# Check Redis is running
redis-cli ping

# If using Docker
docker-compose logs redis

# Set REDIS_ENABLED=False to disable caching
```

#### 4. Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Change port in .env or CLI
python run_app.py --port 8001
```

#### 5. Module Not Found

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt

# Verify Prisma client
prisma generate
```

#### 6. Database Schema Not Found

**Error:** `ProgrammingError: Table doesn't exist`

**Solution:**
```bash
# Run database initialization
python scripts/setup_db.py

# Verify all tables created
mysql -h 127.0.0.1 -u root -p nursery_db
SHOW TABLES;
```

### Debug Mode

Enable detailed logging:

```bash
# Set DEBUG=True in .env
DEBUG=True

# Run with verbose logging
python run_app.py --log-level debug
```

### Getting Help

1. **Check logs:** `docker-compose logs -f app`
2. **Review documentation:** See [PHASE_2A_BACKEND_FOUNDATION.md](PHASE_2A_BACKEND_FOUNDATION.md)
3. **Check admin API docs:** See [ADMIN_PANEL_API.md](ADMIN_PANEL_API.md)
4. **View API examples:** See [sample_requests/](sample_requests/)

---

## 📝 Additional Documentation

- [Phase 2A Backend Implementation](PHASE_2A_BACKEND_FOUNDATION.md) - Detailed backend development guide
- [Admin Panel API](ADMIN_PANEL_API.md) - Complete admin endpoint documentation
- [API Request Examples](sample_requests/api_requests.http) - Sample HTTP requests

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Contributors

- Backend Team

---

## 🔗 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Prisma Documentation](https://www.prisma.io/docs/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [JWT Authentication](https://pyjwt.readthedocs.io/)
- [Razorpay API Documentation](https://razorpay.com/docs/api/)

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 API Endpoints

### Authentication

| Method | Endpoint                       | Description          | Auth Required |
| ------ | ------------------------------ | -------------------- | ------------- |
| POST   | `/api/v1/auth/register`        | Register new user    | No            |
| POST   | `/api/v1/auth/login`           | Login user           | No            |
| POST   | `/api/v1/auth/refresh`         | Refresh access token | No            |
| POST   | `/api/v1/auth/logout`          | Logout user          | Yes           |
| GET    | `/api/v1/auth/me`              | Get current user     | Yes           |
| POST   | `/api/v1/auth/change-password` | Change password      | Yes           |

### Products (Phase 1)

| Method | Endpoint                       | Description                                    | Auth Required |
| ------ | ------------------------------ | ---------------------------------------------- | ------------- |
| GET    | `/api/v1/products`             | List products with pagination & filtering      | No            |
| GET    | `/api/v1/products/{id}`        | Get product details with diseases array        | No            |
| GET    | `/api/v1/categories`           | List all product categories                    | No            |

### Admin Panel (Phase 2) 🔐

**Admin panel endpoints require admin authentication**

#### User Management
| Method | Endpoint                             | Description              | Auth Required |
| ------ | ------------------------------------ | ------------------------ | ------------- |
| GET    | `/api/v1/admin/users`                | List all users           | Admin         |
| GET    | `/api/v1/admin/users/{user_id}`      | Get user details         | Admin         |
| PUT    | `/api/v1/admin/users/{user_id}/status` | Activate/suspend user  | Admin         |
| PUT    | `/api/v1/admin/users/{user_id}/role`   | Change user role       | Super Admin   |
| DELETE | `/api/v1/admin/users/{user_id}`      | Delete user (soft)       | Super Admin   |

#### Order Management
| Method | Endpoint                             | Description              | Auth Required |
| ------ | ------------------------------------ | ------------------------ | ------------- |
| GET    | `/api/v1/admin/orders`               | List all orders          | Admin         |
| GET    | `/api/v1/admin/orders/{order_id}`    | Get order details        | Admin         |
| PUT    | `/api/v1/admin/orders/{order_id}/status` | Update order status  | Admin         |
| POST   | `/api/v1/admin/orders/{order_id}/cancel` | Cancel order        | Admin         |

#### Inventory Management
| Method | Endpoint                                    | Description         | Auth Required |
| ------ | ------------------------------------------- | ------------------- | ------------- |
| GET    | `/api/v1/admin/inventory`                   | List product stock  | Admin         |
| GET    | `/api/v1/admin/inventory/{product_id}`      | Get stock details   | Admin         |
| POST   | `/api/v1/admin/inventory/{inventory_id}/adjust` | Adjust stock    | Admin         |
| GET    | `/api/v1/admin/inventory/low-stock/alert`   | Low stock alerts    | Admin         |

#### Dashboard & Analytics
| Method | Endpoint                             | Description              | Auth Required |
| ------ | ------------------------------------ | ------------------------ | ------------- |
| GET    | `/api/v1/admin/dashboard/statistics` | Dashboard metrics        | Admin         |
| GET    | `/api/v1/admin/dashboard/activity-logs` | Admin activity logs   | Admin         |

**For complete admin panel documentation, see [ADMIN_PANEL_API.md](./ADMIN_PANEL_API.md)**

### Health Check

| Method | Endpoint  | Description           | Auth Required |
| ------ | --------- | --------------------- | ------------- |
| GET    | `/health` | Service health status | No            |
| GET    | `/`       | API information       | No            |

## 📦 Project Structure

```
fastapi-auth-prisma/
├── config/                     # Configuration files
│   ├── dev_app_config.json
│   ├── qa_app_config.json
│   └── prod_app_config.json
├── prisma/                     # Prisma ORM schema
│   └── schema.prisma
├── src/                        # Source code
│   ├── controllers/           # API endpoints
│   │   ├── auth_controller.py
│   │   └── product_controller.py
│   ├── core/                  # Business logic
│   │   ├── auth_core.py
│   │   └── product_core.py
│   ├── data_contracts/        # Request/Response models
│   │   └── api_request_response.py
│   ├── middlewares/           # Custom middlewares
│   │   └── auth_middleware.py
│   ├── plugins/               # Database plugins
│   │   └── database.py
│   ├── services/              # Service layer
│   │   ├── auth_service.py
│   │   └── product_service.py
│   ├── utilities/             # Helper utilities
│   │   ├── cache_manager.py
│   │   ├── config_manager.py
│   │   ├── rate_limiter.py
│   │   └── security.py
│   └── main.py               # Application entry point
├── .env.example              # Environment variables template
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile               # Docker image configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Database (MySQL)
DATABASE_URL=mysql://user:password@localhost:3306/nursery_db

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_ENABLED=False

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

## 🔒 Security Features

- **Password Hashing**: Bcrypt with configurable rounds
- **JWT Tokens**: HS256 algorithm with expiration
- **Rate Limiting**: Per-endpoint and per-user limits
- **Token Refresh**: Secure token rotation
- **CORS Protection**: Configurable origins
- **Input Validation**: Pydantic models

## 📊 Database Schema

### Users Table

- `id` - UUID primary key
- `email` - Unique email address
- `phone` - Optional phone number
- `password_hash` - Bcrypt hashed password
- `is_active` - Account status
- Timestamps: `created_at`, `updated_at`

### Refresh Tokens Table

- `id` - UUID primary key
- `user_id` - Foreign key to users
- `token` - JWT refresh token
- `expires_at` - Expiration timestamp
- `is_revoked` - Revocation status

### Categories Table (Phase 1)

- `id` - UUID primary key
- `name` - Category name
- `slug` - URL-friendly identifier (unique)
- `description` - Category description
- `icon` - Emoji or icon identifier

### Products Table (Phase 1)

- `id` - UUID primary key
- `name` - Product name
- `scientific_name` - Scientific/botanical name
- `slug` - URL-friendly identifier (unique)
- `category_id` - Foreign key to categories
- `price` - Retail price
- `cost_price` - Cost price (optional)
- `image_url` - Product image URL
- `description` - Product description
- `care_instructions` - Plant care details
- `light_requirements` - Light conditions
- `watering_frequency` - Watering schedule
- `temperature_range` - Temperature preferences
- `is_active` - Product availability status

### Product Diseases Table (Phase 1)

- `id` - UUID primary key
- `product_id` - Foreign key to products
- `disease_name` - Common disease name

## 🚀 Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Change `JWT_SECRET_KEY` to strong random value
- [ ] Update `DATABASE_URL` with production database
- [ ] Configure Redis connection
- [ ] Set up proper CORS origins
- [ ] Enable HTTPS
- [ ] Configure rate limits
- [ ] Set up logging & monitoring
- [ ] Run database migrations

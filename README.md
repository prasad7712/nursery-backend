# FastAPI Authentication Boilerplate with Prisma ORM

A production-ready FastAPI authentication service with JWT tokens, rate limiting, and Prisma ORM.

## 🚀 Features

- ✅ **JWT Authentication** - Access & Refresh tokens
- ✅ **User Registration & Login**
- ✅ **Password Management** - Change password
- ✅ **Rate Limiting** - Prevent abuse
- ✅ **Redis Caching** - Fast data access
- ✅ **Prisma ORM** - Type-safe database access
- ✅ **Docker Support** - Easy deployment
- ✅ **CORS Configured** - Frontend integration ready
- ✅ **Health Check** - Service monitoring

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional, for caching)
- Docker & Docker Compose (optional)

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd fastapi-auth-prisma
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

### 5. Generate Prisma client

```bash
prisma generate
```

### 6. Run database migrations

```bash
prisma db push
```

## 🐳 Docker Setup

### Using Docker Compose (Recommended)

```bash
docker-compose up -d

docker-compose logs -f app

docker-compose down
```

## 🏃 Running the Application

### Development Mode

```bash
python run_app.py
```

Or with uvicorn directly:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
export ENVIRONMENT=production
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 API Documentation

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
│   │   └── auth_controller.py
│   ├── core/                  # Business logic
│   │   └── auth_core.py
│   ├── data_contracts/        # Request/Response models
│   │   └── api_request_response.py
│   ├── middlewares/           # Custom middlewares
│   │   └── auth_middleware.py
│   ├── plugins/               # Database plugins
│   │   └── database.py
│   ├── services/              # Service layer
│   │   └── auth_service.py
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
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/auth_db

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_ENABLED=True

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
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

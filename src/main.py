"""FastAPI application entry point"""
from contextlib import asynccontextmanager
from datetime import datetime

# Load environment variables FIRST, before importing config
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.controllers.auth_controller import router as auth_router
from src.controllers.product_controller import router as product_router
from src.controllers.cart_controller import router as cart_router
from src.controllers.order_controller import router as order_router
from src.controllers.payment_controller import router as payment_router
from src.controllers.admin_user_controller import router as admin_user_router
from src.controllers.admin_order_controller import router as admin_order_router
from src.controllers.admin_dashboard_controller import router as admin_dashboard_router
from src.controllers.admin_inventory_controller import router as admin_inventory_router
from src.plugins.database import db
from src.utilities.cache_manager import cache
from src.utilities.config_manager import config
from src.utilities.admin_init import initialize_admin
from src.data_contracts.api_request_response import HealthCheckResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting FastAPI Auth Service...")
    
    try:
        # Connect to database
        await db.connect()
        
        # Initialize admin account if not exists
        await initialize_admin()
        
        # Connect to Redis
        await cache.connect()
        
        print("✅ All services connected successfully")
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise
        raise
    
    yield
    
    # Shutdown
    print("🛑 Shutting down FastAPI Auth Service...")
    await db.disconnect()
    await cache.disconnect()
    print("✅ All services disconnected")


# Create FastAPI application
app = FastAPI(
    title=config.app_name,
    version=config.version,
    description="FastAPI Authentication Service with Prisma ORM and JWT",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get('cors.origins', ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    print(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if config.debug else "An unexpected error occurred",
            "success": False
        }
    )


# Include routers
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(admin_user_router)
app.include_router(admin_order_router)
app.include_router(admin_dashboard_router)
app.include_router(admin_inventory_router)


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns the status of the service and its dependencies
    """
    db_status = "healthy" if await db.health_check() else "unhealthy"
    cache_status = "healthy" if config.redis_enabled and await cache.exists("health_check") is not None else "disabled"
    
    return HealthCheckResponse(
        status="healthy",
        database=db_status,
        cache=cache_status,
        timestamp=datetime.utcnow()
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {config.app_name}",
        "version": config.version,
        "environment": config.environment,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=config.get('server.host', '0.0.0.0'),
        port=config.get('server.port', 8000),
        reload=config.debug
    )

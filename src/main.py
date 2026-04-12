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
from src.controllers.admin_product_controller import router as admin_product_router
from src.controllers.admin_category_controller import router as admin_category_router
from src.controllers.admin_inventory_controller import router as admin_inventory_router
from src.controllers.ai_controller import router as ai_router
from src.database import engine, init_db, dispose_db, health_check
from src.utilities.config_manager import config
from src.utilities.admin_init import initialize_admin
from src.data_contracts.api_request_response import HealthCheckResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting FastAPI Auth Service...")
    
    try:
        # Initialize database schema (create all tables if they don't exist)
        try:
            print("📂 Initializing database schema...")
            await init_db()
            print("✅ Database schema initialized")
            
            # Test database connection
            db_healthy = await health_check()
            if db_healthy:
                print("✅ Database connection successful")
                
                # Initialize admin account if not exists
                await initialize_admin()
            else:
                print("⚠️  Database connection check failed (app will still start)")
                print("⚠️  Database will be retried on first request")
        except Exception as db_error:
            print(f"⚠️  Database initialization warning (app will still start): {db_error}")
            print("⚠️  Database will be retried on first request")
        
        print("✅ FastAPI service started successfully")
        
    except Exception as e:
        print(f"❌ Critical startup error: {e}")
        raise
    
    yield
    
    # Shutdown
    print("🛑 Shutting down FastAPI Auth Service...")
    try:
        await dispose_db()
        print("✅ Database disconnected")
    except Exception as e:
        print(f"⚠️  Shutdown warning: {e}")


# Create FastAPI application
app = FastAPI(
    title=config.app_name,
    version=config.version,
    description="FastAPI Authentication Service with SQLAlchemy ORM and JWT",
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
app.include_router(admin_product_router)
app.include_router(admin_category_router)
app.include_router(admin_inventory_router)
app.include_router(ai_router)


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check_endpoint():
    """
    Health check endpoint
    
    Returns the status of the service and its dependencies
    """
    db_status = "healthy" if await health_check() else "unhealthy"
    
    return HealthCheckResponse(
        status="healthy",
        database=db_status,
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

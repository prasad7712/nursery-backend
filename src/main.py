"""FastAPI application entry point"""
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from src.controllers.auth_controller import router as auth_router
from src.plugins.database import db
from src.utilities.cache_manager import cache
from src.utilities.config_manager import config
from src.data_contracts.api_request_response import HealthCheckResponse

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting FastAPI Auth Service...")
    
    try:
        # Connect to database
        await db.connect()
        
        # Connect to Redis
        await cache.connect()
        
        print("✅ All services connected successfully")
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
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

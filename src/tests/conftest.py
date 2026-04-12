"""Pytest configuration and fixtures for SQLAlchemy async testing"""
import asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from src.models.base import Base
from src.models.user import User
from src.models.product import Product
from src.models.order import Order


# Test database URL - uses SQLite in-memory for fast tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_engine():
    """Create a new async engine for testing"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"timeout": 30}  # For SQLite
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def async_session_maker(async_engine):
    """Create a session factory for testing"""
    return async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


@pytest.fixture
async def session(async_session_maker) -> AsyncSession:
    """Provide a test database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture
async def test_user(session: AsyncSession):
    """Create a test user"""
    from src.utilities.security import hash_password
    
    user = User(
        id="test-user-1",
        email="test@example.com",
        password_hash=hash_password("TestPassword123"),
        first_name="Test",
        last_name="User",
        role="CUSTOMER",
        is_active=True
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture
async def test_admin(session: AsyncSession):
    """Create a test admin user"""
    from src.utilities.security import hash_password
    
    admin = User(
        id="test-admin-1",
        email="admin@example.com",
        password_hash=hash_password("AdminPassword123"),
        first_name="Admin",
        last_name="User",
        role="ADMIN",
        is_active=True
    )
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    return admin


@pytest.fixture
async def test_product(session: AsyncSession):
    """Create a test product"""
    product = Product(
        id="test-product-1",
        name="Test Plant",
        description="A test plant product",
        category="Indoor Plants",
        price=99.99,
        cost_price=50.00,
        image_url="https://example.com/test.jpg",
        is_active=True
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


@pytest.fixture
async def test_order(session: AsyncSession, test_user):
    """Create a test order"""
    order = Order(
        id="test-order-1",
        user_id=test_user.id,
        status="PENDING",
        payment_status="PENDING",
        total_amount=99.99
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


# Pytest markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )

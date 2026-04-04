import asyncio
import sys
sys.path.insert(0, 'd:\\My Projects\\nursery-backend')

from src.data_contracts.api_request_response import RegisterRequest
from src.utilities.security import security

async def test():
    # Test password validation
    try:
        req = RegisterRequest(
            email="test@ex.com",
            password="Test@123",
            first_name="Test",
            last_name="User"
        )
        print(f"✅ Request validation passed: {req.model_dump()}")
        
        # Test password hashing
        hashed = security.hash_password(req.password)
        print(f"✅ Password hashed: {hashed[:50]}...")
        
        # Test verification
        verified = security.verify_password(req.password, hashed)
        print(f"✅ Password verified: {verified}")
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

asyncio.run(test())

"""Test script for Phase 1 API endpoints"""
import asyncio
import httpx
import json
import sys

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

async def test_api():
    """Test all Phase 1 API endpoints"""
    
    async with httpx.AsyncClient() as client:
        print("\n" + "="*60)
        print("Testing Phase 1 API Endpoints")
        print("="*60 + "\n")
        
        # Test 1: Register new user
        print("1. Testing POST /api/v1/auth/register")
        print("-" * 60)
        register_data = {
            "email": "test@example.com",
            "password": "TestPassword123",
            "firstName": "Test",
            "lastName": "User"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/auth/register",
                json=register_data
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}\n")
            
            if response.status_code == 201:
                user_id = response.json().get("userId")
                token = response.json().get("token")
                print("✓ Register endpoint working correctly\n")
            else:
                print("✗ Register endpoint failed\n")
                return False
        except Exception as e:
            print(f"✗ Register endpoint error: {e}\n")
            return False
        
        # Test 2: Login user
        print("2. Testing POST /api/v1/auth/login")
        print("-" * 60)
        login_data = {
            "email": "test@example.com",
            "password": "TestPassword123"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/auth/login",
                json=login_data
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}\n")
            
            if response.status_code == 200:
                token = response.json().get("token")
                print("✓ Login endpoint working correctly\n")
            else:
                print("✗ Login endpoint failed\n")
                return False
        except Exception as e:
            print(f"✗ Login endpoint error: {e}\n")
            return False
        
        # Test 3: Get current user
        print("3. Testing GET /api/v1/auth/me")
        print("-" * 60)
        
        try:
            response = await client.get(
                f"{BASE_URL}/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}\n")
            
            if response.status_code == 200:
                print("✓ Get current user endpoint working correctly\n")
            else:
                print("✗ Get current user endpoint failed\n")
                return False
        except Exception as e:
            print(f"✗ Get current user endpoint error: {e}\n")
            return False
        
        # Test 4: Get categories
        print("4. Testing GET /api/v1/categories")
        print("-" * 60)
        
        try:
            response = await client.get(f"{BASE_URL}/categories")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}\n")
            
            if response.status_code == 200:
                print("✓ Get categories endpoint working correctly\n")
            else:
                print("✗ Get categories endpoint failed\n")
                return False
        except Exception as e:
            print(f"✗ Get categories endpoint error: {e}\n")
            return False
        
        # Test 5: List products
        print("5. Testing GET /api/v1/products")
        print("-" * 60)
        
        try:
            response = await client.get(f"{BASE_URL}/products")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}\n")
            
            if response.status_code == 200:
                print("✓ List products endpoint working correctly\n")
            else:
                print("✗ List products endpoint failed\n")
                return False
        except Exception as e:
            print(f"✗ List products endpoint error: {e}\n")
            return False
        
        print("="*60)
        print("✅ All Phase 1 endpoints tested successfully!")
        print("="*60 + "\n")
        return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_api())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)

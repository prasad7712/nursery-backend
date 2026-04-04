"""Quick test script"""
import httpx
import asyncio
import json

async def test():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            print("Testing GET /api/v1/products...")
            resp = await client.get('http://localhost:8000/api/v1/products')
            print(f'Status: {resp.status_code}')
            try:
                data = resp.json()
                print(f'Response: {json.dumps(data,indent=2)[:500]}')
            except:
                print(f'Response text: {resp.text[:300]}')
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}')

asyncio.run(test())

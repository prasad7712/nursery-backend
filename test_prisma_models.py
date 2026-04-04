import asyncio
import sys
sys.path.insert(0, 'd:\\My Projects\\nursery-backend')

from src.plugins.database import db

async def test():
    try:
        await db.connect()
        
        # List all available models
        print("Available models on db.client:")
        for attr in dir(db.client):
            if not attr.startswith('_'):
                print(f"  - {attr}")
        
        await db.disconnect()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())

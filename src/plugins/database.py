"""Database connection plugin using Prisma ORM"""
import subprocess
import sys

from prisma import Prisma
from typing import Optional




class DatabasePlugin:
    """Database connection manager using Prisma ORM"""
    
    def __init__(self):
        self._client: Optional[Prisma] = None
    
    async def connect(self):
        try:
            # Ensure Prisma binary exists before connecting
            print("🔄 Fetching Prisma binary...")
            result = subprocess.run(
                [sys.executable, "-m", "prisma", "py", "fetch"],
                check=True,
                capture_output=False  # 👈 show output in Render logs
            )
            print(f"✅ Prisma fetch completed")
            
            self._client = Prisma()
            await self._client.connect()
            print("✅ Database connected successfully via Prisma")
        except subprocess.CalledProcessError as e:
            print(f"❌ Prisma fetch failed with code {e.returncode}")
            raise
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from database"""
        if self._client:
            await self._client.disconnect()
            print("✅ Database disconnected")
    
    @property
    def client(self) -> Prisma:
        """Get Prisma client instance"""
        if not self._client:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._client
    
    async def health_check(self) -> bool:
        """Check database connection health"""
        try:
            # Simple query to check connection
            await self._client.user.find_first()
            return True
        except Exception:
            return False


# Singleton instance
db = DatabasePlugin()

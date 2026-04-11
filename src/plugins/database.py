"""Database connection plugin using Prisma ORM"""
import glob
import os
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
            print("🔄 Fetching Prisma binary...")
            subprocess.run(
                [sys.executable, "-m", "prisma", "py", "fetch"],
                check=True,
                capture_output=False
            )
            
            # Fix permissions — make the binary executable
            binary_pattern = os.path.expanduser(
                "~/.cache/prisma-python/binaries/**/*query-engine*"
            )
            for binary_path in glob.glob(binary_pattern, recursive=True):
                print(f"🔧 Setting executable permission on: {binary_path}")
                os.chmod(binary_path, 0o755)
            
            # Also check /opt/render path
            render_pattern = "/opt/render/.cache/prisma-python/binaries/**/*query-engine*"
            for binary_path in glob.glob(render_pattern, recursive=True):
                print(f"🔧 Setting executable permission on: {binary_path}")
                os.chmod(binary_path, 0o755)

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

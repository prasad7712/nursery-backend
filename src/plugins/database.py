"""Database connection plugin using Prisma ORM"""
import glob
import os
import subprocess
import sys

from prisma import Prisma
from typing import Optional

# v2 - forced redeploy


class DatabasePlugin:
    """Database connection manager using Prisma ORM"""
    
    def __init__(self):
        self._client: Optional[Prisma] = None
    
    
async def connect(self):
    try:
        print("🔄 Fetching Prisma binary...")
        
        # Debug: list what's actually in the cache before fetch
        cache_dir = "/opt/render/.cache/prisma-python/binaries"
        if os.path.exists(cache_dir):
            for root, dirs, files in os.walk(cache_dir):
                for f in files:
                    full = os.path.join(root, f)
                    stat = oct(os.stat(full).st_mode)
                    print(f"📁 {full} | perms: {stat}")
        else:
            print(f"⚠️ Cache dir does not exist: {cache_dir}")

        result = subprocess.run(
            [sys.executable, "-m", "prisma", "py", "fetch"],
            capture_output=False,
            check=False  # don't raise, let us see what happens
        )
        print(f"✅ Prisma fetch exit code: {result.returncode}")

        # Debug: list again after fetch
        print("📂 After fetch:")
        if os.path.exists(cache_dir):
            for root, dirs, files in os.walk(cache_dir):
                for f in files:
                    full = os.path.join(root, f)
                    stat = oct(os.stat(full).st_mode)
                    print(f"📁 {full} | perms: {stat}")

        # Fix permissions
        render_pattern = "/opt/render/.cache/prisma-python/binaries/**/*query-engine*"
        for binary_path in glob.glob(render_pattern, recursive=True):
            print(f"🔧 chmod 755: {binary_path}")
            os.chmod(binary_path, 0o755)

        self._client = Prisma()
        await self._client.connect()
        print("✅ Database connected successfully via Prisma")

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

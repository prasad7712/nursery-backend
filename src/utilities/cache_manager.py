"""Cache Management - Disabled for free tier deployment"""
import json
from typing import Optional, Any

from src.utilities.config_manager import config


class CacheManager:
    """Redis cache manager for storing temporary data"""
    
    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None
        self._enabled = config.redis_enabled
    
    async def connect(self):
        """Connect to Redis"""
        if not self._enabled:
            return
        
        try:
            self._redis_client = redis.Redis(
                host=config.get('redis.host', 'localhost'),
                port=config.get('redis.port', 6379),
                db=config.get('redis.db', 0),
                password=config.get('redis.password'),
                decode_responses=True
            )
            await self._redis_client.ping()
            print("✅ Redis connected successfully")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            self._enabled = False
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self._redis_client:
            await self._redis_client.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._enabled or not self._redis_client:
            return None
        
        try:
            value = await self._redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value in cache with optional expiration (seconds)"""
        if not self._enabled or not self._redis_client:
            return False
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            await self._redis_client.set(key, value)
            
            if expire:
                await self._redis_client.expire(key, expire)
            
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self._enabled or not self._redis_client:
            return False
        
        try:
            await self._redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self._enabled or not self._redis_client:
            return False
        
        try:
            return await self._redis_client.exists(key) > 0
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter in cache"""
        if not self._enabled or not self._redis_client:
            return None
        
        try:
            return await self._redis_client.incrby(key, amount)
        except Exception as e:
            print(f"Cache increment error: {e}")
            return None
    
    async def set_with_ttl(self, key: str, value: Any, ttl: int) -> bool:
        """Set value with time-to-live in seconds"""
        return await self.set(key, value, expire=ttl)
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for a key"""
        if not self._enabled or not self._redis_client:
            return None
        
        try:
            return await self._redis_client.ttl(key)
        except Exception as e:
            print(f"Cache TTL error: {e}")
            return None


# Singleton instance
cache = CacheManager()

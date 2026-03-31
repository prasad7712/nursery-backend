"""Rate limiting utilities"""
from typing import Optional
from datetime import datetime, timedelta

from src.utilities.cache_manager import cache
from src.utilities.config_manager import config


class RateLimiter:
    """Rate limiter using Redis or in-memory storage"""
    
    def __init__(self):
        self._enabled = config.rate_limiting_enabled
        self._max_requests = config.get('rate_limiting.requests', 100)
        self._window_seconds = config.get('rate_limiting.window_seconds', 60)
        self._in_memory_store = {}  # Fallback when Redis is not available
    
    async def is_rate_limited(self, identifier: str, max_requests: Optional[int] = None, 
                              window_seconds: Optional[int] = None) -> tuple[bool, dict]:
        """
        Check if identifier is rate limited
        
        Returns:
            (is_limited: bool, info: dict)
        """
        if not self._enabled:
            return False, {}
        
        max_req = max_requests or self._max_requests
        window = window_seconds or self._window_seconds
        
        key = f"rate_limit:{identifier}"
        
        # Try Redis first
        if config.redis_enabled:
            return await self._check_redis_rate_limit(key, max_req, window)
        else:
            return await self._check_memory_rate_limit(key, max_req, window)
    
    async def _check_redis_rate_limit(self, key: str, max_requests: int, 
                                     window_seconds: int) -> tuple[bool, dict]:
        """Check rate limit using Redis"""
        current_count = await cache.increment(key)
        
        if current_count == 1:
            # First request in window, set expiration
            await cache.set_with_ttl(key, current_count, window_seconds)
        
        ttl = await cache.get_ttl(key)
        
        if current_count and current_count > max_requests:
            return True, {
                "limit": max_requests,
                "remaining": 0,
                "reset": ttl if ttl else window_seconds
            }
        
        return False, {
            "limit": max_requests,
            "remaining": max_requests - (current_count or 0),
            "reset": ttl if ttl else window_seconds
        }
    
    async def _check_memory_rate_limit(self, key: str, max_requests: int, 
                                       window_seconds: int) -> tuple[bool, dict]:
        """Check rate limit using in-memory storage (fallback)"""
        now = datetime.utcnow()
        
        if key not in self._in_memory_store:
            self._in_memory_store[key] = {
                "count": 1,
                "window_start": now
            }
            return False, {
                "limit": max_requests,
                "remaining": max_requests - 1,
                "reset": window_seconds
            }
        
        store_data = self._in_memory_store[key]
        window_start = store_data["window_start"]
        
        # Check if window has expired
        if (now - window_start).total_seconds() >= window_seconds:
            self._in_memory_store[key] = {
                "count": 1,
                "window_start": now
            }
            return False, {
                "limit": max_requests,
                "remaining": max_requests - 1,
                "reset": window_seconds
            }
        
        # Increment counter
        store_data["count"] += 1
        
        if store_data["count"] > max_requests:
            remaining_time = int(window_seconds - (now - window_start).total_seconds())
            return True, {
                "limit": max_requests,
                "remaining": 0,
                "reset": remaining_time
            }
        
        remaining_time = int(window_seconds - (now - window_start).total_seconds())
        return False, {
            "limit": max_requests,
            "remaining": max_requests - store_data["count"],
            "reset": remaining_time
        }
    
    async def reset_rate_limit(self, identifier: str) -> bool:
        """Reset rate limit for an identifier"""
        key = f"rate_limit:{identifier}"
        
        if config.redis_enabled:
            return await cache.delete(key)
        else:
            if key in self._in_memory_store:
                del self._in_memory_store[key]
            return True


# Singleton instance
rate_limiter = RateLimiter()

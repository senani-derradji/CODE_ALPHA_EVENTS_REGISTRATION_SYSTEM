from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from app.core.config import settings
import asyncio
import time


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60, auth_requests_per_minute: int = 5):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.auth_requests_per_minute = auth_requests_per_minute
        self._store: dict = defaultdict(list)
        self._lock = asyncio.Lock()
        self._redis = None

        if settings.REDIS_URL:
            try:
                import redis.asyncio as aioredis
                self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception:
                pass  # Fall back to in-memory if Redis unavailable

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _is_auth_route(self, path: str) -> bool:
        return path.startswith("/auth/login") or path.startswith("/auth/google") or path.startswith("/auth/microsoft")

    async def _check_redis(self, key: str, limit: int) -> bool:
        """Returns True if request is allowed, False if rate-limited."""
        now = time.time()
        window_start = now - 60
        pipe = self._redis.pipeline()
        pipe.zremrangebyscore(key, "-inf", window_start)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, 60)
        results = await pipe.execute()
        count = results[2]
        return count <= limit

    async def _check_memory(self, key: str, limit: int) -> bool:
        now = datetime.utcnow()
        window = timedelta(minutes=1)
        async with self._lock:
            self._store[key] = [t for t in self._store[key] if now - t < window]
            if len(self._store[key]) >= limit:
                return False
            self._store[key].append(now)
            return True

    async def dispatch(self, request: Request, call_next):
        ip = self._get_client_ip(request)
        path = request.url.path
        is_auth = self._is_auth_route(path)
        limit = self.auth_requests_per_minute if is_auth else self.requests_per_minute
        key = f"rl:{ip}:{path if is_auth else 'global'}"

        if self._redis:
            allowed = await self._check_redis(key, limit)
        else:
            allowed = await self._check_memory(key, limit)

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": "60"},
            )

        return await call_next(request)

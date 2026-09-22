import time

from redis.asyncio import Redis

from app.core.config import settings


class RateLimiter:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def check(self, identity: str, limit: int | None = None) -> tuple[bool, int]:
        limit = limit or settings.rate_limit_per_minute
        window = int(time.time() // 60)
        key = f"jarvis:rate:{identity}:{window}"
        count = await self.redis.incr(key)

        if count == 1:
            await self.redis.expire(key, 70)

        return count <= limit, count

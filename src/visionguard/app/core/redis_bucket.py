import logging
import time

import redis

from visionguard.app.core.limiter import RateLimiter


class RedisFallbackRateLimiter(RateLimiter):
    def __init__(
        self,
        redis_limiter: RateLimiter,
        fallback_limiter: RateLimiter,
        logger: logging.Logger,
    ):
        self.redis_limiter = redis_limiter
        self.fallback_limiter = fallback_limiter
        self.logger = logger

    def is_allowed(self, user_id: str) -> bool:
        try:
            return self.redis_limiter.is_allowed(user_id)
        except redis.RedisError as exc:
            self.logger.warning(
                "Redis rate limiter unavailable; using in-memory fallback: %s",
                exc,
            )
            return self.fallback_limiter.is_allowed(user_id)


class RedisTokenBucket(RateLimiter):
    """
    Rate limiter basado en Token Bucket utilizando Redis.

    Toda la actualización del balde ocurre mediante un script Lua
    para garantizar atomicidad.
    """

    LUA_SCRIPT = """
    local key = KEYS[1]

    local capacity = tonumber(ARGV[1])
    local refill_rate = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])

    local bucket = redis.call(
        'HMGET',
        key,
        'tokens',
        'last_refill'
    )

    local tokens = tonumber(bucket[1]) or capacity
    local last_refill = tonumber(bucket[2]) or now

    -- Regenerar tokens
    local elapsed = now - last_refill

    tokens = math.min(
        capacity,
        tokens + (elapsed * refill_rate)
    )

    if tokens >= 1 then
        tokens = tokens - 1

        redis.call(
            'HMSET',
            key,
            'tokens',
            tokens,
            'last_refill',
            now
        )

        redis.call('EXPIRE', key, 3600)

        return 1
    else
        redis.call(
            'HMSET',
            key,
            'tokens',
            tokens,
            'last_refill',
            now
        )

        redis.call('EXPIRE', key, 3600)

        return 0
    end
    """

    def __init__(self,redis_client: redis.Redis,capacity: int = 5):
        self.redis = redis_client
        self.capacity = capacity
        self.refill_rate = 1 / 60  # 1 token por minuto

        self.script = self.redis.register_script(
            self.LUA_SCRIPT
        )

    def is_allowed(self, user_id: str) -> bool:
        """
        Verifica si el usuario puede realizar una petición.
        """

        key = f"rate_limit:{user_id}"

        result = self.script(
            keys=[key],
            args=[
                self.capacity,
                self.refill_rate,
                time.time()
            ]
        )

        return result == 1





    
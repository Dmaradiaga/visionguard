import logging
import os

from flask import Flask
import redis

from visionguard.app.core.limiter import RateLimiter
from visionguard.app.core.token_bucket import TokenBucket
from visionguard.app.core.redis_bucket import RedisTokenBucket
from visionguard.app.routes.routes import routes, configure
from visionguard.app.services.service_vision import PhotoService


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


def run() -> Flask:
    """
    Construye la aplicación.

    Intenta utilizar Redis como almacenamiento para el
    rate limiter. Si Redis no está disponible, utiliza
    una implementación en memoria.
    """

    app = Flask(__name__, template_folder="../templates")
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

    try:
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=6379,
            decode_responses=False,
            socket_connect_timeout=1
        )

        redis_client.ping()

        app.logger.info("Using Redis-backed rate limiting")

        rate_limiter = RedisFallbackRateLimiter(
            RedisTokenBucket(redis_client=redis_client, capacity=5),
            TokenBucket(capacity=5, refill_rate=1 / 60),
            app.logger,
        )

    except redis.RedisError as exc:
        app.logger.warning(
            "Redis is unavailable at startup; using in-memory rate limiting: %s",
            exc,
        )
        rate_limiter = TokenBucket(
            capacity=5,
            refill_rate=1 / 60
        )

    photo_service = PhotoService()

    # Inyección de dependencias.
    configure(
        rate_limiter,
        photo_service
    )

    app.register_blueprint(routes)

    return app


def main() -> None:
    app = run()
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8080")),
        debug=False,
    )


if __name__ == "__main__":
    main()

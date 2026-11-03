import os

from flask import Flask
import redis

from visionguard.app.core.token_bucket import TokenBucket
from visionguard.app.core.redis_bucket import (
    RedisFallbackRateLimiter,
    RedisTokenBucket,
)
from visionguard.app.routes.routes import create_routes
from visionguard.app.services.service_vision import PhotoService


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

    app.register_blueprint(
        create_routes(rate_limiter, PhotoService())
    )

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

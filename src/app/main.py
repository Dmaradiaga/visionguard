from flask import Flask
import redis

from app.routes.routes import routes, configure
from app.core.token_bucket import TokenBucket
from app.core.redis_bucket import RedisTokenBucket
from app.services.service_vision import PhotoService


def run():
    """
    Construye la aplicación.

    Intenta utilizar Redis como almacenamiento para el
    rate limiter. Si Redis no está disponible, utiliza
    una implementación en memoria.
    """

    app = Flask(__name__,template_folder="../templates")

    try:
        redis_client = redis.Redis(
            host="redis",
            port=6379,
            decode_responses=False,
            socket_connect_timeout=1
        )

        redis_client.ping()

        print("-> Usando RedisTokenBucket")

        rate_limiter = RedisTokenBucket(
            redis_client=redis_client,
            capacity=5
        )

    except redis.RedisError:
        print("-> Usando TokenBucket")

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


if __name__ == "__main__":
    app = run()

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=True
    )



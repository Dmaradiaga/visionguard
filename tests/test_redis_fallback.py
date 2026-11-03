import logging
import unittest
from unittest.mock import Mock

import redis

from visionguard.app.main import RedisFallbackRateLimiter


class BrokenRedisLimiter:
    def is_allowed(self, _user_id):
        raise redis.ConnectionError("Redis unavailable")


class AllowAll:
    def is_allowed(self, _user_id):
        return True


class RedisFallbackTests(unittest.TestCase):
    def test_uses_local_limiter_when_redis_fails(self):
        logger = Mock(spec=logging.Logger)
        limiter = RedisFallbackRateLimiter(
            BrokenRedisLimiter(),
            AllowAll(),
            logger,
        )

        self.assertTrue(limiter.is_allowed("client"))
        logger.warning.assert_called_once()


if __name__ == "__main__":
    unittest.main()

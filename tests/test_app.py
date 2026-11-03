import unittest
from unittest.mock import patch

import redis

from visionguard.app.main import run


class AppTests(unittest.TestCase):
    @patch("visionguard.app.main.redis.Redis")
    def test_creates_app_with_upload_limit_and_template(self, redis_client):
        redis_client.return_value.ping.side_effect = redis.ConnectionError(
            "Redis unavailable"
        )

        app = run()
        client = app.test_client()

        self.assertEqual(app.config["MAX_CONTENT_LENGTH"], 10 * 1024 * 1024)
        self.assertEqual(client.get("/").status_code, 200)


if __name__ == "__main__":
    unittest.main()

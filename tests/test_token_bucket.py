import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from visionguard.app.core.token_bucket import TokenBucket


class TokenBucketTests(unittest.TestCase):
    def test_limits_requests_concurrently(self):
        limiter = TokenBucket(capacity=5, refill_rate=1 / 60)

        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(limiter.is_allowed, ["client"] * 40))

        self.assertEqual(sum(results), 5)

    def test_refills_tokens(self):
        limiter = TokenBucket(capacity=1, refill_rate=1 / 60)
        with patch("visionguard.app.core.token_bucket.time.monotonic") as clock:
            clock.return_value = 100
            self.assertTrue(limiter.is_allowed("client"))
            self.assertFalse(limiter.is_allowed("client"))

            clock.return_value = 160
            self.assertTrue(limiter.is_allowed("client"))

    def test_keeps_bucket_storage_bounded(self):
        limiter = TokenBucket(capacity=1, refill_rate=1 / 60)
        limiter.MAX_BUCKETS = 2

        for client in ("one", "two", "three"):
            limiter.is_allowed(client)

        self.assertEqual(len(limiter.buckets), 2)


if __name__ == "__main__":
    unittest.main()

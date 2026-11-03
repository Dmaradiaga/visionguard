import time
from collections import OrderedDict
from dataclasses import dataclass
from threading import Lock

from visionguard.app.core.limiter import RateLimiter


@dataclass
class BucketState:
    tokens: float
    last_refill: float


class TokenBucket(RateLimiter):
    MAX_BUCKETS = 10_000

    def __init__(self, capacity: int, refill_rate: float):
        if capacity <= 0:
            raise ValueError("capacity debe ser mayor que cero")
        if refill_rate <= 0:
            raise ValueError("refill_rate debe ser mayor que cero")

        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets: OrderedDict[str, BucketState] = OrderedDict()
        self._lock = Lock()

    def is_allowed(self, user_id: str) -> bool:
        now = time.monotonic()
        with self._lock:
            state = self.buckets.get(user_id)
            if state is None:
                if len(self.buckets) >= self.MAX_BUCKETS:
                    self.buckets.popitem(last=False)
                state = BucketState(self.capacity, now)
                self.buckets[user_id] = state
            else:
                self.buckets.move_to_end(user_id)
                elapsed = max(0.0, now - state.last_refill)
                state.tokens = min(
                    self.capacity,
                    state.tokens + self.refill_rate * elapsed,
                )
                state.last_refill = now

            if state.tokens < 1:
                return False

            state.tokens -= 1
            return True

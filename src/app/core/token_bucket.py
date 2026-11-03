import time
from  dataclasses import dataclass
from app.core.limiter import RateLimiter


@dataclass
class BucketState:
	"""
		Maneja la cantidad de tokens pro usuario
		y su ultima actualizacion
	"""
	tokens: float
	last_refill: float


class  TokenBucket(RateLimiter):
	"""
		Verifica si hay tokens en los baldes de cada usuario
	"""
	def __init__(self, capacity:int, refill_rate:float):
		self.capacity = capacity
		self.refill_rate = refill_rate
		self.buckets:dict[str,BucketState] = {}

	def is_allowed(self,user_id:str) -> bool:
		now = time.time()
		state = self.buckets.get(user_id,BucketState(self.capacity,now))

		#Regeneracion de tokens
		elapsed = now - state.last_refill
		state.tokens = min(self.capacity, state.tokens + self.refill_rate*elapsed)
		state.last_refill = now

		#Verificamos si tiene tokens
		if state.tokens>=1:
			state.tokens-=1
			self.buckets[user_id] = state
			return True
		self.buckets[user_id] = state
		return False








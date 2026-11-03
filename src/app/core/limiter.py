from abc import ABC, abstractmethod

class RateLimiter(ABC):
	"""
		Clase base, todos los limitadores deben tener este metodo
	"""

	@abstractmethod
	def is_allowed(self, user_id:str) -> bool:
		"""
			Devuelve True si pasa y False en caso contraio
		"""
		pass

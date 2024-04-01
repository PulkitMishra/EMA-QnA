from abc import ABC, abstractmethod
from typing import Callable, Any
from app.schemas.api_key import APIKey

class APIClient(ABC):
    @abstractmethod
    def execute_api_call(self, call: str, api_key: APIKey, fallback: Callable[[str], Any] = None):
        pass
from abc import ABC, abstractmethod
from typing import Any
from app.dto.requests import MemoryRequest
from app.dto.responses import MemoryResponse
from app.dto.context import MemoryContext

class MemoryProvider(ABC):
    """Abstract interface for Memory MCP Provider."""

    @abstractmethod
    async def retrieve(self, request: MemoryRequest) -> MemoryContext:
        """Retrieve user profile, preferences, past trips, and long-term memory."""
        pass

    @abstractmethod
    async def store(self, user_id: str, memory_data: dict[str, Any]) -> bool:
        """Store new memory or update user profile."""
        pass

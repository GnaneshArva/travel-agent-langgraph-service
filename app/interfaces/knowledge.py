from abc import ABC, abstractmethod
from app.dto.requests import KnowledgeRequest
from app.dto.context import KnowledgeContext

class KnowledgeProvider(ABC):
    """Abstract interface for Knowledge MCP Provider."""

    @abstractmethod
    async def retrieve(self, request: KnowledgeRequest) -> KnowledgeContext:
        """Retrieve destination knowledge, visa info, weather, and advisories."""
        pass

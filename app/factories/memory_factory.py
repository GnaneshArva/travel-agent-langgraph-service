from app.interfaces.memory import MemoryProvider
from app.integrations.memory.memory_client import MemoryMcpClient

class MemoryFactory:
    """Factory to instantiate Memory providers."""
    @staticmethod
    def get_provider(mcp_url: str | None = None) -> MemoryProvider:
        return MemoryMcpClient(mcp_url=mcp_url)

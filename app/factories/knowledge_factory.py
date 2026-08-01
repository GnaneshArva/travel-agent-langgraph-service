from app.interfaces.knowledge import KnowledgeProvider
from app.integrations.knowledge.knowledge_client import KnowledgeMcpClient

class KnowledgeFactory:
    """Factory to instantiate Knowledge providers."""
    @staticmethod
    def get_provider(mcp_url: str | None = None) -> KnowledgeProvider:
        return KnowledgeMcpClient(mcp_url=mcp_url)

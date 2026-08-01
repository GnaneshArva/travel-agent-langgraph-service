from app.interfaces.tool import ToolProvider
from app.integrations.tools.travel_tools_client import TravelToolsMcpClient

class ToolFactory:
    """Factory to instantiate Tool execution providers."""
    @staticmethod
    def get_provider(mcp_url: str | None = None) -> ToolProvider:
        return TravelToolsMcpClient(mcp_url=mcp_url)

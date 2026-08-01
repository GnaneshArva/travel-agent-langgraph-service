import httpx
from app.interfaces.knowledge import KnowledgeProvider
from app.dto.requests import KnowledgeRequest
from app.dto.context import KnowledgeContext
from app.config.settings import settings
from app.utils.logger import logger

class KnowledgeMcpClient(KnowledgeProvider):
    """Integration Client for travel-knowledge-mcp-server with standalone fallback."""

    def __init__(self, mcp_url: str | None = None):
        self.mcp_url = mcp_url or settings.mcp.knowledge_mcp_url
        self.timeout = settings.timeouts.mcp_timeout

    async def retrieve(self, request: KnowledgeRequest) -> KnowledgeContext:
        logger.info(f"Retrieving destination knowledge for destination={request.destination}", component="KnowledgeMcpClient")
        if not settings.features.enable_knowledge:
            return KnowledgeContext()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.mcp_url}/knowledge/search", json={"destination": request.destination})
                if resp.status_code == 200:
                    data = resp.json()
                    return KnowledgeContext(
                        destination_guides=data.get("guides", []),
                        visa_information=data.get("visa", {}),
                        weather_info=data.get("weather", {}),
                        local_customs=data.get("customs", []),
                        advisories=data.get("advisories", [])
                    )
        except Exception as e:
            logger.warning(f"Knowledge MCP server unreachable ({str(e)}). Using fallback destination knowledge.", component="KnowledgeMcpClient")

        # Mock fallback data for standalone execution
        dest_title = request.destination.title()
        return KnowledgeContext(
            destination_guides=[{"title": f"Top Attractions in {dest_title}", "content": f"Popular cultural landmarks and scenic spots in {dest_title}."}],
            visa_information={"required": True, "type": "e-Visa / Visa on Arrival", "max_stay_days": 30},
            weather_info={"season": "Pleasant", "avg_temp_c": 22.5},
            local_customs=[f"Respect local cultural decorum in {dest_title}."],
            advisories=[f"Check active health and travel guidelines for {dest_title}."]
        )

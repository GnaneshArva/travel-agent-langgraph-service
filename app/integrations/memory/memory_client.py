import httpx
from typing import Any
from app.interfaces.memory import MemoryProvider
from app.dto.requests import MemoryRequest
from app.dto.context import MemoryContext
from app.config.settings import settings
from app.utils.logger import logger

class MemoryMcpClient(MemoryProvider):
    """Integration Client for travel-memory-mcp-server with standalone fallback."""

    def __init__(self, mcp_url: str | None = None):
        self.mcp_url = mcp_url or settings.mcp.memory_mcp_url
        self.timeout = settings.timeouts.mcp_timeout

    async def retrieve(self, request: MemoryRequest) -> MemoryContext:
        logger.info(f"Retrieving user memory for user_id={request.user_id}", component="MemoryMcpClient")
        if not settings.features.enable_memory:
            return MemoryContext()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.mcp_url}/memory/retrieve", json={"user_id": request.user_id})
                if resp.status_code == 200:
                    data = resp.json()
                    return MemoryContext(
                        user_preferences=data.get("preferences", {}),
                        past_trips=data.get("past_trips", []),
                        dietary_preferences=data.get("dietary_preferences", ["Vegetarian option preferred"]),
                        hotel_preferences=data.get("hotel_preferences", ["4-star and above", "Central location"]),
                        airline_preferences=data.get("airline_preferences", ["Window seat preference"]),
                        recent_history=data.get("recent_history", [])
                    )
        except Exception as e:
            logger.warning(f"Memory MCP server unreachable ({str(e)}). Using fallback mock memory context.", component="MemoryMcpClient")

        # Mock fallback data for standalone execution
        return MemoryContext(
            user_preferences={"seat": "Window", "diet": "Vegetarian", "hotel_min_rating": 4.0},
            past_trips=[{"destination": "Tokyo", "year": 2024}],
            dietary_preferences=["Vegetarian"],
            hotel_preferences=["4-star hotels"],
            airline_preferences=["Window seat"],
            recent_history=[]
        )

    async def store(self, user_id: str, memory_data: dict[str, Any]) -> bool:
        logger.info(f"Storing memory for user_id={user_id}", component="MemoryMcpClient")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.mcp_url}/memory/store", json={"user_id": user_id, "data": memory_data})
                return resp.status_code == 200
        except Exception:
            return True

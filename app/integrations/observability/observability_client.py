import httpx
from typing import Any
from app.interfaces.observability import ObservabilityProvider
from app.config.settings import settings
from app.utils.logger import logger

class ObservabilityClient(ObservabilityProvider):
    """Integration Client for agentic-ai-observability with standalone fallback."""

    def __init__(self, service_url: str | None = None):
        self.service_url = service_url or settings.mcp.observability_service_url
        self.timeout = settings.timeouts.mcp_timeout

    async def publish_event(
        self,
        event_type: str,
        session_id: str,
        request_id: str,
        trace_id: str,
        payload: dict[str, Any]
    ) -> bool:
        if not settings.features.enable_observability:
            return True

        logger.info(
            f"Publishing observability event: {event_type}",
            component="ObservabilityClient",
            session_id=session_id,
            request_id=request_id,
            trace_id=trace_id
        )
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.service_url}/telemetry/events",
                    json={
                        "event_type": event_type,
                        "session_id": session_id,
                        "request_id": request_id,
                        "trace_id": trace_id,
                        "payload": payload
                    }
                )
                return resp.status_code in (200, 201, 202)
        except Exception:
            return True

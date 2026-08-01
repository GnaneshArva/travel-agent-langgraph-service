from abc import ABC, abstractmethod
from typing import Any

class ObservabilityProvider(ABC):
    """Abstract interface for Enterprise Observability Telemetry."""

    @abstractmethod
    async def publish_event(
        self,
        event_type: str,
        session_id: str,
        request_id: str,
        trace_id: str,
        payload: dict[str, Any]
    ) -> bool:
        """Publish lifecycle telemetry event (e.g. PlanningStarted, ToolInvoked, ResponseGenerated)."""
        pass

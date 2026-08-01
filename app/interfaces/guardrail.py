from abc import ABC, abstractmethod
from typing import Any

class GuardrailProvider(ABC):
    """Abstract interface for Security & Quality Guardrails Provider."""

    @abstractmethod
    async def validate_input(self, text: str, session_id: str | None = None) -> tuple[bool, str, dict[str, Any]]:
        """
        Validate incoming user request.
        Returns: (is_allowed, sanitized_text_or_reason, metadata)
        """
        pass

    @abstractmethod
    async def validate_output(self, text: str, session_id: str | None = None) -> tuple[bool, str, dict[str, Any]]:
        """
        Validate outgoing model response.
        Returns: (is_allowed, sanitized_text_or_reason, metadata)
        """
        pass

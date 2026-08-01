from abc import ABC, abstractmethod
from typing import Any
from app.dto.context import PromptContext

class PromptProvider(ABC):
    """Abstract interface for Prompt Management Provider."""

    @abstractmethod
    async def load_prompt(self, template_name: str, version: str | None = None, variables: dict[str, Any] | None = None) -> PromptContext:
        """Load and render system prompt template from Prompt Management service."""
        pass

from abc import ABC, abstractmethod
from typing import AsyncGenerator
from app.dto.requests import TravelRequest
from app.dto.responses import TravelResponse
from app.dto.planning_dto import ExecutionPlan
from app.dto.context import ExecutionContext, PromptContext

class PlanningStrategy(ABC):
    """Abstract strategy for plan generation."""

    @abstractmethod
    async def create_plan(self, request: TravelRequest, context: ExecutionContext) -> ExecutionPlan:
        """Create execution plan based on strategy."""
        pass

class ContextBuildingStrategy(ABC):
    """Abstract strategy for building LLM Context."""

    @abstractmethod
    async def build_context(self, context: ExecutionContext) -> ExecutionContext:
        """Enrich and order execution context payload."""
        pass

class PromptRenderingStrategy(ABC):
    """Abstract strategy for rendering final System Prompt."""

    @abstractmethod
    async def render(self, prompt_context: PromptContext, execution_context: ExecutionContext) -> str:
        """Render finalized system prompt string."""
        pass

class ResponseGenerationStrategy(ABC):
    """Abstract strategy for response processing/formatting."""

    @abstractmethod
    async def generate_response(self, context: ExecutionContext) -> TravelResponse:
        """Construct final structured TravelResponse."""
        pass

    @abstractmethod
    async def generate_stream(self, context: ExecutionContext) -> AsyncGenerator[str, None]:
        """Stream chunks for client streaming requests."""
        pass

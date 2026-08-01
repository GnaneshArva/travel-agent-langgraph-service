from abc import ABC, abstractmethod
from typing import AsyncGenerator
from app.dto.context import ExecutionContext
from app.dto.responses import AgentResponse

class BaseAgent(ABC):
    """Abstract interface for all Agent Execution Engines enforcing Dependency Inversion Principle (DIP)."""

    @abstractmethod
    async def run(self, system_prompt: str, user_request: str, context: ExecutionContext) -> AgentResponse:
        """Executes agent workflow and returns AgentResponse DTO."""
        pass

    @abstractmethod
    async def run_stream(self, system_prompt: str, user_request: str, context: ExecutionContext) -> AsyncGenerator[str, None]:
        """Streams agent workflow response chunks."""
        pass

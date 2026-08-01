from abc import ABC, abstractmethod
from typing import Any
from app.dto.tool_dto import ToolExecutionRequest, ToolResult

class ToolProvider(ABC):
    """Abstract interface for MCP Tool Execution."""

    @abstractmethod
    async def execute(self, request: ToolExecutionRequest) -> ToolResult:
        """Execute a single MCP tool call asynchronously."""
        pass

    @abstractmethod
    async def execute_batch(self, requests: list[ToolExecutionRequest]) -> list[ToolResult]:
        """Execute multiple MCP tools in parallel where possible."""
        pass

    @abstractmethod
    def get_available_tools(self) -> list[dict[str, Any]]:
        """Return schema definitions of all available tools."""
        pass

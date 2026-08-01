import uuid
from typing import Any
from app.interfaces.tool import ToolProvider
from app.integrations.tools.travel_tools_client import TravelToolsMcpClient
from app.dto.context import ExecutionContext
from app.dto.tool_dto import ToolExecutionRequest, ToolResult
from app.config.settings import settings
from app.utils.logger import logger

class ToolExecutor:
    """Service executing tool requests concurrently with timeout and retry controls."""

    def __init__(self, provider: ToolProvider | None = None):
        self.provider = provider or TravelToolsMcpClient()

    async def execute_tool(self, tool_name: str, arguments: dict[str, Any], context: ExecutionContext) -> ToolResult:
        tool_call_id = f"call-{uuid.uuid4().hex[:8]}"
        req = ToolExecutionRequest(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            mcp_server="travel-mcp-server",
            arguments=arguments,
            timeout_seconds=settings.timeouts.tool_timeout
        )
        res = await self.provider.execute(req)
        context.tool_results.append(res)
        return res

    async def execute_batch(self, tool_calls: list[dict[str, Any]], context: ExecutionContext) -> list[ToolResult]:
        requests = []
        for call in tool_calls:
            tool_call_id = call.get("id", f"call-{uuid.uuid4().hex[:8]}")
            name = call.get("name") or call.get("function", {}).get("name")
            args = call.get("arguments") or call.get("function", {}).get("arguments", {})
            if isinstance(args, str):
                import json
                try:
                    args = json.loads(args)
                except Exception:
                    args = {}
            requests.append(
                ToolExecutionRequest(
                    tool_call_id=tool_call_id,
                    tool_name=name,
                    mcp_server="travel-mcp-server",
                    arguments=args,
                    timeout_seconds=settings.timeouts.tool_timeout
                )
            )

        logger.info(f"Executing batch of {len(requests)} tools", component="ToolExecutor", session_id=context.session_id)
        results = await self.provider.execute_batch(requests)
        context.tool_results.extend(results)
        return results

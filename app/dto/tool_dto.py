from typing import Any
from pydantic import BaseModel, Field

class ToolExecutionRequest(BaseModel):
    tool_call_id: str
    tool_name: str
    mcp_server: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: float = 15.0

class ToolError(BaseModel):
    tool_name: str
    error_code: str
    message: str
    retryable: bool = False

class ToolResult(BaseModel):
    tool_call_id: str
    tool_name: str
    status: str = "SUCCESS"  # SUCCESS, FAILED, TIMEOUT
    output: Any = None
    error: ToolError | None = None
    execution_time_ms: float = 0.0

class ToolExecutionResponse(BaseModel):
    results: list[ToolResult] = Field(default_factory=list)
    total_tools_executed: int = 0
    successful_count: int = 0
    failed_count: int = 0

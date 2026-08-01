from typing import Any
from pydantic import BaseModel, Field

class PlanStep(BaseModel):
    step_id: int
    name: str
    description: str
    mcp_server: str | None = None
    tool_name: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[int] = Field(default_factory=list)
    can_parallelize: bool = False

class ExecutionStep(BaseModel):
    step_id: int
    name: str
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED, SKIPPED
    result: Any | None = None
    error_message: str | None = None
    execution_time_ms: float = 0.0

class ExecutionMetadata(BaseModel):
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    parallel_batches: int = 0

class ExecutionPlan(BaseModel):
    plan_id: str
    strategy_name: str = "SequentialPlanningStrategy"
    steps: list[PlanStep] = Field(default_factory=list)
    required_mcp_servers: list[str] = Field(default_factory=list)
    expected_output: str = "Comprehensive Travel Itinerary & Recommendation"
    estimated_tool_count: int = 0
    estimated_cost: float = 0.005

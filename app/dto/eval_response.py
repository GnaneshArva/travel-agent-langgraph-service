from typing import Any
from pydantic import BaseModel, Field


class EvalRequest(BaseModel):
    """Evaluation request sent by the agentic-ai-evals platform."""
    user_prompt: str = Field(..., description="The natural-language prompt to evaluate")
    user_id: str = Field(default="eval-user", description="User ID for the evaluation session")
    destination: str = Field(default="", description="Destination extracted or provided for planning")
    duration_days: int = Field(default=5, description="Trip duration in days")
    budget: float | None = Field(default=None, description="Optional budget constraint")
    currency: str = Field(default="USD", description="Currency code")
    is_jailbreak_attempt: bool = Field(default=False, description="Flag indicating adversarial prompt")
    schema_definition: dict[str, Any] | None = Field(default=None, description="Expected JSON schema for structured output validation")


class PerformanceTrace(BaseModel):
    total_latency_ms: float = 0.0
    llm_latency_ms: float = 0.0
    tool_latency_ms: float = 0.0
    retrieval_latency_ms: float = 0.0


class CostTrace(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    embedding_tokens: int = 0
    total_cost_usd: float = 0.0
    average_cost_per_token_usd: float = 0.0


class EvalTraceResponse(BaseModel):
    """Full execution trace returned to the evaluator after running the agent."""
    agent_name: str = "TravelPlannerAgent-v2"
    agent_response: str = Field(default="", description="Final text response from the agent")
    tool_calls: list[dict[str, Any]] = Field(default_factory=list, description="Tools invoked during execution")
    retrieved_doc_ids: list[str] = Field(default_factory=list, description="IDs of RAG documents retrieved")
    retrieved_contexts: list[str] = Field(default_factory=list, description="Content of retrieved documents")
    citations: list[str] = Field(default_factory=list, description="Citations referenced in response")
    planning_steps: list[str] = Field(default_factory=list, description="Execution plan step names in order")
    structured_output: dict[str, Any] | None = Field(default=None, description="Structured JSON output if applicable")
    performance: PerformanceTrace = Field(default_factory=PerformanceTrace)
    cost: CostTrace = Field(default_factory=CostTrace)

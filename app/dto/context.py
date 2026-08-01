from typing import Any
from pydantic import BaseModel, Field
from app.dto.planning_dto import ExecutionPlan
from app.dto.tool_dto import ToolResult

class PromptContext(BaseModel):
    template_name: str = "travel_agent_system"
    rendered_prompt: str = ""
    system_instruction: str = ""
    variables: dict[str, Any] = Field(default_factory=dict)

class MemoryContext(BaseModel):
    user_preferences: dict[str, Any] = Field(default_factory=dict)
    past_trips: list[dict[str, Any]] = Field(default_factory=list)
    dietary_preferences: list[str] = Field(default_factory=list)
    hotel_preferences: list[str] = Field(default_factory=list)
    airline_preferences: list[str] = Field(default_factory=list)
    recent_history: list[dict[str, Any]] = Field(default_factory=list)

class KnowledgeContext(BaseModel):
    destination_guides: list[dict[str, Any]] = Field(default_factory=list)
    visa_information: dict[str, Any] = Field(default_factory=dict)
    weather_info: dict[str, Any] = Field(default_factory=dict)
    local_customs: list[str] = Field(default_factory=list)
    advisories: list[str] = Field(default_factory=list)

class ReasoningContext(BaseModel):
    thought_process: list[str] = Field(default_factory=list)
    tool_justifications: dict[str, str] = Field(default_factory=dict)
    planning_reasoning: str = ""

class ObservationContext(BaseModel):
    events: list[dict[str, Any]] = Field(default_factory=list)
    start_time_iso: str = ""
    end_time_iso: str = ""
    total_tokens: int = 0
    estimated_cost: float = 0.0

class ExecutionContext(BaseModel):
    session_id: str
    user_id: str
    conversation_id: str
    request_id: str
    trace_id: str
    user_request: str
    
    # Enrichment fields
    prompt_context: PromptContext = Field(default_factory=PromptContext)
    memory_context: MemoryContext = Field(default_factory=MemoryContext)
    knowledge_context: KnowledgeContext = Field(default_factory=KnowledgeContext)
    execution_plan: ExecutionPlan | None = None
    tool_results: list[ToolResult] = Field(default_factory=list)
    agent_raw_response: str = ""
    reasoning_context: ReasoningContext = Field(default_factory=ReasoningContext)
    observation_context: ObservationContext = Field(default_factory=ObservationContext)
    metadata: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)

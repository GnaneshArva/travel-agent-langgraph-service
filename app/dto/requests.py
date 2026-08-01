from typing import Any
from pydantic import BaseModel, Field

class TravelRequest(BaseModel):
    user_id: str = Field(..., description="Unique ID of the user requesting travel planning")
    destination: str = Field(..., description="Destination country or city")
    duration_days: int = Field(default=5, description="Length of travel in days")
    budget: float | None = Field(default=None, description="Budget in local currency")
    currency: str = Field(default="USD", description="Currency code (e.g. USD, EUR, INR)")
    travel_dates: str | None = Field(default=None, description="Target travel dates or season")
    additional_notes: str | None = Field(default=None, description="Specific user preferences or instructions")
    session_id: str | None = Field(default=None, description="Optional existing session ID")
    conversation_id: str | None = Field(default=None, description="Optional existing conversation ID")

class ConversationRequest(BaseModel):
    conversation_id: str
    user_id: str
    message: str

class AgentRequest(BaseModel):
    system_prompt: str
    user_message: str
    tools_available: list[dict[str, Any]] = Field(default_factory=list)
    temperature: float = 0.7
    max_tokens: int = 4096

class PlanningRequest(BaseModel):
    user_request: str
    destination: str
    has_memory: bool = True
    has_knowledge: bool = True

class ToolRequest(BaseModel):
    tool_name: str
    mcp_server: str
    arguments: dict[str, Any] = Field(default_factory=dict)

class MemoryRequest(BaseModel):
    user_id: str
    query: str | None = None
    limit: int = 10

class KnowledgeRequest(BaseModel):
    destination: str
    query_topics: list[str] = Field(default_factory=lambda: ["guides", "visa", "weather", "customs"])

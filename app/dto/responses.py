from typing import Any
from pydantic import BaseModel, Field

class FlightOption(BaseModel):
    airline: str
    flight_number: str
    origin: str
    destination: str
    departure_time: str
    price: float
    currency: str = "USD"

class HotelOption(BaseModel):
    name: str
    rating: float
    price_per_night: float
    location: str
    amenities: list[str] = Field(default_factory=list)

class DailyItinerary(BaseModel):
    day: int
    title: str
    activities: list[str] = Field(default_factory=list)
    dining_recommendations: list[str] = Field(default_factory=list)

class TravelResponse(BaseModel):
    session_id: str
    conversation_id: str
    request_id: str
    status: str = "SUCCESS"
    destination: str
    duration_days: int
    summary: str
    itinerary: list[DailyItinerary] = Field(default_factory=list)
    flights: list[FlightOption] = Field(default_factory=list)
    hotels: list[HotelOption] = Field(default_factory=list)
    estimated_total_cost: float = 0.0
    currency: str = "USD"
    warnings: list[str] = Field(default_factory=list)
    applied_preferences: list[str] = Field(default_factory=list)
    execution_time_ms: float = 0.0

class AgentResponse(BaseModel):
    content: str
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    finish_reason: str = "stop"

class PlanningResponse(BaseModel):
    plan_id: str
    steps_count: int
    strategy: str

class ToolResponse(BaseModel):
    tool_name: str
    status: str
    output: Any

class MemoryResponse(BaseModel):
    user_id: str
    preferences: dict[str, Any] = Field(default_factory=dict)
    history_found: bool = False

class KnowledgeResponse(BaseModel):
    destination: str
    found: bool = True
    documents: list[dict[str, Any]] = Field(default_factory=list)

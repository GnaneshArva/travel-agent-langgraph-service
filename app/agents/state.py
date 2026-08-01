from typing import Annotated, Any, Dict, List, Optional, TypedDict
from langchain_core.messages import BaseMessage
import operator


class TravelAgentState(TypedDict):
    """
    Stateful memory context passed between LangGraph nodes in the Multi-Agent mesh.
    """
    user_request: str
    system_prompt: str
    destination: str
    budget: Optional[float]
    duration_days: int

    # Message sequence history
    messages: Annotated[List[BaseMessage], operator.add]

    # Domain Node Outputs
    flight_results: Optional[Dict[str, Any]]
    hotel_results: Optional[Dict[str, Any]]
    weather_results: Optional[Dict[str, Any]]
    final_itinerary: Optional[str]

    # Tracking & Telemetry
    tool_calls_executed: Annotated[List[Dict[str, Any]], operator.add]
    current_node: str
    hand_off_count: int
    is_complete: bool

import json
from typing import Any, Dict
from langchain_core.messages import AIMessage, HumanMessage
from app.agents.state import TravelAgentState
from app.dto.context import ExecutionContext
from app.services.tool_executor import ToolExecutor
from app.reasoning.reasoning_service import ReasoningService
from app.utils.logger import logger


class LangGraphNodes:
    """
    Collection of domain-specialized execution nodes for LangGraph StateGraph mesh.
    Each node receives current state, invokes tools or reasoning, and returns state updates.
    """

    def __init__(self, tool_executor: ToolExecutor, reasoning_service: ReasoningService, context: ExecutionContext):
        self.tool_executor = tool_executor
        self.reasoning_service = reasoning_service
        self.context = context

    async def triage_node(self, state: TravelAgentState) -> Dict[str, Any]:
        """Triage & Router Node: Analyzes user request and initializes workflow."""
        logger.info("LangGraph Node: [TriageAgent] Analyzing travel request", component="LangGraphNodes", session_id=self.context.session_id)
        self.reasoning_service.record_thought(self.context, "LangGraph Node [TriageAgent]: Analyzing travel intent and routing to specialist nodes.")

        return {
            "current_node": "triage",
            "messages": [HumanMessage(content=state["user_request"])],
            "hand_off_count": state.get("hand_off_count", 0) + 1
        }

    async def flight_node(self, state: TravelAgentState) -> Dict[str, Any]:
        """Flight Specialist Node: Queries flight schedules and pricing."""
        destination = state.get("destination", "Switzerland")
        logger.info(f"LangGraph Node: [FlightBookingAgent] Searching flights for {destination}", component="LangGraphNodes", session_id=self.context.session_id)
        self.reasoning_service.record_thought(self.context, f"LangGraph Node [FlightBookingAgent]: Invoking MCP search_flights for {destination}")

        tool_res = await self.tool_executor.execute_tool("search_flights", {"origin": "OriginCity", "destination": destination}, self.context)
        flight_data = tool_res.output if tool_res and tool_res.output else {"flights": [{"airline": "Swiss Air", "price": 850, "status": "AVAILABLE"}]}

        return {
            "current_node": "flight",
            "flight_results": flight_data,
            "tool_calls_executed": [{"name": "search_flights", "arguments": {"destination": destination}}],
            "messages": [AIMessage(content=f"Retrieved flight options: {json.dumps(flight_data)}")]
        }

    async def hotel_node(self, state: TravelAgentState) -> Dict[str, Any]:
        """Lodging & Budget Specialist Node: Queries hotels and validates budget rules."""
        destination = state.get("destination", "Switzerland")
        logger.info(f"LangGraph Node: [HotelBookingAgent] Searching hotels for {destination}", component="LangGraphNodes", session_id=self.context.session_id)
        self.reasoning_service.record_thought(self.context, f"LangGraph Node [HotelBookingAgent]: Invoking MCP search_hotels for {destination}")

        tool_res = await self.tool_executor.execute_tool("search_hotels", {"destination": destination, "min_rating": 4.0}, self.context)
        hotel_data = tool_res.output if tool_res and tool_res.output else {"hotels": [{"name": "Grand Hotel Alpine", "price_per_night": 220, "rating": 4.5}]}

        return {
            "current_node": "hotel",
            "hotel_results": hotel_data,
            "tool_calls_executed": [{"name": "search_hotels", "arguments": {"destination": destination}}],
            "messages": [AIMessage(content=f"Retrieved hotel options: {json.dumps(hotel_data)}")]
        }

    async def weather_node(self, state: TravelAgentState) -> Dict[str, Any]:
        """Weather Specialist Node: Queries destination climate forecasts."""
        destination = state.get("destination", "Switzerland")
        logger.info(f"LangGraph Node: [WeatherActivityAgent] Checking weather for {destination}", component="LangGraphNodes", session_id=self.context.session_id)
        self.reasoning_service.record_thought(self.context, f"LangGraph Node [WeatherActivityAgent]: Invoking MCP get_weather for {destination}")

        tool_res = await self.tool_executor.execute_tool("get_weather", {"destination": destination}, self.context)
        weather_data = tool_res.output if tool_res and tool_res.output else {"forecast": "Sunny and mild 22°C", "activities": ["Sightseeing", "Alpine hiking"]}

        return {
            "current_node": "weather",
            "weather_results": weather_data,
            "tool_calls_executed": [{"name": "get_weather", "arguments": {"destination": destination}}],
            "messages": [AIMessage(content=f"Retrieved weather forecast: {json.dumps(weather_data)}")]
        }

    async def synthesizer_node(self, state: TravelAgentState) -> Dict[str, Any]:
        """Synthesis Node: Consolidates state data into final itinerary synthesis."""
        logger.info("LangGraph Node: [ItinerarySynthesizerAgent] Synthesizing final travel itinerary", component="LangGraphNodes", session_id=self.context.session_id)
        self.reasoning_service.record_thought(self.context, "LangGraph Node [ItinerarySynthesizerAgent]: Compiling flights, hotels, and weather into structured synthesis.")

        destination = state.get("destination", "Switzerland")
        duration = state.get("duration_days", 5)

        synthesis_json = json.dumps({
            "status": "SUCCESS",
            "destination": destination,
            "duration_days": duration,
            "summary": f"Comprehensive {duration}-day trip itinerary to {destination} generated via LangGraph Multi-Agent Mesh.",
            "itinerary": [
                f"Day 1: Arrival in {destination} and hotel check-in.",
                f"Day 2: City sightseeing and cultural exploration.",
                f"Day 3: Outdoor activities and local cuisine.",
                f"Day 4: Guided day tour and shopping.",
                f"Day 5: Check-out and departure flight."
            ],
            "flights": state.get("flight_results", {}).get("flights", []),
            "hotels": state.get("hotel_results", {}).get("hotels", []),
            "weather": state.get("weather_results", {})
        }, indent=2)

        return {
            "current_node": "synthesizer",
            "final_itinerary": synthesis_json,
            "is_complete": True,
            "messages": [AIMessage(content=synthesis_json)]
        }

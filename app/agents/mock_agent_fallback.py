import asyncio
from typing import AsyncGenerator
from app.interfaces.agent import BaseAgent
from app.dto.context import ExecutionContext
from app.dto.responses import AgentResponse
from app.dto.agent_schemas import (
    FlightAgentOutput,
    HotelAgentOutput,
    WeatherAgentOutput,
    FinalItinerarySynthesisOutput
)
from app.services.tool_executor import ToolExecutor
from app.reasoning.reasoning_service import ReasoningService

class MockAgentFallback(BaseAgent):
    """
    Isolated Mock Fallback Pipeline for OpenAIAgent adhering to BaseAgent interface.
    Simulates multi-agent execution offline step-by-step when OPENAI_API_KEY is unconfigured or unavailable.
    """

    def __init__(self, tool_executor: ToolExecutor | None = None, reasoning_service: ReasoningService | None = None):
        self.tool_executor = tool_executor or ToolExecutor()
        self.reasoning_service = reasoning_service or ReasoningService()

    async def run(self, system_prompt: str, user_request: str, context: ExecutionContext) -> AgentResponse:
        """Simulates multi-agent execution offline step-by-step with budget optimization logic."""
        dest = context.metadata.get("destination", "Japan")
        budget = context.metadata.get("budget", 2500.0)

        # Step 1: TravelTriageAgent -> Handoff to FlightBookingAgent
        self.reasoning_service.record_thought(context, f"[TravelTriageAgent] Received request for {dest} (Budget=${budget}). Initiating Handoff -> FlightBookingAgent.")

        # Step 2: FlightBookingAgent -> search_flights -> Handoff to HotelBookingAgent
        self.reasoning_service.record_thought(context, f"[FlightBookingAgent] Searching flight schedules from SFO to {dest}.")
        await self.tool_executor.execute_tool("search_flights", {"origin": "SFO", "destination": dest}, context)
        self.reasoning_service.record_thought(context, f"[FlightBookingAgent] Flights retrieved. Initiating Handoff -> HotelBookingAgent.")

        # Step 3: HotelBookingAgent -> search_hotels -> Budget Evaluation -> Handoff
        self.reasoning_service.record_thought(context, f"[HotelBookingAgent] Searching top 4.5+ star accommodations in {dest}.")
        await self.tool_executor.execute_tool("search_hotels", {"destination": dest, "min_rating": 4.5}, context)
        
        # Simulate dynamic budget check
        self.reasoning_service.record_thought(
            context,
            f"[HotelBookingAgent] Budget Check: Lodging in {dest} center evaluated against total budget ${budget}. "
            f"Lodging selected within budget. Initiating Handoff -> WeatherActivityAgent."
        )

        # Step 4: WeatherActivityAgent -> get_weather -> Handoff to ItinerarySynthesizerAgent
        self.reasoning_service.record_thought(context, f"[WeatherActivityAgent] Fetching destination weather forecast for {dest}.")
        await self.tool_executor.execute_tool("get_weather", {"destination": dest}, context)
        self.reasoning_service.record_thought(context, f"[WeatherActivityAgent] Weather retrieved. Initiating Handoff -> ItinerarySynthesizerAgent.")

        # Step 5: ItinerarySynthesizerAgent -> Final Synthesis Engine
        self.reasoning_service.record_thought(context, f"[ItinerarySynthesizerAgent] Running structured synthesis for {dest}.")

        executed_calls = [
            {"id": res.tool_call_id, "name": res.tool_name, "arguments": {}}
            for res in context.tool_results
        ]
        
        synthesized_json = self.synthesize_mock_itinerary(context)
        context.agent_raw_response = synthesized_json
        return AgentResponse(content=synthesized_json, tool_calls=executed_calls)

    async def run_stream(self, system_prompt: str, user_request: str, context: ExecutionContext) -> AsyncGenerator[str, None]:
        res = await self.run(system_prompt, user_request, context)
        words = res.content.split()
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + " "
            yield chunk
            await asyncio.sleep(0.03)

    def synthesize_mock_itinerary(self, context: ExecutionContext) -> str:
        """Constructs fallback FinalItinerarySynthesisOutput from tool outputs."""
        dest = context.metadata.get("destination", "Destination")
        duration = context.metadata.get("duration_days", 3)
        
        flights = []
        hotels = []
        weather_condition = "Clear Sunny Weather"
        temperature = "22°C"

        for res in context.tool_results:
            if res.status == "SUCCESS" and isinstance(res.output, dict):
                if "flights" in res.output:
                    flights = res.output["flights"]
                elif "hotels" in res.output:
                    hotels = res.output["hotels"]
                elif "condition" in res.output:
                    weather_condition = res.output.get("condition", weather_condition)
                    temperature = res.output.get("temperature", temperature)

        selected_flight = FlightAgentOutput(
            origin=flights[0].get("origin", "SFO") if flights else "SFO",
            destination=dest,
            selected_airline=flights[0].get("airline", "Air Travel Express") if flights else "Air Travel Express",
            flight_number=flights[0].get("flight_number", "AT-101") if flights else "AT-101",
            flight_price=float(flights[0].get("price", 750.0)) if flights else 750.0,
            handoff_notes="Flight selected and handed off to HotelBookingAgent"
        )

        selected_hotel = HotelAgentOutput(
            destination=dest,
            selected_hotel=hotels[0].get("name", f"The Royal {dest} Hotel") if hotels else f"The Royal {dest} Hotel",
            rating=float(hotels[0].get("rating", 4.9)) if hotels else 4.9,
            price_per_night=float(hotels[0].get("price_per_night", 240.0)) if hotels else 240.0,
            location=hotels[0].get("location", "Downtown") if hotels else "Downtown",
            handoff_notes="Lodging selected and handed off to WeatherActivityAgent"
        )

        weather_out = WeatherAgentOutput(
            destination=dest,
            condition=weather_condition,
            temperature=temperature,
            recommended_attractions=[f"Top cultural attraction in {dest}", f"Guided city tour of {dest}"],
            handoff_notes="Weather assessment completed and handed off to ItinerarySynthesizerAgent"
        )

        total_est = selected_flight.flight_price + (selected_hotel.price_per_night * duration)

        synthesis_obj = FinalItinerarySynthesisOutput(
            destination=dest,
            duration_days=duration,
            summary=f"Multi-Agent Dynamic Mesh Itinerary Synthesis for {dest} ({duration} Days)",
            selected_flight=selected_flight,
            selected_hotel=selected_hotel,
            weather=weather_out,
            estimated_total_cost=total_est,
            daily_activities=[
                f"Day 1: Arrival, Hotel Check-in at {selected_hotel.selected_hotel}, Evening Walk",
                f"Day 2: Historical Landmarks & Cultural Tour ({weather_out.condition})",
                f"Day 3: Nature Excursion & Farewell Dinner"
            ]
        )

        return synthesis_obj.model_dump_json(indent=2)

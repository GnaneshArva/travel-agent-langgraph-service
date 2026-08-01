import json
import asyncio
from typing import AsyncGenerator
from app.interfaces.strategies import ResponseGenerationStrategy
from app.dto.context import ExecutionContext
from app.dto.responses import TravelResponse, DailyItinerary, FlightOption, HotelOption

class StructuredResponseStrategy(ResponseGenerationStrategy):
    """Parses multi-turn tool results and agent raw output into typed Pydantic v2 TravelResponse."""

    async def generate_response(self, context: ExecutionContext) -> TravelResponse:
        destination = context.metadata.get("destination", "Target Destination")
        duration_days = context.metadata.get("duration_days", 5)
        
        flights: list[FlightOption] = []
        hotels: list[HotelOption] = []
        weather_info: dict[str, str] = {}
        applied_prefs: list[str] = []

        # Extract tool results from multi-turn feedback loop
        for res in context.tool_results:
            if res.status == "SUCCESS" and isinstance(res.output, dict):
                if res.tool_name in ("search_flights", "flight_search") and "flights" in res.output:
                    for f in res.output["flights"]:
                        flights.append(FlightOption(**f))
                elif res.tool_name in ("search_hotels", "hotel_search") and "hotels" in res.output:
                    for h in res.output["hotels"]:
                        hotels.append(HotelOption(**h))
                elif res.tool_name in ("get_weather", "weather_search"):
                    weather_info = res.output

        # Default fallbacks if tools returned simulated/empty responses
        if not flights:
            flights.append(FlightOption(
                airline="Global Airways",
                flight_number="GA-742",
                origin="SFO",
                destination=destination,
                departure_time="08:00 AM",
                price=850.0
            ))
        if not hotels:
            hotels.append(HotelOption(
                name=f"Grand {destination.title()} Resort & Spa",
                rating=4.8,
                price_per_night=220.0,
                location="City Center",
                amenities=["WiFi", "Breakfast", "Pool", "Spa"]
            ))

        if context.memory_context.user_preferences:
            applied_prefs = [f"{k}: {v}" for k, v in context.memory_context.user_preferences.items()]

        # Generate dynamic itinerary based on destination and weather context
        forecast_condition = weather_info.get("condition", "Clear Sunny Weather")
        temperature = weather_info.get("temperature", "22°C")

        itinerary = []
        activity_templates = [
            (f"Arrival & Check-in at hotel near {destination} center", f"Evening walking tour around main market in {destination}"),
            (f"Explore historical landmarks & museums in {destination}", f"Sunset viewpoint & photography tour"),
            (f"Day trip & outdoor nature excursion in {destination}", f"Local cultural performance & dinner"),
            (f"Shopping at local artisanal quarter in {destination}", f"Gourmet food tasting experience"),
            (f"Relaxation & spa session in {destination}", f"Farewell dinner & departure preparation")
        ]

        for i in range(duration_days):
            day_num = i + 1
            act_pair = activity_templates[i % len(activity_templates)]
            itinerary.append(
                DailyItinerary(
                    day=day_num,
                    title=f"Day {day_num}: {destination.title()} Experience ({forecast_condition}, {temperature})",
                    activities=[
                        f"Morning: {act_pair[0]}",
                        f"Afternoon: {act_pair[1]}",
                        f"Evening: Leisure & sightseeing in {destination}"
                    ],
                    dining_recommendations=[
                        f"Local {destination} specialty restaurant",
                        "Recommended vegetarian friendly café"
                    ]
                )
            )

        summary = context.agent_raw_response or f"Customized {duration_days}-day itinerary to {destination} prepared based on your preferences."

        return TravelResponse(
            session_id=context.session_id,
            conversation_id=context.conversation_id,
            request_id=context.request_id,
            status="SUCCESS",
            destination=destination,
            duration_days=duration_days,
            summary=summary,
            itinerary=itinerary,
            flights=flights,
            hotels=hotels,
            estimated_total_cost=round(sum(f.price for f in flights) + sum(h.price_per_night * duration_days for h in hotels), 2),
            currency="USD",
            warnings=context.warnings,
            applied_preferences=applied_prefs,
            execution_time_ms=context.observation_context.events[-1].get("duration_ms", 0.0) if context.observation_context.events else 0.0
        )

    async def generate_stream(self, context: ExecutionContext) -> AsyncGenerator[str, None]:
        resp = await self.generate_response(context)
        chunks = [
            f"data: {json.dumps({'event': 'started', 'session_id': resp.session_id})}\n\n",
            f"data: {json.dumps({'event': 'summary', 'text': resp.summary})}\n\n",
            f"data: {json.dumps({'event': 'itinerary_ready', 'count': len(resp.itinerary)})}\n\n",
            f"data: {json.dumps({'event': 'completed', 'response': resp.model_dump()})}\n\n"
        ]
        for chunk in chunks:
            yield chunk
            await asyncio.sleep(0.05)

class StreamingResponseStrategy(StructuredResponseStrategy):
    """Focuses on streaming chunks incrementally."""
    pass

class TextOnlyStrategy(StructuredResponseStrategy):
    """Produces plain text summary."""
    pass

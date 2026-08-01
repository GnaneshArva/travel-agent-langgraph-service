from pydantic import BaseModel, Field

class TriageAgentOutput(BaseModel):
    """Structured output for TravelTriageAgent."""
    destination: str = Field(description="Target destination city or country")
    duration_days: int = Field(description="Trip duration in days")
    user_budget: float = Field(description="Estimated user budget limit in USD")
    handoff_reasoning: str = Field(description="Reason for handing off to FlightBookingAgent")

class FlightAgentOutput(BaseModel):
    """Structured output for FlightBookingAgent."""
    origin: str = Field(description="Departure airport code or city")
    destination: str = Field(description="Arrival airport code or city")
    selected_airline: str = Field(description="Chosen airline name")
    flight_number: str = Field(description="Flight identifier code")
    flight_price: float = Field(description="One-way or round-trip ticket price in USD")
    handoff_notes: str = Field(description="Flight selection summary handed off to HotelBookingAgent")

class HotelAgentOutput(BaseModel):
    """Structured output for HotelBookingAgent."""
    destination: str = Field(description="Destination city")
    selected_hotel: str = Field(description="Chosen hotel or resort name")
    rating: float = Field(description="Hotel rating out of 5 stars")
    price_per_night: float = Field(description="Nightly rate in USD")
    location: str = Field(description="Hotel zone or area")
    handoff_notes: str = Field(description="Hotel selection summary handed off to WeatherActivityAgent")

class WeatherAgentOutput(BaseModel):
    """Structured output for WeatherActivityAgent."""
    destination: str = Field(description="Destination city")
    condition: str = Field(description="Weather forecast condition")
    temperature: str = Field(description="Average temperature forecast")
    recommended_attractions: list[str] = Field(description="List of top local attractions matching weather")
    handoff_notes: str = Field(description="Weather advisory summary handed off to ItinerarySynthesizerAgent")

class FinalItinerarySynthesisOutput(BaseModel):
    """Structured output for ItinerarySynthesizerAgent."""
    destination: str = Field(description="Final trip destination")
    duration_days: int = Field(description="Duration of the trip")
    summary: str = Field(description="High-level multi-agent synthesis summary")
    selected_flight: FlightAgentOutput = Field(description="Flight details")
    selected_hotel: HotelAgentOutput = Field(description="Hotel details")
    weather: WeatherAgentOutput = Field(description="Weather forecast details")
    estimated_total_cost: float = Field(description="Total estimated cost in USD")
    daily_activities: list[str] = Field(description="Recommended daily activities")

import uuid
from app.interfaces.strategies import PlanningStrategy
from app.dto.requests import TravelRequest
from app.dto.context import ExecutionContext
from app.dto.planning_dto import ExecutionPlan, PlanStep

class SimplePlanningStrategy(PlanningStrategy):
    """Produces a basic 2-step plan."""
    async def create_plan(self, request: TravelRequest, context: ExecutionContext) -> ExecutionPlan:
        steps = [
            PlanStep(step_id=1, name="Search Flights & Hotels", description="Search basic options", mcp_server="travel-mcp-server", can_parallelize=True),
            PlanStep(step_id=2, name="Generate Itinerary", description="Format final plan", mcp_server="travel-mcp-server", depends_on=[1])
        ]
        return ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            strategy_name="SimplePlanningStrategy",
            steps=steps,
            required_mcp_servers=["travel-mcp-server"],
            estimated_tool_count=2,
            estimated_cost=0.002
        )

class SequentialPlanningStrategy(PlanningStrategy):
    """Produces a full sequential 6-step plan."""
    async def create_plan(self, request: TravelRequest, context: ExecutionContext) -> ExecutionPlan:
        steps = [
            PlanStep(step_id=1, name="Retrieve Memory", description="Fetch user preferences & flight history", mcp_server="travel-memory-mcp-server"),
            PlanStep(step_id=2, name="Retrieve Destination Knowledge", description="Fetch destination guides & visa details", mcp_server="travel-knowledge-mcp-server", depends_on=[1]),
            PlanStep(step_id=3, name="Search Flights", description="Find matching flights based on budget & dates", mcp_server="travel-mcp-server", tool_name="search_flights", depends_on=[2]),
            PlanStep(step_id=4, name="Search Hotels", description="Find top 4-star/5-star accommodations", mcp_server="travel-mcp-server", tool_name="search_hotels", depends_on=[3]),
            PlanStep(step_id=5, name="Check Weather & Attractions", description="Find weather forecast and local attractions", mcp_server="travel-mcp-server", tool_name="get_weather", depends_on=[4]),
            PlanStep(step_id=6, name="Generate Final Itinerary", description="Synthesize findings into structured plan", depends_on=[5])
        ]
        return ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            strategy_name="SequentialPlanningStrategy",
            steps=steps,
            required_mcp_servers=["travel-memory-mcp-server", "travel-knowledge-mcp-server", "travel-mcp-server"],
            estimated_tool_count=5,
            estimated_cost=0.005
        )

class ParallelPlanningStrategy(PlanningStrategy):
    """Produces an optimized plan with parallelized independent tool steps."""
    async def create_plan(self, request: TravelRequest, context: ExecutionContext) -> ExecutionPlan:
        steps = [
            PlanStep(step_id=1, name="Retrieve Memory", description="Fetch memory context", mcp_server="travel-memory-mcp-server", can_parallelize=True),
            PlanStep(step_id=2, name="Retrieve Knowledge", description="Fetch destination context", mcp_server="travel-knowledge-mcp-server", can_parallelize=True),
            PlanStep(step_id=3, name="Search Flights", description="Search flight options", mcp_server="travel-mcp-server", tool_name="search_flights", can_parallelize=True),
            PlanStep(step_id=4, name="Search Hotels", description="Search hotel options", mcp_server="travel-mcp-server", tool_name="search_hotels", can_parallelize=True),
            PlanStep(step_id=5, name="Check Weather", description="Get weather data", mcp_server="travel-mcp-server", tool_name="get_weather", can_parallelize=True),
            PlanStep(step_id=6, name="Consolidate & Generate", description="Synthesize all parallel results", depends_on=[1, 2, 3, 4, 5])
        ]
        return ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            strategy_name="ParallelPlanningStrategy",
            steps=steps,
            required_mcp_servers=["travel-memory-mcp-server", "travel-knowledge-mcp-server", "travel-mcp-server"],
            estimated_tool_count=5,
            estimated_cost=0.004
        )

class CostOptimizedPlanningStrategy(PlanningStrategy):
    """Minimizes tool calls to lower API latency and cost."""
    async def create_plan(self, request: TravelRequest, context: ExecutionContext) -> ExecutionPlan:
        steps = [
            PlanStep(step_id=1, name="Direct Travel Search", description="Execute consolidated query", mcp_server="travel-mcp-server", tool_name="search_travel_bundle"),
            PlanStep(step_id=2, name="Generate Response", description="Synthesize response", depends_on=[1])
        ]
        return ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            strategy_name="CostOptimizedPlanningStrategy",
            steps=steps,
            required_mcp_servers=["travel-mcp-server"],
            estimated_tool_count=1,
            estimated_cost=0.001
        )

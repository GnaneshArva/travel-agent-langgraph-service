from app.interfaces.strategies import PlanningStrategy
from app.factories.planning_factory import PlanningFactory
from app.dto.requests import TravelRequest
from app.dto.context import ExecutionContext
from app.dto.planning_dto import ExecutionPlan
from app.utils.logger import logger

class PlanningService:
    """Service producing execution plan for the requested travel itinerary."""

    def __init__(self, strategy: PlanningStrategy | None = None):
        self.strategy = strategy or PlanningFactory.get_strategy("sequential")

    async def create_plan(self, request: TravelRequest, context: ExecutionContext) -> ExecutionPlan:
        logger.info(
            f"Creating execution plan with strategy {self.strategy.__class__.__name__}",
            component="PlanningService",
            session_id=context.session_id,
            request_id=context.request_id
        )
        plan = await self.strategy.create_plan(request, context)
        context.execution_plan = plan
        return plan

from app.interfaces.strategies import ContextBuildingStrategy
from app.factories.context_factory import ContextFactory
from app.dto.context import ExecutionContext
from app.utils.logger import logger

class ContextBuilder:
    """Builder Pattern for assembling LLM Execution Context."""

    def __init__(self, strategy: ContextBuildingStrategy | None = None):
        self.strategy = strategy or ContextFactory.get_strategy("hybrid")

    async def build(self, context: ExecutionContext) -> ExecutionContext:
        logger.info(f"Assembling context with strategy {self.strategy.__class__.__name__}", component="ContextBuilder")
        return await self.strategy.build_context(context)

from app.builders.context_builder import ContextBuilder
from app.dto.context import ExecutionContext
from app.utils.logger import logger

class ContextService:
    """Service responsible for context pipeline engineering."""

    def __init__(self, builder: ContextBuilder | None = None):
        self.builder = builder or ContextBuilder()

    async def build_context(self, context: ExecutionContext) -> ExecutionContext:
        logger.info("ContextService building execution context pipeline", component="ContextService")
        return await self.builder.build(context)

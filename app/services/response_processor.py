from typing import AsyncGenerator
from app.interfaces.strategies import ResponseGenerationStrategy
from app.strategies.response import StructuredResponseStrategy
from app.integrations.platform_facade import PlatformFacade
from app.dto.context import ExecutionContext
from app.dto.responses import TravelResponse
from app.utils.logger import logger

class ResponseProcessor:
    """Service responsible for formatting, post-processing, and output guardrail validation."""

    def __init__(self, strategy: ResponseGenerationStrategy | None = None, facade: PlatformFacade | None = None):
        self.strategy = strategy or StructuredResponseStrategy()
        self.facade = facade or PlatformFacade()

    async def process_response(self, context: ExecutionContext) -> TravelResponse:
        logger.info("Processing structured response", component="ResponseProcessor", session_id=context.session_id)
        response = await self.strategy.generate_response(context)

        # Output Guardrail validation
        is_allowed, sanitized_summary, meta = await self.facade.validate_output_guardrails(
            text=response.summary,
            session_id=context.session_id
        )
        if not is_allowed:
            logger.warning("Output guardrail flagged response. Applying redaction.", component="ResponseProcessor")
            response.summary = sanitized_summary
            response.warnings.append("Output was modified by security policy.")

        return response

    async def process_stream(self, context: ExecutionContext) -> AsyncGenerator[str, None]:
        logger.info("Processing streaming response", component="ResponseProcessor", session_id=context.session_id)
        async for chunk in self.strategy.generate_stream(context):
            yield chunk

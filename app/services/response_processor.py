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
            logger.warning("Output guardrail flagged response. Applying redaction/remediation.", component="ResponseProcessor")
            response.summary = sanitized_summary
            response.warnings.append("Output was modified by security/coherence policy.")
        elif meta and "violations" in meta:
            for v in meta.get("violations", []):
                g_name = v.get("guardrail_name", "")
                if "Coherence" in g_name or "coherence" in str(v).lower():
                    logger.info("Coherence warning detected on output response", component="ResponseProcessor")
                    response.warnings.append("Output coherence warning: Logical sequence or transition check triggered remediation.")
                elif "Risk" in g_name or "approval" in str(v).lower():
                    logger.warning("HITL Approval required detected in output guardrails", component="ResponseProcessor")
                    response.requires_human_approval = True
                    response.status = "AWAITING_HUMAN_APPROVAL"
                    response.warnings.append("Action paused: Human approval required before booking or payment.")
                    details = v.get("details", {})
                    response.approval_request = {
                        "approval_id": f"appr_{context.session_id[:8]}",
                        "action_type": "BOOKING_AND_PAYMENT",
                        "risk_level": details.get("risk_level", "HIGH"),
                        "amount_usd": response.estimated_total_cost,
                        "reason": v.get("message", "Human approval required before finalizing reservation."),
                        "payload": {"destination": response.destination, "cost": response.estimated_total_cost}
                    }

        return response

    async def process_stream(self, context: ExecutionContext) -> AsyncGenerator[str, None]:
        logger.info("Processing streaming response", component="ResponseProcessor", session_id=context.session_id)
        async for chunk in self.strategy.generate_stream(context):
            yield chunk

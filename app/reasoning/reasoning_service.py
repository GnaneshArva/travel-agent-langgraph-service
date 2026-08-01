from app.dto.context import ExecutionContext
from app.utils.logger import logger

class ReasoningService:
    """Captures agent thoughts, tool choice rationale, and planning traces strictly for observability."""

    def record_thought(self, context: ExecutionContext, thought: str):
        context.reasoning_context.thought_process.append(thought)
        logger.info(f"Reasoning Step: {thought}", component="ReasoningService", session_id=context.session_id)

    def record_tool_justification(self, context: ExecutionContext, tool_name: str, justification: str):
        context.reasoning_context.tool_justifications[tool_name] = justification
        logger.info(f"Tool Selection Justification ({tool_name}): {justification}", component="ReasoningService", session_id=context.session_id)

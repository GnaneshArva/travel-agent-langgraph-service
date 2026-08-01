from app.interfaces.strategies import PromptRenderingStrategy
from app.factories.prompt_factory import PromptFactory
from app.dto.context import ExecutionContext, PromptContext
from app.utils.logger import logger

class PromptBuilder:
    """Builder Pattern for constructing system prompts."""

    def __init__(self, strategy: PromptRenderingStrategy | None = None):
        self.strategy = strategy or PromptFactory.get_strategy("policy_aware")

    async def build(self, prompt_context: PromptContext, execution_context: ExecutionContext) -> str:
        logger.info(f"Building system prompt with strategy {self.strategy.__class__.__name__}", component="PromptBuilder")
        rendered = await self.strategy.render(prompt_context, execution_context)
        prompt_context.system_instruction = rendered
        return rendered

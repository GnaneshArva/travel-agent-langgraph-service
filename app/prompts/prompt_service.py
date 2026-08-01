from app.builders.prompt_builder import PromptBuilder
from app.dto.context import ExecutionContext, PromptContext
from app.utils.logger import logger

class PromptService:
    """Service responsible for requesting templates and rendering prompt contexts."""

    def __init__(self, builder: PromptBuilder | None = None):
        self.builder = builder or PromptBuilder()

    async def render_prompt(self, prompt_context: PromptContext, execution_context: ExecutionContext) -> str:
        logger.info("PromptService rendering system prompt", component="PromptService")
        return await self.builder.build(prompt_context, execution_context)

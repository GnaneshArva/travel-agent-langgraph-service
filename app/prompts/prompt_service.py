from app.builders.prompt_builder import PromptBuilder
from app.dto.context import ExecutionContext, PromptContext
from app.prompts.prompt_cache import prompt_cache
from app.utils.logger import logger

class PromptService:
    """Service responsible for requesting templates and rendering prompt contexts with PromptCache support."""

    def __init__(self, builder: PromptBuilder | None = None):
        self.builder = builder or PromptBuilder()

    async def render_prompt(self, prompt_context: PromptContext, execution_context: ExecutionContext) -> str:
        logger.info(
            "PromptService rendering system prompt",
            component="PromptService",
            cache_stats=prompt_cache.stats
        )
        return await self.builder.build(prompt_context, execution_context)

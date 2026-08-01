from app.interfaces.strategies import PromptRenderingStrategy
from app.dto.context import ExecutionContext, PromptContext

class TemplateStrategy(PromptRenderingStrategy):
    """Renders static prompt template with variable substitution."""
    async def render(self, prompt_context: PromptContext, execution_context: ExecutionContext) -> str:
        base = prompt_context.rendered_prompt or "You are an enterprise AI Travel Planner assistant."
        for key, value in prompt_context.variables.items():
            base = base.replace(f"{{{{{key}}}}}", str(value))
        return base

class DynamicStrategy(PromptRenderingStrategy):
    """Dynamically injects retrieved memory and destination knowledge into system prompt."""
    async def render(self, prompt_context: PromptContext, execution_context: ExecutionContext) -> str:
        base = prompt_context.rendered_prompt or "You are an enterprise AI Travel Planner assistant."
        
        # Inject Memory
        mem = execution_context.memory_context
        pref_str = ", ".join([f"{k}: {v}" for k, v in mem.user_preferences.items()]) if mem.user_preferences else "None specified"
        
        # Inject Knowledge
        know = execution_context.knowledge_context
        advisories_str = "; ".join(know.advisories) if know.advisories else "No active advisories"

        rendered = f"{base}\n\n[USER PREFERENCES]: {pref_str}\n[TRAVEL ADVISORIES]: {advisories_str}"
        return rendered

class PolicyAwareStrategy(PromptRenderingStrategy):
    """Injects corporate travel compliance policy into the rendered prompt."""
    async def render(self, prompt_context: PromptContext, execution_context: ExecutionContext) -> str:
        dynamic_rendered = await DynamicStrategy().render(prompt_context, execution_context)
        policy_header = (
            "\n\n[CORPORATE TRAVEL POLICY ENFORCEMENT]:\n"
            "- Always prioritize economy/business class flights matching user budget limits.\n"
            "- Prefer verified 4-star+ rated accommodations.\n"
            "- Validate visa requirements and local customs for destination safety."
        )
        return dynamic_rendered + policy_header

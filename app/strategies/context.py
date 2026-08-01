from app.interfaces.strategies import ContextBuildingStrategy
from app.dto.context import ExecutionContext

class MinimalContextStrategy(ContextBuildingStrategy):
    """Includes only current user request and prompt."""
    async def build_context(self, context: ExecutionContext) -> ExecutionContext:
        context.metadata["context_strategy"] = "MinimalContextStrategy"
        return context

class ConversationContextStrategy(ContextBuildingStrategy):
    """Includes conversation history and user request."""
    async def build_context(self, context: ExecutionContext) -> ExecutionContext:
        context.metadata["context_strategy"] = "ConversationContextStrategy"
        return context

class MemoryAwareStrategy(ContextBuildingStrategy):
    """Enriches context with user memory and preferences."""
    async def build_context(self, context: ExecutionContext) -> ExecutionContext:
        context.metadata["context_strategy"] = "MemoryAwareStrategy"
        return context

class RagAwareStrategy(ContextBuildingStrategy):
    """Enriches context with retrieved destination knowledge RAG documents."""
    async def build_context(self, context: ExecutionContext) -> ExecutionContext:
        context.metadata["context_strategy"] = "RagAwareStrategy"
        return context

class HybridContextStrategy(ContextBuildingStrategy):
    """
    Full enterprise context pipeline adhering to prompt composition rules:
    System Prompt -> Travel Policies -> Conversation History -> User Memory -> Retrieved Knowledge -> Current Request -> Metadata
    """
    async def build_context(self, context: ExecutionContext) -> ExecutionContext:
        context.metadata["context_strategy"] = "HybridContextStrategy"
        context.metadata["assembly_order"] = [
            "System Prompt",
            "Travel Policies",
            "Conversation History",
            "User Memory",
            "Retrieved Knowledge",
            "Current User Request",
            "Execution Metadata"
        ]
        return context

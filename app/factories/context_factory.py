from app.interfaces.strategies import ContextBuildingStrategy
from app.strategies.context import (
    MinimalContextStrategy,
    ConversationContextStrategy,
    MemoryAwareStrategy,
    RagAwareStrategy,
    HybridContextStrategy,
)

class ContextFactory:
    """Factory to instantiate context building strategies."""
    @staticmethod
    def get_strategy(strategy_type: str = "hybrid") -> ContextBuildingStrategy:
        st = strategy_type.lower()
        if st == "minimal":
            return MinimalContextStrategy()
        elif st == "conversation":
            return ConversationContextStrategy()
        elif st == "memory":
            return MemoryAwareStrategy()
        elif st == "rag":
            return RagAwareStrategy()
        else:
            return HybridContextStrategy()

from app.interfaces.strategies import PromptRenderingStrategy
from app.strategies.prompt import (
    TemplateStrategy,
    DynamicStrategy,
    PolicyAwareStrategy,
)

class PromptFactory:
    """Factory to instantiate prompt rendering strategies."""
    @staticmethod
    def get_strategy(strategy_type: str = "policy_aware") -> PromptRenderingStrategy:
        st = strategy_type.lower()
        if st == "template":
            return TemplateStrategy()
        elif st == "dynamic":
            return DynamicStrategy()
        else:
            return PolicyAwareStrategy()

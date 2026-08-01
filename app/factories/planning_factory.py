from app.interfaces.strategies import PlanningStrategy
from app.strategies.planning import (
    SimplePlanningStrategy,
    SequentialPlanningStrategy,
    ParallelPlanningStrategy,
    CostOptimizedPlanningStrategy,
)

class PlanningFactory:
    """Factory to instantiate planning strategies."""
    @staticmethod
    def get_strategy(strategy_type: str = "sequential") -> PlanningStrategy:
        st = strategy_type.lower()
        if st == "simple":
            return SimplePlanningStrategy()
        elif st == "parallel":
            return ParallelPlanningStrategy()
        elif st == "cost_optimized":
            return CostOptimizedPlanningStrategy()
        else:
            return SequentialPlanningStrategy()

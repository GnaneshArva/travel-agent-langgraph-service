from langgraph.graph import END, StateGraph
from app.agents.state import PlannerState
from app.agents.nodes import LangGraphNodes
from app.config.settings import settings


class LangGraphBuilder:
    """
    Constructs the Goal-Driven Autonomous Reasoning Engine loop topology using LangGraph StateGraph.
    Flow: Planner ──► Executor ──► Reflection ──► Verifier ──► Synthesizer / Loop Back
    """

    def __init__(self, nodes: LangGraphNodes):
        self.nodes = nodes

    def _should_continue_loop(self, state: PlannerState) -> str:
        """Dynamic conditional router determining next action in execution loop."""
        iteration = state.get("iteration_count", 0)
        max_iterations = settings.loop.max_iterations
        progress = state.get("progress_percentage", 0.0)
        is_verified = state.get("is_verified", False)

        # Termination checks
        if state.get("is_complete") or is_verified:
            return "synthesizer"
        if iteration >= max_iterations:
            return "synthesizer"

        # Routing decisions
        curr = state.get("current_node", "")
        if curr == "planner":
            return "executor"
        elif curr == "executor":
            return "reflection"
        elif curr == "reflection":
            return "verifier"
        elif curr == "verifier":
            if is_verified or progress >= 100.0:
                return "synthesizer"
            return "planner"
        return "planner"

    def build_graph(self):
        builder = StateGraph(PlannerState)

        # 1. Register Loop Nodes
        builder.add_node("planner", self.nodes.planner_node)
        builder.add_node("executor", self.nodes.parallel_executor_node)
        builder.add_node("reflection", self.nodes.reflection_node)
        builder.add_node("verifier", self.nodes.independent_verifier_node)
        builder.add_node("synthesizer", self.nodes.synthesizer_node)

        # 2. Set Entry Point
        builder.set_entry_point("planner")

        # 3. Add Edges & Conditional Loop Routing
        builder.add_conditional_edges("planner", self._should_continue_loop, {"executor": "executor", "synthesizer": "synthesizer"})
        builder.add_conditional_edges("executor", self._should_continue_loop, {"reflection": "reflection"})
        builder.add_conditional_edges("reflection", self._should_continue_loop, {"verifier": "verifier"})
        builder.add_conditional_edges("verifier", self._should_continue_loop, {"planner": "planner", "synthesizer": "synthesizer"})
        builder.add_edge("synthesizer", END)

        return builder.compile()

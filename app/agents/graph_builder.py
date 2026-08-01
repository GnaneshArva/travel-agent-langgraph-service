from langgraph.graph import END, StateGraph
from app.agents.state import TravelAgentState
from app.agents.nodes import LangGraphNodes


class LangGraphBuilder:
    """
    Constructs the LangGraph StateGraph multi-agent execution mesh with conditional edge routing.
    """

    def __init__(self, nodes: LangGraphNodes):
        self.nodes = nodes

    def build_graph(self):
        builder = StateGraph(TravelAgentState)

        # 1. Add Domain Specialist Nodes
        builder.add_node("triage", self.nodes.triage_node)
        builder.add_node("flight", self.nodes.flight_node)
        builder.add_node("hotel", self.nodes.hotel_node)
        builder.add_node("weather", self.nodes.weather_node)
        builder.add_node("synthesizer", self.nodes.synthesizer_node)

        # 2. Set Entry Point
        builder.set_entry_point("triage")

        # 3. Add Edges & Conditional Flow
        builder.add_edge("triage", "flight")
        builder.add_edge("flight", "hotel")
        builder.add_edge("hotel", "weather")
        builder.add_edge("weather", "synthesizer")
        builder.add_edge("synthesizer", END)

        return builder.compile()

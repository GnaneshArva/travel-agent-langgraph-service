import asyncio
from typing import AsyncGenerator
from app.interfaces.agent import BaseAgent
from app.dto.context import ExecutionContext
from app.dto.responses import AgentResponse
from app.services.tool_executor import ToolExecutor
from app.reasoning.reasoning_service import ReasoningService
from app.agents.nodes import LangGraphNodes
from app.agents.graph_builder import LangGraphBuilder
from app.agents.mock_agent_fallback import MockAgentFallback
from app.config.settings import settings
from app.utils.logger import logger


class LangGraphAgent(BaseAgent):
    """
    Production Multi-Agent Architecture Service using LangGraph (StateGraph).
    Implements BaseAgent abstract interface (Dependency Inversion Principle).
    Constructs a stateful graph mesh of specialized nodes (Triage, Flight, Hotel, Weather, Synthesizer).
    """

    def __init__(self, tool_executor: ToolExecutor | None = None, reasoning_service: ReasoningService | None = None):
        self.tool_executor = tool_executor or ToolExecutor()
        self.reasoning_service = reasoning_service or ReasoningService()
        self.mock_fallback = MockAgentFallback(self.tool_executor, self.reasoning_service)

    async def run(self, system_prompt: str, user_request: str, context: ExecutionContext) -> AgentResponse:
        """Executes the stateful multi-agent mesh using LangGraph CompiledGraph."""
        logger.info(f"Invoking LangGraph StateGraph Multi-Agent Mesh with model {settings.agent.model}", component="LangGraphAgent", session_id=context.session_id)

        try:
            nodes = LangGraphNodes(self.tool_executor, self.reasoning_service, context)
            graph_builder = LangGraphBuilder(nodes)
            compiled_graph = graph_builder.build_graph()

            initial_state = {
                "user_request": user_request,
                "system_prompt": system_prompt,
                "destination": context.travel_request.destination if context.travel_request else "Switzerland",
                "budget": context.travel_request.budget if context.travel_request else 3000.0,
                "duration_days": context.travel_request.duration_days if context.travel_request else 5,
                "messages": [],
                "flight_results": None,
                "hotel_results": None,
                "weather_results": None,
                "final_itinerary": None,
                "tool_calls_executed": [],
                "current_node": "init",
                "hand_off_count": 0,
                "is_complete": False,
            }

            final_state = await compiled_graph.ainvoke(initial_state)
            output_content = final_state.get("final_itinerary") or "Itinerary synthesis complete."

            context.agent_raw_response = output_content
            executed_calls = final_state.get("tool_calls_executed", [])

            return AgentResponse(content=output_content, tool_calls=executed_calls)

        except Exception as e:
            logger.warning(f"LangGraph Multi-Agent execution failed or in mock fallback ({str(e)}). Delegating to MockAgentFallback pipeline.", component="LangGraphAgent")

        return await self.mock_fallback.run(system_prompt, user_request, context)

    async def run_stream(self, system_prompt: str, user_request: str, context: ExecutionContext) -> AsyncGenerator[str, None]:
        res = await self.run(system_prompt, user_request, context)
        words = res.content.split()
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + " "
            yield chunk
            await asyncio.sleep(0.03)

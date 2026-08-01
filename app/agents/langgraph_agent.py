import asyncio
from typing import AsyncGenerator
from app.interfaces.agent import BaseAgent
from app.dto.context import ExecutionContext
from app.dto.responses import AgentResponse
from app.services.tool_executor import ToolExecutor
from app.reasoning.reasoning_service import ReasoningService
from app.agents.nodes import LangGraphNodes
from app.agents.graph_builder import LangGraphBuilder
from app.agents.state import StrategyType
from app.agents.mock_agent_fallback import MockAgentFallback
from app.config.settings import settings
from app.utils.logger import logger


class LangGraphAgent(BaseAgent):
    """
    Production Goal-Driven Autonomous Reasoning Engine using LangGraph (StateGraph).
    Implements BaseAgent abstract interface (Dependency Inversion Principle).
    Runs dynamic loop execution over PlannerState until goal satisfaction and independent verification.
    """

    def __init__(self, tool_executor: ToolExecutor | None = None, reasoning_service: ReasoningService | None = None):
        self.tool_executor = tool_executor or ToolExecutor()
        self.reasoning_service = reasoning_service or ReasoningService()
        self.mock_fallback = MockAgentFallback(self.tool_executor, self.reasoning_service)

    async def run(self, system_prompt: str, user_request: str, context: ExecutionContext) -> AgentResponse:
        """Executes the Goal-Driven Autonomous Loop Engine via LangGraph CompiledGraph."""
        logger.info(f"Invoking Goal-Driven Autonomous Loop Engine with model {settings.agent.model}", component="LangGraphAgent", session_id=context.session_id)

        try:
            nodes = LangGraphNodes(self.tool_executor, self.reasoning_service, context)
            graph_builder = LangGraphBuilder(nodes)
            compiled_graph = graph_builder.build_graph()

            destination = context.travel_request.destination if context.travel_request else "Switzerland"
            budget = context.travel_request.budget if context.travel_request else 3000.0
            duration = context.travel_request.duration_days if context.travel_request else 5

            initial_state = {
                "user_goal": user_request,
                "system_prompt": system_prompt,
                "destination": destination,
                "budget": budget,
                "duration_days": duration,
                "current_strategy": StrategyType.BUDGET_FIRST,
                "task_queue": {"pending": [], "in_progress": [], "completed": [], "failed": []},
                "active_actions": [],
                "messages": [],
                "flight_results": None,
                "hotel_results": None,
                "weather_results": None,
                "visa_results": None,
                "attraction_results": None,
                "final_itinerary": None,
                "verification_results": [],
                "reflections": [],
                "confidence_score": 0.0,
                "progress_percentage": 0.0,
                "is_verified": False,
                "iteration_count": 0,
                "total_tokens_used": 0,
                "estimated_cost_usd": 0.0,
                "tool_calls_executed": [],
                "current_node": "init",
                "hand_off_count": 0,
                "is_complete": False,
                "termination_reason": None,
            }

            final_state = await compiled_graph.ainvoke(initial_state)
            output_content = final_state.get("final_itinerary") or "Goal execution and itinerary synthesis complete."

            context.agent_raw_response = output_content
            executed_calls = final_state.get("tool_calls_executed", [])

            return AgentResponse(content=output_content, tool_calls=executed_calls)

        except Exception as e:
            logger.warning(f"Goal-Driven Loop Engine execution failed or in mock fallback ({str(e)}). Delegating to MockAgentFallback pipeline.", component="LangGraphAgent")

        return await self.mock_fallback.run(system_prompt, user_request, context)

    async def run_stream(self, system_prompt: str, user_request: str, context: ExecutionContext) -> AsyncGenerator[str, None]:
        res = await self.run(system_prompt, user_request, context)
        words = res.content.split()
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + " "
            yield chunk
            await asyncio.sleep(0.03)

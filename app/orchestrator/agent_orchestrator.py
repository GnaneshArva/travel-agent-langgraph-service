import time
from typing import AsyncGenerator
from app.sessions.session_manager import SessionManager
from app.integrations.platform_facade import PlatformFacade
from app.context.context_service import ContextService
from app.prompts.prompt_service import PromptService
from app.planning.planning_service import PlanningService
from app.reasoning.reasoning_service import ReasoningService
from app.agents.langgraph_agent import LangGraphAgent
from app.services.response_processor import ResponseProcessor
from app.dto.requests import TravelRequest
from app.dto.responses import TravelResponse
from app.exceptions.exceptions import GuardrailException
from app.utils.logger import logger

class AgentOrchestrator:
    """
    Central Orchestrator coordinating the complete enterprise AI Travel Planner request lifecycle.
    No business logic is implemented directly here; all responsibilities are delegated to dedicated services.
    """

    def __init__(
        self,
        session_manager: SessionManager | None = None,
        facade: PlatformFacade | None = None,
        context_service: ContextService | None = None,
        prompt_service: PromptService | None = None,
        planning_service: PlanningService | None = None,
        reasoning_service: ReasoningService | None = None,
        langgraph_agent: LangGraphAgent | None = None,
        response_processor: ResponseProcessor | None = None
    ):
        self.session_manager = session_manager or SessionManager()
        self.facade = facade or PlatformFacade()
        self.context_service = context_service or ContextService()
        self.prompt_service = prompt_service or PromptService()
        self.planning_service = planning_service or PlanningService()
        self.reasoning_service = reasoning_service or ReasoningService()
        self.agent = langgraph_agent or LangGraphAgent()
        self.response_processor = response_processor or ResponseProcessor(facade=self.facade)

    async def execute(self, request: TravelRequest) -> TravelResponse:
        start_time = time.time()
        
        # 1. Initialize Execution Context & Session
        context = self.session_manager.create_execution_context(request)
        
        # Publish Request Received Telemetry
        await self.facade.publish_telemetry("RequestReceived", context.session_id, context.request_id, context.trace_id, {"destination": request.destination})

        # 2. Input Guardrails
        is_allowed, sanitized_text, meta = await self.facade.validate_input_guardrails(request.user_id + " " + request.destination, context.session_id)
        if not is_allowed:
            raise GuardrailException(f"Input request blocked by guardrail policy: {sanitized_text}", correlation_id=context.trace_id)

        # 3. Load Prompt Template & Retrieve Memory & Knowledge
        prompt_ctx = await self.facade.load_prompt_template("travel_agent_system", {"destination": request.destination, "budget": request.budget})
        context.prompt_context = prompt_ctx

        mem_ctx = await self.facade.retrieve_memory(request.user_id)
        context.memory_context = mem_ctx
        await self.facade.publish_telemetry("MemoryRetrieved", context.session_id, context.request_id, context.trace_id, {"keys_found": len(mem_ctx.user_preferences)})

        know_ctx = await self.facade.retrieve_knowledge(request.destination)
        context.knowledge_context = know_ctx
        await self.facade.publish_telemetry("KnowledgeRetrieved", context.session_id, context.request_id, context.trace_id, {"guides_found": len(know_ctx.destination_guides)})

        # 4. Build Context
        context = await self.context_service.build_context(context)
        await self.facade.publish_telemetry("ContextBuilt", context.session_id, context.request_id, context.trace_id, {})

        # 5. Planning Service
        plan = await self.planning_service.create_plan(request, context)
        self.reasoning_service.record_thought(context, f"Created execution plan with {len(plan.steps)} steps using strategy {plan.strategy_name}")
        await self.facade.publish_telemetry("PlanningCompleted", context.session_id, context.request_id, context.trace_id, {"plan_id": plan.plan_id})

        # 6. Render Prompt
        final_system_prompt = await self.prompt_service.render_prompt(prompt_ctx, context)
        await self.facade.publish_telemetry("PromptRendered", context.session_id, context.request_id, context.trace_id, {})

        # 7. OpenAI Agent Execution & Tool Calls
        await self.facade.publish_telemetry("AgentStarted", context.session_id, context.request_id, context.trace_id, {})
        agent_res = await self.agent.run(final_system_prompt, context.user_request, context)
        await self.facade.publish_telemetry("AgentCompleted", context.session_id, context.request_id, context.trace_id, {"tools_executed": len(context.tool_results)})

        # 8. Response Processor & Output Guardrails
        response = await self.response_processor.process_response(context)
        duration_ms = (time.time() - start_time) * 1000
        response.execution_time_ms = round(duration_ms, 2)

        # Record completed event
        context.observation_context.events.append({"event": "RequestCompleted", "duration_ms": duration_ms})
        await self.facade.publish_telemetry("RequestCompleted", context.session_id, context.request_id, context.trace_id, {"duration_ms": duration_ms})

        return response

    async def execute_stream(self, request: TravelRequest) -> AsyncGenerator[str, None]:
        context = self.session_manager.create_execution_context(request)
        prompt_ctx = await self.facade.load_prompt_template("travel_agent_system", {"destination": request.destination})
        context.prompt_context = prompt_ctx
        context.memory_context = await self.facade.retrieve_memory(request.user_id)
        context.knowledge_context = await self.facade.retrieve_knowledge(request.destination)
        context = await self.context_service.build_context(context)
        await self.planning_service.create_plan(request, context)
        final_system_prompt = await self.prompt_service.render_prompt(prompt_ctx, context)

        await self.agent.run(final_system_prompt, context.user_request, context)
        async for chunk in self.response_processor.process_stream(context):
            yield chunk

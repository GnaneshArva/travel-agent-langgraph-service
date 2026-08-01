import time
from fastapi import APIRouter, HTTPException, status
from app.dto.eval_response import EvalRequest, EvalTraceResponse, PerformanceTrace, CostTrace
from app.dto.requests import TravelRequest
from app.orchestrator.agent_orchestrator import AgentOrchestrator
from app.exceptions.exceptions import AgentException, GuardrailException
from app.utils.logger import logger

router = APIRouter(prefix="/api/v1/travel", tags=["Evaluation API"])
eval_router = router
orchestrator = AgentOrchestrator()


@router.post("/evaluate", response_model=EvalTraceResponse, status_code=status.HTTP_200_OK)
async def evaluate_agent(request: EvalRequest) -> EvalTraceResponse:
    """
    Evaluation endpoint for agentic-ai-evals platform.
    Runs the full agent orchestration and returns the complete execution trace
    including tool calls, RAG documents, planning steps, performance and cost metrics.
    """
    start_time = time.perf_counter()

    try:
        # Build a TravelRequest from the eval request
        travel_request = TravelRequest(
            user_id=request.user_id,
            destination=request.destination or _extract_destination(request.user_prompt),
            duration_days=request.duration_days,
            budget=request.budget,
            currency=request.currency,
            additional_notes=request.user_prompt,
        )

        # Execute the full agent orchestration
        context = orchestrator.session_manager.create_execution_context(travel_request)
        context.user_request = request.user_prompt

        # Run through the same orchestration pipeline
        await orchestrator.facade.publish_telemetry(
            "EvalRequestReceived", context.session_id, context.request_id, context.trace_id,
            {"destination": travel_request.destination, "eval_mode": True}
        )

        # Input guardrails
        is_allowed, sanitized_text, meta = await orchestrator.facade.validate_input_guardrails(
            request.user_prompt, context.session_id
        )
        if not is_allowed:
            # Return trace showing guardrail blocked the request
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return EvalTraceResponse(
                agent_response=f"I cannot comply with this request. {sanitized_text}",
                tool_calls=[],
                retrieved_doc_ids=[],
                planning_steps=["block_adversarial_prompt"],
                performance=PerformanceTrace(total_latency_ms=elapsed_ms),
            )

        # Load prompt, memory, knowledge
        prompt_ctx = await orchestrator.facade.load_prompt_template(
            "travel_agent_system", {"destination": travel_request.destination, "budget": travel_request.budget}
        )
        context.prompt_context = prompt_ctx

        mem_ctx = await orchestrator.facade.retrieve_memory(travel_request.user_id)
        context.memory_context = mem_ctx

        know_ctx = await orchestrator.facade.retrieve_knowledge(travel_request.destination)
        context.knowledge_context = know_ctx

        # Build context
        context = await orchestrator.context_service.build_context(context)

        # Planning
        plan = await orchestrator.planning_service.create_plan(travel_request, context)
        orchestrator.reasoning_service.record_thought(
            context, f"Created execution plan with {len(plan.steps)} steps using strategy {plan.strategy_name}"
        )

        # Render prompt
        final_system_prompt = await orchestrator.prompt_service.render_prompt(prompt_ctx, context)

        # Agent execution
        agent_res = await orchestrator.agent.run(final_system_prompt, context.user_request, context)

        # Response processing
        response = await orchestrator.response_processor.process_response(context)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # Map ExecutionContext → EvalTraceResponse
        tool_calls_trace = [
            {
                "name": tr.tool_name,
                "status": tr.status.lower(),
                "args": tr.output if isinstance(tr.output, dict) else {},
                "execution_time_ms": tr.execution_time_ms,
            }
            for tr in context.tool_results
        ]

        planning_steps_trace = [step.name for step in plan.steps] if plan and plan.steps else []

        retrieved_doc_ids = [
            doc.get("id", doc.get("title", f"doc-{i}"))
            for i, doc in enumerate(context.knowledge_context.destination_guides)
        ]

        retrieved_contexts = [
            str(doc) for doc in context.knowledge_context.destination_guides
        ]

        citations = [
            f"Source: {doc_id}" for doc_id in retrieved_doc_ids
        ]

        # Build structured output if schema was expected
        structured_out = None
        if request.schema_definition:
            structured_out = {
                "destination": response.destination,
                "duration_days": response.duration_days,
                "estimated_budget_usd": response.estimated_total_cost,
                "status": response.status,
            }

        tool_latency = sum(tr.execution_time_ms for tr in context.tool_results)

        return EvalTraceResponse(
            agent_response=response.summary,
            tool_calls=tool_calls_trace,
            retrieved_doc_ids=retrieved_doc_ids,
            retrieved_contexts=retrieved_contexts,
            citations=citations,
            planning_steps=planning_steps_trace,
            structured_output=structured_out,
            performance=PerformanceTrace(
                total_latency_ms=round(elapsed_ms, 2),
                llm_latency_ms=0.0,  # populated from observability context if available
                tool_latency_ms=round(tool_latency, 2),
                retrieval_latency_ms=0.0,
            ),
            cost=CostTrace(
                input_tokens=context.observation_context.total_tokens,
                output_tokens=0,
                embedding_tokens=0,
                total_cost_usd=context.observation_context.estimated_cost,
            ),
        )

    except GuardrailException as ge:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return EvalTraceResponse(
            agent_response=f"I cannot comply with this request. Blocked by guardrail policy.",
            tool_calls=[],
            retrieved_doc_ids=[],
            planning_steps=["block_adversarial_prompt"],
            performance=PerformanceTrace(total_latency_ms=elapsed_ms),
        )
    except AgentException as ae:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": ae.error_code, "message": ae.message}
        )
    except Exception as e:
        logger.error(f"Evaluation endpoint error: {str(e)}", component="EvalController")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "EVAL_ERROR", "message": str(e)}
        )


def _extract_destination(prompt: str) -> str:
    """Simple heuristic to extract destination from prompt for eval requests."""
    keywords = ["to ", "visiting ", "for "]
    prompt_lower = prompt.lower()
    for kw in keywords:
        idx = prompt_lower.find(kw)
        if idx != -1:
            remaining = prompt[idx + len(kw):].strip()
            # Take the first few words as destination
            words = remaining.split()
            return " ".join(words[:3]).rstrip(".,!?")
    return "Unknown"

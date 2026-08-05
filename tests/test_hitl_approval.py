import pytest
from app.services.hitl_service import HitlApprovalService
from app.services.response_processor import ResponseProcessor
from app.dto.context import ExecutionContext

@pytest.mark.anyio
async def test_hitl_approval_service_risk_evaluation():
    hitl_service = HitlApprovalService(auto_approval_limit_usd=250.0)
    
    # Low risk action auto-passes (no approval DTO)
    appr_low = hitl_service.evaluate_risk_and_create_approval("SEARCH_FLIGHTS", 100.0, "Search", {})
    assert appr_low is None

    # High risk booking action creates approval DTO
    appr_high = hitl_service.evaluate_risk_and_create_approval("FLIGHT_BOOKING", 550.0, "Flight booking", {"flight_id": "SQ-638"})
    assert appr_high is not None
    assert appr_high.action_type == "FLIGHT_BOOKING"
    assert appr_high.amount_usd == 550.0
    assert appr_high.risk_level in ["HIGH", "CRITICAL"]

@pytest.mark.anyio
async def test_response_processor_hitl_status():
    class RiskFacade:
        async def validate_output_guardrails(self, text: str, session_id: str):
            return True, text, {
                "violations": [
                    {
                        "guardrail_name": "RiskAssessmentGuardrail",
                        "message": "HITL Approval required for flight booking",
                        "details": {"risk_level": "CRITICAL", "requires_human_approval": True}
                    }
                ]
            }

    processor = ResponseProcessor(facade=RiskFacade())
    context = ExecutionContext(
        user_id="u1",
        conversation_id="c1",
        session_id="s1",
        request_id="r1",
        trace_id="t1",
        user_request="Book flight to Tokyo"
    )
    res = await processor.process_response(context)

    assert res.requires_human_approval is True
    assert res.status == "AWAITING_HUMAN_APPROVAL"
    assert res.approval_request is not None

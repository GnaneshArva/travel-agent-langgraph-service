import pytest
from app.services.response_processor import ResponseProcessor
from app.dto.context import ExecutionContext

@pytest.mark.anyio
async def test_coherence_remediation_warning():
    class DummyFacade:
        async def validate_output_guardrails(self, text: str, session_id: str):
            return True, text, {
                "violations": [
                    {
                        "guardrail_name": "CoherenceGuardrail",
                        "message": "Coherence warning: Out-of-order timeline jump"
                    }
                ]
            }

    processor = ResponseProcessor(facade=DummyFacade())
    context = ExecutionContext(
        user_id="u1",
        conversation_id="c1",
        session_id="s1",
        request_id="r1",
        trace_id="t1",
        user_request="Plan trip to Zurich"
    )
    res = await processor.process_response(context)
    assert any("coherence" in w.lower() for w in res.warnings)

import uuid
from app.dto.context import ExecutionContext
from app.dto.session_dto import SessionInfo, ConversationInfo, RequestMetadata
from app.dto.requests import TravelRequest
from app.utils.logger import logger

class SessionManager:
    """Manages session context, conversation IDs, trace correlation, and timeouts."""

    def __init__(self):
        self._active_sessions: dict[str, SessionInfo] = {}

    def create_execution_context(self, request: TravelRequest) -> ExecutionContext:
        session_id = request.session_id or f"sess-{uuid.uuid4().hex[:8]}"
        conversation_id = request.conversation_id or f"conv-{uuid.uuid4().hex[:8]}"
        request_id = f"req-{uuid.uuid4().hex[:8]}"
        trace_id = f"trace-{uuid.uuid4().hex[:12]}"

        session_info = SessionInfo(
            session_id=session_id,
            user_id=request.user_id
        )
        self._active_sessions[session_id] = session_info

        logger.info(
            f"Created new execution session for user_id={request.user_id}",
            component="SessionManager",
            session_id=session_id,
            request_id=request_id,
            conversation_id=conversation_id,
            trace_id=trace_id
        )

        user_req_text = (
            f"Plan a {request.duration_days}-day travel trip to {request.destination}. "
            f"Budget: {request.budget or 'Flexible'} {request.currency}. "
            f"Additional Notes: {request.additional_notes or 'None'}"
        )

        ctx = ExecutionContext(
            session_id=session_id,
            user_id=request.user_id,
            conversation_id=conversation_id,
            request_id=request_id,
            trace_id=trace_id,
            user_request=user_req_text
        )
        ctx.metadata["destination"] = request.destination
        ctx.metadata["duration_days"] = request.duration_days
        ctx.metadata["budget"] = request.budget
        ctx.metadata["currency"] = request.currency
        return ctx

    def get_session(self, session_id: str) -> SessionInfo | None:
        return self._active_sessions.get(session_id)

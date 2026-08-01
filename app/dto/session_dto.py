from datetime import datetime, timezone
from pydantic import BaseModel, Field

class SessionInfo(BaseModel):
    session_id: str
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "ACTIVE"
    timeout_seconds: int = 1800

class ConversationInfo(BaseModel):
    conversation_id: str
    session_id: str
    turn_count: int = 1
    last_active: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RequestMetadata(BaseModel):
    request_id: str
    trace_id: str
    client_ip: str | None = None
    user_agent: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ResponseMetadata(BaseModel):
    response_id: str
    request_id: str
    execution_time_ms: float
    total_tokens_used: int = 0
    estimated_cost_usd: float = 0.0
    status: str = "SUCCESS"

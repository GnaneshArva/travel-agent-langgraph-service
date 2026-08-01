import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any

class StructuredLogger:
    """Structured JSON Logger for Enterprise Observability."""
    
    def __init__(self, name: str = "travel-agent-service"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(handler)

    def _format_event(
        self,
        level: str,
        message: str,
        component: str,
        session_id: str | None = None,
        request_id: str | None = None,
        conversation_id: str | None = None,
        trace_id: str | None = None,
        duration_ms: float | None = None,
        **extra: Any
    ) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            "component": component,
            "session_id": session_id or "N/A",
            "request_id": request_id or "N/A",
            "conversation_id": conversation_id or "N/A",
            "trace_id": trace_id or "N/A",
        }
        if duration_ms is not None:
            payload["duration_ms"] = round(duration_ms, 2)
        if extra:
            # Sanitize extra fields to avoid secrets/PII
            sanitized_extra = {k: v for k, v in extra.items() if "secret" not in k.lower() and "key" not in k.lower()}
            payload["details"] = sanitized_extra
        return json.dumps(payload)

    def info(
        self,
        message: str,
        component: str = "general",
        session_id: str | None = None,
        request_id: str | None = None,
        conversation_id: str | None = None,
        trace_id: str | None = None,
        duration_ms: float | None = None,
        **extra: Any
    ):
        log_msg = self._format_event("INFO", message, component, session_id, request_id, conversation_id, trace_id, duration_ms, **extra)
        self.logger.info(log_msg)

    def error(
        self,
        message: str,
        component: str = "general",
        session_id: str | None = None,
        request_id: str | None = None,
        conversation_id: str | None = None,
        trace_id: str | None = None,
        duration_ms: float | None = None,
        **extra: Any
    ):
        log_msg = self._format_event("ERROR", message, component, session_id, request_id, conversation_id, trace_id, duration_ms, **extra)
        self.logger.error(log_msg)

    def warning(
        self,
        message: str,
        component: str = "general",
        session_id: str | None = None,
        request_id: str | None = None,
        conversation_id: str | None = None,
        trace_id: str | None = None,
        duration_ms: float | None = None,
        **extra: Any
    ):
        log_msg = self._format_event("WARNING", message, component, session_id, request_id, conversation_id, trace_id, duration_ms, **extra)
        self.logger.warning(log_msg)

logger = StructuredLogger()

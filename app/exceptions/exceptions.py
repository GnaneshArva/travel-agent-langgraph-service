"""
Custom Exceptions for Travel Agent Service
"""

class AgentException(Exception):
    """Base exception for all agent service errors."""
    def __init__(
        self, 
        message: str, 
        error_code: str = "AGENT_ERROR", 
        correlation_id: str | None = None,
        retryable: bool = False
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.correlation_id = correlation_id
        self.retryable = retryable

class PlanningException(AgentException):
    """Raised when execution planning fails."""
    def __init__(self, message: str, correlation_id: str | None = None, retryable: bool = False):
        super().__init__(message, error_code="PLANNING_ERROR", correlation_id=correlation_id, retryable=retryable)

class MemoryException(AgentException):
    """Raised when interaction with Memory MCP fails."""
    def __init__(self, message: str, correlation_id: str | None = None, retryable: bool = True):
        super().__init__(message, error_code="MEMORY_ERROR", correlation_id=correlation_id, retryable=retryable)

class KnowledgeException(AgentException):
    """Raised when interaction with Knowledge MCP fails."""
    def __init__(self, message: str, correlation_id: str | None = None, retryable: bool = True):
        super().__init__(message, error_code="KNOWLEDGE_ERROR", correlation_id=correlation_id, retryable=retryable)

class ToolException(AgentException):
    """Raised when MCP tool execution fails."""
    def __init__(self, message: str, correlation_id: str | None = None, retryable: bool = True):
        super().__init__(message, error_code="TOOL_ERROR", correlation_id=correlation_id, retryable=retryable)

class PromptException(AgentException):
    """Raised when prompt rendering or loading fails."""
    def __init__(self, message: str, correlation_id: str | None = None, retryable: bool = False):
        super().__init__(message, error_code="PROMPT_ERROR", correlation_id=correlation_id, retryable=retryable)

class GuardrailException(AgentException):
    """Raised when guardrail validation fails or blocks execution."""
    def __init__(self, message: str, correlation_id: str | None = None, retryable: bool = False):
        super().__init__(message, error_code="GUARDRAIL_BLOCKED", correlation_id=correlation_id, retryable=retryable)

class StreamingException(AgentException):
    """Raised during response streaming errors."""
    def __init__(self, message: str, correlation_id: str | None = None, retryable: bool = False):
        super().__init__(message, error_code="STREAMING_ERROR", correlation_id=correlation_id, retryable=retryable)

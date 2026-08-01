from enum import Enum
from typing import Annotated, Any, Dict, List, Optional, TypedDict
from langchain_core.messages import BaseMessage
import operator


class StrategyType(str, Enum):
    BUDGET_FIRST = "BUDGET_FIRST"
    LUXURY = "LUXURY"
    FASTEST_TRIP = "FASTEST_TRIP"
    WEATHER_FIRST = "WEATHER_FIRST"
    EXPERIENCE_FIRST = "EXPERIENCE_FIRST"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TaskItem(TypedDict):
    task_id: str
    action_name: str
    target_specialist: str
    parameters: Dict[str, Any]
    priority: int
    status: TaskStatus
    retry_count: int
    error_message: Optional[str]


class TaskQueue(TypedDict):
    pending: List[TaskItem]
    in_progress: List[TaskItem]
    completed: List[TaskItem]
    failed: List[TaskItem]


class VerificationResult(TypedDict):
    verifier_name: str
    passed: bool
    score: float
    violations: List[str]
    remediation_suggestion: Optional[str]


class ReflectionSummary(TypedDict):
    iteration: int
    progress_percentage: float
    confidence_score: float
    is_stagnant: bool
    recommended_action: str
    strategy_pivot: Optional[StrategyType]


class PlannerState(TypedDict):
    """
    Central immutable execution state model for Goal-Driven Loop Engineering.
    """
    # Core Goal
    user_goal: str
    system_prompt: str
    destination: str
    budget: Optional[float]
    duration_days: int

    # Strategy & Task Queue
    current_strategy: StrategyType
    task_queue: TaskQueue
    active_actions: List[str]

    # Message sequence history
    messages: Annotated[List[BaseMessage], operator.add]

    # Domain Data & State Artifacts
    flight_results: Optional[Dict[str, Any]]
    hotel_results: Optional[Dict[str, Any]]
    weather_results: Optional[Dict[str, Any]]
    visa_results: Optional[Dict[str, Any]]
    attraction_results: Optional[Dict[str, Any]]
    final_itinerary: Optional[str]

    # Verification & Reflection Outputs
    verification_results: List[VerificationResult]
    reflections: List[ReflectionSummary]
    confidence_score: float
    progress_percentage: float
    is_verified: bool

    # Governance, Limits & Telemetry
    iteration_count: int
    total_tokens_used: int
    estimated_cost_usd: float
    tool_calls_executed: Annotated[List[Dict[str, Any]], operator.add]
    current_node: str
    hand_off_count: int
    is_complete: bool
    termination_reason: Optional[str]

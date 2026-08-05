import time
import uuid
from typing import Optional, Dict, Any
from app.dto.responses import ApprovalRequestDTO
from app.utils.logger import logger


class HitlApprovalService:
    """Service managing Human-in-the-Loop (HITL) risk assessment and approval request lifecycle for LangGraph workflows."""

    def __init__(self, auto_approval_limit_usd: float = 250.0):
        self.auto_approval_limit_usd = auto_approval_limit_usd

    def evaluate_risk_and_create_approval(
        self,
        action_type: str,
        amount_usd: float,
        reason: str,
        payload: Dict[str, Any],
        ttl_seconds: int = 86400
    ) -> Optional[ApprovalRequestDTO]:
        """Evaluates whether an action requires Human-in-the-Loop approval.
        
        Mandatory Approval Trigger Rules:
        - Financial transactions or bookings exceeding auto_approval_limit_usd.
        - Irreversible actions: flight bookings, hotel reservations, payments, cancellations, date changes.
        """
        high_risk_actions = ["FLIGHT_BOOKING", "HOTEL_BOOKING", "PAYMENT", "CANCEL_BOOKING", "BUDGET_OVERRIDE"]
        
        is_high_risk_action = any(hra in action_type.upper() for hra in high_risk_actions)
        exceeds_budget_threshold = amount_usd > self.auto_approval_limit_usd

        if is_high_risk_action or exceeds_budget_threshold:
            approval_id = f"appr_{uuid.uuid4().hex[:10]}"
            risk_level = "CRITICAL" if amount_usd > 1000.0 or "PAYMENT" in action_type.upper() else "HIGH"
            
            logger.warning(
                f"HITL Approval required for LangGraph action '{action_type}' (Amount: ${amount_usd:.2f})",
                component="HitlApprovalService",
                approval_id=approval_id,
                risk_level=risk_level
            )
            
            return ApprovalRequestDTO(
                approval_id=approval_id,
                action_type=action_type,
                risk_level=risk_level,
                amount_usd=amount_usd,
                reason=reason or f"LangGraph action '{action_type}' requires human review before execution.",
                payload=payload,
                expiration_timestamp=time.time() + ttl_seconds
            )

        return None

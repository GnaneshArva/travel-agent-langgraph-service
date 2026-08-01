from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from app.dto.requests import TravelRequest
from app.dto.responses import TravelResponse
from app.orchestrator.agent_orchestrator import AgentOrchestrator
from app.exceptions.exceptions import AgentException

router = APIRouter(prefix="/api/v1/travel", tags=["Travel Agent Service"])
travel_router = router
orchestrator = AgentOrchestrator()

@router.post("/plan", response_model=TravelResponse, status_code=status.HTTP_200_OK)
async def plan_trip(request: TravelRequest) -> TravelResponse:
    """Accept travel planning request and execute agent orchestration lifecycle."""
    try:
        return await orchestrator.execute(request)
    except AgentException as ae:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": ae.error_code, "message": ae.message, "correlation_id": ae.correlation_id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": str(e)}
        )

@router.post("/plan/stream")
async def plan_trip_stream(request: TravelRequest):
    """Accept travel planning request and stream back itinerary progress events."""
    try:
        return StreamingResponse(
            orchestrator.execute_stream(request),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "STREAMING_ERROR", "message": str(e)}
        )

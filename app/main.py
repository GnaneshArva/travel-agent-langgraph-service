import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.controllers import travel_router, eval_router
from app.config.settings import settings
from app.exceptions.exceptions import AgentException
from app.utils.logger import logger

app = FastAPI(
    title="Travel Agent LangGraph Service",
    description="Enterprise Agentic AI Travel Planner Central Orchestration Service using LangGraph Multi-Agent Orchestration",
    version="0.1.0"
)

# Register routes
app.include_router(travel_router)
app.include_router(eval_router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.app_env,
        "features": settings.features.model_dump()
    }

@app.exception_handler(AgentException)
async def agent_exception_handler(request: Request, exc: AgentException):
    logger.error(f"AgentException: {exc.message}", component="FastAPIExceptionHandler", extra={"error_code": exc.error_code})
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "correlation_id": exc.correlation_id,
            "retryable": exc.retryable
        }
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

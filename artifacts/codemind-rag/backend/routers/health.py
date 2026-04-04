import time
from datetime import datetime, timezone

from fastapi import APIRouter
from models.schemas import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])

_start_time = time.monotonic()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
        services={
            "qdrant": "disconnected",
            "groq": "disconnected",
            "huggingface": "disconnected",
        },
        uptime_seconds=round(time.monotonic() - _start_time, 2),
    )

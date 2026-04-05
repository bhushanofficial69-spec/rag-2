import time
from datetime import datetime, timezone

from fastapi import APIRouter
from models.schemas import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])

_start_time = time.monotonic()

_vector_db_ref = None


def set_vector_db(vdb):
    global _vector_db_ref
    _vector_db_ref = vdb


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    if _vector_db_ref and _vector_db_ref.available:
        qdrant_status = "connected"
    elif _vector_db_ref is not None:
        qdrant_status = "disconnected"
    else:
        qdrant_status = "not_configured"

    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
        services={
            "qdrant": qdrant_status,
            "groq": "disconnected",
            "huggingface": "disconnected",
        },
        uptime_seconds=round(time.monotonic() - _start_time, 2),
    )

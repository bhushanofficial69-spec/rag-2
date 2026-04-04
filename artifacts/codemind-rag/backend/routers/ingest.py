from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import ValidationError

from models.schemas import IngestRequest, IngestResponse, IngestionStatus
from services.ingestion import ingestion_service
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse, status_code=202)
async def ingest_repo(request: IngestRequest, background_tasks: BackgroundTasks) -> IngestResponse:
    logger.info(
        "ingest_request_received",
        repo_url=request.repo_url,
        branch=request.branch,
    )

    job_id = ingestion_service.ingest_repo(request.repo_url, request.branch)

    return IngestResponse(
        status="processing",
        job_id=job_id,
        message=f"Ingestion started for {request.repo_url}. Poll /api/ingest/status/{job_id} for progress.",
    )


@router.get("/ingest/status/{job_id}", response_model=IngestionStatus)
async def get_ingestion_status(job_id: str) -> IngestionStatus:
    status = ingestion_service.get_status(job_id)
    if status is None:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id!r} not found. It may have expired or never existed.",
        )
    return status

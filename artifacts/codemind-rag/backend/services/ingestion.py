import uuid
import shutil
import os
from pathlib import Path
from typing import Dict
from concurrent.futures import ThreadPoolExecutor

from config import settings
from models.schemas import IngestionStatus
from services.repo_cloner import RepoCloner
from services.file_filter import FileFilter
from utils.logger import get_logger

logger = get_logger(__name__)

_executor = ThreadPoolExecutor(max_workers=4)

job_store: Dict[str, IngestionStatus] = {}


class IngestionService:
    def __init__(self):
        self.cloner = RepoCloner()
        self.filter = FileFilter()

    def ingest_repo(self, repo_url: str, branch: str) -> str:
        job_id = str(uuid.uuid4())
        job_store[job_id] = IngestionStatus(
            job_id=job_id,
            status="queued",
            files_indexed=0,
            chunks_created=0,
            progress_percent=0,
        )
        _executor.submit(self._run_ingestion, job_id, repo_url, branch)
        logger.info("ingestion_job_queued", job_id=job_id, repo_url=repo_url, branch=branch)
        return job_id

    def _run_ingestion(self, job_id: str, repo_url: str, branch: str) -> None:
        temp_path = os.path.join(settings.TEMP_DIR, job_id)

        try:
            self._update_job(job_id, status="processing", progress_percent=5)

            logger.info("cloning_repo", job_id=job_id, repo_url=repo_url)
            clone_path = self.cloner.clone_repo(repo_url, branch, temp_path)
            self._update_job(job_id, progress_percent=30)

            logger.info("filtering_files", job_id=job_id)
            code_files = self.filter.get_code_files(clone_path)

            if len(code_files) > settings.MAX_FILES:
                raise ValueError(
                    f"Repository has {len(code_files)} files, exceeding limit of {settings.MAX_FILES}. "
                    "Try a smaller repository."
                )

            logger.info(
                "files_found",
                job_id=job_id,
                count=len(code_files),
                repo_url=repo_url,
            )
            self._update_job(job_id, progress_percent=50, files_indexed=len(code_files))

            total = len(code_files)
            for idx, fpath in enumerate(code_files):
                try:
                    content = Path(fpath).read_text(encoding="utf-8", errors="ignore")
                    language = self.filter.detect_language(fpath)
                    logger.debug(
                        "file_read",
                        job_id=job_id,
                        file=fpath,
                        language=language,
                        chars=len(content),
                    )
                except Exception as exc:
                    logger.warning("file_read_error", job_id=job_id, file=fpath, error=str(exc))

                progress = 50 + int((idx + 1) / max(total, 1) * 45)
                self._update_job(job_id, progress_percent=progress)

            self._update_job(
                job_id,
                status="completed",
                progress_percent=100,
                files_indexed=total,
                chunks_created=0,
            )
            logger.info("ingestion_complete", job_id=job_id, files=total)

        except Exception as exc:
            logger.error("ingestion_failed", job_id=job_id, error=str(exc))
            self._update_job(job_id, status="failed", error=str(exc), progress_percent=0)
        finally:
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path, ignore_errors=True)
                logger.debug("temp_cleaned", job_id=job_id, path=temp_path)

    def _update_job(self, job_id: str, **kwargs) -> None:
        if job_id not in job_store:
            return
        current = job_store[job_id]
        updated = current.model_copy(update=kwargs)
        job_store[job_id] = updated

    def get_status(self, job_id: str) -> IngestionStatus | None:
        return job_store.get(job_id)


ingestion_service = IngestionService()

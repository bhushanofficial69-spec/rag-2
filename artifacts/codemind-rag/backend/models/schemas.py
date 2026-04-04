from pydantic import BaseModel, field_validator
from typing import Optional, Dict


class IngestRequest(BaseModel):
    repo_url: str
    branch: str = "main"

    @field_validator("repo_url")
    @classmethod
    def validate_github_url(cls, v: str) -> str:
        import re
        pattern = r"^https://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?$"
        if not re.match(pattern, v.strip()):
            raise ValueError(
                "repo_url must be a valid GitHub URL: https://github.com/owner/repo"
            )
        cleaned = v.strip()
        return cleaned.removesuffix(".git")

    @field_validator("branch")
    @classmethod
    def validate_branch(cls, v: str) -> str:
        import re
        if not re.match(r"^[\w\-\./]+$", v):
            raise ValueError("branch name contains invalid characters")
        return v


class IngestResponse(BaseModel):
    status: str
    job_id: str
    message: str


class IngestionStatus(BaseModel):
    job_id: str
    status: str
    files_indexed: int
    chunks_created: int
    error: Optional[str] = None
    progress_percent: int


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]
    uptime_seconds: float

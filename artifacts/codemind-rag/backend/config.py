from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    BACKEND_URL: str = "http://localhost:8000"
    GITHUB_TOKEN: Optional[str] = None
    MAX_REPO_SIZE: int = Field(default=500, description="Max repo size in MB")
    MAX_FILES: int = Field(default=5000, description="Max number of files to index")
    TEMP_DIR: str = "./temp"
    LOG_LEVEL: str = "INFO"

    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "codemind-codebase"
    VECTOR_DIMENSION: int = 384

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

from pydantic import BaseModel
from typing import Optional, List


class ChunkMetadata(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    language: str
    function_name: Optional[str] = None
    dependencies: List[str] = []
    repo_name: str
    code_snippet: str
    timestamp: str


class VectorChunk(BaseModel):
    id: str
    vector: List[float]
    metadata: ChunkMetadata

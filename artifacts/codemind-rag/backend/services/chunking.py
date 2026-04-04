import ast
import re
from pathlib import Path
from typing import List, Optional, Tuple

from langchain.text_splitter import RecursiveCharacterTextSplitter
from models.schemas import CodeChunk
from utils.logger import get_logger

logger = get_logger(__name__)

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
MIN_CHUNK_TOKENS = 100

EXT_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
}

LANGUAGE_SEPARATORS = {
    "python": ["\nclass ", "\ndef ", "\nasync def ", "\n\n", "\n", ". ", " "],
    "javascript": ["\nfunction ", "\nconst ", "\nlet ", "\nvar ", "\nclass ", "\n\n", "\n", ". ", " "],
    "typescript": ["\nfunction ", "\nconst ", "\nlet ", "\nvar ", "\nclass ", "\ninterface ", "\ntype ", "\n\n", "\n", ". ", " "],
    "java": ["\npublic class ", "\nprivate class ", "\nprotected class ", "\npublic static ", "\npublic ", "\n\n", "\n"],
    "default": ["\n\n", "\n", ". ", " "],
}


def _approx_tokens(text: str) -> int:
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        return max(1, len(text) // 4)


class ChunkingService:
    def detect_language(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        lang = EXT_TO_LANGUAGE.get(ext, "unknown")
        logger.debug("language_detected", file=file_path, language=lang)
        return lang

    def get_language_separators(self, language: str) -> List[str]:
        return LANGUAGE_SEPARATORS.get(language, LANGUAGE_SEPARATORS["default"])

    def _extract_function_name(self, content: str, language: str) -> Optional[str]:
        if language == "python":
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        return node.name
            except SyntaxError:
                pass
            m = re.search(r"(?:def|async def|class)\s+(\w+)", content)
            return m.group(1) if m else None

        if language in ("javascript", "typescript"):
            m = re.search(
                r"(?:function|class)\s+(\w+)"
                r"|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\(|[\w]+\s*=>)",
                content,
            )
            if m:
                return m.group(1) or m.group(2)
            return None

        if language == "java":
            m = re.search(
                r"(?:public|private|protected)?\s*(?:static)?\s*(?:class|interface|enum)\s+(\w+)"
                r"|(?:public|private|protected)\s+(?:static\s+)?(?:[\w<>\[\]]+)\s+(\w+)\s*\(",
                content,
            )
            if m:
                return m.group(1) or m.group(2)
            return None

        return None

    def _get_line_numbers(
        self, original_lines: List[str], chunk_content: str, cursor_line: int
    ) -> Tuple[int, int, int]:
        chunk_lines = chunk_content.splitlines()
        if not chunk_lines:
            return cursor_line, cursor_line, cursor_line

        chunk_line_count = len(chunk_lines)
        total_lines = len(original_lines)

        search_start = cursor_line - 1
        first_chunk_line = chunk_lines[0].strip()

        for i in range(search_start, total_lines):
            if original_lines[i].strip() == first_chunk_line:
                start_line = i + 1
                end_line = min(start_line + chunk_line_count - 1, total_lines)
                next_cursor = end_line
                return start_line, end_line, next_cursor

        start_line = cursor_line
        end_line = min(cursor_line + chunk_line_count - 1, total_lines)
        next_cursor = end_line
        return start_line, end_line, next_cursor

    def chunk_code(
        self,
        code: str,
        language: str,
        file_path: str,
        start_line: int = 1,
    ) -> List[CodeChunk]:
        if not code.strip():
            return []

        separators = self.get_language_separators(language)
        splitter = RecursiveCharacterTextSplitter(
            separators=separators,
            chunk_size=CHUNK_SIZE * 4,
            chunk_overlap=CHUNK_OVERLAP * 4,
            length_function=len,
            is_separator_regex=False,
        )

        raw_chunks = splitter.split_text(code)
        original_lines = code.splitlines()
        total_lines = len(original_lines)

        chunks: List[CodeChunk] = []
        cursor_line = start_line

        for raw in raw_chunks:
            if not raw.strip():
                continue

            token_count = _approx_tokens(raw)
            if token_count < MIN_CHUNK_TOKENS:
                logger.debug(
                    "chunk_skipped_too_small",
                    file=file_path,
                    tokens=token_count,
                )
                continue

            s_line, e_line, cursor_line = self._get_line_numbers(
                original_lines, raw, cursor_line
            )

            func_name = self._extract_function_name(raw, language)

            chunk = CodeChunk(
                file_path=file_path,
                start_line=s_line,
                end_line=e_line,
                language=language,
                content=raw,
                function_name=func_name,
                dependencies=[],
                char_count=len(raw),
                token_count=token_count,
            )
            chunks.append(chunk)

        logger.debug(
            "file_chunked",
            file=file_path,
            language=language,
            total_chunks=len(chunks),
            raw_chunks=len(raw_chunks),
        )
        return chunks


chunking_service = ChunkingService()

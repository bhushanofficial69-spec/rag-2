import os
from pathlib import Path
from typing import List

from utils.logger import get_logger

logger = get_logger(__name__)

SUPPORTED_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".java"}

EXCLUDED_DIRS = {
    "node_modules",
    ".git",
    "__pycache__",
    "dist",
    "build",
    "venv",
    ".venv",
    "vendor",
    ".next",
    ".nuxt",
}

MAX_FILE_SIZE_BYTES = 100 * 1024


class FileFilter:
    def get_code_files(self, repo_path: str) -> List[str]:
        root = Path(repo_path)
        code_files: List[str] = []
        skipped_size = 0
        skipped_ext = 0

        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                d for d in dirnames if d not in EXCLUDED_DIRS
            ]

            current_dir = Path(dirpath)
            rel_dir = current_dir.relative_to(root)

            parts = set(rel_dir.parts)
            if parts & EXCLUDED_DIRS:
                dirnames.clear()
                continue

            excluded = [d for d in os.listdir(dirpath) if d in EXCLUDED_DIRS]
            if excluded:
                logger.info(
                    "filtered_excluded_directories",
                    path=str(rel_dir),
                    excluded=excluded,
                )

            for filename in filenames:
                filepath = current_dir / filename
                ext = filepath.suffix.lower()

                if ext not in SUPPORTED_EXTENSIONS:
                    skipped_ext += 1
                    continue

                try:
                    size = filepath.stat().st_size
                except OSError:
                    continue

                if size > MAX_FILE_SIZE_BYTES:
                    skipped_size += 1
                    logger.debug(
                        "skipped_large_file",
                        file=str(filepath.relative_to(root)),
                        size_kb=round(size / 1024, 1),
                    )
                    continue

                code_files.append(str(filepath))

        logger.info(
            "file_filter_complete",
            total_code_files=len(code_files),
            skipped_wrong_ext=skipped_ext,
            skipped_too_large=skipped_size,
        )
        return code_files

    def detect_language(self, filepath: str) -> str:
        ext = Path(filepath).suffix.lower()
        ext_to_lang = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
        }
        return ext_to_lang.get(ext, "unknown")

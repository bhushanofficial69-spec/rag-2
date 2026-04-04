import ast
import re
from pathlib import Path
from typing import List

from utils.logger import get_logger

logger = get_logger(__name__)

JS_IMPORT_PATTERNS = [
    re.compile(r"""import\s+.*?\s+from\s+['"]([^'"]+)['"]"""),
    re.compile(r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)"""),
    re.compile(r"""import\s*\(\s*['"]([^'"]+)['"]\s*\)"""),
]

JAVA_IMPORT_PATTERN = re.compile(r"import\s+([\w\.]+)\s*;")


class LanguageParser:
    def extract_dependencies(
        self, code: str, language: str, file_path: str
    ) -> List[str]:
        if language == "python":
            return self._extract_python_deps(code, file_path)
        if language in ("javascript", "typescript"):
            return self._extract_js_deps(code, file_path)
        if language == "java":
            return self._extract_java_deps(code, file_path)
        return []

    def _extract_python_deps(self, code: str, file_path: str) -> List[str]:
        deps: List[str] = []
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return deps

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dep = alias.name
                    deps.append(dep)
                    logger.debug("python_dep_found", file=file_path, dep=dep)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dep = node.module
                    deps.append(dep)
                    logger.debug("python_dep_found", file=file_path, dep=dep)

        return list(dict.fromkeys(deps))

    def _extract_js_deps(self, code: str, file_path: str) -> List[str]:
        deps: List[str] = []
        for pattern in JS_IMPORT_PATTERNS:
            for m in pattern.finditer(code):
                dep = m.group(1)
                deps.append(dep)
                logger.debug("js_dep_found", file=file_path, dep=dep)
        return list(dict.fromkeys(deps))

    def _extract_java_deps(self, code: str, file_path: str) -> List[str]:
        deps: List[str] = []
        for m in JAVA_IMPORT_PATTERN.finditer(code):
            dep = m.group(1)
            deps.append(dep)
            logger.debug("java_dep_found", file=file_path, dep=dep)
        return list(dict.fromkeys(deps))


language_parser = LanguageParser()

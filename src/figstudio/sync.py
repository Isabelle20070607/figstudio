"""Controlled script writeback for FigStudio generated code."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


class CodeSyncError(RuntimeError):
    """Raised when a script cannot be safely updated."""


@dataclass
class CodeSyncEngine:
    block_id: str = "main"

    def replace_block(self, source: str, code: str) -> str:
        matches = list(self._find_blocks(source))
        if not matches:
            raise CodeSyncError(f"No figstudio block found for block_id={self.block_id!r}.")
        if len(matches) > 1:
            raise CodeSyncError(f"Multiple figstudio blocks found for block_id={self.block_id!r}.")

        start, content_start, content_end, end = matches[0]
        old_content = source[content_start:content_end]
        if self._marker_re().search(old_content):
            raise CodeSyncError("Nested figstudio markers are not safe to replace.")

        newline = "\r\n" if "\r\n" in source else "\n"
        replacement = code.rstrip() + newline
        return source[:content_start] + replacement + source[content_end:]

    def replace_file(self, path: str | Path, code: str) -> None:
        file_path = Path(path)
        source = file_path.read_text(encoding="utf-8-sig")
        updated = self.replace_block(source, code)
        file_path.write_text(updated, encoding="utf-8")

    def _find_blocks(self, source: str):
        marker_re = self._marker_re()
        stack: tuple[int, int, str] | None = None
        for match in marker_re.finditer(source):
            kind = match.group("kind")
            marker_id = match.group("id") or "main"
            if marker_id != self.block_id:
                continue
            line_end = source.find("\n", match.end())
            if line_end == -1:
                line_end = len(source)
            else:
                line_end += 1
            if kind == "start":
                if stack is not None:
                    raise CodeSyncError("Nested figstudio start marker found.")
                stack = (match.start(), line_end, marker_id)
            elif kind == "end":
                if stack is None:
                    raise CodeSyncError("FigStudio end marker found before start marker.")
                start, content_start, _ = stack
                yield start, content_start, match.start(), match.end()
                stack = None
        if stack is not None:
            raise CodeSyncError("FigStudio start marker has no matching end marker.")

    def _marker_re(self) -> re.Pattern[str]:
        return re.compile(
            r"^[ \t]*#\s*figstudio:(?P<kind>start|end)(?:\s+(?P<id>[A-Za-z0-9_.-]+))?[ \t]*$",
            re.MULTILINE,
        )

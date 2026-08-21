"""Application-wide constants for the Batch File Suffix Appender."""

from __future__ import annotations

APP_NAME: str = "Batch File Suffix Appender"

MAX_UNDO_DEPTH: int = 20

# Characters that are illegal in file names on Windows (and thus any target).
ILLEGAL_FILENAME_CHARS: frozenset[str] = frozenset('<>:"/\\|?*')

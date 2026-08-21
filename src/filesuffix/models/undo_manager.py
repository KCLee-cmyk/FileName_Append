"""LIFO history stack for undo support."""

from __future__ import annotations

from filesuffix.config import MAX_UNDO_DEPTH
from filesuffix.models.rename_command import RenameBatch


class UndoManager:
    """Maintains a history of rename batches for undo.

    The history is capped at ``MAX_UNDO_DEPTH`` entries; the oldest batch is
    silently dropped when the cap is exceeded.
    """

    def __init__(self) -> None:
        """Initialize an empty undo history."""
        self._stack: list[RenameBatch] = []

    def push(self, batch: RenameBatch) -> None:
        """Record a completed batch as the most recent operation.

        Args:
            batch: The batch to add to the top of the history stack.
        """
        self._stack.append(batch)
        if len(self._stack) > MAX_UNDO_DEPTH:
            self._stack.pop(0)

    def pop(self) -> RenameBatch | None:
        """Remove and return the most recent batch.

        Returns:
            The most recent ``RenameBatch``, or ``None`` if the history is
            empty.
        """
        if not self._stack:
            return None
        return self._stack.pop()

    def can_undo(self) -> bool:
        """Return ``True`` when there is at least one batch to undo.

        Returns:
            ``True`` when the history stack is non-empty.
        """
        return bool(self._stack)

    def clear(self) -> None:
        """Discard all history.

        Call this when the user changes folders so stale undo entries from a
        previous directory cannot be applied to the new one.
        """
        self._stack.clear()

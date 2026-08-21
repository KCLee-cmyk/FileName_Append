"""Filesystem rename executor with undo support."""

from __future__ import annotations

import logging
import os

from filesuffix.models.rename_command import RenameBatch, RenameCommand

logger = logging.getLogger(__name__)


class RenameError(Exception):
    """Raised when one or more renames fail during ``RenameService.apply``.

    Attributes:
        completed: The batch of renames that succeeded before the failure.
        conflicts: File names skipped because the target already existed.
        failures: File names that failed due to OS errors.
    """

    def __init__(
        self,
        message: str,
        completed: RenameBatch,
        conflicts: list[str],
        failures: list[str],
    ) -> None:
        """Initialize the error with diagnostic details.

        Args:
            message: Human-readable summary.
            completed: Renames that succeeded and can be undone.
            conflicts: Names skipped due to target-exists collision.
            failures: Names that raised ``OSError`` during rename.
        """
        super().__init__(message)
        self.completed = completed
        self.conflicts = conflicts
        self.failures = failures


class RenameService:
    """Executes and reverts file rename operations on disk."""

    def apply(self, planned: list[tuple[str, str]]) -> RenameBatch:
        """Rename each ``(old_path, new_path)`` pair on disk.

        Pairs whose target already exists are skipped to avoid overwriting.
        Renames proceed one by one; any that succeed before a failure are
        recorded in the returned ``RenameBatch`` so they can still be undone.

        Args:
            planned: Pairs of ``(old_path, new_path)`` to apply.

        Returns:
            A ``RenameBatch`` describing every rename that succeeded.

        Raises:
            RenameError: When at least one rename fails or collides. The
                ``completed`` attribute of the error contains the partial
                batch of successful renames.
        """
        completed = RenameBatch()
        conflicts: list[str] = []
        failures: list[str] = []

        for old_path, new_path in planned:
            if os.path.exists(new_path):
                conflicts.append(os.path.basename(new_path))
                logger.warning("Skipping %s → target already exists", old_path)
                continue
            try:
                os.rename(old_path, new_path)
                completed.commands.append(RenameCommand(old_path, new_path))
            except (OSError, PermissionError) as exc:
                failures.append(os.path.basename(old_path))
                logger.error("Failed to rename %s: %s", old_path, exc)

        if conflicts or failures:
            parts: list[str] = []
            if conflicts:
                parts.append(f"skipped (target exists): {', '.join(conflicts)}")
            if failures:
                parts.append(f"failed: {', '.join(failures)}")
            raise RenameError(
                "; ".join(parts),
                completed=completed,
                conflicts=conflicts,
                failures=failures,
            )

        return completed

    def revert(self, batch: RenameBatch) -> None:
        """Undo a batch by renaming ``new_path`` back to ``old_path``.

        Reverts in reverse apply order. Targets that no longer exist are
        skipped with a warning rather than raising.

        Args:
            batch: The batch previously returned by ``apply()``.
        """
        for cmd in reversed(batch.commands):
            if not os.path.exists(cmd.new_path):
                logger.warning(
                    "Revert skipped: %s no longer exists", cmd.new_path
                )
                continue
            try:
                os.rename(cmd.new_path, cmd.old_path)
            except (OSError, PermissionError) as exc:
                logger.error(
                    "Failed to revert %s → %s: %s",
                    cmd.new_path,
                    cmd.old_path,
                    exc,
                )

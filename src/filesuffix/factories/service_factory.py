"""Factory for constructing services and model helpers."""

from __future__ import annotations

from filesuffix.models.file_type_filter import FileTypeFilter
from filesuffix.models.suffix_renamer import SuffixRenamer
from filesuffix.models.undo_manager import UndoManager
from filesuffix.services.file_system_service import FileSystemService
from filesuffix.services.rename_service import RenameService


class ServiceFactory:
    """Creates services and stateless model helpers (Factory pattern)."""

    def create_file_system_service(self) -> FileSystemService:
        """Build and return a new ``FileSystemService``.

        Returns:
            A freshly constructed ``FileSystemService``.
        """
        return FileSystemService()

    def create_rename_service(self) -> RenameService:
        """Build and return a new ``RenameService``.

        Returns:
            A freshly constructed ``RenameService``.
        """
        return RenameService()

    def create_suffix_renamer(self) -> SuffixRenamer:
        """Build and return a new ``SuffixRenamer``.

        Returns:
            A freshly constructed ``SuffixRenamer``.
        """
        return SuffixRenamer()

    def create_undo_manager(self) -> UndoManager:
        """Build and return a new ``UndoManager``.

        Returns:
            A freshly constructed ``UndoManager`` with an empty history.
        """
        return UndoManager()

    def create_file_type_filter(self) -> FileTypeFilter:
        """Build and return a new ``FileTypeFilter`` (allow-all by default).

        Returns:
            A freshly constructed ``FileTypeFilter`` with no restrictions.
        """
        return FileTypeFilter()

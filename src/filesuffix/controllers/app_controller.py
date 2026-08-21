"""Application controller — wires views to services and models."""

from __future__ import annotations

import logging

from PySide6.QtWidgets import QMessageBox

from filesuffix.models.file_entry import FileEntry
from filesuffix.models.file_type_filter import FileTypeFilter
from filesuffix.models.suffix_renamer import SuffixRenamer
from filesuffix.models.undo_manager import UndoManager
from filesuffix.services.file_system_service import FileSystemService
from filesuffix.services.rename_service import RenameError, RenameService
from filesuffix.views.file_browser_view import FileBrowserView
from filesuffix.views.filter_bar_widget import FilterBarWidget
from filesuffix.views.main_window import MainWindow
from filesuffix.views.suffix_input_widget import SuffixInputWidget

logger = logging.getLogger(__name__)


class AppController:
    """Coordinates views, services, and models for the app.

    This class is the only place where Qt signals are connected to business
    logic. It holds no state of its own beyond references to its collaborators
    and the in-memory list of current file entries.
    """

    def __init__(
        self,
        window: MainWindow,
        browser: FileBrowserView,
        filter_bar: FilterBarWidget,
        suffix_input: SuffixInputWidget,
        fs_service: FileSystemService,
        rename_service: RenameService,
        renamer: SuffixRenamer,
        undo_manager: UndoManager,
        type_filter: FileTypeFilter,
    ) -> None:
        """Store collaborators and connect all view signals to handlers.

        Args:
            window: The top-level window for showing status messages and
                error dialogs.
            browser: The file browser widget.
            filter_bar: The extension filter bar.
            suffix_input: The suffix input with Apply / Undo buttons.
            fs_service: Service for scanning directories.
            rename_service: Service for performing and reverting renames.
            renamer: Pure-logic helper for computing new file names.
            undo_manager: History stack for the Undo action.
            type_filter: Extension filter applied before populating the
                browser.
        """
        self._window = window
        self._browser = browser
        self._filter_bar = filter_bar
        self._suffix_input = suffix_input
        self._fs_service = fs_service
        self._rename_service = rename_service
        self._renamer = renamer
        self._undo_manager = undo_manager
        self._type_filter = type_filter

        self._all_entries: list[FileEntry] = []

        self._connect_signals()

    # ------------------------------------------------------------------
    # Signal connections
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        """Connect view signals to the appropriate handler methods."""
        self._browser.folder_chosen.connect(self._on_folder_chosen)
        self._filter_bar.filter_changed.connect(self._on_filter_changed)
        self._suffix_input.apply_requested.connect(self._on_apply_requested)
        self._suffix_input.undo_requested.connect(self._on_undo_requested)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _on_folder_chosen(self, directory: str) -> None:
        """Scan the chosen directory and refresh the browser.

        Clears undo history because prior renames were in a different folder.

        Args:
            directory: Absolute path of the folder the user selected.
        """
        if not self._fs_service.is_reachable(directory):
            self._window.show_message(f"Cannot reach: {directory}")
            QMessageBox.warning(
                self._window,
                "Folder unreachable",
                f"The folder could not be accessed:\n{directory}",
            )
            return

        try:
            self._all_entries = self._fs_service.list_files(directory)
        except OSError as exc:
            self._window.show_message("Error reading folder.")
            QMessageBox.critical(self._window, "Read error", str(exc))
            return

        self._browser.set_current_directory(directory)
        self._undo_manager.clear()
        self._suffix_input.set_undo_enabled(False)

        available_types = {e.extension for e in self._all_entries if e.extension}
        self._filter_bar.set_available_types(available_types)
        self._type_filter.set_allowed(self._filter_bar.allowed_extensions())

        self._refresh_browser()
        count = len(self._all_entries)
        self._window.show_message(f"Loaded {count} file{'s' if count != 1 else ''}.")

    def _on_filter_changed(self, extensions: set[str]) -> None:
        """Apply the new extension filter and repopulate the browser.

        Args:
            extensions: Normalized set of allowed extensions; empty means all.
        """
        self._type_filter.set_allowed(extensions)
        self._refresh_browser()

    def _on_apply_requested(self, suffix: str) -> None:
        """Validate, compute renames, execute them, and push to undo history.

        Args:
            suffix: The suffix text entered by the user.
        """
        if not self._renamer.is_valid_suffix(suffix):
            self._window.show_message("Invalid suffix — check for illegal characters.")
            QMessageBox.warning(
                self._window,
                "Invalid suffix",
                "The suffix is empty or contains characters that are not\n"
                "allowed in file names: < > : \" / \\ | ? *",
            )
            return

        selected = self._browser.selected_paths()
        if not selected:
            self._window.show_message("No files selected.")
            return

        planned = [
            (path, self._renamer.build_new_path(path, suffix))
            for path in selected
        ]

        partial_batch = None
        try:
            batch = self._rename_service.apply(planned)
            partial_batch = batch
        except RenameError as exc:
            partial_batch = exc.completed
            self._show_rename_error(exc)

        if partial_batch and partial_batch.commands:
            self._undo_manager.push(partial_batch)
            self._suffix_input.set_undo_enabled(True)

        self._reload_current_folder()

    def _on_undo_requested(self) -> None:
        """Revert the most recent rename batch."""
        batch = self._undo_manager.pop()
        if batch is None:
            self._window.show_message("Nothing to undo.")
            return

        self._rename_service.revert(batch)
        self._suffix_input.set_undo_enabled(self._undo_manager.can_undo())
        self._reload_current_folder()
        self._window.show_message("Undo complete.")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _refresh_browser(self) -> None:
        """Repopulate the browser from the current entries after filtering."""
        visible = [e for e in self._all_entries if self._type_filter.accepts(e)]
        self._browser.set_files(visible)
        self._suffix_input.set_apply_enabled(bool(visible))

    def _reload_current_folder(self) -> None:
        """Re-scan the current directory and refresh the browser."""
        directory = self._browser.current_directory()
        if directory:
            try:
                self._all_entries = self._fs_service.list_files(directory)
            except OSError as exc:
                self._window.show_message("Error re-reading folder.")
                logger.error("Reload failed: %s", exc)
                return
            self._refresh_browser()

    def _show_rename_error(self, exc: RenameError) -> None:
        """Display a dialog describing rename conflicts or failures.

        Args:
            exc: The ``RenameError`` raised by ``RenameService.apply``.
        """
        lines: list[str] = []
        if exc.conflicts:
            lines.append("Skipped (target already exists):\n  " + "\n  ".join(exc.conflicts))
        if exc.failures:
            lines.append("Failed:\n  " + "\n  ".join(exc.failures))
        QMessageBox.warning(self._window, "Rename issues", "\n\n".join(lines))

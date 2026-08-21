"""File browser widget with multi-select and UNC path support."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from filesuffix.models.file_entry import FileEntry


def _human_size(size_bytes: int) -> str:
    """Format a byte count as a human-readable string.

    Args:
        size_bytes: Number of bytes.

    Returns:
        A concise string such as ``"1.4 MB"`` or ``"512 B"``.
    """
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024 or unit == "TB":
            return f"{size_bytes:.1f} {unit}" if unit != "B" else f"{size_bytes} B"
        size_bytes //= 1024
    return str(size_bytes)


class FileBrowserView(QWidget):
    """Displays files of the current folder and supports multi-selection.

    Signals:
        folder_chosen (str): Emitted with a directory path when the user picks
            a folder via the dialog or the path entry.
        selection_changed (): Emitted when the file selection changes.
    """

    folder_chosen: Signal = Signal(str)
    selection_changed: Signal = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Set up the browser layout.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._current_directory: str = ""
        self._entries: list[FileEntry] = []
        self._build_ui()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_files(self, entries: list[FileEntry]) -> None:
        """Populate the list with file entries, replacing previous contents.

        Args:
            entries: File entries to display.
        """
        self._entries = entries
        self._tree.blockSignals(True)
        self._tree.clear()
        for entry in entries:
            item = QTreeWidgetItem([
                entry.name,
                _human_size(entry.size_bytes),
                entry.extension.lstrip(".").upper() or "—",
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, entry.path)
            self._tree.addTopLevelItem(item)
        self._tree.blockSignals(False)

    def selected_paths(self) -> list[str]:
        """Return absolute paths of the currently selected files.

        Returns:
            A list of paths; empty when no items are selected.
        """
        return [
            item.data(0, Qt.ItemDataRole.UserRole)
            for item in self._tree.selectedItems()
        ]

    def current_directory(self) -> str:
        """Return the folder currently being displayed.

        Returns:
            The absolute directory path, or an empty string if none has been
            chosen yet.
        """
        return self._current_directory

    def set_current_directory(self, path: str) -> None:
        """Update the displayed directory label.

        Args:
            path: The directory now being shown.
        """
        self._current_directory = path
        self._path_edit.setText(path)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Construct and arrange child widgets."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # --- path bar ---
        path_bar = QHBoxLayout()
        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText(
            r"Type or paste a path (e.g. \\server\share\folder) and press Enter"
        )
        self._path_edit.returnPressed.connect(self._on_path_entered)

        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._on_browse_clicked)

        path_bar.addWidget(QLabel("Folder:"))
        path_bar.addWidget(self._path_edit, stretch=1)
        path_bar.addWidget(browse_btn)
        layout.addLayout(path_bar)

        # --- file tree ---
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Name", "Size", "Type"])
        self._tree.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self._tree.setRootIsDecorated(False)
        self._tree.setSortingEnabled(True)
        self._tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        header = self._tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._tree.itemSelectionChanged.connect(self.selection_changed)

        layout.addWidget(self._tree)

    def _on_browse_clicked(self) -> None:
        """Open a native folder picker and emit ``folder_chosen``."""
        start = self._current_directory or ""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            start,
            QFileDialog.Option.ShowDirsOnly,
        )
        if directory:
            self.folder_chosen.emit(directory)

    def _on_path_entered(self) -> None:
        """Emit ``folder_chosen`` with the text in the path entry field."""
        path = self._path_edit.text().strip()
        if path:
            self.folder_chosen.emit(path)

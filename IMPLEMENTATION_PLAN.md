# Implementation Plan — Batch File Suffix Appender

A desktop GUI app to batch-add a suffix to selected file names, with an undo
button to reverse mistakes. Built with **PySide6 (Qt)**. The suffix is inserted
**before the file extension** (`report.pdf` + `_v2` → `report_v2.pdf`).

This document is a build spec. Implement the files in the order given in
Section 8. Each class has a single responsibility and a Google-style docstring.

---

## 1. Goals & Requirements

Functional:
1. Browse a folder, including **Windows network drives** via UNC paths
   (`\\server\share\folder`) and mapped drives (`Z:\`).
2. Select **multiple files** from the browser.
3. Enter a **suffix** in a dialog / input field.
4. **Apply** button: rename every selected file, inserting the suffix before
   its extension.
5. **Undo** button: revert the most recent apply operation.
6. **Filter by file type** (extension) in the browser so unwanted types are
   hidden.

Non-functional:
- MVC separation (Model / View / Controller), Factory pattern for widget and
  service creation, Command pattern for undo.
- Single-responsibility classes and functions.
- Google-format docstrings on every public class and function.
- Cross-platform (developed on Linux/Raspberry Pi, run on Windows).

---

## 2. Tech Stack & Project Setup

- Python 3.10+
- PySide6 (`pip install PySide6`)
- pytest (dev only) for model/service unit tests

Create these files:

```
requirements.txt
pyproject.toml            # optional; project metadata + tool config
README.md
src/
  filesuffix/
    __init__.py
    app.py                # entry point: builds and runs the app
    config.py             # constants / settings

    models/
      __init__.py
      file_entry.py       # FileEntry dataclass
      file_type_filter.py # FileTypeFilter
      rename_command.py    # RenameCommand (Command pattern) + RenameBatch
      suffix_renamer.py    # SuffixRenamer (pure name-computation logic)
      undo_manager.py      # UndoManager (history stack)

    services/
      __init__.py
      rename_service.py    # RenameService: performs/reverts filesystem renames
      file_system_service.py # FileSystemService: scan dir, network reachability

    views/
      __init__.py
      main_window.py       # MainWindow (top-level View)
      file_browser_view.py # FileBrowserView (tree of files)
      suffix_input_widget.py # SuffixInputWidget
      filter_bar_widget.py # FilterBarWidget (file-type filter)
      status_bar_widget.py # optional status/message area

    controllers/
      __init__.py
      app_controller.py    # AppController: wires views <-> models/services

    factories/
      __init__.py
      widget_factory.py    # WidgetFactory: builds view widgets
      service_factory.py   # ServiceFactory: builds services/models

tests/
  test_suffix_renamer.py
  test_rename_command.py
  test_undo_manager.py
  test_file_type_filter.py
  test_rename_service.py
```

`requirements.txt`:
```
PySide6>=6.5
```

---

## 3. Architecture Overview

```
                 +------------------+
                 |   AppController  |   (controllers/app_controller.py)
                 +--------+---------+
                          |  connects signals, orchestrates
        +-----------------+------------------+
        |                 |                  |
   +----v----+      +-----v------+     +-----v-------+
   |  Views  |      |  Services  |     |   Models    |
   | (Qt)    |      | rename/fs  |     | data + logic|
   +---------+      +------------+     +-------------+

  Factories build Views and Services so the controller never calls
  constructors directly (Factory pattern).

  Undo is a Command pattern: each apply produces a RenameBatch (list of
  RenameCommand). UndoManager keeps a stack of batches; undo() reverts the
  top batch.
```

Data flow for **Apply**:
1. View emits "apply requested" with the current suffix text.
2. Controller reads selected file paths from `FileBrowserView`.
3. Controller asks `SuffixRenamer` to compute new names → list of
   `(old_path, new_path)`.
4. Controller passes them to `RenameService.apply(...)`, which performs renames
   and returns a `RenameBatch`.
5. Controller pushes the batch onto `UndoManager` and refreshes the browser.

Data flow for **Undo**:
1. View emits "undo requested".
2. Controller calls `UndoManager.pop()` → `RenameBatch` (or None).
3. Controller calls `RenameService.revert(batch)`.
4. Controller refreshes the browser and updates status.

---

## 4. Model Layer (pure logic, no Qt imports)

Keep this layer free of PySide6 imports so it is unit-testable in isolation.

### 4.1 `models/file_entry.py` — `FileEntry`
Immutable dataclass describing one file.

```python
from __future__ import annotations
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class FileEntry:
    """A single file discovered in the browser.

    Attributes:
        path: Absolute path to the file (may be a UNC path).
        name: File name including extension (e.g. "report.pdf").
        size_bytes: File size in bytes.

    """

    path: str
    name: str
    size_bytes: int

    @property
    def extension(self) -> str:
        """Return the lowercase extension including the dot, or "".

        Returns:
            The extension such as ".pdf", or an empty string when the file
            has no extension.

        """
        return os.path.splitext(self.name)[1].lower()

    @classmethod
    def from_path(cls, path: str) -> "FileEntry":
        """Build a FileEntry from a filesystem path.

        Args:
            path: Absolute path to an existing file.

        Returns:
            A populated FileEntry.

        """
        return cls(
            path=path,
            name=os.path.basename(path),
            size_bytes=os.path.getsize(path),
        )
```

### 4.2 `models/suffix_renamer.py` — `SuffixRenamer`
Pure logic that computes new file names. **No filesystem writes here.**

Responsibilities:
- Insert the suffix before the extension.
- Handle no-extension files (append suffix to the name).
- Handle multi-dot names using the *last* extension only
  (`data.tar.gz` → `data.tar_v2.gz`).
- Validate the suffix (reject characters illegal on Windows:
  `< > : " / \ | ? *`).

```python
class SuffixRenamer:
    """Computes new file names by inserting a suffix before the extension."""

    _ILLEGAL_CHARS = set('<>:"/\\|?*')

    def is_valid_suffix(self, suffix: str) -> bool:
        """Return True if the suffix is non-empty and filesystem-safe.

        Args:
            suffix: Candidate suffix text.

        Returns:
            True when the suffix contains no illegal characters and is not
            empty; otherwise False.

        """

    def build_new_name(self, file_name: str, suffix: str) -> str:
        """Insert the suffix before the extension of a single file name.

        Args:
            file_name: Original name including extension, e.g. "report.pdf".
            suffix: Text to insert, e.g. "_v2".

        Returns:
            The new file name, e.g. "report_v2.pdf". Names without an
            extension get the suffix appended: "README" -> "README_v2".

        """

    def build_new_path(self, path: str, suffix: str) -> str:
        """Compute the full new path for a file given a suffix.

        Args:
            path: Absolute original path.
            suffix: Text to insert before the extension.

        Returns:
            The absolute new path in the same directory.

        """
```

Implementation note for `build_new_name`: use `os.path.splitext`; if the second
element (ext) is empty, return `file_name + suffix`, else return
`root + suffix + ext`.

### 4.3 `models/file_type_filter.py` — `FileTypeFilter`
Decides whether a `FileEntry` passes the active type filter.

```python
class FileTypeFilter:
    """Filters files by extension.

    An empty allow-set means "allow all". Extensions are compared
    case-insensitively and normalized to include a leading dot.
    """

    def __init__(self, allowed_extensions: set[str] | None = None) -> None:
        """Initialize the filter.

        Args:
            allowed_extensions: Extensions to keep (e.g. {".pdf", ".txt"}).
                None or empty means all files pass.

        """

    def set_allowed(self, extensions: set[str]) -> None:
        """Replace the allowed extension set (normalized internally)."""

    def accepts(self, entry: FileEntry) -> bool:
        """Return True if the entry should be shown under the current filter."""
```

### 4.4 `models/rename_command.py` — `RenameCommand`, `RenameBatch`
Command pattern objects that record a single rename and a batch of them.

```python
@dataclass(frozen=True)
class RenameCommand:
    """A reversible record of one file rename.

    Attributes:
        old_path: Path before the rename.
        new_path: Path after the rename.

    """

    old_path: str
    new_path: str


@dataclass
class RenameBatch:
    """A group of renames applied together, revertible as a unit.

    Attributes:
        commands: The individual RenameCommand records in apply order.

    """

    commands: list[RenameCommand]
```

### 4.5 `models/undo_manager.py` — `UndoManager`
LIFO stack of `RenameBatch`. Pure data structure; no filesystem access.

```python
class UndoManager:
    """Maintains a history of rename batches for undo."""

    def push(self, batch: RenameBatch) -> None:
        """Record a completed batch as the most recent operation."""

    def pop(self) -> RenameBatch | None:
        """Remove and return the most recent batch, or None if empty."""

    def can_undo(self) -> bool:
        """Return True when there is at least one batch to undo."""

    def clear(self) -> None:
        """Discard all history (e.g. after changing folders)."""
```

Optional: cap history depth via a constant in `config.py`
(`MAX_UNDO_DEPTH = 20`).

---

## 5. Service Layer (does the actual I/O)

### 5.1 `services/rename_service.py` — `RenameService`
Performs and reverts filesystem renames. This is the only model/service class
that mutates the disk.

```python
class RenameService:
    """Executes and reverts file rename operations on disk."""

    def apply(self, planned: list[tuple[str, str]]) -> RenameBatch:
        """Rename each (old_path, new_path) pair on disk.

        Skips any pair whose target already exists to avoid overwriting.
        Renames are done one by one; already-completed renames are recorded
        so a partial failure can still be undone.

        Args:
            planned: Pairs of (old_path, new_path) to apply.

        Returns:
            A RenameBatch describing the renames that succeeded.

        Raises:
            RenameError: If a rename fails; the returned/raised state lists
                what already succeeded so the caller can revert.

        """

    def revert(self, batch: RenameBatch) -> None:
        """Undo a batch by renaming new_path back to old_path.

        Reverts in reverse order. Missing targets are skipped with a warning.

        Args:
            batch: The batch previously returned by apply().

        """
```

Define a small `RenameError(Exception)` in this module.

Windows/network notes:
- Use `os.replace`/`os.rename` with full paths; UNC paths work unchanged.
- Before overwriting, check `os.path.exists(new_path)`; skip and collect a
  conflict message rather than clobbering.
- Wrap each rename in try/except to catch `PermissionError` / `OSError`
  (network share may be read-only or disconnected).

### 5.2 `services/file_system_service.py` — `FileSystemService`
Directory scanning and network reachability checks. Keeps Qt out of the model.

```python
class FileSystemService:
    """Reads directory contents and checks path reachability."""

    def list_files(self, directory: str) -> list[FileEntry]:
        """Return FileEntry objects for the files directly in a directory.

        Args:
            directory: Absolute directory path (local, mapped drive, or UNC).

        Returns:
            One FileEntry per regular file (directories excluded).

        Raises:
            OSError: If the directory cannot be read (e.g. share offline).

        """

    def is_reachable(self, path: str) -> bool:
        """Return True if the path exists and is accessible.

        Useful to warn the user when a network share is disconnected.
        """
```

---

## 6. View Layer (PySide6 widgets only; no business logic)

Views expose Qt signals and simple getters/setters. They never call the
services or perform renames — the controller does that.

### 6.1 `views/file_browser_view.py` — `FileBrowserView`
A widget showing the current folder's files with multi-select and a size
column. Recommended approach: `QListWidget` or `QTreeWidget` populated from
`FileEntry` objects (simpler to filter than `QFileSystemModel`), plus a
"Choose folder…" button that opens `QFileDialog.getExistingDirectory` (this
dialog can navigate to `\\server\share`).

Responsibilities / API:
```python
class FileBrowserView(QWidget):
    """Displays files of the current folder and supports multi-selection.

    Signals:
        folder_chosen (str): Emitted with a directory path when the user picks
            a folder.
        selection_changed (): Emitted when the file selection changes.

    """

    def set_files(self, entries: list[FileEntry]) -> None:
        """Populate the list with file entries (replacing previous contents)."""

    def selected_paths(self) -> list[str]:
        """Return absolute paths of the currently selected files."""

    def current_directory(self) -> str:
        """Return the folder currently being displayed."""
```
- Enable multi-selection: `setSelectionMode(QAbstractItemView.ExtendedSelection)`.
- Show columns: Name | Size (human-readable) | Type.
- Provide a "Choose folder…" button; also allow typing/pasting a UNC path into
  a `QLineEdit` and pressing Enter (helps when the dialog is slow on network).

### 6.2 `views/filter_bar_widget.py` — `FilterBarWidget`
Controls the file-type filter.

```python
class FilterBarWidget(QWidget):
    """Lets the user restrict the browser to chosen file types.

    Signals:
        filter_changed (set): Emitted with the set of allowed extensions
            (empty set means "all types").

    """

    def set_available_types(self, extensions: set[str]) -> None:
        """Update the selectable extension list from the current folder."""

    def allowed_extensions(self) -> set[str]:
        """Return the currently selected extensions (empty = all)."""
```
Implement as either a multi-check dropdown or a `QLineEdit` accepting a
comma-separated list like `pdf, txt, docx`. Normalize to `{".pdf", ...}`.

### 6.3 `views/suffix_input_widget.py` — `SuffixInputWidget`
Suffix entry plus the Apply and Undo buttons.

```python
class SuffixInputWidget(QWidget):
    """Suffix text field with Apply and Undo actions.

    Signals:
        apply_requested (str): Emitted with the suffix text on Apply.
        undo_requested (): Emitted on Undo.

    """

    def suffix_text(self) -> str:
        """Return the current suffix string, trimmed of surrounding spaces."""

    def set_undo_enabled(self, enabled: bool) -> None:
        """Enable or disable the Undo button."""

    def set_apply_enabled(self, enabled: bool) -> None:
        """Enable or disable the Apply button."""
```

### 6.4 `views/main_window.py` — `MainWindow`
Assembles the child widgets into a layout. Receives already-built child widgets
via its constructor (built by the factory) so it does not construct them itself.

```python
class MainWindow(QMainWindow):
    """Top-level window arranging the browser, filter bar, and controls."""

    def __init__(
        self,
        browser: FileBrowserView,
        filter_bar: FilterBarWidget,
        suffix_input: SuffixInputWidget,
    ) -> None:
        """Arrange the provided child widgets into the main layout."""

    def show_message(self, text: str) -> None:
        """Display a transient message in the status bar."""
```

---

## 7. Controller & Factories

### 7.1 `controllers/app_controller.py` — `AppController`
The only place that connects views to services/models. Holds no widgets of its
own beyond references passed in.

Responsibilities:
- Connect `browser.folder_chosen` → scan folder, apply filter, populate browser,
  update available types, `undo.clear()`.
- Connect `filter_bar.filter_changed` → re-filter current entries and repopulate.
- Connect `suffix_input.apply_requested` → validate suffix, compute planned
  renames, call `RenameService.apply`, push batch to `UndoManager`, refresh,
  toggle Undo enabled.
- Connect `suffix_input.undo_requested` → pop batch, `RenameService.revert`,
  refresh, toggle Undo enabled.
- Surface errors/conflicts via `MainWindow.show_message` and/or
  `QMessageBox`.

```python
class AppController:
    """Coordinates views, services, and models for the app."""

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
        """Store collaborators and connect all view signals to handlers."""

    def _on_folder_chosen(self, directory: str) -> None: ...
    def _on_filter_changed(self, extensions: set) -> None: ...
    def _on_apply_requested(self, suffix: str) -> None: ...
    def _on_undo_requested(self) -> None: ...
    def _refresh_browser(self) -> None: ...
```

Keep each handler small; push real work down to services/models.

### 7.2 `factories/widget_factory.py` — `WidgetFactory`
Builds and returns the view widgets and the assembled `MainWindow`.

```python
class WidgetFactory:
    """Creates view widgets and the main window (Factory pattern)."""

    def create_main_window(self) -> tuple[MainWindow, FileBrowserView,
                                           FilterBarWidget, SuffixInputWidget]:
        """Build all view widgets and the window that hosts them.

        Returns:
            The MainWindow plus the three child widgets the controller needs
            to connect to.

        """
```

### 7.3 `factories/service_factory.py` — `ServiceFactory`
Builds services and model helpers.

```python
class ServiceFactory:
    """Creates services and stateless model helpers (Factory pattern)."""

    def create_file_system_service(self) -> FileSystemService: ...
    def create_rename_service(self) -> RenameService: ...
    def create_suffix_renamer(self) -> SuffixRenamer: ...
    def create_undo_manager(self) -> UndoManager: ...
    def create_file_type_filter(self) -> FileTypeFilter: ...
```

### 7.4 `app.py` — entry point
```python
def main() -> int:
    """Build the app via factories, wire the controller, and run Qt.

    Returns:
        The Qt application exit code.

    """
    app = QApplication(sys.argv)
    widgets = WidgetFactory()
    services = ServiceFactory()

    window, browser, filter_bar, suffix_input = widgets.create_main_window()
    controller = AppController(
        window, browser, filter_bar, suffix_input,
        services.create_file_system_service(),
        services.create_rename_service(),
        services.create_suffix_renamer(),
        services.create_undo_manager(),
        services.create_file_type_filter(),
    )
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## 8. Build Order (implement in this sequence)

1. **Project scaffold**: directories, `requirements.txt`, empty `__init__.py`
   files, `config.py` (constants: `APP_NAME`, `MAX_UNDO_DEPTH`, illegal chars).
2. **Models** (no Qt): `file_entry.py`, `suffix_renamer.py`,
   `file_type_filter.py`, `rename_command.py`, `undo_manager.py`.
3. **Unit tests** for the models (Section 9). Get them green before touching UI.
4. **Services**: `file_system_service.py`, `rename_service.py` + tests using
   `tmp_path`.
5. **Views**: build each widget, run it standalone with a tiny `__main__` block
   to eyeball layout.
6. **Factories**: `widget_factory.py`, `service_factory.py`.
7. **Controller**: `app_controller.py` wiring everything.
8. **Entry point**: `app.py`; manual end-to-end test.
9. **README**: run instructions.

---

## 9. Testing

Model/service tests run without a display (no Qt needed):

- `test_suffix_renamer.py`
  - `report.pdf` + `_v2` → `report_v2.pdf`
  - `README` + `_v2` → `README_v2`
  - `data.tar.gz` + `_v2` → `data.tar_v2.gz`
  - illegal suffix (`a/b`) → `is_valid_suffix` False
  - empty suffix → invalid
- `test_file_type_filter.py`
  - empty allow-set accepts everything
  - `{".pdf"}` accepts `x.PDF` (case-insensitive), rejects `x.txt`
- `test_rename_command.py` / `test_undo_manager.py`
  - push/pop LIFO order, `can_undo`, `clear`, depth cap
- `test_rename_service.py` (use pytest `tmp_path`)
  - apply renames files on disk and returns a batch
  - revert restores original names
  - target-exists conflict is skipped, not overwritten
  - round trip: apply then revert leaves the directory identical

Manual UI checklist:
- Open a local folder, multi-select, apply, verify names, undo.
- Paste a UNC path (`\\server\share\...`) and confirm listing works.
- Apply the type filter and confirm the list narrows.
- Undo after closing/reopening is expected to be unavailable (history cleared
  on folder change) — confirm the button disables correctly.

---

## 10. Edge Cases & Rules

- **No selection on Apply**: show a message, do nothing.
- **Empty/invalid suffix**: block apply, explain why.
- **Name collision**: if the target name already exists, skip that file and
  report it; never overwrite.
- **Network share offline**: catch `OSError`; show a clear message and keep the
  app responsive.
- **Read-only files / permissions**: catch `PermissionError`; report which
  files failed; already-succeeded renames in the batch remain undoable.
- **Undo history reset**: clear history when the folder changes to avoid
  reverting into a different directory context.
- **Duplicate apply**: applying the same suffix twice yields
  `report_v2_v2.pdf`; that is acceptable and each apply is independently
  undoable.

---

## 11. Coding Standards

- Google-style docstrings on every public module, class, and function.
- Type hints everywhere; `from __future__ import annotations` at file tops.
- No business logic in views; no Qt imports in models.
- One class per responsibility; functions do one thing.
- Constants live in `config.py`, not scattered as literals.

"""Filter bar widget for restricting the file browser by file type."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget


class FilterBarWidget(QWidget):
    """Lets the user restrict the browser to chosen file types.

    The user enters a comma-separated list of extensions (e.g. ``pdf, txt``).
    An empty field means "show all types".

    Signals:
        filter_changed (set): Emitted with the set of allowed normalized
            extensions (e.g. ``{".pdf", ".txt"}``). An empty set means all
            types are shown.
    """

    filter_changed: Signal = Signal(set)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Set up the filter bar layout.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._build_ui()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_available_types(self, extensions: set[str]) -> None:
        """Update the placeholder hint from the current folder's types.

        Args:
            extensions: The extensions present in the current folder
                (e.g. ``{".pdf", ".txt"}``).
        """
        if extensions:
            sample = ", ".join(
                sorted(e.lstrip(".") for e in extensions)
            )
            self._edit.setPlaceholderText(f"Filter by type: {sample}")
        else:
            self._edit.setPlaceholderText("Filter by type: e.g. pdf, txt")

    def allowed_extensions(self) -> set[str]:
        """Return the currently entered extensions, normalized.

        Returns:
            A set of lowercase dot-prefixed extensions such as
            ``{".pdf", ".txt"}``, or an empty set when the field is blank.
        """
        return self._parse(self._edit.text())

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Construct and arrange child widgets."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._edit = QLineEdit()
        self._edit.setPlaceholderText("Filter by type: e.g. pdf, txt")
        self._edit.textChanged.connect(self._on_text_changed)

        layout.addWidget(QLabel("Type filter:"))
        layout.addWidget(self._edit, stretch=1)

    def _on_text_changed(self, _text: str) -> None:
        """Emit ``filter_changed`` with the parsed extension set."""
        self.filter_changed.emit(self.allowed_extensions())

    @staticmethod
    def _parse(text: str) -> set[str]:
        """Parse a comma-separated extension list into a normalized set.

        Args:
            text: Raw user input such as ``"pdf, TXT, .docx"``.

        Returns:
            Normalized set such as ``{".pdf", ".txt", ".docx"}``.
        """
        result: set[str] = set()
        for token in text.split(","):
            token = token.strip().lower()
            if not token:
                continue
            if not token.startswith("."):
                token = "." + token
            result.add(token)
        return result

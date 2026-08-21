"""Suffix entry with Apply and Undo controls."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget


class SuffixInputWidget(QWidget):
    """Suffix text field with Apply and Undo actions.

    Signals:
        apply_requested (str): Emitted with the trimmed suffix text when the
            user clicks Apply or presses Enter in the text field.
        undo_requested (): Emitted when the user clicks Undo.
    """

    apply_requested: Signal = Signal(str)
    undo_requested: Signal = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Set up the suffix input layout.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._build_ui()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def suffix_text(self) -> str:
        """Return the current suffix string, trimmed of surrounding spaces.

        Returns:
            The trimmed text from the suffix input field.
        """
        return self._edit.text().strip()

    def set_undo_enabled(self, enabled: bool) -> None:
        """Enable or disable the Undo button.

        Args:
            enabled: ``True`` to enable the button, ``False`` to disable.
        """
        self._undo_btn.setEnabled(enabled)

    def set_apply_enabled(self, enabled: bool) -> None:
        """Enable or disable the Apply button.

        Args:
            enabled: ``True`` to enable the button, ``False`` to disable.
        """
        self._apply_btn.setEnabled(enabled)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Construct and arrange child widgets."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._edit = QLineEdit()
        self._edit.setPlaceholderText("Suffix to add (e.g. _v2)")
        self._edit.returnPressed.connect(self._on_apply)

        self._apply_btn = QPushButton("Apply")
        self._apply_btn.setEnabled(False)
        self._apply_btn.clicked.connect(self._on_apply)

        self._undo_btn = QPushButton("Undo")
        self._undo_btn.setEnabled(False)
        self._undo_btn.clicked.connect(self.undo_requested)

        layout.addWidget(QLabel("Suffix:"))
        layout.addWidget(self._edit, stretch=1)
        layout.addWidget(self._apply_btn)
        layout.addWidget(self._undo_btn)

    def _on_apply(self) -> None:
        """Emit ``apply_requested`` with the current suffix text."""
        self.apply_requested.emit(self.suffix_text())

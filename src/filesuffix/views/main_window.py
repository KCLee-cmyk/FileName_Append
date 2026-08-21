"""Top-level application window."""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from filesuffix.config import APP_NAME
from filesuffix.views.file_browser_view import FileBrowserView
from filesuffix.views.filter_bar_widget import FilterBarWidget
from filesuffix.views.suffix_input_widget import SuffixInputWidget


class MainWindow(QMainWindow):
    """Top-level window arranging the browser, filter bar, and controls.

    Child widgets are injected via the constructor so ``MainWindow`` has no
    knowledge of how they are built (Factory pattern).
    """

    def __init__(
        self,
        browser: FileBrowserView,
        filter_bar: FilterBarWidget,
        suffix_input: SuffixInputWidget,
        parent: QWidget | None = None,
    ) -> None:
        """Arrange the provided child widgets into the main layout.

        Args:
            browser: The file browser widget.
            filter_bar: The extension filter bar.
            suffix_input: The suffix entry with Apply / Undo buttons.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle(APP_NAME)
        self.resize(800, 550)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(browser)
        layout.addWidget(filter_bar)
        layout.addWidget(suffix_input)
        self.setCentralWidget(central)

        self.statusBar().showMessage("Ready")

    def show_message(self, text: str) -> None:
        """Display a transient message in the status bar.

        Args:
            text: The message to display.
        """
        self.statusBar().showMessage(text)

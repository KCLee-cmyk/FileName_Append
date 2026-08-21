"""Factory for constructing all view widgets."""

from __future__ import annotations

from filesuffix.views.file_browser_view import FileBrowserView
from filesuffix.views.filter_bar_widget import FilterBarWidget
from filesuffix.views.main_window import MainWindow
from filesuffix.views.suffix_input_widget import SuffixInputWidget


class WidgetFactory:
    """Creates view widgets and the main window (Factory pattern).

    Using a factory keeps widget construction out of the controller and entry
    point, making each piece independently replaceable (e.g. for testing with
    stub widgets).
    """

    def create_file_browser_view(self) -> FileBrowserView:
        """Build and return a new ``FileBrowserView``.

        Returns:
            A freshly constructed ``FileBrowserView``.
        """
        return FileBrowserView()

    def create_filter_bar_widget(self) -> FilterBarWidget:
        """Build and return a new ``FilterBarWidget``.

        Returns:
            A freshly constructed ``FilterBarWidget``.
        """
        return FilterBarWidget()

    def create_suffix_input_widget(self) -> SuffixInputWidget:
        """Build and return a new ``SuffixInputWidget``.

        Returns:
            A freshly constructed ``SuffixInputWidget``.
        """
        return SuffixInputWidget()

    def create_main_window(
        self,
    ) -> tuple[MainWindow, FileBrowserView, FilterBarWidget, SuffixInputWidget]:
        """Build all view widgets and the window that hosts them.

        Returns:
            A 4-tuple of ``(MainWindow, FileBrowserView, FilterBarWidget,
            SuffixInputWidget)``. The controller needs the three child widgets
            to connect their signals.
        """
        browser = self.create_file_browser_view()
        filter_bar = self.create_filter_bar_widget()
        suffix_input = self.create_suffix_input_widget()
        window = MainWindow(browser, filter_bar, suffix_input)
        return window, browser, filter_bar, suffix_input

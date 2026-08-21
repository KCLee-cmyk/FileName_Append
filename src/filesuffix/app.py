"""Application entry point."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from filesuffix.controllers.app_controller import AppController
from filesuffix.factories.service_factory import ServiceFactory
from filesuffix.factories.widget_factory import WidgetFactory


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
        window=window,
        browser=browser,
        filter_bar=filter_bar,
        suffix_input=suffix_input,
        fs_service=services.create_file_system_service(),
        rename_service=services.create_rename_service(),
        renamer=services.create_suffix_renamer(),
        undo_manager=services.create_undo_manager(),
        type_filter=services.create_file_type_filter(),
    )

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

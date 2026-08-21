# Batch File Suffix Appender

A desktop GUI app to batch-add a suffix to file names, inserting it before the
extension (`report.pdf` + `_v2` → `report_v2.pdf`).

## Features

- Browse local folders or Windows network drives (UNC paths like `\\server\share`)
- Select multiple files with Ctrl/Shift-click
- Filter the file list by extension (e.g. `pdf, txt`)
- Apply a suffix to all selected files in one click
- Undo the last apply operation

## Requirements

- Python 3.10+
- PySide6

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python -m filesuffix.app
```

Or after installing the package (`pip install -e .`):

```bash
filesuffix
```

## Run tests

```bash
python -m pytest
```

## Project structure

```
src/filesuffix/
  app.py                  # entry point
  config.py               # constants
  models/                 # pure logic, no Qt
    file_entry.py
    file_type_filter.py
    rename_command.py
    suffix_renamer.py
    undo_manager.py
  services/               # filesystem I/O
    file_system_service.py
    rename_service.py
  views/                  # PySide6 widgets
    file_browser_view.py
    filter_bar_widget.py
    main_window.py
    suffix_input_widget.py
  controllers/
    app_controller.py     # wires views to services/models
  factories/
    widget_factory.py
    service_factory.py
tests/
```

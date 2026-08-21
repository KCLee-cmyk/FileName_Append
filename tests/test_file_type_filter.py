"""Tests for FileTypeFilter."""

from __future__ import annotations

import pytest

from filesuffix.models.file_entry import FileEntry
from filesuffix.models.file_type_filter import FileTypeFilter


def _entry(name: str) -> FileEntry:
    return FileEntry(path=f"/tmp/{name}", name=name, size_bytes=0)


class TestFileTypeFilter:
    def test_empty_filter_accepts_all(self) -> None:
        f = FileTypeFilter()
        assert f.accepts(_entry("report.pdf")) is True
        assert f.accepts(_entry("data.txt")) is True
        assert f.accepts(_entry("README")) is True

    def test_accepts_matching_extension(self) -> None:
        f = FileTypeFilter({".pdf"})
        assert f.accepts(_entry("report.pdf")) is True

    def test_rejects_non_matching_extension(self) -> None:
        f = FileTypeFilter({".pdf"})
        assert f.accepts(_entry("data.txt")) is False

    def test_case_insensitive_match(self) -> None:
        f = FileTypeFilter({".pdf"})
        assert f.accepts(_entry("REPORT.PDF")) is True

    def test_normalizes_extension_without_dot(self) -> None:
        f = FileTypeFilter({"pdf"})
        assert f.accepts(_entry("report.pdf")) is True

    def test_set_allowed_replaces_filter(self) -> None:
        f = FileTypeFilter({".pdf"})
        f.set_allowed({".txt"})
        assert f.accepts(_entry("data.txt")) is True
        assert f.accepts(_entry("report.pdf")) is False

    def test_set_allowed_empty_accepts_all(self) -> None:
        f = FileTypeFilter({".pdf"})
        f.set_allowed(set())
        assert f.accepts(_entry("data.txt")) is True

    def test_multiple_allowed_extensions(self) -> None:
        f = FileTypeFilter({".pdf", ".docx"})
        assert f.accepts(_entry("a.pdf")) is True
        assert f.accepts(_entry("b.docx")) is True
        assert f.accepts(_entry("c.txt")) is False

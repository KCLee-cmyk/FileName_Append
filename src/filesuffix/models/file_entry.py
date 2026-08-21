"""Immutable data descriptor for a single file in the browser."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class FileEntry:
    """A single file discovered in the browser.

    Attributes:
        path: Absolute path to the file (may be a UNC path).
        name: File name including extension (e.g. ``"report.pdf"``).
        size_bytes: File size in bytes.
    """

    path: str
    name: str
    size_bytes: int

    @property
    def extension(self) -> str:
        """Return the lowercase extension including the dot, or ``""``.

        Returns:
            The extension such as ``".pdf"``, or an empty string when the
            file has no extension.
        """
        return os.path.splitext(self.name)[1].lower()

    @classmethod
    def from_path(cls, path: str) -> FileEntry:
        """Build a ``FileEntry`` from a filesystem path.

        Args:
            path: Absolute path to an existing file.

        Returns:
            A populated ``FileEntry``.
        """
        return cls(
            path=path,
            name=os.path.basename(path),
            size_bytes=os.path.getsize(path),
        )

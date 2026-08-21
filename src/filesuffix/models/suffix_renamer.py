"""Pure logic for computing new file names with a suffix inserted."""

from __future__ import annotations

import os

from filesuffix.config import ILLEGAL_FILENAME_CHARS


class SuffixRenamer:
    """Computes new file names by inserting a suffix before the extension.

    This class performs no filesystem I/O; all methods are pure functions
    over strings.
    """

    def is_valid_suffix(self, suffix: str) -> bool:
        """Return ``True`` if the suffix is non-empty and filesystem-safe.

        Args:
            suffix: Candidate suffix text.

        Returns:
            ``True`` when the suffix contains no illegal characters and is not
            empty or whitespace-only; otherwise ``False``.
        """
        if not suffix or not suffix.strip():
            return False
        return not any(ch in ILLEGAL_FILENAME_CHARS for ch in suffix)

    def build_new_name(self, file_name: str, suffix: str) -> str:
        """Insert the suffix before the extension of a single file name.

        Args:
            file_name: Original name including extension, e.g. ``"report.pdf"``.
            suffix: Text to insert, e.g. ``"_v2"``.

        Returns:
            The new file name, e.g. ``"report_v2.pdf"``. Names without an
            extension get the suffix appended: ``"README"`` → ``"README_v2"``.
        """
        root, ext = os.path.splitext(file_name)
        if ext:
            return root + suffix + ext
        return file_name + suffix

    def build_new_path(self, path: str, suffix: str) -> str:
        """Compute the full new path for a file given a suffix.

        Args:
            path: Absolute original path.
            suffix: Text to insert before the extension.

        Returns:
            The absolute new path in the same directory.
        """
        directory = os.path.dirname(path)
        old_name = os.path.basename(path)
        new_name = self.build_new_name(old_name, suffix)

        if "/" in path and "\\" not in path:
            if not directory:
                return new_name
            return f"{directory.rstrip('/')}/{new_name}"

        if "\\" in path and "/" not in path:
            if not directory:
                return new_name
            return f"{directory.rstrip('\\')}\\{new_name}"

        return os.path.join(directory, new_name)

"""File-type filter that restricts visible entries by extension."""

from __future__ import annotations

from filesuffix.models.file_entry import FileEntry


class FileTypeFilter:
    """Filters files by extension.

    An empty allow-set means "allow all". Extensions are compared
    case-insensitively and normalized to include a leading dot.
    """

    def __init__(self, allowed_extensions: set[str] | None = None) -> None:
        """Initialize the filter.

        Args:
            allowed_extensions: Extensions to keep (e.g. ``{".pdf", ".txt"}``).
                ``None`` or empty means all files pass.
        """
        self._allowed: set[str] = self._normalize(allowed_extensions or set())

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_allowed(self, extensions: set[str]) -> None:
        """Replace the allowed extension set (normalized internally).

        Args:
            extensions: New set of extensions to allow. Pass an empty set to
                allow all file types.
        """
        self._allowed = self._normalize(extensions)

    def accepts(self, entry: FileEntry) -> bool:
        """Return ``True`` if the entry should be shown under the current filter.

        Args:
            entry: The file entry to evaluate.

        Returns:
            ``True`` when the allow-set is empty (all pass) or when the
            entry's extension is in the allow-set.
        """
        if not self._allowed:
            return True
        return entry.extension in self._allowed

    def allowed_extensions(self) -> set[str]:
        """Return the current normalized allow-set (empty = all).

        Returns:
            A copy of the internal allowed-extensions set.
        """
        return set(self._allowed)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize(extensions: set[str]) -> set[str]:
        """Normalize extensions to lowercase with a leading dot.

        Args:
            extensions: Raw extension strings such as ``{"pdf", ".TXT"}``.

        Returns:
            Normalized set such as ``{".pdf", ".txt"}``.
        """
        result: set[str] = set()
        for ext in extensions:
            ext = ext.strip().lower()
            if ext and not ext.startswith("."):
                ext = "." + ext
            if ext:
                result.add(ext)
        return result

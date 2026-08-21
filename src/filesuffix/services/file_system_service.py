"""Directory scanning and path reachability for the file browser."""

from __future__ import annotations

import os

from filesuffix.models.file_entry import FileEntry


class FileSystemService:
    """Reads directory contents and checks path reachability."""

    def list_files(self, directory: str) -> list[FileEntry]:
        """Return ``FileEntry`` objects for the files directly in a directory.

        Only regular files are returned; sub-directories are excluded.

        Args:
            directory: Absolute directory path (local, mapped drive, or UNC).

        Returns:
            One ``FileEntry`` per regular file, sorted by name.

        Raises:
            OSError: If the directory cannot be read (e.g. share offline or
                path does not exist).
        """
        entries: list[FileEntry] = []
        with os.scandir(directory) as it:
            for entry in it:
                if entry.is_file(follow_symlinks=False):
                    stat = entry.stat(follow_symlinks=False)
                    entries.append(
                        FileEntry(
                            path=entry.path,
                            name=entry.name,
                            size_bytes=stat.st_size,
                        )
                    )
        entries.sort(key=lambda e: e.name.lower())
        return entries

    def is_reachable(self, path: str) -> bool:
        """Return ``True`` if the path exists and is accessible.

        Args:
            path: Filesystem path to test (local or UNC).

        Returns:
            ``True`` when the path exists and can be stat-ed; ``False``
            otherwise (including network errors).
        """
        try:
            os.stat(path)
            return True
        except OSError:
            return False

"""Tests for RenameCommand and RenameBatch."""

from __future__ import annotations

from filesuffix.models.rename_command import RenameBatch, RenameCommand


class TestRenameCommand:
    def test_fields(self) -> None:
        cmd = RenameCommand(old_path="/a/old.txt", new_path="/a/old_v2.txt")
        assert cmd.old_path == "/a/old.txt"
        assert cmd.new_path == "/a/old_v2.txt"

    def test_immutable(self) -> None:
        cmd = RenameCommand(old_path="/a/old.txt", new_path="/a/old_v2.txt")
        try:
            cmd.old_path = "/changed"  # type: ignore[misc]
            assert False, "Should have raised"
        except (AttributeError, TypeError):
            pass


class TestRenameBatch:
    def test_default_empty(self) -> None:
        batch = RenameBatch()
        assert batch.commands == []

    def test_stores_commands(self) -> None:
        cmd = RenameCommand("/a/old.txt", "/a/old_v2.txt")
        batch = RenameBatch(commands=[cmd])
        assert len(batch.commands) == 1
        assert batch.commands[0] is cmd

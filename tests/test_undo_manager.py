"""Tests for UndoManager."""

from __future__ import annotations

import pytest

from filesuffix.config import MAX_UNDO_DEPTH
from filesuffix.models.rename_command import RenameBatch, RenameCommand
from filesuffix.models.undo_manager import UndoManager


def _batch(tag: str) -> RenameBatch:
    return RenameBatch(commands=[RenameCommand(f"/old_{tag}", f"/new_{tag}")])


class TestUndoManager:
    def test_initially_cannot_undo(self) -> None:
        mgr = UndoManager()
        assert mgr.can_undo() is False

    def test_can_undo_after_push(self) -> None:
        mgr = UndoManager()
        mgr.push(_batch("a"))
        assert mgr.can_undo() is True

    def test_pop_returns_last_pushed(self) -> None:
        mgr = UndoManager()
        b1 = _batch("1")
        b2 = _batch("2")
        mgr.push(b1)
        mgr.push(b2)
        assert mgr.pop() is b2
        assert mgr.pop() is b1

    def test_pop_empty_returns_none(self) -> None:
        mgr = UndoManager()
        assert mgr.pop() is None

    def test_clear_empties_stack(self) -> None:
        mgr = UndoManager()
        mgr.push(_batch("a"))
        mgr.push(_batch("b"))
        mgr.clear()
        assert mgr.can_undo() is False
        assert mgr.pop() is None

    def test_depth_cap_drops_oldest(self) -> None:
        mgr = UndoManager()
        batches = [_batch(str(i)) for i in range(MAX_UNDO_DEPTH + 1)]
        for b in batches:
            mgr.push(b)
        # oldest (index 0) should have been evicted; most recent is still there
        recovered = []
        while mgr.can_undo():
            recovered.append(mgr.pop())
        assert len(recovered) == MAX_UNDO_DEPTH
        # Most recent should be last pushed (LIFO order in recovered list)
        assert recovered[0] is batches[-1]

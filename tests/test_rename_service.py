"""Tests for RenameService."""

from __future__ import annotations

import os

import pytest

from filesuffix.services.rename_service import RenameError, RenameService


@pytest.fixture()
def service() -> RenameService:
    return RenameService()


class TestApply:
    def test_renames_files_on_disk(self, service: RenameService, tmp_path: pytest.TempPathFactory) -> None:
        old = tmp_path / "report.pdf"
        old.write_text("data")
        new = tmp_path / "report_v2.pdf"

        batch = service.apply([(str(old), str(new))])

        assert not old.exists()
        assert new.exists()
        assert len(batch.commands) == 1
        assert batch.commands[0].old_path == str(old)
        assert batch.commands[0].new_path == str(new)

    def test_skips_existing_target(self, service: RenameService, tmp_path: pytest.TempPathFactory) -> None:
        old = tmp_path / "report.pdf"
        old.write_text("data")
        collision = tmp_path / "report_v2.pdf"
        collision.write_text("already here")

        with pytest.raises(RenameError) as exc_info:
            service.apply([(str(old), str(collision))])

        err = exc_info.value
        assert "report_v2.pdf" in err.conflicts
        assert old.exists()          # original untouched
        assert collision.read_text() == "already here"  # not overwritten

    def test_returns_partial_batch_on_failure(self, service: RenameService, tmp_path: pytest.TempPathFactory) -> None:
        ok_old = tmp_path / "ok.pdf"
        ok_old.write_text("")
        ok_new = tmp_path / "ok_v2.pdf"

        bad_old = tmp_path / "missing.pdf"   # does not exist
        bad_new = tmp_path / "missing_v2.pdf"

        with pytest.raises(RenameError) as exc_info:
            service.apply([(str(ok_old), str(ok_new)), (str(bad_old), str(bad_new))])

        err = exc_info.value
        assert ok_new.exists()
        assert len(err.completed.commands) == 1


class TestRevert:
    def test_round_trip(self, service: RenameService, tmp_path: pytest.TempPathFactory) -> None:
        original = tmp_path / "report.pdf"
        original.write_text("content")
        renamed = tmp_path / "report_v2.pdf"

        batch = service.apply([(str(original), str(renamed))])
        service.revert(batch)

        assert original.exists()
        assert not renamed.exists()

    def test_revert_multiple_in_reverse_order(self, service: RenameService, tmp_path: pytest.TempPathFactory) -> None:
        files = []
        for i in range(3):
            f = tmp_path / f"file{i}.txt"
            f.write_text(str(i))
            files.append(f)

        planned = [(str(f), str(f.with_stem(f.stem + "_v2"))) for f in files]
        batch = service.apply(planned)
        service.revert(batch)

        for f in files:
            assert f.exists()

    def test_revert_skips_missing_target(self, service: RenameService, tmp_path: pytest.TempPathFactory) -> None:
        old = tmp_path / "report.pdf"
        old.write_text("")
        new = tmp_path / "report_v2.pdf"

        batch = service.apply([(str(old), str(new))])
        new.unlink()   # simulate the renamed file being deleted externally

        # Should not raise even though the file is gone
        service.revert(batch)

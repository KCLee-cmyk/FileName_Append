"""Tests for SuffixRenamer."""

from __future__ import annotations

import pytest

from filesuffix.models.suffix_renamer import SuffixRenamer


@pytest.fixture()
def renamer() -> SuffixRenamer:
    return SuffixRenamer()


class TestBuildNewName:
    def test_simple_extension(self, renamer: SuffixRenamer) -> None:
        assert renamer.build_new_name("report.pdf", "_v2") == "report_v2.pdf"

    def test_no_extension(self, renamer: SuffixRenamer) -> None:
        assert renamer.build_new_name("README", "_v2") == "README_v2"

    def test_last_extension_only(self, renamer: SuffixRenamer) -> None:
        assert renamer.build_new_name("data.tar.gz", "_v2") == "data.tar_v2.gz"

    def test_hidden_file_no_extension(self, renamer: SuffixRenamer) -> None:
        # ".bashrc" — os.path.splitext sees root=".bashrc", ext="" on Python
        assert renamer.build_new_name(".bashrc", "_bak") == ".bashrc_bak"

    def test_multiple_dots(self, renamer: SuffixRenamer) -> None:
        assert renamer.build_new_name("my.file.name.txt", "_copy") == "my.file.name_copy.txt"


class TestBuildNewPath:
    def test_preserves_directory(self, renamer: SuffixRenamer) -> None:
        result = renamer.build_new_path("/some/dir/report.pdf", "_v2")
        assert result == "/some/dir/report_v2.pdf"


class TestIsValidSuffix:
    def test_valid_suffix(self, renamer: SuffixRenamer) -> None:
        assert renamer.is_valid_suffix("_v2") is True

    def test_empty_suffix(self, renamer: SuffixRenamer) -> None:
        assert renamer.is_valid_suffix("") is False

    def test_whitespace_only(self, renamer: SuffixRenamer) -> None:
        assert renamer.is_valid_suffix("   ") is False

    @pytest.mark.parametrize("bad", ["a/b", "a\\b", "a:b", "a*b", "a?b",
                                      'a"b', "a<b", "a>b", "a|b"])
    def test_illegal_characters(self, renamer: SuffixRenamer, bad: str) -> None:
        assert renamer.is_valid_suffix(bad) is False

    def test_spaces_within_suffix_are_valid(self, renamer: SuffixRenamer) -> None:
        assert renamer.is_valid_suffix(" copy") is True

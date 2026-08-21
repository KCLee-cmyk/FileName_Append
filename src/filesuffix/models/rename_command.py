"""Command-pattern data classes for recording and reversing renames."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RenameCommand:
    """A reversible record of one file rename.

    Attributes:
        old_path: Absolute path before the rename.
        new_path: Absolute path after the rename.
    """

    old_path: str
    new_path: str


@dataclass
class RenameBatch:
    """A group of renames applied together, revertible as a unit.

    Attributes:
        commands: The individual ``RenameCommand`` records in apply order.
    """

    commands: list[RenameCommand] = field(default_factory=list)

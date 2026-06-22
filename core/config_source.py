"""ConfigSource abstraction — where the files to scan come from.

S5 ships the uploaded-files implementation only; the public-repo-URL source
arrives at S5b behind the same protocol.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol


class ConfigSource(Protocol):
    source_type: str

    def iter_files(self) -> Iterable[tuple[str, str]]:
        """Yield (filename, text content) pairs to scan."""
        ...


@dataclass
class UploadedFilesSource:
    """Files supplied directly by the caller (the always-works baseline)."""

    files: list[tuple[str, str]]
    source_type: str = "upload"

    def iter_files(self) -> Iterable[tuple[str, str]]:
        return list(self.files)

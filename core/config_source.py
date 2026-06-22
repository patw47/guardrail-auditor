"""ConfigSource abstraction — where the files to scan come from.

Two implementations behind one protocol: `UploadedFilesSource` (the always-works
baseline) and `RepoUrlSource` (a public-https repo, shallow read-only clone).
The repo source is SSRF-safe by construction: `validate_repo_url` runs BEFORE any
network call (https-only, exact-match host allowlist, no credentials), and the
temp clone dir is always cleaned up — even when the scan raises.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from urllib.parse import urlparse

ALLOWED_HOSTS = frozenset({"github.com", "gitlab.com"})
_SCAN_SUFFIXES = (".tf", ".yaml", ".yml", ".json", ".template")

Cloner = Callable[[str, Path], None]


class ConfigSourceError(ValueError):
    """Raised when a config source is invalid or unsafe (e.g. the SSRF guard)."""


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


def validate_repo_url(url: str, allowed_hosts: frozenset[str] = ALLOWED_HOSTS) -> str:
    """SSRF guard — runs BEFORE any network call. Returns the URL if safe, else raises.

    https-only · exact-match host allowlist (rejects IP literals, localhost, and
    suffix look-alikes like github.com.evil.com) · no credentials/userinfo.
    """
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ConfigSourceError(
            f"repo_url must use https (got {parsed.scheme or 'no scheme'!r})"
        )
    if parsed.username or parsed.password:
        raise ConfigSourceError("repo_url must not embed credentials (userinfo)")
    host = parsed.hostname or ""
    if host not in allowed_hosts:
        raise ConfigSourceError(
            f"host {host!r} is not allowlisted {sorted(allowed_hosts)}"
        )
    return url


def _git_clone(url: str, dest: Path) -> None:
    """Shallow, read-only clone. No tags, no submodules, no credential prompt; never apply."""
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    subprocess.run(
        ["git", "clone", "--depth", "1", "--no-tags", url, str(dest)],
        check=True,
        capture_output=True,
        env=env,
        timeout=120,
    )


@dataclass
class RepoUrlSource:
    """A public-https repo, shallow read-only clone. `cloner` is injectable so CI
    runs offline; production uses the hardened git clone."""

    repo_url: str
    allowed_hosts: frozenset[str] = ALLOWED_HOSTS
    cloner: Cloner | None = None
    source_type: str = "repo_url"

    def iter_files(self) -> Iterable[tuple[str, str]]:
        validate_repo_url(self.repo_url, self.allowed_hosts)  # before any clone
        clone = self.cloner or _git_clone
        tmp = Path(tempfile.mkdtemp(prefix="guardrail-clone-"))
        try:
            clone(self.repo_url, tmp)
            return list(self._walk(tmp))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)  # always, even on error

    def _walk(self, root: Path) -> Iterator[tuple[str, str]]:
        for path in sorted(root.rglob("*")):
            if ".git" in path.parts or not path.is_file():
                continue
            if path.name.lower().endswith(_SCAN_SUFFIXES):
                try:
                    yield path.relative_to(root).as_posix(), path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue

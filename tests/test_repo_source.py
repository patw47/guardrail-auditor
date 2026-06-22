"""S5b: RepoUrlSource — SSRF guard (before any clone), parity with upload,
and temp-dir cleanup even on error. All offline (injectable cloner)."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.config_source import (
    Cloner,
    ConfigSourceError,
    RepoUrlSource,
    UploadedFilesSource,
    validate_repo_url,
)
from core.pipeline import run_scan

MULTI = (Path(__file__).parent / "fixtures" / "detectors" / "multi_violation.tf").read_text()


def _cloner(files: dict[str, str]) -> Cloner:
    def clone(_url: str, dest: Path) -> None:
        for name, content in files.items():
            (dest / name).write_text(content)
    return clone


@pytest.mark.parametrize(
    "url",
    [
        "http://github.com/owner/repo",            # non-https
        "git://github.com/owner/repo",             # non-https scheme
        "ftp://github.com/owner/repo",
        "github.com/owner/repo",                   # no scheme
        "https://169.254.169.254/owner/repo",      # IP literal (metadata SSRF)
        "https://127.0.0.1/owner/repo",
        "https://localhost/owner/repo",
        "https://github.com.evil.com/owner/repo",  # suffix look-alike
        "https://user:pass@github.com/owner/repo", # embedded credentials
    ],
)
def test_ssrf_guard_rejects(url: str) -> None:
    with pytest.raises(ConfigSourceError):
        validate_repo_url(url)


def test_ssrf_guard_accepts_allowlisted_https() -> None:
    assert validate_repo_url("https://github.com/owner/repo") == "https://github.com/owner/repo"
    assert validate_repo_url("https://gitlab.com/owner/repo")


def test_repo_source_validates_before_cloning() -> None:
    cloned: list[str] = []

    def spy(url: str, _dest: Path) -> None:
        cloned.append(url)

    src = RepoUrlSource("https://169.254.169.254/x", cloner=spy)
    with pytest.raises(ConfigSourceError):
        list(src.iter_files())
    assert cloned == []  # never reached the clone


def test_parity_upload_vs_repo_identical_findings_and_score() -> None:
    upload = run_scan(UploadedFilesSource([("multi_violation.tf", MULTI)]))
    repo = run_scan(
        RepoUrlSource("https://github.com/o/r", cloner=_cloner({"multi_violation.tf": MULTI})),
        strict=False,
    )
    assert upload.score == repo.score
    key = lambda r: [  # noqa: E731
        (i.finding.rule_id, i.finding.file, i.finding.line, i.finding.severity) for i in r.items
    ]
    assert key(upload) == key(repo)


def test_temp_dir_cleaned_up_even_on_error() -> None:
    created: list[Path] = []

    def failing_clone(_url: str, dest: Path) -> None:
        created.append(dest)
        raise RuntimeError("clone failed")

    src = RepoUrlSource("https://github.com/o/r", cloner=failing_clone)
    with pytest.raises(RuntimeError):
        list(src.iter_files())
    assert created and not created[0].exists()  # cleanup ran in finally

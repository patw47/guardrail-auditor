"""S5b: repo-scan + rescan endpoints (offline via a patched cloner)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app

MULTI = (Path(__file__).parent / "fixtures" / "detectors" / "multi_violation.tf").read_text()


@pytest.fixture
def fake_clone(monkeypatch: pytest.MonkeyPatch) -> None:
    def clone(_url: str, dest: Path) -> None:
        (dest / "multi_violation.tf").write_text(MULTI)
    monkeypatch.setattr("core.config_source._git_clone", clone)


def test_repo_scan_then_rescan(fake_clone: None) -> None:
    with TestClient(app) as client:
        r = client.post("/api/scans/repo", json={"repo_url": "https://github.com/owner/repo"})
        assert r.status_code == 201
        body = r.json()
        assert body["source_type"] == "repo_url"
        assert body["score"]["value"] == 95
        assert body["score"]["grade"] == "F"
        scan_id = body["id"]
        # Rescan re-fetches the same source → a fresh scan
        again = client.post(f"/api/scans/{scan_id}/rescan")
        assert again.status_code == 201
        assert again.json()["source_type"] == "repo_url"
        assert again.json()["id"] != scan_id


def test_repo_scan_rejects_ssrf_urls() -> None:
    with TestClient(app) as client:
        for url in [
            "http://github.com/o/r",
            "https://169.254.169.254/o/r",
            "https://localhost/o/r",
            "https://github.com.evil.com/o/r",
            "https://user:pass@github.com/o/r",
        ]:
            resp = client.post("/api/scans/repo", json={"repo_url": url})
            assert resp.status_code == 400, url


def test_rescan_upload_source_is_409() -> None:
    with TestClient(app) as client:
        up = client.post(
            "/api/scans",
            files=[("files", ("multi_violation.tf", MULTI, "text/plain"))],
        )
        scan_id = up.json()["id"]
        resp = client.post(f"/api/scans/{scan_id}/rescan")
        assert resp.status_code == 409  # an upload is genuinely not re-fetchable

"""S5: REST API + persistence. POST→201, persisted-vs-pipeline round-trip,
404, determinism, OpenAPI completeness. DB is isolated (see conftest)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.config_source import UploadedFilesSource
from core.pipeline import run_scan
from core.repository import load_result, save_scan
from main import app

FIX = Path(__file__).parent / "fixtures" / "detectors"
_MULTI = FIX / "multi_violation.tf"


def _upload() -> list[tuple[str, tuple[str, str, str]]]:
    return [("files", ("multi_violation.tf", _MULTI.read_text(), "text/plain"))]


def test_post_scan_returns_201_with_score_and_findings() -> None:
    with TestClient(app) as client:
        resp = client.post("/api/scans", files=_upload())
        assert resp.status_code == 201
        body = resp.json()
        assert body["score"]["value"] == 95
        assert body["score"]["grade"] == "F"
        assert len(body["findings"]) == 4
        for finding in body["findings"]:
            assert finding["controls"], "each finding must carry named controls"
            assert finding["explanation"]
        scan_id = body["id"]
        assert client.get(f"/api/scans/{scan_id}").status_code == 200
        assert client.get(f"/api/scans/{scan_id}/findings").status_code == 200
        assert client.get(f"/api/scans/{scan_id}/score").json()["value"] == 95


def test_round_trip_persisted_equals_pipeline(session: Session) -> None:
    result = run_scan(UploadedFilesSource([("multi_violation.tf", _MULTI.read_text())]))
    scan_id = save_scan(session, result)
    loaded = load_result(session, scan_id)
    # persisted-vs-pipeline-output (not persisted-vs-itself): a mangled save/load fails here.
    assert loaded == result


def test_unknown_scan_returns_404() -> None:
    with TestClient(app) as client:
        assert client.get("/api/scans/does-not-exist").status_code == 404


def test_same_upload_is_deterministic() -> None:
    src = UploadedFilesSource([("x.tf", _MULTI.read_text())])
    assert run_scan(src) == run_scan(src)


def test_openapi_documents_every_endpoint() -> None:
    with TestClient(app) as client:
        paths = client.get("/openapi.json").json()["paths"]
        assert "post" in paths["/api/scans"]
        assert "get" in paths["/api/scans"]
        assert "/api/scans/{scan_id}" in paths
        assert "/api/scans/{scan_id}/findings" in paths
        assert "/api/scans/{scan_id}/score" in paths

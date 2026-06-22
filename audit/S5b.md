# S5b Verification — public-repo-URL ConfigSource + Rescan

Verifier: isolated, read-only. No network calls, no clone performed. Only file written: `audit/S5b.md`.
Date: 2026-06-22. Branch: `main` (working tree, uncommitted S5b surface).

## L1 gate (real output)

| tool | command | result | exit |
|---|---|---|---|
| ruff | `./.venv/bin/ruff check .` | `All checks passed!` | 0 |
| mypy | `./.venv/bin/mypy .` | `Success: no issues found in 39 source files` | 0 |
| pytest | `./.venv/bin/pytest -q` | `76 passed, 1 warning in 1.96s` | 0 |

Targeted re-run (17 tests): `test_dashboard.py::test_error_state_malformed_returns_400` + all of `test_repo_source.py` + `test_repo_api.py` → **17 passed**, exit 0.

## Criteria

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | L1 ruff/mypy/pytest green | PASS | see table above (all exit 0) |
| 2 | SSRF guard `validate_repo_url`: rejects non-https / IP literals / localhost / suffix look-alike / userinfo; accepts exact-match https allowlist; `ALLOWED_HOSTS == {github.com, gitlab.com}` | PASS | `core/config_source.py:22` `ALLOWED_HOSTS = frozenset({"github.com","gitlab.com"})`; `:51-69` https-only (`:58`), userinfo reject (`:62-63`), `parsed.hostname` exact-match against allowlist (`:64-68` → rejects IP literals/localhost/`github.com.evil.com` since none are in the set). Parametrized test asserts each of the 9 bad URLs raises: `tests/test_repo_source.py:29-45`; accept test `:48-50` |
| 3 | Guard runs BEFORE any clone; spy cloner never called for bad URL | PASS | `core/config_source.py:94-96` — `iter_files` calls `validate_repo_url(...)` on line 95 BEFORE `clone = self.cloner or _git_clone` (96) and the `clone(...)` call (99). Test `test_repo_source_validates_before_cloning` (`:53-62`) injects a spy and asserts `cloned == []` after a bad URL raises |
| 4 | Cleanup-on-error: temp dir removed even when clone/scan raises (try/finally + shutil.rmtree) | PASS | `core/config_source.py:97-102` — `tmp = mkdtemp(...)`; `try: clone(...); return list(self._walk(tmp))` `finally: shutil.rmtree(tmp, ignore_errors=True)`. Test `test_temp_dir_cleaned_up_even_on_error` (`:78-88`) uses a raising cloner and asserts `created and not created[0].exists()` |
| 5 | Parity: UploadedFilesSource vs RepoUrlSource (offline cloner) → identical findings AND score | PASS | `test_parity_upload_vs_repo_identical_findings_and_score` (`tests/test_repo_source.py:65-75`): asserts `upload.score == repo.score` AND compares the full per-item tuple list `(rule_id,file,line,severity)` for every finding. Same fixture `multi_violation.tf` fed to both sources |
| 6 | API: POST /api/scans/repo → 201 source_type=repo_url; SSRF → 400; rescan repo → 201 (new id); rescan upload → 409 | PASS | `api/routes.py:181-183` (`/scans/repo` 201 ScanDetail), `:160-178` validate→400 (`:163-165`), `:186-193` rescan (404 if missing, 409 if `source_type != "repo_url" or not source_ref`, else 201 new scan). Tests `tests/test_repo_api.py`: `:22-35` (201 + `source_type=="repo_url"` + new id on rescan), `:38-48` (5 SSRF urls → 400), `:51-59` (upload rescan → 409) |
| 7 | Clone hardening: `--depth 1 --no-tags`, GIT_TERMINAL_PROMPT=0, no submodules, no credentials, never apply | PASS | `core/config_source.py:72-81`: `env={**os.environ,"GIT_TERMINAL_PROMPT":"0"}`; `["git","clone","--depth","1","--no-tags",url,str(dest)]`; no `--recurse-submodules` (git default = submodules NOT fetched); no credential helper / no userinfo (guard strips); no `git apply` anywhere |

## Constraints

| id | Constraint | Verdict | Evidence |
|---|---|---|---|
| C1 | No new runtime dependency | PASS | `git diff HEAD -- pyproject.toml` empty. `[project.dependencies]` = fastapi, uvicorn, sqlalchemy, pydantic, python-hcl2, pyyaml, python-multipart (unchanged). git is a system tool, not a pip dep |
| C2 | Schema change minimal: only a NULLABLE `source_ref` on ScanRow | PASS | `git diff HEAD -- core/tables.py` = `+2 -0`: only `source_ref: Mapped[str \| None] = mapped_column(nullable=True, default=None)` (`core/tables.py:25`). No other table/column touched. `save_scan(... source_ref=None)` defaults NULL for uploads (`core/repository.py:20,27`), repo_url passed for repo scans (`api/routes.py:174`) |
| C3 | Upload path preserved: `run_scan` gained `strict` (default True); malformed UPLOAD still 400; strict=False only on repo endpoints | PASS | `core/pipeline.py:40` `def run_scan(source, strict=True)`; strict raises ParseError (`:54-56`). Upload endpoint calls `run_scan(UploadedFilesSource(...))` with default strict=True (`api/routes.py:121`) → ParseError→400 (`:122-123`). Repo path uses `strict=False` (`:167`). `test_error_state_malformed_returns_400` PASSES (`tests/test_dashboard.py:92-96`) |
| C4 | Pipeline detection/scoring/compliance unchanged | PASS | `git diff --stat HEAD -- rules/ core/scoring.py core/compliance.py core/parsing/ models/` = EMPTY. pipeline.py changed only for the strict param (`+14 -4`, diff confirms: import ParseError + strict param + try/except, plus a `not ... endswith → continue` refactor of the same supported-suffix filter, no detection logic change). S5b surface = config_source/tables/repository/api/pipeline/web/tests only |
| C5 | CI offline: injectable/patched cloner, no real clone/network | PASS | `RepoUrlSource.cloner` injectable (`core/config_source.py:91`). Tests inject a closure cloner (`tests/test_repo_source.py:22-26`) and monkeypatch `core.config_source._git_clone` (`tests/test_repo_api.py:16-19`). grep of `tests/` for subprocess/socket/requests/httpx/urlopen → only the monkeypatch line; no real clone or network in any test |
| D1 | Dashboard consumes /api only; Rescan shown only when source_type==repo_url; no business logic | PASS | `web/static/app.js`: `/api/scans/repo` (`:19`), `/api/scans/{id}/rescan` (`:27`), gate `$("rescan").hidden = data.source_type !== "repo_url"` (`:58`), rescan no-ops unless repo_url (`:26`). Header comment "No business logic here" (`:2-3`); severity/score/controls all from API. `web/index.html`: repo-url input (`:22-23`), scan-repo button (`:24`), rescan button hidden by default (`:41`) |

## Tampering hunt

- No `skip` / `xfail` / `xpass` / `assert True` / `return True` in `tests/test_repo_source.py` or `tests/test_repo_api.py`. The only `pytest.mark` is the legitimate `@pytest.mark.parametrize` driving the 9 SSRF cases (`tests/test_repo_source.py:29`).
- SSRF test asserts each bad URL raises `ConfigSourceError` (parametrized, 9 cases, all observed PASSING individually).
- Cleanup test asserts the dir is actually gone: `not created[0].exists()`.
- Parity test compares the FULL per-finding structure tuple list AND the score, not a count.
- `dangerous`/weakened assertions: none found.

## VERDICT: PASS

All 7 criteria pass. SSRF guard runs before any clone (line 95 before 96/99, proven by spy test). Cleanup-on-error holds (try/finally + rmtree, proven by raising-clone test). Parity is exact (findings tuples + score). Schema change is the single approved nullable `source_ref` column. No new runtime dependency. CI is offline (injectable/patched cloner; no real clone or network in tests). Constraints C1–C5 + D1 all hold; no tampering detected.

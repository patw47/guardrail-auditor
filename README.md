# Guardrail Auditor

**Static, API-first IaC compliance auditor.** It reads Terraform / CloudFormation
files, flags high-risk patterns, maps each finding to a named compliance control
(CIS / SOC 2 / ISO 27001 / GDPR), aggregates a **0–100 Risk Score**, and shows it
on a dashboard — **shift-left compliance**, caught in the pull request, not in
production.

- **No cloud, no `apply`, no API key.** Pure static analysis; the scoring/audit
  path is deterministic. (Any LLM is fenced out of the trust path — roadmap.)
- **Two inputs, one abstraction:** upload files, or paste a public repo URL
  (shallow read-only clone, https-only, host-allowlisted).

![Dashboard](docs/screenshots/dashboard.png)

## Quickstart (clone → working scan)

```bash
git clone https://github.com/patw47/guardrail-auditor.git
cd guardrail-auditor
python3 -m venv .venv && ./.venv/bin/pip install -e ".[dev]"
./.venv/bin/uvicorn main:app          # serves the API + dashboard on :8000
```

Open <http://127.0.0.1:8000/> and either:

- **Upload** the bundled vulnerable fixtures `tests/fixtures/detectors/*.tf`
  (e.g. `multi_violation.tf` → **95/100, grade F**), or
- **Paste a public repo URL** — `https://github.com/bridgecrewio/terragoat`
  → **3 findings, 80/F** (real clone, proven end-to-end).

Run the test suite and the L1 gate:

```bash
./.venv/bin/ruff check .
./.venv/bin/mypy .
./.venv/bin/pytest -q
```

Seed a demo scan so the dashboard shows data immediately (idempotent, offline):

```bash
./.venv/bin/python tools/demo_seed.py
```

## API

OpenAPI / Swagger at `/docs`, schema at `/openapi.json`.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/scans` | scan uploaded files (multipart) → 201 |
| POST | `/api/scans/repo` | scan a public repo URL → 201 |
| GET  | `/api/scans` | list scans |
| GET  | `/api/scans/{id}` | scan detail (score + findings + controls + remediation) |
| GET  | `/api/scans/{id}/findings` | findings |
| GET  | `/api/scans/{id}/score` | the Risk Score |
| POST | `/api/scans/{id}/rescan` | re-fetch a repo-sourced scan (upload → 409) |

## Detectors → compliance

| rule | severity | named controls |
|------|----------|----------------|
| `OPEN_SSH` | critical | CIS AWS v3.0.0 §5.2 · SOC 2 CC6.1 · ISO 27001:2022 A.8.20 |
| `S3_PUBLIC_BUCKET` | high | CIS §2.1.4 · SOC 2 CC6.1 · ISO A.5.15 · GDPR Art. 32 |
| `UNENCRYPTED_STORAGE` | high | CIS §2.2.1 · ISO A.8.24 · GDPR Art. 32 |
| `PUBLIC_DB` | high | ISO A.8.20 · CIS §2.3 (section) |

Severities are anchored to a citable source (AVD / CIS), verified against the
pinned benchmark — see `memory/decisions.md`. Each finding carries a plain-language
explanation **and** a remediation (corrected snippet / CLI action) that closes the
same control it cites.

## Assurance

Two distinct evidence streams:

- **Coverage matrix** (`docs/coverage_matrix.md`) — every detector fires on its
  true-positive and stays silent on a safe look-alike (incl. the hard
  wildcard-Principal + `Condition` false-positive), generated from real
  `pytest --junitxml` output.
- **External oracle** — Checkov 3.2.334 × TerraGoat (pinned), **K→K agreement
  3/3** on the implemented subset TerraGoat exercises. *"Checkov validates; the
  copilot differentiates."* See `tests/oracle/SOURCES.md`.

## Architecture

Layered: `api/` (REST) · `core/` (parsing, scoring, compliance, persistence) ·
`rules/` (detectors) · `models/` (domain types). SQLite via SQLAlchemy. The audit
path is deterministic; the dashboard is a client of the same documented API.

## Limitations & roadmap

See [`LIMITATIONS.md`](LIMITATIONS.md): scope vs. Checkov's breadth, the CIS RDS
section-level cite, deferred `.tf.json`, more allowlist hosts, and fenced LLM
narration (never in the trust path).

## License

Apache-2.0 — see [`LICENSE`](LICENSE).

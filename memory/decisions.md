# decisions.md — design forks later sprints must honor

_(SCRIBE; re-read at sprint start. Write only what a later sprint needs.)_

## S0
- **Layered source tree** (`api/ core/ rules/ models/`) over a single `app/`.
  Each is a tracked package via `__init__.py`. Fills: models@S1, rules@S2,
  core scoring@S3, api + core pipeline@S5.
- **pyproject.toml is the single dependency source of truth** — no
  `requirements.txt`. Install/CI: `pip install -e ".[dev]"`.
- **core/ is the data layer; `core/db.py` is the thin SQLite layer**
  (`engine` / `SessionLocal` / `Base(DeclarativeBase)` / `init_db()`). NO domain
  tables yet — the concrete schema (Scan/Finding/Score/Control) is the **S5
  sensitive gate**; tables register on `Base` there.
- **Governance files at repo root**, byte-for-byte as approved (CLAUDE.md must be
  root to auto-load).
- **DB path** `./guardrail.db` (gitignored). `init_db()` is a no-op create until
  tables register at S5.
- **Thin app entry** `main.py` creates the FastAPI app + `/health`; domain
  routers accrete under `api/` and are included here at S5.

## S1
- **Parsers live in `core/parsing/`** (ingest = front of the pipeline, in the
  core data layer). Public API: `parse_file(path)`, `parse_content(content,
  filename)`, `ParseError`. Dispatch by extension: `.tf`→Terraform;
  `.yaml/.yml/.json/.template`→CloudFormation.
- **`Resource`** (`models/resource.py`) is the single normalized type both
  formats converge on: `format`, `type` (native string), `name`/logical-id,
  `attributes` (dict), `file`, `line`.
- **hcl2 v8 reality** (probed before coding): blocks are ALWAYS lists tagged
  `__is_block__` (marker stripped by the mapper) — so a nested block is always a
  list, len 1 for a single occurrence; scalar strings are quote-wrapped (mapper
  unquotes). `with_meta` is gone in v8 → **TF line numbers come from a
  comment-stripped header line-scan** (`_header_lines`), provably robust to
  leading comments.
- **CFN**: a `yaml.SafeLoader` subclass + `add_multi_constructor("!", …)` turns
  intrinsic tags into marker dicts (`!Ref X`→`{"Ref":"X"}`, `!Foo`→`{"Fn::Foo":…}`);
  per-resource line from the `yaml.compose` node tree; JSON rides the same path.
- **`.tf.json` deferred** (TF-first = HCL); `.json` currently routes to CFN.
- **For S2 detectors**: read normalized resources. TF security-group ingress is
  at `attributes["ingress"]` (list of dicts, `cidr_blocks` list of unquoted
  strings); CFN is `attributes["SecurityGroupIngress"]` (list) with `CidrIp`.
  Public-bucket signals differ too (TF `acl`/policy vs CFN `AccessControl`).
  Detectors must map BOTH native shapes onto each rule.

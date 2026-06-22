# Prompts Audit Log — Guardrail Auditor

Architect prompts logged **verbatim**, every turn (SCRIBE duty).

---

## Prompt #0 — T0 (2026-06-22)

> Lead Architect mode: ON. We are building a Python-based, API-first
> Enterprise Security Guardrail Auditor using a free database and a
> dashboard.
> Rules:
> - No Manual Edits: You provide all logic and fixes. I will not edit any code.
> - Audit Log: You must maintain a file named prompts.md. After every turn,
>   update that file (or provide the text block) with the prompt I just used.
> - Time-Check: Start a timer. Goal is an MVP in 4-6 hours (Max window: 16h).
>   Report 'Elapsed Time' at the end of every response. Acknowledge and let's start.

---

## Prompt #1 — T0 (2026-06-22) — PROJECT BRIEF (supersedes #0 scope)

> PROJECT BRIEF (verbatim):
> "Project 2: Enterprise Security Guardrail Auditor. Focus: Compliance. Create a
> scanner that audits infrastructure configuration files (Terraform/CloudFormation)
> against a security baseline. It must flag high-risk patterns - such as public S3
> buckets or open SSH ports - and present a visual 'Risk Score' dashboard."
>
> You are the engineer on this build, and the only tool used end-to-end.
> I am the architect: I own the design and the direction and approve at the
> gates; you plan and build under it. I never edit code by hand - you write
> all code and all tests, and you fix the bugs I describe. The value here is
> the quality of my gates, not the number of prompts.
>
> You work as ONE agent that switches between five named hats. State the hat
> you are wearing each turn:
> - PLANNER - break the work into bounded sprints; define each sprint's
>   acceptance criteria before any code.
> - BUILDER - implement exactly one sprint and write its tests, including the
>   adversarial pair: a test proving each check catches a real violation, and
>   one proving it ignores a safe look-alike.
> - VERIFIER - an independent, read-only review (a separate subagent) that
>   audits the delivered work against the sprint's criteria and reports gaps.
>   It never edits.
> - SCRIBE - keep the working memory and the prompt log up to date.
> - REPORTER - capture the few moments worth a slide.
>
> THE LOOP - one bounded sprint per exchange:
> 1. PLANNER explores the relevant existing code first, states the current
>    flow, then proposes the sprint - Goal, Context, Constraints, Done-when
>    (the validation commands + expected result). STOP for my approval.
> 2. BUILDER implements it and writes the tests. Run lint, type-check, tests.
> 3. VERIFIER audits and writes its report; SCRIBE updates memory + prompt
>    log; REPORTER logs a highlight only if one occurred.
> 4. STOP, present the evidence, and wait for my approval. Only after I
>    approve do you commit.
> Work autonomously inside a sprint; never chain sprints; always stop at the
> two gates. Also stop and ask before anything sensitive (secrets, auth,
> destructive or external operations).
>
> NON-NEGOTIABLES:
> - One tool end-to-end (you). Switching model is fine; switching tool is not.
> - prompts.md: log my prompts verbatim, every turn.
> - Time: aim for a 4-6h MVP (hard max 16h). Report Elapsed Time at the end
>   of every reply (active build time, excluding my review time).
> - Git: trunk-based on https://github.com/patw47/guardrail-auditor; one
>   commit per sprint, pushed only after I approve.
> - Bounded context: at each sprint start, re-read only the relevant memory
>   and the sprint plan; don't carry the whole history.
>
> THE TARGET: a STATIC analysis tool - it reads Terraform/CloudFormation files
> (no live cloud, no apply), flags the high-risk patterns, explains each
> finding and maps it to a named compliance control (CIS / SOC 2 / ISO 27001 /
> GDPR), and aggregates a 0-100 Risk Score shown on a dashboard. Python,
> API-first (documented REST), SQLite. The core must be deterministic and run
> with no API key.
> Input is chosen per request behind one ConfigSource abstraction: uploaded
> files (the always-works baseline) or a public repo URL it shallow-clones
> read-only, restricted to an exact-match host allowlist (https only). No
> private-repo tokens in this build.
> Build only this tool.
>
> Acknowledge, and confirm you will hold at the gates. Then WAIT: your first
> job is to draft the governance files (vision, method, rules) for my
> approval; the sprint plan comes after. Do not propose the sprint plan yet.

---

## Prompt #2 — T0 (2026-06-22) — Gate A1: VISION redo

> [PLANNER] Hold - you ran ahead of the gate. The contract said your first job
> is to draft the governance files for my approval; starting with the vision is
> the right instinct, but we do this in THREE gated steps - A1 vision, A2
> method, A3 the rule files - and I approve each before the next. So don't
> touch PROTOCOL.md / ADAPTER.md / CLAUDE.md / verifier.md yet. Redo VISION.md
> ONLY, to this spec, then STOP for my approval.
>
> Foundations 1/3 - VISION.md only. Text in your reply; no tree, no code, no
> scaffold.
>
> VISION.md - strategic intent, one page, evaluator-facing:
> - WHAT this tool is and WHY it matters: a compliance-focused auditor that
>   turns infrastructure configuration into an auditable, control-mapped Risk
>   Score, caught pre-deployment ("shift-left compliance").
> - Guiding principles for HOW it is built. These are mandatory and your
>   current draft is missing three of them:
>   1. A deterministic trust path: the scoring/audit path is deterministic and
>      runs with no API key. An LLM is kept as an OPTIONAL accelerant
>      (narration only), never the authority, fenced out of the audit path and
>      never able to introduce or change a finding. Do NOT frame this as "no
>      AI" - frame it as the AI being deliberately fenced out of the trust
>      path.
>   2. Every detector is proven by adversarial evidence: it catches its real
>      violation AND ignores a safe look-alike; nothing ships without that
>      evidence.
>   3. The build method (how findings are detected, proven, and mapped) is
>      designed to generalize to other infrastructure-governance domains
>      beyond this single tool.
>   Keep your other good principles too (explain don't just flag, safe by
>   construction, API-first).
>
> Objective + principles ONLY - no method mechanics (the 5 roles, gates and
> sprints belong in PROTOCOL.md), no sprint detail, no invented facts or client
> names. Your §1-6 (one-liner, problem, who it serves, in/out of scope, MVP
> success criteria) are good - keep them. Fix the §5 non-goal line
> `No non-LLM "AI" scoring` so it matches principle 1.
>
> Present VISION.md and STOP at the gate.

---

## Prompt #3 — T0 (2026-06-22) — Gate A1 reject: fix §6

> [GATE A1 REJECT - VISION.md] The principles are right - 1 (AI fenced from the
> trust path; "removing the LLM changes wording, never verdicts"), 2
> (adversarial evidence), 3 (method generalizes) all land. §1-5 and §7 are
> approved as written. One real defect, in §6: criterion 2 got mangled in the
> edit - it's now an orphan line ("does not flag safe look-alikes") hanging
> under criterion 1, and the list skips from 1 to 3. Restore criterion 2 as one
> complete item: "Catches the named high-risk patterns (public S3, open SSH) in
> real fixtures, AND does not flag safe look-alikes." Renumber 1-6 cleanly.
> Change nothing else. Resubmit §6.

---

## Prompt #4 — T0 (2026-06-22) — Gate A1 OK; A2 PROTOCOL.md

> [GATE A1 OK] VISION.md approved in full. Proceed to A2. [PLANNER] Foundations
> 2/3 - PROTOCOL.md only, for my approval. Text in your reply; no tree, no code.
>
> PROTOCOL.md - the orchestration method, written PROJECT-AGNOSTIC: no
> security / IaC / S3 / SSH / Terraform / bucket wording anywhere, so the same
> method could drive a different infrastructure-governance module unchanged.
> It must contain these sections:
>
> a. THE FIVE HATS - one agent, explicit hats, full definitions:
>    - PLANNER: decomposes into bounded sprints with dependencies; defines
>      acceptance criteria before any code; maintains the sprint plan.
>    - BUILDER: implements exactly one sprint and writes ALL its tests -
>      including the discrimination pair per detector (a true-positive that
>      MUST fire + a near-miss false-positive that must NOT) and the
>      behavioral tests a UI sprint needs. While editing: keep the diff
>      minimal, touch only what the sprint needs, add no dependency without
>      explicit justification, preserve public API contracts unless the
>      sprint changes them. The tests run in CI and ARE the automated
>      assurance.
>    - VERIFIER: an INDEPENDENT read-only review in an isolated context
>      (separate subagent; Read/Grep/Bash only, never Write/Edit). It (1)
>      confirms clean execution (lint/type/tests green, the app runs), (2)
>      audits the delivered work against the sprint's prompt + criteria and
>      flags every gap - unmet criterion, scope creep, a required test
>      missing, or any silenced error / fabricated result - with file/line
>      refs, (3) returns a structured report (per-criterion PASS/FAIL +
>      gaps). Never writes code or tests. Frame its value as context
>      isolation that reduces self-justification, NOT model independence.
>    - SCRIBE: maintains the working memory a future bounded sprint must
>      re-read. decisions.md (a design fork + tradeoff, a convention later
>      sprints must follow, a scope/criteria change at a gate, a deferral to
>      roadmap). lessons.md (a bug's root cause + fix, a check that caught
>      something, a corrected false assumption). Writes ONLY what a later
>      sprint needs; at each sprint end states the new entries OR "no decision
>      / no lesson this sprint". Keeps prompts.md updated mechanically.
>    - REPORTER: logs a highlight ONLY on one of these triggers (name it in
>      the entry): CATCH, DISCRIMINATION, GATE, DECISION, GENERALITY, MAPPING,
>      METRIC. Skip routine work; at each sprint end state the highlight(s) +
>      trigger OR "no highlight this sprint".
>
> b. VALIDATION LADDER (every sprint) - tests written by the BUILDER, run in
>    CI; the VERIFIER confirms they exist, pass, and match the prompt:
>    - L1 deterministic: lint + type-check + tests green on every push.
>    - L2 conformance: VERIFIER audits delivered-vs-prompt; flags unmet
>      criteria, scope creep, or a missing required test (file/line).
>    - L3 adversarial: per detector, a true-positive + a near-miss
>      false-positive test; for a UI sprint, integration tests. Versioned and
>      CI-run, regression-proof.
>
> c. THE GATES - autonomous inside a sprint; STOP at three types: (1) once,
>    after proposing the sprint plan; (2) per sprint, TWICE - (a) at start,
>    after proposing approach + acceptance criteria, before any code, and (b)
>    after the VERIFIER evidence, before the next sprint; (3) on any sensitive
>    decision (secrets, auth, permissions, database schema, deployment config,
>    destructive/external ops). Never chain sprints.
>
> d. SPRINT CLOSE SEQUENCE (in order, before the evidence gate): VERIFIER
>    audits -> report persisted to the audit file; SCRIBE updates memory;
>    REPORTER updates highlights; prompts.md updated. Then STOP ("holding
>    commit until you approve") and present the evidence. Commit (trunk-based,
>    one per sprint) only after I approve.
>
> e. THE TRACKED FILES - everything recorded is NOT everything re-injected:
>    write to files so we don't drag the whole history into one thread,
>    re-inject only the relevant slice at sprint start.
>    - prompts.md: my verbatim prompts (deliverable).
>    - memory/decisions.md + lessons.md: SCRIBE; re-read by later sprints.
>    - audit/<sprint>.md: the VERIFIER report; correction hand-off + evidence.
>    - highlights.md: REPORTER; deck material; write-only, never re-injected.
>
> f. THE SPRINT TICKET SHAPE - the PLANNER proposes every sprint as Goal
>    (what it must achieve) / Context (existing files + current behavior it
>    builds on) / Constraints (what must NOT be broken, changed, or added) /
>    Done-when (validation commands that must pass, real output pasted, AND
>    the acceptance criteria met; never "looks done").
>
> g. EXPLORE BEFORE CODE - for any sprint touching existing code, explore the
>    relevant files and state the current flow FIRST, then propose the
>    approach; no code before it is gate-approved. Greenfield goes straight to
>    the proposal.
>
> h. EVIDENCE (the gate's teeth) - no success claimed without evidence. The
>    agent NEVER: invents a file, command, or test result; suppresses an error
>    to go green (no blanket ignore/skip/except-pass added, no assertion bent
>    to match wrong output, no threshold lowered, no failing test deleted); or
>    marks work done without the validation commands actually run and their
>    real output shown. Gate evidence = commands run + their true output; the
>    VERIFIER flags any silenced error or fabricated result as a FAIL.
>
> Present PROTOCOL.md and STOP at the gate.

---

## Prompt #5 — T0 (2026-06-22) — Gate A2: fix section f header

> [GATE A2] Substance approved - five hats, L1/L2/L3, the three gate types
> (type 2 twice), close sequence, tracked files, explore-before-code, evidence,
> all project-agnostic. One structural fix before I lock it: section f has no
> header. The ticket-shape block (Goal / Context / Constraints / Done-when) sits
> under "## e. The Tracked Files", where it doesn't belong - it's not a tracked
> file - and the headers run e -> g. Give it its own header
> "## f. The Sprint Ticket Shape" as its own section between e and g. Nothing
> else changes. Resubmit the e/f area.

---

## Prompt #6 — T0 (2026-06-22) — Gate A2 OK; A3 thin files

> [GATE A2 OK] Section f now stands on its own between e and g; ticket-shape is
> out of Tracked Files. PROTOCOL.md approved in full. A2 is locked. Proceed to
> A3. [PLANNER] Foundations 3/3 - the three thin files, for my approval. Text in
> your reply; no tree, no code.
>
> ADAPTER.md - EXACTLY the 2 module-specific clauses, nothing else (no method
> content): (1) the domain layer in its universal shape - finding -> a named
> compliance control (CIS / SOC 2 / ISO 27001 / GDPR) with a reference URL ->
> a Risk Score; explanation by a DETERMINISTIC template, any LLM narration
> optional and fenced (may reference only a control already in the mapping,
> can never introduce a control or change a verdict, falls back to the
> template if absent). (2) the L3 false-positive trap: a public-via-policy
> bucket MUST flag; a private bucket with versioning enabled MUST NOT.
>
> CLAUDE.md - lean, auto-loaded standing rules. POINTS to PROTOCOL.md for the
> method (no duplication); always-on rules only: single tool = you,
> end-to-end; the per-sprint loop in one line; explore before editing; keep
> the diff minimal; no success claimed without evidence (commands + real
> output), never silence an error to go green; trunk-based, one commit per
> sprint after my gate; update prompts.md/memory/highlights each sprint; the
> model-routing line (switching model fine, switching tool not); the
> test/lint/type-check commands. Keep it SHORT - it loads every turn.
>
> .claude/agents/verifier.md - the VERIFIER subagent config: tools
> Read/Grep/Bash ONLY, NO Write/Edit; returns the structured report
> (per-criterion PASS/FAIL + gaps with file/line refs, including any silenced
> error or fabricated result) and never edits code or tests.
>
> Present all three and STOP at the gate.

---

## Prompt #7 — T0 (2026-06-22) — Gate A3: pin verifier model

> [GATE A3] ADAPTER.md (exactly the 2 module clauses, no method leak), CLAUDE.md
> (lean, points to PROTOCOL.md, commands present), and verifier.md (Read/Grep/
> Bash only, audits delivered-vs-prompt, hunts evidence tampering, per-criterion
> PASS/FAIL) are all good. One change to verifier.md before I lock it: pin its
> model. You dropped the pin and justified it with the independence point, but
> those are two separate things. Pinning is about AUDIT QUALITY - the strongest
> reasoner does the audit regardless of which model built the code - and is
> fully compatible with "independence = context isolation, not model
> difference". Add `model: opus` to the verifier.md frontmatter, and change the
> parenthetical from "model intentionally not pinned" to: "Model pinned to the
> strongest reasoner for audit quality; independence still comes from context
> isolation, not from running a different model than the build." Resubmit
> verifier.md only.
>
> Also - do NOT write any files to disk yet. Governance is approved in context;
> the files are written at S0 (the scaffold sprint), as the S0 prompt specifies,
> not now. Once the verifier.md pin is in, the next step is Gate 1: propose the
> full SPRINTS.md decomposition (Prompt B) - no code - and STOP.

---

## Prompt #8 — T0 (2026-06-22) — Gate A3 OK (governance LOCKED); Gate 1: SPRINTS.md

> [GATE A3 OK] verifier.md pinned to opus, Read/Grep/Bash only. All five
> governance files approved in context (VISION, PROTOCOL, ADAPTER, CLAUDE,
> verifier) - LOCKED. At S0 you write each to disk exactly as approved; do not
> redraft. Nothing on disk until S0.
>
> [PLANNER] Plan step. With the governance files approved, now propose the
> initial SPRINTS.md decomposition for my approval, aimed at the GLOBAL
> DELIVERABLE - the complete tool as defined in THE TARGET (Tour 2) and the
> approved VISION.md, not any single slice of it: a static Terraform/
> CloudFormation auditor, API-first on SQLite, deterministic core, that flags
> high-risk patterns, maps each finding to a named compliance control
> (CIS/SOC2/ISO 27001/GDPR), aggregates a 0-100 Risk Score, and shows it on a
> dashboard. Decompose the WHOLE tool into bounded sprints with dependencies and
> acceptance criteria, following the approved PROTOCOL.md. The MVP is the
> scaffold through the dashboard; the differentiators and polish come after. The
> first sprint is the scaffold (project tree + the approved governance files
> written in + a FastAPI/SQLite skeleton + CI). Write NO code yet - this is the
> decomposition for my Gate 1 approval. Present SPRINTS.md and STOP.

---

## Prompt #9 — T0 (2026-06-22) — Gate 1: adjust SPRINTS.md (5 changes + 2 lighter)

> [GATE 1 — adjust, do not lock] The spine is right (S0 scaffold → dashboard
> MVP, differentiators after). Approving the shape, rejecting five things.
> Re-issue SPRINTS.md with these changes, then STOP for re-approval. No code.
>
> 1. RESTORE the adversarial-assurance sprint. Your plan has no sprint that
>    aggregates the per-detector true-positive / near-miss verdicts into a
>    published coverage matrix, and no external oracle at all. That matrix +
>    oracle IS the differentiator (functional assurance — what an
>    audit/compliance evaluator actually cares about), not optional polish.
>    Add a post-MVP sprint: collect every detector's TP + FP-trap verdict
>    into one rule->case->verdict artifact, cross-checked against the
>    labelled fixture manifest; plus Checkov-on-TerraGoat (pinned version +
>    commit, reference committed in tests/oracle/), claim = agreement on my
>    implemented subset (K->K), NOT recall vs all Checkov. It builds the
>    matrix from the CI tests already written in their sprints — it does not
>    re-run detection by hand.
>
> 2. KEEP the repo-URL ConfigSource INSIDE the MVP, not deferred. You put the
>    uploaded-files source early and pushed the public-repo-URL clone to
>    post-MVP. The headline demo is "paste a public repo URL -> Risk Score" —
>    it must be in the graded MVP. Fold both sources into the API sprint
>    behind one ConfigSource abstraction. Treat the network clone as its own
>    sensitive gate within that sprint: SSRF-safe by construction (exact-match
>    host allowlist, https only), and a discrimination test proves a
>    non-allowlisted host (169.254.169.254, localhost) is REJECTED and an
>    allowed host accepted.
>
> 3. SPLIT scoring from mapping — you flagged this splittable yourself. Risk
>    Score is its OWN sprint: a pure, deterministic, severity-weighted
>    aggregation, unit-tested for same-input-same-output, edge cases covered
>    (no findings -> 0; all-critical -> capped at 100), returning the
>    per-finding breakdown, not just a number. Compliance mapping + the
>    deterministic NL explanation is the NEXT, separate sprint (finding -> a
>    named control CIS/SOC2/ISO27001/GDPR + reference_url; a pure render()
>    template, no LLM). That second sprint is the differentiator and earns its
>    own gate.
>
> 4. DROP the standalone persistence/ORM sprint — but keep its one good
>    criterion. A full models + repository sprint before the domain shape is
>    discovered is premature abstraction and a scope trap in this window. Let
>    the entities accrete with the domain (resource at parse, finding at
>    detect, score at aggregate, control at map); SQLite stays a thin layer in
>    the scaffold. BUT on the sprint where a scan first gets persisted, add an
>    acceptance criterion: a Scan with its Findings + Score round-trips
>    write->read identical.
>
> 5. Detectors: 2 must-have + 2 amplification, with an eject rule — not
>    2-then-expand-much-later. Seed the engine with the two named detectors
>    (public S3 bucket, open SSH 0.0.0.0/0:22) as the gated core, plus two
>    more (unencrypted storage, publicly-accessible DB) as in-sprint
>    amplification. Every detector ships its discrimination pair (a
>    true-positive that MUST fire + a near-miss that must NOT). Eject rule: if
>    the engine sprint runs long, ship the 2 must-haves green + their pairs
>    and record the other 2 as next-up — never a detector without its FP-trap
>    test.
>
> Two lighter ones:
> - LLM narration stays ROADMAP, not a planned sprint. If built after the MVP,
>   it carries a fence test: verdict + Risk Score byte-identical LLM-on vs
>   LLM-off, plus a post-check rejecting any control_id outside the mapping.
>   Never in the trust path; the evaluator runs the MVP with no API key.
> - Remediation (a corrected IaC snippet / CLI action per finding) + README
>   belong in the final polish sprint, not scattered.
>
> Re-issue the full SPRINTS.md against this: keep the linear dependency chain
> and per-sprint acceptance criteria, mark the MVP boundary at the dashboard,
> and flag the sensitive gates (the persist-bearing sprint, the in-MVP network
> clone, any LLM/secret work). Present it and STOP at Gate 1.

---

## Prompt #10 — T0 (2026-06-22) — Gate 1 OK; split S5/S5b; write SPRINTS.md; S0 ticket

> [GATE 1 OK — rev 2] Decomposition approved. Verified against the five
> corrections:
> - assurance matrix + Checkov/TerraGoat K->K oracle restored (S7), built
>   from the CI tests already written, not re-run by hand.
> - repo-URL ConfigSource in the graded MVP behind one abstraction; headline
>   "paste repo URL -> Risk Score" preserved; SSRF discrimination test present.
> - Risk Score (S3, pure deterministic) split from mapping + explanation (S4).
> - standalone ORM sprint dropped; entities accrete; round-trip criterion on
>   the persist-bearing sprint.
> - detectors = 2 must-have + 2 amplification with the eject rule (S2); each
>   ships its TP + near-miss pair.
> LLM correctly in Roadmap with the fence test; remediation + README in the
> polish sprint. Good.
>
> One adjustment before you lock — take the split you offered. S5 carries
> three concerns and two independent sensitive decisions; that breaks
> one-bounded-sprint-per-exchange and entangles a security feature with the
> schema. Split it cleanly:
> - S5 = REST API + uploaded-files ConfigSource + persistence: the concrete
>   SQLite tables (Scan/Finding/Score/Control) + the write->read round-trip
>   criterion. ONE sensitive sub-gate: the schema.
> - S5b = the public-repo-URL ConfigSource ONLY: shallow read-only clone,
>   https-only exact-match host allowlist, the SSRF discrimination test
>   (non-allowlisted host + 169.254.169.254/localhost rejected, allowlisted
>   accepted) and the parity test (same files via upload vs via repo_url ->
>   identical findings + score). ONE sensitive sub-gate: the network clone.
>   Still pre-dashboard, still in the graded MVP.
> Renumber the dashboard and everything after accordingly. The assurance
> sprint depends on the detectors sprint + the persistence/pipeline sprint —
> NOT on the clone sprint, so the matrix isn't blocked by S5b.
>
> Fold the split in and re-issue SPRINTS.md to disk (mechanical renumber, no
> need to STOP again on the plan). Then proceed to the S0 start gate: propose
> the S0 ticket — Goal / Context / Constraints / Done-when — and STOP before
> writing anything.

---

## Prompt #11 — T0 (2026-06-22) — Gate 2(a) S0: amend ticket

> [GATE 2(a) S0 — amend before build] Ticket is sound and the minimal
> dependency set is right. Root placement of the governance files is correct
> (CLAUDE.md must auto-load from root) — keep it. Fixes before I approve; no
> code yet:
>
> 1. highlights.md is NOT a bare stub. It ships with the trigger legend
>    (CATCH / DISCRIMINATION / GATE / DECISION / GENERALITY / MAPPING /
>    METRIC) AND the one seeded foundational highlight: "ASSURANCE —
>    validation runs in an independent read-only agent (separate context
>    window, Read/Grep/Bash only) that reviews the repo artifacts but not the
>    BUILDER's conversation or reasoning — structural assurance, not
>    self-review." Add it to Done-when.
>
> 2. Add docs/ and docs/screenshots/ (.gitkeep) — home for the deck and its
>    screenshots (dashboard / matrix / gate-rejection), referenced by path
>    later. Scaffold now.
>
> 3. Scaffold audit/ and tests/fixtures/ with .gitkeep so every later sprint
>    has its place (VERIFIER reports -> audit/; deterministic regression
>    corpus -> tests/fixtures/).
>
> 4. One dependency source of truth: drop requirements.txt unless CI needs it;
>    if kept, justify it and generate it from pyproject, never hand-edit.
>
> 5. Confirm LICENSE is Apache 2.0; if the file on disk isn't, write it.
>
> One decision, not a question: use the layered source tree, not app/. Create
> top-level api/, core/, rules/, models/ (each with __init__.py; .gitkeep
> where still empty) plus the thin app entry. These aren't padding — models/
> fills at S1, rules/ at S2, core/ at S3/S5, api/ at S5; all populated before
> the MVP closes, and the layered tree is the repo legibility I'm graded on.
> db.py stays thin (engine/session/init only, no domain tables) wherever it
> lands.
>
> Re-issue the S0 ticket with these folded in and STOP again at Gate 2(a) —
> still no code.

---

## Prompt #12 — T0 (2026-06-22) — Gate 2(a) S0 APPROVED; build

> [GATE 2(a) S0 — approved] Ticket rev 2 is clean; all six amendments folded
> in (verified: highlights.md legend + seeded ASSURANCE highlight in
> Done-when #6; docs/ + docs/screenshots/ + audit/ + tests/fixtures/ with
> .gitkeep; requirements.txt dropped, pyproject single source via
> pip install -e ".[dev]"; LICENSE Apache 2.0; layered api/core/rules/models).
>
> Both micro-decisions resolved — no veto:
> - core/db.py: correct. core/ is the data layer in this architecture; db.py
>   belongs there. Keep it.
> - __init__.py over .gitkeep for the empty packages: correct — that is how
>   you keep a Python package tracked; .gitkeep is only for the non-package
>   dirs. Keep it.
>
> One trivial add before you build: make .gitignore exclude the dev SQLite
> file (e.g. *.db / *.sqlite3 and whatever path init_db() writes) so a local
> DB is never committed.
>
> Approved. BUILDER: implement exactly this tree, run the L1 ladder
> (ruff / mypy / pytest) + the /health test. Then VERIFIER audits to
> audit/S0.md, SCRIBE updates memory, REPORTER logs the seeded highlight.
> STOP at the evidence gate with the real command output pasted — hold the
> commit until I approve.

---

## Prompt #13 — T0 (2026-06-22) — Gate S0: genericity grep + frontmatter checks, then commit

> [GATE S0] Evidence is strong - L1 green with real output, the independent
> verifier ran live and returned PASS, tampering hunt clean, constraints
> honored, governance on disk. Two things before I approve the commit:
>
> 1. Run the genericity grep on the written file and paste the output:
>    grep -riE "s3|ssh|terraform|cloudform|bucket|security" PROTOCOL.md
>    I need zero hits - this is the falsifiable proof PROTOCOL.md is
>    project-agnostic. If anything hits, fix it before commit.
>
> 2. Criterion 5 (governance byte-for-byte vs approved) is only a NOTE because
>    the verifier can't check it from inside the repo. Print the verifier.md
>    frontmatter (confirm `model: opus`, tools Read/Grep/Bash only) and confirm
>    PROTOCOL.md still has sections a-h including f. I'll eyeball against what I
>    approved.
>
> Once the grep is zero and those are confirmed, approved - commit S0 with your
> proposed subject and push, then open the S1 start gate. S1 is the parser
> sprint (the highest-risk one): at its start gate I want the HCL edge-case list
> BEFORE any code, and the eject rule (TF-first + LIMITATIONS.md if the CFN
> mapper tangles) in the ticket.

---

## Prompt #14 — T0 (2026-06-22) — Gate S1: approach approved + two refinements

> [GATE S1 OK - approach approved, two refinements to fold in]
> Strong ticket - the edge-case list, the line-number fallback, and the eject
> rule are exactly right for the highest-risk sprint. Deps approved (python-hcl2
> + pyyaml). .tf.json deferral approved (TF-first = HCL). The with_meta /
> line-scan fallback is the right hedge.
>
> Two things to fold in, both about not pushing format quirks downstream:
>
> 1. Normalize nested-block shape in the Resource model. python-hcl2 can return
>    a single nested block (one `ingress`) as a dict and repeated ones as a
>    list; if that reaches the detectors, each one has to branch on type and
>    will miss cases. Absorb it in the mapper: a same-named nested block is
>    ALWAYS a list (length 1 for a single occurrence), documented, with a test
>    proving single-vs-multiple present the same shape.
>
> 2. Line accuracy under comments is the most likely silent break. The TF
>    fixture for the line-ref criterion must include comments (#, //, /* */) and
>    blank lines BEFORE a resource, so the test proves the reported line
>    survives comments - especially if the line-scan fallback kicks in. Same for
>    one CFN fixture.
>
> Everything else approved as written. Build parsers + fixtures + tests, run L1,
> and STOP at the S1 evidence gate - I'll want the real type/name/line output on
> a commented multi-resource fixture, not just "passed".

---

## Prompt #15 — T0 (2026-06-22) — Gate S1 APPROVED; commit + push; open S2

> [GATE S1 OK] Evidence is conclusive: L1 green with real output, exact
> type/name/line on commented multi-resource fixtures (lines 6/14/7/13/4
> asserted, not weakened), YAML/JSON parity, both refinements PASS (nested-block
> always-list + line-under-comments), VERIFIER 7/7 PASS, constraints honored,
> both formats land (no eject). The single `# noqa: S506` is legitimate - it's a
> SafeLoader subclass, bandit S ruleset isn't enabled. Approved - commit S1 with
> your proposed subject and push.
>
> Then open the S2 start gate: detector engine + the 4 detectors (public S3 +
> open SSH must-have, unencrypted storage + public DB amplification), EACH with
> its discrimination pair (true-positive MUST fire, near-miss MUST NOT). This is
> the first L3 sprint - the adversarial pairs are the deliverable, not an extra.
> Propose the S2 ticket (Goal / Context / Constraints / Done-when) and STOP
> before any code. Keep the eject (ship the 2 must-haves with their pairs if the
> sprint runs long).

---

## Prompt #16 — T0 (2026-06-22) — Gate S2 approved + two hardenings; build

> [GATE S2 OK - approach approved, with two hardenings]
> Strong L3 ticket - discrimination pairs as the deliverable, cross-format TPs,
> determinism test, and the VERIFIER anti-fake focus (no always-None/always-fire
> detector) are exactly right. Decisions approved: (c) UNENCRYPTED_STORAGE scoped
> to explicit encrypted=false on EBS/RDS (S3-SSE-absence -> roadmap/LIMITATIONS).
> Two hardenings before code:
>
> 1. Severities: align each detector's severity with the citable authority you'll
>    map to in S4 (AVD/CIS), so the score weights and the S4 mapping come from the
>    same source and survive the Checkov oracle at S7. In particular reconcile
>    S3_PUBLIC_BUCKET vs OPEN_SSH (AVD anchors SSH-open as CRITICAL); pick per the
>    source and document the choice in memory/decisions.md.
>
> 2. S3_PUBLIC_BUCKET near-miss must include the hard one: a bucket policy with
>    Principal:"*" BUT a restrictive Condition that scopes it (e.g. a VPCe / source
>    IP condition) - this MUST NOT flag. That's the exact false positive Checkov
>    trips on, so proving your detector stays silent here is the differentiator.
>    Keep the private+versioning near-miss too (ADAPTER §2 verbatim).
>
> Everything else approved: rule_ids as the S4 join keys, policy-public via
> wildcard-Principal Allow, the 4 detectors with their pairs, the eject (2
> must-haves with pairs if long). Build the engine + detectors + discrimination
> corpus, run L1, and STOP at the S2 evidence gate. At that gate I want, per
> detector, the real TP-fires / near-miss-silent output - not just "passed".

---

## Prompt #17 — T0 (2026-06-22) — ANOMALY: verbatim duplicate of #12

> Received a prompt identical to #12 ("[GATE 2(a) S0 — approved] … Approved.
> BUILDER: implement exactly this tree …"). Flagged as a stale/duplicate paste,
> NOT re-executed. S0 is already built + verified + committed/pushed as e895474.
> Held: S2 remains at Gate 2(b) awaiting approval; no commit, no S0 rebuild.
> Awaiting architect clarification (commit S2 + open S3, or other intent).
>
> RESOLVED via clarification — real intended prompt #18 below.

---

## Prompt #18 — T0 (2026-06-22) — Gate S2: prove severities against source before commit

> [GATE S2 - substance approved, one source-check before commit]
> The detectors are done and the discrimination is real: every detector fires on
> its TP and is silent on a same-type near-miss (not always-None/always-fire),
> the hard one holds - wildcard Principal + Condition stays SILENT (the exact
> Checkov false positive), the ADAPTER §2 pair is verbatim, cross-format CFN
> fires, determinism holds. The heredoc false-negative caught by your own L3 test
> (fixed without touching the S1 parser) and the VERIFIER FAIL -> remediate ->
> PASS on the severity doc/code drift are exactly the evidence this sprint should
> produce.
> One confirmation before you commit, because S3 turns these severities into
> score weights: prove each severity against its citable source rather than
> asserting it. Paste, per detector, the AVD (or CIS) ID and the severity that
> page actually states. In particular PUBLIC_DB - you set it CRITICAL via
> AVD-AWS-0011, but my sourcing had publicly-accessible RDS at HIGH. Reconcile
> against the real AVD page and set each severity to what the source says; if any
> isn't backed by its page, change it NOW, before S3 weights on it. Then I
> approve, you commit + push, and open the S3 start gate.

---

## Prompt #19 — T0 (2026-06-22) — Gate S2 ruling: OPEN_SSH critical; verify then commit

> [GATE S2 OK - ruling: OPEN_SSH stays CRITICAL, then commit]
> Good source-check - reading the trivy-checks rego metadata via the GitHub API
> when the AVD SPA wouldn't fetch is the right move, and correcting PUBLIC_DB
> critical->high is the reconciliation I asked for.
>
> Ruling on OPEN_SSH: keep CRITICAL. Deciding reason = consistency with the cited
> source: OPEN_SSH's reference_url points at the AVD-AWS-0107 page, which states
> Critical, so the assigned severity must match the page the dashboard cites - or
> the tool contradicts its own authority. It also matches the merits
> (unauthenticated SSH from 0.0.0.0/0 is the textbook critical) and gives the Risk
> Score a real spread (1 critical / 3 high) instead of flat weights. Document the
> AVD-page-vs-current-rego drift in decisions.md (done) and seed it as
> LIMITATIONS.md material - show the discrepancy and the adjudication, don't hide
> it.
>
> Governing rule, applied to all four: each detector's severity must equal what
> its OWN reference_url page states (this also binds S4's mapping). Confirm in one
> line that S3_PUBLIC_BUCKET / UNENCRYPTED_STORAGE / PUBLIC_DB reference_urls will
> point to pages consistent with HIGH, so severity and cited source agree across
> the board.
>
> Before commit: run the VERIFIER once more on the severity change only - confirm
> RULES, the test assertions, and decisions.md all agree at the final values
> (OPEN_SSH critical, the other three high). On its PASS, commit + push S2 with
> your subject, then open the S3 start gate.

---

## Prompt #20 — T0 (2026-06-22) — Gate S3 approved + two dial fixes; build

> [GATE S3 OK - additive-capped approved, two dial fixes]
> The structure is right: pure function, the two edge cases ([]->0/A,
> all-critical->cap 100/F), the per-finding breakdown, order-independent
> determinism via the sort, and the monotonic criterion are all good. Keep
> additive-capped - normalized would be overkill for the MVP. Two dial fixes
> before code, both about not flattening the severity spread we just locked:
>
> 1. Weights flatten critical. With 40/20/10/5, one critical (40) ties two highs
>    (40), and OPEN_SSH being critical stops meaning more - which defeats
>    yesterday's decision. Set weights so ONE critical outranks TWO highs, e.g.
>    critical=50, high=15, medium=5, low=1. A single critical should already
>    read as serious.
>
> 2. Couple the grade to the worst severity present, not just the sum. With a
>    pure additive cap, a lone critical can land at a reassuring grade. Add: if
>    any finding is critical, the grade floors at D (and high floors at C). The
>    numeric score still refines within that. Document the band table + the
>    severity-floor rule in decisions.md so it's auditable.
>
> Everything else approved: additive cap at 100, breakdown, determinism,
> monotonicity. Re-propose the final dials (weights + bands + the severity-floor)
> in one line for my nod, then build + tests, and STOP at the S3 evidence gate.
> I want the real score dump on the multi-violation fixture (1 critical + 3 high)
> showing the score AND the breakdown, plus both edge cases.

---

## Prompt #21 — T0 (2026-06-22) — Gate S3 APPROVED; commit + push; open S4

> [GATE S3 OK] Evidence is conclusive: the multi-violation dump shows 95/100 / F
> with critical (50) outranking two highs, the severity-floor holds (lone
> critical->D, lone high->C, 3-crit stays F), both edge cases land (0/A, cap
> 100/F), purity confirmed (scoring imports only stdlib + models), determinism
> via the sort (10x shuffle identical), monotonicity and breakdown
> Sigma==raw all green, VERIFIER 7/7 + dials PASS, no tampering. Applying the S2
> "document the dials up front" lesson is exactly the memory loop working.
> Approved - commit S3 with your subject and push.
>
> Then open the S4 start gate: compliance mapping (finding -> named control +
> reference_url via a deterministic table) + the pure render() explanation. NO
> LLM in this sprint - the narration layer is roadmap, post-MVP. The governing
> rule from S2 binds here: each control's reference_url page must be consistent
> with the detector's severity (so cited source and severity agree). Propose the
> mapping schema + the deterministic template (Goal / Context / Constraints /
> Done-when) and STOP before any code.

---

## Prompt #22 — T0 (2026-06-22) — Gate S4: verify control IDs, drop AVD framework, add SOC2

> [GATE S4 - structure approved, two source fixes + one addition before code]
> The deterministic core (no LLM this sprint), the pure render() with clean
> missing-line handling (no :None), the ADAPTER §1 fence test, and refusing to
> ship a fabricated URL are all right. Three changes before code:
>
> 1. VERIFY the CIS/ISO control IDs against a pinned benchmark version - do not
>    assert them. CIS AWS Foundations numbering changes across versions (v1.2 vs
>    v1.4 vs v3.0), so "CIS AWS 5.2" for SSH may be wrong - in older versions the
>    SSH-0.0.0.0/0 control was 4.1. Pin ONE CIS version (state it, e.g. v3.0.0)
>    and verify each control_id against it the same way you source-checked the S2
>    severities (read the authoritative source, not memory). If a precise number
>    isn't verifiable, cite the benchmark section, never a guessed number. Same
>    for ISO 27001 Annex A control refs. A fabricated control id is the single
>    worst credibility hit for an audit tool.
>
> 2. AVD is NOT a compliance framework - drop it from the Framework enum. AVD is
>    your severity-anchor/provenance, not a control an auditor cites. The
>    dashboard's "Compliance:" line must show only CIS / SOC 2 / ISO 27001 / GDPR.
>    Keep the AVD anchor as a separate severity-source field (or in
>    decisions.md), used by the governing-rule test (criterion 3), but never
>    rendered as a compliance control.
>
> 3. Add SOC 2 where it fits - it's named in the brief and it's the client's core
>    business (TeamMate = audit), but it's absent from every row. Map OPEN_SSH and
>    S3_PUBLIC_BUCKET to SOC 2 CC6.1 (logical access controls) - verify the
>    criterion ref, don't assert it.
>
> URL sourcing ruling: never fabricate a per-control deep link. GDPR ->
> gdpr-info.eu deep links (fine), AVD technical ref -> avd.aquasec.com/misconfig/
> <id>, CIS/ISO -> control-id + the pinned-benchmark landing URL. Honest over
> precise-but-fake.
>
> Everything else approved: Control schema, map_finding, the fence test, render()
> purity, criterion 3 scoped to the AVD anchor. Re-propose the corrected mapping
> table (verified IDs + pinned CIS version + SOC 2 rows + AVD moved out of the
> framework list) for my nod, then build + tests, and STOP at the S4 evidence
> gate. At that gate I want the real per-finding dump: each finding -> its
> controls + the rendered explanation, with real reference_urls.

---

## Prompt #23 — T0 (2026-06-22) — Gate S4 table approved; build

> [GATE S4 OK - table approved, build it]
> Source-check is exactly right: CIS pinned to v3.0.0, two IDs corrected (SSH
> §5.2, S3 §2.1.4 - the version drift), ISO 2022 + SOC 2 CC6.1 confirmed, and
> refusing to guess the RDS sub-number is the correct call, not a gap. Table
> approved as verified.
>
> PUBLIC_DB CIS ruling: keep section-level §2.3, don't drop CIS. ISO 27001:2022
> A.8.20 is PUBLIC_DB's primary named control (criterion 2 satisfied); CIS §2.3
> rides along explicitly marked as section-level. Citing the section because the
> precise sub-number wasn't verifiable is a maturity signal - surface it, don't
> hide it. Seed it in LIMITATIONS.md (CIS RDS sub-number unverified -> cited at
> section level).
>
> One requirement on the output: the distinction between a verified precise
> control (e.g. CIS §5.2) and a section-level cite (CIS §2.3) must be VISIBLE in
> the rendered/stored output, not only in your notes - a reader must not mistake
> §2.3 for a precise control. A simple marker like "§2.3 (section)" is enough.
>
> Everything approved. Build models/control.py + core/compliance.py (table +
> map_finding + pure render) + tests (fence: no stray control_id; governing-rule:
> AVD anchor severity == detector severity; render determinism incl. the no-line
> case -> no :None). Run L1 and STOP at the S4 evidence gate with the real
> per-finding dump: each finding -> its named controls + the rendered explanation
> + real reference_urls.

---

## Prompt #24 — T0 (2026-06-22) — Gate S4 APPROVED; commit + push; open S5

> [GATE S4 OK] Evidence is conclusive: the per-finding dump shows verified
> controls + rendered explanations + real reference_urls, the section-level
> marker is visible in output (§2.3 (section) vs §5.2 clean), the version
> corrections hold (2.1.5->2.1.4, SSH §5.2), the ADAPTER §1 fence and the
> governing-rule severity match all pass, render() is pure with no :None, and the
> diff confirms zero regression / no new dep. The differentiator layer is sourced,
> not asserted - exactly the bar for an audit tool. Approved - commit S4 with your
> subject and push.
>
> Then open the S5 start gate. S5 carries the DB-schema sensitive gate (gate type
> 3): surface the Scan/Finding/Score/Control table design for my approval BEFORE
> any code. Scope = REST API + uploaded-files ConfigSource + persistence ONLY (NOT
> the repo-URL ConfigSource - that's S5b). Acceptance must include the
> write->read round-trip (a Scan with its Findings + Score + controls reads back
> identical) and OpenAPI documenting every endpoint. Propose the ticket (Goal /
> Context / Constraints / Done-when) with the schema called out, and STOP.

---

## Prompt #25 — T0 (2026-06-22) — Gate S5 schema approved; build

> [GATE S5 OK - schema approved (sensitive gate cleared), two notes]
> Schema approved: 4 tables with correct cascades (Scan 1-1 Score, 1-* Finding,
> Finding 1-* Control), ORM in core/tables.py kept separate from the pure
> models/ dataclasses via a repository, and the control `level` (precise/section)
> persisted so the S4 marker survives to the dashboard. Sensitive gate cleared.
>
> Two things:
>
> 1. Denormalizing `explanation` and `weight` is fine for the MVP, but it means a
>    persisted scan can drift from the pipeline if a rule/template later changes.
>    Bound it: the round-trip test (criterion 3) must assert that what's persisted
>    equals what the IN-MEMORY pipeline produced for the same input - compare
>    persisted-vs-pipeline-output, not persisted-vs-itself. That catches a
>    save/load that silently mangles a field.
>
> 2. Upload transport: take multipart (python-multipart). It's your one new dep
>    and it's justified - the demo differentiator is "upload files / paste repo
>    URL", so a real multipart upload endpoint (testable in Swagger) beats a JSON
>    {files:[...]} body that's a fake upload. Approved as a justified dependency.
>
> Scope confirmed: uploaded-files only, repo-URL deferred to S5b. Everything else
> approved (pipeline reused unchanged, OpenAPI on every endpoint, DB-isolated
> tests). Build it, run L1, and STOP at the S5 evidence gate. At that gate I want:
> the real POST /api/scans response on the vulnerable fixtures (201 + score +
> findings with controls + explanation), the persisted-vs-pipeline round-trip
> output, a 404 case, and the /openapi.json path assertions.

---

## Prompt #26 — T0 (2026-06-22) — Gate S5 APPROVED; commit; re-sequence S6 before S5b

> [GATE S5 OK] Conclusive: real POST -> 201 with score + findings + controls +
> explanation, 404 on unknown id, OpenAPI complete, schema matches the approved
> sensitive-gate design, scope grep proves no clone/network leaked (repo-URL is
> correctly absent), pipeline diff empty, DB isolated, only python-multipart
> added, no tampering. The round-trip is genuinely persisted-vs-pipeline and the
> VERIFIER's negative control (corrupt a persisted value -> equality flips)
> proves the test has teeth - log that as a highlight. Approved - commit S5 with
> your subject and push.
>
> Sequencing change before the next sprint: do S6 (dashboard) BEFORE S5b. The
> brief is already satisfied on the upload path at S5, so S6 on uploaded-files
> gives a complete, submittable visual MVP without the SSRF clone on the critical
> path; S5b (repo-URL) then becomes pure upside that adds a URL input to the
> existing dashboard. Open the S6 start gate now: a dashboard served by FastAPI,
> consuming the documented API only, on the upload path - Risk Score gauge +
> grade, findings table (severity badge by colour AND text, the rendered
> explanation, the control reference links), empty/error states, and
> behavioral/integration tests. Defer the repo-URL input to after S5b. Propose
> the minimal UI ticket (Goal / Context / Constraints / Done-when) and STOP.

---

## Timer
- **T0 start**: turn 1 (2026-06-22)
- **Goal**: MVP in 4–6h active build time
- **Hard max**: 16h
- **Elapsed (cumulative active)**: ~0.2h

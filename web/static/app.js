"use strict";
// Dashboard — a thin client of the documented /api endpoints. No business
// logic here: severity, score, controls and explanations all come from the API.

const $ = (id) => document.getElementById(id);
let current = null; // { id, source_type } of the last rendered scan (for Rescan)

async function scanFiles() {
  const input = $("files");
  if (!input.files.length) { showError("Choose at least one file to scan."); return; }
  const form = new FormData();
  for (const file of input.files) form.append("files", file);
  await submit(() => fetch("/api/scans", { method: "POST", body: form }));
}

async function scanRepo() {
  const url = $("repo-url").value.trim();
  if (!url) { showError("Enter a public repo URL."); return; }
  await submit(() => fetch("/api/scans/repo", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: url }),
  }));
}

async function rescan() {
  if (!current || current.source_type !== "repo_url") return;
  await submit(() => fetch(`/api/scans/${current.id}/rescan`, { method: "POST" }));
}

async function submit(request) {
  setStatus("Scanning…");
  try {
    const res = await request();
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      showError(`Scan failed (${res.status}): ${body.detail || "bad input"}`);
      return;
    }
    renderResult(await res.json());
  } catch (err) {
    showError("Network error: " + err);
  }
}

function setStatus(msg) { const s = $("status"); s.textContent = msg; s.hidden = !msg; }

function showError(msg) {
  setStatus("");
  const e = $("error"); e.textContent = msg; e.hidden = false;
  $("results").hidden = true;
}

function renderResult(data) {
  current = { id: data.id, source_type: data.source_type };
  $("error").hidden = true;
  setStatus("");
  $("results").hidden = false;
  $("rescan").hidden = data.source_type !== "repo_url"; // Rescan only for re-fetchable sources
  renderGauge(data.score);
  renderFindings(data.findings);
}

function renderGauge(score) {
  $("score-value").textContent = score.value;
  const grade = $("grade");
  grade.textContent = score.grade;
  grade.className = "grade grade-" + score.grade;

  const arc = $("gauge-arc");
  const len = (arc.getTotalLength && arc.getTotalLength()) || 327; // 2πr, r=52
  const pct = Math.max(0, Math.min(100, score.value)) / 100;
  arc.style.strokeDasharray = String(len);
  arc.style.strokeDashoffset = String(len * (1 - pct));
  arc.setAttribute("class", "arc grade-" + score.grade);

  const c = score.counts;
  $("counts").textContent =
    `Critical ${c.critical} · High ${c.high} · Medium ${c.medium} · Low ${c.low}`;
}

function renderFindings(findings) {
  const body = $("findings-body");
  body.innerHTML = "";
  $("empty").hidden = findings.length > 0;
  $("findings").hidden = findings.length === 0;

  for (const f of findings) {
    const tr = document.createElement("tr");

    const sevCell = document.createElement("td");
    const badge = document.createElement("span");
    badge.className = "badge sev-" + f.severity;
    badge.textContent = f.severity.toUpperCase(); // TEXT label — never colour alone
    sevCell.appendChild(badge);
    tr.appendChild(sevCell);

    tr.appendChild(cell(f.title));
    tr.appendChild(cell(`${f.resource_type} '${f.resource_name}'`));
    tr.appendChild(cell(`${f.file}:${f.line}`));
    tr.appendChild(cell(f.explanation));

    const ctrlCell = document.createElement("td");
    for (const c of f.controls) {
      const a = document.createElement("a");
      a.href = c.reference_url;
      a.target = "_blank";
      a.rel = "noopener";
      a.textContent = c.label; // single source of truth from the API
      ctrlCell.appendChild(a);
      ctrlCell.appendChild(document.createTextNode(" "));
    }
    tr.appendChild(ctrlCell);
    body.appendChild(tr);
  }
}

function cell(text) {
  const td = document.createElement("td");
  td.textContent = text;
  return td;
}

document.addEventListener("DOMContentLoaded", () => {
  $("scan").addEventListener("click", scanFiles);
  $("scan-repo").addEventListener("click", scanRepo);
  $("rescan").addEventListener("click", rescan);
});

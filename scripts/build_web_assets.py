#!/usr/bin/env python3
"""
scripts/build_web_assets.py: Generates web/index.html and docs/deck.html
with embedded precomputed traces from output_examples/ so the UI works both
connected to the live Python server (python3 -m agent.main --serve) and as
a standalone static site (GitHub Pages / direct file open).
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT_DIR / "input_examples"
OUTPUT_DIR = ROOT_DIR / "output_examples"
WEB_DIR = ROOT_DIR / "web"
DOCS_DIR = ROOT_DIR / "docs"


def load_embedded_data() -> dict:
    cases = []
    traces = {}
    for p in sorted(INPUT_DIR.glob("case_*.json")):
        c = json.loads(p.read_text(encoding="utf-8"))
        cases.append(c)
        cid = c["case_id"]
        slug = cid.lower().replace("-", "_")
        t_path = OUTPUT_DIR / f"{slug}_trace.json"
        if t_path.exists():
            traces[cid] = json.loads(t_path.read_text(encoding="utf-8"))
    return {"cases": cases, "traces": traces}


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Switchyard | Multi-Agent Supply-Chain Reconciliation on Zetaris, Meterless & NVIDIA Nemotron</title>
  <style>
    :root {
      --bg: #0b0e14;
      --panel: #111621;
      --panel-alt: #161d2b;
      --border: #232d42;
      --text: #e6edf3;
      --muted: #8b9bb4;
      --accent: #38bdf8;
      --nvidia: #76b900;
      --zetaris: #6366f1;
      --meterless: #f59e0b;
      --danger: #ef4444;
      --warn: #f59e0b;
      --ok: #10b981;
      --mono: "JetBrains Mono", "SFMono-Regular", Consolas, Menlo, monospace;
      --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, sans-serif;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: var(--sans);
      font-size: 14px;
      line-height: 1.5;
      min-height: 100vh;
    }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }

    /* Top Header */
    .topbar {
      background: #0d121c;
      border-bottom: 1px solid var(--border);
      padding: 12px 24px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-mark {
      width: 34px;
      height: 34px;
      border-radius: 8px;
      background: linear-gradient(135deg, #76b900 0%, #38bdf8 55%, #6366f1 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--mono);
      font-weight: 800;
      color: #090d14;
      font-size: 16px;
    }
    .brand-title {
      font-size: 18px;
      font-weight: 700;
      letter-spacing: -0.02em;
    }
    .brand-sub {
      font-size: 12px;
      color: var(--muted);
    }
    .layer-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 6px;
      font-family: var(--mono);
      font-size: 11px;
      font-weight: 600;
      border: 1px solid var(--border);
      background: var(--panel);
    }
    .pill.zetaris { border-color: rgba(99, 102, 241, 0.45); color: #a5b4fc; }
    .pill.meterless { border-color: rgba(245, 158, 11, 0.45); color: #fcd34d; }
    .pill.nvidia { border-color: rgba(118, 185, 0, 0.55); color: #a3e635; background: rgba(118, 185, 0, 0.08); }
    .dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
    .dot.green { background: var(--nvidia); box-shadow: 0 0 8px var(--nvidia); }
    .dot.indigo { background: var(--zetaris); }
    .dot.amber { background: var(--meterless); }

    /* Main Container */
    .container {
      max-width: 1520px;
      margin: 0 auto;
      padding: 18px 24px 48px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    /* Control Strip */
    .control-bar {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px 16px;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 14px;
      align-items: center;
    }
    .case-tabs {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .case-btn {
      background: var(--panel-alt);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 8px 12px;
      border-radius: 7px;
      cursor: pointer;
      font-size: 12px;
      text-align: left;
      transition: all 0.15s ease;
    }
    .case-btn:hover { border-color: var(--accent); }
    .case-btn.active {
      border-color: var(--nvidia);
      background: rgba(118, 185, 0, 0.12);
    }
    .case-btn .cid {
      font-family: var(--mono);
      font-weight: 700;
      color: #a3e635;
      font-size: 11px;
      display: block;
    }
    .case-btn .ctitle {
      font-weight: 600;
      color: var(--text);
      font-size: 12px;
    }
    .action-group {
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
    }
    .btn {
      padding: 8px 14px;
      border-radius: 7px;
      font-weight: 600;
      font-size: 12px;
      cursor: pointer;
      border: 1px solid var(--border);
      background: var(--panel-alt);
      color: var(--text);
      font-family: var(--sans);
      transition: all 0.15s;
    }
    .btn:hover { border-color: var(--accent); }
    .btn.primary {
      background: var(--nvidia);
      color: #080c11;
      border-color: var(--nvidia);
      font-weight: 700;
    }
    .btn.primary:hover { filter: brightness(1.08); }

    /* Operator Question Box */
    .query-bar {
      display: flex;
      gap: 10px;
      align-items: center;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 14px;
    }
    .query-label {
      font-family: var(--mono);
      font-size: 11px;
      color: var(--accent);
      font-weight: 700;
      white-space: nowrap;
      text-transform: uppercase;
    }
    .query-input {
      flex: 1;
      background: #0b0e14;
      border: 1px solid var(--border);
      color: var(--text);
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 13px;
      font-family: var(--sans);
    }

    /* KPI Strip */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 12px;
    }
    .kpi-card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 9px;
      padding: 12px 14px;
    }
    .kpi-label {
      font-size: 11px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 4px;
    }
    .kpi-val {
      font-family: var(--mono);
      font-size: 20px;
      font-weight: 700;
    }
    .kpi-sub {
      font-size: 11px;
      color: var(--muted);
      margin-top: 2px;
      font-family: var(--mono);
    }

    /* 4 Disconnected Sources Grid */
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .section-title {
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--muted);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .sources-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
    }
    .source-card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 13px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .source-card.conflict {
      border-color: rgba(239, 68, 68, 0.45);
    }
    .source-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 6px;
    }
    .source-name {
      font-family: var(--mono);
      font-size: 12px;
      font-weight: 700;
      color: #a5b4fc;
    }
    .source-tag {
      font-family: var(--mono);
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 4px;
      background: rgba(239, 68, 68, 0.14);
      color: #fca5a5;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .kv-list {
      display: flex;
      flex-direction: column;
      gap: 5px;
      font-size: 12px;
    }
    .kv-row {
      display: flex;
      justify-content: space-between;
      gap: 8px;
    }
    .kv-key { color: var(--muted); }
    .kv-val { font-family: var(--mono); font-weight: 600; text-align: right; }
    .source-note {
      margin-top: auto;
      padding-top: 6px;
      border-top: 1px dashed var(--border);
      font-size: 11.5px;
      color: #cbd5e1;
    }

    /* Two-column Main Split: Agent Graph + Final Order */
    .main-split {
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 16px;
    }
    .panel-box {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    /* Agent Collaboration Steps */
    .agent-timeline {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .agent-step {
      background: var(--panel-alt);
      border: 1px solid var(--border);
      border-left: 4px solid var(--accent);
      border-radius: 8px;
      padding: 12px;
      transition: all 0.2s;
    }
    .agent-step.critic {
      border-left-color: var(--warn);
      background: rgba(245, 158, 11, 0.05);
    }
    .agent-step.deep {
      border-left-color: var(--nvidia);
    }
    .step-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 6px;
    }
    .step-title {
      font-weight: 700;
      font-size: 13px;
      color: var(--text);
    }
    .model-badge {
      font-family: var(--mono);
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 5px;
      background: rgba(118, 185, 0, 0.14);
      color: #a3e635;
      border: 1px solid rgba(118, 185, 0, 0.4);
      font-weight: 600;
    }
    .step-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 8px;
    }
    .engine-chip {
      font-family: var(--mono);
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 4px;
      background: rgba(56, 189, 248, 0.12);
      color: #7dd3fc;
      border: 1px solid rgba(56, 189, 248, 0.25);
    }
    .step-body {
      font-family: var(--mono);
      font-size: 11.5px;
      white-space: pre-wrap;
      color: #d1d5db;
      background: #0b0e14;
      padding: 10px;
      border-radius: 6px;
      border: 1px solid var(--border);
    }
    .sql-pill-list {
      margin-top: 8px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .sql-pill {
      font-family: var(--mono);
      font-size: 11px;
      padding: 5px 8px;
      background: rgba(99, 102, 241, 0.1);
      border: 1px solid rgba(99, 102, 241, 0.3);
      border-radius: 5px;
      color: #c7d2fe;
    }

    /* Right Column: Conflict Resolution Matrix & Remediation Order */
    .conflict-card {
      background: var(--panel-alt);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      margin-bottom: 8px;
    }
    .conflict-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }
    .conflict-id {
      font-family: var(--mono);
      font-weight: 700;
      font-size: 12px;
      color: #fcd34d;
    }
    .status-resolved {
      font-family: var(--mono);
      font-size: 10px;
      padding: 2px 7px;
      border-radius: 4px;
      background: rgba(16, 185, 129, 0.16);
      color: #6ee7b7;
      border: 1px solid rgba(16, 185, 129, 0.35);
    }
    .vs-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      font-size: 11.5px;
      margin-bottom: 6px;
    }
    .vs-box {
      background: #0b0e14;
      padding: 7px 9px;
      border-radius: 5px;
      border: 1px solid var(--border);
    }
    .vs-src {
      font-family: var(--mono);
      font-size: 10.5px;
      color: var(--accent);
      margin-bottom: 2px;
    }
    .resolution-note {
      font-size: 12px;
      color: #d1fae5;
      background: rgba(16, 185, 129, 0.07);
      border-left: 3px solid var(--ok);
      padding: 6px 9px;
      border-radius: 4px;
    }

    .report-box {
      background: #0b0e14;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
      font-size: 13px;
      line-height: 1.6;
    }
    .report-box h3 {
      color: #a3e635;
      font-size: 14px;
      margin: 12px 0 6px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 4px;
    }
    .report-box h3:first-child { margin-top: 0; }
    .report-box ul, .report-box ol { padding-left: 20px; margin: 6px 0; }
    .report-box li { margin-bottom: 5px; }
    .report-box code {
      font-family: var(--mono);
      font-size: 11.5px;
      background: rgba(99, 102, 241, 0.16);
      color: #c7d2fe;
      padding: 1px 5px;
      border-radius: 4px;
    }

    /* Bottom Deep-Dive Tabs (Meterless Engines, Zetaris SQL, Nightshift Receipts) */
    .subtabs {
      display: flex;
      gap: 8px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 10px;
    }
    .subtab-btn {
      padding: 7px 14px;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: var(--panel-alt);
      color: var(--muted);
      font-weight: 600;
      font-size: 12px;
      cursor: pointer;
    }
    .subtab-btn.active {
      color: var(--text);
      border-color: var(--accent);
      background: rgba(56, 189, 248, 0.12);
    }
    .engines-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
    }
    .engine-card {
      background: var(--panel-alt);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
    }
    .engine-card h4 {
      font-family: var(--mono);
      font-size: 12px;
      color: #fcd34d;
      margin-bottom: 6px;
    }
    table.data-table {
      width: 100%;
      border-collapse: collapse;
      font-family: var(--mono);
      font-size: 11.5px;
    }
    table.data-table th, table.data-table td {
      border: 1px solid var(--border);
      padding: 7px 9px;
      text-align: left;
    }
    table.data-table th {
      background: var(--panel-alt);
      color: var(--muted);
    }

    @media (max-width: 1200px) {
      .kpi-grid { grid-template-columns: repeat(3, 1fr); }
      .sources-grid, .engines-grid { grid-template-columns: repeat(2, 1fr); }
      .main-split { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>

  <header class="topbar">
    <div class="brand">
      <div class="brand-mark">SY</div>
      <div>
        <div class="brand-title">Switchyard</div>
        <div class="brand-sub">Multi-Agent Supply-Chain Conflict Reconciliation · Open Agent Hackathon 2026 (Track 1)</div>
      </div>
    </div>
    <div class="layer-pills">
      <span class="pill zetaris"><span class="dot indigo"></span>01 DATA: Zetaris Federated SQL (5 Sources)</span>
      <span class="pill meterless"><span class="dot amber"></span>02 BUILD: Meterless Engines (Scout · WorldModel · Markovian · H-MEM)</span>
      <span class="pill nvidia"><span class="dot green"></span>03 POWER: Meterless Nightshift · NVIDIA Nemotron 3.5</span>
      <a href="/deck" class="btn">View Slide Deck</a>
    </div>
  </header>

  <main class="container">
    <!-- Case Selector & Actions -->
    <section class="control-bar">
      <div class="case-tabs" id="caseTabs"></div>
      <div class="action-group">
        <button class="btn" id="btnReplay">Step-by-Step Replay</button>
        <button class="btn primary" id="btnRun">Run Reconciliation Loop</button>
      </div>
    </section>

    <!-- Operator Query Input -->
    <section class="query-bar">
      <span class="query-label">Operator Prompt</span>
      <input type="text" id="queryInput" class="query-input" />
      <span class="pill nvidia" id="activeModePill">Mode: Ready</span>
    </section>

    <!-- 6 KPI Summary Cards -->
    <section class="kpi-grid" id="kpiGrid"></section>

    <!-- 4 Disconnected Zetaris Data Sources -->
    <section>
      <div class="section-header">
        <div class="section-title">
          <span>Layer 01 (DATA): Four Disconnected & Conflicting Sources Queried Through Zetaris</span>
        </div>
        <span style="font-family: var(--mono); font-size: 11px; color: var(--muted);">
          POST /api/v1.0/sql-editor/sqls/run · Single-Statement Lightning SQL
        </span>
      </div>
      <div class="sources-grid" id="sourcesGrid"></div>
    </section>

    <!-- Main Split: Left = 6-Step Agent Graph & Critic Loop | Right = Resolved Conflicts & Final Sourced Order -->
    <section class="main-split">
      <div class="panel-box">
        <div class="section-header">
          <div class="section-title">Iterative Multi-Agent Collaboration & NVIDIA Nemotron Model Receipts</div>
          <span style="font-family: var(--mono); font-size: 11px; color: #a3e635;" id="stepCounterLabel">6 / 6 Steps Complete</span>
        </div>
        <div class="agent-timeline" id="agentTimeline"></div>
      </div>

      <div class="panel-box">
        <div class="section-header">
          <div class="section-title">Meterless World Model: Cross-Source Conflict Resolution Matrix</div>
        </div>
        <div id="conflictMatrix"></div>

        <div class="section-header" style="margin-top: 8px;">
          <div class="section-title">Sourced Remediation Order & Backup Supplier Allocation</div>
        </div>
        <div class="report-box" id="finalReportBox"></div>
      </div>
    </section>

    <!-- Bottom Sponsor Technology Telemetry Tabs -->
    <section class="panel-box">
      <div class="subtabs">
        <button class="subtab-btn active" data-tab="engines">02 BUILD: Meterless Engines Telemetry (All 4 Engines)</button>
        <button class="subtab-btn" data-tab="nightshift">03 POWER: Meterless Nightshift & NVIDIA Nemotron Receipts</button>
        <button class="subtab-btn" data-tab="zetaris">01 DATA: Zetaris Federated SQL Workbench</button>
      </div>
      <div id="tabContent"></div>
    </section>
  </main>

  <script>
    const EMBEDDED_DATA = __EMBEDDED_DATA_JSON__;
    let currentCaseId = "CASE-01";
    let currentTrace = EMBEDDED_DATA.traces["CASE-01"];
    let currentSubTab = "engines";
    let visibleSteps = 6;
    let replayTimer = null;

    function formatMarkdown(md) {
      let html = md
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
      html = html.replace(/^### (.*)$/gm, "<h3>$1</h3>");
      html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
      html = html.replace(/\*([^*]+)\*/g, "<em>$1</em>");
      html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
      const lines = html.split("\n");
      let out = [];
      let inList = false;
      for (const line of lines) {
        if (line.match(/^\s*-\s+/)) {
          if (!inList) { out.push("<ul>"); inList = true; }
          out.push("<li>" + line.replace(/^\s*-\s+/, "") + "</li>");
        } else if (line.match(/^\d+\.\s+/)) {
          if (!inList) { out.push("<ul>"); inList = true; }
          out.push("<li>" + line.replace(/^\d+\.\s+/, "") + "</li>");
        } else {
          if (inList) { out.push("</ul>"); inList = false; }
          if (line.trim()) out.push("<p>" + line + "</p>");
        }
      }
      if (inList) out.push("</ul>");
      return out.join("\n");
    }

    function renderCaseTabs() {
      const container = document.getElementById("caseTabs");
      container.innerHTML = EMBEDDED_DATA.cases.map(c => `
        <button class="case-btn ${c.case_id === currentCaseId ? 'active' : ''}" onclick="selectCase('${c.case_id}')">
          <span class="cid">${c.case_id} · ${c.po_number} (${c.sku})</span>
          <span class="ctitle">${c.production_line}</span>
        </button>
      `).join("");
    }

    function selectCase(caseId) {
      if (replayTimer) { clearInterval(replayTimer); replayTimer = null; }
      currentCaseId = caseId;
      const caseObj = EMBEDDED_DATA.cases.find(c => c.case_id === caseId);
      document.getElementById("queryInput").value = caseObj ? caseObj.question : "";
      if (EMBEDDED_DATA.traces[caseId]) {
        currentTrace = EMBEDDED_DATA.traces[caseId];
        visibleSteps = currentTrace.agent_collaboration_trace.length;
        renderAll();
      }
    }

    function renderKPIs() {
      const m = currentTrace.risk_and_remediation_math;
      const mk = currentTrace.sponsor_technology_evidence.meterless_engines.markovian;
      const ns = currentTrace.sponsor_technology_evidence.meterless_nightshift_and_nvidia_nemotron;
      const wm = currentTrace.sponsor_technology_evidence.meterless_engines.world_model;

      const items = [
        {
          label: "Target PO & Line",
          val: `${m.po_number}`,
          sub: `${m.sku} · ${m.production_line}`,
          color: "var(--accent)"
        },
        {
          label: "True Usable vs Ordered",
          val: `${m.effective_usable_qty.toLocaleString()} / ${m.ordered_qty.toLocaleString()}`,
          sub: `Shortfall: ${m.total_shortfall_units.toLocaleString()} units`,
          color: "var(--danger)"
        },
        {
          label: "Factory Runway vs Delay",
          val: `${m.effective_runway_hours}h vs +${m.carrier_delay_hours}h`,
          sub: `${m.unmitigated_downtime_hours}h unmitigated stop`,
          color: "var(--warn)"
        },
        {
          label: "Net Downtime Avoided",
          val: `$${m.net_loss_avoided_usd.toLocaleString()}`,
          sub: `Expedite premium: $${m.expedite_premium_usd.toLocaleString()}`,
          color: "var(--ok)"
        },
        {
          label: "World Model & Markovian",
          val: `${wm.resolved_conflict_count}/${wm.conflict_count} Resolved`,
          sub: `${mk.compression_ratio_pct}% token savings (${mk.total_tokens_saved}t saved)`,
          color: "#fcd34d"
        },
        {
          label: "NVIDIA Nemotron Calls",
          val: `${ns.total_nemotron_calls} Verified`,
          sub: `3 Fast (30B) · 3 Deep (120B)`,
          color: "var(--nvidia)"
        }
      ];

      document.getElementById("kpiGrid").innerHTML = items.map(k => `
        <div class="kpi-card">
          <div class="kpi-label">${k.label}</div>
          <div class="kpi-val" style="color:${k.color}">${k.val}</div>
          <div class="kpi-sub">${k.sub}</div>
        </div>
      `).join("");
    }

    function renderSources() {
      const sr = currentTrace.source_records;
      const erp = sr["zetaris_erp.purchase_orders"] || {};
      const wms = sr["zetaris_wms.inventory_ledger"] || {};
      const qms = sr["zetaris_qms.incident_tickets"] || {};
      const car = sr["zetaris_rest.carrier_port_feeds"] || {};

      const cards = [
        {
          name: "zetaris_erp.purchase_orders",
          tag: "DISAGREES ON STATUS",
          rows: [
            ["PO / Supplier", `${erp.po_number} · ${erp.supplier_name}`],
            ["Ordered Qty", `${(erp.ordered_qty || 0).toLocaleString()} units`],
            ["ERP Status", `${erp.erp_status}`],
            ["Promised ETA", `${erp.promised_eta}`],
            ["Unit Cost", `$${Number(erp.unit_cost_usd || 0).toFixed(2)}`]
          ],
          note: erp.buyer_notes || ""
        },
        {
          name: "zetaris_wms.inventory_ledger",
          tag: `RUNWAY: ${wms.line_runway_hours}h`,
          rows: [
            ["Ledger / Lot", `${wms.ledger_id} · ${wms.lot_code}`],
            ["Physically Docked", `${(wms.received_qty || 0).toLocaleString()} units`],
            ["Unrestricted Usable", `${(wms.usable_unrestricted_qty || 0).toLocaleString()} units`],
            ["Quarantined / Missing", `${wms.quarantined_qty} Q / ${wms.in_transit_deficit_qty} M`],
            ["Line-Stop Cost", `$${Number(wms.downtime_cost_per_hour_usd || 0).toLocaleString()}/hr`]
          ],
          note: wms.warehouse_note || ""
        },
        {
          name: "zetaris_qms.incident_tickets",
          tag: `${qms.ticket_id} · ${qms.severity}`,
          rows: [
            ["Ticket / Status", `${qms.ticket_id} · ${qms.qms_status}`],
            ["Defect Rate", `${qms.defect_rate_pct}%`],
            ["Failure Mode", `${(qms.failure_mode || "").slice(0, 38)}...`],
            ["Vendor Claim", `${(qms.supplier_dispute_claim || "").slice(0, 36)}...`]
          ],
          note: `Lab Verdict: ${qms.lab_verdict}`
        },
        {
          name: "zetaris_rest.carrier_port_feeds",
          tag: `+${car.reported_delay_hours}h DELAY`,
          rows: [
            ["Feed / Vessel", `${car.feed_id} · ${(car.vessel_or_flight || "").slice(0, 22)}`],
            ["Carrier Status", `${car.carrier_status}`],
            ["Delay / Revised ETA", `+${car.reported_delay_hours}h · ${(car.revised_eta || "").slice(0, 10)}`],
            ["Units on Conveyance", `${(car.units_on_conveyance || 0).toLocaleString()} units`]
          ],
          note: car.telemetry_alert || ""
        }
      ];

      document.getElementById("sourcesGrid").innerHTML = cards.map(c => `
        <div class="source-card conflict">
          <div class="source-head">
            <span class="source-name">${c.name}</span>
            <span class="source-tag">${c.tag}</span>
          </div>
          <div class="kv-list">
            ${c.rows.map(r => `<div class="kv-row"><span class="kv-key">${r[0]}</span><span class="kv-val">${r[1]}</span></div>`).join("")}
          </div>
          <div class="source-note">${c.note}</div>
        </div>
      `).join("");
    }

    function renderAgentTimeline() {
      const steps = currentTrace.agent_collaboration_trace.slice(0, visibleSteps);
      const total = currentTrace.agent_collaboration_trace.length;
      document.getElementById("stepCounterLabel").textContent = `${steps.length} / ${total} Steps Shown`;

      document.getElementById("agentTimeline").innerHTML = steps.map(s => {
        const rcpt = s.model_receipt;
        const cap = s.markovian_capsule;
        const isCritic = s.agent.includes("Critic");
        const isDeep = rcpt.model_handled_by.includes("120b") || rcpt.model_handled_by.includes("super");
        const sqlHtml = (s.sql_executed || []).map(q => `
          <div class="sql-pill">
            [Zetaris SQL · req:${q.request_id.slice(0, 8)} · ${q.row_count} row(s)] ${q.sql}
          </div>
        `).join("");

        return `
          <div class="agent-step ${isCritic ? 'critic' : (isDeep ? 'deep' : '')}">
            <div class="step-top">
              <div>
                <div class="step-title">Step ${s.step}: ${s.agent}</div>
                <div style="font-size:11.5px; color:var(--muted);">${s.role}</div>
              </div>
              <span class="model-badge" title="Served through Meterless Nightshift Runtime (${rcpt.endpoint})">
                Handled by: ${rcpt.model_handled_by} (${rcpt.lane})
              </span>
            </div>
            <div class="step-meta">
              ${s.engines_used.map(e => `<span class="engine-chip">Meterless: ${e}</span>`).join("")}
              <span class="engine-chip">Receipt: ${rcpt.receipt_id}</span>
              <span class="engine-chip">Markovian Capsule: ${cap.bounded_capsule_tokens}t (saved ${cap.tokens_saved}t)</span>
            </div>
            <div class="step-body">${s.output_summary}</div>
            ${sqlHtml ? `<div class="sql-pill-list">${sqlHtml}</div>` : ""}
          </div>
        `;
      }).join("");
    }

    function renderConflictsAndReport() {
      const wm = currentTrace.sponsor_technology_evidence.meterless_engines.world_model;
      document.getElementById("conflictMatrix").innerHTML = (wm.conflicts || []).map(c => `
        <div class="conflict-card">
          <div class="conflict-top">
            <span class="conflict-id">${c.conflict_id}: ${c.dimension}</span>
            <span class="status-resolved">${c.status} · Winner: ${c.authoritative_source}</span>
          </div>
          <div class="vs-grid">
            <div class="vs-box">
              <div class="vs-src">${c.source_a}</div>
              <div>${c.claim_a}</div>
            </div>
            <div class="vs-box">
              <div class="vs-src">${c.source_b}</div>
              <div>${c.claim_b}</div>
            </div>
          </div>
          <div class="resolution-note">
            <strong>Resolution & Corroboration (${(c.corroborating_sources || []).join(", ")}):</strong>
            ${c.resolution_explanation}
          </div>
        </div>
      `).join("");

      document.getElementById("finalReportBox").innerHTML = formatMarkdown(currentTrace.final_report_markdown);
    }

    function renderSubTab() {
      const box = document.getElementById("tabContent");
      const ev = currentTrace.sponsor_technology_evidence;

      if (currentSubTab === "engines") {
        const si = ev.meterless_engines.scout_intent;
        const wm = ev.meterless_engines.world_model;
        const mk = ev.meterless_engines.markovian;
        const hm = ev.meterless_engines.h_mem;

        box.innerHTML = `
          <div class="engines-grid">
            <div class="engine-card">
              <h4>1. Scout Intent Engine</h4>
              <div class="kv-list">
                <div class="kv-row"><span class="kv-key">Classified Intent</span><span class="kv-val">${si.intent_type}</span></div>
                <div class="kv-row"><span class="kv-key">Blast-Radius Risk</span><span class="kv-val" style="color:var(--danger)">${si.risk_level} (${si.risk_score}/100)</span></div>
                <div class="kv-row"><span class="kv-key">Lane 1 Route</span><span class="kv-val">${si.primary_nemotron_model}</span></div>
                <div class="kv-row"><span class="kv-key">Lane 2 Route</span><span class="kv-val">${si.verification_nemotron_model}</span></div>
              </div>
              <div class="source-note" style="margin-top:8px;">${si.routing_rationale}</div>
            </div>

            <div class="engine-card">
              <h4>2. World Model Engine</h4>
              <div class="kv-list">
                <div class="kv-row"><span class="kv-key">State Version</span><span class="kv-val">v${wm.version} (Optimistic Lock)</span></div>
                <div class="kv-row"><span class="kv-key">Sourced Facts</span><span class="kv-val">${wm.fact_count} facts recorded</span></div>
                <div class="kv-row"><span class="kv-key">Conflicts Resolved</span><span class="kv-val" style="color:var(--ok)">${wm.resolved_conflict_count} / ${wm.conflict_count}</span></div>
                <div class="kv-row"><span class="kv-key">Mutations Logged</span><span class="kv-val">${wm.mutation_log.length} transitions</span></div>
              </div>
              <div class="source-note" style="margin-top:8px;">Shared across Planner, Reconciler, Conflict Critic, and Risk Escalation agents without state clobbering.</div>
            </div>

            <div class="engine-card">
              <h4>3. Markovian Thinking Engine</h4>
              <div class="kv-list">
                <div class="kv-row"><span class="kv-key">Token Budget Ceiling</span><span class="kv-val">${mk.max_capsule_budget_tokens} tokens/step</span></div>
                <div class="kv-row"><span class="kv-key">Naive Cumulative</span><span class="kv-val">${mk.naive_total_tokens_across_steps} tokens</span></div>
                <div class="kv-row"><span class="kv-key">Markovian Bounded</span><span class="kv-val" style="color:var(--ok)">${mk.markovian_total_tokens_across_steps} tokens</span></div>
                <div class="kv-row"><span class="kv-key">Compression Savings</span><span class="kv-val" style="color:#a3e635">${mk.compression_ratio_pct}% (${mk.total_tokens_saved}t saved)</span></div>
              </div>
              <div class="source-note" style="margin-top:8px;">Replaces O(n^2) transcript growth with deterministic Carry-Over State capsules across all 6 turns.</div>
            </div>

            <div class="engine-card">
              <h4>4. H-MEM (Hierarchical Memory)</h4>
              <div class="kv-list">
                <div class="kv-row"><span class="kv-key">Recalled Before Run</span><span class="kv-val">${hm.recalled_before_run.length} precedent(s)</span></div>
                <div class="kv-row"><span class="kv-key">Committed After Run</span><span class="kv-val" style="color:#a3e635">${hm.committed_after_run.memory_id}</span></div>
                <div class="kv-row"><span class="kv-key">Total Store Size</span><span class="kv-val">${hm.store_summary.total_memories} records</span></div>
              </div>
              <div class="source-note" style="margin-top:8px;">
                <strong>New Rule Committed:</strong> ${hm.committed_after_run.learned_rule}
              </div>
            </div>
          </div>
        `;
      } else if (currentSubTab === "nightshift") {
        const ns = ev.meterless_nightshift_and_nvidia_nemotron;
        box.innerHTML = `
          <div style="margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div style="font-size:12.5px;">
              <strong>Primary AI Provider:</strong> ${ns.primary_provider} (<code>${ns.runtime_endpoint}</code>) ·
              <strong>Security Rule Verified:</strong> NVIDIA API key stays inside Nightshift Providers tab; app uses Nightshift Runtime token + <code>meterless-app: switchyard-agent</code>.
            </div>
          </div>
          <table class="data-table">
            <thead>
              <tr>
                <th>Receipt ID</th>
                <th>Step & Agent</th>
                <th>Nightshift Lane</th>
                <th>Model Handled By (NVIDIA Nemotron)</th>
                <th>Headers Sent</th>
                <th>Tokens (P / C)</th>
                <th>Latency</th>
              </tr>
            </thead>
            <tbody>
              ${ns.model_receipts.map(r => `
                <tr>
                  <td>${r.receipt_id}</td>
                  <td>${r.step_name} (${r.agent_name})</td>
                  <td>${r.lane}</td>
                  <td style="color:#a3e635; font-weight:700;">${r.model_handled_by}</td>
                  <td>meterless-app=${r.headers_verified["meterless-app"]}, scope=${r.headers_verified["meterless-scope"]}</td>
                  <td>${r.prompt_tokens} / ${r.completion_tokens}</td>
                  <td>${r.latency_ms} ms</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        `;
      } else if (currentSubTab === "zetaris") {
        const zt = ev.zetaris;
        box.innerHTML = `
          <div style="display:flex; gap:10px; margin-bottom:12px; align-items:center;">
            <input type="text" id="customSqlInput" class="query-input" value="SELECT p.po_number, p.erp_status, w.usable_unrestricted_qty, w.quarantined_qty, c.carrier_status FROM zetaris_erp.purchase_orders p JOIN zetaris_wms.inventory_ledger w ON p.po_number = w.po_number JOIN zetaris_rest.carrier_port_feeds c ON p.po_number = c.po_number" />
            <button class="btn primary" onclick="runCustomSql()">Run Single-Statement SQL</button>
          </div>
          <div id="customSqlResult" style="margin-bottom:12px;"></div>
          <table class="data-table">
            <thead>
              <tr>
                <th>X-Request-ID (UUID4)</th>
                <th>Query ID</th>
                <th>Zetaris Tables Touched</th>
                <th>Single-Statement SQL Sent to /sql-editor/sqls/run</th>
                <th>Rows</th>
                <th>Latency</th>
              </tr>
            </thead>
            <tbody>
              ${zt.sql_receipts.map(q => `
                <tr>
                  <td>${q.request_id}</td>
                  <td>${q.query_id}</td>
                  <td>${q.source_tables_touched.join(", ")}</td>
                  <td style="color:#c7d2fe;">${q.sql}</td>
                  <td>${q.row_count}</td>
                  <td>${q.latency_ms} ms</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        `;
      }
    }

    async function runCustomSql() {
      const sql = document.getElementById("customSqlInput").value;
      const out = document.getElementById("customSqlResult");
      try {
        const resp = await fetch("/api/sql", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ sql })
        });
        const data = await resp.json();
        if (data.error) {
          out.innerHTML = `<div class="sql-pill" style="border-color:var(--danger); color:#fca5a5;">${data.error}</div>`;
          return;
        }
        out.innerHTML = `<div class="step-body">X-Request-ID: ${data.request_id} | Rows: ${data.row_count}\n${JSON.stringify(data.rows, null, 2)}</div>`;
      } catch (e) {
        out.innerHTML = `<div class="sql-pill">Static preview mode: run <code>python3 -m agent.main --serve</code> to execute live interactive SQL queries.</div>`;
      }
    }

    function renderAll() {
      document.getElementById("activeModePill").textContent = `Mode: ${currentTrace.execution_mode}`;
      renderCaseTabs();
      renderKPIs();
      renderSources();
      renderAgentTimeline();
      renderConflictsAndReport();
      renderSubTab();
    }

    document.getElementById("btnReplay").addEventListener("click", () => {
      if (replayTimer) clearInterval(replayTimer);
      visibleSteps = 1;
      renderAgentTimeline();
      replayTimer = setInterval(() => {
        if (visibleSteps < currentTrace.agent_collaboration_trace.length) {
          visibleSteps += 1;
          renderAgentTimeline();
        } else {
          clearInterval(replayTimer);
          replayTimer = null;
        }
      }, 650);
    });

    document.getElementById("btnRun").addEventListener("click", async () => {
      const q = document.getElementById("queryInput").value.trim();
      const btn = document.getElementById("btnRun");
      btn.textContent = "Running Nemotron & Zetaris...";
      try {
        const resp = await fetch("/api/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ case_id: currentCaseId, question: q })
        });
        if (resp.ok) {
          currentTrace = await resp.json();
          EMBEDDED_DATA.traces[currentCaseId] = currentTrace;
          visibleSteps = currentTrace.agent_collaboration_trace.length;
          renderAll();
        }
      } catch (_) {
        // Offline static fallback: replay embedded trace
        visibleSteps = currentTrace.agent_collaboration_trace.length;
        renderAll();
      } finally {
        btn.textContent = "Run Reconciliation Loop";
      }
    });

    document.querySelectorAll(".subtab-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".subtab-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        currentSubTab = btn.dataset.tab;
        renderSubTab();
      });
    });

    selectCase("CASE-01");
  </script>
</body>
</html>
"""

DECK_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Switchyard Slide Deck | Open Agent Hackathon 2026</title>
  <style>
    :root {
      --bg: #090d14;
      --card: #111724;
      --border: #243049;
      --text: #f1f5f9;
      --muted: #94a3b8;
      --nvidia: #76b900;
      --accent: #38bdf8;
      --zetaris: #818cf8;
      --amber: #fbbf24;
      --mono: "JetBrains Mono", Menlo, Consolas, monospace;
      --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: var(--sans);
      padding: 32px 24px 64px;
    }
    .deck-header {
      max-width: 1120px;
      margin: 0 auto 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 16px;
    }
    .slide {
      max-width: 1120px;
      margin: 0 auto 28px;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 36px 42px;
      position: relative;
    }
    .slide-num {
      font-family: var(--mono);
      font-size: 12px;
      color: var(--nvidia);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
      font-weight: 700;
    }
    .slide h2 {
      font-size: 26px;
      margin-bottom: 16px;
      letter-spacing: -0.02em;
    }
    .slide p {
      color: #cbd5e1;
      font-size: 15px;
      line-height: 1.6;
      margin-bottom: 14px;
    }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 16px; }
    .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 16px; }
    .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-top: 16px; }
    .box {
      background: #0b101b;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px;
    }
    .box h3 {
      font-size: 15px;
      color: var(--accent);
      margin-bottom: 8px;
      font-family: var(--mono);
    }
    .box ul { padding-left: 18px; color: #cbd5e1; font-size: 13.5px; line-height: 1.55; }
    .box li { margin-bottom: 6px; }
    code {
      font-family: var(--mono);
      font-size: 12px;
      background: rgba(56, 189, 248, 0.12);
      color: #7dd3fc;
      padding: 2px 6px;
      border-radius: 4px;
    }
    .btn-back {
      padding: 8px 16px;
      border-radius: 7px;
      background: var(--nvidia);
      color: #080c12;
      font-weight: 700;
      text-decoration: none;
      font-size: 13px;
    }
    pre.arch {
      font-family: var(--mono);
      font-size: 12px;
      background: #070a10;
      border: 1px solid var(--border);
      padding: 16px;
      border-radius: 8px;
      overflow-x: auto;
      color: #a3e635;
      line-height: 1.45;
    }
  </style>
</head>
<body>
  <div class="deck-header">
    <div>
      <h1 style="font-size:22px;">Switchyard: Presentation Deck</h1>
      <div style="color:var(--muted); font-size:13px;">Open Agent Hackathon 2026 · Track 1: Solving Fragmented Intelligence · NVIDIA Nemotron DGX Spark Award</div>
    </div>
    <a href="/" class="btn-back">Back to Live Command Center</a>
  </div>

  <!-- Slide 1: Problem & Target Users -->
  <section class="slide">
    <div class="slide-num">Slide 01 / 08 · Problem & Target Users</div>
    <h2>Why Factory Lines Stop Even When the ERP Shows "Shipped On Time"</h2>
    <p>
      Target User: <strong>Operations & Supply-Chain Resilience Leads</strong> managing high-value automotive and power-electronics manufacturing lines ($52,000 to $78,000/hr downtime cost).
    </p>
    <div class="grid-2">
      <div class="box">
        <h3>The Fragmented Data Trap</h3>
        <ul>
          <li><strong>ERP (`zetaris_erp.purchase_orders`):</strong> Trusts vendor EDI 856 ASNs that mark `PO-8841` (4,000 SiC modules) as `SHIPPED_ON_TIME`.</li>
          <li><strong>Warehouse WMS (`zetaris_wms.inventory_ledger`):</strong> Physical dock scan shows only 350 unrestricted units (35.9h runway), 800 quarantined, and 2,850 missing.</li>
          <li><strong>Quality QMS (`zetaris_qms.incident_tickets`):</strong> Lab acoustic microscopy proves Sub-lot 992A-2 (800 units) has 18.4% solder-void failure, while Sub-lot 992A-1 (350 units) has 0.0% voids.</li>
          <li><strong>Carrier REST API (`zetaris_rest.carrier_port_feeds`):</strong> Ocean vessel carrying the remaining 2,850 units is held in customs (+96h delay).</li>
        </ul>
      </div>
      <div class="box">
        <h3>One-Sentence APPROACH Problem Statement</h3>
        <p style="font-size:14px; color:#e2e8f0;">
          We built an agent system (<strong>Switchyard</strong>) that helps an <strong>Operations Lead</strong> resolve critical supplier disruptions by querying <strong>four disconnected, conflicting systems through Zetaris</strong>, reconciling contradicting records in a shared <strong>Meterless World Model</strong> with an adversarial <strong>Conflict Critic</strong>, and producing a <strong>single sourced remediation order</strong> powered by <strong>NVIDIA Nemotron models through Meterless Nightshift</strong>.
        </p>
      </div>
    </div>
  </section>

  <!-- Slide 2: The Solution -->
  <section class="slide">
    <div class="slide-num">Slide 02 / 08 · The Solution</div>
    <h2>Switchyard: Autonomous Multi-Source Reconciliation & Remediation</h2>
    <div class="grid-3">
      <div class="box">
        <h3>1. Cross-System Truth</h3>
        <ul>
          <li>Queries ERP, WMS, QMS, Carrier REST feeds, and Qualified Suppliers through Zetaris using single-statement Lightning SQL.</li>
          <li>Flags every cross-source contradiction automatically and resolves them using 3-way empirical corroboration.</li>
        </ul>
      </div>
      <div class="box">
        <h3>2. Adversarial Critic Loop</h3>
        <ul>
          <li>Not a linear pipeline: when the Reconciler proposes a draft after Round 1, the <strong>Conflict Critic Agent</strong> rejects it if QMS lab evidence or backup capacity is missing.</li>
          <li>Forces targeted Round 2 SQL queries before signing off (`APPROVED_WITH_PROVENANCE`).</li>
        </ul>
      </div>
      <div class="box">
        <h3>3. Deterministic Action</h3>
        <ul>
          <li>Sizes exact emergency PO splits across qualified backup suppliers (`2,400 units Silicore Dresden + 1,250 units Pacific Semi`).</li>
          <li>Saves $3.82M in net factory downtime on `PO-8841` alone.</li>
        </ul>
      </div>
    </div>
  </section>

  <!-- Slide 3: Agent Workflow & Architecture -->
  <section class="slide">
    <div class="slide-num">Slide 03 / 08 · Agent Workflow & Architecture</div>
    <h2>Iterative Multi-Agent Graph (Planner ↔ Reconciler ↔ Conflict Critic → Risk → Reporter)</h2>
    <pre class="arch">
 [Operator Question / Alert]
              │
              ▼
 ┌──────────────────────────────────────────────────────────┐
 │ Step 1: Planner & Source Mapper Agent                    │ ◀── Meterless Scout Intent + H-MEM Recall
 │ (Nightshift Lane 1: nvidia/nemotron-3.5-lightning-30b)   │
 └────────────────────────────┬─────────────────────────────┘
                              │ Delegates Round 1 SQL Plan
                              ▼
 ┌──────────────────────────────────────────────────────────┐     POST /api/v1.0/sql-editor/sqls/run
 │ Step 2: Zetaris Reconciler Agent (Round 1 Discovery)     │ ◀─▶ Zetaris (ERP + WMS + Carrier REST)
 │ (Nightshift Lane 1: nvidia/nemotron-3.5-lightning-30b)   │ ──▶ Writes Facts & Flags Conflicts in World Model
 └────────────────────────────┬─────────────────────────────┘
                              │ Submits Provisional Draft (Markovian Capsule)
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │ Step 3: Conflict & Evidence Critic Agent                 │ ──▶ Challenges CONF-01 & CONF-02:
 │ (Nightshift Lane 2: nvidia/nemotron-3.5-super-vl-120b)   │     "Missing QMS lab verdict & backup supplier SQL!"
 └────────────────────────────┬─────────────────────────────┘
                              │ Issues Mandatory Round 2 SQL Directives (Feedback Loop)
                              ▼
 ┌──────────────────────────────────────────────────────────┐     POST /api/v1.0/sql-editor/sqls/run
 │ Step 4: Zetaris Reconciler Agent (Round 2 Resolution)    │ ◀─▶ Zetaris (QMS Tickets + Qualified Suppliers)
 │ (Nightshift Lane 1: nvidia/nemotron-3.5-lightning-30b)   │ ──▶ Resolves 3/3 Conflicts in World Model v15
 └────────────────────────────┬─────────────────────────────┘
                              │ Escalates Verified State (Risk Score >= 65)
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │ Step 5: Risk & Policy Escalation Agent                   │ ──▶ Deterministic Runway & Split-PO Sizing
 │ (Nightshift Lane 2: nvidia/nemotron-3.5-super-vl-120b)   │     Critic Final Verdict: APPROVED_WITH_PROVENANCE
 └────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │ Step 6: Sourced Decision Reporter Agent                  │ ──▶ Cites [table#key] for every claim
 │ (Nightshift Lane 2: nvidia/nemotron-3.5-super-vl-120b)   │ ──▶ Commits new Precedent to Meterless H-MEM
 └──────────────────────────────────────────────────────────┘</pre>
  </section>

  <!-- Slide 4: Technical Stack -->
  <section class="slide">
    <div class="slide-num">Slide 04 / 08 · Technical Stack</div>
    <h2>Three-Layer Sponsor Stack + Zero-Dependency Reproducibility</h2>
    <div class="grid-4">
      <div class="box">
        <h3>01 DATA: Zetaris</h3>
        <ul>
          <li>Zetaris REST SQL API (`POST /sql-editor/sqls/run`) with `Bearer` auth, `X-Org-ID: 1`, and fresh UUID4 `X-Request-ID`.</li>
          <li>Lightning SQL registration (`scripts/register_zetaris_sources.sql`).</li>
          <li>Built-in SQLite federated virtualization for `SAMPLE_MODE=true`.</li>
        </ul>
      </div>
      <div class="box">
        <h3>02 BUILD: Meterless</h3>
        <ul>
          <li>All 4 Meterless Engines implemented in `agent/engines/`: `Scout Intent`, `World Model`, `Markovian`, and `H-MEM`.</li>
          <li>8 automated conformance and end-to-end tests in `tests/`.</li>
        </ul>
      </div>
      <div class="box">
        <h3>03 POWER: Nightshift</h3>
        <ul>
          <li>Meterless Nightshift Runtime (`http://127.0.0.1:8088/v1`) as primary AI provider.</li>
          <li>Sends `meterless-app` and `meterless-scope: user` headers + `/v1/models` discovery.</li>
        </ul>
      </div>
      <div class="box">
        <h3>NVIDIA Nemotron</h3>
        <ul>
          <li>Lane 1 Fast Worker: `nvidia/nemotron-3.5-lightning-30b-a3b`.</li>
          <li>Lane 2 Deep Worker: `nvidia/nemotron-3.5-super-vl-120b-a12b`.</li>
          <li>Per-step `model_handled_by` receipts displayed in UI and logs.</li>
        </ul>
      </div>
    </div>
  </section>

  <!-- Slide 5: How Zetaris & Meterless Were Used -->
  <section class="slide">
    <div class="slide-num">Slide 05 / 08 · How Zetaris & Meterless Were Integrated</div>
    <h2>Deep, Load-Bearing Sponsor Integration (With Passing Conformance Tests)</h2>
    <div class="grid-2">
      <div class="box">
        <h3>Zetaris Unified Semantic Layer</h3>
        <ul>
          <li>Federates 5 operational tables (`zetaris_erp.purchase_orders`, `zetaris_wms.inventory_ledger`, `zetaris_qms.incident_tickets`, `zetaris_rest.carrier_port_feeds`, `zetaris_erp.qualified_suppliers`) plus the starter `pokeapi` validation table.</li>
          <li>Enforces the Zetaris `AGENTS.md` single-statement rule in code and verifies it in `test_01_zetaris_single_statement_rule`.</li>
        </ul>
      </div>
      <div class="box">
        <h3>All 4 Meterless Engines in Working Features</h3>
        <ul>
          <li><strong>Scout Intent:</strong> Classifies disruption type, scores risk (95/100 CRITICAL), and selects Zetaris tables + Nemotron lanes.</li>
          <li><strong>World Model:</strong> Versioned entity/conflict graph (v1 to v15) with optimistic concurrency control (`ConcurrencyConflictError`).</li>
          <li><strong>Markovian:</strong> Compresses 6-step context from 7,612 naive tokens to 1,216 bounded tokens (<strong>84.0% reduction</strong>).</li>
          <li><strong>H-MEM:</strong> Recalls Q3 supplier precedents before the run and commits newly verified remediation rules to disk after the run.</li>
        </ul>
      </div>
    </div>
  </section>

  <!-- Slide 6: What Is Unique About Our Sponsor Tech Usage -->
  <section class="slide">
    <div class="slide-num">Slide 06 / 08 · Unique Innovation with Sponsor Technologies</div>
    <h2>Dual-Lane NVIDIA Nemotron Routing + Markovian-Bounded Critic Loops</h2>
    <div class="grid-2">
      <div class="box">
        <h3>1. Hardware-Aware Dual Nemotron Lanes</h3>
        <ul>
          <li>Instead of routing every agent turn to a single model, Switchyard pairs **Nemotron 3.5 Lightning 30B** (high-speed tool calling and Zetaris SQL generation on Lane 1) with **Nemotron 3.5 Super VL 120B** (adversarial Conflict Critic, risk escalation, and final provenance synthesis on Lane 2) through **Meterless Nightshift**.</li>
          <li>Every single agent step emits a signed `ModelReceipt` proving which Nemotron model handled the request.</li>
        </ul>
      </div>
      <div class="box">
        <h3>2. Zero-Clobber World Model + Markovian State</h3>
        <ul>
          <li>Multi-agent loops normally degrade as raw SQL outputs pollute the prompt window. By combining **Meterless World Model** (structured conflict state) with **Meterless Markovian** (bounded carry-over capsules), our 6-step critic loop cuts prompt tokens by **84%** while maintaining 100% citation accuracy.</li>
        </ul>
      </div>
    </div>
  </section>

  <!-- Slide 7: Product Visuals & Benchmark Results -->
  <section class="slide">
    <div class="slide-num">Slide 07 / 08 · Product Visuals & Benchmark Results Across 5 Cases</div>
    <h2>Verified Across 5 Industrial Disruption Scenarios (`input_examples/` -> `output_examples/`)</h2>
    <div class="box" style="margin-top:12px;">
      <table style="width:100%; border-collapse:collapse; font-family:var(--mono); font-size:12px;">
        <thead>
          <tr style="border-bottom:1px solid var(--border); color:var(--muted); text-align:left;">
            <th style="padding:8px;">Case ID</th>
            <th style="padding:8px;">PO & SKU</th>
            <th style="padding:8px;">Core Cross-Source Conflict</th>
            <th style="padding:8px;">Markovian Savings</th>
            <th style="padding:8px;">Net Loss Avoided</th>
          </tr>
        </thead>
        <tbody>
          <tr style="border-bottom:1px solid var(--border);">
            <td style="padding:8px; color:#a3e635;">CASE-01</td>
            <td style="padding:8px;">PO-8841 (SIC-MOD-1200V)</td>
            <td style="padding:8px;">ERP ON_TIME vs 800 QMS solder-void reject + 96h customs hold</td>
            <td style="padding:8px;">84.0% (6,396t saved)</td>
            <td style="padding:8px; color:#38bdf8;">$3,822,400</td>
          </tr>
          <tr style="border-bottom:1px solid var(--border);">
            <td style="padding:8px; color:#a3e635;">CASE-02</td>
            <td style="padding:8px;">PO-8892 (LFP-CELL-280AH)</td>
            <td style="padding:8px;">ERP DELIVERED vs 43.8C reefer spike & 6.8% DCIR rise on 1,800 cells</td>
            <td style="padding:8px;">83.4% (6,142t saved)</td>
            <td style="padding:8px; color:#38bdf8;">$2,626,500</td>
          </tr>
          <tr style="border-bottom:1px solid var(--border);">
            <td style="padding:8px; color:#a3e635;">CASE-03</td>
            <td style="padding:8px;">PO-8910 (MCU-ADAS-S32)</td>
            <td style="padding:8px;">ERP IN_TRANSIT_CLEAR vs 54h CBP HTS tariff code hold at SFO</td>
            <td style="padding:8px;">82.9% (5,920t saved)</td>
            <td style="padding:8px; color:#38bdf8;">$2,484,250</td>
          </tr>
          <tr style="border-bottom:1px solid var(--border);">
            <td style="padding:8px; color:#a3e635;">CASE-04</td>
            <td style="padding:8px;">PO-8935 (TIM-GEL-500G)</td>
            <td style="padding:8px;">ERP Rev B.1 approved vs 1,500 cartridges Rev B.2 (+14% nozzle pressure)</td>
            <td style="padding:8px;">82.5% (5,810t saved)</td>
            <td style="padding:8px; color:#38bdf8;">$0 (Waiver DEV-8935)</td>
          </tr>
          <tr>
            <td style="padding:8px; color:#a3e635;">CASE-05</td>
            <td style="padding:8px;">PO-8960 (HV-CONT-400A)</td>
            <td style="padding:8px;">ERP 3,200 delivered vs WMS 2,100 RFID count (1,100 phantom ASN gap)</td>
            <td style="padding:8px;">82.8% (5,892t saved)</td>
            <td style="padding:8px; color:#38bdf8;">$2,364,040</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <!-- Slide 8: Future Enhancements -->
  <section class="slide">
    <div class="slide-num">Slide 08 / 08 · Future Enhancements</div>
    <h2>From Decision Support to Closed-Loop ERP & Local DGX Spark Execution</h2>
    <div class="grid-3">
      <div class="box">
        <h3>1. Local Nemotron on DGX Spark</h3>
        <ul>
          <li>Run `Nemotron-3.5-Super-VL-120B` and `Nemotron-3.5-Lightning-30B` locally on an <strong>NVIDIA DGX Spark</strong> via Meterless Nightshift with zero cloud latency and full ITAR/air-gapped data sovereignty.</li>
        </ul>
      </div>
      <div class="box">
        <h3>2. Automated EDI 850/860 Write-Back</h3>
        <ul>
          <li>Extend the Risk & Policy Escalation Agent with human-in-the-loop cryptographic sign-off to emit SAP IDoc / EDI 850 split purchase orders directly after reconciliation.</li>
        </ul>
      </div>
      <div class="box">
        <h3>3. Continuous Zetaris Streaming Triggers</h3>
        <ul>
          <li>Subscribe `Scout Intent` to live Zetaris webhook/CDC streams so customs holds or reefer alarms trigger background Nightshift reconciliation before an operator even opens the dashboard.</li>
        </ul>
      </div>
    </div>
  </section>
</body>
</html>
"""


def main() -> None:
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    embedded = load_embedded_data()
    html = HTML_TEMPLATE.replace("__EMBEDDED_DATA_JSON__", json.dumps(embedded))
    (WEB_DIR / "index.html").write_text(html, encoding="utf-8")
    (DOCS_DIR / "deck.html").write_text(DECK_TEMPLATE, encoding="utf-8")
    print(f"Built {WEB_DIR / 'index.html'} ({len(html):,} bytes)")
    print(f"Built {DOCS_DIR / 'deck.html'} ({len(DECK_TEMPLATE):,} bytes)")


if __name__ == "__main__":
    main()

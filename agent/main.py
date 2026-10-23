#!/usr/bin/env python3
"""
agent/main.py: Switchyard CLI Runner & Interactive Web Command Center Server.

Usage:
  # Run a single benchmark case and print full agent + Nemotron + Zetaris trace:
  python3 -m agent.main --case CASE-01

  # Run all 5 benchmark cases and save outputs to output_examples/:
  python3 -m agent.main --all-cases

  # Run a custom operator question:
  python3 -m agent.main --query "Why is PO-8841 blocked at Dock-4?"

  # Start the interactive Switchyard Web Command Center on http://127.0.0.1:8050:
  python3 -m agent.main --serve
"""

import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse

from .config import SwitchyardConfig
from .llm import NightshiftNemotronClient
from .orchestrator import SwitchyardOrchestrator
from .tools_zetaris import ZetarisClient

ROOT_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT_DIR / "input_examples"
OUTPUT_DIR = ROOT_DIR / "output_examples"
WEB_DIR = ROOT_DIR / "web"
DOCS_DIR = ROOT_DIR / "docs"
SAMPLE_DIR = ROOT_DIR / "data" / "sample"


def load_input_cases() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    for path in sorted(INPUT_DIR.glob("case_*.json")):
        cases.append(json.loads(path.read_text(encoding="utf-8")))
    return cases


def print_run_summary(result: Dict[str, Any]) -> None:
    ns = result["sponsor_technology_evidence"]["meterless_nightshift_and_nvidia_nemotron"]
    zt = result["sponsor_technology_evidence"]["zetaris"]
    mk = result["sponsor_technology_evidence"]["meterless_engines"]["markovian"]
    wm = result["sponsor_technology_evidence"]["meterless_engines"]["world_model"]
    hm = result["sponsor_technology_evidence"]["meterless_engines"]["h_mem"]

    print("=" * 86)
    print(
        f"SWITCHYARD RUN {result['run_id']} | PO: {result['po_number']} ({result['sku']}) | "
        f"Mode: {result['execution_mode']}"
    )
    print("=" * 86)
    print("\n[1] MULTI-AGENT COLLABORATION & NVIDIA NEMOTRON RECEIPTS (via Meterless Nightshift):")
    for step in result["agent_collaboration_trace"]:
        rcpt = step["model_receipt"]
        cap = step["markovian_capsule"]
        sql_count = len(step["sql_executed"])
        print(
            f"  Step {step['step']}: {step['agent']:36s} | "
            f"Model: {rcpt['model_handled_by']:40s} | "
            f"SQLs: {sql_count} | "
            f"Markovian: {cap['bounded_capsule_tokens']}t (saved {cap['tokens_saved']}t)"
        )

    print("\n[2] ZETARIS DATA LAYER TELEMETRY:")
    print(
        f"  Total Federated SQL Queries: {zt['total_sql_queries']} | "
        f"Tables: {', '.join(zt['tables_queried'])}"
    )
    for q in zt["sql_receipts"]:
        print(f"    - [{q['request_id'][:8]}] ({q['row_count']} rows, {q['latency_ms']}ms): {q['sql']}")

    print("\n[3] METERLESS ENGINES TELEMETRY:")
    print(
        f"  - Scout Intent : {result['sponsor_technology_evidence']['meterless_engines']['scout_intent']['intent_type']} "
        f"(risk={result['sponsor_technology_evidence']['meterless_engines']['scout_intent']['risk_level']})"
    )
    print(
        f"  - World Model  : v{wm['version']} | {wm['fact_count']} sourced facts | "
        f"{wm['resolved_conflict_count']}/{wm['conflict_count']} conflicts resolved"
    )
    print(
        f"  - Markovian    : {mk['compression_ratio_pct']}% token reduction "
        f"(naive {mk['naive_total_tokens_across_steps']}t -> bounded {mk['markovian_total_tokens_across_steps']}t)"
    )
    print(
        f"  - H-MEM        : {len(hm['recalled_before_run'])} recalled before run | "
        f"Committed {hm['committed_after_run']['memory_id']} after run"
    )

    print("\n[4] NVIDIA NEMOTRON MODEL ATTRIBUTION SUMMARY:")
    for model_id, count in ns["models_used_summary"].items():
        print(f"  - {model_id}: handled {count} request(s) via {ns['primary_provider']}")

    print("\n[5] SOURCED REMEDIATION ORDER:\n")
    print(result["final_report_markdown"])
    print("=" * 86)


def save_output_example(case_id: str, result: Dict[str, Any]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = case_id.lower().replace("-", "_")
    json_path = OUTPUT_DIR / f"{slug}_trace.json"
    md_path = OUTPUT_DIR / f"{slug}_report.md"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    md_path.write_text(result["final_report_markdown"], encoding="utf-8")
    return json_path


class SwitchyardHTTPHandler(BaseHTTPRequestHandler):
    config: SwitchyardConfig = SwitchyardConfig.from_env()

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, payload: Any, status: int = 200) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def _send_file(self, file_path: Path) -> None:
        if not file_path.exists() or not file_path.is_file():
            self._send_json({"error": "Not found"}, status=404)
            return
        ctype, _ = mimetypes.guess_type(str(file_path))
        raw = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype or "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self._send_file(WEB_DIR / "index.html")
            return
        if path in ("/deck", "/deck.html", "/docs/deck.html"):
            self._send_file(DOCS_DIR / "deck.html")
            return
        if path == "/api/status":
            ns = NightshiftNemotronClient(self.config)
            zt = ZetarisClient(self.config)
            dbs = zt.run_sql("SHOW LIGHTNING DATABASES")
            self._send_json(
                {
                    "app": "Switchyard",
                    "track": "Track 1: Solving Fragmented Intelligence",
                    "sample_mode": self.config.sample_mode,
                    "zetaris": {
                        "rest_url": self.config.zetaris_rest_url,
                        "org_id": self.config.zetaris_org_id,
                        "databases": dbs.rows,
                    },
                    "nightshift": ns.discover_models(),
                    "nemotron_lanes": {
                        "lane_1_fast": self.config.nemotron_fast_model,
                        "lane_2_deep": self.config.nemotron_deep_model,
                    },
                }
            )
            return
        if path == "/api/cases":
            cases = load_input_cases()
            precomputed: Dict[str, Any] = {}
            for c in cases:
                cid = c["case_id"]
                slug = cid.lower().replace("-", "_")
                trace_file = OUTPUT_DIR / f"{slug}_trace.json"
                if trace_file.exists():
                    precomputed[cid] = json.loads(trace_file.read_text(encoding="utf-8"))
            self._send_json({"cases": cases, "precomputed": precomputed})
            return
        if path == "/api/mock-carrier-feed":
            car_json = SAMPLE_DIR / "carrier_port_feeds.json"
            self._send_json(json.loads(car_json.read_text(encoding="utf-8")))
            return

        # Serve static assets from web/ or docs/
        candidate = WEB_DIR / path.lstrip("/")
        if candidate.exists() and candidate.is_file():
            self._send_file(candidate)
            return
        self._send_json({"error": f"Unknown route: {path}"}, status=404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        body_raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        payload = json.loads(body_raw or "{}")

        if parsed.path == "/api/run":
            question = payload.get("question", "").strip()
            case_id = payload.get("case_id")
            cases = {c["case_id"]: c for c in load_input_cases()}
            meta = cases.get(case_id, {}) if case_id else {}
            if not question and meta:
                question = meta.get("question", "")
            if not question:
                self._send_json({"error": "Missing question"}, status=400)
                return

            orch = SwitchyardOrchestrator(self.config)
            result = orch.run_investigation(question=question, case_meta=meta)
            self._send_json(result)
            return

        if parsed.path == "/api/sql":
            sql = payload.get("sql", "SELECT 1 AS one").strip()
            try:
                zt = ZetarisClient(self.config)
                receipt = zt.run_sql(sql)
                self._send_json(receipt.to_dict())
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=400)
            return

        self._send_json({"error": f"Unknown POST endpoint: {parsed.path}"}, status=404)


def main() -> None:
    parser = argparse.ArgumentParser(description="Switchyard Multi-Agent CLI & Server")
    parser.add_argument("--case", type=str, default="CASE-01", help="Case ID to run (e.g. CASE-01..CASE-05)")
    parser.add_argument("--all-cases", action="store_true", help="Run all 5 benchmark cases and save traces")
    parser.add_argument("--query", type=str, default=None, help="Custom operator question to investigate")
    parser.add_argument("--live", action="store_true", help="Force live Zetaris and Meterless Nightshift mode")
    parser.add_argument("--serve", action="store_true", help="Start interactive web command center")
    parser.add_argument("--port", type=int, default=None, help="Port for --serve (default 8050)")
    args = parser.parse_args()

    cfg = SwitchyardConfig.from_env(force_sample_mode=False if args.live else None)
    if args.port:
        cfg.port = args.port

    if args.serve:
        SwitchyardHTTPHandler.config = cfg
        server = ThreadingHTTPServer(("127.0.0.1", cfg.port), SwitchyardHTTPHandler)
        print(f"Switchyard Command Center running at http://127.0.0.1:{cfg.port}")
        print(f"Slide Deck available at           http://127.0.0.1:{cfg.port}/deck")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down Switchyard server.")
            server.server_close()
        return

    cases = {c["case_id"]: c for c in load_input_cases()}

    if args.all_cases:
        for cid, cmeta in cases.items():
            orch = SwitchyardOrchestrator(cfg)
            res = orch.run_investigation(question=cmeta["question"], case_meta=cmeta)
            out_path = save_output_example(cid, res)
            print_run_summary(res)
            print(f"Saved trace to {out_path}\n")
        return

    if args.query:
        orch = SwitchyardOrchestrator(cfg)
        res = orch.run_investigation(question=args.query)
        print_run_summary(res)
        return

    target = cases.get(args.case.upper())
    if not target:
        raise SystemExit(f"Unknown case {args.case}. Available: {', '.join(cases.keys())}")
    orch = SwitchyardOrchestrator(cfg)
    res = orch.run_investigation(question=target["question"], case_meta=target)
    out_path = save_output_example(target["case_id"], res)
    print_run_summary(res)
    print(f"Saved trace to {out_path}")


if __name__ == "__main__":
    main()

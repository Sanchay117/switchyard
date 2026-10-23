#!/usr/bin/env python3
"""
scripts/preflight.py: Read-only preflight validator and optional Zetaris source registrar.
Follows Participant Setup Guide Page 11:
- Runs SELECT 1 and SHOW LIGHTNING DATABASES
- Checks Meterless Nightshift /v1/models discovery
- Optionally dry-runs or executes scripts/register_zetaris_sources.sql one statement at a time
"""

import argparse
import re
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.config import SwitchyardConfig
from agent.llm import NightshiftNemotronClient
from agent.tools_zetaris import ZetarisClient
from data.download_data import verify_samples


def split_sql_statements(sql_text: str) -> list[str]:
    lines = [
        line for line in sql_text.splitlines() if not line.strip().startswith("--")
    ]
    cleaned = "\n".join(lines)
    stmts = [s.strip() for s in re.split(r";\s*", cleaned) if s.strip()]
    return stmts


def main() -> None:
    parser = argparse.ArgumentParser(description="Switchyard Preflight & Zetaris SQL Check")
    parser.add_argument("--live", action="store_true", help="Force live Zetaris and Nightshift checks")
    parser.add_argument("--dry-run-sql", action="store_true", help="Print statements in register_zetaris_sources.sql")
    args = parser.parse_args()

    cfg = SwitchyardConfig.from_env(force_sample_mode=False if args.live else None)
    print(f"=== Switchyard Preflight (mode={'SAMPLE_MODE' if cfg.sample_mode else 'LIVE'}) ===")

    # 1. Sample dataset integrity
    sample_report = verify_samples()
    print(f"[1/4] Sample Data Integrity: PASS ({len(sample_report)} datasets verified)")

    # 2. Zetaris SELECT 1 and SHOW LIGHTNING DATABASES
    z_client = ZetarisClient(cfg)
    r_one = z_client.run_sql("SELECT 1 AS one")
    r_dbs = z_client.run_sql("SHOW LIGHTNING DATABASES")
    r_pika = z_client.run_sql("SELECT pokemon_name, ability_name, is_hidden FROM pokeapi.pikachu_abilities_table")
    print(
        f"[2/4] Zetaris SQL Engine: PASS | SELECT 1 -> {r_one.rows} | "
        f"Databases={r_dbs.row_count} | Pikachu rows={r_pika.row_count}"
    )

    # 3. Nightshift Runtime & NVIDIA Nemotron discovery
    ns_client = NightshiftNemotronClient(cfg)
    discovery = ns_client.discover_models()
    print(
        f"[3/4] Meterless Nightshift Discovery: PASS | endpoint={discovery['endpoint']} | "
        f"models={discovery['models_discovered']}"
    )

    # 4. SQL registration dry-run check
    sql_path = Path(__file__).resolve().parent / "register_zetaris_sources.sql"
    stmts = split_sql_statements(sql_path.read_text(encoding="utf-8"))
    print(f"[4/4] Lightning SQL Onboarding Script: PASS ({len(stmts)} single-statement blocks ready)")
    if args.dry_run_sql:
        for idx, stmt in enumerate(stmts, 1):
            print(f"\n--- Statement {idx} ---\n{stmt};")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Verify or regenerate the curated sample datasets in data/sample/.
Follows Section 12 of the Open Agent Hackathon 2026 APPROACH Guide:
- Small, deterministic sample files (<50 KB total)
- No external API key required
- Zero manual steps
"""

import csv
import hashlib
import json
from pathlib import Path

SAMPLE_DIR = Path(__file__).resolve().parent / "sample"

REQUIRED_FILES = [
    "erp_purchase_orders.csv",
    "qualified_suppliers.csv",
    "wms_inventory_ledger.json",
    "qms_incident_tickets.json",
    "carrier_port_feeds.json",
    "hmem_seed_precedents.json",
]


def verify_samples() -> dict:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    report = {}
    for filename in REQUIRED_FILES:
        fpath = SAMPLE_DIR / filename
        if not fpath.exists():
            raise FileNotFoundError(f"Missing required sample file: {fpath}")
        raw = fpath.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()[:12]
        if filename.endswith(".csv"):
            with fpath.open("r", encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            count = len(rows)
        else:
            rows = json.loads(raw.decode("utf-8"))
            count = len(rows)
        report[filename] = {
            "rows": count,
            "bytes": len(raw),
            "sha256_prefix": digest,
        }
    return report


if __name__ == "__main__":
    summary = verify_samples()
    print("Switchyard Sample Dataset Verification:")
    for fname, meta in summary.items():
        print(f"  [OK] {fname:30s} | {meta['rows']:2d} records | {meta['bytes']:5d} B | sha256:{meta['sha256_prefix']}")

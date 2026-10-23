# Switchyard Data Layer Documentation (`data/README.md`)

This directory holds the curated, lightweight sample datasets served through **Zetaris** (and used by `SAMPLE_MODE=true` for offline reproducibility during judging).

## 1. Data Sources Overview

Switchyard demonstrates **Track 1: Solving Fragmented Intelligence** by querying **four disconnected, conflicting operational data sources** plus a qualified backup supplier directory through Zetaris:

| Source Table in Zetaris | Local Sample File | Records | Format | What It Represents & Why It Disagrees |
| :--- | :--- | :--- | :--- | :--- |
| `zetaris_erp.purchase_orders` | `data/sample/erp_purchase_orders.csv` | 5 POs | CSV / Relational | Enterprise ERP purchase order master. Reflects vendor-submitted EDI 856 ASNs that frequently over-report on-time status (`SHIPPED_ON_TIME`, `DELIVERED_COMPLETE`). |
| `zetaris_wms.inventory_ledger` | `data/sample/wms_inventory_ledger.json` | 5 Ledgers | JSON / Postgres | Physical warehouse dock scans, RFID gate counts, quarantined sub-lots, hourly factory burn rates, and line-stop cost per hour. |
| `zetaris_qms.incident_tickets` | `data/sample/qms_incident_tickets.json` | 5 Tickets | JSON / Filestore | Quality Management System tickets containing acoustic/X-ray lab verdicts, sub-lot failure rates, and vendor dispute claims. |
| `zetaris_rest.carrier_port_feeds` | `data/sample/carrier_port_feeds.json` | 5 Feeds | REST API Table | Live customs, ocean bill-of-lading, air waybill, and IoT reefer telemetry feeds registered as a `LIGHTNING REST TABLE` in Zetaris. |
| `zetaris_erp.qualified_suppliers` | `data/sample/qualified_suppliers.csv` | 11 Vendors | CSV / Relational | Approved primary and backup suppliers with expedited air lead times, weekly capacity caps, and historical defect rates. |
| `H-MEM Precedent Store` | `data/sample/hmem_seed_precedents.json` | 3 Rules | JSON | Cross-session hierarchical memory precedents used by the Meterless `H-MEM` engine. |

## 2. Source URL, Licence, and Sensitivity

- **Source URL & Provenance:** Synthetic industrial supply-chain and quality telemetry modeled after standard automotive/power-electronics ERP (SAP IDoc/EDI 856), WMS, QMS (8D/CAPA), and ocean/air carrier API schemas, combined with Zetaris's official `zetaris/getting-started` REST & TPC-H virtualization patterns (`https://github.com/zetaris/getting-started`).
- **Licence & Usage Note:** Released under the MIT License for open hackathon, benchmarking, and prototype evaluation.
- **Privacy & Sensitivity:** Contains **zero** personal identifiable information (PII), zero confidential corporate records, and zero restricted data.

## 3. How Sources Are Registered in Zetaris

All sources are registered in Zetaris using **Zetaris Lightning SQL** (`scripts/register_zetaris_sources.sql`):
1. `CREATE LIGHTNING DATABASE SWITCHYARD_ERP` and `CREATE LIGHTNING DATABASE SWITCHYARD_REST` register the underlying relational, filestore, and REST endpoints.
2. `CREATE SCHEMASTORE CONTAINER switchyard` creates the Unified Semantic Layer (USL) container.
3. `CREATE LIGHTNING REST TABLE carrier_port_feeds` registers the live carrier/customs JSON API directly inside Zetaris so agents can join REST telemetry with ERP and WMS tables in standard SQL.
4. `CREATE SCHEMASTORE VIEW unified_disruption_view` exposes a cross-source federated view.

To register the tables against a running local Zetaris Docker instance (`http://localhost:8888/api/v1.0`), run:
```bash
python3 scripts/preflight.py --register
```
Or run the statements in `scripts/register_zetaris_sources.sql` one statement at a time inside the Zetaris SQL Editor (`http://localhost:3000`).

## 4. Regenerating or Downloading the Sample Data

To verify, reset, or regenerate all sample files in `data/sample/` with deterministic checksums:
```bash
python3 data/download_data.py
```

## 5. Limitations

- The curated dataset is intentionally bounded to 5 high-conflict purchase orders (`PO-8841`, `PO-8892`, `PO-8910`, `PO-8935`, `PO-8960`) and 11 qualified supplier records so that every multi-agent run completes in under 60 seconds and remains 100% auditable by judges.
- In `SAMPLE_MODE=true` (the default when Zetaris Docker or Nightshift is offline), `agent/tools_zetaris.py` loads these exact files into an in-memory SQL virtualization engine so all agent `run_sql` tool calls execute real SQL queries identically to a live Zetaris container.

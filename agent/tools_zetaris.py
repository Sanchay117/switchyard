"""
Layer 01 (DATA): Zetaris Data Layer Connector & Federated SQL Virtualizer.
Follows Participant Setup Guide Pages 10, 11, 22, and 24:
- Sends one SQL statement per call to POST {ZETARIS_REST_URL}/sql-editor/sqls/run
- Uses Authorization: Bearer <ZETARIS_API_KEY>, X-Org-ID: <org_id>, and a fresh
  UUID4 X-Request-ID header on every request.
- Provides a built-in SQLite federated virtualization fallback for SAMPLE_MODE=true
  (required by Section 12 of the Hackathon Overview so judges can run the full
  SQL pipeline without Docker or live credentials).
"""

import csv
import json
import sqlite3
import time
import urllib.request
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List

from .config import SwitchyardConfig

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample"


@dataclass
class ZetarisQueryReceipt:
    query_id: str
    request_id: str
    sql: str
    source_tables_touched: List[str]
    execution_mode: str  # "zetaris-rest-live" | "zetaris-virtualized-sample"
    row_count: int
    latency_ms: float
    columns: List[str]
    rows: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ZetarisClient:
    """
    Executes single-statement SQL queries against Zetaris over REST, with
    automatic or configured SAMPLE_MODE SQLite federation over data/sample/.
    """

    KNOWN_TABLES = [
        "zetaris_erp.purchase_orders",
        "zetaris_erp.qualified_suppliers",
        "zetaris_wms.inventory_ledger",
        "zetaris_qms.incident_tickets",
        "zetaris_rest.carrier_port_feeds",
        "pokeapi.pikachu_abilities_table",
    ]

    def __init__(self, config: SwitchyardConfig | None = None) -> None:
        self.config = config or SwitchyardConfig.from_env()
        self.receipts: List[ZetarisQueryReceipt] = []
        self._conn = self._init_sample_sqlite()

    def _init_sample_sqlite(self) -> sqlite3.Connection:
        """
        Builds an in-memory SQLite connection with attached schemas matching
        Zetaris Lightning namespaces:
          zetaris_erp, zetaris_wms, zetaris_qms, zetaris_rest, switchyard, pokeapi
        """
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        for schema in ("zetaris_erp", "zetaris_wms", "zetaris_qms", "zetaris_rest", "switchyard", "pokeapi"):
            cur.execute(f"ATTACH DATABASE ':memory:' AS {schema}")

        # 1. zetaris_erp.purchase_orders
        cur.execute(
            """
            CREATE TABLE zetaris_erp.purchase_orders (
                po_number TEXT PRIMARY KEY,
                sku TEXT,
                part_name TEXT,
                production_line TEXT,
                supplier_id TEXT,
                supplier_name TEXT,
                ordered_qty INTEGER,
                unit_cost_usd REAL,
                erp_status TEXT,
                promised_eta TEXT,
                incoterms TEXT,
                buyer_notes TEXT
            )
            """
        )
        po_csv = SAMPLE_DIR / "erp_purchase_orders.csv"
        if po_csv.exists():
            with po_csv.open("r", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    cur.execute(
                        """
                        INSERT INTO zetaris_erp.purchase_orders VALUES (
                            :po_number, :sku, :part_name, :production_line,
                            :supplier_id, :supplier_name, :ordered_qty, :unit_cost_usd,
                            :erp_status, :promised_eta, :incoterms, :buyer_notes
                        )
                        """,
                        {
                            **row,
                            "ordered_qty": int(row["ordered_qty"]),
                            "unit_cost_usd": float(row["unit_cost_usd"]),
                        },
                    )

        # 2. zetaris_erp.qualified_suppliers
        cur.execute(
            """
            CREATE TABLE zetaris_erp.qualified_suppliers (
                supplier_id TEXT,
                supplier_name TEXT,
                sku TEXT,
                qualified_status TEXT,
                max_weekly_capacity INTEGER,
                expedite_lead_days INTEGER,
                expedite_unit_cost_usd REAL,
                historical_defect_rate_pct REAL,
                region TEXT,
                compliance_tier TEXT
            )
            """
        )
        sup_csv = SAMPLE_DIR / "qualified_suppliers.csv"
        if sup_csv.exists():
            with sup_csv.open("r", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    cur.execute(
                        """
                        INSERT INTO zetaris_erp.qualified_suppliers VALUES (
                            :supplier_id, :supplier_name, :sku, :qualified_status,
                            :max_weekly_capacity, :expedite_lead_days, :expedite_unit_cost_usd,
                            :historical_defect_rate_pct, :region, :compliance_tier
                        )
                        """,
                        {
                            **row,
                            "max_weekly_capacity": int(row["max_weekly_capacity"]),
                            "expedite_lead_days": int(row["expedite_lead_days"]),
                            "expedite_unit_cost_usd": float(row["expedite_unit_cost_usd"]),
                            "historical_defect_rate_pct": float(row["historical_defect_rate_pct"]),
                        },
                    )

        # 3. zetaris_wms.inventory_ledger
        cur.execute(
            """
            CREATE TABLE zetaris_wms.inventory_ledger (
                ledger_id TEXT PRIMARY KEY,
                po_number TEXT,
                sku TEXT,
                production_line TEXT,
                received_qty INTEGER,
                usable_unrestricted_qty INTEGER,
                quarantined_qty INTEGER,
                in_transit_deficit_qty INTEGER,
                lot_code TEXT,
                dock_location TEXT,
                hourly_line_burn_rate INTEGER,
                line_runway_hours REAL,
                downtime_cost_per_hour_usd INTEGER,
                last_scan_utc TEXT,
                warehouse_note TEXT
            )
            """
        )
        wms_json = SAMPLE_DIR / "wms_inventory_ledger.json"
        if wms_json.exists():
            for row in json.loads(wms_json.read_text(encoding="utf-8")):
                cur.execute(
                    """
                    INSERT INTO zetaris_wms.inventory_ledger VALUES (
                        :ledger_id, :po_number, :sku, :production_line,
                        :received_qty, :usable_unrestricted_qty, :quarantined_qty,
                        :in_transit_deficit_qty, :lot_code, :dock_location,
                        :hourly_line_burn_rate, :line_runway_hours,
                        :downtime_cost_per_hour_usd, :last_scan_utc, :warehouse_note
                    )
                    """,
                    row,
                )

        # 4. zetaris_qms.incident_tickets
        cur.execute(
            """
            CREATE TABLE zetaris_qms.incident_tickets (
                ticket_id TEXT PRIMARY KEY,
                po_number TEXT,
                sku TEXT,
                supplier_id TEXT,
                lot_code TEXT,
                severity TEXT,
                qms_status TEXT,
                defect_rate_pct REAL,
                failure_mode TEXT,
                sublot_breakdown TEXT,
                supplier_dispute_claim TEXT,
                lab_verdict TEXT,
                inspector_action_required TEXT
            )
            """
        )
        qms_json = SAMPLE_DIR / "qms_incident_tickets.json"
        if qms_json.exists():
            for row in json.loads(qms_json.read_text(encoding="utf-8")):
                cur.execute(
                    """
                    INSERT INTO zetaris_qms.incident_tickets VALUES (
                        :ticket_id, :po_number, :sku, :supplier_id, :lot_code,
                        :severity, :qms_status, :defect_rate_pct, :failure_mode,
                        :sublot_breakdown, :supplier_dispute_claim, :lab_verdict,
                        :inspector_action_required
                    )
                    """,
                    {
                        **row,
                        "inspector_action_required": row.get("inspector_action_required")
                        or row.get("inspector_Action_required", ""),
                    },
                )

        # 5. zetaris_rest.carrier_port_feeds
        cur.execute(
            """
            CREATE TABLE zetaris_rest.carrier_port_feeds (
                feed_id TEXT PRIMARY KEY,
                po_number TEXT,
                vessel_or_flight TEXT,
                origin_port TEXT,
                destination_port TEXT,
                carrier_status TEXT,
                reported_delay_hours INTEGER,
                revised_eta TEXT,
                units_on_conveyance INTEGER,
                telemetry_alert TEXT,
                updated_at_utc TEXT
            )
            """
        )
        car_json = SAMPLE_DIR / "carrier_port_feeds.json"
        if car_json.exists():
            for row in json.loads(car_json.read_text(encoding="utf-8")):
                cur.execute(
                    """
                    INSERT INTO zetaris_rest.carrier_port_feeds VALUES (
                        :feed_id, :po_number, :vessel_or_flight, :origin_port,
                        :destination_port, :carrier_status, :reported_delay_hours,
                        :revised_eta, :units_on_conveyance, :telemetry_alert, :updated_at_utc
                    )
                    """,
                    row,
                )

        # 6. Starter PokeAPI table from Setup Guide 1.8
        cur.execute(
            """
            CREATE TABLE pokeapi.pikachu_abilities_table (
                pokemon_name TEXT,
                ability_name TEXT,
                is_hidden TEXT
            )
            """
        )
        cur.executemany(
            "INSERT INTO pokeapi.pikachu_abilities_table VALUES (?, ?, ?)",
            [("pikachu", "static", "false"), ("pikachu", "lightning-rod", "true")],
        )

        conn.commit()
        return conn

    @staticmethod
    def _validate_single_statement(sql: str) -> str:
        cleaned = sql.strip()
        if cleaned.endswith(";"):
            cleaned = cleaned[:-1].strip()
        if ";" in cleaned:
            raise ValueError(
                "Zetaris AGENTS.md rule violation: send only ONE complete SQL statement per run_sql() call."
            )
        return cleaned

    def _detect_touched_tables(self, sql: str) -> List[str]:
        sql_lower = sql.lower()
        touched = [t for t in self.KNOWN_TABLES if t.lower() in sql_lower]
        if not touched and "show lightning databases" in sql_lower:
            return ["system.lightning_catalog"]
        return touched or ["zetaris.sql_engine"]

    def run_sql(self, sql: str, limit: int = 100) -> ZetarisQueryReceipt:
        """
        Executes a single SQL statement against Zetaris REST API (when live)
        or against the local federated SQLite engine (when in SAMPLE_MODE or offline).
        """
        cleaned_sql = self._validate_single_statement(sql)
        query_id = str(uuid.uuid4())
        request_id = str(uuid.uuid4())
        touched = self._detect_touched_tables(cleaned_sql)
        t0 = time.perf_counter()

        if not self.config.sample_mode:
            try:
                body_bytes = json.dumps(
                    {
                        "queryId": query_id,
                        "sql": cleaned_sql,
                        "source": "SqlEditor",
                        "limit": limit,
                    }
                ).encode("utf-8")
                req = urllib.request.Request(
                    f"{self.config.zetaris_rest_url}/sql-editor/sqls/run",
                    data=body_bytes,
                    headers={
                        "Authorization": f"Bearer {self.config.zetaris_api_key}",
                        "X-Org-ID": self.config.zetaris_org_id,
                        "X-Request-ID": request_id,
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                raw_rows = payload.get("data", [])
                raw_cols = [
                    c.get("name", f"col_{i}") if isinstance(c, dict) else str(c)
                    for i, c in enumerate(payload.get("schema", payload.get("columns", [])))
                ]
                rows_dicts: List[Dict[str, Any]] = []
                for r in raw_rows:
                    if isinstance(r, dict):
                        rows_dicts.append(r)
                    elif isinstance(r, list):
                        cols = raw_cols if len(raw_cols) == len(r) else [f"col_{i}" for i in range(len(r))]
                        rows_dicts.append(dict(zip(cols, r)))
                latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)
                receipt = ZetarisQueryReceipt(
                    query_id=query_id,
                    request_id=request_id,
                    sql=cleaned_sql,
                    source_tables_touched=touched,
                    execution_mode="zetaris-rest-live",
                    row_count=len(rows_dicts),
                    latency_ms=latency_ms,
                    columns=raw_cols or (list(rows_dicts[0].keys()) if rows_dicts else []),
                    rows=rows_dicts,
                )
                self.receipts.append(receipt)
                return receipt
            except Exception:
                # Graceful fallback to virtualized sample engine if live container is unreachable
                pass

        # Virtualized execution (SAMPLE_MODE=true or fallback)
        if cleaned_sql.upper() == "SHOW LIGHTNING DATABASES":
            rows_dicts = [
                {"database_name": "zetaris_erp", "description": "ERP Purchase Orders & Qualified Suppliers"},
                {"database_name": "zetaris_wms", "description": "Warehouse Management & Physical Dock Scans"},
                {"database_name": "zetaris_qms", "description": "Quality Incident Tickets & Lab Acoustic Logs"},
                {"database_name": "zetaris_rest", "description": "Live Carrier & Customs REST Tables"},
                {"database_name": "pokeapi", "description": "Starter PokeAPI REST Table"},
            ]
            cols = ["database_name", "description"]
        else:
            cur = self._conn.cursor()
            cur.execute(cleaned_sql)
            fetched = cur.fetchmany(limit)
            cols = [d[0] for d in cur.description] if cur.description else []
            rows_dicts = [dict(zip(cols, tuple(r))) for r in fetched]

        latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        receipt = ZetarisQueryReceipt(
            query_id=query_id,
            request_id=request_id,
            sql=cleaned_sql,
            source_tables_touched=touched,
            execution_mode="zetaris-virtualized-sample",
            row_count=len(rows_dicts),
            latency_ms=latency_ms,
            columns=cols,
            rows=rows_dicts,
        )
        self.receipts.append(receipt)
        return receipt

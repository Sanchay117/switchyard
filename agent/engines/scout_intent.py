"""
Meterless Engine 1: Scout Intent (agent/engines/scout_intent.py)
Follows the Meterless Scout Intent specification (meterless.ai/engines.html):
- Early goal and intent recognition on incoming user/event payloads
- Operational risk and constraint detection before deep agent execution
- Deterministic routing to the required Zetaris tables and Nightshift Nemotron lanes
"""

import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class IntentRoute:
    intent_type: str
    risk_level: str
    risk_score: int
    po_number: str | None
    sku: str | None
    production_line: str | None
    target_zetaris_tables: List[str]
    primary_lane: str
    primary_nemotron_model: str
    verification_lane: str
    verification_nemotron_model: str
    require_risk_escalation_check: bool
    routing_rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ScoutIntentEngine:
    """
    Meterless Scout Intent Engine: classifies operator requests, extracts target
    identifiers, evaluates operational blast-radius risk, and routes to the right
    Zetaris SQL tables and Nightshift NVIDIA Nemotron model lanes.
    """

    PO_MAP = {
        "PO-8841": ("SIC-MOD-1200V", "Line-B Inverter"),
        "PO-8892": ("LFP-CELL-280AH", "Line-A Pack Assembly"),
        "PO-8910": ("MCU-ADAS-S32", "Line-C Controller"),
        "PO-8935": ("TIM-GEL-500G", "Line-A Pack Assembly"),
        "PO-8960": ("HV-CONT-400A", "Line-B Inverter"),
    }

    SKU_TO_PO = {v[0]: k for k, v in PO_MAP.items()}

    def __init__(
        self,
        fast_model: str = "nvidia/nemotron-3.5-lightning-30b-a3b",
        deep_model: str = "nvidia/nemotron-3.5-super-vl-120b-a12b",
    ):
        self.fast_model = fast_model
        self.deep_model = deep_model

    def evaluate(self, query: str, context_hint: Dict[str, Any] | None = None) -> IntentRoute:
        hint = context_hint or {}
        text_upper = query.upper()
        text_lower = query.lower()

        # 1. Extract PO number and SKU
        po_match = re.search(r"PO-\d{4}", text_upper)
        po_number = hint.get("po_number") or (po_match.group(0) if po_match else None)

        sku = hint.get("sku")
        if not sku:
            for candidate_sku in self.SKU_TO_PO:
                if candidate_sku in text_upper:
                    sku = candidate_sku
                    break

        if po_number and not sku and po_number in self.PO_MAP:
            sku = self.PO_MAP[po_number][0]
        elif sku and not po_number and sku in self.SKU_TO_PO:
            po_number = self.SKU_TO_PO[sku]

        # Default to PO-8841 if an open-ended supply query doesn't name a specific PO
        if not po_number:
            po_number = "PO-8841"
            sku = self.PO_MAP[po_number][0]

        production_line = hint.get("production_line") or self.PO_MAP.get(po_number, (sku, "Line-B Inverter"))[1]

        # 2. Classify intent category
        if any(k in text_lower for k in ("reefer", "thermal", "temperature", "dcir", "cold-bay", "impedance")):
            intent_type = "cold_chain_thermal_audit"
        elif any(k in text_lower for k in ("customs", "hts", "tariff", "broker", "cbp")):
            intent_type = "customs_hold_mitigation"
        elif any(k in text_lower for k in ("rev b", "viscosity", "formulation", "spec", "waiver", "gel")):
            intent_type = "spec_drift_engineering_waiver"
        elif any(k in text_lower for k in ("phantom", "accounts payable", "over-report", "missing", "rfid", "bin-b14")):
            intent_type = "phantom_inventory_reconciliation"
        elif any(k in text_lower for k in ("catalog", "schema", "list tables", "health")):
            intent_type = "catalog_inspection"
        else:
            intent_type = "multi_source_disruption_reconciliation"

        # 3. Score operational risk and select Zetaris tables
        risk_score = 45
        if any(w in text_lower for w in ("line-stop", "quarantine", "shortage", "critical", "hours", "blocked", "runway")):
            risk_score += 35
        if any(w in text_lower for w in ("void", "defect", "43.8c", "customs", "phantom", "disagree", "conflict")):
            risk_score += 15
        risk_score = min(risk_score, 98)

        if intent_type == "catalog_inspection":
            risk_level = "LOW"
            risk_score = 15
            tables = ["zetaris_erp.purchase_orders"]
            require_escalation = False
        else:
            risk_level = "CRITICAL" if risk_score >= 80 else ("HIGH" if risk_score >= 65 else "MEDIUM")
            tables = [
                "zetaris_erp.purchase_orders",
                "zetaris_wms.inventory_ledger",
                "zetaris_qms.incident_tickets",
                "zetaris_rest.carrier_port_feeds",
                "zetaris_erp.qualified_suppliers",
            ]
            require_escalation = risk_score >= 65

        rationale = (
            f"Scout Intent classified request as '{intent_type}' for {po_number} ({sku} on {production_line}) "
            f"with risk={risk_level} ({risk_score}/100). Routed SQL discovery to Lane 1 ({self.fast_model}) across "
            f"{len(tables)} Zetaris tables and assigned adversarial conflict verification to Lane 2 ({self.deep_model})."
        )

        return IntentRoute(
            intent_type=intent_type,
            risk_level=risk_level,
            risk_score=risk_score,
            po_number=po_number,
            sku=sku,
            production_line=production_line,
            target_zetaris_tables=tables,
            primary_lane="Lane 1: Fast Worker",
            primary_nemotron_model=self.fast_model,
            verification_lane="Lane 2: Deep Worker",
            verification_nemotron_model=self.deep_model,
            require_risk_escalation_check=require_escalation,
            routing_rationale=rationale,
        )

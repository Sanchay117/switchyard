"""
Meterless Engine 4: H-MEM (agent/engines/h_mem.py)
Follows the Meterless H-MEM (Hierarchical Memory Engine) specification:
- Manages 3 memory tiers: EPISODIC (session observations), SEMANTIC (supplier
  and chemistry rules), and PRECEDENT (verified cross-session operational decisions).
- Persists memories to disk so earlier session decisions are recalled and applied
  automatically in later runs with full provenance citations.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

DEFAULT_SEED_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "sample" / "hmem_seed_precedents.json"


@dataclass
class MemoryRecord:
    memory_id: str
    tier: str  # EPISODIC | SEMANTIC | PRECEDENT
    supplier_id: str
    supplier_name: str
    sku_family: str
    session_date: str
    incident_summary: str
    learned_rule: str
    provenance: str
    approved_by: str = "Switchyard Autonomous Auditor"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HMemEngine:
    """
    Meterless H-MEM (Hierarchical Memory Engine): mines, stores, and retrieves
    multi-tiered operational memory across sessions.
    """

    def __init__(self, storage_path: Path | None = None, seed_path: Path | None = None) -> None:
        self.seed_path = seed_path or DEFAULT_SEED_PATH
        self.storage_path = storage_path
        self.memories: List[MemoryRecord] = []
        self._load()

    def _load(self) -> None:
        records_raw: List[Dict[str, Any]] = []
        if self.storage_path and self.storage_path.exists():
            records_raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
        elif self.seed_path and self.seed_path.exists():
            records_raw = json.loads(self.seed_path.read_text(encoding="utf-8"))

        self.memories = [
            MemoryRecord(
                memory_id=r["memory_id"],
                tier=r.get("tier", "PRECEDENT"),
                supplier_id=r.get("supplier_id", "ANY"),
                supplier_name=r.get("supplier_name", "Unknown"),
                sku_family=r.get("sku_family", "ANY"),
                session_date=r.get("session_date", "2026-10-23"),
                incident_summary=r["incident_summary"],
                learned_rule=r["learned_rule"],
                provenance=r.get("provenance", "Session Memory"),
                approved_by=r.get("approved_by", "Switchyard Autonomous Auditor"),
            )
            for r in records_raw
        ]

    def _save(self) -> None:
        if self.storage_path:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            self.storage_path.write_text(
                json.dumps([m.to_dict() for m in self.memories], indent=2),
                encoding="utf-8",
            )

    def recall(
        self,
        supplier_id: str | None = None,
        sku: str | None = None,
        query_text: str = "",
        top_k: int = 3,
    ) -> List[MemoryRecord]:
        scored: List[tuple[int, MemoryRecord]] = []
        q_upper = query_text.upper()
        sku_upper = (sku or "").upper()
        sup_upper = (supplier_id or "").upper()

        for mem in self.memories:
            score = 0
            if sup_upper and mem.supplier_id.upper() == sup_upper:
                score += 50
            if sku_upper and (
                sku_upper.startswith(mem.sku_family.upper())
                or mem.sku_family.upper() in sku_upper
            ):
                score += 45
            if mem.supplier_name.upper() in q_upper:
                score += 35
            if mem.sku_family.upper() in q_upper:
                score += 30
            # Keyword overlap
            for token in ("APEX", "SILICORE", "VOLTGRID", "LFP", "SIC", "VOID", "DCIR", "REEFER", "ASN"):
                if token in q_upper and (
                    token in mem.learned_rule.upper() or token in mem.incident_summary.upper()
                ):
                    score += 10
            if score > 0:
                scored.append((score, mem))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

    def commit_memory(
        self,
        tier: str,
        supplier_id: str,
        supplier_name: str,
        sku_family: str,
        incident_summary: str,
        learned_rule: str,
        provenance: str,
    ) -> MemoryRecord:
        # Deduplicate if identical rule already exists for this supplier & SKU
        for existing in self.memories:
            if (
                existing.supplier_id == supplier_id
                and existing.sku_family == sku_family
                and existing.learned_rule == learned_rule
            ):
                return existing

        mem = MemoryRecord(
            memory_id=f"HMEM-{tier[:4]}-{len(self.memories) + 1:03d}",
            tier=tier,
            supplier_id=supplier_id,
            supplier_name=supplier_name,
            sku_family=sku_family,
            session_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            incident_summary=incident_summary,
            learned_rule=learned_rule,
            provenance=provenance,
        )
        self.memories.append(mem)
        self._save()
        return mem

    def summary(self) -> Dict[str, Any]:
        return {
            "total_memories": len(self.memories),
            "by_tier": {
                tier: sum(1 for m in self.memories if m.tier == tier)
                for tier in ("EPISODIC", "SEMANTIC", "PRECEDENT")
            },
            "records": [m.to_dict() for m in self.memories],
        }

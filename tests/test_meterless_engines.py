"""
Conformance and Feature Tests for all 4 Meterless Engines:
1. Scout Intent (agent/engines/scout_intent.py)
2. World Model  (agent/engines/world_model.py)
3. Markovian    (agent/engines/markovian.py)
4. H-MEM        (agent/engines/h_mem.py)

Run with:
  python3 -m unittest discover -s tests -v
"""

import tempfile
import unittest
from pathlib import Path

from agent.engines import (
    ScoutIntentEngine,
    WorldModelEngine,
    MarkovianEngine,
    HMemEngine,
)
from agent.engines.world_model import ConcurrencyConflictError


class TestMeterlessEngines(unittest.TestCase):
    def test_01_scout_intent_routing_and_risk(self) -> None:
        engine = ScoutIntentEngine(
            fast_model="nvidia/nemotron-3.5-lightning-30b-a3b",
            deep_model="nvidia/nemotron-3.5-super-vl-120b-a12b",
        )
        route = engine.evaluate(
            "ERP says PO-8841 is SHIPPED_ON_TIME, but Dock-4 quarantined 800 units due to solder void defects and we face a line-stop."
        )
        self.assertEqual(route.po_number, "PO-8841")
        self.assertEqual(route.sku, "SIC-MOD-1200V")
        self.assertEqual(route.risk_level, "CRITICAL")
        self.assertGreaterEqual(route.risk_score, 80)
        self.assertTrue(route.require_risk_escalation_check)
        self.assertEqual(route.primary_nemotron_model, "nvidia/nemotron-3.5-lightning-30b-a3b")
        self.assertEqual(route.verification_nemotron_model, "nvidia/nemotron-3.5-super-vl-120b-a12b")
        self.assertIn("zetaris_qms.incident_tickets", route.target_zetaris_tables)

        # Test thermal excursion classification on PO-8892
        route_thermal = engine.evaluate(
            "Check PO-8892 reefer temperature excursion and DCIR impedance rise in Cold-Bay-2."
        )
        self.assertEqual(route_thermal.po_number, "PO-8892")
        self.assertEqual(route_thermal.intent_type, "cold_chain_thermal_audit")

    def test_02_world_model_shared_state_and_concurrency(self) -> None:
        wm = WorldModelEngine()
        v1 = wm.register_entity(
            entity_id="PO-8841",
            entity_type="PurchaseOrder",
            attributes={"sku": "SIC-MOD-1200V"},
            agent_name="Planner",
        )
        self.assertEqual(v1, 1)

        # Parallel agent with stale version must raise ConcurrencyConflictError
        wm.record_fact(
            entity_id="PO-8841",
            source_table="zetaris_erp.purchase_orders",
            record_key="PO-8841",
            attribute="ordered_qty",
            value=4000,
            agent_name="Reconciler",
            sql_used="SELECT ordered_qty FROM zetaris_erp.purchase_orders WHERE po_number='PO-8841'",
            expected_version=1,
        )
        with self.assertRaises(ConcurrencyConflictError):
            wm.record_fact(
                entity_id="PO-8841",
                source_table="zetaris_wms.inventory_ledger",
                record_key="WMS-701",
                attribute="received_qty",
                value=1150,
                agent_name="StaleAgent",
                sql_used="SELECT received_qty FROM zetaris_wms.inventory_ledger",
                expected_version=1,  # Stale! Current version is 2
            )

        # Conflict lifecycle: DETECTED -> CHALLENGED_BY_CRITIC -> RESOLVED
        conflict = wm.flag_conflict(
            entity_id="PO-8841",
            dimension="Quantity",
            source_a="zetaris_erp.purchase_orders#PO-8841",
            claim_a="4000 shipped",
            source_b="zetaris_wms.inventory_ledger#WMS-701",
            claim_b="350 usable, 800 quarantined",
            agent_name="Reconciler",
        )
        self.assertEqual(conflict.status, "DETECTED")
        self.assertEqual(len(wm.get_unresolved_conflicts()), 1)

        wm.challenge_conflict(
            conflict.conflict_id,
            critic_notes="Missing QMS lab verification for LOT-992A",
            agent_name="Conflict Critic",
        )
        self.assertEqual(wm.conflicts[conflict.conflict_id].status, "CHALLENGED_BY_CRITIC")

        wm.resolve_conflict(
            conflict.conflict_id,
            authoritative_source="zetaris_wms.inventory_ledger#WMS-701",
            resolution_explanation="Physical dock scan + QMS-419 acoustic lab test confirm 350 usable.",
            corroborating_sources=["zetaris_qms.incident_tickets#QMS-419"],
            agent_name="Reconciler Round 2",
        )
        self.assertEqual(wm.conflicts[conflict.conflict_id].status, "RESOLVED")
        self.assertEqual(len(wm.get_unresolved_conflicts()), 0)

    def test_03_markovian_bounded_context_compression(self) -> None:
        markovian = MarkovianEngine(max_capsule_tokens=220)
        for i in range(1, 7):
            raw_dump = ("RAW_SQL_LOG_ROW_" * 85) + f" step={i}"
            cap = markovian.transition(
                step_name=f"Step {i}",
                agent_name=f"Agent_{i}",
                raw_step_transcript=raw_dump,
                verified_facts=[f"Fact {j}: verified source record #{j}" for j in range(1, i + 3)],
                active_conflicts=[f"CONF-01 open in step {i}"] if i < 4 else [],
                open_directives=[f"Directive for step {i + 1}"],
            )
            self.assertLessEqual(cap.bounded_capsule_tokens, 250)

        telemetry = markovian.telemetry_summary()
        self.assertEqual(telemetry["steps_completed"], 6)
        self.assertGreater(telemetry["compression_ratio_pct"], 65.0)
        self.assertGreater(telemetry["total_tokens_saved"], 2500)

    def test_04_hmem_cross_session_persistence_and_recall(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store_file = Path(tmpdir) / "hmem_test_store.json"

            # Session 1: Load seed memories and commit a new precedent
            hmem_session_1 = HMemEngine(storage_path=store_file)
            initial_recalled = hmem_session_1.recall(
                supplier_id="SUP-101",
                sku="SIC-MOD-1200V",
                query_text="Apex Wafer Corp solder void",
            )
            self.assertGreaterEqual(len(initial_recalled), 1)
            self.assertEqual(initial_recalled[0].memory_id, "HMEM-PREC-001")

            committed = hmem_session_1.commit_memory(
                tier="PRECEDENT",
                supplier_id="SUP-309",
                supplier_name="Kuroda Microelectronics",
                sku_family="MCU-ADAS-S32",
                incident_summary="PO-8910 held by CBP for HTS 8542.31 vs 8526.91 mismatch.",
                learned_rule="Always pre-validate HTS 8526.91 on Kuroda radar SoC commercial invoices and hold 500-unit domestic buffer with Austin Silicon Works.",
                provenance="Unit Test Session 1",
            )
            self.assertTrue(store_file.exists())

            # Session 2: New HMemEngine instance reads persisted precedent from disk
            hmem_session_2 = HMemEngine(storage_path=store_file)
            recalled_s2 = hmem_session_2.recall(
                supplier_id="SUP-309",
                sku="MCU-ADAS-S32",
                query_text="Kuroda customs HTS hold",
            )
            self.assertTrue(any(m.memory_id == committed.memory_id for m in recalled_s2))


if __name__ == "__main__":
    unittest.main()

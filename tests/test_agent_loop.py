"""
End-to-End Multi-Agent Collaboration Loop Test (tests/test_agent_loop.py).
Proves that Switchyard executes a genuine non-linear agent workflow:
- Planner delegates based on Scout Intent and H-MEM
- Reconciler executes Round 1 SQL queries and flags conflicts in World Model
- Adversarial Critic challenges Round 1 and triggers Round 2 SQL queries
- Reconciler executes Round 2 SQL queries on QMS and backup suppliers and resolves conflicts
- Risk Escalation Agent computes deterministic line-stop and split-PO allocation math
- Reporter synthesizes a citation-backed Remediation Order and logs all NVIDIA Nemotron receipts
"""

import tempfile
import unittest
from pathlib import Path

from agent.config import SwitchyardConfig
from agent.orchestrator import SwitchyardOrchestrator


class TestMultiAgentCollaborationLoop(unittest.TestCase):
    def test_end_to_end_reconciliation_and_critic_loop(self) -> None:
        cfg = SwitchyardConfig.from_env(force_sample_mode=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            hmem_file = Path(tmpdir) / "hmem.json"
            orch = SwitchyardOrchestrator(config=cfg, hmem_storage_path=hmem_file)
            result = orch.run_investigation(
                question="Reconcile PO-8841 across ERP, WMS, QMS, and Carrier telemetry and recommend an emergency supplier split."
            )

            self.assertEqual(result["po_number"], "PO-8841")
            self.assertEqual(result["sku"], "SIC-MOD-1200V")
            self.assertEqual(len(result["agent_collaboration_trace"]), 6)

            # Verify Zetaris SQL queries (3 in Round 1 + 2 in Round 2 = 5 queries)
            zetaris_ev = result["sponsor_technology_evidence"]["zetaris"]
            self.assertEqual(zetaris_ev["total_sql_queries"], 5)

            # Verify World Model resolved all 3 cross-source conflicts
            wm_ev = result["sponsor_technology_evidence"]["meterless_engines"]["world_model"]
            self.assertEqual(wm_ev["conflict_count"], 3)
            self.assertEqual(wm_ev["resolved_conflict_count"], 3)

            # Verify Markovian bounded context achieved >75% token compression
            mk_ev = result["sponsor_technology_evidence"]["meterless_engines"]["markovian"]
            self.assertGreater(mk_ev["compression_ratio_pct"], 75.0)

            # Verify NVIDIA Nemotron models through Meterless Nightshift handled all 6 steps
            ns_ev = result["sponsor_technology_evidence"]["meterless_nightshift_and_nvidia_nemotron"]
            self.assertEqual(ns_ev["total_nemotron_calls"], 6)
            self.assertEqual(
                ns_ev["models_used_summary"]["nvidia/nemotron-3.5-lightning-30b-a3b"], 3
            )
            self.assertEqual(
                ns_ev["models_used_summary"]["nvidia/nemotron-3.5-super-vl-120b-a12b"], 3
            )

            # Verify deterministic backup supplier split math (2,400 Silicore + 1,250 Pacific Semi = 3,650 shortfall)
            math_ev = result["risk_and_remediation_math"]
            self.assertEqual(math_ev["total_shortfall_units"], 3650)
            self.assertEqual(len(math_ev["backup_allocations"]), 2)
            self.assertEqual(math_ev["backup_allocations"][0]["supplier_id"], "SUP-108")
            self.assertEqual(math_ev["backup_allocations"][0]["allocated_units"], 2400)
            self.assertEqual(math_ev["backup_allocations"][1]["supplier_id"], "SUP-115")
            self.assertEqual(math_ev["backup_allocations"][1]["allocated_units"], 1250)


if __name__ == "__main__":
    unittest.main()

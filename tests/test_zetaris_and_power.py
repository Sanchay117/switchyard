"""
Tests for Layer 01 (Zetaris Data Layer) and Layer 03 (Meterless Nightshift + NVIDIA Nemotron).
Verifies:
- Single-statement SQL enforcement per Zetaris AGENTS.md
- Federated SQL queries across ERP, WMS, QMS, Carrier REST, and Starter PokeAPI tables
- Nightshift runtime model discovery and NVIDIA Nemotron per-request model receipts
"""

import unittest

from agent.config import SwitchyardConfig
from agent.llm import NightshiftNemotronClient
from agent.tools_zetaris import ZetarisClient


class TestZetarisAndNightshiftPower(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = SwitchyardConfig.from_env(force_sample_mode=True)

    def test_01_zetaris_single_statement_rule(self) -> None:
        client = ZetarisClient(self.cfg)
        with self.assertRaises(ValueError):
            client.run_sql("SELECT 1; SELECT 2")

    def test_02_zetaris_federated_queries_and_pokeapi(self) -> None:
        client = ZetarisClient(self.cfg)

        r_dbs = client.run_sql("SHOW LIGHTNING DATABASES")
        self.assertGreaterEqual(r_dbs.row_count, 5)

        r_pika = client.run_sql(
            "SELECT pokemon_name, ability_name, is_hidden FROM pokeapi.pikachu_abilities_table"
        )
        self.assertEqual(r_pika.row_count, 2)
        self.assertEqual(r_pika.rows[0]["pokemon_name"], "pikachu")

        r_join = client.run_sql(
            """
            SELECT p.po_number, p.erp_status, w.usable_unrestricted_qty, q.ticket_id, c.carrier_status
            FROM zetaris_erp.purchase_orders p
            JOIN zetaris_wms.inventory_ledger w ON p.po_number = w.po_number
            JOIN zetaris_qms.incident_tickets q ON p.po_number = q.po_number
            JOIN zetaris_rest.carrier_port_feeds c ON p.po_number = c.po_number
            WHERE p.po_number = 'PO-8841'
            """
        )
        self.assertEqual(r_join.row_count, 1)
        row = r_join.rows[0]
        self.assertEqual(row["erp_status"], "SHIPPED_ON_TIME")
        self.assertEqual(row["usable_unrestricted_qty"], 350)
        self.assertEqual(row["ticket_id"], "QMS-419")
        self.assertEqual(row["carrier_status"], "CUSTOMS_HOLD_ORIGIN")

    def test_03_nightshift_nemotron_lanes_and_receipts(self) -> None:
        ns = NightshiftNemotronClient(self.cfg)
        disc = ns.discover_models()
        self.assertIn("nvidia/nemotron-3.5-lightning-30b-a3b", disc["models_discovered"])
        self.assertIn("nvidia/nemotron-3.5-super-vl-120b-a12b", disc["models_discovered"])

        out_fast, rcpt_fast = ns.run_agent_step(
            step_name="Test Fast Lane",
            agent_name="Reconciler",
            lane="fast",
            system_prompt="System",
            user_prompt="User",
            deterministic_builder=lambda: "fast-lane-ok",
        )
        self.assertEqual(out_fast, "fast-lane-ok")
        self.assertEqual(rcpt_fast.model_handled_by, "nvidia/nemotron-3.5-lightning-30b-a3b")
        self.assertEqual(rcpt_fast.headers_verified["meterless-scope"], "user")

        out_deep, rcpt_deep = ns.run_agent_step(
            step_name="Test Deep Lane",
            agent_name="Conflict Critic",
            lane="deep",
            system_prompt="System",
            user_prompt="User",
            deterministic_builder=lambda: "deep-lane-ok",
        )
        self.assertEqual(out_deep, "deep-lane-ok")
        self.assertEqual(rcpt_deep.model_handled_by, "nvidia/nemotron-3.5-super-vl-120b-a12b")


if __name__ == "__main__":
    unittest.main()

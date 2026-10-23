# HackOS Submission Form Package (`SUBMISSION.md`)

Ready-to-paste answers for the HackOS submission portal (`hackathon.genai.works/event/open-agent-hackathon-2026`).

---

## 1. Track Selection
- **Primary Track:** **Track 1: Solving Fragmented Intelligence**
  *(Note: Switchyard also satisfies Track 2 "The Agent That Can Explain Why" and Track 3 "Reasoning Architecture", and competes for the **Best use of NVIDIA Nemotron / NVIDIA DGX Spark Founder's Edition** and **Best Cursor-built product** awards.)*

## 2. Project Name
**Switchyard**

## 3. Tagline / One-Sentence Problem Statement (APPROACH Format)
We built an agent system (**Switchyard**) that helps an **Operations & Supply-Chain Lead** resolve critical supplier and shipment disruptions by querying **four disconnected, conflicting data sources through Zetaris**, reconciling contradicting records in a shared **Meterless World Model** with an adversarial **Conflict Critic**, compressing multi-step context with **Markovian**, and recalling cross-session precedents with **H-MEM**, powered by **NVIDIA Nemotron (`nvidia/nemotron-3.5-lightning-30b-a3b` and `nvidia/nemotron-3.5-super-vl-120b-a12b`) through Meterless Nightshift**, producing a **single sourced remediation order showing which system each fact came from and which Nemotron model handled every step**.

## 4. Sponsor Technology Explanation (Copy-Paste into HackOS Sponsor Tech Field)

### How Zetaris Was Integrated (Data Layer)
- **Zetaris Federated SQL (`agent/tools_zetaris.py` & `scripts/register_zetaris_sources.sql`):** Switchyard registers and queries five operational sources in Zetaris across four disconnected schemas (`zetaris_erp.purchase_orders`, `zetaris_wms.inventory_ledger`, `zetaris_qms.incident_tickets`, `zetaris_rest.carrier_port_feeds` registered as a `LIGHTNING REST TABLE`, and `zetaris_erp.qualified_suppliers`) plus the starter `pokeapi.pikachu_abilities_table`.
- **REST API Contract:** Every agent `run_sql()` call sends a single SQL statement to `POST {ZETARIS_REST_URL}/sql-editor/sqls/run` with `Authorization: Bearer <ZETARIS_API_KEY>`, `X-Org-ID: 1`, and a fresh UUID4 `X-Request-ID` header. Single-statement execution is enforced in code (`_validate_single_statement`) and tested in `tests/test_zetaris_and_power.py`.
- **Zero-Dependency `SAMPLE_MODE=true` Fallback:** When `SAMPLE_MODE=true` (so judges can run the project cleanly without Docker or live credentials), `ZetarisClient` mounts `data/sample/` into an in-memory SQLite federation engine with identical `zetaris_erp`, `zetaris_wms`, `zetaris_qms`, and `zetaris_rest` schemas so agents execute real SQL queries end to end.

### Which Meterless Engines Were Implemented & Tests Showing They Work (Build Layer)
Switchyard implements **all four Meterless Engines** (`meterless.ai/engines.html`) in `agent/engines/` and verifies all four with automated tests in `tests/test_meterless_engines.py` (`python3 -m unittest discover -s tests -v`):
1. **Scout Intent (`agent/engines/scout_intent.py`):** Classifies incoming operator disruption queries into 5 operational intents, scores blast-radius risk (`0-100`), selects required Zetaris tables, and routes tasks between Nightshift Lane 1 and Lane 2. *(Verified by `test_01_scout_intent_routing_and_risk`)*
2. **World Model (`agent/engines/world_model.py`):** Maintains the shared, versioned entity-state and conflict ledger (`v1` to `v15`) across our 5 collaborating agents, tracking conflict lifecycle (`DETECTED` -> `CHALLENGED_BY_CRITIC` -> `RESOLVED`) and enforcing optimistic concurrency control (`ConcurrencyConflictError`). *(Verified by `test_02_world_model_shared_state_and_concurrency`)*
3. **Markovian (`agent/engines/markovian.py`):** Compresses each completed agent step into a bounded JSON `CarryOverState` capsule (`<= 420 tokens`), achieving **82.5% to 84.0% token reduction** (saving over 6,300 tokens per 6-step run compared to naive $O(n^2)$ transcript accumulation). *(Verified by `test_03_markovian_bounded_context_compression`)*
4. **H-MEM (`agent/engines/h_mem.py`):** 3-tier Hierarchical Memory (`EPISODIC`, `SEMANTIC`, `PRECEDENT`) that recalls historical supplier rules before Step 1 and persists newly verified resolution precedents to disk after Step 6 for subsequent sessions. *(Verified by `test_04_hmem_cross_session_persistence_and_recall`)*

### How Switchyard Connects to Meterless Nightshift & Where NVIDIA Technology Contributes (Power Layer)
- **Meterless Nightshift Runtime (`agent/llm.py`):** Switchyard connects directly to `METERLESS_BASE_URL` (`http://127.0.0.1:8088/v1`) with `Authorization: Bearer <METERLESS_RUNTIME_TOKEN>`, `meterless-app: switchyard-agent`, and `meterless-scope: user`, supporting `GET /v1/models` discovery and `POST /v1/chat/completions`. Per the security rules, the NVIDIA API key is stored only in Nightshift's `Providers` tab, never in `.env` or source code.
- **Dual NVIDIA Nemotron Lanes:**
  - **Lane 1 (Fast Worker - `nvidia/nemotron-3.5-lightning-30b-a3b`):** Powers Step 1 (`Planner & Source Mapper Agent`), Step 2 (`Zetaris Reconciler Round 1 SQL`), and Step 4 (`Zetaris Reconciler Round 2 SQL`).
  - **Lane 2 (Deep Worker - `nvidia/nemotron-3.5-super-vl-120b-a12b`):** Powers Step 3 (`Conflict & Evidence Critic Agent`), Step 5 (`Risk & Policy Escalation Agent`), and Step 6 (`Sourced Decision Reporter Agent`).
- **Explicit Per-Step Model Attribution:** Every agent turn logs and displays a `ModelReceipt` (`receipt_id`, `lane`, `model_handled_by`, `provider`, `latency_ms`, `prompt_tokens`, `completion_tokens`) in the Web Command Center, CLI output, and `output_examples/*_trace.json`.

### What Was Unique About Our Use of Sponsor Technologies
Switchyard combines **Zetaris federated SQL** with a **Markovian-bounded adversarial critic loop** running across **dual NVIDIA Nemotron lanes on Meterless Nightshift**. When the Fast Worker (`nemotron-3.5-lightning-30b-a3b`) flags initial ERP vs WMS conflicts in the **Meterless World Model**, the Deep Worker (`nemotron-3.5-super-vl-120b-a12b`) acts as an adversarial Conflict Critic that challenges unverified quarantine lots, forces a second round of Zetaris SQL queries against QMS acoustic lab logs and backup suppliers, and commits the resulting rule into **H-MEM** while **Markovian** cuts multi-turn token overhead by 84%.

## 5. Pre-Existing Components Declaration
None. All code, datasets, SQL scripts, tests, slide deck, and video assets were created during the Open Agent Hackathon 2026 build window (22-27 October 2026).

## 6. Submission Deliverables Included in Repository
- **Mastered Demo Video (2m 46s, 1080p30, `-16 LUFS`):** `video/out/switchyard-final.mp4`
- **Slide Deck (8-slide presentation):** `docs/deck.html` (also served at `http://127.0.0.1:8050/deck`)
- **High-DPI Product Screenshots:** `docs/command-center.png`, `docs/conflict-reconciliation.png`, `docs/meterless-engines.png`, `docs/nightshift-receipts.png`, `docs/zetaris-sql.png`
- **Official Smoke Test & Conformance Suite:** `smoke_test.py` and `tests/` (`python3 -m unittest discover -s tests -v`)
- **5 Benchmark Disruption Cases & Full Traces:** `input_examples/case_01..05.json` and `output_examples/case_01..05_trace.json` + `_report.md`


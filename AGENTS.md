# AGENTS.md: Open Agent Hackathon 2026 Master Technical Brief & Agent Instructions

This document contains all extracted rules, technical contracts from the 30-page *Participant Setup Guide* PDF, judging criteria, prize requirements, and architectural standards for any AI coding agent (Cursor, Claude Code, Antigravity, Windsurf, Codex) working in this repository.

---

## 1. Hackathon Summary & Prize Strategy

- **Event:** Open Agent Hackathon 2026 (hosted on `hackathon.genai.works` / HackOS)
- **Build Window:** 22 October 2026, 00:00 UTC to 27 October 2026, 23:45 UTC (144 hours)
- **Hard Submission Deadline:** **27 October 2026, 23:45 UTC**
- **Submission Limit:** **Strictly 1 submission per participant/team.**
  - Duplicate accounts disqualify the entire team.
  - A participant may belong to exactly one team (solo teams of 1 compete in the same pool as teams of up to 5).
  - Every submission selects **one primary track**, which can be changed any time before the deadline in the HackOS team workspace.
- **Prize Pool ($20,000 total: $13,000 cash + $7,000 in-kind):**
  - **Track 1: Solving Fragmented Intelligence:** 1st `$1,600` | 2nd `$1,200` | 3rd `$900`
  - **Track 2: The Agent That Can Explain Why:** 1st `$1,600` | 2nd `$1,200` | 3rd `$900`
  - **Track 3: Reasoning Architecture:** 1st `$1,500` | 2nd `$1,200` | 3rd `$900`
  - **Bonus Track: Wildcard [Tinkerer]:** 1st `$1,000` | 2nd `$600` | 3rd `$400`
  - **In-Kind Headline Hardware Award: Best use of NVIDIA Nemotron:** **NVIDIA DGX Spark (Founder's Edition, $4,699 value)**
  - **In-Kind Award: Best Cursor-built product:** **$2,301 Cursor API credits**

### Mandatory Rule to Win the NVIDIA DGX Spark ($4,699)
> *"To compete for the NVIDIA award, a submission must use at least one Nemotron model through Meterless Nightshift in a working feature, and show which model handled the request."*

1. **Never put an NVIDIA API key in `.env` or source code.** The NVIDIA API key from `build.nvidia.com/models` is entered inside **Meterless Nightshift -> Setup -> Providers -> NVIDIA**.
2. The application connects to **Meterless Nightshift Runtime** (`METERLESS_BASE_URL`, default `http://127.0.0.1:8088/v1`) using `METERLESS_RUNTIME_TOKEN` from Nightshift's **Console** tab.
3. Because `meterless/auto` can route to non-NVIDIA models if multiple providers are enabled, **pin an explicit NVIDIA Nemotron lane/model** (e.g. `nvidia/nemotron-3.5-lightning-30b-a3b` for Lane 1 Fast Worker and `nvidia/nemotron-3.5-super-vl-120b-a12b` for Lane 2 Deep Worker) so NVIDIA Nemotron execution is 100% unambiguous.
4. **Every agent step, UI card, log file, and final output must record and display which concrete model handled the request** (`model_handled_by`, `lane`, `provider: "meterless-nightshift"`, latency, and token count).

---

## 2. Exact Technical Contracts (Extracted from the 30-Page Setup Guide PDF)

### Layer 01: DATA (Zetaris)
Every submission **must** use Zetaris as its data layer.

- **Local Docker Endpoints:**
  - Web UI & SQL Editor: `http://localhost:3000` (`ZETARIS_BASE_URL`)
  - REST API Base URL: `http://localhost:8888/api/v1.0` (`ZETARIS_REST_URL`)
  - OpenAPI / ReDoc Reference: `http://localhost:8888/redoc/index.html` (Do not use port `8889`, which is internal)
  - JDBC URL (optional): `jdbc:zetaris:lightning@localhost:10000`
- **REST API SQL Execution Contract (`POST /sql-editor/sqls/run`):**
  - **URL:** `{ZETARIS_REST_URL}/sql-editor/sqls/run`
  - **Headers:**
    ```http
    Authorization: Bearer <ZETARIS_API_KEY>
    X-Org-ID: 1
    X-Request-ID: <fresh-uuid4-per-request>
    Content-Type: application/json
    ```
  - **Request Body:**
    ```json
    {
      "queryId": "<fresh-uuid4>",
      "sql": "SELECT 1",
      "source": "SqlEditor",
      "limit": 100
    }
    ```
  - **Response Parsing:** `response.json().get("data")` returns a list of row arrays.
- **Zetaris Agent Rules (from `zetaris/getting-started` `AGENTS.md`):**
  1. Send **one complete SQL statement at a time** (never batch semicolon-separated statements in a single REST call).
  2. Start preflight checks with read-only statements: `SELECT 1` and `SHOW LIGHTNING DATABASES`.
  3. Use Zetaris **Lightning SQL** syntax when registering sources:
     ```sql
     CREATE LIGHTNING DATABASE <DB_NAME> DESCRIBE BY "<description>";
     CREATE SCHEMASTORE CONTAINER <container_name>;
     CREATE LIGHTNING REST TABLE <table_name> FROM <DB_NAME> REQUEST (endpoint "<url>", method "get", response_type "json", http_encoding "URLENCODED") HEADER () BODY ();
     CREATE SCHEMASTORE VIEW <view_name> WITH CONTAINER <container_name> AS SELECT ... FROM <db>.<table>;
     ```
  4. Zetaris running in Docker cannot read arbitrary local laptop paths directly unless mounted or served over HTTP/S3/Postgres. Always provide both `scripts/register_zetaris_sources.sql` (registering REST tables and federated views in Zetaris) and a built-in `SAMPLE_MODE=true` local SQL virtualization fallback over `/data/sample/` so judges can run the project cleanly even without Docker running.

### Layer 02: BUILD (Meterless Engines)
Every submission **must** implement at least one **Meterless Engine** (`meterless.ai/engines.html` / `github.com/Meterless/Meterless`) in a working product feature and include a reproducible test proving it works.

In this project (`Switchyard`), we implement **all four Meterless Engines** in `agent/engines/` and test all four in `tests/test_meterless_engines.py`:
1. **`Scout Intent` (`agent/engines/scout_intent.py`):**
   - Entry-gate intent classification, blast-radius risk scoring (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), Zetaris source selection, and Nightshift lane routing (`Fast Lane 1` vs `Deep Lane 2`).
2. **`World Model` (`agent/engines/world_model.py`):**
   - Shared, versioned entity-state and conflict ledger across parallel/collaborating agents (`entities`, `facts_by_source`, `conflicts`, `resolutions`, `version`). Prevents agents from overwriting each other's findings and tracks provenance per fact.
3. **`Markovian` (`agent/engines/markovian.py`):**
   - Bounded-context state transition engine for multi-step investigations. Compresses each completed reasoning turn into a deterministic carry-over state capsule (`verified_facts`, `open_conflicts`, `pending_queries`, `token_metrics`) to eliminate $O(n^2)$ history growth and log exact token savings.
4. **`H-MEM` (`agent/engines/h_mem.py`):**
   - Hierarchical Memory Engine (`Episodic` session logs -> `Semantic` supplier reliability patterns -> `Precedent` cross-session resolution decisions persisted to disk). Recalls earlier session decisions and applies them to new incidents with provenance citations.

### Layer 03: POWER (Meterless Nightshift & NVIDIA Nemotron)
Every submission **must** use **Meterless Nightshift** as its primary AI provider.

- **Environment Variables (`.env` / `.env.example`):**
  ```ini
  METERLESS_BASE_URL=http://127.0.0.1:8088/v1
  METERLESS_RUNTIME_TOKEN=your-nightshift-runtime-token-here
  METERLESS_MODEL=nvidia/nemotron-3.5-lightning-30b-a3b
  # Also support Setup Guide Page 24 smoke_test.py aliases:
  MODEL_BASE_URL=http://127.0.0.1:8088/v1
  MODEL_API_KEY=your-nightshift-runtime-token-here
  NEMOTRON_MODEL=nvidia/nemotron-3.5-lightning-30b-a3b
  ```
- **Nightshift Runtime HTTP Contract:**
  - **Discovery:** `GET {METERLESS_BASE_URL}/models`
  - **Completions:** `POST {METERLESS_BASE_URL}/chat/completions`
  - **Required Headers:**
    ```http
    Authorization: Bearer <METERLESS_RUNTIME_TOKEN>
    Content-Type: application/json
    meterless-app: switchyard-agent
    meterless-scope: user
    ```
- **Suggested NVIDIA Nemotron Lanes (Setup Guide Page 18):**
  - **Lane 1 (Fast worker):** `nvidia/nemotron-3.5-lightning-30b-a3b` (Quick responses, tool use, SQL generation, first attempts)
  - **Lane 2 (Deep worker):** `nvidia/nemotron-3.5-super-vl-120b-a12b` (Complex reasoning, planning, Conflict Critic, final verification)

### Official `smoke_test.py` Contract (Setup Guide Page 24)
Keep `smoke_test.py` at the repository root so judges and participants can run `python3 smoke_test.py` to verify:
1. `PASS Data: Zetaris web interface`
2. `PASS Data: Zetaris runs SQL over its REST API`
3. `PASS Power: Nemotron replies`

---

## 3. Judging Rubric (100 Points) & Architectural Mandates

| Criterion | Points | What Judges Score |
| :--- | :--- | :--- |
| **Impact** | **30** | Solves a concrete, high-value operational problem for a clearly defined user. Ties are broken on Impact score first, then submission timestamp. |
| **Technical** | **20** | Reliable end-to-end execution, real multi-agent coordination, clean setup, `SAMPLE_MODE=true` fallback, error recovery. |
| **Innovation** | **15** | Non-linear agent collaboration: critique loops, shared `World Model`, `Markovian` bounded context, `H-MEM` cross-session memory. |
| **Demo** | **15** | Clear 1-4 minute video + interactive live walkthrough demonstrating data conflict reconciliation and Nemotron model attribution. |
| **Product & UX** | **10** | Intuitive operator command center where every conclusion traces back to its exact Zetaris source table and Nemotron model receipt. |
| **Sponsor Tech** | **10** | Meaningful, load-bearing integration of Zetaris, Meterless Engines, Meterless Nightshift, and NVIDIA Nemotron. |

### Agent Collaboration Requirements (Section 3 & Section 9 of Guides)
- **DO NOT build a linear pipeline (`Agent A -> Agent B -> Agent C`).**
- **MUST demonstrate:**
  1. Dynamic task delegation (`Planner / Source Mapper Agent` using `Scout Intent` + `H-MEM`).
  2. Multi-source SQL retrieval (`Zetaris Reconciler Agent` querying 4 disagreeing sources via Zetaris and updating `World Model`).
  3. Adversarial validation & critique (`Conflict & Evidence Critic Agent` rejecting unsupported claims or uncorroborated source conflicts and forcing a targeted Round 2 SQL re-query).
  4. Conditional risk branching (`Risk & Policy Escalation Agent` computing deterministic factory line-stop exposure and split-order math when exposure exceeds policy thresholds).
  5. Auditable final output (`Sourced Decision Reporter Agent` citing exact Zetaris table/row IDs and logging every Nightshift/Nemotron model receipt).

---

## 4. Style & Copywriting Conventions

- **No em-dashes (`—`)** in UI labels, README prose, slide decks, or code comments. Use colons (`:`), commas, parentheses, or periods.
- **Concrete numbers over vague adjectives:** Show exact unit deficits, hours of line runway, failure rates, SQL queries executed, Markovian token compression percentages, and Nightshift model IDs.
- **Zero committed secrets:** `.env` is gitignored; `.env.example` uses placeholders only; NVIDIA API key stays inside Nightshift's `Providers` tab.

---

## 5. Current Implementation Map & Verification Commands for AI Agents

The complete **Switchyard** system is implemented and verified in this repository:

- `smoke_test.py`: Official Setup Guide Page 24 Data + Power smoke test (`PASS Data: Zetaris web interface`, `PASS Data: Zetaris runs SQL over its REST API`, `PASS Power: Nemotron replies`).
- `scripts/preflight.py`: Read-only validator for sample datasets, `SELECT 1`, `SHOW LIGHTNING DATABASES`, `pokeapi.pikachu_abilities_table`, Nightshift `/v1/models` discovery, and `scripts/register_zetaris_sources.sql`.
- `agent/tools_zetaris.py`: Zetaris REST SQL client (`POST /sql-editor/sqls/run`, single-statement enforcement, `X-Org-ID`, UUID4 `X-Request-ID`) + `SAMPLE_MODE=true` in-memory SQLite federation over `data/sample/`.
- `agent/llm.py`: Meterless Nightshift Runtime client (`http://127.0.0.1:8088/v1`, `meterless-app: switchyard-agent`, `meterless-scope: user`) with dual NVIDIA Nemotron lanes (`nvidia/nemotron-3.5-lightning-30b-a3b` and `nvidia/nemotron-3.5-super-vl-120b-a12b`) and per-request `ModelReceipt` tracking.
- `agent/engines/`: Working implementations of all 4 Meterless Engines (`scout_intent.py`, `world_model.py`, `markovian.py`, `h_mem.py`).
- `agent/orchestrator.py`: 6-step iterative multi-agent collaboration loop (`Planner` -> `Reconciler Round 1` -> `Conflict Critic` -> `Reconciler Round 2` -> `Risk Escalator` -> `Sourced Reporter`).
- `tests/`: 8 automated unit, conformance, and end-to-end tests (`python3 -m unittest discover -s tests -v`).
- `web/index.html` & `docs/deck.html`: Interactive Web Command Center and 8-slide presentation deck (`python3 scripts/build_web_assets.py` to rebuild; `python3 -m agent.main --serve` to serve on `http://127.0.0.1:8050`).
- `docs/*.png`: High-DPI Retina screenshots captured from `web/index.html` via `video/scripts/capture_ui.ts` (`command-center.png`, `conflict-reconciliation.png`, `meterless-engines.png`, `nightshift-receipts.png`, `zetaris-sql.png`).
- `video/`: Complete Remotion 1080p30 demo video pipeline (`2m 46s`, `4983 frames @ 30fps`) featuring persistent telemetry chrome, 3D perspective glass browser windows, animated cubic-bezier Zetaris SQL node graphs, Deepgram Aura-2 voiceover narration (`video/scripts/tts.ts`), synthesized 48kHz stereo electronic synth/sub-bass score + UI SFX (`video/scripts/sfx.ts`), and EBU R128 `-16 LUFS` loudness mastering (`video/out/switchyard-final.mp4`).



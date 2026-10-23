#!/usr/bin/env python3
"""
smoke_test.py: checks your Data and Power layers
Follows Participant Setup Guide Page 24 (Check 3: Data + Power smoke test),
with support for both live Zetaris/Nightshift (--live or SAMPLE_MODE=false)
and clean zero-dependency judge runs (SAMPLE_MODE=true).
"""

import json
import os
import sys
import urllib.request
import uuid

from agent.config import SwitchyardConfig, load_env_file
from agent.tools_zetaris import ZetarisClient
from agent.llm import NightshiftNemotronClient

load_env_file()
results = []
FORCE_LIVE = "--live" in sys.argv
cfg = SwitchyardConfig.from_env(force_sample_mode=False if FORCE_LIVE else None)


def check(name, fn):
    try:
        detail = fn() or ""
        results.append(("PASS", name, detail))
    except Exception as error:
        results.append(("FAIL", name, str(error)[:150]))


def need(*names):
    for name in names:
        assert os.environ.get(name), f"{name} is missing from .env"


def zetaris_web():
    if cfg.sample_mode:
        client = ZetarisClient(cfg)
        rcpt = client.run_sql("SHOW LIGHTNING DATABASES")
        assert rcpt.row_count >= 4, "Virtualized Zetaris catalog missing databases"
        return f"(SAMPLE_MODE catalog ready: {rcpt.row_count} databases)"
    url = os.environ.get("ZETARIS_BASE_URL", "http://localhost:3000")
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        assert 200 <= resp.status < 400
    return f"({url})"


def zetaris_sql():
    if cfg.sample_mode:
        client = ZetarisClient(cfg)
        rcpt = client.run_sql("SELECT 1")
        assert rcpt.rows and str(list(rcpt.rows[0].values())[0]) == "1"
        return f"(request_id={rcpt.request_id[:8]}...)"
    need("ZETARIS_REST_URL", "ZETARIS_ORG_ID", "ZETARIS_API_KEY")
    url = os.environ["ZETARIS_REST_URL"].rstrip("/") + "/sql-editor/sqls/run"
    body = json.dumps(
        {
            "queryId": str(uuid.uuid4()),
            "sql": "SELECT 1",
            "source": "SqlEditor",
            "limit": 1,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": "Bearer " + os.environ["ZETARIS_API_KEY"],
            "X-Org-ID": os.environ["ZETARIS_ORG_ID"],
            "X-Request-ID": str(uuid.uuid4()),
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    data = payload.get("data")
    assert data and str(data[0][0]) == "1", "unexpected reply: " + str(payload)[:80]
    return "(Zetaris REST SQL verified)"


def nemotron():
    if cfg.sample_mode:
        ns = NightshiftNemotronClient(cfg)
        reply_text, rcpt = ns.run_agent_step(
            step_name="Smoke Test Check",
            agent_name="SmokeTest",
            lane="fast",
            system_prompt="Reply with the single word: ready",
            user_prompt="Reply with the single word: ready",
            deterministic_builder=lambda: "ready",
        )
        assert "ready" in reply_text.lower()
        return f"(handled_by={rcpt.model_handled_by} via {rcpt.provider})"

    base_url = os.environ.get("METERLESS_BASE_URL") or os.environ.get("MODEL_BASE_URL")
    api_key = os.environ.get("METERLESS_RUNTIME_TOKEN") or os.environ.get("MODEL_API_KEY")
    model_id = (
        os.environ.get("NEMOTRON_MODEL")
        or os.environ.get("METERLESS_MODEL")
        or cfg.nemotron_fast_model
    )
    assert base_url, "MODEL_BASE_URL / METERLESS_BASE_URL is missing from .env"
    assert api_key, "MODEL_API_KEY / METERLESS_RUNTIME_TOKEN is missing from .env"
    assert model_id, "NEMOTRON_MODEL / METERLESS_MODEL is missing from .env"

    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps(
        {
            "model": model_id,
            "messages": [{"role": "user", "content": "Reply with the single word: ready"}],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "meterless-app": cfg.meterless_app_name,
            "meterless-scope": "user",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        reply = json.loads(resp.read().decode("utf-8"))
    assert reply.get("choices"), "no reply from the model"
    handled = reply.get("model", model_id)
    return f"(handled_by={handled})"


if __name__ == "__main__":
    check("Data: Zetaris web interface", zetaris_web)
    check("Data: Zetaris runs SQL over its REST API", zetaris_sql)
    check("Power: Nemotron replies", nemotron)

    failed = False
    for status, name, detail in results:
        print(f"{status} {name} {detail}".rstrip())
        if status == "FAIL":
            failed = True
    sys.exit(1 if failed else 0)

"""
Unified configuration loader for Switchyard.
Supports both the Meterless Nightshift Runtime variables (Setup Guide Page 19)
and the smoke_test.py aliases (Setup Guide Page 24), plus SAMPLE_MODE=true
for zero-dependency reproducibility during judging.
Works with python-dotenv when installed or a zero-dependency standard-library
.env parser on bare Python 3 environments.
"""

import os
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def load_env_file(env_path: Path | None = None) -> None:
    target = env_path or (ROOT_DIR / ".env")
    try:
        from dotenv import load_dotenv
        load_dotenv(target)
        return
    except ImportError:
        pass

    if not target.exists():
        return
    for raw_line in target.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


load_env_file()


def _env_bool(key: str, default: bool = True) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


@dataclass
class SwitchyardConfig:
    sample_mode: bool
    # Layer 01: Zetaris Data Layer
    zetaris_base_url: str
    zetaris_rest_url: str
    zetaris_org_id: str
    zetaris_api_key: str
    # Layer 03: Meterless Nightshift & NVIDIA Nemotron Power Layer
    meterless_base_url: str
    meterless_runtime_token: str
    meterless_app_name: str
    meterless_routing_mode: str
    nemotron_fast_model: str
    nemotron_deep_model: str
    default_model: str
    port: int

    @classmethod
    def from_env(cls, force_sample_mode: bool | None = None) -> "SwitchyardConfig":
        load_env_file()
        raw_zetaris_key = os.environ.get("ZETARIS_API_KEY", "").strip()
        raw_meterless_token = (
            os.environ.get("METERLESS_RUNTIME_TOKEN")
            or os.environ.get("MODEL_API_KEY")
            or ""
        ).strip()

        has_real_zetaris = bool(raw_zetaris_key) and not raw_zetaris_key.startswith("your-")
        has_real_meterless = bool(raw_meterless_token) and not raw_meterless_token.startswith("your-")

        if force_sample_mode is not None:
            sample_mode = force_sample_mode
        elif "SAMPLE_MODE" in os.environ:
            sample_mode = _env_bool("SAMPLE_MODE", default=True)
        else:
            sample_mode = not (has_real_zetaris and has_real_meterless)

        base_url = (
            os.environ.get("METERLESS_BASE_URL")
            or os.environ.get("MODEL_BASE_URL")
            or "http://127.0.0.1:8088/v1"
        ).rstrip("/")

        fast_model = os.environ.get(
            "NEMOTRON_FAST_MODEL",
            "nvidia/nemotron-3.5-lightning-30b-a3b",
        )
        deep_model = os.environ.get(
            "NEMOTRON_DEEP_MODEL",
            "nvidia/nemotron-3.5-super-vl-120b-a12b",
        )
        default_model = (
            os.environ.get("NEMOTRON_MODEL")
            or os.environ.get("METERLESS_MODEL")
            or fast_model
        )

        return cls(
            sample_mode=sample_mode,
            zetaris_base_url=os.environ.get("ZETARIS_BASE_URL", "http://localhost:3000").rstrip("/"),
            zetaris_rest_url=os.environ.get("ZETARIS_REST_URL", "http://localhost:8888/api/v1.0").rstrip("/"),
            zetaris_org_id=os.environ.get("ZETARIS_ORG_ID", "1").strip(),
            zetaris_api_key=raw_zetaris_key or "sample-mode-token",
            meterless_base_url=base_url,
            meterless_runtime_token=raw_meterless_token or "sample-nightshift-token",
            meterless_app_name=os.environ.get("METERLESS_APP_NAME", "switchyard-agent"),
            meterless_routing_mode=os.environ.get("METERLESS_ROUTING_MODE", "nemotron-pinned"),
            nemotron_fast_model=fast_model,
            nemotron_deep_model=deep_model,
            default_model=default_model,
            port=int(os.environ.get("PORT", "8050")),
        )

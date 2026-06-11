from __future__ import annotations

import json
import secrets
import shlex
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .config import Config


def tool_name() -> str:
    return "wordpress-api-tool"


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def env_fingerprint(cfg: Config) -> dict[str, str]:
    return {"base_url": cfg.base_url}


def command_string(argv: list[str]) -> str:
    if not argv:
        return tool_name()
    return f"{tool_name()} {shlex.join(list(argv))}"


def plan_common_fields(*, cfg: Config, argv: list[str]) -> dict[str, Any]:
    return {
        "tool": tool_name(),
        "version": __version__,
        "generated_at_utc": now_utc_iso(),
        "env_fingerprint": env_fingerprint(cfg),
        "command": command_string(argv),
    }


def receipt_common_fields(*, cfg: Config, argv: list[str]) -> dict[str, Any]:
    return {
        "tool": tool_name(),
        "version": __version__,
        "applied_at_utc": now_utc_iso(),
        "env_fingerprint": env_fingerprint(cfg),
        "command": command_string(argv),
    }


def write_json_file(path: str, payload: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def default_run_id() -> str:
    ts = time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime())
    return f"{ts}_{secrets.token_hex(3)}"


def before_state_root(*, env_file: str, run_id: str) -> Path:
    env_dir = Path(env_file).expanduser().resolve().parent
    return env_dir / ".state" / "runs" / run_id / "before"


def save_before_state(
    *,
    env_file: str,
    run_id: str,
    family: str,
    selector: str,
    payload: Any,
) -> dict[str, Any]:
    safe_family = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "_" for ch in family).strip("._") or "write"
    safe_selector = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "_" for ch in selector).strip("._") or "target"
    path = before_state_root(env_file=env_file, run_id=run_id) / f"{safe_family}__{safe_selector}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "saved": True,
        "path": str(path),
        "kind": "json",
        "captured_at_utc": now_utc_iso(),
        "restore_note": "Use this saved before-state as the source for a deliberate manual restore if you need to undo the change later.",
    }

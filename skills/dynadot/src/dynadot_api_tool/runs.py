from __future__ import annotations

import json
import secrets
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _default_run_id() -> str:
    # Human-browsable + unique enough for local history.
    ts = time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime())
    short = secrets.token_hex(3)
    return f"{ts}_{short}"


def _tool_root_from_env_file(env_file: str) -> Path:
    # We intentionally anchor `.state/` next to `--env-file` so customers can find it.
    return Path(env_file).expanduser().resolve().parent


def runs_index_path_for_env_file(env_file: str) -> Path:
    tool_root = _tool_root_from_env_file(env_file)
    return tool_root / ".state" / "runs" / "index.jsonl"


@dataclass(frozen=True)
class RunContext:
    enabled: bool
    run_id: str | None
    artifacts_dir: Path | None
    runs_index_path: Path | None
    audit_log_path: Path | None


def init_run_context(
    *,
    env_file: str,
    enabled: bool,
    run_id: str | None,
    artifacts_dir: str | None,
    no_artifacts: bool,
) -> RunContext:
    if not enabled or no_artifacts:
        return RunContext(
            enabled=False,
            run_id=None,
            artifacts_dir=None,
            runs_index_path=None,
            audit_log_path=None,
        )

    tool_root = _tool_root_from_env_file(env_file)
    runs_root = tool_root / ".state" / "runs"
    runs_root.mkdir(parents=True, exist_ok=True)

    rid = str(run_id).strip() if run_id else _default_run_id()
    run_dir = Path(artifacts_dir).expanduser().resolve() if artifacts_dir else (runs_root / rid)
    run_dir.mkdir(parents=True, exist_ok=True)

    return RunContext(
        enabled=True,
        run_id=rid,
        artifacts_dir=run_dir,
        runs_index_path=runs_root / "index.jsonl",
        audit_log_path=run_dir / "audit.jsonl",
    )


def append_index_row(index_path: Path, row: dict[str, Any]) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def iter_index_rows(index_path: Path) -> list[dict[str, Any]]:
    if not index_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with index_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def list_runs(index_path: Path, *, limit: int = 20, tool: str | None = None) -> list[dict[str, Any]]:
    rows = iter_index_rows(index_path)
    if tool:
        wanted = str(tool).strip()
        rows = [row for row in rows if str(row.get("tool") or "").strip() == wanted]
    rows = rows[-limit:]
    return list(reversed(rows))


def find_run(index_path: Path, *, run_id: str, tool: str | None = None) -> dict[str, Any] | None:
    rid = str(run_id).strip()
    wanted = str(tool).strip() if tool else None
    for row in reversed(iter_index_rows(index_path)):
        if wanted and str(row.get("tool") or "").strip() != wanted:
            continue
        if str(row.get("run_id") or "") == rid:
            return row
    return None


def write_summary_md(*, path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join([ln.rstrip() for ln in lines]).strip() + "\n"
    path.write_text(content, encoding="utf-8")


def build_deterministic_summary(
    *,
    tool: str,
    version: str,
    run_id: str,
    env_fingerprint: str | None,
    command: str | None,
    output_obj: dict[str, Any] | None,
    plan_path: str | None,
    receipt_path: str | None,
    audit_log_path: str | None,
    audit_log_global_path: str | None,
    runs_index_path: str | None,
) -> list[str]:
    outcome = "unknown"
    if isinstance(output_obj, dict):
        if bool(output_obj.get("refused")):
            outcome = "refused"
        elif bool(output_obj.get("ok")) and bool(output_obj.get("dry_run")):
            outcome = "dry_run"
        elif bool(output_obj.get("ok")):
            outcome = "ok"
        else:
            outcome = "error"

    lines = [
        f"# Run summary ({tool})",
        "",
        f"- Time (UTC): {_utc_now()}",
        f"- Tool: {tool}",
        f"- Version: {version}",
        f"- Run ID: {run_id}",
        f"- Outcome: {outcome}",
        f"- Env fingerprint: {env_fingerprint or '<unknown>'}",
        f"- Command: {command or '<unknown>'}",
        "",
        "## Proof paths",
        f"- Runs index: {runs_index_path or '<none>'}",
        f"- Audit log (run): {audit_log_path or '<none>'}",
        f"- Audit log (global): {audit_log_global_path or '<none>'}",
        f"- Plan: {plan_path or '<none>'}",
        f"- Receipt: {receipt_path or '<none>'}",
        "",
        "Tip: ask your agent natural-language questions like:",
        '- "What happened in the last run?"',
        f'- "Show me what happened in run {run_id}."',
    ]
    return lines

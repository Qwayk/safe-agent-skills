from __future__ import annotations

from pathlib import Path

from ..json_files import write_json_file
from .write_safety import build_local_write_plan, ensure_blocked_apply_contract, refusal_output


def _read_text_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    if not text:
        return []
    return text.splitlines(keepends=True)


def _has_nonempty_env_value(lines: list[str], key: str) -> bool:
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        candidate = stripped
        if candidate.startswith("export "):
            candidate = candidate[len("export ") :].lstrip()
        k, v = candidate.split("=", 1)
        if k.strip() == key and v.strip().strip("'").strip('"'):
            return True
    return False


def cmd_onboarding(args: object, ctx: dict) -> int:
    out = ctx["out"]
    env_file = str(getattr(args, "env_file", ".env"))
    write_env = bool(ctx.get("apply")) and not bool(getattr(args, "no_write_env", False))

    env_path = Path(env_file)
    env_created = False
    required_keys = [
        "AMAZON_CREATORS_API_BASE_URL",
        "AMAZON_CREATORS_CREDENTIAL_ID",
        "AMAZON_CREATORS_CREDENTIAL_SECRET",
        "AMAZON_CREATORS_CREDENTIAL_VERSION",
        "AMAZON_CREATORS_LOCALE",
        "AMAZON_CREATORS_PARTNER_TAG",
    ]

    if write_env and not env_path.exists():
        plan = build_local_write_plan(
            ctx=ctx,
            command_id="onboarding",
            selector={"kind": "env_file", "path": str(env_path)},
            proposed_changes=[{"action": "create_env_file_from_example", "path": str(env_path)}],
            risk_reasons=["local-env-file-write"],
            local_state={"kind": "env_file", "path": str(env_path), "writes_env_file": True},
        )
        plan_out = ctx.get("plan_out")
        if plan_out:
            write_json_file(plan_out, plan)
        plan = ensure_blocked_apply_contract(
            plan,
            action="onboarding",
            local_state={"kind": "env_file", "path": str(env_path), "writes_env_file": True},
        )
        payload = refusal_output(plan=plan)
        payload["onboarding"] = {
            "env_file": env_file,
            "env_created": False,
            "missing": required_keys,
            "next_command": "amazon-creators-api-tool --output json auth token fetch",
            "steps": [],
        }
        out.emit(payload)
        return 0

    lines = _read_text_lines(env_path)

    missing: list[str] = []
    for key in required_keys:
        if not _has_nonempty_env_value(lines, key):
            missing.append(key)

    steps = [
        "Copy .env.example → .env (local-only; do not commit it).",
        "Open .env and fill the required fields:",
        "  - AMAZON_CREATORS_API_BASE_URL=https://creatorsapi.amazon/catalog/v1",
        "  - AMAZON_CREATORS_CREDENTIAL_ID=<credential id from Amazon Creators portal>",
        "  - AMAZON_CREATORS_CREDENTIAL_SECRET=<credential secret>",
        "  - AMAZON_CREATORS_CREDENTIAL_VERSION=2.1",
        "  - AMAZON_CREATORS_LOCALE=en_US",
        "  - AMAZON_CREATORS_PARTNER_TAG=<partner tag from your Amazon Creators credential>",
        "  - (optional) AMAZON_CREATORS_TOKEN_URL=https://creatorsapi.amazon/login... if you need to override the token endpoint",
        "Run: amazon-creators-api-tool --output json auth token fetch to review the blocked token-cache plan.",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "next_command": "amazon-creators-api-tool --output json auth token fetch",
            "steps": steps,
        },
    }

    if str(getattr(args, "output", "json")) == "json":
        out.emit(payload)
    else:
        print("To connect this tool to your API, do this once:")
        for i, s in enumerate(steps, start=1):
            print(f"{i}. {s}")
        if missing:
            print("")
            print(f"Missing in {env_file}: " + ", ".join(missing))
        print("")
        print("Next: amazon-creators-api-tool --output json auth token fetch")
    return 0

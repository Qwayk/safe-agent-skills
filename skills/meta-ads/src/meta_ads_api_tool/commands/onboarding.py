from __future__ import annotations

from pathlib import Path

from ..config import normalize_ad_account_id

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
    write_env = not bool(getattr(args, "no_write_env", False))

    env_path = Path(env_file)
    env_created = False

    if write_env and not env_path.exists():
        example_path = env_path.parent / ".env.example"
        if example_path.exists():
            env_path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            env_path.write_text("", encoding="utf-8")
        env_created = True

    lines = _read_text_lines(env_path)

    missing: list[str] = []
    if not _has_nonempty_env_value(lines, "META_ADS_ACCESS_TOKEN"):
        missing.append("META_ADS_ACCESS_TOKEN")

    steps = [
        "Copy .env.example → .env (local-only; do not commit it).",
        "Create a Meta access token with the minimum required permissions (typically ads_read).",
        "Find your Ad Account ID (a numeric id; the tool will normalize to act_<id>).",
        "Open .env and fill the required values:",
        "  - META_ADS_ACCESS_TOKEN=<your token>",
        "Optional (recommended):",
        "  - META_ADS_AD_ACCOUNT_ID=<numeric id or act_<id>>",
        "Run: meta-ads-api-tool --output json auth check",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "next_command": "meta-ads-api-tool --output json auth check",
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
        existing_id = None
        for line in lines:
            if line.strip().startswith("META_ADS_AD_ACCOUNT_ID="):
                existing_id = line.strip().split("=", 1)[1].strip()
                break
        if existing_id:
            norm = normalize_ad_account_id(existing_id)
            if norm and norm != existing_id:
                print("")
                print(f"Note: META_ADS_AD_ACCOUNT_ID will be normalized to {norm}.")
        print("")
        print("Next: meta-ads-api-tool --output json auth check")
    return 0

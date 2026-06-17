from __future__ import annotations

from pathlib import Path


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
    if not _has_nonempty_env_value(lines, "FORTNOX_API_BASE_URL"):
        missing.append("FORTNOX_API_BASE_URL")
    if not _has_nonempty_env_value(lines, "FORTNOX_CLIENT_ID"):
        missing.append("FORTNOX_CLIENT_ID")
    if not _has_nonempty_env_value(lines, "FORTNOX_CLIENT_SECRET"):
        missing.append("FORTNOX_CLIENT_SECRET")
    if not _has_nonempty_env_value(lines, "FORTNOX_REDIRECT_URI"):
        missing.append("FORTNOX_REDIRECT_URI")

    steps = [
        "Copy .env.example → .env (local-only; do not commit it).",
        "Open .env and fill the required Fortnox app values:",
        "  - FORTNOX_API_BASE_URL=https://api.fortnox.se/3",
        "  - FORTNOX_CLIENT_ID=<your Fortnox app client id>",
        "  - FORTNOX_CLIENT_SECRET=<your Fortnox app client secret>",
        "  - FORTNOX_REDIRECT_URI=<the redirect URI registered in Fortnox Developer Portal>",
        "Run: fortnox-api-tool --output json auth login",
        "After approval, run: fortnox-api-tool --output json auth exchange-code --code <code> --state <state>",
        "Then run: fortnox-api-tool --output json auth check",
        "If you use Fortnox service accounts, save FORTNOX_SERVICE_TENANT_ID after the first activation and then use auth service-account-token.",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "next_command": "fortnox-api-tool --output json auth login",
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
        print("Next: fortnox-api-tool --output json auth login")
    return 0

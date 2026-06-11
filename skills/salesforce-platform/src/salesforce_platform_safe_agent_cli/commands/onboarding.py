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
    for key in ["SALESFORCE_INSTANCE_URL", "SALESFORCE_API_VERSION"]:
        if not _has_nonempty_env_value(lines, key):
            missing.append(key)
    has_token = _has_nonempty_env_value(lines, "SALESFORCE_ACCESS_TOKEN")

    steps = [
        "Create a Salesforce External Client App or Connected App that can issue a REST API access token.",
        "Fill .env with your org URL and version, for example SALESFORCE_INSTANCE_URL=https://your-domain.my.salesforce.com and SALESFORCE_API_VERSION=67.0.",
        "Choose one token path: set SALESFORCE_ACCESS_TOKEN in .env, or store a token JSON file with qwayk-salesforce-platform-safe-agent-cli auth token set --file token.json.",
        "Run qwayk-salesforce-platform-safe-agent-cli --output json auth check.",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "token_configured_in_env": has_token,
            "next_command": "qwayk-salesforce-platform-safe-agent-cli --output json auth check",
            "steps": steps,
        },
    }

    if str(getattr(args, "output", "json")) == "json":
        out.emit(payload)
    else:
        print("To connect this tool to Salesforce Platform REST:")
        for i, step in enumerate(steps, start=1):
            print(f"{i}. {step}")
        if missing:
            print("")
            print(f"Missing in {env_file}: " + ", ".join(missing))
        if not has_token:
            print("No SALESFORCE_ACCESS_TOKEN found in the env file. A stored token JSON is also supported.")
        print("")
        print("Next: qwayk-salesforce-platform-safe-agent-cli --output json auth check")
    return 0

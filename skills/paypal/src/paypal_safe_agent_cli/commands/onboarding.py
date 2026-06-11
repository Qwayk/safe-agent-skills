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
    if not _has_nonempty_env_value(lines, "PAYPAL_ENVIRONMENT"):
        missing.append("PAYPAL_ENVIRONMENT")
    if not _has_nonempty_env_value(lines, "PAYPAL_CLIENT_ID"):
        missing.append("PAYPAL_CLIENT_ID")
    if not _has_nonempty_env_value(lines, "PAYPAL_CLIENT_SECRET"):
        missing.append("PAYPAL_CLIENT_SECRET")

    steps = [
        "Copy .env.example to .env if it is missing. Keep it local and do not commit it.",
        "Open the PayPal Developer Dashboard and go to Apps & Credentials.",
        "Create or open a REST app, then copy the client ID and client secret.",
        "Set PAYPAL_ENVIRONMENT to sandbox while testing or live when you are ready for production.",
        "Fill the required .env values:",
        "  - PAYPAL_ENVIRONMENT=sandbox",
        "  - PAYPAL_CLIENT_ID=<your PayPal REST app client ID>",
        "  - PAYPAL_CLIENT_SECRET=<your PayPal REST app client secret>",
        "Optional partner/on-behalf-of headers can stay blank unless your PayPal setup needs them.",
        "Run: qwayk-paypal-safe-agent-cli --output json auth check",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "next_command": "qwayk-paypal-safe-agent-cli --output json auth check",
            "steps": steps,
        },
    }

    if str(getattr(args, "output", "json")) == "json":
        out.emit(payload)
    else:
        print("To connect this tool to PayPal, do this once:")
        for i, s in enumerate(steps, start=1):
            print(f"{i}. {s}")
        if missing:
            print("")
            print(f"Missing in {env_file}: " + ", ".join(missing))
        print("")
        print("Next: qwayk-paypal-safe-agent-cli --output json auth check")
    return 0

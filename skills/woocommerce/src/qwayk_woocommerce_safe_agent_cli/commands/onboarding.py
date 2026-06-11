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
        current_key, value = candidate.split("=", 1)
        if current_key.strip() == key and value.strip().strip("'").strip('"'):
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
    for key in [
        "WOOCOMMERCE_STORE_URL",
        "WOOCOMMERCE_CONSUMER_KEY",
        "WOOCOMMERCE_CONSUMER_SECRET",
    ]:
        if not _has_nonempty_env_value(lines, key):
            missing.append(key)

    steps = [
        "Set WOOCOMMERCE_STORE_URL to your store home URL, for example https://shop.example.com",
        "In WordPress admin open WooCommerce > Settings > Advanced > REST API",
        "Create a new REST API key with Read/Write access",
        "Paste the consumer key and consumer secret into .env",
        "If your server strips Authorization headers, set WOOCOMMERCE_QUERY_STRING_AUTH=true",
        "Run: qwayk-woocommerce-safe-agent-cli --output json auth check",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "next_command": "qwayk-woocommerce-safe-agent-cli --output json auth check",
            "steps": steps,
        },
    }
    if str(getattr(args, "output", "json")) == "json":
        out.emit(payload)
        return 0

    print("To connect the WooCommerce tool, do this once:")
    for idx, step in enumerate(steps, start=1):
        print(f"{idx}. {step}")
    if missing:
        print("")
        print(f"Missing in {env_file}: " + ", ".join(missing))
    print("")
    print("Next: qwayk-woocommerce-safe-agent-cli --output json auth check")
    return 0

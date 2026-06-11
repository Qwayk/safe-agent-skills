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

    product_missing: list[str] = []
    account_missing: list[str] = []
    for key in ("CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET"):
        if not _has_nonempty_env_value(lines, key):
            product_missing.append(key)
    for key in ("CLOUDINARY_ACCOUNT_ID", "CLOUDINARY_ACCOUNT_API_KEY", "CLOUDINARY_ACCOUNT_API_SECRET"):
        if not _has_nonempty_env_value(lines, key):
            account_missing.append(key)

    steps = [
        "Open Cloudinary Console -> Settings -> API Keys and copy your product environment values into `.env`.",
        "For the media, video, and analyze APIs fill `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET`.",
        "For the provisioning and permissions APIs fill `CLOUDINARY_ACCOUNT_ID`, `CLOUDINARY_ACCOUNT_API_KEY`, and `CLOUDINARY_ACCOUNT_API_SECRET`.",
        "If your Cloudinary account uses EU or AP hosts, change `CLOUDINARY_PRODUCT_API_HOST` and `CLOUDINARY_ACCOUNT_API_HOST` too.",
        "Run `cloudinary-safe-agent-cli --output json auth check`.",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": {
                "product": product_missing,
                "account": account_missing,
            },
            "next_command": "cloudinary-safe-agent-cli --output json auth check",
            "steps": steps,
        },
    }

    if str(getattr(args, "output", "json")) == "json":
        out.emit(payload)
    else:
        print("To connect this Cloudinary tool, do this once:")
        for i, s in enumerate(steps, start=1):
            print(f"{i}. {s}")
        if product_missing or account_missing:
            print("")
            print(f"Missing product values in {env_file}: " + ", ".join(product_missing or ["none"]))
            print(f"Missing account values in {env_file}: " + ", ".join(account_missing or ["none"]))
        print("")
        print("Next: cloudinary-safe-agent-cli --output json auth check")
    return 0

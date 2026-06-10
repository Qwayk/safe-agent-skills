from __future__ import annotations

from pathlib import Path


_PLACEHOLDER_ENV = """# LinkedIn Ads tool values
LINKEDIN_ADS_BASE_URL=https://api.linkedin.com/rest
LINKEDIN_ADS_TOKEN=
LINKEDIN_ADS_LINKEDIN_VERSION=202605
LINKEDIN_ADS_RESTLI_PROTOCOL_VERSION=2.0.0
LINKEDIN_ADS_TIMEOUT_S=30
"""


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
        env_path.write_text(_PLACEHOLDER_ENV, encoding="utf-8")
        env_created = True

    lines = _read_text_lines(env_path)
    missing: list[str] = []
    for key in (
        "LINKEDIN_ADS_BASE_URL",
        "LINKEDIN_ADS_TOKEN",
        "LINKEDIN_ADS_LINKEDIN_VERSION",
        "LINKEDIN_ADS_RESTLI_PROTOCOL_VERSION",
    ):
        if not _has_nonempty_env_value(lines, key):
            missing.append(key)

    steps = [
        "Run onboarding on a local machine, not in CI.",
        "Put a real LinkedIn Ads access token in LINKEDIN_ADS_TOKEN.",
        "LinkedIn may hide some endpoints unless your app and account are approval-gated correctly.",
        "If auth is denied, ask your app owner to confirm the LinkedIn access request in developer settings.",
        "Run: linkedin-ads-api-tool --output json auth check",
        "Then run one read family command to confirm your account scope.",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "next_command": "linkedin-ads-api-tool --output json auth check",
            "steps": steps,
        },
    }

    out.emit(payload)
    return 0

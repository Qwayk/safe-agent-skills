from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from ..errors import ValidationError


@dataclass(frozen=True)
class OnboardingResult:
    env_file: str
    env_created: bool
    admin_api_url_written: bool
    accept_version_written: bool
    missing: list[str]
    next_command: str
    steps: list[str]


def _build_admin_api_url(api_url_value: str) -> str:
    raw = (api_url_value or "").strip()
    if not raw:
        raise ValidationError("Missing API URL value (example: https://your-site.ghost.io)")
    if not (raw.startswith("https://") or raw.startswith("http://")):
        raw = "https://" + raw
    parsed = urlparse(raw)
    if not parsed.scheme or not parsed.netloc:
        raise ValidationError("API URL must look like https://example.com (no /ghost/api/admin/ path needed)")

    # If the user pasted a full admin API base URL already, accept it.
    if "/ghost/api/admin" in (parsed.path or ""):
        base = raw.rstrip("/") + "/"
        if "/ghost/api/admin/" not in base:
            # normalize missing trailing slash after admin
            base = base.replace("/ghost/api/admin", "/ghost/api/admin/")
        return base

    base = f"{parsed.scheme}://{parsed.netloc}"
    return base.rstrip("/") + "/ghost/api/admin/"


def _read_text_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    if not text:
        return []
    # Preserve newline characters for stable rewriting.
    return text.splitlines(keepends=True)


def _upsert_env_value(lines: list[str], key: str, value: str) -> tuple[list[str], bool]:
    out: list[str] = []
    found = False
    changed = False
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            out.append(line)
            continue
        candidate = stripped
        export_prefix = ""
        if candidate.startswith("export "):
            export_prefix = "export "
            candidate = candidate[len("export ") :].lstrip()
        k = candidate.split("=", 1)[0].strip()
        if k != key:
            out.append(line)
            continue
        if not found:
            out.append(f"{export_prefix}{key}={value}\n")
            found = True
            if line != f"{export_prefix}{key}={value}\n":
                changed = True
        else:
            # Drop duplicates (keep the first).
            changed = True
            continue

    if not found:
        if out and not out[-1].endswith("\n"):
            out[-1] = out[-1] + "\n"
        out.append(f"{key}={value}\n")
        changed = True
    return out, changed


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
    api_url_value = str(getattr(args, "api_url", "") or "").strip()
    write_env = not bool(getattr(args, "no_write_env", False))
    accept_version = str(getattr(args, "accept_version", "") or "").strip() or "v5.0"

    env_path = Path(env_file)
    env_created = False
    admin_api_url_written = False
    accept_version_written = False

    if write_env and not env_path.exists():
        example_path = env_path.parent / ".env.example"
        if example_path.exists():
            env_path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            env_path.write_text("", encoding="utf-8")
        env_created = True

    lines = _read_text_lines(env_path)

    if api_url_value:
        admin_api_url = _build_admin_api_url(api_url_value)
        lines, _ = _upsert_env_value(lines, "GHOST_ADMIN_API_URL", admin_api_url)
        admin_api_url_written = True

    # Always ensure accept version exists (safe default).
    if write_env:
        lines, _ = _upsert_env_value(lines, "GHOST_ACCEPT_VERSION", accept_version)
        accept_version_written = True

    if write_env:
        env_path.write_text("".join(lines), encoding="utf-8")

    missing: list[str] = []
    if not _has_nonempty_env_value(lines, "GHOST_ADMIN_API_URL"):
        missing.append("GHOST_ADMIN_API_URL")
    if not _has_nonempty_env_value(lines, "GHOST_ADMIN_API_KEY"):
        missing.append("GHOST_ADMIN_API_KEY")
    if not _has_nonempty_env_value(lines, "GHOST_ACCEPT_VERSION"):
        missing.append("GHOST_ACCEPT_VERSION")

    steps = [
        "In Ghost Admin, go to Settings → Integrations and open your custom integration.",
        "Copy the field labeled “API URL” (safe to share). Note: it can differ from your public website domain.",
        "Copy the “Admin API Key” (secret; do not paste it into chat).",
        f"Open {env_file} and set:",
        "  - GHOST_ADMIN_API_URL=<API URL>/ghost/api/admin/",
        "  - GHOST_ADMIN_API_KEY=<id:secret>",
        f"  - GHOST_ACCEPT_VERSION={accept_version}",
        "Run: ghost-api-tool --output json auth check",
    ]

    next_command = "ghost-api-tool --output json auth check"
    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "admin_api_url_written": admin_api_url_written,
            "accept_version_written": accept_version_written,
            "missing": missing,
            "next_command": next_command,
            "steps": steps,
        },
    }

    if str(getattr(args, "output", "json")) == "json":
        out.emit(payload)
    else:
        print("To connect ghost-api-tool to your Ghost site, do this once:")
        for i, s in enumerate(steps, start=1):
            print(f"{i}. {s}")
        if missing:
            print("")
            print(f"Missing in {env_file}: " + ", ".join(missing))
        print("")
        print(f"Next: {next_command}")
    return 0

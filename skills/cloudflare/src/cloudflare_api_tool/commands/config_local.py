from __future__ import annotations

import os
import stat
from pathlib import Path

from ..config import load_config
from ..errors import ValidationError


def _is_git_repo(path: Path) -> bool:
    cur = path
    for _ in range(10_000):
        if (cur / ".git").exists():
            return True
        if cur.parent == cur:
            return False
        cur = cur.parent
    return False


def _is_file_tracked_by_git(file_path: Path) -> bool:
    """
    Best-effort check whether a file is tracked by git (never required).
    """
    try:
        import subprocess

        res = subprocess.run(  # noqa: S603
            ["git", "ls-files", "--error-unmatch", str(file_path)],
            cwd=str(file_path.parent),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return res.returncode == 0
    except Exception:
        return False


def _chmod_0600_best_effort(path: Path) -> None:
    try:
        if os.name != "posix":
            return
        os.chmod(str(path), 0o600)
    except Exception:
        return


def cmd_config_init(args, ctx) -> int:
    """
    Local-only helper: ensure the env file exists, seeded from `.env.example`.

    This command never prints secrets and never calls the Cloudflare API.
    """
    env_file = Path(str(ctx.get("env_file") or ".env")).expanduser()
    force = bool(getattr(args, "force", False))

    raw_example = getattr(args, "env_example", None)
    example_str = str(raw_example or "").strip()
    example = Path(example_str).expanduser() if example_str else Path("")
    if not example_str:
        example = env_file.parent / ".env.example"

    if env_file.exists() and not force:
        _chmod_0600_best_effort(env_file)
        ctx["out"].emit(
            {
                "ok": True,
                "command": "config.init",
                "changed": False,
                "env_file": str(env_file),
                "note": "Env file already exists (use --force to overwrite).",
            }
        )
        return 0

    if not example.exists():
        raise ValidationError(f"Missing env example file: {example}")

    env_file.parent.mkdir(parents=True, exist_ok=True)
    env_file.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
    _chmod_0600_best_effort(env_file)
    ctx["out"].emit(
        {
            "ok": True,
            "command": "config.init",
            "changed": True,
            "env_file": str(env_file),
            "seeded_from": str(example),
            "note": "Wrote placeholders only. Paste your Cloudflare API token into the env file locally (never into chat).",
        }
    )
    return 0


def cmd_config_check(args, ctx) -> int:
    """
    Local-only helper: validate env file basics (no API calls).
    """
    _ = args
    env_file = Path(str(ctx.get("env_file") or ".env")).expanduser()
    checks: list[dict[str, object]] = []
    warnings: list[str] = []

    if not env_file.exists():
        ctx["out"].emit(
            {
                "ok": False,
                "command": "config.check",
                "error_type": "NotFound",
                "error": f"Env file not found: {env_file}",
                "hint": "Run: cloudflare-api-tool config init",
            }
        )
        return 1

    # Permissions check (best-effort)
    if os.name == "posix":
        try:
            mode = stat.S_IMODE(os.stat(str(env_file)).st_mode)
            too_open = bool(mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH))
            checks.append({"name": "env_permissions_posix", "ok": not too_open, "mode_octal": oct(mode)})
            if too_open:
                warnings.append("Env file permissions are too open; recommended: chmod 600 <env-file>.")
        except Exception:
            checks.append({"name": "env_permissions_posix", "ok": None})

    # Git safety check (best-effort)
    try:
        if _is_git_repo(env_file.parent):
            tracked = _is_file_tracked_by_git(env_file)
            checks.append({"name": "env_git_tracked", "ok": not tracked, "tracked": tracked})
            if tracked:
                warnings.append("Env file appears to be tracked by git. Remove it from the repository and rotate the token.")
    except Exception:
        pass

    # Parse config (does not call the API)
    try:
        cfg = load_config(str(env_file))
        checks.append({"name": "env_parse", "ok": True})
    except Exception as e:  # noqa: BLE001
        ctx["out"].emit(
            {
                "ok": False,
                "command": "config.check",
                "error_type": "InvalidConfig",
                "error": str(e),
                "env_file": str(env_file),
            }
        )
        return 1

    missing: list[str] = []
    if not str(cfg.base_url or "").strip():
        missing.append("CLOUDFLARE_API_BASE_URL")
    if not cfg.token:
        missing.append("CLOUDFLARE_API_TOKEN")

    ok = len(missing) == 0
    checks.append({"name": "required_keys_present", "ok": ok, "missing": missing})

    out = {
        "ok": ok,
        "command": "config.check",
        "env_file": str(env_file),
        "base_url": cfg.base_url,
        "token_present": bool(cfg.token),
        "token_fingerprint": cfg.token_fingerprint,
        "connect_timeout_s": float(cfg.connect_timeout_s),
        "read_timeout_s": float(cfg.read_timeout_s),
        "checks": checks,
        "warnings": warnings,
    }
    ctx["out"].emit(out)
    return 0 if ok else 1

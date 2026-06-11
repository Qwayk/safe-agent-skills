from __future__ import annotations

import os
import time
from typing import Any

from ..runtime import get_api


def add_theme_commands(theme_sub) -> None:
    theme_upload = theme_sub.add_parser("upload", help="Upload a theme zip (dry-run by default)")
    theme_upload.add_argument("--file", required=True, help="Path to theme zip file")
    theme_upload.add_argument("--upload-name", default=None, help="Optional upload filename (sanitized)")
    theme_upload.set_defaults(func=cmd_theme_upload)

    theme_activate = theme_sub.add_parser(
        "activate",
        help="Activate a theme (high-impact; dry-run by default; apply requires --yes --plan-in --ack-theme-change)",
    )
    theme_activate.add_argument("--name", required=True, help="Theme name to activate (from theme object name)")
    theme_activate.set_defaults(func=cmd_theme_activate)


def _extract_theme(obj: dict[str, Any], *, label: str) -> dict[str, Any]:
    themes = obj.get("themes") or []
    if not isinstance(themes, list) or not themes or not isinstance(themes[0], dict):
        raise RuntimeError(f"Unexpected response (missing themes list) for {label}")
    return themes[0]


def cmd_theme_upload(args, ctx) -> int:
    file_path = str(args.file)
    if not os.path.exists(file_path):
        raise RuntimeError(f"File not found: {file_path}")
    size = os.path.getsize(file_path)

    if not ctx["apply"]:
        ctx["out"].print(
            {
                "apply": False,
                "refused": False,
                "upload": {"file": file_path, "bytes": size, "upload_name": args.upload_name},
            }
        )
        return 0

    api = get_api(ctx)
    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-theme.upload"
        backup.write_before_after(
            kind="theme",
            resource_id=os.path.basename(file_path),
            slug=None,
            action="theme.upload",
            before=None,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "file": os.path.basename(file_path)},
        )

    res = api.themes_upload(file_path=file_path, upload_name=args.upload_name)
    theme = _extract_theme(res, label="upload")
    ctx["audit"].write("theme.upload", {"apply": True, "name": theme.get("name")})

    if backup is not None:
        backup.write_before_after(
            kind="theme",
            resource_id=str(theme.get("name") or os.path.basename(file_path)),
            slug=None,
            action="theme.upload",
            before=None,
            after=res,
            meta={"stage": "after", "correlation_id": correlation_id},
        )

    ctx["out"].print({"ok": True, "uploaded": {"name": theme.get("name"), "active": theme.get("active")}})
    return 0


def cmd_theme_activate(args, ctx) -> int:
    theme_name = str(args.name).strip()
    if not theme_name:
        raise RuntimeError("--name is required")

    if not ctx["apply"]:
        ctx["out"].print({"apply": False, "refused": False, "activate": {"name": theme_name}})
        return 0

    if not bool(ctx.get("ack_theme_change")):
        ctx["out"].print(
            {
                "ok": True,
                "apply": True,
                "refused": True,
                "reasons": ["Refused: theme activation requires --ack-theme-change"],
                "activate": {"name": theme_name},
            }
        )
        return 0

    api = get_api(ctx)
    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-theme.activate"
        backup.write_before_after(
            kind="theme",
            resource_id=theme_name,
            slug=None,
            action="theme.activate",
            before=None,
            after=None,
            meta={"stage": "before", "correlation_id": correlation_id, "name": theme_name},
        )

    res = api.themes_activate(theme_name)
    theme = _extract_theme(res, label="activate")
    if theme.get("name") != theme_name:
        raise RuntimeError("Verification failed: activated theme name mismatch")
    if theme.get("active") is not True:
        raise RuntimeError("Verification failed: theme not active after activate response")

    ctx["audit"].write("theme.activate", {"apply": True, "name": theme_name})
    if backup is not None:
        backup.write_before_after(
            kind="theme",
            resource_id=theme_name,
            slug=None,
            action="theme.activate",
            before=None,
            after=res,
            meta={"stage": "after", "correlation_id": correlation_id},
        )

    ctx["out"].print({"ok": True, "activated": {"name": theme_name}})
    return 0


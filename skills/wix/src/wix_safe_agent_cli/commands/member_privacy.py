from __future__ import annotations

from . import member_abouts as _base


COMMAND_FAMILY = "member-privacy"
DEFAULT_PRIVACY_PATH = "/members/v1/default-privacy-status"
PRIVACY_SETTINGS_PATH = "/members/v1/privacy-settings"


def _require_settings_revision(body: dict) -> None:
    settings = body.get("memberPrivacySettings")
    if not isinstance(settings, dict) or not str(settings.get("revision") or "").strip():
        raise _base.ValidationError("--settings-json must include memberPrivacySettings.revision for set-settings")


def _run_read(*, method_name: str, http_method: str, path: str, body: dict | None, ctx: dict) -> int:
    original_family = _base.COMMAND_FAMILY
    try:
        _base.COMMAND_FAMILY = COMMAND_FAMILY
        return _base._run_read(method_name=method_name, http_method=http_method, path=path, body=body, ctx=ctx)
    finally:
        _base.COMMAND_FAMILY = original_family


def _run_write(
    *,
    method_name: str,
    http_method: str,
    path: str,
    body: dict | None,
    selector: dict,
    proposed_changes: list[dict],
    ctx: dict,
    requires_ack: bool,
    risk_reasons: list[str],
    verification_notes: str,
) -> int:
    original_family = _base.COMMAND_FAMILY
    try:
        _base.COMMAND_FAMILY = COMMAND_FAMILY
        return _base._run_write(
            method_name=method_name,
            http_method=http_method,
            path=path,
            body=body,
            selector=selector,
            proposed_changes=proposed_changes,
            ctx=ctx,
            requires_ack=requires_ack,
            risk_reasons=risk_reasons,
            verification_notes=verification_notes,
        )
    finally:
        _base.COMMAND_FAMILY = original_family


def cmd_member_privacy_get_default(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-default"
    try:
        return _run_read(method_name=method, http_method="GET", path=DEFAULT_PRIVACY_PATH, body=None, ctx=ctx)
    except Exception as exc:
        return _base._emit_error(ctx, method=method, exc=exc)


def cmd_member_privacy_set_default(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.set-default"
    try:
        body = _base._read_json_arg(getattr(args, "privacy_json", None), field="privacy-json")
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=DEFAULT_PRIVACY_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "set-default"},
            proposed_changes=[{"operation": "set-default-privacy-status", "body": body}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["default-member-privacy-update", "developer-preview"],
            verification_notes="Provider response confirms the Set Default Privacy Status request was accepted.",
        )
    except Exception as exc:
        return _base._emit_error(ctx, method=method, exc=exc)


def cmd_member_privacy_get_settings(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-settings"
    try:
        return _run_read(method_name=method, http_method="GET", path=PRIVACY_SETTINGS_PATH, body=None, ctx=ctx)
    except Exception as exc:
        return _base._emit_error(ctx, method=method, exc=exc)


def cmd_member_privacy_set_settings(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.set-settings"
    try:
        body = _base._read_json_arg(getattr(args, "settings_json", None), field="settings-json")
        _require_settings_revision(body)
        return _run_write(
            method_name=method,
            http_method="POST",
            path=PRIVACY_SETTINGS_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "set-settings"},
            proposed_changes=[{"operation": "set-member-privacy-settings", "body": body}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["member-privacy-settings-update", "requires-current-revision", "affects-all-current-members"],
            verification_notes="Provider response confirms the Set Member Privacy Settings request was accepted.",
        )
    except Exception as exc:
        return _base._emit_error(ctx, method=method, exc=exc)

from __future__ import annotations

import argparse
import contextlib
import hashlib
import hmac
import json
import os
import stat
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypedDict, cast

from . import OPERATIONS, __version__
from .config import BASE_URL, Config, load_config
from .errors import HttpResponseError, SafetyError, StateError, ToolError, ValidationError
from .http import HttpClient
from .output import Output
from .redaction import redact
from .safety import (
    PLAN_REQUIRED_ACKS,
    PLAN_SCHEMA_VERSION,
    assert_any_whois_update,
    build_plan_hmac,
    parse_auth_code,
    parse_country_code,
    parse_flag,
    parse_nameserver,
    parse_sale_price,
    parse_timeout_s,
    validate_domain,
)
from .state import ensure_private_directory, read_plan_key, write_private_bytes, write_private_json


class _JSONArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


class OperationLike(TypedDict):
    command_path: str
    operation_id: str
    http_method: str
    kind: str
    required_params: list[dict[str, object]]


PLAN_REQUIRED_ACKS_TUPLE = list(PLAN_REQUIRED_ACKS)
SNAPSHOT_STATUS = "unavailable"
SNAPSHOT_REASON = (
    "The official SAV collection does not document a reliable before-state response "
    "for this operation."
)
TRANSFER_AUTH_FILE_FLAG = "--auth-code-file"


def _operation_map() -> dict[tuple[str, str], OperationLike]:
    by_path: dict[tuple[str, str], OperationLike] = {}
    for op in OPERATIONS:
        section, action = op["command_path"].split(" ", 1)
        by_path[(section, action)] = cast(OperationLike, op)
    return by_path


def _operation_required_params(op: OperationLike) -> list[dict[str, object]]:
    if op["operation_id"] == "submit_auth_code_for_pending_transfer_in":
        out: list[dict[str, object]] = []
        for raw in op["required_params"]:
            param = dict(raw)
            if str(param["name"]) == "auth_code":
                param["required"] = False
                param["cli_flag"] = TRANSFER_AUTH_FILE_FLAG
            out.append(param)
        return out
    return op["required_params"]


def _arg_type_for_param(param_name: str) -> Callable[[str], str]:
    if param_name in {"enabled", "update_registrant", "update_admin", "update_tech"}:
        return lambda raw: parse_flag(raw, name=param_name)
    if param_name == "sale_price":
        return parse_sale_price
    if param_name == "country":
        return parse_country_code
    if param_name in {"ns_1", "ns_2"}:
        return lambda raw: parse_nameserver(raw, label=param_name.replace("_", "-"))
    return str


def build_parser() -> argparse.ArgumentParser:
    by_path = _operation_map()
    parser = _JSONArgumentParser(prog="sav")
    parser.add_argument("--version", action="store_true", help="Print tool version")
    parser.add_argument("--env-file", default=".env", help="Path to .env file")
    parser.add_argument("--output", choices=("json", "text"), default="json", help="Output mode")
    parser.add_argument("--timeout-s", type=str, default=None, help="HTTP timeout in seconds")
    parser.add_argument("--apply", action="store_true", help="Apply an existing write plan")
    parser.add_argument("--yes", action="store_true", help="Confirm write apply")
    parser.add_argument("--ack-no-snapshot", action="store_true", help="Confirm no-snapshot write")
    parser.add_argument("--ack-high-risk", action="store_true", help="Confirm high-risk write")
    parser.add_argument("--plan-out", default=None, help="Write dry-run plan JSON to a path")
    parser.add_argument("--plan-in", default=None, help="Read and apply a saved plan JSON")
    parser.add_argument("--receipt-out", default=None, help="Write apply receipt JSON to a path")

    subs = parser.add_subparsers(dest="section", required=False)
    sections: dict[str, list[tuple[str, OperationLike]]] = {}
    for (section, action), op in by_path.items():
        sections.setdefault(section, []).append((action, op))

    for section_name, actions in sections.items():
        section_parser = subs.add_parser(section_name, help=section_name)
        action_sub = section_parser.add_subparsers(dest="action", required=True)
        for action_name, op in actions:
            action_parser = action_sub.add_parser(action_name, help=op["operation_id"])
            for raw in _operation_required_params(op):
                action_parser.add_argument(
                    str(raw["cli_flag"]),
                    required=bool(raw.get("required", False)),
                    dest=str(raw["name"]),
                    type=_arg_type_for_param(str(raw["name"])),
                    help=(
                        f"{raw['name']} (required)"
                        if bool(raw.get("required", False))
                        else f"{raw['name']} (dry-run only)"
                    ),
                )

    return parser


def _env_dir(*, env_file: str) -> Path:
    return Path(os.path.abspath(env_file)).parent


def _state_dirs(*, env_file: str) -> tuple[Path, Path, Path, Path]:
    base = _env_dir(env_file=env_file)
    state_dir = base / ".state"
    return (
        state_dir,
        state_dir / "plans",
        state_dir / "receipts",
        state_dir / "keys",
    )


def _default_plan_path(*, env_file: str, plan_id: str) -> Path:
    return _state_dirs(env_file=env_file)[1] / f"{plan_id}.plan.json"


def _default_receipt_path(*, env_file: str, plan_id: str) -> Path:
    return _state_dirs(env_file=env_file)[2] / f"{plan_id}.receipt.json"


def _key_path(*, env_file: str) -> Path:
    return _state_dirs(env_file=env_file)[3] / "plan-hmac.key"


def _ensure_private_state(*, env_file: str) -> tuple[Path, Path, Path]:
    state_dir, plans_dir, receipts_dir, keys_dir = (*_state_dirs(env_file=env_file),)
    root = _env_dir(env_file=env_file)
    ensure_private_directory(state_dir, stop_at=root)
    ensure_private_directory(plans_dir, stop_at=root)
    ensure_private_directory(receipts_dir, stop_at=root)
    ensure_private_directory(keys_dir, stop_at=root)
    return plans_dir, receipts_dir, keys_dir


def _load_or_create_signing_key(*, env_file: str) -> tuple[bytes, Path]:
    _plans_dir, _receipts_dir, keys_dir = _ensure_private_state(env_file=env_file)
    key_path = keys_dir / "plan-hmac.key"
    if key_path.exists():
        return read_plan_key(key_path), key_path

    key = os.urandom(32)
    write_private_bytes(key_path, key, stop_at=_env_dir(env_file=env_file))
    return key, key_path


def _load_signing_key(*, env_file: str) -> tuple[bytes, Path]:
    _ensure_private_state(env_file=env_file)
    key_path = _key_path(env_file=env_file)
    return read_plan_key(key_path), key_path


def _read_auth_code_file(raw_path: str) -> str:
    path = Path(raw_path)
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        if path.parent.is_symlink() or stat.S_IMODE(path.parent.stat().st_mode) != 0o700:
            raise ValidationError("Invalid --auth-code-file")
        fd = os.open(str(path), flags)
        try:
            st = os.fstat(fd)
            if not stat.S_ISREG(st.st_mode) or stat.S_IMODE(st.st_mode) != 0o600:
                raise ValidationError("--auth-code-file must be mode 0600")
            raw_bytes = b""
            while True:
                chunk = os.read(fd, 4096)
                if not chunk:
                    break
                raw_bytes += chunk
        finally:
            with contextlib.suppress(OSError):
                os.close(fd)
        value = raw_bytes.decode("utf-8")
        lines = value.splitlines()
    except (OSError, UnicodeError) as exc:
        raise ValidationError("Unable to read --auth-code-file") from exc
    if len(lines) != 1:
        raise ValidationError("--auth-code-file must contain exactly one non-empty line")
    value = lines[0].strip()
    if not value:
        raise ValidationError("--auth-code-file cannot be empty")
    return parse_auth_code(value)


def _canonicalize_query_value(name: str, value: object) -> str:
    raw = ("" if value is None else str(value)).strip()
    if name == "domain_name":
        return validate_domain(raw)
    if name == "auth_code":
        return parse_auth_code(raw)
    if name in {"enabled", "update_registrant", "update_admin", "update_tech"}:
        return parse_flag(raw, name=name)
    if name == "sale_price":
        return parse_sale_price(raw)
    if name in {"ns_1", "ns_2"}:
        return parse_nameserver(raw, label=name.replace("_", "-"))
    if name == "country":
        return parse_country_code(raw)
    if name in {
        "name",
        "organization",
        "email_address",
        "street",
        "city",
        "state",
        "postal_code",
        "phone",
    }:
        if not raw:
            raise ValidationError(f"{name.replace('_', '-')} cannot be empty")
        return raw
    return raw


def _build_query(op: OperationLike, args: argparse.Namespace, *, auth_code: str | None = None) -> dict[str, str]:
    out: dict[str, str] = {}
    for param in op["required_params"]:
        key = str(param["name"])
        raw = args.__dict__.get(key)
        if key == "auth_code" and auth_code is not None:
            raw = auth_code
        if raw is None:
            raise ValidationError(f"{key.replace('_', '-')} is required")
        out[key] = _canonicalize_query_value(key, raw)

    if op["operation_id"] == "update_domain_whois_contacts":
        assert_any_whois_update(
            update_registrant=out["update_registrant"],
            update_admin=out["update_admin"],
            update_tech=out["update_tech"],
        )
    return out


def _normalize_plan_params(op: OperationLike, params: dict[str, Any]) -> dict[str, str]:
    required = [str(raw["name"]) for raw in op["required_params"]]
    if set(params.keys()) != set(required):
        raise ValidationError("Plan params are invalid")
    normalized: dict[str, str] = {}
    for name in required:
        if not isinstance(name, str):
            raise ValidationError("Plan params are invalid")
        if name not in params:
            raise ValidationError("Plan params are missing")
        normalized[name] = _canonicalize_query_value(name, params[name])

    if op["operation_id"] == "update_domain_whois_contacts":
        assert_any_whois_update(
            update_registrant=normalized["update_registrant"],
            update_admin=normalized["update_admin"],
            update_tech=normalized["update_tech"],
        )

    return normalized


def _load_plan_json(path: Path) -> dict[str, Any]:
    try:
        if path.suffix != ".json":
            raise ValidationError("Malformed plan JSON")

        if path.is_symlink():
            raise ValidationError("Malformed plan file")
        if not path.is_file():
            raise ValidationError("Plan file is not valid")
        if path.parent.is_symlink() or stat.S_IMODE(path.parent.stat().st_mode) != 0o700:
            raise SafetyError("Plan parent directory must use private mode 0700")
        if stat.S_IMODE(path.stat().st_mode) != 0o600:
            raise SafetyError("Plan file must use private mode 0600")
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise StateError("Plan file is not valid") from exc

    def _reject_dupes(pairs: list[tuple[str, object]]) -> dict[str, object]:
        out: dict[str, object] = {}
        for key, value in pairs:
            if key in out:
                raise ValidationError("Malformed plan JSON")
            out[key] = value
        return out

    try:
        loaded = json.loads(
            raw,
            object_pairs_hook=_reject_dupes,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError("invalid numeric constant")),
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValidationError("Malformed plan JSON") from exc

    if not isinstance(loaded, dict):
        raise ValidationError("Malformed plan JSON")
    return cast(dict[str, Any], loaded)


def _validate_plan(
    plan_path: str,
    *,
    op: OperationLike,
    command: str,
    env_file: str,
    args: argparse.Namespace,
) -> tuple[dict[str, Any], bytes]:
    if not Path(plan_path).exists():
        raise ValidationError("Plan file not found")
    plan = _load_plan_json(Path(plan_path))
    required_keys = {
        "schema_version",
        "plan_id",
        "key_id",
        "command",
        "operation_id",
        "endpoint",
        "method",
        "params",
        "required_acks",
        "snapshot_status",
        "snapshot_reason",
        "independent_readback_available",
        "rollback_available",
        "plan_hmac",
    }
    if set(plan.keys()) != required_keys:
        raise ValidationError("Plan schema is invalid")

    if not isinstance(plan.get("schema_version"), int) or int(plan["schema_version"]) != PLAN_SCHEMA_VERSION:
        raise ValidationError("Invalid plan schema version")
    if not isinstance(plan.get("plan_id"), str) or not plan.get("plan_id"):
        raise ValidationError("Plan is missing an id")
    if plan.get("command") != command:
        raise SafetyError("Plan command does not match")
    if plan.get("operation_id") != op["operation_id"]:
        raise SafetyError("Plan operation does not match")
    if plan.get("endpoint") != f"{BASE_URL}/{op['operation_id']}":
        raise SafetyError("Plan endpoint does not match")
    if plan.get("method") != op["http_method"]:
        raise SafetyError("Plan method does not match")
    if plan.get("required_acks") != PLAN_REQUIRED_ACKS_TUPLE:
        raise ValidationError("Plan approvals field is invalid")
    if plan.get("snapshot_status") != SNAPSHOT_STATUS:
        raise ValidationError("snapshot_status is invalid")
    if plan.get("snapshot_reason") != SNAPSHOT_REASON:
        raise ValidationError("snapshot_reason is invalid")
    if plan.get("independent_readback_available") is not False:
        raise ValidationError("independent_readback_available is invalid")
    if plan.get("rollback_available") is not False:
        raise ValidationError("rollback_available is invalid")

    if (
        not isinstance(plan.get("key_id"), str)
        or len(plan["key_id"]) != 64
        or any(ch not in "0123456789abcdef" for ch in plan["key_id"])
    ):
        raise SafetyError("Plan key reference is invalid")

    signing_key, _ = _load_signing_key(env_file=env_file)
    if hashlib.sha256(signing_key).hexdigest() != str(plan["key_id"]):
        raise SafetyError("Plan key is invalid")

    if (
        not isinstance(plan.get("plan_hmac"), str)
        or len(plan["plan_hmac"]) != 64
        or any(ch not in "0123456789abcdef" for ch in plan["plan_hmac"])
    ):
        raise ValidationError("Plan signature is invalid")
    public_plan = dict(plan)
    public_plan.pop("plan_hmac")
    if not hmac.compare_digest(
        build_plan_hmac(public_plan, signing_key),
        cast(str, plan["plan_hmac"]),
    ):
        raise SafetyError("Plan signature mismatch")

    if not isinstance(plan.get("params"), dict):
        raise ValidationError("Plan params are invalid")
    normalized_params = _normalize_plan_params(op, cast(dict[str, Any], plan["params"]))
    if normalized_params != cast(dict[str, Any], plan["params"]):
        raise SafetyError("Plan params are not normalized")

    query = _build_query(op, args, auth_code=normalized_params.get("auth_code"))
    if query != normalized_params:
        raise SafetyError("Plan command payload mismatch")

    return plan, signing_key


def _build_plan(op: OperationLike, args: argparse.Namespace, *, key: bytes) -> dict[str, Any]:
    command = f"sav {op['command_path']}"
    params = _build_query(op, args)
    payload: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "plan_id": hashlib.sha256(os.urandom(16)).hexdigest(),
        "key_id": hashlib.sha256(key).hexdigest(),
        "command": command,
        "operation_id": op["operation_id"],
        "endpoint": f"{BASE_URL}/{op['operation_id']}",
        "method": op["http_method"],
        "params": params,
        "required_acks": PLAN_REQUIRED_ACKS_TUPLE,
        "snapshot_status": SNAPSHOT_STATUS,
        "snapshot_reason": SNAPSHOT_REASON,
        "independent_readback_available": False,
        "rollback_available": False,
    }
    payload["plan_hmac"] = build_plan_hmac(payload, key)
    return payload


def _write_private_payload(path: Path, payload: dict[str, Any], *, env_file: str) -> None:
    write_private_json(path, payload, stop_at=_env_dir(env_file=env_file))


def _receipt_verification(*, independent_readback_available: bool, provider_response_received: bool) -> str:
    if provider_response_received:
        return (
            "SAV returned a provider response. No independent readback was available."
            if not independent_readback_available
            else "SAV returned a provider response."
        )
    return "SAV request was prepared but no provider response was received."


def _build_apply_receipt(
    *,
    plan: dict[str, Any],
    op: OperationLike,
    status: int | None,
    response: object | None,
    request_attempted: bool | str,
    provider_response_received: bool,
) -> dict[str, Any]:
    snapshot_status = str(plan.get("snapshot_status"))
    independent_readback = bool(plan.get("independent_readback_available", False))
    rollback_available = bool(plan.get("rollback_available", False))
    provider_2xx = status is not None and 200 <= status <= 299
    outcome = (
        "unknown"
        if not provider_response_received
        else ("provider_accepted" if provider_2xx else "failure")
    )
    return {
        "command": f"sav {op['command_path']}",
        "operation_id": op["operation_id"],
        "plan_id": plan.get("plan_id"),
        "request_attempted": request_attempted,
        "provider_response_received": provider_response_received,
        "outcome": outcome,
        "provider_received": provider_response_received,
        "provider_status": status,
        "provider_2xx": provider_2xx,
        "provider_response_only": provider_response_received,
        "snapshot_status": snapshot_status,
        "snapshot_reason": str(plan.get("snapshot_reason", "")),
        "independent_readback_available": independent_readback,
        "rollback_available": rollback_available,
        "verification": _receipt_verification(
            independent_readback_available=independent_readback,
            provider_response_received=provider_response_received,
        ),
        "response": redact(response) if response is not None else None,
    }


def _resolve_receipt_path(*, args: argparse.Namespace, plan: dict[str, Any], env_file: str) -> Path:
    return Path(
        args.receipt_out
        or str(_default_receipt_path(env_file=str(env_file), plan_id=str(plan["plan_id"])))
    )


def _run_read(op: OperationLike, *, args: argparse.Namespace, cfg: Config, out: Output) -> int:
    query = _build_query(op, args)
    response = HttpClient(timeout_s=cfg.timeout_s).get(
        url=f"{BASE_URL}/{op['operation_id']}",
        headers={"APIKEY": cfg.api_key or ""},
        params=query,
    )
    out.emit(
        {
            "ok": True,
            "dry_run": False,
            "command": f"sav {op['command_path']}",
            "operation_id": op["operation_id"],
            "api_host": BASE_URL,
            "read": {
                "status": response.status,
                "response": redact(response.json_body),
            },
        }
    )
    return 0


def _safe_write_gates(op: OperationLike, args: argparse.Namespace) -> None:
    if op["kind"] == "read" and bool(args.apply):
        raise SafetyError("Read commands do not use write plans or apply flags")

    if bool(args.apply) and args.plan_out is not None:
        raise SafetyError("Conflicting params: --apply cannot be used with --plan-out")
    if not bool(args.apply) and args.plan_in is not None:
        raise SafetyError("Conflicting params: --plan-in requires --apply")

    if not bool(args.apply):
        return

    missing = [
        name
        for name, enabled in [
            ("--apply", bool(args.apply)),
            ("--yes", bool(args.yes)),
            ("--ack-no-snapshot", bool(args.ack_no_snapshot)),
            ("--ack-high-risk", bool(args.ack_high_risk)),
        ]
        if not enabled
    ]
    if missing:
        raise SafetyError("Missing required write approvals: " + ", ".join(missing))
    if not args.plan_in:
        raise SafetyError("Write apply requires --plan-in")
    if (
        op["operation_id"] == "submit_auth_code_for_pending_transfer_in"
        and args.__dict__.get("auth_code") is not None
    ):
        raise SafetyError("Do not provide --auth-code-file when applying a plan")


def _run_write(
    op: OperationLike,
    *,
    args: argparse.Namespace,
    cfg: Config | None,
    out: Output,
) -> int:
    command = f"sav {op['command_path']}"

    if not bool(args.apply):
        if args.plan_out is not None and Path(str(args.plan_out)).suffix != ".json":
            raise ValidationError("Plan output must be a JSON file")

        auth_code = None
        if op["operation_id"] == "submit_auth_code_for_pending_transfer_in":
            raw = args.__dict__.get("auth_code")
            if raw is None:
                raise ValidationError("--auth-code-file is required")
            auth_code = _read_auth_code_file(str(raw))

        _ = _build_query(op, args, auth_code=auth_code)
        signing_key, _ = _load_or_create_signing_key(env_file=str(args.env_file))
        plan = _build_plan(op, args=NamespaceProxy(args, auth_code=auth_code), key=signing_key)

        plan_path = Path(
            args.plan_out
            or str(_default_plan_path(env_file=str(args.env_file), plan_id=str(plan["plan_id"])) )
        )
        _write_private_payload(plan_path, plan, env_file=str(args.env_file))
        out.emit(
            {
                "ok": True,
                "dry_run": True,
                "command": command,
                "operation_id": op["operation_id"],
                "plan_path": str(plan_path),
                "plan": redact(plan),
            }
        )
        return 0

    plan, _ = _validate_plan(
        str(args.plan_in),
        op=op,
        command=command,
        env_file=str(args.env_file),
        args=args,
    )
    if cfg is None:
        raise ValidationError("Missing authentication for apply path")

    query = _build_query(
        op,
        args,
        auth_code=str(cast(dict[str, Any], plan["params"]).get("auth_code", "")),
    )
    receipt_path = _resolve_receipt_path(args=args, plan=plan, env_file=str(args.env_file))
    pre_receipt = _build_apply_receipt(
        plan=plan,
        op=op,
        status=None,
        response=None,
        request_attempted="unknown",
        provider_response_received=False,
    )
    try:
        _write_private_payload(
            receipt_path,
            {"ok": False, "receipt": pre_receipt},
            env_file=str(args.env_file),
        )
    except StateError as exc:
        out.emit(
            {
                "ok": False,
                "command": command,
                "operation_id": op["operation_id"],
                "provider_received": False,
                "provider_response_received": False,
                "provider_status": None,
                "provider_2xx": False,
                "outcome": "not_attempted",
                "durable_state_verified": False,
                "receipt_written": False,
                "retry": "fix-receipt-path-before-retry",
                "error": str(exc),
                "error_type": "StateError",
            }
        )
        return 1

    try:
        response = HttpClient(timeout_s=cfg.timeout_s).get(
            url=f"{BASE_URL}/{op['operation_id']}",
            headers={"APIKEY": cfg.api_key or ""},
            params=query,
        )
    except HttpResponseError as exc:
        is_redirect_like = 300 <= exc.status < 400
        response_receipt = _build_apply_receipt(
            plan=plan,
            op=op,
            status=exc.status,
            response=exc.response,
            request_attempted=True,
            provider_response_received=True,
        )
        try:
            _write_private_payload(
                receipt_path,
                {"ok": False, "receipt": response_receipt},
                env_file=str(args.env_file),
            )
            out.emit(
                {
                    "ok": False,
                    "command": command,
                    "operation_id": op["operation_id"],
                    "provider_received": True,
                    "provider_response_received": True,
                    "provider_status": exc.status,
                    "provider_2xx": False,
                    "outcome": "failure",
                    "durable_state_verified": False,
                    "receipt_written": True,
                    "receipt_path": str(receipt_path),
                    "receipt": response_receipt,
                    "error": str(exc),
                    "error_type": "ValidationError" if is_redirect_like else "RuntimeError",
                    "retry": "do-not-retry",
                }
            )
            return 1
        except StateError as write_exc:
            out.emit(
                {
                    "ok": False,
                    "command": command,
                    "operation_id": op["operation_id"],
                    "provider_received": True,
                    "provider_response_received": True,
                    "provider_status": exc.status,
                    "provider_2xx": False,
                    "outcome": "failure",
                    "durable_state_verified": False,
                    "receipt_written": False,
                    "receipt": response_receipt,
                    "error": str(write_exc),
                    "error_type": "StateError",
                    "retry": "do-not-retry",
                }
            )
            return 1

    except ToolError as exc:
        request_exception_receipt = _build_apply_receipt(
            plan=plan,
            op=op,
            status=None,
            response=None,
            request_attempted=True,
            provider_response_received=False,
        )
        receipt_written = True
        try:
            _write_private_payload(
                receipt_path,
                {"ok": False, "receipt": request_exception_receipt},
                env_file=str(args.env_file),
            )
        except StateError:
            receipt_written = False
        out.emit(
            {
                "ok": False,
                "command": command,
                "operation_id": op["operation_id"],
                "provider_received": False,
                "provider_response_received": False,
                "provider_status": None,
                "provider_2xx": False,
                "outcome": "unknown",
                "durable_state_verified": False,
                "receipt_written": receipt_written,
                "receipt_path": str(receipt_path),
                "receipt": request_exception_receipt,
                "error": str(exc),
                "error_type": type(exc).__name__,
                "retry": "do-not-retry",
            }
        )
        return 1

    provider_status = response.status
    provider_receipt = _build_apply_receipt(
        plan=plan,
        op=op,
        status=provider_status,
        response=response.json_body,
        request_attempted=True,
        provider_response_received=True,
    )
    provider_ok = 200 <= provider_status <= 299
    try:
        _write_private_payload(
            receipt_path,
            {"ok": provider_ok, "receipt": provider_receipt},
            env_file=str(args.env_file),
        )
    except StateError as exc:
        out.emit(
            {
                "ok": False,
                "command": command,
                "operation_id": op["operation_id"],
                "provider_received": True,
                "provider_response_received": True,
                "provider_status": provider_status,
                "provider_2xx": provider_ok,
                "outcome": "provider_accepted" if provider_ok else "failure",
                "durable_state_verified": False,
                "receipt_written": False,
                "receipt": provider_receipt,
                "error": str(exc),
                "error_type": "StateError",
                "retry": "do-not-retry",
            }
        )
        return 1

    if provider_ok:
        out.emit(
            {
                "ok": True,
                "dry_run": False,
                "command": command,
                "operation_id": op["operation_id"],
                "receipt_path": str(receipt_path),
                "receipt": provider_receipt,
                "provider_received": True,
                "provider_response_received": True,
                "provider_status": provider_status,
                "provider_2xx": True,
                "outcome": "provider_accepted",
                "durable_state_verified": False,
                "receipt_written": True,
            }
        )
        return 0

    out.emit(
        {
            "ok": False,
            "command": command,
            "operation_id": op["operation_id"],
            "provider_received": True,
            "provider_response_received": True,
            "provider_status": provider_status,
            "provider_2xx": False,
            "outcome": "failure",
            "durable_state_verified": False,
            "receipt_written": True,
            "receipt_path": str(receipt_path),
            "receipt": provider_receipt,
            "error": f"Provider request failed: HTTP {provider_status}",
            "error_type": "RuntimeError",
            "retry": "do-not-retry",
        }
    )
    return 1


class NamespaceProxy(argparse.Namespace):
    def __init__(self, base: argparse.Namespace, **updates: Any) -> None:
        self.__dict__.update(base.__dict__)
        self.__dict__.update(updates)



def main(argv: list[str] | None = None) -> int:
    argv = list(argv or [])
    parser = build_parser()
    output_mode = "json"
    for idx, value in enumerate(argv):
        if value == "--output" and idx + 1 < len(argv):
            output_mode = argv[idx + 1]
            break
    out = Output(mode=output_mode)

    try:
        args = parser.parse_args(argv)
        if bool(args.version):
            out.emit({"ok": True, "tool": "sav", "version": __version__})
            return 0

        if not args.section or not args.action:
            raise ValidationError("Missing command path")

        op = _operation_map().get((args.section, args.action))
        if op is None:
            raise ValidationError("Unknown command path")

        _safe_write_gates(op=op, args=args)

        if op["kind"] == "write":
            cfg = load_config(env_file=str(args.env_file), require_api_key=bool(args.apply))
            if args.timeout_s is not None:
                cfg = Config(
                    base_url=cfg.base_url,
                    api_key=cfg.api_key,
                    timeout_s=parse_timeout_s(args.timeout_s, field_name="--timeout-s"),
                )
            return _run_write(op=op, args=args, cfg=cfg if args.apply else None, out=out)

        cfg = load_config(env_file=str(args.env_file), require_api_key=True)
        if args.timeout_s is not None:
            cfg = Config(
                base_url=cfg.base_url,
                api_key=cfg.api_key,
                timeout_s=parse_timeout_s(args.timeout_s, field_name="--timeout-s"),
            )
        return _run_read(op=op, args=args, cfg=cfg, out=out)
    except SafetyError as exc:
        out.emit({"ok": True, "refused": True, "reason": str(exc), "error_type": "SafetyError"})
        return 0
    except ValueError:
        out.emit(
            {
                "ok": False,
                "error": "Invalid value",
                "error_type": "ValidationError",
                "parse_error": True,
            }
        )
        return 1
    except ValidationError as exc:
        out.emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "parse_error": True})
        return 1
    except StateError as exc:
        out.emit({"ok": False, "error": str(exc), "error_type": "StateError"})
        return 1
    except ToolError as exc:
        out.emit({"ok": False, "error": str(exc), "error_type": type(exc).__name__})
        return 1
    except RuntimeError as exc:
        out.emit({"ok": False, "error": str(exc), "error_type": "RuntimeError", "parse_error": False})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

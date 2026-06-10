from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ..auth import utc_now
from ..discovery import MethodSpec, iter_methods
from ..errors import SafetyError, ValidationError
from ..gtm_api import GtmApi
from ..json_files import read_json_file, write_json_file
from ..method_inventory import InventoryRow, build_inventory, to_kebab
from ..plan import build_plan, env_fingerprint, request_fingerprint, validate_plan_for_apply


_INVENTORY: list[InventoryRow] = build_inventory()
_METHODS_BY_ID: dict[str, MethodSpec] = {m.method_id: m for m in iter_methods()}
_REGISTERED: dict[str, tuple[str, ...]] | None = None
_BEFORE_STATE_ACTIONS = {"update", "delete", "publish", "set_latest"}


def inventory_rows() -> list[InventoryRow]:
    return list(_INVENTORY)


def method_spec(method_id: str) -> MethodSpec:
    m = _METHODS_BY_ID.get(method_id)
    if not m:
        raise ValidationError(f"Unknown method id: {method_id}")
    return m


def _is_write(method: MethodSpec) -> bool:
    risk_level, _ = _risk_level(method)
    return risk_level != "low"


def _mutating_family_missing_safe_before_state_read(method: MethodSpec) -> tuple[bool, str]:
    if not _is_write(method):
        return False, ""
    parts = method.method_id.rsplit(".", 1)
    if len(parts) != 2:
        return False, ""
    family = parts[0]
    if f"{family}.get" in _METHODS_BY_ID:
        return False, ""
    return True, family


def _no_snapshot_before_state(*, family_name: str) -> dict[str, Any]:
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "reason": f"GTM mutating family '{family_name}' has no safe read path for a saved before-state snapshot.",
    }


def _risk_level(method: MethodSpec) -> tuple[str, list[str]]:
    mid = method.method_id
    hm = method.http_method
    # Discovery includes one read-like POST (entities listing). Treat it as low-risk read.
    if mid == "tagmanager.accounts.containers.workspaces.folders.entities":
        return "low", ["read", "read_like_post"]
    if hm == "GET":
        return "low", ["read"]
    # Irreversible / production-impact operations.
    # - DELETE cannot be rolled back by the tool.
    # - publish changes what code is live; effects in production are not reliably reversible.
    if hm == "DELETE" or ".publish" in mid:
        return "irreversible", ["write", "irreversible"]

    # High-risk (batch / conflict resolution / linking / mass moves).
    high_markers = (
        ".combine",
        ".bulk_update",
        ".resolve_conflict",
        ".sync",
        ".move_tag_id",
        ".move_entities_to_folder",
        ".destinations.link",
        ".import_from_gallery",
        ".revert",
    )
    for m in high_markers:
        if m in mid:
            return "high", ["write", m.lstrip(".")]

    # Medium-risk: most single-resource creates/updates.
    if hm in {"POST", "PUT", "PATCH"}:
        # quick_preview has side effects in some UIs; keep it as medium.
        if ".quick_preview" in mid:
            return "medium", ["write", "preview"]
        return "medium", ["write"]

    # Fallback.
    return "high", ["write"]


def _normalize_api_path(path: str | None) -> str | None:
    p = str(path or "").strip()
    if not p:
        return None
    p = p.lstrip("/")
    if p.startswith("tagmanager/"):
        return p
    return f"tagmanager/v2/{p}"


def _resource_path_from_response(path: Any) -> str | None:
    if not isinstance(path, str):
        return None
    return _normalize_api_path(path.strip())


def _before_state_read_path(*, method: MethodSpec, request_path: str | None) -> str | None:
    """
    Return the concrete read path for supported before-state capture actions.

    We only capture before-state when the method family has a matching GET endpoint.
    """
    if not request_path:
        return None
    parts = method.method_id.rsplit(".", 1)
    if len(parts) != 2:
        return None
    family, action = parts
    if action not in _BEFORE_STATE_ACTIONS:
        return None
    if f"{family}.get" not in _METHODS_BY_ID:
        return None
    if ":" in request_path:
        return request_path.split(":", 1)[0]
    return request_path


def _capture_before_state(
    *,
    api: GtmApi,
    method: MethodSpec,
    request_path: str | None,
    read_retries: int,
    artifacts_dir: Path | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    read_path = _before_state_read_path(method=method, request_path=request_path)
    if not read_path:
        return None, None

    before_state: dict[str, Any] = {
        "attempted": True,
        "ok": None,
        "path": read_path,
        "status": None,
        "url": None,
        "body": None,
    }
    try:
        before_resp = api.request(
            http_method="GET",
            path=read_path,
            query=None,
            body=None,
            retries=read_retries,
        )
        before_state["ok"] = before_resp.status < 400
        before_state["status"] = before_resp.status
        before_state["url"] = before_resp.url
        before_state["body"] = before_resp.body_json
        if before_state["body"] is None:
            before_state["body"] = before_resp.body_text
    except Exception as e:  # noqa: BLE001
        before_state["ok"] = False
        before_state["error"] = f"{type(e).__name__}: {e}"
    artifact_path = None
    if isinstance(artifacts_dir, Path):
        try:
            artifact_path = write_json_file(artifacts_dir / "before_state.json", before_state)
            before_state["artifact_path"] = artifact_path
        except Exception as e:  # noqa: BLE001
            before_state["artifact_error"] = f"{type(e).__name__}: {e}"
    return before_state, artifact_path


def _build_write_recovery(
    *,
    method: MethodSpec,
    request_path: str,
    created_resource_path: str | None = None,
) -> dict[str, Any]:
    parts = method.method_id.rsplit(".", 1)
    if len(parts) != 2:
        return {
            "end_state": "irreversible_and_clearly_labeled",
            "strategy": "no_inverse",
            "reason": "Method id format does not allow recovery analysis",
            "rollback_ready": False,
            "rollback_plan": None,
        }

    family = parts[0]
    action = parts[1]

    if action in {"create", "update", "delete"}:
        revert_mid = f"{family}.revert"
        revert_method = _METHODS_BY_ID.get(revert_mid)
        if revert_method:
            return {
                "end_state": "rollback_by_inverse_action",
                "strategy": "revert",
                "reason": f"{method.method_id} can be rolled back using {revert_mid}.",
                "rollback_ready": True,
                "rollback_plan": {
                    "method_id": revert_mid,
                    "http_method": revert_method.http_method,
                    "path": request_path,
                },
            }

    if action == "delete":
        undelete_mid = f"{family}.undelete"
        undelete_method = _METHODS_BY_ID.get(undelete_mid)
        if undelete_method:
            return {
                "end_state": "rollback_by_inverse_action",
                "strategy": "undelete",
                "reason": f"{method.method_id} can be rolled back using {undelete_mid}.",
                "rollback_ready": True,
                "rollback_plan": {
                    "method_id": undelete_mid,
                    "http_method": undelete_method.http_method,
                    "path": request_path,
                },
            }

    if action == "create":
        delete_mid = f"{family}.delete"
        delete_method = _METHODS_BY_ID.get(delete_mid)
        if delete_method:
            rollback_path = _resource_path_from_response(created_resource_path)
            if rollback_path:
                return {
                    "end_state": "rollback_by_inverse_action",
                    "strategy": "delete_after_create",
                    "reason": f"{method.method_id} can be rolled back by deleting the created resource.",
                    "rollback_ready": True,
                    "rollback_plan": {
                        "method_id": delete_mid,
                        "http_method": delete_method.http_method,
                        "path": rollback_path,
                    },
                }

            return {
                "end_state": "rollback_by_inverse_action",
                "strategy": "delete_after_create",
                "reason": f"{method.method_id} can be rolled back by deleting the created resource path from the apply response.",
                "rollback_ready": False,
                "rollback_plan": {
                    "method_id": delete_mid,
                    "http_method": delete_method.http_method,
                    "path": None,
                },
            }

    return {
        "end_state": "irreversible_and_clearly_labeled",
        "strategy": "no_inverse",
        "reason": "No inverse action was found in GTM discovery methods.",
        "rollback_ready": False,
        "rollback_plan": None,
    }


def _parse_json_body(*, body_json: str | None, body_file: str | None) -> dict[str, Any] | None:
    if body_json and body_file:
        raise ValidationError("Use only one of --body-json or --body-file")
    if body_json:
        try:
            obj = json.loads(body_json)
        except Exception as e:  # noqa: BLE001
            raise ValidationError(f"--body-json must be valid JSON: {type(e).__name__}: {e}") from None
        if not isinstance(obj, dict):
            raise ValidationError("--body-json must be a JSON object")
        return obj
    if body_file:
        p = Path(body_file)
        if not p.exists():
            raise ValidationError(f"--body-file not found: {body_file}")
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            raise ValidationError(f"--body-file must be valid JSON: {type(e).__name__}: {e}") from None
        if not isinstance(obj, dict):
            raise ValidationError("--body-file must be a JSON object")
        return obj
    return None


def _parse_boolish(value: str) -> str:
    v = str(value or "").strip().lower()
    if v in {"1", "true", "t", "yes", "y"}:
        return "true"
    if v in {"0", "false", "f", "no", "n"}:
        return "false"
    raise ValidationError("Boolean query params must be one of: true/false/1/0")


def _parse_query_value(param_type: str | None, raw: str) -> Any:
    if param_type == "boolean":
        return _parse_boolish(raw)
    if param_type == "integer":
        try:
            return int(str(raw).strip())
        except Exception:
            raise ValidationError("Integer query params must be valid integers") from None
    return str(raw)


def _expand_path_template(path_template: str, path_params: dict[str, str]) -> str:
    # Discovery paths use patterns like: tagmanager/v2/{+parent}/tags
    out = str(path_template or "")
    for k, v in path_params.items():
        out = out.replace("{+" + k + "}", str(v).lstrip("/"))
        out = out.replace("{" + k + "}", str(v).lstrip("/"))
    if "{" in out or "}" in out:
        raise ValidationError(f"Unresolved path template: {path_template}")
    return out


def cmd_discovery_method(args: Any, ctx: dict[str, Any]) -> int:
    mid = str(getattr(args, "method_id", "") or "").strip()
    if not mid:
        raise ValidationError("Missing method id")
    method = method_spec(mid)

    path_params: dict[str, str] = {}
    query_params: dict[str, Any] = {}

    for p in method.parameters:
        flag_dest = p.name
        val = getattr(args, flag_dest, None)
        if p.required and (val is None or str(val).strip() == ""):
            raise ValidationError(f"Missing required --{to_kebab(p.name)}")
        if val is None:
            continue
        if p.location == "path":
            path_params[p.name] = str(val).strip()
        elif p.location == "query":
            query_params[p.name] = _parse_query_value(p.type, str(val))

    # System query params (global, optional).
    if getattr(args, "fields", None):
        query_params["fields"] = str(args.fields)
    if getattr(args, "quota_user", None):
        query_params["quotaUser"] = str(args.quota_user)
    if getattr(args, "pretty_print", None):
        query_params["prettyPrint"] = _parse_boolish(str(args.pretty_print))

    body = _parse_json_body(body_json=getattr(args, "body_json", None), body_file=getattr(args, "body_file", None))
    if method.request_ref and method.http_method in {"POST", "PUT", "PATCH"} and body is None:
        raise ValidationError("Missing request body (use --body-json or --body-file)")

    expanded_path = _expand_path_template(method.path, path_params)
    risk_level, risk_reasons = _risk_level(method)
    is_write = risk_level != "low"

    efp = env_fingerprint(ctx["cfg"])
    rfp = request_fingerprint(
        method_id=method.method_id,
        http_method=method.http_method,
        path_template=method.path,
        path_params=path_params,
        query=query_params,
        body=body,
    )

    if is_write:
        recovery = _build_write_recovery(method=method, request_path=expanded_path)
        before_state = None
        before_state_path = None
        missing_before_state, family_name = _mutating_family_missing_safe_before_state_read(method=method)
        if _before_state_read_path(method=method, request_path=expanded_path):
            api = GtmApi(
                cfg=ctx["cfg"],
                verbose=bool(ctx.get("verbose")),
                user_agent=f"{ctx['tool']}/{ctx['tool_version']}",
                timeout_s=ctx.get("timeout_s"),
            )
            before_state, before_state_path = _capture_before_state(
                api=api,
                method=method,
                request_path=expanded_path,
                read_retries=ctx["cfg"].read_retries,
                artifacts_dir=ctx.get("artifacts_dir") if isinstance(ctx.get("artifacts_dir"), Path) else None,
            )
        elif missing_before_state:
            before_state = _no_snapshot_before_state(family_name=family_name)
        plan = build_plan(
            tool=ctx["tool"],
            version=ctx["tool_version"],
            command=ctx.get("command_str"),
            cfg=ctx["cfg"],
            method_id=method.method_id,
            http_method=method.http_method,
            path_template=method.path,
            path_params=path_params,
            query=query_params,
            body=body,
            risk_level=risk_level,
            risk_reasons=risk_reasons,
        )
        plan["recovery"] = recovery
        if before_state is not None:
            plan["before_state"] = before_state
            if before_state_path:
                plan["before_state_path"] = before_state_path
            if not bool(before_state.get("supported", True)):
                plan.setdefault("notes", []).append(
                    "No saved before-state snapshot is available for this mutating family. Apply requires explicit --ack-no-snapshot approval."
                )
        plan_out = ctx.get("plan_out")
        plan_path = write_json_file(plan_out, plan) if plan_out else None

        if not bool(ctx.get("apply")):
            out = {
                "ok": True,
                "dry_run": True,
                "risk_level": risk_level,
                "plan": plan,
                "plan_out": plan_path,
            }
            ctx["audit"].write("method.plan", {"method_id": method.method_id, "plan_out": plan_path})
            ctx["out"].emit(out)
            return 0

        # Apply gate checks (must happen before any network).
        if missing_before_state and not bool(ctx.get("ack_no_snapshot")):
            raise SafetyError(
                f"Refused: GTM mutating family '{family_name}' has no saved before-state snapshot. Review the dry-run plan "
                "and pass --ack-no-snapshot only when the approved change should continue without an automatic restore point."
            )
        if risk_level in {"high", "irreversible"} and not ctx.get("plan_in"):
            raise SafetyError("Refused: high-risk writes require --plan-in (apply from a reviewed plan)")
        if risk_level in {"high", "irreversible"} and not bool(ctx.get("yes")):
            raise SafetyError("Refused: high-risk write actions require --yes")
        if risk_level == "irreversible" and not bool(ctx.get("ack_irreversible")):
            raise SafetyError("Refused: irreversible actions require --ack-irreversible")

        # If a plan is provided, enforce drift detection (env + request fingerprints).
        if ctx.get("plan_in"):
            plan_in_obj = read_json_file(str(ctx["plan_in"]))
            _ = validate_plan_for_apply(
                plan_in_obj,
                cfg=ctx["cfg"],
                expected_env_fingerprint=efp,
                expected_request_fingerprint=rfp,
            )
            if isinstance(plan_in_obj.get("before_state"), dict):
                before_state = dict(plan_in_obj["before_state"])
                before_state_path = str(plan_in_obj.get("before_state_path") or before_state.get("artifact_path") or "").strip() or None

        api = GtmApi(
            cfg=ctx["cfg"],
            verbose=bool(ctx.get("verbose")),
            user_agent=f"{ctx['tool']}/{ctx['tool_version']}",
            timeout_s=ctx.get("timeout_s"),
        )
        if before_state is None:
            before_state, before_state_path = _capture_before_state(
                api=api,
                method=method,
                request_path=expanded_path,
                read_retries=ctx["cfg"].read_retries,
                artifacts_dir=ctx.get("artifacts_dir") if isinstance(ctx.get("artifacts_dir"), Path) else None,
            )
            if before_state is None and missing_before_state:
                before_state = _no_snapshot_before_state(family_name=family_name)
        resp = api.request(http_method=method.http_method, path=expanded_path, query=query_params, body=body, retries=0)
        created_resource_path = None
        if method.method_id.endswith(".create") and isinstance(resp.body_json, dict):
            created_resource_path = _resource_path_from_response(resp.body_json.get("path"))
        recovery = _build_write_recovery(
            method=method,
            request_path=expanded_path,
            created_resource_path=created_resource_path,
        )

        verification: dict[str, Any] = {"attempted": False, "ok": None, "details": None}
        if isinstance(resp.body_json, dict) and isinstance(resp.body_json.get("path"), str):
            p = str(resp.body_json.get("path") or "").strip().lstrip("/")
            if p:
                try:
                    vresp = api.request(
                        http_method="GET",
                        path="tagmanager/v2/" + p,
                        query=None,
                        body=None,
                        retries=ctx["cfg"].read_retries,
                    )
                    verification = {
                        "attempted": True,
                        "ok": vresp.status < 400,
                        "details": {"status": vresp.status, "url": vresp.url, "body": vresp.body_json},
                    }
                except Exception as e:  # noqa: BLE001
                    verification = {"attempted": True, "ok": False, "details": {"error": f"{type(e).__name__}: {e}"}}

        receipt = {
            "tool": ctx["tool"],
            "version": ctx["tool_version"],
            "applied_at_utc": utc_now(),
            "env_fingerprint": efp,
            "request_fingerprint": rfp,
            "risk_level": risk_level,
            "request": {
                "method_id": method.method_id,
                "http_method": method.http_method,
                "path": expanded_path,
                "path_params": path_params,
                "query": query_params,
            },
            "response": {"status": resp.status, "url": resp.url, "body": resp.body_json},
            "before_state": before_state,
            "before_state_path": before_state_path,
            "recovery": recovery,
            "verification": verification,
        }
        if isinstance(before_state, dict) and not bool(before_state.get("supported", True)):
            receipt["no_snapshot_approval"] = {
                "approved": bool(ctx.get("ack_no_snapshot")),
                "reason": "No saved before-state snapshot was available for this GTM write.",
            }

        receipt_out = ctx.get("receipt_out")
        receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None

        out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
        ctx["audit"].write("method.apply", {"method_id": method.method_id, "receipt_out": receipt_path})
        ctx["out"].emit(out)
        return 0

    # Read-only method: execute directly.
    api = GtmApi(
        cfg=ctx["cfg"],
        verbose=bool(ctx.get("verbose")),
        user_agent=f"{ctx['tool']}/{ctx['tool_version']}",
        timeout_s=ctx.get("timeout_s"),
    )
    resp = api.request(
        http_method=method.http_method,
        path=expanded_path,
        query=query_params,
        body=body,
        retries=ctx["cfg"].read_retries,
    )
    out = {
        "ok": resp.status < 400,
        "dry_run": False,
        "risk_level": risk_level,
        "method_id": method.method_id,
        "status": resp.status,
        "url": resp.url,
        "body": resp.body_json,
    }
    ctx["audit"].write("method.read", {"method_id": method.method_id, "status": resp.status})
    ctx["out"].emit(out)
    return 0 if out["ok"] else 1


def register_discovery_commands(
    *,
    root_subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    parser_class: type[argparse.ArgumentParser],
) -> dict[str, tuple[str, ...]]:
    """
    Register one explicit CLI command per discovery method id.

    Returns:
      method_id -> command tokens (kebab-case), excluding the leading program name.
    """
    groups: dict[tuple[str, ...], tuple[argparse.ArgumentParser, argparse._SubParsersAction]] = {}  # type: ignore[name-defined]
    groups[()] = (None, root_subparsers)  # type: ignore[assignment]

    registry: dict[str, tuple[str, ...]] = {}
    used_commands: dict[tuple[str, ...], str] = {}

    for row in _INVENTORY:
        tokens = tuple(row.command_tokens)
        if not tokens:
            continue
        if tokens in used_commands and used_commands[tokens] != row.method_id:
            raise RuntimeError(f"Command collision: {' '.join(tokens)} for {row.method_id} and {used_commands[tokens]}")
        used_commands[tokens] = row.method_id

        # Create intermediate groups.
        prefix: tuple[str, ...] = ()
        parent_sub = root_subparsers
        for depth, tok in enumerate(tokens[:-1], start=1):
            prefix = prefix + (tok,)
            if prefix in groups:
                parent_sub = groups[prefix][1]
                continue
            gp = parent_sub.add_parser(tok, help=f"Group: {' '.join(prefix)}")
            sub = gp.add_subparsers(
                dest=f"subcmd_{depth}_{'_'.join(prefix)}",
                required=True,
                parser_class=parser_class,
            )
            groups[prefix] = (gp, sub)
            parent_sub = sub

        leaf_tok = tokens[-1]
        leaf = parent_sub.add_parser(leaf_tok, help=f"{row.http_method} {row.path} ({row.method_id})")

        method = _METHODS_BY_ID.get(row.method_id)
        if not method:
            raise RuntimeError(f"Missing method spec for id: {row.method_id}")

        # Per-method parameters from discovery.
        for p in method.parameters:
            flag = "--" + to_kebab(p.name)
            kwargs: dict[str, Any] = {"required": bool(p.required), "help": f"{p.location} param"}
            leaf.add_argument(flag, dest=p.name, **kwargs)

        # System query params (optional, supported for all methods).
        leaf.add_argument("--fields", default=None, help="Partial response fields mask (system parameter)")
        leaf.add_argument("--quota-user", default=None, help="Quota user string (system parameter)")
        leaf.add_argument(
            "--pretty-print",
            default=None,
            help="Pretty-print response (true/false) (system parameter)",
        )

        needs_body = bool(method.request_ref) and method.http_method in {"POST", "PUT", "PATCH"}
        body_group = leaf.add_mutually_exclusive_group(required=needs_body)
        body_group.add_argument("--body-json", default=None, help="Request body JSON string")
        body_group.add_argument("--body-file", default=None, help="Request body JSON file path")

        leaf.set_defaults(
            func=cmd_discovery_method,
            write_capable=_is_write(method),
            method_id=row.method_id,
        )
        registry[row.method_id] = tokens

    global _REGISTERED
    _REGISTERED = dict(registry)
    return registry


def registered_method_ids() -> list[str]:
    if _REGISTERED is None:
        return []
    return sorted(_REGISTERED.keys())

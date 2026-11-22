from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from shlex import join
from typing import Any

import requests

from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..oauth_tokens import resolve_access_token


_TOOL_NAME = "qwayk-hubspot-safe-agent-cli"
_USER_AGENT = f"{_TOOL_NAME}/safe-apis"
_PATH_RE = re.compile(r"\{([A-Za-z0-9_]+)\}")
_REVIEW_FIELDS = ("tool", "family", "action", "method", "path", "query", "payload", "upload_details")


@dataclass(frozen=True)
class ActionSpec:
    method: str
    path: str
    write: bool
    query_args: tuple[tuple[str, dict[str, Any]], ...] = ()
    query_map: dict[str, str] | None = None
    fixed_query: dict[str, Any] | None = None
    requires_body_file: bool = False
    requires_request_file: bool = False
    requires_files: bool = False
    min_files: int = 0
    require_apply: bool = True
    require_yes: bool = False
    require_ack: bool = False
    require_plan_in: bool = False


_ACTIONS: dict[str, dict[str, ActionSpec]] = {
    "object-library": {
        "list-enablement": ActionSpec(method="GET", path="/crm/object-library/2026-03/enablement", write=False),
        "get-enablement": ActionSpec(
            method="GET",
            path="/crm/object-library/2026-03/{object_type}/enablement",
            write=False,
        ),
    },
    "objects": {
        "list": ActionSpec(
            method="GET",
            path="/crm/objects/2026-03/{object_type}",
            write=False,
            query_args=(
                ("limit", {"type": int, "help": "Limit records"}),
                ("after", {"help": "Paging cursor"}),
                ("archived", {"action": "store_true", "help": "Include archived records"}),
                ("properties", {"help": "Comma-separated property list"}),
                ("associations", {"help": "Comma-separated association labels"}),
            ),
        ),
        "get": ActionSpec(
            method="GET",
            path="/crm/objects/2026-03/{object_type}/{object_id}",
            write=False,
            query_args=(
                ("id_property", {"help": "Use unique id property"}),
                ("archived", {"action": "store_true", "help": "Include archived record"}),
                ("properties", {"help": "Comma-separated property list"}),
                ("properties_with_history", {"help": "Comma-separated properties with history"}),
                ("associations", {"help": "Comma-separated association types"}),
            ),
            query_map={
                "properties_with_history": "propertiesWithHistory",
                "id_property": "idProperty",
            },
        ),
        "batch-read": ActionSpec(
            method="POST",
            path="/crm/objects/2026-03/{object_type}/batch/read",
            write=False,
            requires_body_file=True,
        ),
        "create": ActionSpec(
            method="POST",
            path="/crm/objects/2026-03/{object_type}",
            write=True,
            requires_body_file=True,
            require_apply=True,
        ),
        "batch-create": ActionSpec(
            method="POST",
            path="/crm/objects/2026-03/{object_type}/batch/create",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
        ),
        "update": ActionSpec(
            method="PATCH",
            path="/crm/objects/2026-03/{object_type}/{object_id}",
            write=True,
            requires_body_file=True,
            require_apply=True,
        ),
        "batch-update": ActionSpec(
            method="POST",
            path="/crm/objects/2026-03/{object_type}/batch/update",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
        ),
        "batch-upsert": ActionSpec(
            method="POST",
            path="/crm/objects/2026-03/{object_type}/batch/upsert",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
        ),
        "merge": ActionSpec(
            method="POST",
            path="/crm/objects/2026-03/{object_type}/merge",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
        ),
        "archive": ActionSpec(
            method="DELETE",
            path="/crm/objects/2026-03/{object_type}/{object_id}",
            write=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
        ),
        "batch-archive": ActionSpec(
            method="POST",
            path="/crm/objects/2026-03/{object_type}/batch/archive",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
        ),
        "gdpr-delete": ActionSpec(
            method="POST",
            path="/crm/objects/2025-09/{object_type}/gdpr-delete",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
            require_plan_in=True,
        ),
        "search": ActionSpec(
            method="POST",
            path="/crm/objects/2026-03/{object_type}/search",
            write=False,
            requires_body_file=True,
        ),
    },
    "associations": {
        "create-default": ActionSpec(
            method="PUT",
            path="/crm/objects/2026-03/{from_object_type}/{from_object_id}/associations/default/{to_object_type}/{to_object_id}",
            write=True,
            require_apply=True,
        ),
        "create-labeled": ActionSpec(
            method="PUT",
            path="/crm/objects/2026-03/{object_type}/{object_id}/associations/{to_object_type}/{to_object_id}",
            write=True,
            requires_body_file=True,
            require_apply=True,
        ),
        "list-record": ActionSpec(
            method="GET",
            path="/crm/objects/2026-03/{from_object_type}/{object_id}/associations/{to_object_type}",
            write=False,
        ),
        "remove-record": ActionSpec(
            method="DELETE",
            path="/crm/objects/2026-03/{object_type}/{object_id}/associations/{to_object_type}/{to_object_id}",
            write=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
        ),
        "batch-read": ActionSpec(
            method="POST",
            path="/crm/associations/2026-03/{from_object_type}/{to_object_type}/batch/read",
            write=False,
            requires_body_file=True,
        ),
        "batch-create-default": ActionSpec(
            method="POST",
            path="/crm/associations/2026-03/{from_object_type}/{to_object_type}/batch/associate/default",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
        ),
        "batch-create-labeled": ActionSpec(
            method="POST",
            path="/crm/associations/2026-03/{from_object_type}/{to_object_type}/batch/create",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
        ),
        "batch-archive": ActionSpec(
            method="POST",
            path="/crm/associations/2026-03/{from_object_type}/{to_object_type}/batch/archive",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
        ),
        "batch-archive-labels": ActionSpec(
            method="POST",
            path="/crm/associations/2026-03/{from_object_type}/{to_object_type}/batch/labels/archive",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
        ),
    },
    "association-labels": {
        "list": ActionSpec(
            method="GET",
            path="/crm/associations/2026-03/{from_object_type}/{to_object_type}/labels",
            write=False,
        ),
        "create": ActionSpec(
            method="POST",
            path="/crm/associations/2026-03/{from_object_type}/{to_object_type}/labels",
            write=True,
            requires_body_file=True,
            require_apply=True,
        ),
        "update": ActionSpec(
            method="PATCH",
            path="/crm/associations/2026-03/{from_object_type}/{to_object_type}/labels/{association_type_id}",
            write=True,
            requires_body_file=True,
            require_apply=True,
        ),
        "delete": ActionSpec(
            method="DELETE",
            path="/crm/associations/2026-03/{from_object_type}/{to_object_type}/labels/{association_type_id}",
            write=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
        ),
    },
    "association-limits": {
        "list-all": ActionSpec(
            method="GET",
            path="/crm/associations/2026-03/definitions/configurations/all",
            write=False,
        ),
        "get": ActionSpec(
            method="GET",
            path="/crm/associations/2026-03/definitions/configurations/{from_object_type}/{to_object_type}",
            write=False,
        ),
        "batch-create": ActionSpec(
            method="POST",
            path="/crm/associations/2026-03/definitions/configurations/{from_object_type}/{to_object_type}/batch/create",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
        ),
        "batch-update": ActionSpec(
            method="POST",
            path="/crm/associations/2026-03/definitions/configurations/{from_object_type}/{to_object_type}/batch/update",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
        ),
        "batch-purge": ActionSpec(
            method="POST",
            path="/crm/associations/2026-03/definitions/configurations/{from_object_type}/{to_object_type}/batch/purge",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
        ),
    },
    "properties": {
        "list": ActionSpec(
            method="GET",
            path="/crm/properties/2026-03/{object_type}",
            write=False,
            query_args=(("archived", {"action": "store_true", "help": "Include archived properties"}),),
        ),
        "get": ActionSpec(
            method="GET",
            path="/crm/properties/2026-03/{object_type}/{property_name}",
            write=False,
            query_args=(("archived", {"action": "store_true", "help": "Include archived property"}),),
        ),
        "batch-read": ActionSpec(
            method="POST",
            path="/crm/properties/2026-03/{object_type}/batch/read",
            write=False,
            requires_body_file=True,
        ),
        "create": ActionSpec(
            method="POST",
            path="/crm/properties/2026-03/{object_type}",
            write=True,
            requires_body_file=True,
            require_apply=True,
        ),
        "batch-create": ActionSpec(
            method="POST",
            path="/crm/properties/2026-03/{object_type}/batch/create",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
        ),
        "update": ActionSpec(
            method="PATCH",
            path="/crm/properties/2026-03/{object_type}/{property_name}",
            write=True,
            requires_body_file=True,
            require_apply=True,
        ),
        "archive": ActionSpec(
            method="DELETE",
            path="/crm/properties/2026-03/{object_type}/{property_name}",
            write=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
        ),
        "batch-archive": ActionSpec(
            method="POST",
            path="/crm/properties/2026-03/{object_type}/batch/archive",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
        ),
    },
    "property-groups": {
        "list": ActionSpec(
            method="GET",
            path="/crm/properties/2026-03/{object_type}/groups",
            write=False,
        ),
        "get": ActionSpec(
            method="GET",
            path="/crm/properties/2026-03/{object_type}/groups/{group_name}",
            write=False,
            query_args=(("locale", {"help": "Locale override"}),),
        ),
        "create": ActionSpec(
            method="POST",
            path="/crm/properties/2026-03/{object_type}/groups",
            write=True,
            requires_body_file=True,
            require_apply=True,
        ),
        "update": ActionSpec(
            method="PATCH",
            path="/crm/properties/2026-03/{object_type}/groups/{group_name}",
            write=True,
            requires_body_file=True,
            require_apply=True,
        ),
        "archive": ActionSpec(
            method="DELETE",
            path="/crm/properties/2026-03/{object_type}/groups/{group_name}",
            write=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
        ),
    },
    "owners": {
        "list": ActionSpec(method="GET", path="/crm/owners/2026-03", write=False),
        "get": ActionSpec(
            method="GET",
            path="/crm/owners/2026-03/{owner_id}",
            write=False,
            query_args=(("email", {"help": "Filter by owner email"}),),
        ),
    },
    "pipelines": {
        "list": ActionSpec(
            method="GET",
            path="/crm/pipelines/2026-03/{object_type}",
            write=False,
            query_args=(("archived", {"action": "store_true", "help": "Include archived pipelines"}),),
        ),
        "get": ActionSpec(
            method="GET",
            path="/crm/pipelines/2026-03/{object_type}/{pipeline_id}",
            write=False,
            query_args=(("archived", {"action": "store_true", "help": "Include archived pipeline"}),),
        ),
        "create": ActionSpec(
            method="POST",
            path="/crm/pipelines/2026-03/{object_type}",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
        ),
        "replace": ActionSpec(
            method="PUT",
            path="/crm/pipelines/2026-03/{object_type}/{pipeline_id}",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
        ),
        "update": ActionSpec(
            method="PATCH",
            path="/crm/pipelines/2026-03/{object_type}/{pipeline_id}",
            write=True,
            requires_body_file=True,
            require_apply=True,
        ),
        "archive": ActionSpec(
            method="DELETE",
            path="/crm/pipelines/2026-03/{object_type}/{pipeline_id}",
            write=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
            query_args=(
                ("validate_references_before_delete", {"action": "store_true", "help": "Validate references before delete"}),
                ("validate_deal_stage_usages_before_delete", {"action": "store_true", "help": "Validate deal-stage usages before delete"}),
            ),
            query_map={
                "validate_references_before_delete": "validateReferencesBeforeDelete",
                "validate_deal_stage_usages_before_delete": "validateDealStageUsagesBeforeDelete",
            },
        ),
    },
    "pipeline-stages": {
        "list": ActionSpec(
            method="GET",
            path="/crm/pipelines/2026-03/{object_type}/{pipeline_id}/stages",
            write=False,
        ),
        "get": ActionSpec(
            method="GET",
            path="/crm/pipelines/2026-03/{object_type}/{pipeline_id}/stages/{stage_id}",
            write=False,
        ),
        "create": ActionSpec(
            method="POST",
            path="/crm/pipelines/2026-03/{object_type}/{pipeline_id}/stages",
            write=True,
            requires_body_file=True,
            require_apply=True,
        ),
        "replace": ActionSpec(
            method="PUT",
            path="/crm/pipelines/2026-03/{object_type}/{pipeline_id}/stages/{stage_id}",
            write=True,
            requires_body_file=True,
            require_apply=True,
        ),
        "update": ActionSpec(
            method="PATCH",
            path="/crm/pipelines/2026-03/{object_type}/{pipeline_id}/stages/{stage_id}",
            write=True,
            requires_body_file=True,
            require_apply=True,
        ),
        "archive": ActionSpec(
            method="DELETE",
            path="/crm/pipelines/2026-03/{object_type}/{pipeline_id}/stages/{stage_id}",
            write=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
        ),
    },
    "schemas": {
        "list": ActionSpec(
            method="GET",
            path="/crm-object-schemas/2026-03/schemas",
            write=False,
            query_args=(
                ("include_properties", {"action": "store_true", "help": "Include schema properties"}),
                ("include_associations", {"action": "store_true", "help": "Include associations"}),
                ("include_audit", {"action": "store_true", "help": "Include audit metadata"}),
            ),
            query_map={
                "include_properties": "includeProperties",
                "include_associations": "includeAssociations",
                "include_audit": "includeAudit",
            },
        ),
        "get": ActionSpec(
            method="GET",
            path="/crm-object-schemas/2026-03/schemas/{object_type}",
            write=False,
            query_args=(
                ("include_properties", {"action": "store_true", "help": "Include schema properties"}),
                ("include_associations", {"action": "store_true", "help": "Include associations"}),
                ("include_audit", {"action": "store_true", "help": "Include audit metadata"}),
                ("archived", {"action": "store_true", "help": "Include archived schemas"}),
            ),
            query_map={
                "include_properties": "includeProperties",
                "include_associations": "includeAssociations",
                "include_audit": "includeAudit",
            },
        ),
        "create": ActionSpec(
            method="POST",
            path="/crm-object-schemas/2026-03/schemas",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
        ),
        "update": ActionSpec(
            method="PATCH",
            path="/crm-object-schemas/2026-03/schemas/{object_type}",
            write=True,
            requires_body_file=True,
            require_apply=True,
        ),
        "archive": ActionSpec(
            method="DELETE",
            path="/crm-object-schemas/2026-03/schemas/{object_type}",
            write=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
        ),
        "hard-delete": ActionSpec(
            method="DELETE",
            path="/crm-object-schemas/2026-03/schemas/{object_type}",
            write=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
            require_plan_in=True,
            fixed_query={"archived": "true"},
        ),
    },
    "imports": {
        "list": ActionSpec(
            method="GET",
            path="/crm/imports/2026-03",
            write=False,
            query_args=(("limit", {"type": int, "help": "Limit records"}),),
        ),
        "get": ActionSpec(
            method="GET",
            path="/crm/imports/2026-03/{import_id}",
            write=False,
        ),
        "create": ActionSpec(
            method="POST",
            path="/crm/imports/2026-03",
            write=True,
            requires_request_file=True,
            requires_files=True,
            min_files=1,
            require_apply=True,
            require_yes=True,
        ),
        "errors": ActionSpec(
            method="GET",
            path="/crm/imports/2026-03/{import_id}/errors",
            write=False,
            query_args=(("limit", {"type": int, "help": "Limit errors"}),),
        ),
        "cancel": ActionSpec(
            method="POST",
            path="/crm/imports/2026-03/{import_id}/cancel",
            write=True,
            require_apply=True,
            require_yes=True,
            require_ack=True,
        ),
    },
    "exports": {
        "create": ActionSpec(
            method="POST",
            path="/crm/exports/2026-03/export/async",
            write=True,
            requires_body_file=True,
            require_apply=True,
            require_yes=True,
        ),
        "status": ActionSpec(
            method="GET",
            path="/crm/exports/2026-03/export/async/tasks/{task_id}/status",
            write=False,
        ),
    },
}


def actions() -> dict[str, dict[str, ActionSpec]]:
    return _ACTIONS


def _to_snake(name: str) -> str:
    return name.replace("-", "_")


def _to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(part.title() for part in parts[1:])


def _safe_now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _path_names(path: str) -> list[str]:
    return _PATH_RE.findall(path)


def _collect_query(spec: ActionSpec, args: Any) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if spec.fixed_query:
        out.update(spec.fixed_query)

    query_map = spec.query_map or {}
    for arg_name, _ in spec.query_args:
        attr = _to_snake(arg_name)
        value = getattr(args, attr, None)
        if value is None or value == []:
            continue
        if isinstance(value, bool):
            if not value:
                continue
        elif isinstance(value, str) and not value.strip():
            continue
        out[query_map.get(arg_name, _to_camel(arg_name))] = value

    return out


def _collect_path_values(spec: ActionSpec, args: Any) -> dict[str, str]:
    values: dict[str, str] = {}
    for name in _path_names(spec.path):
        attr = _to_snake(name)
        raw = str(getattr(args, attr, "")).strip()
        if not raw:
            raise ValidationError(f"Missing --{name.replace('_', '-')}")
        values[name] = raw
    return values


def _read_body(payload_path: str | None) -> Any:
    if not payload_path:
        raise ValidationError("Missing JSON body file flag")
    body = read_json_file(payload_path)
    if not isinstance(body, (dict, list)):
        raise ValidationError("JSON body must be object or array")
    return body


def _build_headers(token: str | None) -> dict[str, str]:
    if not token:
        raise ValidationError("Missing token. Set HUBSPOT_ACCESS_TOKEN or run auth token set --file token.json")
    return {
        "User-Agent": _USER_AGENT,
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }


def _needs_saved_plan(spec: ActionSpec, action: str) -> bool:
    return spec.require_plan_in or spec.requires_files or action.startswith("batch-")


def _reviewed_request(plan: dict[str, Any]) -> bytes:
    fields = {key: plan.get(key) for key in _REVIEW_FIELDS}
    fields["base_url"] = plan["baseline"].get("env_fingerprint")
    return json.dumps(fields, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _build_plan(
    *,
    family: str,
    action: str,
    spec: ActionSpec,
    cfg: Any,
    path: str,
    command_str: str,
    payload: Any,
    query: dict[str, Any],
    upload_files: list[str],
    upload_details: list[dict[str, str]],
    token: str | None,
) -> dict[str, Any]:
    risk_reasons: list[str] = []
    if spec.require_yes:
        risk_reasons.append("require_yes")
    if spec.require_ack:
        risk_reasons.append("require_ack")
    if _needs_saved_plan(spec, action):
        risk_reasons.append("require_plan_in")
    if spec.requires_files:
        risk_reasons.append("requires_files")

    plan = {
        "tool": _TOOL_NAME,
        "version": "0.1.0",
        "generated_at_utc": _safe_now_utc(),
        "env_fingerprint": cfg.base_url,
        "command": command_str,
        "family": family,
        "action": action,
        "method": spec.method,
        "path": path,
        "risk_level": "high" if risk_reasons else "low",
        "risk_reasons": risk_reasons,
        "query": query,
        "payload": payload,
        "upload_files": upload_files,
        "upload_details": upload_details,
        "baseline": {"env_fingerprint": cfg.base_url},
        "before_state": {
            "required": True,
            "supported": False,
            "status": "no_snapshot_available",
            "approval_required": "--ack-no-snapshot",
            "statement": (
                "No useful before-state snapshot is captured for this HubSpot write. "
                "The write may still run after the reviewed plan and explicit no-snapshot approval."
            ),
        },
        "proposed_changes": [{"family": family, "action": action}],
        "rollback_plan": {
            "possible": False,
            "statement": (
                "No automatic rollback is available because this CLI does not yet create "
                "restorable snapshots or provider backups for HubSpot writes."
            ),
        },
    }
    if token:
        plan["connection_proof"] = hmac.digest(token.encode(), _reviewed_request(plan), "sha256").hex()
    return plan


def _assert_write_gates(spec: ActionSpec, action: str, ctx: dict[str, Any]) -> None:
    if spec.require_yes and not bool(ctx.get("yes")):
        raise SafetyError(f"Refused: {spec.method} {spec.path} requires --yes")
    if spec.require_ack and not bool(ctx.get("ack_irreversible")):
        raise SafetyError(f"Refused: {spec.method} {spec.path} requires --ack-irreversible")
    if _needs_saved_plan(spec, action) and not ctx.get("plan_in"):
        raise SafetyError("Refused: this command requires --plan-in. Save and review a preview first.")
    if not ctx.get("ack_no_snapshot"):
        raise SafetyError(
            "Refused: this HubSpot write has no saved before-state snapshot. "
            "Review the plan, confirm the recovery limit, then re-run with --ack-no-snapshot."
        )


def _check_saved_plan(plan_path: str, current: dict[str, Any]) -> None:
    saved = read_json_file(plan_path)
    if not isinstance(saved, dict):
        raise ValidationError("Plan file must be a JSON object")
    saved_proof = saved.get("connection_proof")
    current_proof = current.get("connection_proof")
    if not isinstance(saved.get("baseline"), dict) or not saved_proof or not current_proof:
        raise SafetyError("Refused: save a fresh preview with the HubSpot connection you will use.")
    if _reviewed_request(saved) != _reviewed_request(current):
        raise SafetyError("Refused: the request changed. Save and review a fresh preview.")
    if not isinstance(saved_proof, str) or not hmac.compare_digest(saved_proof.encode(), current_proof.encode()):
        raise SafetyError("Refused: the HubSpot connection changed. Save and review a fresh preview.")


def _validate_request_payload(spec: ActionSpec, args: Any) -> Any:
    if spec.requires_body_file:
        return _read_body(getattr(args, "body_file"))
    if spec.requires_request_file:
        return _read_body(getattr(args, "request_file"))
    return None


def _validate_file_uploads(spec: ActionSpec, args: Any) -> list[str]:
    if not spec.requires_files:
        return []

    files = list(getattr(args, "file", []) or [])
    if len(files) < spec.min_files:
        raise ValidationError("Missing --file for import create")

    paths: list[str] = []
    for item in files:
        path = Path(item)
        if not path.is_file():
            raise ValidationError(f"Upload file missing: {item}")
        paths.append(str(path))
    return paths


def _upload_details(paths: list[str], uploads: list[tuple[str, bytes]]) -> list[dict[str, str]]:
    if uploads:
        return [{"name": name, "sha256": hashlib.sha256(contents).hexdigest()} for name, contents in uploads]
    details = []
    for item in paths:
        path = Path(item)
        with path.open("rb") as source:
            sha256 = hashlib.file_digest(source, "sha256").hexdigest()
        details.append({"name": path.name, "sha256": sha256})
    return details


def _http_request(
    *,
    spec: ActionSpec,
    url: str,
    token: str | None,
    ctx: dict[str, Any],
    query: dict[str, Any],
    payload: Any,
    uploads: list[tuple[str, bytes]],
) -> tuple[int, Any]:
    headers = _build_headers(token)

    if spec.requires_request_file and spec.requires_files:
        resp = requests.post(
            url=url,
            headers=headers,
            params=query or None,
            data={"importRequest": json.dumps(payload)},
            files=[("files", (name, contents, "application/octet-stream")) for name, contents in uploads],
            timeout=ctx["timeout_s"],
        )

        if resp.status_code >= 400:
            raise RuntimeError(f"HTTP {resp.status_code} for HubSpot API request")
        try:
            return resp.status_code, resp.json()
        except ValueError:
            return resp.status_code, {"status": resp.status_code, "text": resp.text}

    transport = HttpClient(timeout_s=ctx["timeout_s"], verbose=bool(ctx.get("verbose")), user_agent=_USER_AGENT)
    response = transport.request(
        spec.method,
        url,
        headers=headers,
        params=query or None,
        json_body=(payload if isinstance(payload, (dict, list)) else None),
    )

    if response.status in (204, 205) or not response.body:
        return response.status, {}
    try:
        return response.status, response.json()
    except ValueError:
        return response.status, {"status": response.status, "text": response.text()}


def _import_result(response: dict[str, Any], env_file: str) -> dict[str, Any]:
    state = response.get("state")
    import_id = response.get("importId")
    if state in ("FAILED", "CANCELED"):
        result = "failed"
    elif state == "DONE":
        result = "completed"
    elif import_id and state in (None, "STARTED", "PROCESSING", "DEFERRED"):
        result = "submitted"
    else:
        result = "unconfirmed"
    details: dict[str, Any] = {"status": result, "ok": result == "completed", "state": state}
    if import_id:
        check = [_TOOL_NAME, "--env-file", env_file, "hubspot", "imports"]
        details.update(
            import_id=import_id,
            check_status=join([*check, "get", "--import-id", str(import_id)]),
            check_errors=join([*check, "errors", "--import-id", str(import_id)]),
        )
    return details


def _write_result(
    family: str, action: str, http_status: int, response: Any, env_file: str
) -> dict[str, Any]:
    payload = response if isinstance(response, dict) else {}
    if (family, action) == ("imports", "create"):
        return {"type": "provider_response", **_import_result(payload, env_file)}
    if action.startswith("batch-"):
        status = payload.get("status")
        count = payload.get("numErrors")
        if status in ("FAILED", "CANCELED", "CANCELLED"):
            result = "failed"
        elif http_status == 207 or payload.get("errors") or (isinstance(count, int) and count > 0):
            result = "partial" if payload.get("results") else "failed"
        elif status in ("PENDING", "PROCESSING") or http_status == 202:
            result = "submitted"
        elif status == "COMPLETE" or http_status in (204, 205):
            result = "completed"
        else:
            result = "unconfirmed"
        return {"type": "provider_response", "status": result, "ok": result == "completed"}
    return {"type": "provider_response", "ok": True}


def _register_action_parser(
    parser: argparse.ArgumentParser,
    family: str,
    action: str,
    spec: ActionSpec,
) -> None:
    path_names = _path_names(spec.path)
    for name in dict.fromkeys(path_names):
        parser.add_argument(f"--{name.replace('_', '-')}", required=True, help=f"Path arg {name}")

    for arg_name, opts in spec.query_args:
        parser.add_argument(f"--{arg_name.replace('_', '-')}", **opts)

    if spec.requires_body_file:
        parser.add_argument("--body-file", required=True, help="JSON body file")
    if spec.requires_request_file:
        parser.add_argument("--request-file", required=True, help="JSON request file for multipart import")
    if spec.requires_files:
        parser.add_argument("--file", action="append", default=[], help="Import file path (repeatable)")

    parser.set_defaults(
        func=cmd_hubspot_api,
        hubspot_family=family,
        hubspot_action=action,
        hubspot_spec=spec,
        write_capable=spec.write,
    )


def register_commands(parent: argparse._SubParsersAction[Any]) -> None:
    hubspot = parent.add_parser("hubspot", help="HubSpot CRM API actions")
    families = hubspot.add_subparsers(dest="hubspot_family", required=True)

    for family_name in sorted(_ACTIONS):
        family_parser = families.add_parser(family_name, help=f"{family_name} commands")
        actions = family_parser.add_subparsers(dest="hubspot_action", required=True)

        for action_name in sorted(_ACTIONS[family_name]):
            spec = _ACTIONS[family_name][action_name]
            p = actions.add_parser(action_name, help=f"{action_name} {spec.method} {spec.path}")
            _register_action_parser(p, family_name, action_name, spec)


def cmd_hubspot_api(args: Any, ctx: dict[str, Any]) -> int:
    spec = getattr(args, "hubspot_spec", None)
    if spec is None:
        raise ValidationError("Missing HubSpot action spec")
    if not isinstance(spec, ActionSpec):
        raise ValidationError("Invalid HubSpot action spec")

    cfg = ctx["cfg"]
    family = str(getattr(args, "hubspot_family", "")).strip()
    action = str(getattr(args, "hubspot_action", "")).strip()

    query = _collect_query(spec, args)
    path = spec.path.format(**_collect_path_values(spec, args))
    payload = _validate_request_payload(spec, args)
    upload_paths = _validate_file_uploads(spec, args)

    applying = bool(ctx.get("apply"))
    env_file = str(ctx["env_file"])
    uploads = []
    if spec.write and applying:
        _assert_write_gates(spec, action, ctx)
        uploads = [(Path(item).name, Path(item).read_bytes()) for item in upload_paths]

    token = resolve_access_token(cfg.token, env_file)
    if spec.write:
        plan = _build_plan(
            family=family,
            action=action,
            spec=spec,
            cfg=cfg,
            path=path,
            command_str=ctx["command_str"],
            payload=payload,
            query=query,
            upload_files=upload_paths,
            upload_details=_upload_details(upload_paths, uploads),
            token=token,
        )

    if spec.write and not applying:
        plan_out = ctx.get("plan_out")
        plan_path = write_json_file(plan_out, plan) if isinstance(plan_out, str) else None
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "plan": plan,
                "plan_out": plan_path,
                "method": spec.method,
                "path": spec.path,
                "query": query,
                "upload_files": upload_paths,
            }
        )
        return 0

    if spec.write and ctx.get("plan_in"):
        _check_saved_plan(ctx["plan_in"], plan)

    http_status, response = _http_request(
        spec=spec,
        url=cfg.base_url.rstrip("/") + path,
        token=token,
        ctx=ctx,
        query=query,
        payload=payload,
        uploads=uploads,
    )

    if spec.write:
        verification = _write_result(family, action, http_status, response, env_file)
        ok = verification.get("status") not in ("partial", "failed", "unconfirmed")
        receipt = {
            "tool": _TOOL_NAME,
            "version": "0.1.0",
            "applied_at_utc": _safe_now_utc(),
            "family": family,
            "action": action,
            "method": spec.method,
            "path": path,
            "before_state": plan.get("before_state"),
            "no_snapshot_approval": {"approved": True, "flag": "--ack-no-snapshot"},
            "rollback_plan": plan.get("rollback_plan"),
            "response": response,
            "verification": verification,
        }
        receipt_out = ctx.get("receipt_out")
        receipt_path = write_json_file(receipt_out, receipt) if isinstance(receipt_out, str) else None
        ctx["out"].emit(
            {
                "ok": ok,
                "dry_run": False,
                "receipt": receipt,
                "receipt_out": receipt_path,
                "method": spec.method,
                "path": spec.path,
                "query": query,
            }
        )
        return 0 if ok else 1

    if not spec.write:
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": False,
                "response": response,
                "method": spec.method,
                "path": spec.path,
                "query": query,
            }
        )
        return 0

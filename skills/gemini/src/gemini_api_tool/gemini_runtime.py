from __future__ import annotations

import dataclasses
import hashlib
import hmac
import json
import mimetypes
import re
import uuid
from pathlib import Path
from typing import Any

import requests

from .json_files import read_json_file, write_json_file
from .operation_registry import OPERATION_BY_COMMAND, OperationSpec

BASE_URL = "https://generativelanguage.googleapis.com"
SECRET_REPLACEMENT = "[REDACTED]"
TOKEN_COUNT_METHODS = {"count-tokens", "count-text-tokens", "count-message-tokens"}
ASYNC_BATCH_METHODS = {"async-batch-embed-content", "batch-generate-content"}
BILLABLE_CHANGES = {
    ("cached-contents", "create"),
    ("cached-contents", "patch"),
    ("file-search-stores", "import-file"),
    ("media", "upload-to-file-search-store"),
    ("tuned-models", "create"),
}


def may_charge(op: OperationSpec) -> bool:
    if op.safety_class == "compute_read":
        return op.method_name not in TOKEN_COUNT_METHODS
    return op.command_key in BILLABLE_CHANGES


def requires_plan(op: OperationSpec) -> bool:
    return op.safety_class == "state_changing" or op.method_name in ASYNC_BATCH_METHODS


@dataclasses.dataclass(frozen=True)
class GeminiRequest:
    method: str
    url: str
    headers: dict[str, str]
    params: dict[str, Any]
    body: Any
    media_file: str | None = None
    media_type: str | None = None
    media_bytes: bytes | None = dataclasses.field(default=None, repr=False)

    def media_digest(self) -> str | None:
        if self.media_bytes is None:
            return None
        return hashlib.sha256(self.media_bytes).hexdigest()

    def redacted(self) -> dict[str, Any]:
        headers = dict(self.headers)
        if "x-goog-api-key" in headers:
            headers["x-goog-api-key"] = SECRET_REPLACEMENT
        return {
            "method": self.method,
            "url": self.url,
            "headers": headers,
            "params": self.params,
            "body": None,
            "media_file": self.media_file,
            "media_type": self.media_type,
        }


class GeminiClient:
    def __init__(self, *, api_key: str, timeout_s: float, base_url: str = BASE_URL, verbose: bool = False):
        self.api_key = api_key
        self.timeout_s = timeout_s
        self.base_url = base_url.rstrip("/")
        self.verbose = verbose

    def build_request(
        self,
        op: OperationSpec,
        *,
        path_values: dict[str, str],
        query_values: dict[str, Any],
        body: Any,
        api_version: str | None = None,
        media_file: str | None = None,
    ) -> GeminiRequest:
        version = _choose_version(op, api_version)
        path = op.version_paths.get(version, op.path)
        for key in op.path_params:
            value = path_values.get(key)
            if not value:
                raise ValueError(f"Missing --{_flag_name(key)}")
            path = path.replace("{+" + key + "}", value).replace("{" + key + "}", value)
        media_type = None
        params = {k: v for k, v in query_values.items() if v not in (None, "")}
        if media_file:
            if not op.supports_media_upload:
                raise ValueError(f"{op.operation_id} does not support media upload")
            media_type = mimetypes.guess_type(media_file)[0] or "application/octet-stream"
            path = f"upload/{path.lstrip('/')}"
            params["uploadType"] = "multipart" if body is not None else "media"
        return GeminiRequest(
            method=op.http_method,
            url=f"{self.base_url}/{path.lstrip('/')}",
            headers={"x-goog-api-key": self.api_key, "Content-Type": "application/json"},
            params=params,
            body=body,
            media_file=media_file,
            media_type=media_type,
        )

    def send(self, request: GeminiRequest) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "method": request.method,
            "url": request.url,
            "headers": request.headers,
            "params": request.params,
            "timeout": self.timeout_s,
        }
        if request.media_file:
            media_bytes = request.media_bytes
            if media_bytes is None:
                media_bytes = Path(request.media_file).read_bytes()
            if request.params.get("uploadType") == "multipart":
                body, content_type = _multipart_related_body(
                    metadata=request.body or {},
                    media_bytes=media_bytes,
                    media_type=request.media_type or "application/octet-stream",
                )
                kwargs["data"] = body
                kwargs["headers"] = {
                    "x-goog-api-key": self.api_key,
                    "Content-Type": content_type,
                }
            else:
                kwargs["data"] = media_bytes
                kwargs["headers"] = {
                    "x-goog-api-key": self.api_key,
                    "Content-Type": request.media_type or "application/octet-stream",
                }
        elif request.body is not None:
            kwargs["json"] = request.body
        response = requests.request(**kwargs)
        payload: Any
        try:
            payload = response.json()
        except Exception:
            payload = response.text
        return {
            "ok": response.status_code < 400,
            "status_code": response.status_code,
            "json": payload,
            "url": response.url,
        }


def _multipart_related_body(*, metadata: Any, media_bytes: bytes, media_type: str) -> tuple[bytes, str]:
    boundary = f"gemini-api-tool-{uuid.uuid4().hex}"
    metadata_json = json.dumps(metadata, separators=(",", ":")).encode("utf-8")
    parts = [
        f"--{boundary}\r\n".encode("ascii"),
        b"Content-Type: application/json; charset=UTF-8\r\n\r\n",
        metadata_json,
        b"\r\n",
        f"--{boundary}\r\n".encode("ascii"),
        f"Content-Type: {media_type}\r\n\r\n".encode("ascii"),
        media_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode("ascii"),
    ]
    return b"".join(parts), f"multipart/related; boundary={boundary}"


def _flag_name(name: str) -> str:
    return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name).replace("_", "-").lower()


def _choose_version(op: OperationSpec, requested: str | None) -> str:
    if requested:
        if requested not in op.versions:
            raise ValueError(f"{op.operation_id} is not available in {requested}")
        return requested
    if "v1beta" in op.versions:
        return "v1beta"
    return op.versions[0]


def load_json_arg(value: str | None) -> Any:
    if not value:
        return None
    candidate = Path(value)
    if candidate.exists():
        return json.loads(candidate.read_text(encoding="utf-8"))
    return json.loads(value)


def _review_fields(
    op: OperationSpec,
    request: GeminiRequest,
    path_values: dict[str, str],
) -> dict[str, Any]:
    body_digest = None
    if request.body is not None:
        canonical = json.dumps(request.body, sort_keys=True, separators=(",", ":"))
        body_digest = hashlib.sha256(canonical.encode()).hexdigest()
    return {
        "operation_id": op.operation_id,
        "method": request.method,
        "url": request.url,
        "path_values": path_values,
        "query_values": request.params,
        "body_sha256": body_digest,
        "media_file": request.media_file,
        "media_type": request.media_type,
        "media_sha256": request.media_digest(),
    }


def _plan_signature(
    key: str, plan_id: str, sent_plans: Path, fields: dict[str, Any],
) -> str:
    message = json.dumps(["gemini-plan-v2", plan_id, str(sent_plans.resolve()), fields], sort_keys=True)
    return hmac.new(key.encode(), message.encode(), hashlib.sha256).hexdigest()


def _plan_for(
    op: OperationSpec,
    fields: dict[str, Any],
    plan_id: str,
    signature: str,
) -> dict[str, Any]:
    risk_flags = list(op.risk_flags)
    if op.method_name in ASYNC_BATCH_METHODS:
        risk_flags.append("no_snapshot")
    warnings = [
        label
        for flag, label in (
            ("no_snapshot", "no_snapshot_available"),
            ("destructive", "destructive_action"),
            ("permission", "permission_change"),
            ("bulk", "bulk_or_batch_action"),
        )
        if flag in risk_flags
    ]
    if may_charge(op):
        warnings.append("can_cost_money")
    return {
        **fields,
        "plan_id": plan_id,
        "signature": signature,
        "command": list(op.command_key),
        "body": None,
        "warnings": warnings,
        "safety_class": "state_changing",
        "risk_flags": risk_flags,
        "review_required": True,
    }


def _write_json(path: str | None, payload: dict[str, Any]) -> None:
    if path:
        write_json_file(path, payload)


def _refuse(message: str) -> dict[str, Any]:
    return {"ok": False, "refused": True, "error": message}


def execute_operation(
    op: OperationSpec,
    *,
    client: GeminiClient,
    path_values: dict[str, str],
    query_values: dict[str, Any],
    body: Any,
    media_file: str | None,
    apply: bool,
    yes: bool,
    ack_no_snapshot: bool,
    ack_irreversible: bool,
    plan_in: str | None,
    receipt_out: str | None,
    plan_out: str | None = None,
    api_version: str | None = None,
    ack_spend_money: bool = False,
    sent_plans: Path | None = None,
) -> dict[str, Any]:
    planning = requires_plan(op)
    if may_charge(op) and (not planning or apply) and not ack_spend_money:
        return _refuse("This request can cost money. Get spending approval before using --ack-spend-money.")

    if planning and apply:
        if not plan_in:
            return _refuse("Live apply requires --plan-in with a reviewed dry-run plan.")
        if not yes:
            return _refuse("Live apply requires --yes.")
        if ("no_snapshot" in op.risk_flags or op.method_name in ASYNC_BATCH_METHODS) and not ack_no_snapshot:
            return _refuse("There is no snapshot to restore. Add --ack-no-snapshot after review.")
        if "irreversible" in op.risk_flags and not ack_irreversible:
            return _refuse("This action can be irreversible. Add --ack-irreversible after review.")

    try:
        request = client.build_request(
            op,
            path_values=path_values,
            query_values=query_values,
            body=body,
            api_version=api_version,
            media_file=media_file,
        )
        if media_file:
            request = dataclasses.replace(request, media_bytes=Path(media_file).read_bytes())
    except (ValueError, OSError) as exc:
        return {"ok": False, "error": str(exc), "error_type": type(exc).__name__}

    if not planning:
        response = client.send(request)
        return {
            "ok": bool(response.get("ok")),
            "operation_id": op.operation_id,
            "dry_run": False,
            "request": request.redacted(),
            "response": response,
        }

    if sent_plans is None:
        sent_plans = Path(plan_in or plan_out or "plan.json").resolve().parent / ".state" / "runs" / "sent-plans"
    fields = _review_fields(op, request, path_values)
    if not apply:
        plan_id = uuid.uuid4().hex
        signature = _plan_signature(client.api_key, plan_id, sent_plans, fields)
        plan = _plan_for(op, fields, plan_id, signature)
        _write_json(plan_out, plan)
        return {
            "ok": True,
            "dry_run": True,
            "status": "review_required",
            "plan": plan,
            "next_step": "Review the request, then apply with --plan-in, --apply, --yes, and any required approvals.",
        }

    assert plan_in is not None
    reviewed = read_json_file(plan_in)
    if not isinstance(reviewed, dict):
        return _refuse("Generate and review a new Gemini plan.")
    plan_id = reviewed.get("plan_id")
    signature = reviewed.get("signature")
    if (
        not isinstance(plan_id, str)
        or not re.fullmatch(r"[0-9a-f]{32}", plan_id)
        or not isinstance(signature, str)
        or not re.fullmatch(r"[0-9a-f]{64}", signature)
    ):
        return _refuse("This saved plan uses an older or invalid format. Generate and review a new plan.")
    expected = _plan_signature(client.api_key, plan_id, sent_plans, fields)
    if not hmac.compare_digest(signature, expected) or any(
        reviewed.get(name) != value for name, value in fields.items()
    ):
        return _refuse("The request, API key, or settings folder changed since the reviewed plan. Review a new plan.")

    sent_plans.mkdir(parents=True, exist_ok=True)
    try:
        # Claim this plan before sending so parallel applies cannot both send it.
        (sent_plans / plan_id).mkdir()
    except FileExistsError:
        return _refuse("This plan was already attempted. Check the result in Gemini before making a new plan.")

    receipt = {
        "operation_id": op.operation_id,
        "plan_id": plan_id,
        "dry_run": False,
        "request": request.redacted(),
    }
    try:
        response = client.send(request)
    except requests.exceptions.RequestException:
        receipt.update(
            ok=False,
            applied=None,
            status="outcome_unknown",
            error="Gemini did not reply.",
            verification="No reply from Gemini. Check whether the action happened before trying again.",
        )
    else:
        receipt.update(
            ok=bool(response.get("ok")),
            applied=bool(response.get("ok")),
            response=response,
            verification="Gemini replied. Check the changed resource separately when possible.",
        )
    _write_json(receipt_out, receipt)
    return receipt


def operation_from_command(family: str, method_name: str) -> OperationSpec:
    try:
        return OPERATION_BY_COMMAND[(family, method_name)]
    except KeyError as exc:
        raise KeyError(f"Unknown Gemini command: {family} {method_name}") from exc

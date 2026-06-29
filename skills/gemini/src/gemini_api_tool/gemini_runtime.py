from __future__ import annotations

import dataclasses
import json
import mimetypes
import re
import uuid
from pathlib import Path
from typing import Any

import requests

from .operation_registry import OPERATION_BY_COMMAND, OperationSpec

BASE_URL = "https://generativelanguage.googleapis.com"
SECRET_REPLACEMENT = "[REDACTED]"


@dataclasses.dataclass(frozen=True)
class GeminiRequest:
    method: str
    url: str
    headers: dict[str, str]
    params: dict[str, Any]
    body: Any
    media_file: str | None = None
    media_type: str | None = None

    def redacted(self) -> dict[str, Any]:
        headers = dict(self.headers)
        if "x-goog-api-key" in headers:
            headers["x-goog-api-key"] = SECRET_REPLACEMENT
        return {
            "method": self.method,
            "url": self.url,
            "headers": headers,
            "params": self.params,
            "body": self.body,
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
            media_path = Path(request.media_file)
            media_bytes = media_path.read_bytes()
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


def _plan_for(op: OperationSpec, request: GeminiRequest) -> dict[str, Any]:
    warnings: list[str] = []
    if op.safety_class == "state_changing":
        warnings.append("no_snapshot_available")
    if "destructive" in op.risk_flags:
        warnings.append("destructive_action")
    if "permission" in op.risk_flags:
        warnings.append("permission_change")
    if "bulk" in op.risk_flags:
        warnings.append("bulk_or_batch_action")
    return {
        "operation_id": op.operation_id,
        "command": [op.family, op.method_name],
        "method": request.method,
        "url": request.url,
        "path_values": _extract_path_values(op, request.url),
        "query_values": request.params,
        "body": request.body,
        "media_file": request.media_file,
        "warnings": warnings,
        "safety_class": op.safety_class,
        "risk_flags": list(op.risk_flags),
        "review_required": True,
    }


def _extract_path_values(op: OperationSpec, url: str) -> dict[str, Any]:
    _ = op, url
    return {}


def _write_json(path: str | None, payload: dict[str, Any]) -> None:
    if not path:
        return
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_plan(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _same_reviewed_target(
    plan: dict[str, Any],
    request: GeminiRequest,
    op: OperationSpec,
    path_values: dict[str, str],
) -> bool:
    return (
        plan.get("operation_id") == op.operation_id
        and plan.get("method") == request.method
        and plan.get("url") == request.url
        and plan.get("path_values", {}) == path_values
        and plan.get("query_values", {}) == request.params
        and plan.get("body") == request.body
        and plan.get("media_file") == request.media_file
    )


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
) -> dict[str, Any]:
    try:
        request = client.build_request(
            op,
            path_values=path_values,
            query_values=query_values,
            body=body,
            api_version=api_version,
            media_file=media_file,
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc), "error_type": type(exc).__name__}

    if op.safety_class != "state_changing":
        response = client.send(request)
        return {
            "ok": bool(response.get("ok")),
            "operation_id": op.operation_id,
            "dry_run": False,
            "request": request.redacted(),
            "response": response,
        }

    if not apply:
        plan = _plan_for(op, request)
        plan["path_values"] = path_values
        _write_json(plan_out, plan)
        return {
            "ok": True,
            "dry_run": True,
            "status": "review_required",
            "plan": plan,
            "next_step": "Review the plan, then apply with --plan-in, --apply, --yes, and required acknowledgements.",
        }

    reviewed = _load_plan(plan_in)
    if not reviewed:
        return {"ok": False, "refused": True, "error": "Live apply requires --plan-in with a reviewed dry-run plan."}
    if not yes:
        return {"ok": False, "refused": True, "error": "Live apply requires --yes."}
    if not _same_reviewed_target(reviewed, request, op, path_values):
        return {"ok": False, "refused": True, "error": "The reviewed plan does not match this apply request."}
    if "no_snapshot" in op.risk_flags and not ack_no_snapshot:
        return {"ok": False, "refused": True, "error": "This operation has no safe before-state snapshot. Add --ack-no-snapshot after review."}
    if "irreversible" in op.risk_flags and not ack_irreversible:
        return {"ok": False, "refused": True, "error": "This operation can be irreversible. Add --ack-irreversible after review."}

    response = client.send(request)
    receipt = {
        "ok": bool(response.get("ok")),
        "operation_id": op.operation_id,
        "dry_run": False,
        "applied": bool(response.get("ok")),
        "request": request.redacted(),
        "response": response,
        "verification": "Provider response captured; live read-back is operation-specific and not assumed.",
    }
    _write_json(receipt_out, receipt)
    return receipt


def operation_from_command(family: str, method_name: str) -> OperationSpec:
    try:
        return OPERATION_BY_COMMAND[(family, method_name)]
    except KeyError as exc:
        raise KeyError(f"Unknown Gemini command: {family} {method_name}") from exc

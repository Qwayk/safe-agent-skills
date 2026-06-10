from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import SafetyError, ValidationError
from .json_files import read_json_file, write_json_file
from .youtube_discovery import MethodInfo, get_method_info, load_official_discovery_doc
from .commands.write_safety import before_state_refusal_verification_plan, blocked_before_state, recovery_contract


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_hex(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def _canonical_json_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))).encode("utf-8")


def build_no_recovery_contract() -> dict[str, Any]:
    return recovery_contract()


def compute_request_fingerprint(
    *,
    method: str,
    url_path: str,
    http_method: str,
    params: dict[str, Any],
    body: Any,
    upload: dict[str, Any] | None,
    download: dict[str, Any] | None,
) -> str:
    payload = {
        "method": method,
        "http_method": http_method,
        "url_path": url_path,
        "params": params,
        "body": body,
        "upload": upload,
        "download": download,
    }
    return _sha256_hex(_canonical_json_bytes(payload))


@dataclass(frozen=True)
class UploadSpec:
    path: str
    size_bytes: int
    mtime_utc: str
    mime_type: str | None
    protocol: str

    @classmethod
    def from_file(cls, *, path: str, mime_type: str | None, protocol: str) -> "UploadSpec":
        p = Path(path)
        if not p.exists():
            raise ValidationError(f"Upload file not found: {p}")
        st = p.stat()
        return cls(
            path=str(p),
            size_bytes=int(st.st_size),
            mtime_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
            mime_type=mime_type,
            protocol=protocol,
        )

    def to_plan_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "size_bytes": self.size_bytes,
            "mtime_utc": self.mtime_utc,
            "mime_type": self.mime_type,
            "protocol": self.protocol,
        }


@dataclass(frozen=True)
class DownloadSpec:
    to_path: str
    overwrite: bool

    def to_plan_dict(self) -> dict[str, Any]:
        return {
            "to_path": self.to_path,
            "overwrite": bool(self.overwrite),
        }


def classify_risk(*, method_info: MethodInfo, upload: UploadSpec | None) -> tuple[str, list[str]]:
    hm = method_info.http_method.upper()
    if hm == "GET":
        return "low", ["Read-only method (GET)"]

    reasons: list[str] = []
    if hm == "DELETE" or method_info.name.endswith(".delete"):
        return "irreversible", ["Delete method (irreversible)"]

    if upload is not None:
        reasons.append("Media upload request")
    reasons.append(f"Write-capable method ({hm})")
    return "high" if upload is not None else "medium", reasons


def build_api_call_plan(
    *,
    ctx: dict[str, Any],
    method: str,
    params: dict[str, Any],
    body: Any,
    upload: UploadSpec | None,
    download: DownloadSpec | None,
) -> dict[str, Any]:
    discovery = load_official_discovery_doc()
    info = get_method_info(discovery_obj=discovery, method_name=method)

    required_params = [p.name for p in info.params if p.required]
    missing_required = [p for p in required_params if (p not in params or params.get(p) in ("", None))]

    risk_level, risk_reasons = classify_risk(method_info=info, upload=upload)

    upload_plan = upload.to_plan_dict() if upload is not None else None
    download_plan = download.to_plan_dict() if download is not None else None
    req_fp = compute_request_fingerprint(
        method=info.name,
        http_method=info.http_method,
        url_path=info.path,
        params={k: params[k] for k in sorted(params)},
        body=body,
        upload=upload_plan,
        download=download_plan,
    )

    preconditions: list[str] = ["env_fingerprint must match", "request_fingerprint must match"]
    if missing_required:
        preconditions.append("required_params must be provided before apply")

    verification_plan = {
        "type": "api_call",
        "notes": "API method call plan. GET reads may execute with --live; non-GET methods require explicit no-snapshot approval before apply.",
    }
    if info.http_method.upper() != "GET":
        verification_plan = before_state_refusal_verification_plan()

    plan = {
        "tool": ctx.get("tool") or "youtube-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url if ctx.get("cfg") else None,
        "command": ctx.get("command_str") or None,
        "selector": {"kind": "youtube_method", "value": info.name},
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url if ctx.get("cfg") else None,
            "request_fingerprint_sha256": req_fp,
        },
        "request": {
            "method": info.name,
            "http_method": info.http_method,
            "path": info.path,
            "scopes": list(info.scopes),
            "params": {k: params[k] for k in sorted(params)},
            "body": body,
            "upload": upload_plan,
            "download": download_plan,
            "missing_required_params": missing_required,
        },
        # API method calls can't promise a resource-level diff without domain-specific logic.
        "proposed_changes": [],
        "verification_plan": verification_plan,
        "recovery": build_no_recovery_contract(),
    }
    if info.http_method.upper() != "GET":
        plan["before_state"] = blocked_before_state(
            action=f"api.{info.name}",
            provider_write={
                "service": "YouTube Data API v3",
                "method": info.name,
                "http_method": info.http_method,
                "path": info.path,
                "media_upload": bool(upload_plan),
            },
        )
    return plan


def load_or_build_plan(
    *,
    ctx: dict[str, Any],
    method: str,
    params: dict[str, Any],
    body: Any,
    upload: UploadSpec | None,
    download: DownloadSpec | None,
) -> dict[str, Any]:
    plan_in = ctx.get("plan_in")
    if plan_in:
        obj = read_json_file(plan_in)
        if not isinstance(obj, dict):
            raise ValidationError("Plan file must be a JSON object")
        return obj
    return build_api_call_plan(ctx=ctx, method=method, params=params, body=body, upload=upload, download=download)


def write_plan_if_requested(*, ctx: dict[str, Any], plan: dict[str, Any]) -> str | None:
    plan_out = ctx.get("plan_out")
    if not plan_out:
        return None
    return write_json_file(plan_out, plan)


def validate_plan_for_apply(
    *,
    ctx: dict[str, Any],
    plan: dict[str, Any],
    expected_method: str,
    expected_info: MethodInfo,
) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise ValidationError("Plan must be a JSON object")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")

    req = plan.get("request")
    if not isinstance(req, dict):
        raise ValidationError("Plan missing request dict")
    if str(req.get("method") or "") != expected_method:
        raise SafetyError("Refused: plan method does not match requested method")
    if str(req.get("http_method") or "").upper() != str(expected_info.http_method).upper():
        raise SafetyError("Refused: plan http_method does not match discovery snapshot")
    if str(req.get("path") or "") != str(expected_info.path):
        raise SafetyError("Refused: plan path does not match discovery snapshot")

    expected_fp = str(baseline.get("request_fingerprint_sha256") or "")
    if not expected_fp:
        raise ValidationError("Plan missing request_fingerprint_sha256")

    computed_fp = compute_request_fingerprint(
        method=str(req.get("method") or ""),
        http_method=str(req.get("http_method") or ""),
        url_path=str(req.get("path") or ""),
        params={k: req.get("params", {}).get(k) for k in sorted((req.get("params") or {}).keys())}
        if isinstance(req.get("params"), dict)
        else {},
        body=req.get("body"),
        upload=req.get("upload") if isinstance(req.get("upload"), dict) else None,
        download=req.get("download") if isinstance(req.get("download"), dict) else None,
    )
    if computed_fp != expected_fp:
        raise SafetyError("Refused: plan fingerprint does not match current request payload")
    return req

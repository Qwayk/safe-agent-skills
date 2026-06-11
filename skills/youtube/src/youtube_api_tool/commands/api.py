from __future__ import annotations

import hashlib
import json
import mimetypes
import secrets
import time
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit, urlunsplit

from ..api_call import (
    DownloadSpec,
    UploadSpec,
    build_no_recovery_contract,
    load_or_build_plan,
    validate_plan_for_apply,
    write_plan_if_requested,
)
from ..errors import NotSupportedError, SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..oauth_tokens import read_token_json, token_path_for_env_file
from ..youtube_discovery import get_method_info, load_official_discovery_doc
from .write_safety import ensure_blocked_apply_contract, refusal_output


def _parse_json_arg(val: str) -> Any:
    try:
        return json.loads(val)
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Invalid JSON: {type(e).__name__}: {e}") from None


def _merge_dicts(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        out[str(k)] = v
    return out


def _parse_params(args: Any) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if getattr(args, "params_file", None):
        obj = read_json_file(str(args.params_file))
        if not isinstance(obj, dict):
            raise ValidationError("--params-file must be a JSON object")
        out = _merge_dicts(out, obj)
    if getattr(args, "params_json", None):
        obj = _parse_json_arg(str(args.params_json))
        if not isinstance(obj, dict):
            raise ValidationError("--params-json must be a JSON object")
        out = _merge_dicts(out, obj)
    return out


def _parse_body(args: Any) -> Any:
    body_sources = [
        bool(getattr(args, "body_file", None)),
        bool(getattr(args, "body_json", None)),
        bool(getattr(args, "body_stdin", False)),
    ]
    if sum(body_sources) > 1:
        raise ValidationError("Body may be provided only once (use one of: --body-file, --body-json, --body-stdin)")

    if getattr(args, "body_file", None):
        return read_json_file(str(args.body_file))
    if getattr(args, "body_json", None):
        return _parse_json_arg(str(args.body_json))
    if bool(getattr(args, "body_stdin", False)):
        import sys

        raw = sys.stdin.read().strip()
        if not raw:
            return None
        return _parse_json_arg(raw)
    return None


def _guess_mime(path: str) -> str:
    mt, _ = mimetypes.guess_type(path)
    return mt or "application/octet-stream"


def _redact_upload_session_url(url: str) -> str:
    """
    Resumable upload session URLs can be used to continue an upload; keep them out of receipts/logs.
    """
    try:
        parts = urlsplit(url)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    except Exception:
        return "***REDACTED***"


def _mtime_utc_from_epoch_seconds(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def _assert_upload_file_matches_plan(*, upload_plan: dict[str, Any]) -> None:
    raw_path = str(upload_plan.get("path") or "").strip()
    if not raw_path:
        raise ValidationError("Plan upload missing path")
    p = Path(raw_path)
    if not p.exists():
        raise SafetyError(f"Refused: upload file missing at apply time: {p}")
    st = p.stat()
    expected_size = int(upload_plan.get("size_bytes") or 0)
    expected_mtime_utc = str(upload_plan.get("mtime_utc") or "")
    cur_mtime_utc = _mtime_utc_from_epoch_seconds(float(st.st_mtime))
    if int(st.st_size) != expected_size or cur_mtime_utc != expected_mtime_utc:
        raise SafetyError("Refused: upload file drift detected since plan creation (size/mtime mismatch)")


def _write_stream_to_file_with_sha256(*, data: bytes, out_path: Path, overwrite: bool) -> dict[str, Any]:
    if out_path.exists() and not overwrite:
        raise SafetyError("Refused: download output file already exists (pass --download-overwrite or --yes)")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    with open(out_path, "wb") as f:  # noqa: PTH123
        f.write(data)
        h.update(data)
    return {"path": str(out_path), "sha256": h.hexdigest(), "size_bytes": int(out_path.stat().st_size)}


def _extract_entity_id_from_write_response(resp_json: Any) -> str | None:
    if isinstance(resp_json, dict):
        rid = resp_json.get("id")
        if isinstance(rid, str) and rid.strip():
            return rid.strip()
        items = resp_json.get("items")
        if isinstance(items, list) and items:
            first = items[0]
            if isinstance(first, dict):
                fid = first.get("id")
                if isinstance(fid, str) and fid.strip():
                    return fid.strip()
    return None


def _attempt_read_back_verification(
    *,
    discovery: dict[str, Any],
    write_method: str,
    write_req_params: dict[str, Any],
    write_resp_json: Any,
    cfg: Any,
    client: HttpClient,
    headers: dict[str, str],
) -> dict[str, Any] | None:
    """
    Best-effort read-back verification for approved writes when a direct read path can be inferred.

    Strategy:
    - If the write response includes an id, and a sibling `<resource>.list` exists that supports `id`,
      perform a GET read-back and confirm the id is present in `items`.
    - Only attempt when the read-back method's required params are satisfied by `id` and `part`.
    """
    entity_id = _extract_entity_id_from_write_response(write_resp_json)
    if not entity_id:
        return None

    resource_prefix = str(write_method).rsplit(".", 1)[0]
    read_method = f"{resource_prefix}.list"
    try:
        read_info = get_method_info(discovery_obj=discovery, method_name=read_method)
    except Exception:
        return None

    required = {p.name for p in read_info.params if p.required}
    if not required.issubset({"id", "part"}):
        return None

    if not any(p.name == "id" for p in read_info.params):
        return None

    part_val = write_req_params.get("part")
    if "part" in required and (not isinstance(part_val, str) or not part_val.strip()):
        return None

    base_url = str(cfg.base_url).rstrip("/")
    read_url = base_url + "/" + str(read_info.path).lstrip("/")
    read_params: dict[str, Any] = {"id": entity_id}
    if part_val is not None:
        read_params["part"] = part_val

    # If the write used API key fallback (rare for writes), preserve it for read-back.
    if getattr(cfg, "api_key", None) and "key" in write_req_params and "key" not in read_params:
        read_params["key"] = write_req_params.get("key")

    try:
        read_resp = client.request("GET", read_url, headers=headers, params=read_params, json_body=None)
        try:
            read_json = read_resp.json()
        except Exception:
            read_json = None
        found = False
        ids_preview: list[str] = []
        items_count = None
        if isinstance(read_json, dict):
            items = read_json.get("items")
            if isinstance(items, list):
                items_count = len(items)
                for it in items[:3]:
                    if isinstance(it, dict) and isinstance(it.get("id"), str):
                        ids_preview.append(str(it.get("id")))
                found = any(isinstance(it, dict) and str(it.get("id") or "") == entity_id for it in items)
        return {
            "ok": bool(found),
            "details": {
                "type": "read_back",
                "entity_id": entity_id,
                "read_method": read_method,
                "read_status": read_resp.status,
                "read_url": read_resp.url,
                "items_count": items_count,
                "ids_preview": ids_preview,
                "found": bool(found),
            },
        }
    except Exception as e:  # noqa: BLE001
        return {
            "ok": False,
            "details": {
                "type": "read_back_error",
                "entity_id": entity_id,
                "read_method": read_method,
                "error_type": type(e).__name__,
                "error": str(e),
            },
        }


def _oauth_access_token(*, ctx: dict[str, Any]) -> str:
    cfg = ctx["cfg"]
    token_path = token_path_for_env_file(ctx["env_file"])
    data = read_token_json(token_path)
    if not isinstance(data, dict):
        raise ValidationError(
            f"Missing OAuth token file: {token_path} (run `youtube-api-tool auth login --console`)"
        )

    try:
        from google.auth.transport.requests import Request  # type: ignore
        from google.oauth2.credentials import Credentials  # type: ignore
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"Missing google-auth deps: {type(e).__name__}: {e}") from None

    creds = Credentials.from_authorized_user_info(data, scopes=list(cfg.oauth_scopes))
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
    if not creds.token:
        raise ValidationError("OAuth token missing access token")
    return str(creds.token)


def _multipart_related_stream(*, metadata_json: bytes, file_path: str, mime_type: str, boundary: str) -> Iterable[bytes]:
    pre = (
        f"--{boundary}\r\n"
        "Content-Type: application/json; charset=UTF-8\r\n\r\n"
    ).encode("utf-8") + metadata_json + b"\r\n"
    mid = (
        f"--{boundary}\r\n"
        f"Content-Type: {mime_type}\r\n"
        "Content-Transfer-Encoding: binary\r\n\r\n"
    ).encode("utf-8")
    post = f"\r\n--{boundary}--\r\n".encode("utf-8")

    yield pre
    yield mid
    with open(file_path, "rb") as f:  # noqa: PTH123
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            yield chunk
    yield post


def cmd_api_call(args: Any, ctx: dict[str, Any]) -> int:
    method = str(getattr(args, "api_method_id", "") or "").strip()
    if not method:
        raise ValidationError("Internal error: missing api method id")

    live = bool(getattr(args, "live", False))
    paginate = bool(getattr(args, "paginate", False))
    max_pages = int(getattr(args, "max_pages", 5) or 5)
    if max_pages <= 0:
        raise ValidationError("--max-pages must be >= 1")

    plan_in = str(ctx.get("plan_in") or "").strip()
    if plan_in:
        conflicting = []
        if getattr(args, "params_json", None) or getattr(args, "params_file", None):
            conflicting.append("--params-*")
        if getattr(args, "body_json", None) or getattr(args, "body_file", None) or bool(getattr(args, "body_stdin", False)):
            conflicting.append("--body-*")
        if getattr(args, "upload_file", None) or getattr(args, "upload_mime", None):
            conflicting.append("--upload-*")
        if getattr(args, "download_to", None) or bool(getattr(args, "download_overwrite", False)):
            conflicting.append("--download-*")
        if bool(getattr(args, "paginate", False)):
            conflicting.append("--paginate/--max-pages")
        if conflicting:
            raise ValidationError(f"When using --plan-in, do not pass request-building flags: {', '.join(conflicting)}")

    # Validate method existence early and enforce upload flag correctness.
    discovery = load_official_discovery_doc()
    info = get_method_info(discovery_obj=discovery, method_name=method)
    hm = info.http_method.upper()

    params: dict[str, Any] = {}
    body: Any = None
    upload: UploadSpec | None = None
    download: DownloadSpec | None = None
    if not plan_in:
        params = _parse_params(args)
        body = _parse_body(args)

        upload_file = str(getattr(args, "upload_file", "") or "").strip()
        upload_protocol = str(getattr(args, "upload_protocol", "") or "simple").strip().lower()
        upload_mime = str(getattr(args, "upload_mime", "") or "").strip() or None
        if upload_file:
            if upload_protocol not in {"simple", "resumable"}:
                raise ValidationError("--upload-protocol must be one of: simple, resumable")
            if not info.has_media_upload:
                raise ValidationError(f"Method does not support media upload: {method}")
            if upload_protocol == "simple" and not info.media_simple_path:
                raise NotSupportedError("This mediaUpload method does not support the simple protocol in the discovery snapshot")
            if upload_protocol == "resumable" and not info.media_resumable_path:
                raise NotSupportedError("This mediaUpload method does not support the resumable protocol in the discovery snapshot")
            upload = UploadSpec.from_file(path=upload_file, mime_type=upload_mime or _guess_mime(upload_file), protocol=upload_protocol)

        download_to = str(getattr(args, "download_to", "") or "").strip() or None
        if download_to:
            if info.http_method.upper() != "GET":
                raise ValidationError("--download-to is only valid for GET methods")
            if not bool(info.supports_media_download):
                raise ValidationError(f"Method is not a supportsMediaDownload method: {method}")
            download = DownloadSpec(to_path=download_to, overwrite=bool(getattr(args, "download_overwrite", False)) or bool(ctx.get("yes")))

    plan = load_or_build_plan(ctx=ctx, method=method, params=params, body=body, upload=upload, download=download)
    plan_path = write_plan_if_requested(ctx=ctx, plan=plan)

    # Reads are executed only when explicitly requested via --live.
    # `--apply` is reserved for write-capable methods and must never trigger a live GET.
    should_execute_read = (hm == "GET") and live
    if hm == "GET" and bool(ctx.get("apply")):
        raise SafetyError("Refused: GET methods do not use --apply; use --live")
    if paginate and not should_execute_read:
        raise ValidationError("--paginate requires a live GET (use --live on a GET method)")

    if not bool(ctx.get("apply")) and not should_execute_read:
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("api.call.plan", {"method": method, "plan_out": plan_path, "plan_in": plan_in or None})
        ctx["out"].emit(out)
        return 0

    req = validate_plan_for_apply(ctx=ctx, plan=plan, expected_method=method, expected_info=info)

    req_params = req.get("params")
    if not isinstance(req_params, dict):
        raise ValidationError("Plan request params must be a JSON object")

    upload_plan = req.get("upload")
    has_upload = isinstance(upload_plan, dict) and bool(upload_plan.get("path"))
    if has_upload and not info.has_media_upload:
        raise ValidationError(f"Method does not support media upload: {method}")

    download_plan = req.get("download")
    has_download = isinstance(download_plan, dict) and bool(str(download_plan.get("to_path") or "").strip())
    if has_download:
        if hm != "GET":
            raise ValidationError("Plan download is only supported for GET methods")
        if not bool(info.supports_media_download):
            raise ValidationError(f"Method is not a supportsMediaDownload method: {method}")

    if bool(ctx.get("apply")):
        if hm != "GET" and not bool(ctx.get("yes")):
            raise SafetyError("Refused: non-GET API requests require --apply --yes")
        if (hm == "DELETE" or method.endswith(".delete")) and not bool(ctx.get("ack_irreversible")):
            raise SafetyError("Refused: delete methods require --apply --yes --ack-irreversible")
        if info.has_media_upload and not has_upload:
            raise SafetyError("Refused: media upload methods require --apply --yes and --upload-file")
        if has_upload and not bool(ctx.get("yes")):
            raise SafetyError("Refused: media uploads require --apply --yes")

    if hm == "GET" and bool(info.supports_media_download) and should_execute_read and not has_download:
        raise ValidationError("This method returns a media download body; pass --download-to <path> to save it")

    missing = req.get("missing_required_params") or []
    if missing and bool(ctx.get("apply")):
        raise ValidationError(f"Missing required params for apply: {', '.join([str(x) for x in missing])}")
    if missing and should_execute_read:
        raise ValidationError(f"Missing required params for live read: {', '.join([str(x) for x in missing])}")

    if bool(ctx.get("apply")) and hm != "GET":
        if has_upload:
            if not isinstance(upload_plan, dict):
                raise ValidationError("Plan upload must be a JSON object")
            _assert_upload_file_matches_plan(upload_plan=upload_plan)
        plan = ensure_blocked_apply_contract(
            plan,
            action=f"api.{method}",
            provider_write={
                "service": "YouTube Data API v3",
                "method": method,
                "http_method": hm,
                "path": info.path,
                "media_upload": bool(has_upload),
            },
        )
        if not bool(ctx.get("ack_no_snapshot")):
            out = refusal_output(plan=plan)
            ctx["audit"].write("api.call.refused", {"method": method, "plan_out": plan_path, "media_upload": bool(has_upload)})
            ctx["out"].emit(out)
            return 0

    cfg = ctx["cfg"]

    token: str | None
    if has_upload:
        token = _oauth_access_token(ctx=ctx)
    elif hm == "GET" and cfg.api_key:
        # Reads: allow API key fallback even if discovery lists OAuth scopes.
        try:
            token = _oauth_access_token(ctx=ctx)
        except Exception:
            token = None
    elif info.scopes:
        token = _oauth_access_token(ctx=ctx)
    else:
        try:
            token = _oauth_access_token(ctx=ctx)
        except Exception:
            token = None

    if (should_execute_read or bool(ctx.get("apply"))) and not token and not cfg.api_key:
        raise ValidationError("Missing credentials: set YOUTUBE_API_KEY or run `youtube-api-tool auth login --console`")

    headers: dict[str, str] = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    query_params = {str(k): v for k, v in req_params.items()}
    if cfg.api_key and not token and "key" not in query_params:
        query_params["key"] = cfg.api_key

    client = HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx["verbose"]),
        user_agent=f"youtube-api-tool/{ctx.get('tool_version')}",
    )

    base_url = str(cfg.base_url).rstrip("/")
    url = base_url + "/" + str(info.path).lstrip("/")

    # Path templating (rare in this discovery doc, but supported).
    if "{" in url and "}" in url:
        for p in info.params:
            if p.location == "path" and ("{" + p.name + "}") in url:
                if p.name not in query_params or query_params.get(p.name) in ("", None):
                    raise ValidationError(f"Missing required path param: {p.name}")
                url = url.replace("{" + p.name + "}", str(query_params.pop(p.name)))

    if hm == "GET" and paginate:
        pages: list[dict[str, Any]] = []
        page_token: str | None = None
        for _ in range(max_pages):
            pparams = dict(query_params)
            if page_token:
                pparams["pageToken"] = page_token
            r = client.request(hm, url, headers=headers, params=pparams, json_body=None)
            try:
                r_json = r.json()
            except Exception:
                r_json = None
            pages.append({"status": r.status, "url": r.url, "json": r_json})
            if not isinstance(r_json, dict):
                break
            page_token = str(r_json.get("nextPageToken") or "").strip() or None
            if not page_token:
                break
        ctx["audit"].write("api.call.read", {"method": method, "pages": len(pages)})
        ctx["out"].emit({"ok": True, "dry_run": False, "live": True, "method": method, "pages": pages, "page_count": len(pages)})
        return 0

    resp = None
    if has_upload:
        if not token:
            raise ValidationError("Missing OAuth credentials for upload (run `youtube-api-tool auth login --console`)")
        if not info.media_multipart:
            raise NotSupportedError("This mediaUpload method is not marked as multipart-capable in the discovery snapshot")
        if not isinstance(upload_plan, dict):
            raise ValidationError("Plan upload must be a JSON object")

        _assert_upload_file_matches_plan(upload_plan=upload_plan)
        up_path = str(upload_plan.get("path") or "")
        mime_type = str(upload_plan.get("mime_type") or "") or _guess_mime(up_path)
        protocol = str(upload_plan.get("protocol") or "simple").strip().lower()
        if protocol not in {"simple", "resumable"}:
            raise ValidationError("Plan upload protocol must be one of: simple, resumable")
        size_bytes = int(upload_plan.get("size_bytes") or 0)

        metadata_obj: Any = req.get("body") if ("body" in req) else None
        if metadata_obj is None:
            metadata_obj = {}

        if protocol == "simple":
            if not info.media_simple_path:
                raise NotSupportedError("This mediaUpload method does not support the simple protocol in the discovery snapshot")
            metadata_json = json.dumps(metadata_obj, ensure_ascii=False, sort_keys=True).encode("utf-8")
            boundary = "boundary_" + secrets.token_hex(16)
            up_headers = dict(headers)
            up_headers["Content-Type"] = f'multipart/related; boundary=\"{boundary}\"'
            up_params = dict(query_params)
            up_params.setdefault("uploadType", "multipart")

            upload_url = base_url + str(info.media_simple_path)
            data_stream = _multipart_related_stream(
                metadata_json=metadata_json,
                file_path=up_path,
                mime_type=mime_type,
                boundary=boundary,
            )
            resp = client.request(hm, upload_url, headers=up_headers, params=up_params, data=data_stream)
        else:
            if not info.media_resumable_path:
                raise NotSupportedError("This mediaUpload method does not support the resumable protocol in the discovery snapshot")
            up_params = dict(query_params)
            up_params.setdefault("uploadType", "resumable")

            init_headers = dict(headers)
            init_headers["Content-Type"] = "application/json; charset=UTF-8"
            init_headers["X-Upload-Content-Type"] = mime_type
            init_headers["X-Upload-Content-Length"] = str(size_bytes)

            init_url = base_url + str(info.media_resumable_path)
            init_resp = client.request(hm, init_url, headers=init_headers, params=up_params, json_body=metadata_obj)
            session_url = str(init_resp.headers.get("location") or "").strip()
            if not session_url:
                raise RuntimeError("Resumable upload initiation missing Location header")

            upload_headers = dict(headers)
            upload_headers["Content-Type"] = mime_type
            upload_headers["Content-Length"] = str(size_bytes)
            with open(up_path, "rb") as f:  # noqa: PTH123
                resp = client.request("PUT", session_url, headers=upload_headers, data=f)
            ctx["audit"].write(
                "api.upload.resumable.session",
                {"method": method, "session_url": _redact_upload_session_url(session_url)},
            )
    else:
        req_body = req.get("body") if ("body" in req) else None
        if hm == "GET" and has_download and bool(info.supports_media_download):
            # Ensure the server returns the raw media body instead of JSON metadata.
            query_params.setdefault("alt", "media")
        resp = client.request(hm, url, headers=headers, params=query_params, json_body=req_body)

    if resp is None:
        raise RuntimeError("Internal error: no HTTP response")

    if hm == "GET" and has_download and bool(info.supports_media_download) and not bool(ctx.get("apply")):
        to_path = Path(str(download_plan.get("to_path") or "").strip())
        overwrite = bool(download_plan.get("overwrite")) or bool(ctx.get("yes"))
        saved = _write_stream_to_file_with_sha256(data=resp.body, out_path=to_path, overwrite=overwrite)
        ctx["audit"].write("api.call.media_download", {"method": method, "status": resp.status, "saved_to": saved.get("path")})
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": False,
                "live": True,
                "method": method,
                "download": saved,
                "response": {"status": resp.status, "url": resp.url, "json": None},
                "plan_out": plan_path,
            }
        )
        return 0

    try:
        resp_json = resp.json()
    except Exception:
        resp_json = None

    response_obj = {"status": resp.status, "url": resp.url, "json": resp_json}
    if hm == "GET" and not bool(ctx.get("apply")):
        ctx["audit"].write("api.call.read", {"method": method, "status": resp.status})
        ctx["out"].emit({"ok": True, "dry_run": False, "live": True, "method": method, "response": response_obj, "plan_out": plan_path})
        return 0

    receipt = {
        "tool": ctx.get("tool") or "youtube-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": cfg.base_url,
        "selector": {"kind": "youtube_method", "value": method},
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {
            "acknowledged": hm != "GET",
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for this YouTube API write.",
        } if hm != "GET" else None,
        "changed": hm != "GET",
        "verification": None,
        "diff_applied": [],
        "response": response_obj,
        "recovery": build_no_recovery_contract(),
    }

    verification = {"ok": resp.status < 400, "details": {"type": "http_status", "status": resp.status}}
    if resp.status < 400 and hm != "GET":
        rb = _attempt_read_back_verification(
            discovery=discovery,
            write_method=method,
            write_req_params=query_params,
            write_resp_json=resp_json,
            cfg=cfg,
            client=client,
            headers=headers,
        )
        if rb is not None:
            verification = {
                "ok": bool(rb.get("ok")),
                "details": _merge_dicts({"write_status": resp.status}, rb.get("details") if isinstance(rb.get("details"), dict) else {}),
            }
        else:
            verification = {
                "ok": resp.status < 400,
                "details": {"type": "http_status_only", "status": resp.status, "reason": "No safe read-back verification strategy available"},
            }

    receipt["verification"] = verification

    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None

    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path, "response": receipt["response"]}
    ctx["audit"].write("api.call.apply", {"method": method, "receipt_out": receipt_path, "status": resp.status})
    ctx["out"].emit(out)
    return 0

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from ..api import PinterestApi, resolve_access_token
from ..write_framework import require_write_allowed
from .write_safety import before_state_contract
from ..http import DownloadResult, HttpClient

TERMINAL_STATUSES = {
    "FINISHED",
    "FAILED",
    "CANCELLED",
    "EXPIRED",
    "DOES_NOT_EXIST",
}


def build_reports_create_path(ad_account_id: str) -> str:
    ad_account_id = str(ad_account_id or "").strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    return f"/ad_accounts/{ad_account_id}/reports"


def build_reports_get_path(ad_account_id: str) -> str:
    return build_reports_create_path(ad_account_id)


def build_reports_template_create_path(ad_account_id: str, template_id: str) -> str:
    ad_account_id = str(ad_account_id or "").strip()
    template_id = str(template_id or "").strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    if not template_id:
        raise RuntimeError("--template-id is required")
    return f"/ad_accounts/{ad_account_id}/templates/{template_id}/reports"


def _as_upper_str(v: Any) -> str | None:
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        return s.upper() if s else None
    return str(v).strip().upper()


def extract_report_status(data: dict[str, Any]) -> str | None:
    if not isinstance(data, dict):
        return None
    for key in ("report_status", "status"):
        if key in data:
            s = _as_upper_str(data.get(key))
            if s:
                return s
    return None


def extract_report_token(data: dict[str, Any]) -> str | None:
    if not isinstance(data, dict):
        return None
    for key in ("token", "report_token", "id"):
        v = data.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def extract_report_url(data: dict[str, Any]) -> str | None:
    if not isinstance(data, dict):
        return None
    for key in ("url", "report_url", "download_url"):
        v = data.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


class PollingCapExceededError(RuntimeError):
    pass


def poll_report_status(
    get_fn: Callable[[str], dict[str, Any]],
    *,
    token: str,
    max_attempts: int,
    max_seconds: float,
    poll_interval_s: float,
    sleep_fn: Callable[[float], None] = time.sleep,
    now_fn: Callable[[], float] = time.monotonic,
) -> dict[str, Any]:
    token = str(token or "").strip()
    if not token:
        raise RuntimeError("--token is required")
    if max_attempts < 1:
        raise RuntimeError("--max-poll-attempts must be >= 1")
    if max_seconds < 0:
        raise RuntimeError("--max-poll-seconds must be >= 0")
    if poll_interval_s < 0:
        raise RuntimeError("--poll-interval-s must be >= 0")

    start = now_fn()
    last_status: str | None = None
    last_data: dict[str, Any] | None = None

    for attempt in range(1, int(max_attempts) + 1):
        elapsed = now_fn() - start
        if elapsed >= float(max_seconds) and float(max_seconds) != 0.0:
            raise PollingCapExceededError(
                f"Polling exceeded max_seconds ({max_seconds}) after {attempt - 1} attempts. "
                f"Last status: {last_status or 'UNKNOWN'}"
            )

        data = get_fn(token)
        if not isinstance(data, dict):
            raise RuntimeError("Unexpected report job response (not an object)")
        last_data = data
        last_status = extract_report_status(data) or "UNKNOWN"

        if last_status in TERMINAL_STATUSES:
            return data

        if attempt >= int(max_attempts):
            raise PollingCapExceededError(
                f"Polling exceeded max_attempts ({max_attempts}). Last status: {last_status}"
            )

        sleep_fn(float(poll_interval_s))

    # Defensive: the loop should return/raise before this.
    raise PollingCapExceededError(
        f"Polling exceeded caps. Last status: {last_status or 'UNKNOWN'}",
    )


_SAFE_TOKEN_RE = re.compile(r"[^a-zA-Z0-9._-]+")


def _sanitize_token(token: str) -> str:
    token = str(token or "").strip()
    token = token.replace(os.sep, "_")
    token = _SAFE_TOKEN_RE.sub("_", token)
    token = token.strip("._-")
    return token or "report"


def safe_filename_for_report(token: str, format_hint: str | None = None) -> str:
    safe_token = _sanitize_token(token)
    hint = (format_hint or "").strip().lower()
    ext = ".bin"
    if "csv" in hint or hint == "text/csv":
        ext = ".csv"
    elif "json" in hint or hint == "application/json":
        ext = ".json"
    elif "zip" in hint or hint == "application/zip":
        ext = ".zip"
    return f"{safe_token}{ext}"


def download_report(
    url: str,
    *,
    http: HttpClient,
    dest_path: str,
    max_bytes: int,
) -> dict[str, Any]:
    res: DownloadResult = http.download_to_file(url, max_bytes=max_bytes, dest_path=dest_path)
    return asdict(res)


def read_json_file(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise RuntimeError("Request body JSON must be an object")
    return data


def ensure_dir(path: str) -> str:
    p = Path(path).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return str(p.resolve())


def write_json_file(path: str, data: dict[str, Any]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def create_report_job(
    api: PinterestApi,
    *,
    ad_account_id: str,
    request_body: dict[str, Any],
) -> dict[str, Any]:
    return api.post(build_reports_create_path(ad_account_id), json_body=request_body)


def get_report_job(
    api: PinterestApi,
    *,
    ad_account_id: str,
    token: str,
) -> dict[str, Any]:
    token = str(token or "").strip()
    if not token:
        raise RuntimeError("--token is required")
    return api.get(build_reports_get_path(ad_account_id), params={"token": token})


def api_from_ctx(ctx: dict[str, Any]) -> PinterestApi:
    cfg = ctx["cfg"]
    return PinterestApi(
        base_url=cfg.base_url,
        http=ctx["http"],
        access_token=resolve_access_token(
            env_file=ctx["env_file"],
            env_access_token=cfg.access_token,
            env_refresh_token=cfg.refresh_token,
            app_id=cfg.app_id,
            app_secret=cfg.app_secret,
            base_url=cfg.base_url,
            http=ctx["http"],
        ),
    )


def _require_apply_yes_ack_volume(ctx: dict[str, Any], *, action: str, label: str) -> None:
    _ = action, label
    require_write_allowed(ctx, acks_required=["ack-volume"])


def _no_snapshot_fields(*, action: str) -> dict[str, Any]:
    reason = "No reliable before-state snapshot is available for this Pinterest report job write."
    return {
        "before_state": before_state_contract(
            reason=reason,
            provider_write={
                "service": "Pinterest API",
                "action": action,
                "operations": [{"method": "POST", "path": "/ad_accounts/{ad_account_id}/reports"}],
            },
        ),
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": reason,
        },
    }


def format_hint_from_url(url: str) -> str | None:
    u = (url or "").strip().lower()
    if u.endswith(".csv"):
        return "csv"
    if u.endswith(".json"):
        return "json"
    if u.endswith(".zip"):
        return "zip"
    return None


def cmd_ads_reports_create(args: Any, ctx: dict[str, Any]) -> int:
    _require_apply_yes_ack_volume(ctx, action="ads.reports.create", label="report job creation")
    api = api_from_ctx(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    body = read_json_file(str(args.body_file))

    data = create_report_job(api, ad_account_id=ad_account_id, request_body=body)
    token = extract_report_token(data)
    if not token:
        raise RuntimeError("Report create response missing token")

    out = {
        "ok": True,
        "ad_account_id": ad_account_id,
        "token": token,
        "warnings": [
            "Creating report jobs triggers remote work and may incur costs or large outputs.",
            "Always review request bodies and caps before running downloads.",
        ],
        "create_response": data,
        **_no_snapshot_fields(action="ads.reports.create"),
    }
    ctx["audit"].write("ads.reports.create", {"ad_account_id": ad_account_id})
    ctx["out"].emit(out)
    return 0


def cmd_ads_reports_get(args: Any, ctx: dict[str, Any]) -> int:
    api = api_from_ctx(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    token = str(args.token).strip()

    data = get_report_job(api, ad_account_id=ad_account_id, token=token)
    status = extract_report_status(data)
    url = extract_report_url(data)

    out = {
        "ok": True,
        "ad_account_id": ad_account_id,
        "token": token,
        "report_status": status,
        "download_url": url,
        "report": data,
    }
    ctx["audit"].write("ads.reports.get", {"ad_account_id": ad_account_id})
    ctx["out"].emit(out)
    return 0


def cmd_ads_reports_run(args: Any, ctx: dict[str, Any]) -> int:
    _require_apply_yes_ack_volume(ctx, action="ads.reports.run", label="report job run")
    api = api_from_ctx(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    body = read_json_file(str(args.body_file))
    out_dir = ensure_dir(str(args.out_dir))

    max_poll_attempts = int(getattr(args, "max_poll_attempts", 60))
    max_poll_seconds = float(getattr(args, "max_poll_seconds", 600.0))
    poll_interval_s = float(getattr(args, "poll_interval_s", 10.0))
    max_download_bytes = int(getattr(args, "max_download_bytes", 100 * 1024 * 1024))

    created = create_report_job(api, ad_account_id=ad_account_id, request_body=body)
    token = extract_report_token(created)
    if not token:
        raise RuntimeError("Report create response missing token")

    def _get(tok: str) -> dict[str, Any]:
        return get_report_job(api, ad_account_id=ad_account_id, token=tok)

    final = poll_report_status(
        _get,
        token=token,
        max_attempts=max_poll_attempts,
        max_seconds=max_poll_seconds,
        poll_interval_s=poll_interval_s,
    )

    status = extract_report_status(final) or "UNKNOWN"
    download_url = extract_report_url(final)
    receipt_dir = Path(out_dir) / "receipts"
    receipt_path = str((receipt_dir / f"report-{_sanitize_token(token)}.json").resolve())

    receipt: dict[str, Any] = {
        "ok": status == "FINISHED",
        "ad_account_id": ad_account_id,
        "token": token,
        "report_status": status,
        "download_url": download_url,
        "download_path": None,
        "download": None,
        **_no_snapshot_fields(action="ads.reports.run"),
    }

    rc = 0
    if status != "FINISHED":
        rc = 1
    elif not download_url:
        receipt["ok"] = False
        receipt["error"] = "Report finished but response did not include a download URL"
        rc = 1
    else:
        fmt_hint = format_hint_from_url(download_url)
        filename = safe_filename_for_report(token, fmt_hint)
        download_path = str((Path(out_dir) / filename).resolve())
        receipt["download_path"] = download_path
        try:
            dl = download_report(
                download_url,
                http=ctx["http"],
                dest_path=download_path,
                max_bytes=max_download_bytes,
            )
            receipt["download"] = dl
        except Exception as e:  # noqa: BLE001
            receipt["ok"] = False
            receipt["error"] = str(e)
            receipt["error_type"] = type(e).__name__
            rc = 1

    write_json_file(receipt_path, receipt)

    out = {
        "ok": bool(receipt.get("ok")),
        "receipt_path": receipt_path,
        "token": token,
        "report_status": status,
        "download_path": receipt.get("download_path"),
        **_no_snapshot_fields(action="ads.reports.run"),
    }
    ctx["audit"].write(
        "ads.reports.run",
        {"ad_account_id": ad_account_id, "token": token, "status": status, "ok": bool(receipt.get("ok"))},
    )
    ctx["out"].emit(out)
    return rc


# Back-compat internal names (kept stable for tests/consumers inside this repo).
_api = api_from_ctx
_format_hint_from_url = format_hint_from_url

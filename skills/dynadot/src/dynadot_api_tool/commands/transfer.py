from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Type

from ..config import load_config_file_only
from ..domains_list import chunk
from ..dynadot_api import DynadotApi
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ._write_safety import (
    build_before_state_refusal_verification_plan,
    build_no_recovery_contract,
    emit_before_state_refusal,
    ensure_before_state_refusal_plan,
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk_bytes in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk_bytes)
    return h.hexdigest()


def _extract_list_domain_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("MainDomains", "Domains", "DomainInfoList", "DomainInfo", "DomainList"):
        v = payload.get(key)
        if isinstance(v, list):
            return [x for x in v if isinstance(x, dict)]
        if isinstance(v, dict):
            for inner_key in ("Domains", "MainDomains", "DomainInfo", "DomainInfoList", "DomainList"):
                inner = v.get(inner_key)
                if isinstance(inner, list):
                    return [x for x in inner if isinstance(x, dict)]
    return []


def _parse_domain_names_from_list_domain_records(records: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for row in records:
        name = row.get("Name")
        if name is None:
            continue
        d = str(name).strip().lower().rstrip(".")
        if not d:
            continue
        if d not in out:
            out.append(d)
    return out


def _domain_info_from_response(payload: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("DomainInfo", "Domain", "domain", "domainInfo"):
        v = payload.get(key)
        if isinstance(v, dict):
            return v
    return None


def _parse_push_request_domains(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip().lower().rstrip(".") for x in value if str(x).strip()]
    s = str(value).strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    out: list[str] = []
    s = s.replace(";", ",")
    for part in s.split(","):
        d = part.strip().strip('"').strip("'").strip().lower().rstrip(".")
        if d and d not in out:
            out.append(d)
    return out


def _is_sender_account_locked_error(msg: str) -> bool:
    s = str(msg or "").lower()
    return "unlock your account" in s


def _is_no_push_order_found_error(msg: str) -> bool:
    s = str(msg or "").lower()
    return "no push order found" in s


def _push_domains_one_by_one(
    *,
    api: DynadotApi,
    domains: list[str],
    to_username: str,
    push_unlock: bool,
    sleep_between_calls_s: float,
    chunk_id: int,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for i, d in enumerate(domains, start=1):
        payload = {"domain": d, "receiver_push_username": to_username}
        if push_unlock:
            payload["unlock_domain_for_push"] = "1"
        try:
            res = api.call(command="push", params=payload)
            results.append(
                {
                    "chunk": chunk_id,
                    "domains": [d],
                    "ok": True,
                    "status": res.status,
                    "response": res.response,
                    "fallback": "per_domain",
                    "attempt": i,
                }
            )
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            row: dict[str, Any] = {
                "chunk": chunk_id,
                "domains": [d],
                "ok": False,
                "error": msg,
                "fallback": "per_domain",
                "attempt": i,
            }
            if _is_sender_account_locked_error(msg):
                row["blocked_reason"] = "sender_account_locked"
                row["hint"] = "Unlock the sender Dynadot account in the Dynadot control panel (Account Lock), then re-run apply (unlock lasts about 1 hour)."
                results.append(row)
                break
            results.append(row)
        if sleep_between_calls_s > 0 and i < len(domains):
            time.sleep(sleep_between_calls_s)
    return results


def _accept_domains_one_by_one(
    *,
    api: DynadotApi,
    domains: list[str],
    sleep_between_calls_s: float,
    chunk_id: int,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for i, d in enumerate(domains, start=1):
        try:
            res = api.call(command="set_domain_push_request", params={"domains": d, "action": "accept"})
            results.append(
                {
                    "chunk": chunk_id,
                    "domains": [d],
                    "ok": True,
                    "status": res.status,
                    "response": res.response,
                    "fallback": "per_domain",
                    "attempt": i,
                }
            )
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            if _is_no_push_order_found_error(msg):
                results.append(
                    {
                        "chunk": chunk_id,
                        "domains": [d],
                        "ok": True,
                        "status": "no_push_order_found",
                        "warning": msg,
                        "fallback": "per_domain",
                        "attempt": i,
                    }
                )
            else:
                results.append(
                    {
                        "chunk": chunk_id,
                        "domains": [d],
                        "ok": False,
                        "error": msg,
                        "fallback": "per_domain",
                        "attempt": i,
                    }
                )
        if sleep_between_calls_s > 0 and i < len(domains):
            time.sleep(sleep_between_calls_s)
    return results


def _api_from_cfg(cfg: Any, *, timeout_s: float, verbose: bool) -> DynadotApi:
    if not getattr(cfg, "api_key", None):
        raise ValidationError("Missing DYNADOT_API_KEY")
    http = HttpClient(timeout_s=float(timeout_s), verbose=bool(verbose), user_agent="dynadot-api-tool")
    return DynadotApi(base_url=str(cfg.base_url), api_key=str(cfg.api_key), http=http)


def _receiver_cfg_from_args(args: Any) -> Any:
    receiver_env_file = str(getattr(args, "receiver_env_file", "") or "").strip()
    if not receiver_env_file:
        raise ValidationError("Missing --receiver-env-file")
    return load_config_file_only(receiver_env_file)


def _normalize_name_servers(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in items:
        ns = str(raw or "").strip().lower().rstrip(".")
        if not ns:
            continue
        if ns in seen:
            continue
        seen.add(ns)
        out.append(ns)
    return sorted(out)


def _parse_name_servers_from_get_ns_response(payload: dict[str, Any]) -> list[str]:
    ns_content = payload.get("NsContent")
    if not isinstance(ns_content, dict):
        return []
    hosts: list[str] = []
    for i in range(0, 13):
        v = ns_content.get(f"Host{i}")
        if v is None:
            continue
        s = str(v).strip()
        if s:
            hosts.append(s)
    return _normalize_name_servers(hosts)


_NAMESERVER_HOST_RE = re.compile(
    r"^(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$"
)

_DOMAIN_TOKEN_RE = re.compile(r"([a-z0-9-]{1,63}(?:\.[a-z0-9-]{1,63})+)", re.IGNORECASE)


def _parse_epoch_ms(raw: Any) -> int | None:
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def _utc_now_ms() -> int:
    return int(time.time() * 1000)


def _is_expired_epoch_ms(exp_ms: int | None, *, now_ms: int) -> bool:
    if exp_ms is None:
        return False
    return exp_ms <= now_ms


def _extract_domains_from_error_message(msg: str, *, candidates: list[str]) -> list[str]:
    if not msg:
        return []
    cand = set([str(d).strip().lower().rstrip(".") for d in candidates if str(d).strip()])
    found: set[str] = set()
    for m in _DOMAIN_TOKEN_RE.finditer(str(msg)):
        d = str(m.group(1) or "").strip().lower().rstrip(".")
        if d in cand:
            found.add(d)
    return sorted(found)


def _parse_desired_name_servers(args: Any) -> list[str]:
    desired = getattr(args, "desired_ns", None)
    desired_file = str(getattr(args, "desired_ns_file", "") or "").strip() or None
    items_raw: list[str] = []
    if desired:
        items_raw.extend([str(x) for x in desired])
    if desired_file:
        p = Path(desired_file)
        if not p.exists():
            raise ValidationError(f"Desired name servers file not found: {p}")
        for raw in p.read_text(encoding="utf-8").splitlines():
            s = raw.strip()
            if not s or s.startswith("#"):
                continue
            items_raw.append(s)

    seen: set[str] = set()
    out: list[str] = []
    for raw in items_raw:
        ns = str(raw or "").strip().lower().rstrip(".")
        if not ns:
            continue
        if not _NAMESERVER_HOST_RE.match(ns):
            raise ValidationError(f"Invalid name server hostname: {ns}")
        if ns in seen:
            continue
        seen.add(ns)
        out.append(ns)
    out = sorted(out)
    if not out:
        raise ValidationError("No desired name servers provided (use --desired-ns or --desired-ns-file)")
    if len(out) > 13:
        raise ValidationError("Dynadot supports up to 13 name servers (ns0-ns12)")
    return out


def _status_is_active(status: Any) -> bool:
    return str(status or "").strip().lower() == "active"


def _parse_epoch_ms(raw: Any) -> int | None:
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def _utc_now_ms() -> int:
    return int(time.time() * 1000)


def _is_expired_epoch_ms(exp_ms: int | None, *, now_ms: int) -> bool:
    if exp_ms is None:
        return False
    # Dynadot uses epoch milliseconds.
    return exp_ms <= now_ms


def _extract_domains_from_error_message(msg: str, *, candidates: list[str]) -> list[str]:
    if not msg:
        return []
    cand = set([str(d).strip().lower().rstrip(".") for d in candidates if str(d).strip()])
    found: set[str] = set()
    for m in _DOMAIN_TOKEN_RE.finditer(str(msg)):
        d = str(m.group(1) or "").strip().lower().rstrip(".")
        if d in cand:
            found.add(d)
    return sorted(found)


def _confirm_receiver_domains_present_via_domain_info(
    *,
    api: DynadotApi,
    domains: list[str],
    retries: int,
    sleep_between_retries_s: float,
    sleep_between_calls_s: float,
) -> tuple[set[str], set[str], list[dict[str, Any]]]:
    present: set[str] = set()
    missing: set[str] = set([d for d in domains if d])
    errors: list[dict[str, Any]] = []

    if not domains:
        return present, missing, errors

    for attempt in range(0, retries + 1):
        still_missing = sorted([d for d in missing if d and d not in present])
        if not still_missing:
            break

        for idx, d in enumerate(still_missing):
            if idx and sleep_between_calls_s > 0:
                time.sleep(sleep_between_calls_s)
            try:
                res = api.call(command="domain_info", params={"domain": d})
                di = _domain_info_from_response(res.response)
                if isinstance(di, dict) and str(di.get("Name") or di.get("DomainName") or "").strip():
                    present.add(d)
                    missing.discard(d)
                else:
                    # Unexpected shape; treat as missing.
                    missing.add(d)
            except Exception as e:  # noqa: BLE001
                errors.append({"domain": d, "attempt": attempt + 1, "error": str(e)})
                missing.add(d)

        if attempt < retries and sleep_between_retries_s > 0:
            time.sleep(sleep_between_retries_s)

    return present, missing, errors


def _validate_plan_for_apply(plan: dict[str, Any], *, baseline: dict[str, Any], ctx: dict[str, Any]) -> None:
    if str(plan.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    b = plan.get("baseline")
    if not isinstance(b, dict):
        raise ValidationError("Plan missing baseline object")
    for k, v in baseline.items():
        if str(b.get(k) or "") != str(v or ""):
            raise SafetyError(f"Refused: plan baseline mismatch for {k}")


def _parse_resume_receipt(path: str, *, ctx: dict[str, Any]) -> tuple[str, set[str]]:
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("Resume receipt must be a JSON object")
    if str(obj.get("tool") or "") != str(ctx.get("tool") or "dynadot-api-tool"):
        # Soft check: different tool name means it's likely the wrong file.
        raise ValidationError("Resume receipt tool mismatch")
    sel = obj.get("selector")
    if not isinstance(sel, dict) or str(sel.get("kind") or "") != "transfer.run":
        raise ValidationError("Resume receipt selector kind mismatch (expected transfer.run)")
    summary = obj.get("summary") if isinstance(obj.get("summary"), dict) else {}
    done_any = (summary or {}).get("done_domains")
    failed_any = (summary or {}).get("failed_domains")
    skip: set[str] = set()
    for items in (done_any, failed_any):
        if isinstance(items, list):
            for item in items:
                d = str(item or "").strip().lower().rstrip(".")
                if d:
                    skip.add(d)
    return _sha256_file(path), skip


@dataclass(frozen=True)
class _DomainStatusRow:
    domain: str
    ok: bool
    status: str | None
    expiration_ms: int | None
    error: str | None


def _sender_export_domains(
    *,
    api: DynadotApi,
    page_size: int | None,
    max_pages: int,
    sleep_between_pages_s: float,
) -> tuple[list[str], dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    combined: list[str] = []
    stopped_reason = "empty_page"
    for offset in range(0, max_pages):
        page_index = 1 + offset
        params: dict[str, Any] = {"page_index": page_index}
        if page_size is not None:
            params["count_per_page"] = page_size
        res = api.call(command="list_domain", params=params)
        records = _extract_list_domain_records(res.response)
        names = _parse_domain_names_from_list_domain_records(records)
        pages.append({"page_index": page_index, "count": len(names)})
        combined.extend(names)
        if len(names) == 0:
            stopped_reason = "empty_page"
            break
        if offset + 1 >= max_pages:
            stopped_reason = "max_pages"
            break
        if sleep_between_pages_s > 0:
            time.sleep(sleep_between_pages_s)
    export = {
        "command": "list_domain",
        "paging": {"max_pages": max_pages, "attempted_pages": len(pages), "stopped_reason": stopped_reason},
        "count": len(combined),
        "domains": combined,
        "pages": pages,
    }
    return combined, export


def _extract_status_from_list_domain_row(row: dict[str, Any]) -> str | None:
    v = row.get("Status")
    if v is None:
        return None
    s = str(v).strip().lower()
    return s or None


def _sender_export_domain_statuses(
    *,
    api: DynadotApi,
    domains: list[str],
    sleep_s: float,
) -> tuple[list[_DomainStatusRow], dict[str, int]]:
    rows: list[_DomainStatusRow] = []
    counts: dict[str, int] = {}
    for idx, d in enumerate(domains):
        if idx and sleep_s > 0:
            time.sleep(sleep_s)
        try:
            res = api.call(command="domain_info", params={"domain": d})
            di = _domain_info_from_response(res.response) or {}
            status = str(di.get("Status") or "").strip()
            status_norm = status.lower() if status else "unknown"
            counts[status_norm] = counts.get(status_norm, 0) + 1
            exp_ms = _parse_epoch_ms(di.get("Expiration"))
            rows.append(_DomainStatusRow(domain=d, ok=True, status=status_norm, expiration_ms=exp_ms, error=None))
        except Exception as e:  # noqa: BLE001
            counts["error"] = counts.get("error", 0) + 1
            rows.append(_DomainStatusRow(domain=d, ok=False, status=None, expiration_ms=None, error=str(e)))
    return rows, counts


def _select_active_domains_from_sender(
    *,
    api: DynadotApi,
    page_size: int | None,
    max_pages: int,
    sleep_between_pages_s: float,
    max_active_domains: int | None,
    skip_domains: set[str],
    status_sleep_s_fallback: float,
) -> tuple[list[str], dict[str, int], dict[str, Any]]:
    """
    Select active domains using `list_domain` pages.

    Dynadot often includes a `Status` field in each list_domain row. When present, we use it
    to avoid making one `domain_info` call per domain (too slow for 1,000+).

    If `Status` is missing, we fall back to `domain_info` for those rows only.
    """
    active: list[str] = []
    status_counts: dict[str, int] = {}
    pages: list[dict[str, Any]] = []
    stopped_reason = "empty_page"
    total_domains_seen = 0
    now_ms = _utc_now_ms()

    for offset in range(0, max_pages):
        page_index = 1 + offset
        params: dict[str, Any] = {"page_index": page_index}
        if page_size is not None:
            params["count_per_page"] = page_size
        res = api.call(command="list_domain", params=params)
        records = _extract_list_domain_records(res.response)
        pages.append({"page_index": page_index, "count": len(records)})
        if len(records) == 0:
            stopped_reason = "empty_page"
            break

        for row in records:
            name = row.get("Name")
            if name is None:
                continue
            d = str(name).strip().lower().rstrip(".")
            if not d:
                continue

            total_domains_seen += 1
            status = _extract_status_from_list_domain_row(row)
            exp_ms = _parse_epoch_ms(row.get("Expiration"))
            used_fallback = False
            if status is None:
                # Fallback: per-domain status call only when list_domain does not include it.
                try:
                    di_res = api.call(command="domain_info", params={"domain": d})
                    di = _domain_info_from_response(di_res.response) or {}
                    status = str(di.get("Status") or "").strip().lower() or "unknown"
                    exp_ms = _parse_epoch_ms(di.get("Expiration")) if exp_ms is None else exp_ms
                except Exception:
                    status = "error"
                used_fallback = True

            status_counts[status] = status_counts.get(status, 0) + 1
            expired = _is_expired_epoch_ms(exp_ms, now_ms=now_ms)
            if expired:
                status_counts["expired_by_date"] = status_counts.get("expired_by_date", 0) + 1
            if status == "active" and not expired and d not in active and d not in skip_domains:
                active.append(d)
                if max_active_domains is not None and len(active) >= max_active_domains:
                    stopped_reason = "max_active_domains_reached"
                    break

            if status_sleep_s_fallback > 0 and used_fallback:
                time.sleep(status_sleep_s_fallback)

        if stopped_reason == "max_active_domains_reached":
            break
        if offset + 1 >= max_pages:
            stopped_reason = "max_pages"
            break
        if sleep_between_pages_s > 0:
            time.sleep(sleep_between_pages_s)

    export = {
        "command": "list_domain",
        "paging": {"max_pages": max_pages, "attempted_pages": len(pages), "stopped_reason": stopped_reason},
        "domains_seen": total_domains_seen,
        "active_selected_count": len(active),
        "status_counts": status_counts,
        "pages": pages,
    }
    return active, status_counts, export


def _sender_get_domain_statuses(
    *,
    api: DynadotApi,
    domains: list[str],
    sleep_s: float,
) -> list[_DomainStatusRow]:
    rows: list[_DomainStatusRow] = []
    for idx, d in enumerate(domains):
        if idx and sleep_s > 0:
            time.sleep(sleep_s)
        try:
            res = api.call(command="domain_info", params={"domain": d})
            di = _domain_info_from_response(res.response) or {}
            status = str(di.get("Status") or "").strip()
            status_norm = status.lower() if status else "unknown"
            exp_ms = _parse_epoch_ms(di.get("Expiration"))
            rows.append(_DomainStatusRow(domain=d, ok=True, status=status_norm, expiration_ms=exp_ms, error=None))
        except Exception as e:  # noqa: BLE001
            rows.append(_DomainStatusRow(domain=d, ok=False, status=None, expiration_ms=None, error=str(e)))
    return rows


def cmd_transfer_run(args: Any, ctx: dict[str, Any]) -> int:
    receiver_env_file = str(getattr(args, "receiver_env_file", "") or "").strip()
    to_username = str(getattr(args, "to_username", "") or "").strip()
    if not to_username:
        raise ValidationError("Missing --to-push-username / --to-username")

    desired = _parse_desired_name_servers(args)

    # Sender config is the main `--env-file` for this run.
    sender_cfg = ctx["cfg"]
    receiver_cfg = _receiver_cfg_from_args(args)

    if str(sender_cfg.base_url) == str(receiver_cfg.base_url) and str(getattr(sender_cfg, "api_key", "") or "") == str(
        getattr(receiver_cfg, "api_key", "") or ""
    ):
        raise SafetyError("Refused: sender and receiver appear to be the same Dynadot account/config")

    # Pacing/limits (defaults are intentionally conservative but simple).
    sender_list_page_size_raw = getattr(args, "sender_list_page_size", None)
    sender_list_page_size = int(sender_list_page_size_raw) if sender_list_page_size_raw is not None else None
    if sender_list_page_size is not None and sender_list_page_size < 1:
        raise ValidationError("--sender-list-page-size must be >= 1")
    sender_list_max_pages = int(getattr(args, "sender_list_max_pages", 200) or 200)
    if sender_list_max_pages < 1:
        raise ValidationError("--sender-list-max-pages must be >= 1")
    sender_list_sleep_s = float(getattr(args, "sender_list_sleep_s", 0.0) or 0.0)
    if sender_list_sleep_s < 0:
        raise ValidationError("--sender-list-sleep-s must be >= 0")

    sender_status_sleep_s = float(getattr(args, "sender_status_sleep_s", 0.0) or 0.0)
    if sender_status_sleep_s < 0:
        raise ValidationError("--sender-status-sleep-s must be >= 0")

    max_domains_raw = getattr(args, "max_domains", None)
    max_domains = int(max_domains_raw) if max_domains_raw is not None else None
    if max_domains is not None and max_domains < 1:
        raise ValidationError("--max-domains must be >= 1")

    push_unlock = not bool(getattr(args, "no_unlock", False))
    push_sleep_between_batches_s = float(getattr(args, "push_sleep_between_batches_s", 0.0) or 0.0)
    if push_sleep_between_batches_s < 0:
        raise ValidationError("--push-sleep-between-batches-s must be >= 0")
    push_max_batches_raw = getattr(args, "push_max_batches", None)
    push_max_batches = int(push_max_batches_raw) if push_max_batches_raw is not None else None
    if push_max_batches is not None and push_max_batches < 1:
        raise ValidationError("--push-max-batches must be >= 1")

    accept_sleep_between_batches_s = float(getattr(args, "accept_sleep_between_batches_s", 0.0) or 0.0)
    if accept_sleep_between_batches_s < 0:
        raise ValidationError("--accept-sleep-between-batches-s must be >= 0")
    accept_max_batches_raw = getattr(args, "accept_max_batches", None)
    accept_max_batches = int(accept_max_batches_raw) if accept_max_batches_raw is not None else None
    if accept_max_batches is not None and accept_max_batches < 1:
        raise ValidationError("--accept-max-batches must be >= 1")

    sleep_after_push_s = float(getattr(args, "sleep_after_push_s", 0.0) or 0.0)
    if sleep_after_push_s < 0:
        raise ValidationError("--sleep-after-push-s must be >= 0")
    sleep_after_accept_s = float(getattr(args, "sleep_after_accept_s", 0.0) or 0.0)
    if sleep_after_accept_s < 0:
        raise ValidationError("--sleep-after-accept-s must be >= 0")

    presence_retries = int(getattr(args, "presence_retries", 0) or 0)
    if presence_retries < 0:
        raise ValidationError("--presence-retries must be >= 0")
    presence_sleep_s = float(getattr(args, "presence_sleep_s", 0.0) or 0.0)
    if presence_sleep_s < 0:
        raise ValidationError("--presence-sleep-s must be >= 0")
    presence_domain_info_sleep_s = float(getattr(args, "presence_domain_info_sleep_s", 0.0) or 0.0)
    if presence_domain_info_sleep_s < 0:
        raise ValidationError("--presence-domain-info-sleep-s must be >= 0")

    ns_sleep_between_batches_s = float(getattr(args, "ns_sleep_between_batches_s", 0.0) or 0.0)
    if ns_sleep_between_batches_s < 0:
        raise ValidationError("--ns-sleep-between-batches-s must be >= 0")
    ns_sleep_between_verifications_s = float(getattr(args, "ns_sleep_between_verifications_s", 0.0) or 0.0)
    if ns_sleep_between_verifications_s < 0:
        raise ValidationError("--ns-sleep-between-verifications-s must be >= 0")
    ns_max_batches_raw = getattr(args, "ns_max_batches", None)
    ns_max_batches = int(ns_max_batches_raw) if ns_max_batches_raw is not None else None
    if ns_max_batches is not None and ns_max_batches < 1:
        raise ValidationError("--ns-max-batches must be >= 1")
    continue_on_error = bool(getattr(args, "continue_on_error", False))

    require_available_name_servers = bool(getattr(args, "require_available_name_servers", False))
    skip_availability_check = bool(getattr(args, "skip_availability_check", False))
    availability_check_mode = "skip" if skip_availability_check else ("require" if require_available_name_servers else "warn")

    verification_mode = str(getattr(args, "verification_mode", "full") or "full").strip().lower()
    if verification_mode not in ("full", "fast"):
        raise ValidationError("--verification-mode must be one of: full, fast")
    fast_presence_sample_size_raw = getattr(args, "fast_presence_sample_size", None)
    fast_presence_sample_size = int(fast_presence_sample_size_raw) if fast_presence_sample_size_raw is not None else 10
    if fast_presence_sample_size < 0:
        raise ValidationError("--fast-presence-sample-size must be >= 0")

    resume_from_receipt = str(getattr(args, "resume_from_receipt", "") or "").strip() or None
    resume_receipt_sha256 = ""
    already_done: set[str] = set()
    if resume_from_receipt:
        resume_receipt_sha256, already_done = _parse_resume_receipt(resume_from_receipt, ctx=ctx)

    plan_in = ctx.get("plan_in")
    if bool(ctx.get("apply")) and not plan_in:
        recovery = build_no_recovery_contract(
            notes="Transfer run coordinates push, accept, and name-server verification, but this CLI does not offer a built-in rollback or restore path for the combined workflow."
        )
        plan = {
            "tool": ctx.get("tool") or "dynadot-api-tool",
            "version": ctx.get("tool_version") or None,
            "generated_at_utc": _utc_now(),
            "env_fingerprint": str(sender_cfg.base_url),
            "command": ctx.get("command_str") or None,
            "selector": {"kind": "transfer.run", "value": to_username},
            "risk_level": "high",
            "risk_reasons": ["domain-transfer", "bulk"],
            "preconditions": [
                "env_fingerprint (sender) must match",
                "receiver env_fingerprint must match",
                "receiver push username must be correct",
                "apply must use a reviewed --plan-in file",
            ],
            "baseline": {
                "receiver_env_fingerprint": str(receiver_cfg.base_url),
                "to_username": to_username,
                "desired_name_servers_comma": ",".join(desired),
            },
            "preview": {"to_push_username": to_username, "desired_name_servers": desired},
            "proposed_changes": [],
            "verification_plan": build_before_state_refusal_verification_plan(),
            "rollback": {"supported": False, "notes": "Domain pushes and accept actions are not safely auto-reversible."},
            "recovery": recovery,
        }
        ensure_before_state_refusal_plan(
            plan,
            selector_kind="transfer.run",
            selector_value=to_username,
            notes="Transfer run has no reliable combined before-state snapshot here; apply requires explicit no-snapshot approval.",
        )
        auto_plan_path = None
        try:
            ad = ctx.get("artifacts_dir")
            if ad:
                auto_plan_path = write_json_file(str(ad / "plan.json"), plan)  # type: ignore[operator]
        except Exception:
            auto_plan_path = None
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": ["Refused: transfer run apply requires a reviewed plan file (--plan-in). Run the dry-run first."],
            "refusal_type": "SafetyError",
            "plan": plan,
            "plan_out": auto_plan_path,
        }
        ctx["audit"].write("transfer.run.refused", {"reason": "missing-plan-in", "plan_out": auto_plan_path})
        ctx["out"].emit(out)
        return 0

    # APIs (allow injection for tests).
    sender_api = ctx.get("api_sender") or _api_from_cfg(sender_cfg, timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx["verbose"]))
    receiver_api = ctx.get("api_receiver") or _api_from_cfg(receiver_cfg, timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx["verbose"]))

    # Build or load plan
    if plan_in:
        plan_obj = read_json_file(plan_in)
        if not isinstance(plan_obj, dict):
            raise ValidationError("Plan file must be a JSON object")
        plan = plan_obj
        ensure_before_state_refusal_plan(
            plan,
            selector_kind="transfer.run",
            selector_value=to_username,
            notes="Transfer run has no reliable combined before-state snapshot here; apply requires explicit no-snapshot approval.",
        )
    else:
        active_domains, status_counts, sender_domains_export = _select_active_domains_from_sender(
            api=sender_api,
            page_size=sender_list_page_size,
            max_pages=sender_list_max_pages,
            sleep_between_pages_s=sender_list_sleep_s,
            max_active_domains=max_domains,
            skip_domains=already_done,
            status_sleep_s_fallback=sender_status_sleep_s,
        )

        # Receiver reads for preview.
        receiver_push = receiver_api.call(command="get_domain_push_request")
        receiver_pending = set(_parse_push_request_domains(receiver_push.response.get("pushDomainName")))

        receiver_list, receiver_list_export = _sender_export_domains(
            api=receiver_api,
            page_size=None,
            max_pages=sender_list_max_pages,
            sleep_between_pages_s=0.0,
        )
        receiver_domains_set = set(receiver_list)

        selected = active_domains
        already_in_receiver = sorted([d for d in selected if d in receiver_domains_set])
        pending_on_receiver = sorted([d for d in selected if d in receiver_pending])
        need_push = sorted([d for d in selected if d not in receiver_domains_set and d not in receiver_pending])

        preview = {
            "sender": {
                "status_counts": status_counts,
                "active_selected_count": len(selected),
                "skipped_already_done_count": len(already_done),
            },
            "receiver": {
                "pending_push_requests_count": len(receiver_pending),
                "already_in_receiver_count": len(already_in_receiver),
                "pending_matching_count": len(pending_on_receiver),
            },
            "plan": {
                "to_push_username": to_username,
                "desired_name_servers": desired,
                "need_push_count": len(need_push),
            },
        }

        baseline = {
            "receiver_env_fingerprint": str(receiver_cfg.base_url),
            "to_username": to_username,
            "desired_name_servers_comma": ",".join(desired),
            "filter_status": "active",
            "sender_list_page_size": "" if sender_list_page_size is None else str(sender_list_page_size),
            "sender_list_max_pages": str(sender_list_max_pages),
            "sender_list_sleep_s": str(sender_list_sleep_s),
            "sender_status_sleep_s": str(sender_status_sleep_s),
            "max_domains": "" if max_domains is None else str(max_domains),
            "push_unlock_domain_for_push": "1" if push_unlock else "0",
            "push_sleep_between_batches_s": str(push_sleep_between_batches_s),
            "push_max_batches": "" if push_max_batches is None else str(push_max_batches),
            "accept_sleep_between_batches_s": str(accept_sleep_between_batches_s),
            "accept_max_batches": "" if accept_max_batches is None else str(accept_max_batches),
            "sleep_after_push_s": str(sleep_after_push_s),
            "sleep_after_accept_s": str(sleep_after_accept_s),
            "presence_retries": str(presence_retries),
            "presence_sleep_s": str(presence_sleep_s),
            "presence_domain_info_sleep_s": "" if presence_domain_info_sleep_s == 0.0 else str(presence_domain_info_sleep_s),
            "ns_sleep_between_batches_s": str(ns_sleep_between_batches_s),
            "ns_sleep_between_verifications_s": str(ns_sleep_between_verifications_s),
            "ns_max_batches": "" if ns_max_batches is None else str(ns_max_batches),
            "continue_on_error": "1" if continue_on_error else "0",
            "availability_check_mode": "" if availability_check_mode == "warn" else availability_check_mode,
            "resume_receipt_sha256": resume_receipt_sha256,
            "selected_domains_comma": ",".join(selected),
        }

        recovery = build_no_recovery_contract(
            notes="Transfer run coordinates push, accept, and name-server verification, but this CLI does not offer a built-in rollback or restore path for the combined workflow."
        )
        plan = {
            "tool": ctx.get("tool") or "dynadot-api-tool",
            "version": ctx.get("tool_version") or None,
            "generated_at_utc": _utc_now(),
            "env_fingerprint": str(sender_cfg.base_url),
            "command": ctx.get("command_str") or None,
            "selector": {"kind": "transfer.run", "value": to_username},
            "risk_level": "high",
            "risk_reasons": ["domain-transfer", "bulk"] if len(selected) > 1 else ["domain-transfer"],
            "preconditions": [
                "env_fingerprint (sender) must match",
                "receiver env_fingerprint must match",
                "receiver push username must be correct",
                "only domains with status=active are included",
            ],
            "baseline": baseline,
            "preview": preview,
            "proposed_changes": [
                {"domain": d, "push": (d in need_push), "accept": (d not in already_in_receiver), "set_name_servers": True}
                for d in selected
            ],
            "artifacts_preview": {
                "sender_domains_export": sender_domains_export,
                "receiver_domains_export": receiver_list_export,
                "receiver_push_requests_raw": receiver_push.response,
            },
            "post_apply_verification_plan": {
                "type": "read-back",
                "notes": "Verify push requests are cleared, domains appear in receiver list, and name servers match desired values.",
            },
            "verification_plan": build_before_state_refusal_verification_plan(),
            "rollback": {"supported": False, "notes": "Domain pushes and accept actions are not safely auto-reversible."},
            "recovery": recovery,
        }
        ensure_before_state_refusal_plan(
            plan,
            selector_kind="transfer.run",
            selector_value=to_username,
            notes="Transfer run has no reliable combined before-state snapshot here; apply requires explicit no-snapshot approval.",
        )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if plan_out and not bool(ctx.get("apply")) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("transfer.run.plan", {"plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    # Apply: require plan-in and --yes, like other high-risk commands.
    if not plan_in:
        auto_plan_path = None
        try:
            ad = ctx.get("artifacts_dir")
            if ad:
                auto_plan_path = write_json_file(str(ad / "plan.json"), plan)  # type: ignore[operator]
        except Exception:
            auto_plan_path = None
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": ["Refused: transfer run apply requires a reviewed plan file (--plan-in). Run the dry-run first."],
            "refusal_type": "SafetyError",
            "plan": plan,
            "plan_out": auto_plan_path,
        }
        ctx["audit"].write("transfer.run.refused", {"reason": "missing-plan-in", "plan_out": auto_plan_path})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: transfer run requires --apply --yes")

    # Validate baseline drift for apply.
    baseline_expected = dict(plan.get("baseline") or {})
    selected_domains = str(baseline_expected.get("selected_domains_comma") or "").split(",") if baseline_expected else []
    selected_domains = [d.strip().lower().rstrip(".") for d in selected_domains if d.strip()]

    receiver_env_fingerprint_expected = str(baseline_expected.get("receiver_env_fingerprint") or "")
    if receiver_env_fingerprint_expected and str(receiver_cfg.base_url) != receiver_env_fingerprint_expected:
        raise SafetyError("Refused: receiver env_fingerprint does not match plan baseline")

    if str(baseline_expected.get("resume_receipt_sha256") or ""):
        if not resume_from_receipt:
            raise SafetyError("Refused: plan was created with --resume-from-receipt; apply requires the same receipt file")
        actual_resume_sha = _sha256_file(resume_from_receipt)
        if str(baseline_expected.get("resume_receipt_sha256") or "") != str(actual_resume_sha):
            raise SafetyError("Refused: resume receipt changed since plan creation (sha256 mismatch)")

    _validate_plan_for_apply(
        plan,
        baseline={
            "receiver_env_fingerprint": str(receiver_cfg.base_url),
            "to_username": to_username,
            "desired_name_servers_comma": ",".join(desired),
            "filter_status": "active",
            "sender_list_page_size": str(sender_list_page_size) if sender_list_page_size is not None else "",
            "sender_list_max_pages": str(sender_list_max_pages),
            "sender_list_sleep_s": str(sender_list_sleep_s),
            "sender_status_sleep_s": str(sender_status_sleep_s),
            "max_domains": "" if max_domains is None else str(max_domains),
            "push_unlock_domain_for_push": "1" if push_unlock else "0",
            "push_sleep_between_batches_s": str(push_sleep_between_batches_s),
            "push_max_batches": "" if push_max_batches is None else str(push_max_batches),
            "accept_sleep_between_batches_s": str(accept_sleep_between_batches_s),
            "accept_max_batches": "" if accept_max_batches is None else str(accept_max_batches),
            "sleep_after_push_s": str(sleep_after_push_s),
            "sleep_after_accept_s": str(sleep_after_accept_s),
            "presence_retries": str(presence_retries),
            "presence_sleep_s": str(presence_sleep_s),
            "presence_domain_info_sleep_s": "" if presence_domain_info_sleep_s == 0.0 else str(presence_domain_info_sleep_s),
            "ns_sleep_between_batches_s": str(ns_sleep_between_batches_s),
            "ns_sleep_between_verifications_s": str(ns_sleep_between_verifications_s),
            "ns_max_batches": "" if ns_max_batches is None else str(ns_max_batches),
            "continue_on_error": "1" if continue_on_error else "0",
            "availability_check_mode": "" if availability_check_mode == "warn" else availability_check_mode,
            "resume_receipt_sha256": resume_receipt_sha256,
            "selected_domains_comma": ",".join(selected_domains),
        },
        ctx=ctx,
    )
    if not bool(ctx.get("ack_no_snapshot")):
        return emit_before_state_refusal(
            ctx=ctx,
            plan=plan,
            audit_event="transfer.run.refused",
            extra={"summary": {"done": 0, "failed": 0, "remaining": len(selected_domains), "done_domains": [], "failed_domains": [], "remaining_domains": selected_domains}},
        )

    # Receiver current state (before)
    receiver_push_before = receiver_api.call(command="get_domain_push_request")
    receiver_pending_before = set(_parse_push_request_domains(receiver_push_before.response.get("pushDomainName")))

    # IMPORTANT: for large receiver accounts, `list_domain` pagination can miss newly transferred domains.
    # For safe resume, use per-domain receiver `domain_info` to decide what still needs a sender-side push.
    receiver_present_before, _, _ = _confirm_receiver_domains_present_via_domain_info(
        api=receiver_api,
        domains=selected_domains,
        retries=0,
        sleep_between_retries_s=0.0,
        sleep_between_calls_s=presence_domain_info_sleep_s,
    )

    # Apply-time safety check: validate sender-side push eligibility only for domains that still need pushing.
    to_push_candidates = [d for d in selected_domains if d and d not in receiver_present_before and d not in receiver_pending_before]
    now_ms = _utc_now_ms()
    status_errors: list[str] = []
    not_active: list[str] = []
    expired_by_date: list[str] = []
    for r in _sender_get_domain_statuses(api=sender_api, domains=to_push_candidates, sleep_s=sender_status_sleep_s):
        if not r.ok:
            status_errors.append(r.domain)
            continue
        if not _status_is_active(r.status):
            not_active.append(r.domain)
            continue
        if _is_expired_epoch_ms(r.expiration_ms, now_ms=now_ms):
            expired_by_date.append(r.domain)
    ineligible_for_push = sorted(set(not_active + status_errors + expired_by_date))

    if ineligible_for_push and not continue_on_error:
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [
                "Refused: some domains are not eligible to push right now (not status=active, expired by date, or status could not be verified). Re-run with --continue-on-error to skip them."
            ],
            "refusal_type": "SafetyError",
            "ineligible_domains": ineligible_for_push,
            "not_active": not_active,
            "status_errors": status_errors,
            "expired_by_date": expired_by_date,
        }
        ctx["audit"].write("transfer.run.refused", {"reason": "ineligible-domains", "count": len(ineligible_for_push)})
        ctx["out"].emit(out)
        return 0

    eligible_domains = [d for d in selected_domains if d and (continue_on_error or d not in ineligible_for_push)]

    # Apply steps
    errors = 0
    push_results: list[dict[str, Any]] = []
    accept_results: list[dict[str, Any]] = []
    ns_results: list[dict[str, Any]] = []
    push_blocked_reason: str | None = None

    # Additional receiver context for the receipt (best-effort paging snapshot).
    receiver_list_before, _ = _sender_export_domains(api=receiver_api, page_size=None, max_pages=sender_list_max_pages, sleep_between_pages_s=0.0)
    receiver_domains_before = set(receiver_list_before)
    already_in_receiver_before = sorted(receiver_present_before)

    # Push: only domains that are not already present and not already pending.
    to_push = [d for d in to_push_candidates if d and d not in ineligible_for_push]
    push_chunks = chunk(to_push, 50)
    attempted_push_chunks: list[list[str]] = []
    for idx, c in enumerate(push_chunks, start=1):
        if push_max_batches is not None and idx > push_max_batches:
            break
        attempted_push_chunks.append(c)
        payload = {"domain": ";".join(c), "receiver_push_username": to_username}
        if push_unlock:
            payload["unlock_domain_for_push"] = "1"
        try:
            res = sender_api.call(command="push", params=payload)
            push_results.append({"chunk": idx, "domains": c, "ok": True, "status": res.status, "response": res.response})
        except Exception as e:  # noqa: BLE001
            errors += 1
            msg = str(e)
            failed = _extract_domains_from_error_message(msg, candidates=c)
            if _is_sender_account_locked_error(msg):
                push_blocked_reason = "sender_account_locked"
                push_results.append(
                    {
                        "chunk": idx,
                        "domains": c,
                        "ok": False,
                        "error": msg,
                        "blocked_reason": push_blocked_reason,
                        "hint": "Unlock the sender Dynadot account in the Dynadot control panel (Account Lock), then re-run apply (unlock lasts about 1 hour).",
                    }
                )
                break

            # If we can identify a subset, retry the rest one-by-one so one bad domain doesn't block progress.
            if failed and set(failed) != set(c):
                push_results.append(
                    {
                        "chunk": idx,
                        "domains": c,
                        "ok": False,
                        "error": msg,
                        "failed_domains": failed,
                        "fallback": "identified_subset",
                    }
                )
                remaining = [d for d in c if d not in set(failed)]
                if remaining:
                    fallback_results = _push_domains_one_by_one(
                        api=sender_api,
                        domains=remaining,
                        to_username=to_username,
                        push_unlock=push_unlock,
                        sleep_between_calls_s=push_sleep_between_batches_s,
                        chunk_id=idx,
                    )
                    errors += sum(1 for r in fallback_results if r.get("ok") is False)
                    if any(r.get("blocked_reason") == "sender_account_locked" for r in fallback_results):
                        push_blocked_reason = "sender_account_locked"
                        push_results.extend(fallback_results)
                        break
                    push_results.extend(fallback_results)
                continue

            # Otherwise, fall back to per-domain pushes to isolate failures (ex: US nexus setup blocks only .us domains).
            push_results.append({"chunk": idx, "domains": c, "ok": False, "error": msg, "fallback": "unknown_batch_error"})
            fallback_results = _push_domains_one_by_one(
                api=sender_api,
                domains=c,
                to_username=to_username,
                push_unlock=push_unlock,
                sleep_between_calls_s=push_sleep_between_batches_s,
                chunk_id=idx,
            )
            errors += sum(1 for r in fallback_results if r.get("ok") is False)
            if any(r.get("blocked_reason") == "sender_account_locked" for r in fallback_results):
                push_blocked_reason = "sender_account_locked"
                push_results.extend(fallback_results)
                break
            push_results.extend(fallback_results)
            continue
        if push_sleep_between_batches_s > 0 and idx < len(push_chunks) and (push_max_batches is None or idx < push_max_batches):
            time.sleep(push_sleep_between_batches_s)

    if sleep_after_push_s > 0:
        time.sleep(sleep_after_push_s)

    pushed_domains: list[str] = []
    for row in push_results:
        if row.get("ok") is True:
            pushed_domains.extend(list(row.get("domains") or []))
    pushed_domains = sorted(set([d for d in pushed_domains if d]))

    push_failed_domains: list[str] = []
    for row in push_results:
        if row.get("ok") is False:
            if isinstance(row.get("failed_domains"), list) and row.get("failed_domains"):
                push_failed_domains.extend(list(row.get("failed_domains") or []))
            elif row.get("fallback") in ("unknown_batch_error", "identified_subset") and len(list(row.get("domains") or [])) > 1:
                # Informational batch error rows: don't mark the whole chunk as failed, since we retry per-domain.
                continue
            else:
                push_failed_domains.extend(list(row.get("domains") or []))
    push_failed_domains = sorted(set([d for d in push_failed_domains if d]))

    # Accept: accept any matching push requests currently present.
    receiver_push_mid = receiver_api.call(command="get_domain_push_request")
    receiver_pending_mid = set(_parse_push_request_domains(receiver_push_mid.response.get("pushDomainName")))
    to_accept = sorted([d for d in eligible_domains if d in receiver_pending_mid])
    accept_chunks = chunk(to_accept, 50)
    attempted_accept_chunks: list[list[str]] = []
    for idx, c in enumerate(accept_chunks, start=1):
        if accept_max_batches is not None and idx > accept_max_batches:
            break
        attempted_accept_chunks.append(c)
        try:
            res = receiver_api.call(command="set_domain_push_request", params={"domains": ",".join(c), "action": "accept"})
            accept_results.append({"chunk": idx, "domains": c, "ok": True, "status": res.status, "response": res.response})
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            failed = _extract_domains_from_error_message(msg, candidates=c)
            if _is_no_push_order_found_error(msg) and failed:
                # Dynadot can return "No push order found" even if the domain has already left the
                # push-request queue (eventual consistency / partial success). Refresh the queue
                # and only retry domains that are still pending.
                receiver_push_retry = receiver_api.call(command="get_domain_push_request")
                receiver_pending_retry = set(_parse_push_request_domains(receiver_push_retry.response.get("pushDomainName")))
                still_pending = [d for d in c if d in receiver_pending_retry]
                accept_results.append(
                    {
                        "chunk": idx,
                        "domains": c,
                        "ok": True,
                        "status": "no_push_order_found",
                        "warning": msg,
                        "warning_domains": failed,
                        "fallback": "identified_subset",
                    }
                )
                if still_pending:
                    try:
                        res2 = receiver_api.call(
                            command="set_domain_push_request",
                            params={"domains": ",".join(still_pending), "action": "accept"},
                        )
                        accept_results.append(
                            {
                                "chunk": idx,
                                "domains": still_pending,
                                "ok": True,
                                "status": res2.status,
                                "response": res2.response,
                                "fallback": "retry_still_pending",
                            }
                        )
                    except Exception as e2:  # noqa: BLE001
                        msg2 = str(e2)
                        if _is_no_push_order_found_error(msg2):
                            # Same benign failure mode; refresh queue and only retry domains that
                            # are still pending. If none remain, rely on verification.
                            accept_results.append(
                                {
                                    "chunk": idx,
                                    "domains": still_pending,
                                    "ok": True,
                                    "status": "no_push_order_found",
                                    "warning": msg2,
                                    "fallback": "retry_still_pending_warning",
                                }
                            )
                            receiver_push_retry2 = receiver_api.call(command="get_domain_push_request")
                            receiver_pending_retry2 = set(
                                _parse_push_request_domains(receiver_push_retry2.response.get("pushDomainName"))
                            )
                            still_pending2 = [d for d in still_pending if d in receiver_pending_retry2]
                            if still_pending2:
                                fallback_results = _accept_domains_one_by_one(
                                    api=receiver_api,
                                    domains=still_pending2,
                                    sleep_between_calls_s=accept_sleep_between_batches_s,
                                    chunk_id=idx,
                                )
                                errors += sum(1 for r in fallback_results if r.get("ok") is False)
                                accept_results.extend(fallback_results)
                        else:
                            errors += 1
                            accept_results.append(
                                {
                                    "chunk": idx,
                                    "domains": still_pending,
                                    "ok": False,
                                    "error": msg2,
                                    "fallback": "retry_still_pending_failed",
                                }
                            )
                            fallback_results = _accept_domains_one_by_one(
                                api=receiver_api,
                                domains=still_pending,
                                sleep_between_calls_s=accept_sleep_between_batches_s,
                                chunk_id=idx,
                            )
                            errors += sum(1 for r in fallback_results if r.get("ok") is False)
                            accept_results.extend(fallback_results)
                continue

            errors += 1
            if failed and set(failed) != set(c):
                accept_results.append(
                    {
                        "chunk": idx,
                        "domains": c,
                        "ok": False,
                        "error": msg,
                        "failed_domains": failed,
                        "fallback": "identified_subset",
                    }
                )
                remaining = [d for d in c if d not in set(failed)]
                if remaining:
                    fallback_results = _accept_domains_one_by_one(
                        api=receiver_api,
                        domains=remaining,
                        sleep_between_calls_s=accept_sleep_between_batches_s,
                        chunk_id=idx,
                    )
                    errors += sum(1 for r in fallback_results if r.get("ok") is False)
                    accept_results.extend(fallback_results)
                continue
            accept_results.append({"chunk": idx, "domains": c, "ok": False, "error": msg, "fallback": "unknown_batch_error"})
            fallback_results = _accept_domains_one_by_one(
                api=receiver_api,
                domains=c,
                sleep_between_calls_s=accept_sleep_between_batches_s,
                chunk_id=idx,
            )
            errors += sum(1 for r in fallback_results if r.get("ok") is False)
            accept_results.extend(fallback_results)
            continue
        if accept_sleep_between_batches_s > 0 and idx < len(accept_chunks) and (accept_max_batches is None or idx < accept_max_batches):
            time.sleep(accept_sleep_between_batches_s)

    if sleep_after_accept_s > 0:
        time.sleep(sleep_after_accept_s)

    # Verify: push requests cleared for those we attempted to accept.
    receiver_push_after_accept = receiver_api.call(command="get_domain_push_request")
    receiver_pending_after_accept = set(_parse_push_request_domains(receiver_push_after_accept.response.get("pushDomainName")))
    accepted_domains = sorted([d for d in to_accept if d and d not in receiver_pending_after_accept])
    remaining_pending_matching = sorted([d for d in to_accept if d and d in receiver_pending_after_accept])
    accept_failed_domains = remaining_pending_matching

    # Confirm presence in receiver domain list (with optional retries).
    # We only *expect* domains to be present after accept, or if they already existed in the receiver before this run.
    expected_in_receiver = sorted(set(already_in_receiver_before) | set(accepted_domains))
    present_set: set[str] = set()
    missing_set: set[str] = set(expected_in_receiver)
    presence_errors: list[dict[str, Any]] = []
    presence_checked_domains: list[str] | None = None
    if expected_in_receiver:
        if verification_mode == "fast":
            warning_domains: set[str] = set()
            for row in accept_results:
                if row.get("status") != "no_push_order_found":
                    continue
                for items in (row.get("warning_domains"), row.get("domains")):
                    if isinstance(items, list):
                        for item in items:
                            d = str(item or "").strip().lower().rstrip(".")
                            if d:
                                warning_domains.add(d)
            sample_domains = accepted_domains[:fast_presence_sample_size] if fast_presence_sample_size > 0 else []
            presence_checked_domains = sorted(set(already_in_receiver_before) | warning_domains | set(sample_domains))
            _checked_present, checked_missing, presence_errors = _confirm_receiver_domains_present_via_domain_info(
                api=receiver_api,
                domains=presence_checked_domains,
                retries=presence_retries,
                sleep_between_retries_s=presence_sleep_s,
                sleep_between_calls_s=presence_domain_info_sleep_s,
            )
            present_set = set(expected_in_receiver)
            for d in checked_missing:
                present_set.discard(d)
            missing_set = set(checked_missing)
        else:
            present_set, missing_set, presence_errors = _confirm_receiver_domains_present_via_domain_info(
                api=receiver_api,
                domains=expected_in_receiver,
                retries=presence_retries,
                sleep_between_retries_s=presence_sleep_s,
                sleep_between_calls_s=presence_domain_info_sleep_s,
            )

    # Name servers: only for domains that are present.
    domains_for_ns = sorted(present_set) if verification_mode == "full" else []

    availability_check = None
    if availability_check_mode != "skip" and domains_for_ns:
        res = receiver_api.call(command="server_list")
        ns_list = res.response.get("NameServerList")
        available: list[str] = []
        if isinstance(ns_list, dict):
            lst = ns_list.get("List")
            if isinstance(lst, list):
                for item in lst:
                    if isinstance(item, dict) and item.get("ServerName"):
                        available.append(str(item["ServerName"]).strip().lower().rstrip("."))
        missing_ns = sorted(set(desired) - set(available))
        availability_check = {"available_count": len(available), "missing": missing_ns}
        if availability_check_mode == "require" and missing_ns:
            out = {
                "ok": True,
                "dry_run": False,
                "refused": True,
                "reasons": ["Refused: desired name servers are not available in the receiver Dynadot account"],
                "refusal_type": "SafetyError",
                "availability_check": availability_check,
            }
            ctx["audit"].write("transfer.run.refused", {"reason": "missing-ns", "missing": missing_ns})
            ctx["out"].emit(out)
            return 0

    attempted_ns_batches: list[list[str]] = []
    verified: dict[str, bool] = {}
    mismatches: list[dict[str, Any]] = []
    need_change: list[str] = []

    if verification_mode != "full":
        # Fast mode skips the name server read-back verification (and any `set_ns` changes). Domains are
        # considered done once they are expected to be in the receiver and not confirmed missing.
        for d in sorted(present_set):
            verified[d] = True
    else:
        desired_set = set(desired)
        current_ns_by_domain: dict[str, list[str]] = {}
        ns_read_sleep_count = 0
        for d in domains_for_ns:
            try:
                if ns_sleep_between_verifications_s > 0 and ns_read_sleep_count > 0:
                    time.sleep(ns_sleep_between_verifications_s)
                ns_read_sleep_count += 1
                res = receiver_api.call(command="get_ns", params={"domain": d})
                cur = _parse_name_servers_from_get_ns_response(res.response)
                current_ns_by_domain[d] = cur
                if set(cur) != desired_set:
                    need_change.append(d)
            except Exception as e:  # noqa: BLE001
                errors += 1
                ns_results.append({"domain": d, "ok": False, "stage": "get_ns", "error": str(e)})
                if not continue_on_error:
                    break

        # Mark already-correct domains as verified.
        for d in domains_for_ns:
            if d in current_ns_by_domain and set(current_ns_by_domain[d]) == desired_set:
                verified[d] = True

        ns_params: dict[str, Any] = {}
        for idx, ns in enumerate(desired):
            ns_params[f"ns{idx}"] = ns

        batches = chunk(need_change, 100)
        verification_sleep_count = 0
        for idx, batch_domains in enumerate(batches, start=1):
            if ns_max_batches is not None and idx > ns_max_batches:
                break
            attempted_ns_batches.append(batch_domains)
            try:
                res = receiver_api.call(command="set_ns", params=({"domain": ",".join(batch_domains)} | ns_params))
                ns_results.append({"batch": idx, "domains": batch_domains, "ok": True, "status": res.status, "response": res.response})
            except Exception as e:  # noqa: BLE001
                errors += 1
                ns_results.append({"batch": idx, "domains": batch_domains, "ok": False, "error": str(e)})
                if not continue_on_error:
                    break
                continue

            for d in batch_domains:
                try:
                    if ns_sleep_between_verifications_s > 0 and verification_sleep_count > 0:
                        time.sleep(ns_sleep_between_verifications_s)
                    verification_sleep_count += 1
                    after = receiver_api.call(command="get_ns", params={"domain": d})
                    cur = _parse_name_servers_from_get_ns_response(after.response)
                    ok = set(cur) == desired_set
                    verified[d] = ok
                    if not ok:
                        mismatches.append({"domain": d, "current": cur, "desired": desired})
                except Exception as ve:  # noqa: BLE001
                    verified[d] = False
                    errors += 1
                    ns_results.append({"domain": d, "verification_ok": False, "verification_error": str(ve)})
                    if not continue_on_error:
                        break
            if errors and not continue_on_error:
                break
            if ns_sleep_between_batches_s > 0 and idx < len(batches) and (ns_max_batches is None or idx < ns_max_batches):
                time.sleep(ns_sleep_between_batches_s)

    # Summary
    done_domains = sorted([d for d, ok in verified.items() if ok is True])
    missing_expected = sorted([d for d in expected_in_receiver if d and d in missing_set])
    failed_domains = (
        sorted([d for d, ok in verified.items() if ok is False])
        + remaining_pending_matching
        + missing_expected
        + ineligible_for_push
        + push_failed_domains
        + accept_failed_domains
    )
    failed_domains = sorted(set([d for d in failed_domains if d]))
    remaining_domains = sorted(set(eligible_domains) - set(done_domains) - set(failed_domains))

    partial = bool(remaining_domains) or bool(errors) or bool(failed_domains) or bool(remaining_pending_matching)

    ns_applied_domains: set[str] = set()
    for row in ns_results:
        if row.get("ok") is True and isinstance(row.get("domains"), list):
            for d in row.get("domains") or []:
                if isinstance(d, str) and d:
                    ns_applied_domains.add(d)

    changed = bool(pushed_domains or accepted_domains or ns_applied_domains)

    recovery = build_no_recovery_contract(
        notes="Transfer run coordinates push, accept, and name-server verification, but this CLI does not offer a built-in rollback or restore path for the combined workflow."
    )
    receipt = {
        "tool": ctx.get("tool") or "dynadot-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": str(sender_cfg.base_url),
        "receiver_env_fingerprint": str(receiver_cfg.base_url),
        "command": ctx.get("command_str") or None,
        "selector": {"kind": "transfer.run", "value": to_username},
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for this combined Dynadot transfer workflow.",
        },
        "changed": changed,
        "partial": partial,
        "baseline": plan.get("baseline"),
        "steps": {
            "apply_time_status_check": {
                "eligible_count": len(eligible_domains),
                "ineligible_domains": ineligible_for_push,
                "not_active": not_active,
                "status_errors": status_errors,
                "expired_by_date": expired_by_date,
            },
            "receiver_state_before": {
                "pending_push_requests_count": len(receiver_pending_before),
                "receiver_domains_count": len(receiver_domains_before),
            },
            "push": {
                "count": len(to_push),
                "attempted_batches": len(attempted_push_chunks),
                "results": push_results,
                "diff_applied": [{"domain": d, "to_username": to_username} for d in pushed_domains],
                "blocked_reason": push_blocked_reason,
            },
            "accept": {
                "count": len(to_accept),
                "attempted_batches": len(attempted_accept_chunks),
                "results": accept_results,
                "verification": {"remaining_pending_matching": remaining_pending_matching},
                "diff_applied": [{"domain": d, "action": "accept"} for d in accepted_domains],
            },
            "confirm_presence": {
                "present_count": len(present_set),
                "missing": sorted(missing_set),
                "expected": expected_in_receiver,
                "errors": presence_errors,
                **(
                    {"mode": "fast", "checked": presence_checked_domains or []}
                    if verification_mode == "fast"
                    else {}
                ),
            },
            "name_servers": {
                "availability_check": availability_check,
                "present_count": len(domains_for_ns),
                "need_change_count": len(need_change),
                "attempted_batches": len(attempted_ns_batches),
                "verification": {"verified": verified, "mismatches": mismatches},
                "results": ns_results,
                **(
                    {"mode": "fast", "skipped": True, "skipped_reason": "verification-mode-fast"}
                    if verification_mode == "fast"
                    else {}
                ),
            },
        },
        "errors": errors,
        "summary": {"done": len(done_domains), "failed": len(failed_domains), "remaining": len(remaining_domains), "done_domains": done_domains, "failed_domains": failed_domains, "remaining_domains": remaining_domains},
        "backups": recovery["backups"],
        "rollback_plan": recovery["rollback_plan"],
        "recovery": recovery,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None

    out = {
        "ok": errors == 0,
        "dry_run": False,
        "receipt": receipt,
        "receipt_out": receipt_path,
        "partial": partial,
        "summary": receipt["summary"],
    }
    ctx["audit"].write("transfer.run.apply", {"errors": errors, "partial": partial, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 1 if errors else 0


def register_transfer(
    subparsers: Any,  # argparse._SubParsersAction
    *,
    parser_class: Type[Any],  # Type[argparse.ArgumentParser]
) -> None:
    transfer = subparsers.add_parser("transfer", help="Guided end-to-end transfer workflow (safe)")
    transfer_sub = transfer.add_subparsers(dest="transfer_cmd", required=True, parser_class=parser_class)

    run = transfer_sub.add_parser("run", help="Push (sender) → accept (receiver) → verify → fix name servers")
    run.add_argument(
        "--receiver-env-file",
        dest="receiver_env_file",
        required=True,
        help="Path to receiver Dynadot .env file (contains receiver API key; keep it private)",
    )
    run.add_argument(
        "--to-push-username",
        "--to-username",
        dest="to_username",
        required=True,
        help="Receiver Push Username (not their login username)",
    )
    run.add_argument("--desired-ns", action="append", default=None, help="Desired name server hostname (repeatable)")
    run.add_argument("--desired-ns-file", default=None, help="File with desired name servers (one per line)")

    run.add_argument("--sender-list-page-size", type=int, default=None, help="Optional list_domain page size (count_per_page)")
    run.add_argument("--sender-list-max-pages", type=int, default=200, help="Safety cap on sender list_domain pagination")
    run.add_argument("--sender-list-sleep-s", type=float, default=0.0, help="Sleep seconds between list_domain pages (default: 0)")
    run.add_argument("--sender-status-sleep-s", type=float, default=0.0, help="Sleep seconds between domain_info calls (default: 0)")
    run.add_argument("--max-domains", type=int, default=None, help="Safety cap on selected active domains")

    run.add_argument("--no-unlock", action="store_true", help="Do not set unlock_domain_for_push=1 (default is to unlock for push)")
    run.add_argument("--push-sleep-between-batches-s", type=float, default=0.0, help="Sleep seconds between push batches (default: 0)")
    run.add_argument("--push-max-batches", type=int, default=None, help="Limit number of 50-domain push batches attempted (partial completion)")

    run.add_argument("--accept-sleep-between-batches-s", type=float, default=0.0, help="Sleep seconds between accept batches (default: 0)")
    run.add_argument("--accept-max-batches", type=int, default=None, help="Limit number of 50-domain accept batches attempted (partial completion)")

    run.add_argument("--sleep-after-push-s", type=float, default=0.0, help="Sleep seconds after push step before listing push requests (default: 0)")
    run.add_argument("--sleep-after-accept-s", type=float, default=0.0, help="Sleep seconds after accept step before confirming receiver domains (default: 0)")
    run.add_argument("--presence-retries", type=int, default=0, help="Retry count for confirming domains exist in receiver account (default: 0)")
    run.add_argument("--presence-sleep-s", type=float, default=0.0, help="Sleep seconds between presence retries (default: 0)")
    run.add_argument(
        "--presence-domain-info-sleep-s",
        type=float,
        default=0.0,
        help="Sleep seconds between receiver domain_info calls during presence checks (default: 0)",
    )
    run.add_argument(
        "--verification-mode",
        choices=["full", "fast"],
        default="full",
        help=(
            "Verification mode. full = confirm presence for all expected domains + verify/fix name servers. "
            "fast = confirm presence only for warning domains + a small sample and skip name server verification (much faster)."
        ),
    )
    run.add_argument(
        "--fast-presence-sample-size",
        type=int,
        default=10,
        help="In --verification-mode fast, how many accepted domains to spot-check for presence (default: 10; 0 disables sampling).",
    )

    run.add_argument("--ns-sleep-between-batches-s", type=float, default=0.0, help="Sleep seconds between set_ns batches (default: 0)")
    run.add_argument("--ns-sleep-between-verifications-s", type=float, default=0.0, help="Sleep seconds between get_ns verification calls (default: 0)")
    run.add_argument("--ns-max-batches", type=int, default=None, help="Limit number of 100-domain set_ns batches attempted (partial completion)")
    run.add_argument("--continue-on-error", action="store_true", help="Continue on per-domain errors where possible (partial completion)")

    run.add_argument("--skip-availability-check", action="store_true", help="Skip checking desired name servers exist in the receiver account")
    run.add_argument("--require-available-name-servers", action="store_true", help="Refuse if desired name servers are not available in the receiver account")

    run.add_argument(
        "--resume-from-receipt",
        dest="resume_from_receipt",
        default=None,
        help="Resume from a previous transfer receipt (skips already done domains)",
    )

    run.set_defaults(func=cmd_transfer_run, write_capable=True)

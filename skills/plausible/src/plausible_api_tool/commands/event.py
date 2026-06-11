from __future__ import annotations

import re
import time
from urllib.parse import urlparse

from typing import Any

from .. import __version__
from ..plausible import PlausibleClient
from ..output import write_json_file
from ..recovery import build_irreversible_recovery


_PII_PROP_KEYWORDS = (
    "email",
    "e-mail",
    "mail",
    "password",
    "pass",
    "token",
    "secret",
    "auth",
    "authorization",
)


def _looks_like_email(value: str) -> bool:
    v = (value or "").strip()
    if "@" not in v:
        return False
    local, _, domain = v.partition("@")
    return bool(local) and "." in domain and " " not in v


_SENSITIVE_WORD_RE = re.compile(
    r"(^|[^a-z0-9])(email|e-mail|password|token|secret|authorization|bearer|api[_-]?key|auth)([^a-z0-9]|$)",
    flags=re.IGNORECASE,
)


def _detect_pii_text(*, field_name: str, value: str) -> list[str]:
    v = (value or "").strip()
    if not v:
        return []
    reasons: list[str] = []
    if _looks_like_email(v):
        reasons.append(f"Refusing {field_name} (looks like an email address).")
    if "@" in v and "://" in v:
        # URL containing '@' commonly indicates userinfo or an embedded email address.
        reasons.append(f"Refusing {field_name} (contains '@' which may include an email address or credentials).")
    if _SENSITIVE_WORD_RE.search(v):
        reasons.append(f"Refusing {field_name} (contains sensitive keywords).")
    return reasons


def _detect_pii_props(props: dict[str, str]) -> list[str]:
    reasons: list[str] = []
    for k, v in props.items():
        lk = k.lower().strip()
        lv = (v or "").strip()
        if any(word in lk for word in _PII_PROP_KEYWORDS):
            reasons.append(f"Refusing property key '{k}' (looks sensitive/PII).")
            continue
        if _looks_like_email(lv):
            reasons.append(f"Refusing property '{k}' value (looks like an email address).")
    return reasons


def _safe_props_for_output(props: dict[str, str], *, pii_reasons: list[str]) -> dict[str, Any]:
    if pii_reasons:
        return {"redacted": True, "keys": sorted(props.keys())}
    return {"redacted": False, "values": props}


def _validate_url(url: str) -> tuple[bool, str | None, str | None]:
    try:
        p = urlparse(url)
    except Exception:
        return False, None, "URL parse error"
    if p.scheme not in ("http", "https"):
        return False, None, "URL must start with http:// or https://"
    if not p.netloc:
        return False, None, "URL must include a host"
    return True, p.hostname, None


def _verify_event_visible(
    *,
    client: PlausibleClient,
    site_id: str,
    url: str,
    max_wait_s: float,
) -> dict[str, Any]:
    p = urlparse(url)
    path = p.path or "/"
    now = time.time()
    start = now - 10 * 60
    # Use ISO8601 in UTC. Plausible supports date-time ranges for real time.
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(start))
    end_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))

    query = {
        "site_id": site_id,
        "date_range": [start_iso, end_iso],
        "metrics": ["events"],
        "filters": [["is", "event:page", [path]]],
    }

    deadline = time.time() + max(0.0, float(max_wait_s))
    attempts = 0
    last_resp: dict[str, Any] | None = None

    while True:
        attempts += 1
        last_resp = client.stats_query(query)
        # Response shapes vary; look for any numeric count > 0.
        count = None
        try:
            # Common shape: {"results": [{"metrics": [N]}]}
            results = last_resp.get("results")  # type: ignore[assignment]
            if isinstance(results, list) and results and isinstance(results[0], dict):
                metrics = results[0].get("metrics")
                if isinstance(metrics, list) and metrics and isinstance(metrics[0], (int, float)):
                    count = float(metrics[0])
        except Exception:
            count = None

        if count is not None and count > 0:
            return {"ok": True, "attempts": attempts, "query": query, "events_on_path": int(count)}
        if time.time() >= deadline:
            return {"ok": False, "attempts": attempts, "query": query, "last_response": last_resp}
        time.sleep(1.0)


def cmd_event_send(args, ctx) -> int:
    cfg = ctx["cfg"]
    domain = (args.domain or cfg.site_id).strip()
    props = dict(args.prop or [])
    referrer = (getattr(args, "referrer", None) or "").strip() or None
    revenue_currency = (getattr(args, "revenue_currency", None) or "").strip() or None
    revenue_amount = (getattr(args, "revenue_amount", None) or "").strip() or None

    if (revenue_currency is None) != (revenue_amount is None):
        ctx["out"].emit(
            {
                "ok": False,
                "error": "Revenue requires both --revenue-currency and --revenue-amount.",
                "error_type": "ValidationError",
            }
        )
        return 1

    pii_reasons = _detect_pii_props(props)
    url_ok, url_host, url_err = _validate_url(args.url)
    if not url_ok:
        ctx["out"].emit({"ok": False, "error": url_err or "Invalid URL", "error_type": "ValueError"})
        return 1
    if referrer is not None:
        ref_ok, _ref_host, ref_err = _validate_url(referrer)
        if not ref_ok:
            ctx["out"].emit({"ok": False, "error": ref_err or "Invalid referrer URL", "error_type": "ValueError"})
            return 1

    safety_reasons: list[str] = []
    if domain != cfg.site_id and not bool(args.allow_non_default_domain):
        safety_reasons.append(
            "Refusing non-default domain: pass --allow-non-default-domain to use --domain != PLAUSIBLE_SITE_ID."
        )
    if url_host and not (url_host == domain or url_host.endswith(f".{domain}")) and not bool(args.allow_url_host_mismatch):
        safety_reasons.append(
            "Refusing URL host mismatch: pass --allow-url-host-mismatch if URL host does not match the event domain."
        )
    safety_reasons.extend(pii_reasons)
    if referrer is not None:
        safety_reasons.extend(_detect_pii_text(field_name="referrer", value=referrer))
    if revenue_currency is not None:
        safety_reasons.extend(_detect_pii_text(field_name="revenue currency", value=revenue_currency))
    if revenue_amount is not None:
        safety_reasons.extend(_detect_pii_text(field_name="revenue amount", value=revenue_amount))

    safe_props = _safe_props_for_output(props, pii_reasons=pii_reasons)
    safe_referrer: Any | None = None
    if referrer is not None:
        safe_referrer = {"redacted": True} if any(r.lower().startswith("refusing referrer") for r in safety_reasons) else referrer
    safe_revenue: Any | None = None
    if revenue_currency is not None and revenue_amount is not None:
        if any("revenue currency" in r.lower() or "revenue amount" in r.lower() for r in safety_reasons):
            safe_revenue = {"redacted": True}
        else:
            safe_revenue = {"currency": revenue_currency, "amount": revenue_amount}

    env_fingerprint = {"base_url": str(getattr(cfg, "base_url", "")), "site_id": str(getattr(cfg, "site_id", ""))}
    selector = {"domain": domain, "name": args.name, "url": args.url}
    plan: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": env_fingerprint,
        "command": "event send",
        "selector": selector,
        "risk_level": "irreversible",
        "risk_reasons": ["Sends an analytics event; Plausible does not provide a delete/undo API for events"],
        "preconditions": [
            "Reviewed this plan and confirmed the event details are correct",
            "Confirmed the event does not include PII in props",
            "Acknowledged the action is irreversible",
        ],
        "proposed_changes": [
            {
                "action": "plausible.events.send",
                "payload": {
                    "domain": domain,
                    "name": args.name,
                    "url": args.url,
                    **({"referrer": safe_referrer} if safe_referrer is not None else {}),
                    **({"revenue": safe_revenue} if safe_revenue is not None else {}),
                    "props": safe_props,
                    "interactive": bool(args.interactive),
                },
            }
        ],
        "verification_plan": "Optional: poll Stats API v2 for events on the URL path (best-effort, may be delayed).",
        "rollback": {"supported": False, "notes": "Not supported: events cannot be removed once sent."},
        "recovery": build_irreversible_recovery(),
        "before_state": {
            "required": True,
            "supported": False,
            "status": "no_snapshot_available",
            "reason": "Plausible event send creates analytics data that cannot be snapshotted or removed later.",
        },
    }

    plan_path = None
    if ctx.get("plan_out"):
        plan_path = write_json_file(str(ctx["plan_out"]), plan)

    if not ctx["apply"]:
        out = {
            "ok": True,
            "dry_run": True,
            "risk_level": "irreversible",
            "refused": True,
            "reasons": [
                "Write disabled: pass --apply --yes --ack-irreversible --ack-no-snapshot to send events (pollutes analytics).",
                *safety_reasons,
            ],
            "plan": plan,
        }
        if plan_path:
            out["plan_path"] = plan_path
        ctx["audit"].write("event.send_refused", {"domain": domain, "name": args.name, "url": args.url})
        ctx["out"].emit(out)
        return 0

    if not ctx["yes"]:
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "risk_level": "irreversible",
                "error": "Refusing to send events without --yes (this writes data to Plausible).",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1

    if not bool(ctx.get("ack_irreversible", False)):
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "risk_level": "irreversible",
                "error": "Refusing irreversible action without --ack-irreversible (events cannot be undone).",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1
    if not bool(ctx.get("ack_no_snapshot", False)):
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "risk_level": "irreversible",
                "error": "Refused: event send has no saved before-state snapshot. Review the dry-run plan and pass --ack-no-snapshot only when the approved event should continue without an automatic restore point.",
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1

    if safety_reasons:
        ctx["out"].emit(
            {
                "ok": False,
                "dry_run": False,
                "risk_level": "irreversible",
                "error": "; ".join(safety_reasons),
                "error_type": "SafetyError",
                "plan": plan,
            }
        )
        return 1

    payload: dict[str, Any] = {
        "domain": domain,
        "name": args.name,
        "url": args.url,
        "props": props,
        "interactive": bool(args.interactive),
    }
    if referrer is not None:
        payload["referrer"] = referrer
    if revenue_currency is not None and revenue_amount is not None:
        payload["revenue"] = {"currency": revenue_currency, "amount": revenue_amount}

    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    resp = client.send_event(payload)
    verify = None
    if bool(getattr(args, "verify", False)):
        if domain != cfg.site_id:
            verify = {
                "ok": False,
                "error": "Verification only supports the default domain (PLAUSIBLE_SITE_ID).",
                "error_type": "NotSupported",
            }
        else:
            verify = _verify_event_visible(
                client=client,
                site_id=cfg.site_id,
                url=args.url,
                max_wait_s=float(getattr(args, "verify_wait_s", 8.0)),
            )
    verified = bool(verify["ok"]) if isinstance(verify, dict) and "ok" in verify else None
    receipt: dict[str, Any] = {
        "tool": "plausible-api-tool",
        "version": __version__,
        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": env_fingerprint,
        "command": "event send",
        "selector": selector,
        "changed": True,
        "verification": {
            "ok": verified,
            "details": verify if verify is not None else {"ok": False, "reason": "best-effort verification not requested"},
        },
        "diff_applied": [{"action": "plausible.events.send", "sent": {"domain": domain, "name": args.name, "url": args.url}}],
        "recovery": build_irreversible_recovery(),
        "before_state": plan["before_state"],
        "no_snapshot_approval": {
            "approved": bool(ctx.get("ack_no_snapshot")),
            "reason": "No saved before-state snapshot was available for this Plausible event send.",
        },
        "rollback_plan": None,
    }

    receipt_path = None
    if ctx.get("receipt_out"):
        receipt_path = write_json_file(str(ctx["receipt_out"]), receipt)

    out = {
        "ok": True,
        "dry_run": False,
        "changed": True,
        "risk_level": "irreversible",
        "verified": verified,
        "plan": plan,
        "receipt": receipt,
        "sent": {"domain": payload["domain"], "name": payload["name"], "url": payload["url"]},
        "response": resp,
    }
    if plan_path:
        out["plan_path"] = plan_path
    if receipt_path:
        out["receipt_path"] = receipt_path
    if verify is not None:
        out["verify"] = verify
    ctx["audit"].write("event.send", {"domain": payload["domain"], "name": payload["name"], "url": payload["url"]})
    ctx["out"].emit(out)
    return 0

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..arg_parsing import clamp_limit, parse_comma_separated_ints, quote_path_segment
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient
from ..json_files import read_json_file, write_json_file
from ..plans import build_plan, utc_now


def _client(ctx: dict) -> InstantlyClient:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    return InstantlyClient(cfg=cfg, http=http)


def _load_file_json(file_path: str, *, field: str = "file") -> dict[str, Any]:
    p = Path(file_path)
    body_any = read_json_file(p)
    if not isinstance(body_any, dict):
        raise ValidationError(f"Input JSON {field} must be a JSON object")
    return dict(body_any)


def _extract_id(obj: Any) -> str | None:
    if isinstance(obj, dict):
        for k in ("id", "test_id", "testId", "inbox_placement_test_id"):
            v = obj.get(k)
            if v:
                s = str(v).strip()
                if s:
                    return s
    return None


def _starting_after(args: Any) -> str | None:
    v = str(getattr(args, "starting_after", "") or "").strip()
    return v or None


def _tests_list_params(args: Any) -> dict[str, Any]:
    params: dict[str, Any] = {}
    limit = clamp_limit(getattr(args, "limit", None), default=20, max_value=50)
    if limit is not None:
        params["limit"] = limit
    cur = _starting_after(args)
    if cur:
        params["starting_after"] = cur
    search = str(getattr(args, "search", "") or "").strip()
    if search:
        params["search"] = search
    status = getattr(args, "status", None)
    if status is not None:
        params["status"] = int(status)
    sort_order = str(getattr(args, "sort_order", "") or "").strip()
    if sort_order:
        params["sort_order"] = sort_order
    return params


def cmd_inbox_placement_tests_list(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.get("/inbox-placement-tests", params=_tests_list_params(args))
    out = {"ok": True, "tests": res.data, "next_starting_after": res.next_starting_after}
    ctx["audit"].write("inbox_placement.tests.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_inbox_placement_tests_get(args: Any, ctx: dict) -> int:
    test_id = str(getattr(args, "test_id", "") or "").strip()
    if not test_id:
        raise ValidationError("Missing --test-id")
    client = _client(ctx)
    res = client.get(f"/inbox-placement-tests/{quote_path_segment(test_id, field='test-id')}")
    out = {"ok": True, "test": res.data}
    ctx["audit"].write("inbox_placement.tests.get", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_inbox_placement_tests_esp_options(args: Any, ctx: dict) -> int:
    _ = args
    client = _client(ctx)
    res = client.get("/inbox-placement-tests/email-service-provider-options")
    out = {"ok": True, "esp_options": res.data}
    ctx["audit"].write("inbox_placement.tests.esp_options", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_inbox_placement_tests_create(args: Any, ctx: dict) -> int:
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (test JSON)")
    body = _load_file_json(file_path)

    if bool(ctx.get("apply")) and (not bool(ctx.get("yes")) or not bool(ctx.get("ack_irreversible"))):
        raise SafetyError("Refused: inbox-placement tests create requires --apply --yes --ack-irreversible (sends email tests)")

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "inbox_placement.tests.create", "value": file_path},
        risk_level="irreversible",
        risk_reasons=["inbox-placement-test-sends-emails"],
        request={"method": "POST", "path": "/inbox-placement-tests", "body": body},
        verification_plan={"type": "read-back", "notes": "Best-effort GET by returned test id."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("inbox_placement.tests.create.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    created = client.post("/inbox-placement-tests", json_body=body).data
    tid = _extract_id(created)
    verified = None
    if tid:
        try:
            verified = client.get(f"/inbox-placement-tests/{quote_path_segment(tid, field='test-id')}").data
        except Exception:  # noqa: BLE001
            verified = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": verified is not None, "details": {"type": "inbox-placement-tests.get", "test_id": tid}},
        "result": {"created": created, "verified_test": verified},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("inbox_placement.tests.create.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_inbox_placement_tests_patch(args: Any, ctx: dict) -> int:
    test_id = str(getattr(args, "test_id", "") or "").strip()
    if not test_id:
        raise ValidationError("Missing --test-id")
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (patch JSON)")
    body = _load_file_json(file_path)

    if bool(ctx.get("apply")) and not bool(ctx.get("yes")):
        raise SafetyError("Refused: inbox-placement tests patch requires --apply --yes")

    path = f"/inbox-placement-tests/{quote_path_segment(test_id, field='test-id')}"
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "inbox_placement.tests.patch", "value": test_id},
        risk_level="medium",
        risk_reasons=["updates-inbox-placement-test"],
        request={"method": "PATCH", "path": path, "body": body},
        verification_plan={"type": "read-back", "notes": "Best-effort GET by test id after apply."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url), "test_id": test_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("inbox_placement.tests.patch.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    patched = client.patch(path, json_body=body).data
    verified = None
    try:
        verified = client.get(path).data
    except Exception:  # noqa: BLE001
        verified = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": verified is not None, "details": {"type": "inbox-placement-tests.get", "test_id": test_id}},
        "result": {"patched": patched, "verified_test": verified},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("inbox_placement.tests.patch.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_inbox_placement_tests_delete(args: Any, ctx: dict) -> int:
    test_id = str(getattr(args, "test_id", "") or "").strip()
    if not test_id:
        raise ValidationError("Missing --test-id")
    if bool(ctx.get("apply")) and not bool(ctx.get("yes")):
        raise SafetyError("Refused: inbox-placement tests delete requires --apply --yes")

    path = f"/inbox-placement-tests/{quote_path_segment(test_id, field='test-id')}"
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "inbox_placement.tests.delete", "value": test_id},
        risk_level="high",
        risk_reasons=["deletes-inbox-placement-test"],
        request={"method": "DELETE", "path": path, "body": {}},
        verification_plan={"type": "best-effort", "notes": "Best-effort: list tests after apply."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url), "test_id": test_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("inbox_placement.tests.delete.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    deleted = client.delete(path, json_body={}).data
    after = None
    try:
        after = client.get("/inbox-placement-tests", params={"limit": 20}).data
    except Exception:  # noqa: BLE001
        after = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": after is not None, "details": {"type": "inbox-placement-tests.list", "limit": 20}},
        "result": {"deleted": deleted, "tests_after": after},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("inbox_placement.tests.delete.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def _inbox_placement_analytics_list_params(args: Any) -> dict[str, Any]:
    test_id = str(getattr(args, "test_id", "") or "").strip()
    if not test_id:
        raise ValidationError("Missing --test-id")
    params: dict[str, Any] = {"test_id": test_id}
    limit = clamp_limit(getattr(args, "limit", None), default=20, max_value=50)
    if limit is not None:
        params["limit"] = limit
    cur = _starting_after(args)
    if cur:
        params["starting_after"] = cur
    date_from = str(getattr(args, "date_from", "") or "").strip()
    date_to = str(getattr(args, "date_to", "") or "").strip()
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to
    sender_email = str(getattr(args, "sender_email", "") or "").strip()
    if sender_email:
        params["sender_email"] = sender_email
    recipient_esp = str(getattr(args, "recipient_esp", "") or "").strip()
    if recipient_esp:
        params["recipient_esp"] = ",".join(str(i) for i in parse_comma_separated_ints(recipient_esp, field="recipient-esp"))
    recipient_geo = str(getattr(args, "recipient_geo", "") or "").strip()
    if recipient_geo:
        params["recipient_geo"] = ",".join(str(i) for i in parse_comma_separated_ints(recipient_geo, field="recipient-geo"))
    recipient_type = str(getattr(args, "recipient_type", "") or "").strip()
    if recipient_type:
        params["recipient_type"] = ",".join(str(i) for i in parse_comma_separated_ints(recipient_type, field="recipient-type"))
    return params


def cmd_inbox_placement_analytics_list(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.get("/inbox-placement-analytics", params=_inbox_placement_analytics_list_params(args))
    out = {"ok": True, "analytics": res.data, "next_starting_after": res.next_starting_after}
    ctx["audit"].write("inbox_placement.analytics.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_inbox_placement_analytics_get(args: Any, ctx: dict) -> int:
    analytics_id = str(getattr(args, "analytics_id", "") or "").strip()
    if not analytics_id:
        raise ValidationError("Missing --analytics-id")
    client = _client(ctx)
    res = client.get(f"/inbox-placement-analytics/{quote_path_segment(analytics_id, field='analytics-id')}")
    out = {"ok": True, "analytics": res.data}
    ctx["audit"].write("inbox_placement.analytics.get", {"ok": True})
    ctx["out"].emit(out)
    return 0


def _stats_body(args: Any) -> dict[str, Any]:
    test_id = str(getattr(args, "test_id", "") or "").strip()
    if not test_id:
        raise ValidationError("Missing --test-id")
    return {"test_id": test_id}


def cmd_inbox_placement_analytics_stats_by_test_id(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.post("/inbox-placement-analytics/stats-by-test-id", json_body=_stats_body(args))
    out = {"ok": True, "stats_by_test_id": res.data}
    ctx["audit"].write("inbox_placement.analytics.stats_by_test_id", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_inbox_placement_analytics_deliverability_insights(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.post("/inbox-placement-analytics/deliverability-insights", json_body=_stats_body(args))
    out = {"ok": True, "deliverability_insights": res.data}
    ctx["audit"].write("inbox_placement.analytics.deliverability_insights", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_inbox_placement_analytics_stats_by_date(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.post("/inbox-placement-analytics/stats-by-date", json_body=_stats_body(args))
    out = {"ok": True, "stats_by_date": res.data}
    ctx["audit"].write("inbox_placement.analytics.stats_by_date", {"ok": True})
    ctx["out"].emit(out)
    return 0


def _reports_list_params(args: Any) -> dict[str, Any]:
    test_id = str(getattr(args, "test_id", "") or "").strip()
    if not test_id:
        raise ValidationError("Missing --test-id")
    params: dict[str, Any] = {"test_id": test_id}
    limit = clamp_limit(getattr(args, "limit", None), default=20, max_value=50)
    if limit is not None:
        params["limit"] = limit
    cur = _starting_after(args)
    if cur:
        params["starting_after"] = cur
    date_from = str(getattr(args, "date_from", "") or "").strip()
    date_to = str(getattr(args, "date_to", "") or "").strip()
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to
    if bool(getattr(args, "skip_blacklist_report", False)):
        params["skip_blacklist_report"] = True
    if bool(getattr(args, "skip_spam_assassin_report", False)):
        params["skip_spam_assassin_report"] = True
    return params


def cmd_inbox_placement_reports_list(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.get("/inbox-placement-reports", params=_reports_list_params(args))
    out = {"ok": True, "reports": res.data, "next_starting_after": res.next_starting_after}
    ctx["audit"].write("inbox_placement.reports.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_inbox_placement_reports_get(args: Any, ctx: dict) -> int:
    report_id = str(getattr(args, "report_id", "") or "").strip()
    if not report_id:
        raise ValidationError("Missing --report-id")
    client = _client(ctx)
    res = client.get(f"/inbox-placement-reports/{quote_path_segment(report_id, field='report-id')}")
    out = {"ok": True, "report": res.data}
    ctx["audit"].write("inbox_placement.reports.get", {"ok": True})
    ctx["out"].emit(out)
    return 0

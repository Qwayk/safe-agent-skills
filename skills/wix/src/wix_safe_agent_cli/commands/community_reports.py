from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "community-reports"
BASE_PATH = "/reports/v2/reports"


def _report_id(raw) -> str:
    return _groups._coerce_text(raw, field="report-id")


def _entity_name(raw) -> str:
    return _groups._coerce_text(raw, field="entity-name")


def _entity_id(raw) -> str:
    return _groups._coerce_text(raw, field="entity-id")


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _query_body(raw) -> dict:
    body = _object_body(raw, field="query-json", allow_empty=True)
    if "query" in body:
        return body
    return {"query": body}


def cmd_community_reports_get(args, ctx) -> int:
    method = "community-reports.get"
    try:
        report_id = _report_id(args.report_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{report_id}",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reports_query(args, ctx) -> int:
    method = "community-reports.query"
    try:
        body = _query_body(args.query_json)
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/query",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reports_count_by_reason_types(args, ctx) -> int:
    method = "community-reports.count-by-reason-types"
    try:
        body = _object_body(args.request_json, field="request-json", allow_empty=True)
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/reason-types/count",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reports_create(args, ctx) -> int:
    method = "community-reports.create"
    try:
        body = _object_body(args.report_json, field="report-json")
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"operation": "create-report", "report": body.get("report", body)},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["create-community-report"],
            verification_notes="Provider response only. Official docs say Create Report creates a report and triggers Report Created.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reports_update(args, ctx) -> int:
    method = "community-reports.update"
    try:
        report_id = _report_id(args.report_id)
        body = _object_body(args.report_json, field="report-json")
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{report_id}",
            body=body,
            selector={"reportId": report_id, "report": body.get("report", body)},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["update-community-report"],
            verification_notes="Provider response only. Official docs say the current revision must be passed when updating a report.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reports_upsert(args, ctx) -> int:
    method = "community-reports.upsert"
    try:
        entity_name = _entity_name(args.entity_name)
        entity_id = _entity_id(args.entity_id)
        body = _object_body(args.report_json, field="report-json")
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/upsert/entity-name/{entity_name}/entity-id/{entity_id}",
            body=body,
            selector={"entityName": entity_name, "entityId": entity_id, "report": body.get("report", body)},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["upsert-community-report"],
            verification_notes="Provider response only. Official docs say Upsert Report creates a report or updates the existing report for the entity with the provided reason.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reports_delete(args, ctx) -> int:
    method = "community-reports.delete"
    try:
        report_id = _report_id(args.report_id)
        return _groups._run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{report_id}",
            body=None,
            selector={"reportId": report_id},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["delete-community-report"],
            verification_notes="Provider response only. Official docs say Delete Report removes the report from the dashboard report list.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_community_reports_bulk_delete_by_filter(args, ctx) -> int:
    method = "community-reports.bulk-delete-by-filter"
    try:
        body = _object_body(args.filter_json, field="filter-json")
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/bulk/delete-by-filter",
            body=body,
            selector={"operation": "bulk-delete-reports-by-filter", "filter": body.get("filter", body)},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["bulk-delete-community-reports"],
            verification_notes="Provider response only. Official docs say Bulk Delete Reports By Filter deletes multiple reports and triggers Report Deleted.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)

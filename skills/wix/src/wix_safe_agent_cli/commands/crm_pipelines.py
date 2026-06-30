from __future__ import annotations

from urllib.parse import quote

from . import community_groups as _groups


COMMAND_FAMILY = "crm-pipelines"
BASE_PATH = "/crm/pipelines/v1/pipelines"


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _pipeline_id(raw) -> str:
    return _groups._coerce_text(raw, field="pipeline-id")


def _query_body(raw) -> dict:
    body = _object_body(raw, field="query-json", allow_empty=True)
    if body:
        return body
    return {"query": {"sort": [{"fieldName": "updatedDate", "order": "DESC"}], "paging": {"limit": 50}}}


def _require_pipeline_body(body: dict, *, field: str) -> dict:
    pipeline = body.get("pipeline")
    if not isinstance(pipeline, dict) or not pipeline:
        raise _groups.ValidationError(f"--{field} must include pipeline")
    return pipeline


def _pipeline_id_from_body(body: dict, *, field: str) -> str:
    pipeline = _require_pipeline_body(body, field=field)
    value = pipeline.get("id")
    if not isinstance(value, str) or not value.strip():
        raise _groups.ValidationError(f"--{field} must include pipeline.id")
    return value.strip()


def _require_revision(body: dict, *, field: str) -> None:
    pipeline = _require_pipeline_body(body, field=field)
    if pipeline.get("revision") in (None, ""):
        raise _groups.ValidationError(f"--{field} must include pipeline.revision")


def _pipeline_ids_from_tags_body(body: dict, *, field: str) -> list[str]:
    raw_ids = body.get("pipelineIds")
    if not isinstance(raw_ids, list) or not raw_ids:
        raise _groups.ValidationError(f"--{field} must include non-empty pipelineIds")
    pipeline_ids: list[str] = []
    for raw_id in raw_ids:
        if not isinstance(raw_id, str) or not raw_id.strip():
            raise _groups.ValidationError("Each pipeline ID must be a non-empty string")
        pipeline_ids.append(raw_id.strip())
    return pipeline_ids


def _require_tag_change(body: dict, *, field: str) -> None:
    assign_tags = body.get("assignTags")
    unassign_tags = body.get("unassignTags")
    if not assign_tags and not unassign_tags:
        raise _groups.ValidationError(f"--{field} must include assignTags or unassignTags")


def cmd_crm_pipelines_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _object_body(args.pipeline_json, field="pipeline-json")
        pipeline = _require_pipeline_body(body, field="pipeline-json")
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"pipeline": pipeline},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-crm-pipeline-create", "developer-preview"],
            verification_notes="Inspect provider response, then use crm-pipelines get or query to verify the saved pipeline.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_pipelines_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        pipeline_id = _pipeline_id(args.pipeline_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{quote(pipeline_id, safe='')}",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_pipelines_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        body = _object_body(args.pipeline_json, field="pipeline-json")
        pipeline_id = _pipeline_id_from_body(body, field="pipeline-json")
        _require_revision(body, field="pipeline-json")
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{quote(pipeline_id, safe='')}",
            body=body,
            selector={"pipelineId": pipeline_id},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-crm-pipeline-update", "requires-current-revision", "developer-preview"],
            verification_notes="Inspect provider response, then use crm-pipelines get to verify the saved pipeline revision.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_pipelines_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        pipeline_id = _pipeline_id(args.pipeline_id)
        return _groups._run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{quote(pipeline_id, safe='')}",
            body=None,
            selector={"pipelineId": pipeline_id},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-crm-pipeline-delete", "permanently-removes-pipeline", "developer-preview"],
            verification_notes="Inspect provider response, then use crm-pipelines get or query to confirm the pipeline is gone.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_pipelines_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
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


def cmd_crm_pipelines_bulk_update_tags(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update-tags"
    try:
        body = _object_body(args.tags_json, field="tags-json")
        pipeline_ids = _pipeline_ids_from_tags_body(body, field="tags-json")
        _require_tag_change(body, field="tags-json")
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path="/crm/pipelines/v1/bulk/pipelines/update-tags",
            body=body,
            selector={"pipelineIds": pipeline_ids},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-crm-pipeline-tags-update", "developer-preview"],
            verification_notes="Inspect provider response, then use crm-pipelines get or query to verify pipeline tags.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_pipelines_bulk_update_tags_by_filter(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update-tags-by-filter"
    try:
        body = _object_body(args.tags_json, field="tags-json")
        _require_tag_change(body, field="tags-json")
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path="/crm/pipelines/v1/bulk/pipelines/update-tags-by-filter",
            body=body,
            selector={"filter": body.get("filter", {})},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-crm-pipeline-tags-update-by-filter", "can-affect-all-pipelines", "async-job", "developer-preview"],
            verification_notes=(
                "This Developer Preview method returns an async job ID. "
                "Use async-jobs get or list-items to inspect provider-side job progress."
            ),
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)

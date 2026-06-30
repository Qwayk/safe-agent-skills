from __future__ import annotations

from urllib.parse import quote

from . import community_groups as _groups


COMMAND_FAMILY = "crm-cards"
BASE_PATH = "/crm/pipelines/v1/cards"


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _card_id(raw) -> str:
    return _groups._coerce_text(raw, field="card-id")


def _query_body(raw) -> dict:
    body = _object_body(raw, field="query-json", allow_empty=True)
    if body:
        return body
    return {"query": {"sort": [{"fieldName": "updatedDate", "order": "DESC"}], "paging": {"limit": 50}}}


def _search_body(raw) -> dict:
    body = _object_body(raw, field="search-json", allow_empty=True)
    if body:
        return body
    return {"search": {"sort": [{"fieldName": "updatedDate", "order": "DESC"}], "paging": {"limit": 50}}}


def _require_card_body(body: dict, *, field: str) -> dict:
    card = body.get("card")
    if not isinstance(card, dict) or not card:
        raise _groups.ValidationError(f"--{field} must include card")
    return card


def _card_id_from_body(body: dict, *, field: str) -> str:
    card = _require_card_body(body, field=field)
    value = card.get("id")
    if not isinstance(value, str) or not value.strip():
        raise _groups.ValidationError(f"--{field} must include card.id")
    return value.strip()


def _require_revision(body: dict, *, field: str) -> None:
    card = _require_card_body(body, field=field)
    if card.get("revision") in (None, ""):
        raise _groups.ValidationError(f"--{field} must include card.revision")


def _card_ids_from_tags_body(body: dict, *, field: str) -> list[str]:
    raw_ids = body.get("cardIds")
    if not isinstance(raw_ids, list) or not raw_ids:
        raise _groups.ValidationError(f"--{field} must include non-empty cardIds")
    card_ids: list[str] = []
    for raw_id in raw_ids:
        if not isinstance(raw_id, str) or not raw_id.strip():
            raise _groups.ValidationError("Each card ID must be a non-empty string")
        card_ids.append(raw_id.strip())
    return card_ids


def _require_tag_change(body: dict, *, field: str) -> None:
    assign_tags = body.get("assignTags")
    unassign_tags = body.get("unassignTags")
    if not assign_tags and not unassign_tags:
        raise _groups.ValidationError(f"--{field} must include assignTags or unassignTags")


def _require_pipeline_id(body: dict, *, field: str) -> str:
    value = body.get("pipelineId")
    if not isinstance(value, str) or not value.strip():
        raise _groups.ValidationError(f"--{field} must include pipelineId")
    return value.strip()


def cmd_crm_cards_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _object_body(args.card_json, field="card-json")
        card = _require_card_body(body, field="card-json")
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"card": card},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-crm-card-create", "developer-preview"],
            verification_notes="Inspect provider response, then use crm-cards get or query to verify the saved card.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_cards_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        card_id = _card_id(args.card_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{quote(card_id, safe='')}",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_cards_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        body = _object_body(args.card_json, field="card-json")
        card_id = _card_id_from_body(body, field="card-json")
        _require_revision(body, field="card-json")
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{quote(card_id, safe='')}",
            body=body,
            selector={"cardId": card_id},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-crm-card-update", "requires-current-revision", "developer-preview"],
            verification_notes="Inspect provider response, then use crm-cards get to verify the saved card revision.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_cards_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        card_id = _card_id(args.card_id)
        return _groups._run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{quote(card_id, safe='')}",
            body=None,
            selector={"cardId": card_id},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-crm-card-delete", "permanently-removes-card", "developer-preview"],
            verification_notes="Inspect provider response, then use crm-cards get or query to confirm the card is gone.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_cards_query(args, ctx) -> int:
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


def cmd_crm_cards_search(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.search"
    try:
        body = _search_body(args.search_json)
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/search",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_cards_bulk_update_tags(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update-tags"
    try:
        body = _object_body(args.tags_json, field="tags-json")
        card_ids = _card_ids_from_tags_body(body, field="tags-json")
        _require_tag_change(body, field="tags-json")
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path="/crm/pipelines/v1/bulk/cards/update-tags",
            body=body,
            selector={"cardIds": card_ids},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-crm-card-tags-update", "developer-preview"],
            verification_notes="Inspect provider response, then use crm-cards get or query to verify card tags.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_cards_bulk_update_tags_by_filter(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update-tags-by-filter"
    try:
        body = _object_body(args.tags_json, field="tags-json")
        pipeline_id = _require_pipeline_id(body, field="tags-json")
        _require_tag_change(body, field="tags-json")
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path="/crm/pipelines/v1/bulk/cards/update-tags-by-filter",
            body=body,
            selector={"pipelineId": pipeline_id, "filter": body.get("filter", {})},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-crm-card-tags-update-by-filter", "can-affect-all-cards-in-pipeline", "async-job", "developer-preview"],
            verification_notes=(
                "This Developer Preview method returns an async job ID. "
                "Use async-jobs get or list-items to inspect provider-side job progress."
            ),
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_cards_move(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.move"
    try:
        card_id = _card_id(args.card_id)
        body = _object_body(args.move_json, field="move-json")
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/move/{quote(card_id, safe='')}",
            body=body,
            selector={"cardId": card_id, "stageId": body.get("stageId"), "outcome": body.get("outcome")},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-crm-card-stage-move", "same-pipeline-only", "developer-preview"],
            verification_notes="Inspect provider response, then use crm-cards get or search-by-stage to verify the card stage.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_crm_cards_search_by_stage(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.search-by-stage"
    try:
        body = _object_body(args.search_json, field="search-json")
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/search-by-stage",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)

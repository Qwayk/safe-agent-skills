from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from .faq_category_v2 import (
    _coerce_text,
    _emit_error,
    _read_json_arg,
    _run_read,
    _run_write,
)


COMMAND_FAMILY = "faq-question-entry-v2"
BASE_PATH = "/faq/v2/question-entries"


def _ctx(ctx: dict[str, Any]) -> dict[str, Any]:
    return {**ctx, "command_family_override": COMMAND_FAMILY}


def _question_entry_body(raw: Any, *, field: str) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = _read_json_arg(raw, field=field)
    body = dict(payload) if "questionEntry" in payload else {"questionEntry": payload}
    question_entry = body.get("questionEntry")
    if not isinstance(question_entry, dict) or not question_entry:
        raise ValidationError(f"--{field} must include a non-empty questionEntry object")
    return body, question_entry


def _question_entry_id_and_revision(question_entry: dict[str, Any], *, field: str) -> str:
    question_entry_id = _coerce_text(question_entry.get("id"), field=f"{field} questionEntry.id")
    _coerce_text(question_entry.get("revision"), field=f"{field} questionEntry.revision")
    return question_entry_id


def cmd_faq_question_entry_v2_list(args, ctx) -> int:
    method = "faqQuestionEntryV2.listQuestionEntries"
    try:
        body = _read_json_arg(getattr(args, "query_json", "{}"), field="query-json", allow_empty=True)
        path = BASE_PATH if not body else BASE_PATH
        return _run_read(method_name=method, http_method="GET", path=path, body=None, ctx=_ctx(ctx))
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_faq_question_entry_v2_get(args, ctx) -> int:
    method = "faqQuestionEntryV2.getQuestionEntry"
    try:
        question_entry_id = _coerce_text(args.question_entry_id, field="question-entry-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{question_entry_id}", body=None, ctx=_ctx(ctx))
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_faq_question_entry_v2_query(args, ctx) -> int:
    method = "faqQuestionEntryV2.queryQuestionEntries"
    try:
        body = _read_json_arg(getattr(args, "query_json", "{}"), field="query-json", allow_empty=True)
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/query", body=body, ctx=_ctx(ctx))
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_faq_question_entry_v2_create(args, ctx) -> int:
    method = "faqQuestionEntryV2.createQuestionEntry"
    try:
        body, question_entry = _question_entry_body(args.question_entry_json, field="question-entry-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"questionEntry": question_entry},
            proposed_changes=[{"operation": "create-question-entry", "questionEntry": question_entry}],
            ctx=_ctx(ctx),
            requires_ack=False,
            risk_reasons=["wix-faq-question-entry-create"],
            verification_notes="Inspect the provider response, then use faq-question-entry-v2 get or query to verify the question entry.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_faq_question_entry_v2_update(args, ctx) -> int:
    method = "faqQuestionEntryV2.updateQuestionEntry"
    try:
        body, question_entry = _question_entry_body(args.question_entry_json, field="question-entry-json")
        question_entry_id = _question_entry_id_and_revision(question_entry, field="question-entry-json")
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{question_entry_id}",
            body=body,
            selector={"questionEntry": question_entry},
            proposed_changes=[{"operation": "update-question-entry", "questionEntry": question_entry}],
            ctx=_ctx(ctx),
            requires_ack=False,
            risk_reasons=["wix-faq-question-entry-update", "requires-current-revision"],
            verification_notes="Inspect the provider response, then use faq-question-entry-v2 get to verify the question entry.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_faq_question_entry_v2_delete(args, ctx) -> int:
    method = "faqQuestionEntryV2.deleteQuestionEntry"
    try:
        question_entry_id = _coerce_text(args.question_entry_id, field="question-entry-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{question_entry_id}",
            body=None,
            selector={"questionEntryId": question_entry_id},
            proposed_changes=[{"operation": "delete-question-entry", "questionEntryId": question_entry_id}],
            ctx=_ctx(ctx),
            requires_ack=True,
            risk_reasons=["wix-faq-question-entry-delete", "irreversible"],
            verification_notes="Inspect the provider response, then use faq-question-entry-v2 get or query to confirm removal.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_faq_question_entry_v2_bulk_delete(args, ctx) -> int:
    method = "faqQuestionEntryV2.bulkDeleteQuestionEntries"
    try:
        body = _read_json_arg(args.question_entries_json, field="question-entries-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/faq/question-entry/v2/bulk/question-entries/delete",
            body=body,
            selector={"bulkDelete": body},
            proposed_changes=[{"operation": "bulk-delete-question-entries", "body": body}],
            ctx=_ctx(ctx),
            requires_ack=True,
            risk_reasons=["wix-faq-question-entry-bulk-delete", "irreversible"],
            verification_notes="Inspect the provider response, then query the deleted IDs to confirm removal.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_faq_question_entry_v2_bulk_update(args, ctx) -> int:
    method = "faqQuestionEntryV2.bulkUpdateQuestionEntry"
    try:
        body = _read_json_arg(args.question_entries_json, field="question-entries-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/faq/question-entry/v2/bulk/question-entries/update",
            body=body,
            selector={"bulkUpdate": body},
            proposed_changes=[{"operation": "bulk-update-question-entries", "body": body}],
            ctx=_ctx(ctx),
            requires_ack=False,
            risk_reasons=["wix-faq-question-entry-bulk-update", "requires-current-revision"],
            verification_notes="Inspect the provider response, then query the updated IDs to confirm revisions changed.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_faq_question_entry_v2_set_labels(args, ctx) -> int:
    method = "faqQuestionEntryV2.setQuestionEntryLabels"
    try:
        question_entry_id = _coerce_text(args.question_entry_id, field="question-entry-id")
        body = _read_json_arg(args.labels_json, field="labels-json")
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{question_entry_id}/labels",
            body=body,
            selector={"questionEntryId": question_entry_id},
            proposed_changes=[{"operation": "set-question-entry-labels", "questionEntryId": question_entry_id, "body": body}],
            ctx=_ctx(ctx),
            requires_ack=False,
            risk_reasons=["wix-faq-question-entry-set-labels", "replaces-all-existing-labels"],
            verification_notes="Inspect the provider response, then use faq-question-entry-v2 get to verify labels.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_faq_question_entry_v2_update_extended_fields(args, ctx) -> int:
    method = "faqQuestionEntryV2.updateExtendedFields"
    try:
        question_entry_id = _coerce_text(args.question_entry_id, field="question-entry-id")
        body = _read_json_arg(args.extended_fields_json, field="extended-fields-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{question_entry_id}/update-extended-fields",
            body=body,
            selector={"questionEntryId": question_entry_id},
            proposed_changes=[
                {"operation": "update-question-entry-extended-fields", "questionEntryId": question_entry_id, "body": body}
            ],
            ctx=_ctx(ctx),
            requires_ack=False,
            risk_reasons=["wix-faq-question-entry-update-extended-fields"],
            verification_notes="Inspect the provider response, then use faq-question-entry-v2 get to verify extended fields.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)

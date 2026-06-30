from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "loyalty-imports"
BASE_PATH = "/_api/loyalty-imports/v1/loyalty-imports"


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _import_id(raw) -> str:
    return _groups._coerce_text(raw, field="import-id")


def _query_body(raw) -> dict:
    body = _object_body(raw, field="query-json", allow_empty=True)
    if body:
        return body
    return {"query": {"sort": [{"fieldName": "createdDate", "order": "DESC"}], "paging": {"limit": 50}}}


def _create_body(raw) -> dict:
    body = _object_body(raw, field="import-json")
    file_url = body.get("fileUrl")
    if not isinstance(file_url, str) or not file_url.strip():
        raise _groups.ValidationError("--import-json must include fileUrl")
    body["fileUrl"] = file_url.strip()
    return body


def _execute_body(raw) -> dict:
    body = _object_body(raw, field="execute-json")
    import_id = body.get("loyaltyImportId")
    if not isinstance(import_id, str) or not import_id.strip():
        raise _groups.ValidationError("--execute-json must include loyaltyImportId")
    mapping_info = body.get("headerMappingInfo")
    if not isinstance(mapping_info, dict):
        raise _groups.ValidationError("--execute-json must include headerMappingInfo")
    mappings = mapping_info.get("headerMappings")
    if not isinstance(mappings, list) or not mappings:
        raise _groups.ValidationError("--execute-json must include headerMappingInfo.headerMappings")
    body["loyaltyImportId"] = import_id.strip()
    return body


def cmd_loyalty_imports_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        import_id = _import_id(args.import_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=BASE_PATH,
            params={"loyaltyImportId": import_id},
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_imports_query(args, ctx) -> int:
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


def cmd_loyalty_imports_create_file_url(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create-file-url"
    try:
        _ = args
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/wixmp-upload-url",
            body=None,
            selector={"operation": "create-loyalty-import-file-url"},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["create-loyalty-import-upload-url"],
            verification_notes="Use the returned filePath and uploadUrl only for the official Loyalty Imports upload flow.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_imports_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _create_body(args.import_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"operation": "create-loyalty-import", "fileUrl": body.get("fileUrl")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["create-loyalty-import", "customer-point-balances-import-flow"],
            verification_notes="Verify with loyalty-imports get until the import object is parsed or reports row-level errors.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_imports_execute(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.execute"
    try:
        body = _execute_body(args.execute_json)
        import_id = body["loyaltyImportId"]
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/execute",
            body=body,
            selector={"operation": "execute-loyalty-import", "loyaltyImportId": import_id},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["execute-loyalty-import", "can-overwrite-customer-point-balances"],
            verification_notes=(
                "Only apply after loyalty-imports get shows PARSED. "
                "Verify with loyalty-imports get and use get-error-file-download-url for failed rows."
            ),
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_imports_get_error_file_download_url(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-error-file-download-url"
    try:
        import_id = _import_id(args.import_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/error-file-download-url",
            params={"loyaltyImportId": import_id},
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)

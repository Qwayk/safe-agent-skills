"""Generate the ElevenLabs operation ledger from the pinned OpenAPI document.

The handwritten ledger in :mod:`operations` is treated as an override layer.  This
keeps carefully reviewed command names, descriptions, and safety tags stable while
making additions from the provider specification reproducible.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from pprint import pformat
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OPENAPI = ROOT / "openapi.json"
OPERATIONS = Path(__file__).with_name("operations.py")
GENERATED = Path(__file__).with_name("generated_inventory.py")
COVERAGE = ROOT / "docs" / "api_coverage.md"
COMMAND_REFERENCE = ROOT / "docs" / "command_reference.md"

MANUAL_ROWS = (
    {"name": "agents_conversation_wss", "section": "Agents", "description": "ElevenAgents conversation WebSocket.", "method": "WEBSOCKET", "path": "wss://api.elevenlabs.io/v1/convai/conversation?agent_id={agent_id}", "status": "Implemented", "doc_url": "https://elevenlabs.io/docs/eleven-agents/api-reference/eleven-agents/websocket", "safety": ("write", "spend_money", "sensitive_output"), "cli_command": "convai conversation websocket"},
    {"name": "tts_stream_input_wss", "section": "Text-to-speech", "description": "Stream-input text-to-speech WebSocket.", "method": "WEBSOCKET", "path": "wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input", "status": "Implemented", "doc_url": "https://elevenlabs.io/docs/api-reference/text-to-speech/v-1-text-to-speech-voice-id-stream-input", "safety": ("write", "spend_money", "binary_output"), "cli_command": "tts stream-input websocket"},
    {"name": "tts_multi_stream_input_wss", "section": "Text-to-speech", "description": "Multi-context stream-input text-to-speech WebSocket.", "method": "WEBSOCKET", "path": "wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/multi-stream-input", "status": "Implemented", "doc_url": "https://elevenlabs.io/docs/api-reference/text-to-speech/v-1-text-to-speech-voice-id-multi-stream-input", "safety": ("write", "spend_money", "binary_output"), "cli_command": "tts multi-stream-input websocket"},
    {"name": "dialogue_stream_input_wss", "section": "Text-to-dialogue", "description": "Stream-input text-to-dialogue WebSocket.", "method": "WEBSOCKET", "path": "wss://api.elevenlabs.io/v1/text-to-dialogue/stream-input", "status": "Implemented", "doc_url": "https://elevenlabs.io/docs/api-reference/text-to-dialogue/ttd-websocket", "safety": ("write", "spend_money", "binary_output"), "cli_command": "dialogue stream-input websocket"},
    {"name": "dialogue_multi_stream_input_wss", "section": "Text-to-dialogue", "description": "Multi-context stream-input text-to-dialogue WebSocket.", "method": "WEBSOCKET", "path": "wss://api.elevenlabs.io/v1/text-to-dialogue/multi-stream-input", "status": "Implemented", "doc_url": "https://elevenlabs.io/docs/api-reference/text-to-dialogue/ttd-multi-websocket", "safety": ("write", "spend_money", "binary_output"), "cli_command": "dialogue multi-stream-input websocket"},
    {"name": "speech_engine_upstream_callback", "section": "Callbacks", "description": "Speech-engine upstream reverse-connection WebSocket.", "method": "WEBSOCKET", "path": "wss://api.elevenlabs.io/speech-engine/upstream", "status": "Callback-only", "doc_url": "https://elevenlabs.io/docs/api-reference/speech-engine/speech-engine-upstream", "safety": ("read",)},
    {"name": "twilio_initiation_webhook_callback", "section": "Callbacks", "description": "Developer-hosted Twilio conversation-initiation webhook.", "method": "CALLBACK", "path": "callback://twilio/conversation-initiation", "status": "Callback-only", "doc_url": "https://elevenlabs.io/docs/eleven-agents/phone-numbers/twilio-integration/customising-calls", "safety": ("read",)},
)

def _slug(value: Any) -> str:
    values = value if isinstance(value, list) else [value]
    text = "-".join(str(v) for v in values if v)
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "operation"

def _overrides() -> dict[tuple[str, str], dict[str, Any]]:
    tree = ast.parse(OPERATIONS.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "handwritten_inventory_data":
            if node.value is None:
                continue
            data = ast.literal_eval(node.value)
            return {(str(x["method"]).upper(), str(x["path"])): x for x in data}
    raise RuntimeError("handwritten_inventory_data assignment not found")

def _schema_fields(schema: dict[str, Any], schemas: dict[str, Any], prefix: str = "", seen: set[str] | None = None) -> set[str]:
    """Return dotted property paths reachable from an OpenAPI schema."""
    seen = set() if seen is None else seen
    fields: set[str] = set()
    ref = schema.get("$ref")
    if ref:
        if ref in seen:
            return fields
        seen.add(ref)
        target = schemas.get(ref.rsplit("/", 1)[-1], {})
        fields.update(_schema_fields(target, schemas, prefix, seen))
    for key in ("anyOf", "oneOf", "allOf"):
        for alternative in schema.get(key, ()):
            if isinstance(alternative, dict):
                fields.update(_schema_fields(alternative, schemas, prefix, seen))
    items = schema.get("items")
    if isinstance(items, dict):
        fields.update(_schema_fields(items, schemas, prefix, seen))
    for name, child in (schema.get("properties") or {}).items():
        path = f"{prefix}.{name}" if prefix else str(name)
        fields.add(path)
        if isinstance(child, dict):
            fields.update(_schema_fields(child, schemas, path, seen.copy()))
    return fields

def _schema_reaches_ref(schema: dict[str, Any], target_ref: str, schemas: dict[str, Any], seen: set[str] | None = None) -> bool:
    """Whether a schema can reach a named component through composition/ref edges."""
    seen = set() if seen is None else seen
    ref = schema.get("$ref")
    if ref == f"#/components/schemas/{target_ref}":
        return True
    if ref:
        if ref in seen:
            return False
        seen.add(ref)
        target = schemas.get(ref.rsplit("/", 1)[-1], {})
        if _schema_reaches_ref(target, target_ref, schemas, seen):
            return True
    for value in schema.values():
        if isinstance(value, dict) and _schema_reaches_ref(value, target_ref, schemas, seen.copy()):
            return True
        if isinstance(value, list) and any(isinstance(item, dict) and _schema_reaches_ref(item, target_ref, schemas, seen.copy()) for item in value):
            return True
    return False

def _schema_contract(schema: dict[str, Any], schemas: dict[str, Any], prefix: str = "", seen: set[str] | None = None) -> tuple[set[str], set[str], set[str]]:
    """Collect resolved fields, required properties, and binary upload fields.

    Required properties are collected only from the current schema/allOf branches;
    alternatives remain alternatives and are therefore not over-required.
    """
    seen = set() if seen is None else seen
    fields: set[str] = set()
    required: set[str] = set()
    files: set[str] = set()
    if schema.get("format") == "binary" and prefix:
        files.add(prefix)
    ref = schema.get("$ref")
    if ref:
        if ref in seen:
            return fields, required, files
        seen = seen | {ref}
        target = schemas.get(ref.rsplit("/", 1)[-1], {})
        f, r, u = _schema_contract(target, schemas, prefix, seen)
        fields |= f
        required |= r
        files |= u
    for branch_name in ("allOf", "oneOf", "anyOf"):
        for branch in schema.get(branch_name, ()):
            if isinstance(branch, dict):
                f, r, u = _schema_contract(branch, schemas, prefix, seen.copy())
                fields |= f
                files |= u
                if branch_name == "allOf":
                    required |= r
    properties = schema.get("properties") or {}
    required_names = {str(x) for x in schema.get("required", ())}
    for name, child in properties.items():
        path = f"{prefix}.{name}" if prefix else str(name)
        fields.add(path)
        if str(name) in required_names:
            required.add(path)
        if isinstance(child, dict):
            if child.get("format") == "binary":
                files.add(path)
            f, r, u = _schema_contract(child, schemas, path, seen.copy())
            fields |= f
            required |= r
            files |= u
    items = schema.get("items")
    if isinstance(items, dict):
        f, r, u = _schema_contract(items, schemas, prefix, seen.copy())
        fields |= f
        required |= r
        files |= u
    return fields, required, files

def _schema_open_prefixes(schema: dict[str, Any], schemas: dict[str, Any], prefix: str = "", seen: set[str] | None = None) -> set[str]:
    """Return object prefixes whose additionalProperties are intentionally open."""
    seen = set() if seen is None else seen
    ref = schema.get("$ref")
    if ref:
        if ref in seen:
            return set()
        seen = seen | {ref}
        return _schema_open_prefixes(schemas.get(ref.rsplit("/", 1)[-1], {}), schemas, prefix, seen)
    result: set[str] = set()
    if "additionalProperties" in schema and schema.get("additionalProperties") is not False:
        result.add(prefix)
    for key in ("allOf", "oneOf", "anyOf"):
        for branch in schema.get(key, ()):
            if isinstance(branch, dict):
                result |= _schema_open_prefixes(branch, schemas, prefix, seen.copy())
    for name, child in (schema.get("properties") or {}).items():
        if isinstance(child, dict):
            child_prefix = f"{prefix}.{name}" if prefix else str(name)
            result |= _schema_open_prefixes(child, schemas, child_prefix, seen.copy())
    if isinstance(schema.get("items"), dict):
        result |= _schema_open_prefixes(schema["items"], schemas, prefix, seen.copy())
    return result

def _contract(operation: dict[str, Any], path: str, path_item: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    parameters = list(path_item.get("parameters", [])) + list(operation.get("parameters", []))
    path_params = tuple(p["name"] for p in parameters if p.get("in") == "path" and p.get("required"))
    query_params = tuple(p["name"] for p in parameters if p.get("in") == "query")
    required_query_params = tuple(p["name"] for p in parameters if p.get("in") == "query" and p.get("required"))
    headers = tuple(p["name"] for p in parameters if p.get("in") == "header" and p.get("required") and p["name"].lower() not in {"xi-api-key", "authorization"})
    body = operation.get("requestBody") or {}
    responses = operation.get("responses") or {}
    response_types = tuple(sorted({ctype for response in responses.values() for ctype in (response.get("content") or {})}))
    body_fields: set[str] = set()
    body_required: set[str] = set()
    file_fields: set[str] = set()
    file_required: set[str] = set()
    open_prefixes: set[str] = set()
    webhook_events: set[str] = set()
    schemas = spec.get("components", {}).get("schemas", {})
    can_configure_webhooks = False
    for media in (body.get("content") or {}).values():
        schema = media.get("schema") or {}
        if isinstance(schema, dict):
            fields, required, files = _schema_contract(schema, schemas)
            body_fields.update(fields)
            body_required.update(required)
            file_fields.update(files)
            file_required.update(required & files)
            open_prefixes.update(_schema_open_prefixes(schema, schemas))
        can_configure_webhooks = can_configure_webhooks or _schema_reaches_ref(schema, "ConvAIWebhooks", schemas)
    if can_configure_webhooks:
        for schema in spec.get("components", {}).get("schemas", {}).values():
            if schema.get("title") == "WebhookEventType":
                webhook_events.update(schema.get("enum") or ())
    return {
        "required_path_params": path_params,
        "required_query_params": required_query_params,
        "query_params": query_params,
        "required_headers": headers,
        "request_body_required": bool(body.get("required")),
        "request_body_content_types": tuple(sorted((body.get("content") or {}).keys())),
        "response_content_types": response_types,
        "request_body_fields": tuple(sorted(body_fields)),
        "request_body_required_fields": tuple(sorted(body_required)),
        "request_file_fields": tuple(sorted(file_fields)),
        "request_file_required_fields": tuple(sorted(file_required)),
        "request_body_open_prefixes": tuple(sorted(open_prefixes)),
        "webhook_events": tuple(sorted(webhook_events)),
    }

def _derived_safety(operation: dict[str, Any], path: str, method: str) -> tuple[str, ...]:
    method = method.upper()
    content_types = {ctype for ctype in (operation.get("responses", {}).get("200", {}).get("content") or {})}
    family = path.lower()
    tags: set[str] = {"read"} if method == "GET" else set()
    if method == "DELETE":
        tags.update(("write", "irreversible"))
    elif method in {"POST", "PUT", "PATCH"}:
        tags.add("write")
        if method == "POST" and any(x in family for x in ("query", "analytics", "usage", "simulate", "calculate")):
            tags = {"post_read"}
        if any(x in family for x in ("generation", "text-to-speech", "text-to-dialogue", "sound-generation", "music", "dubbing", "speech-to-text", "speech-to-speech", "audio-isolation", "conversation", "/calls", "/messages")):
            tags.update(("write", "spend_money"))
    if any(ctype.startswith(("audio/", "video/", "application/octet-stream")) or ctype in {"binary/octet-stream", "application/zip"} for ctype in content_types):
        tags.add("binary_output")
    if any(x in family for x in ("account", "conversation", "phone", "secrets", "webhook", "transcript")):
        tags.add("sensitive_output")
    if any(x in family for x in ("calls", "messages")) or method == "DELETE":
        tags.update(("write", "irreversible"))
    return tuple(x for x in ("read", "post_read", "write", "spend_money", "irreversible", "binary_output", "sensitive_output") if x in tags)

_SENSITIVE_JSON = {
    "text_to_speech_full_with_timestamps", "text_to_speech_stream_with_timestamps",
    "text_to_dialogue_full_with_timestamps", "text_to_dialogue_stream_with_timestamps",
    "compose_detailed_stream", "dubbing_language_get", "get_signed_url_deprecated",
    "get_knowledge_base_source_file_url", "get_dubbed_transcript_file",
    "get_workspace_batch_calls", "get_batch_call", "export_batch_call",
    "handle_twilio_outbound_call", "handle_exotel_outbound_call", "handle_sip_trunk_outbound_call",
    "whatsapp_outbound_message",
}
_SPEND = {
    "create_podcast", "convert_project_endpoint", "convert_chapter_endpoint", "add_language", "transcribe", "translate", "render",
    "audio_native_create", "audio_native_project_update_content_endpoint", "audio_native_update_content_from_url",
    "create_video_generation", "create_image_generation", "retry_batch_call", "speech_to_text_realtime", "agents_conversation_wss",
    "handle_twilio_outbound_call", "handle_exotel_outbound_call", "handle_sip_trunk_outbound_call",
    "whatsapp_outbound_call", "whatsapp_outbound_message", "twilio_register_call", "public_submit_order",
}
_IRREVERSIBLE = {
    "remove_rules", "disable", "remove_member", "unshare_resource_endpoint", "cancel_crawl_job_route",
    "post_knowledge_base_bulk_delete_route", "cancel_batch_call", "handle_twilio_outbound_call", "handle_exotel_outbound_call",
    "handle_sip_trunk_outbound_call", "whatsapp_outbound_call", "whatsapp_outbound_message", "public_remove_order_item",
    "retry_batch_call", "public_submit_order", "twilio_register_call",
}
_POST_READ = {"get_similar_library_voices", "get_knowledge_base_bulk_dependent_agents_route"}
_READ_SENSITIVE_PATHS = {
    "/v1/convai/conversations/{conversation_id}/sip-messages",
    "/v1/convai/conversations/messages/text-search",
    "/v1/convai/conversations/messages/smart-search",
    "/v1/convai/phone-numbers/{phone_number_id}/sip-messages",
}

def _audit_corrections(name: str, safety: tuple[str, ...]) -> tuple[str, ...]:
    tags = list(safety)
    if name in _SENSITIVE_JSON:
        tags = [x for x in tags if x != "binary_output"]
        if "sensitive_output" not in tags:
            tags.append("sensitive_output")
    if name == "stream_project_snapshot_archive_endpoint":
        tags = [x for x in tags if x != "sensitive_output"]
        if "binary_output" not in tags:
            tags.append("binary_output")
    if name == "compose_detailed":
        if "binary_output" not in tags:
            tags.append("binary_output")
    if name in _SPEND and "spend_money" not in tags:
        tags.append("spend_money")
    if name in _IRREVERSIBLE and "irreversible" not in tags:
        tags.append("irreversible")
    if name in _POST_READ:
        tags = [x for x in tags if x not in {"write", "spend_money", "irreversible"}]
        if "post_read" not in tags:
            tags.append("post_read")
    return tuple(dict.fromkeys(tags))

def build_inventory() -> list[dict[str, Any]]:
    spec = json.loads(OPENAPI.read_text(encoding="utf-8"))
    overrides = _overrides()
    rows: list[dict[str, Any]] = []
    used: set[str] = set()
    for path, path_item in spec["paths"].items():
        for method, operation in path_item.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            key = (method.upper(), path)
            override = dict(overrides.get(key, {}))
            deprecated = bool(operation.get("deprecated"))
            if deprecated:
                row = {"name": operation.get("operationId", f"{method}_{path}"), "section": "Deprecated", "description": operation.get("summary", "Deprecated operation."), "method": method.upper(), "path": path, "status": "Deprecated", "doc_url": "https://elevenlabs.io/docs/api-reference", "safety": ("write", "irreversible") if method.upper() == "DELETE" else (("read",) if method.upper() == "GET" else ("write",))}
                row.update({k: v for k, v in override.items() if k in {"name", "section", "description", "doc_url", "safety"}})
                row["safety"] = _audit_corrections(str(row["name"]), tuple(row["safety"]))
                row.update(_contract(operation, path, path_item, spec))
                rows.append(row)
                continue
            group = operation.get("x-fern-sdk-group-name")
            method_name = operation.get("x-fern-sdk-method-name")
            base = f"{_slug(group)} {_slug(method_name)}" if group and method_name else f"{_slug(operation.get('operationId', method))}"
            command = str(override.get("cli_command") or base)
            if command in used:
                command = f"{command} {_slug(method)}-{_slug(path)}"
            while command in used:
                command += "-op"
            used.add(command)
            row = {"name": operation.get("operationId") or _slug(command).replace("-", "_"), "section": _slug(group).replace("-", " ").title() if group else "API", "description": operation.get("description") or operation.get("summary") or "Execute this ElevenLabs API operation.", "method": method.upper(), "path": path, "status": "Implemented", "doc_url": "https://elevenlabs.io/docs/api-reference", "safety": _derived_safety(operation, path, method)}
            row.update(_contract(operation, path, path_item, spec))
            derived_safety = tuple(row["safety"])
            row.update(override)
            override_safety = tuple(override.get("safety", ()))
            if "post_read" in override_safety:
                # post_read is an explicit non-mutating override; retain only
                # output-classification tags from the derived result.
                row["safety"] = tuple(dict.fromkeys(override_safety + tuple(x for x in derived_safety if x in {"binary_output", "sensitive_output"})))
            else:
                row["safety"] = tuple(dict.fromkeys(derived_safety + override_safety))
            row["safety"] = _audit_corrections(str(row["name"]), tuple(row["safety"]))
            if method.upper() == "GET" and path in _READ_SENSITIVE_PATHS:
                row["safety"] = ("read", "sensitive_output")
            row["cli_command"] = command
            rows.append(row)
    # Preserve existing non-HTTP handwritten rows (not represented by OpenAPI),
    # notably the realtime STT WebSocket and documentation-only authentication row.
    openapi_keys = {(r["method"], r["path"]) for r in rows}
    rows.extend(x for x in overrides.values() if (str(x["method"]).upper(), x["path"]) not in openapi_keys)
    rows.extend(MANUAL_ROWS)
    return rows

def render(rows: list[dict[str, Any]]) -> None:
    payload = "from __future__ import annotations\n\n# Generated by inventory_generator.py; do not edit.\ninventory_data = " + pformat(rows, width=120, sort_dicts=True) + "\n"
    GENERATED.write_text(payload, encoding="utf-8")
    lines = ["# API coverage", "", "Generated from `openapi.json` by `python -m elevenlabs_api_tool.inventory_generator`.", "", "| Endpoint | Capability | Status | CLI command(s) | Safety gates | Notes |", "|---|---|---|---|---|---|"]
    for row in rows:
        safety = ", ".join(row.get("safety", ()))
        command = row.get("cli_command") or "—"
        capability = str(row["description"]).replace("|", "/").replace("\n", " ").replace("\r", " ").strip()
        lines.append(f"| {row['method']} {row['path']} | {capability} | {row['status']} | {command} | {safety} | Doc: {row['doc_url']} |")
    COVERAGE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ref = ["# Command reference", "", "Generated from `openapi.json` by `python -m elevenlabs_api_tool.inventory_generator`.", "", "Each implemented command includes its provider request contract.", ""]
    for row in rows:
        command = row.get("cli_command")
        if not command:
            continue
        req = ", ".join(row.get("required_path_params", ())) or "none"
        query = ", ".join(row.get("required_query_params", ())) or "none"
        headers = ", ".join(row.get("required_headers", ())) or "none"
        body = ", ".join(row.get("request_body_content_types", ())) or "none"
        fields = ", ".join(row.get("request_body_fields", ())) or "none"
        response = ", ".join(row.get("response_content_types", ())) or "unspecified"
        ref.extend([f"- `elevenlabs-api-tool {command}`", f"  - Contract: required path `{req}`; query `{query}`; headers `{headers}`; body required `{str(bool(row.get('request_body_required'))).lower()}` ({body}); fields `{fields}`; responses `{response}`."])
    COMMAND_REFERENCE.write_text("\n".join(ref) + "\n", encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail when generated files drift")
    args = parser.parse_args()
    rows = build_inventory()
    if args.check:
        expected = "from __future__ import annotations\n\n# Generated by inventory_generator.py; do not edit.\ninventory_data = " + pformat(rows, width=120, sort_dicts=True) + "\n"
        if GENERATED.read_text(encoding="utf-8") != expected:
            return 1
        before = {p: p.read_text(encoding="utf-8") for p in (COVERAGE, COMMAND_REFERENCE)}
        render(rows)
        changed = any(p.read_text(encoding="utf-8") != before[p] for p in (COVERAGE, COMMAND_REFERENCE))
        for p, content in before.items():
            p.write_text(content, encoding="utf-8")
        return 1 if changed else 0
    render(rows)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

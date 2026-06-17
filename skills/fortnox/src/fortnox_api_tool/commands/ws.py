from __future__ import annotations

from typing import Any

from ..auth_runtime import resolve_access_token
from ..errors import ValidationError
from ..websocket_inventory import topic_names
from ..websocket_runtime import (
    build_add_tenants_command,
    build_add_topics_command,
    build_list_tenants_command,
    build_remove_tenants_command,
    websocket_roundtrip,
    websocket_subscribe_session,
)


def _normalize_bearer_token(token: str) -> str:
    cleaned = str(token or "").strip()
    if not cleaned:
        raise ValidationError("Websocket access token cannot be empty")
    return cleaned if cleaned.lower().startswith("bearer ") else f"Bearer {cleaned}"


def _resolve_access_tokens(ctx: dict[str, Any], supplied_tokens: list[str] | None) -> list[str]:
    tokens = [token for token in (supplied_tokens or []) if str(token or "").strip()]
    if tokens:
        return [_normalize_bearer_token(token) for token in tokens]

    resolved = resolve_access_token(cfg=ctx["cfg"], env_file=ctx["env_file"])
    if not resolved.token:
        raise ValidationError(
            "No websocket access token is available. Pass `--access-token` or run `fortnox-api-tool auth login` first."
        )
    if resolved.expired is True and resolved.source == "token_file":
        raise ValidationError("Stored Fortnox access token looks expired. Run `fortnox-api-tool auth refresh` first.")
    return [_normalize_bearer_token(resolved.token)]


def _resolve_client_secret(ctx: dict[str, Any], override: str | None) -> str:
    secret = str(override or ctx["cfg"].client_secret or "").strip()
    if not secret:
        raise ValidationError("FORTNOX_CLIENT_SECRET or `--client-secret` is required for websocket tenant add.")
    return secret


def _topic_choices() -> tuple[str, ...]:
    return topic_names()


def topic_choice_list() -> tuple[str, ...]:
    return _topic_choices()


def _parse_topic_offset(raw: str) -> tuple[str, str]:
    value = str(raw or "").strip()
    if "=" not in value:
        raise ValidationError("Topic offsets must use the format `<topic>=<offset>`.")
    topic, offset = value.split("=", 1)
    topic = topic.strip()
    offset = offset.strip()
    if topic not in _topic_choices():
        raise ValidationError(f"Unknown Fortnox websocket topic: {topic}")
    if not offset:
        raise ValidationError("Topic offsets must include a non-empty offset value.")
    return topic, offset


def _build_topic_specs(args) -> list[dict[str, str]]:
    specs: dict[str, dict[str, str]] = {}
    ordered_topics: list[str] = []

    for topic in list(getattr(args, "topic", None) or []):
        if topic not in specs:
            specs[topic] = {"topic": topic}
            ordered_topics.append(topic)

    for raw in list(getattr(args, "topic_offset", None) or []):
        topic, offset = _parse_topic_offset(raw)
        if topic not in specs:
            specs[topic] = {"topic": topic}
            ordered_topics.append(topic)
        specs[topic]["offset"] = offset

    if not ordered_topics:
        raise ValidationError("At least one `--topic` or `--topic-offset <topic>=<offset>` value is required.")

    return [specs[topic] for topic in ordered_topics]


def _redact_add_tenants_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "command": payload["command"],
        "includeChildTenants": bool(payload.get("includeChildTenants")),
        "clientSecretProvided": bool(payload.get("clientSecret")),
        "accessTokenCount": len(list(payload.get("accessTokens") or [])),
    }


def _redact_add_tenants_response(response: dict[str, Any], access_tokens: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "response": response.get("response"),
        "result": response.get("result"),
    }

    tenant_ids = response.get("tenantIds")
    if isinstance(tenant_ids, dict):
        rows: list[dict[str, Any]] = []
        for index, token in enumerate(access_tokens):
            if token in tenant_ids:
                rows.append({"token_index": index, "tenant_id": tenant_ids[token]})
        out["tenantIds"] = rows

    invalid_tokens = response.get("invalidTokens")
    if isinstance(invalid_tokens, list):
        invalid_indexes = [index for index, token in enumerate(access_tokens) if token in invalid_tokens]
        out["invalidTokenIndexes"] = invalid_indexes
        out["invalidTokenCount"] = len(invalid_tokens)

    return out


def _redact_generic_response(response: dict[str, Any]) -> dict[str, Any]:
    return dict(response)


def _emit_roundtrip_result(
    *,
    ctx: dict[str, Any],
    request_summary: dict[str, Any],
    response_summary: dict[str, Any],
) -> int:
    ctx["out"].emit(
        {
            "ok": True,
            "ws_url": ctx["cfg"].ws_url,
            "request": request_summary,
            "response": response_summary,
        }
    )
    return 0


def cmd_ws_tenants_add(args, ctx: dict[str, Any]) -> int:
    access_tokens = _resolve_access_tokens(ctx, getattr(args, "access_token", None))
    client_secret = _resolve_client_secret(ctx, getattr(args, "client_secret", None))
    payload = build_add_tenants_command(
        access_tokens=access_tokens,
        client_secret=client_secret,
        include_child_tenants=bool(getattr(args, "include_child_tenants", False)),
    )
    response = websocket_roundtrip(ws_url=ctx["cfg"].ws_url, timeout_s=float(ctx["timeout_s"]), payload=payload)
    return _emit_roundtrip_result(
        ctx=ctx,
        request_summary=_redact_add_tenants_payload(payload),
        response_summary=_redact_add_tenants_response(response, access_tokens),
    )


def cmd_ws_tenants_remove(args, ctx: dict[str, Any]) -> int:
    tenant_ids = [int(value) for value in list(getattr(args, "tenant_id", None) or [])]
    if not tenant_ids:
        raise ValidationError("At least one `--tenant-id` is required.")
    payload = build_remove_tenants_command(tenant_ids=tenant_ids)
    response = websocket_roundtrip(ws_url=ctx["cfg"].ws_url, timeout_s=float(ctx["timeout_s"]), payload=payload)
    return _emit_roundtrip_result(
        ctx=ctx,
        request_summary={"command": payload["command"], "tenantIds": tenant_ids},
        response_summary=_redact_generic_response(response),
    )


def cmd_ws_tenants_list(args, ctx: dict[str, Any]) -> int:
    _ = args
    payload = build_list_tenants_command()
    response = websocket_roundtrip(ws_url=ctx["cfg"].ws_url, timeout_s=float(ctx["timeout_s"]), payload=payload)
    return _emit_roundtrip_result(
        ctx=ctx,
        request_summary={"command": payload["command"]},
        response_summary=_redact_generic_response(response),
    )


def cmd_ws_topics_add(args, ctx: dict[str, Any]) -> int:
    topics = _build_topic_specs(args)
    payload = build_add_topics_command(topics=topics)
    response = websocket_roundtrip(ws_url=ctx["cfg"].ws_url, timeout_s=float(ctx["timeout_s"]), payload=payload)
    return _emit_roundtrip_result(
        ctx=ctx,
        request_summary={"command": payload["command"], "topics": topics},
        response_summary=_redact_generic_response(response),
    )


def cmd_ws_subscribe_start(args, ctx: dict[str, Any]) -> int:
    access_tokens = _resolve_access_tokens(ctx, getattr(args, "access_token", None))
    client_secret = _resolve_client_secret(ctx, getattr(args, "client_secret", None))
    topics = _build_topic_specs(args)
    max_events = int(getattr(args, "max_events", 10) or 0)
    idle_timeout_s = float(getattr(args, "idle_timeout_s", 30.0) or 0.0)
    if max_events < 0:
        raise ValidationError("`--max-events` must be 0 or greater.")
    if idle_timeout_s <= 0:
        raise ValidationError("`--idle-timeout-s` must be greater than 0.")

    add_tenants_payload = build_add_tenants_command(
        access_tokens=access_tokens,
        client_secret=client_secret,
        include_child_tenants=bool(getattr(args, "include_child_tenants", False)),
    )
    add_topics_payload = build_add_topics_command(topics=topics)
    session = websocket_subscribe_session(
        ws_url=ctx["cfg"].ws_url,
        timeout_s=float(ctx["timeout_s"]),
        add_tenants_payload=add_tenants_payload,
        add_topics_payload=add_topics_payload,
        max_events=max_events,
        idle_timeout_s=idle_timeout_s,
    )

    control_responses = list(session["control_responses"])
    add_tenants_response = _redact_add_tenants_response(control_responses[0], access_tokens)
    add_topics_response = _redact_generic_response(control_responses[1])
    subscribe_response = _redact_generic_response(control_responses[2])

    ctx["out"].emit(
        {
            "ok": True,
            "ws_url": ctx["cfg"].ws_url,
            "request": {
                "addTenants": _redact_add_tenants_payload(add_tenants_payload),
                "addTopics": {"command": add_topics_payload["command"], "topics": topics},
                "subscribe": {"command": "subscribe-v1"},
                "maxEvents": max_events,
                "idleTimeoutSeconds": idle_timeout_s,
            },
            "responses": {
                "addTenants": add_tenants_response,
                "addTopics": add_topics_response,
                "subscribe": subscribe_response,
            },
            "events": list(session["events"]),
            "event_count": len(list(session["events"])),
            "stop_reason": session["stop_reason"],
        }
    )
    return 0

from __future__ import annotations

import json
from typing import Any, Callable


def build_add_tenants_command(
    *,
    access_tokens: list[str],
    client_secret: str,
    include_child_tenants: bool,
) -> dict[str, Any]:
    return {
        "command": "add-tenants-v1",
        "includeChildTenants": include_child_tenants,
        "clientSecret": client_secret,
        "accessTokens": list(access_tokens),
    }


def build_remove_tenants_command(*, tenant_ids: list[int]) -> dict[str, Any]:
    return {
        "command": "remove-tenants-v1",
        "tenants": list(tenant_ids),
    }


def build_list_tenants_command() -> dict[str, Any]:
    return {"command": "list-tenants-v1"}


def build_add_topics_command(*, topics: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "command": "add-topics-v1",
        "topics": list(topics),
    }


def build_subscribe_command() -> dict[str, Any]:
    return {"command": "subscribe-v1"}


def _load_websocket_client():
    try:
        import websocket  # type: ignore[import-not-found]
    except ImportError as e:  # pragma: no cover - exercised via runtime, not unit tests
        raise RuntimeError(
            "Missing websocket client support. Reinstall the tool so the `websocket-client` dependency is available."
        ) from e
    return websocket


def _default_connection_factory(*, ws_url: str, timeout_s: float):
    websocket = _load_websocket_client()
    try:
        return websocket.create_connection(ws_url, timeout=timeout_s)
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"Could not connect to Fortnox websocket stream: {type(e).__name__}: {e}") from e


def _parse_json_message(raw: Any) -> dict[str, Any]:
    if isinstance(raw, bytes):
        text = raw.decode("utf-8", errors="replace")
    else:
        text = str(raw)
    try:
        payload = json.loads(text)
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"Fortnox websocket returned invalid JSON: {type(e).__name__}: {e}") from e
    if not isinstance(payload, dict):
        raise RuntimeError("Fortnox websocket returned a non-object JSON message")
    return payload


def _is_timeout_error(error: Exception) -> bool:
    return isinstance(error, TimeoutError) or type(error).__name__ in {"WebSocketTimeoutException", "TimeoutError"}


def _send_json(connection: Any, payload: dict[str, Any]) -> None:
    connection.send(json.dumps(payload, ensure_ascii=False))


def _recv_json(connection: Any) -> dict[str, Any]:
    return _parse_json_message(connection.recv())


def _ensure_ok_response(response: dict[str, Any], expected_response: str) -> None:
    actual = str(response.get("response") or "").strip()
    if actual != expected_response:
        raise RuntimeError(
            f"Expected websocket response `{expected_response}`, got `{actual or 'unknown'}`."
        )
    result = str(response.get("result") or "").strip().lower()
    if result != "ok":
        raise RuntimeError(
            f"Fortnox websocket command `{expected_response}` failed: {json.dumps(response, ensure_ascii=False)}"
        )


def websocket_roundtrip(
    *,
    ws_url: str,
    timeout_s: float,
    payload: dict[str, Any],
    connection_factory: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    factory = connection_factory or _default_connection_factory
    connection = factory(ws_url=ws_url, timeout_s=timeout_s)
    try:
        _send_json(connection, payload)
        return _recv_json(connection)
    finally:
        try:
            connection.close()
        except Exception:  # noqa: BLE001
            pass


def websocket_subscribe_session(
    *,
    ws_url: str,
    timeout_s: float,
    add_tenants_payload: dict[str, Any] | None,
    add_topics_payload: dict[str, Any] | None,
    max_events: int,
    idle_timeout_s: float,
    connection_factory: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    factory = connection_factory or _default_connection_factory
    connection = factory(ws_url=ws_url, timeout_s=timeout_s)
    try:
        control_responses: list[dict[str, Any]] = []

        if add_tenants_payload is not None:
            _send_json(connection, add_tenants_payload)
            add_tenants_response = _recv_json(connection)
            _ensure_ok_response(add_tenants_response, "add-tenants-v1")
            control_responses.append(add_tenants_response)

        if add_topics_payload is not None:
            _send_json(connection, add_topics_payload)
            add_topics_response = _recv_json(connection)
            _ensure_ok_response(add_topics_response, "add-topics-v1")
            control_responses.append(add_topics_response)

        subscribe_payload = build_subscribe_command()
        _send_json(connection, subscribe_payload)
        subscribe_response = _recv_json(connection)
        _ensure_ok_response(subscribe_response, "subscribe-v1")
        control_responses.append(subscribe_response)

        if hasattr(connection, "settimeout"):
            connection.settimeout(idle_timeout_s)

        events: list[dict[str, Any]] = []
        stop_reason = "max_events_reached"
        while True:
            if max_events > 0 and len(events) >= max_events:
                break
            try:
                message = _recv_json(connection)
            except Exception as e:  # noqa: BLE001
                if _is_timeout_error(e):
                    stop_reason = "idle_timeout"
                    break
                raise
            events.append(message)

        return {
            "control_responses": control_responses,
            "events": events,
            "stop_reason": stop_reason,
        }
    finally:
        try:
            connection.close()
        except Exception:  # noqa: BLE001
            pass

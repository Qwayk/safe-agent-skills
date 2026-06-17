from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from fortnox_api_tool.cli import main
from fortnox_api_tool.websocket_runtime import websocket_roundtrip, websocket_subscribe_session


class _FakeTimeout(TimeoutError):
    pass


class _FakeConnection:
    def __init__(self, messages):
        self.messages = list(messages)
        self.sent = []
        self.closed = False
        self.timeout = None

    def send(self, raw: str) -> None:
        self.sent.append(json.loads(raw))

    def recv(self):
        if not self.messages:
            raise _FakeTimeout("idle")
        message = self.messages.pop(0)
        if isinstance(message, Exception):
            raise message
        return json.dumps(message)

    def settimeout(self, timeout: float) -> None:
        self.timeout = timeout

    def close(self) -> None:
        self.closed = True


class TestWebsocketRuntime(unittest.TestCase):
    def test_websocket_roundtrip_sends_payload_and_reads_single_response(self) -> None:
        connection = _FakeConnection([{"response": "list-tenants-v1", "result": "ok", "tenantIds": [34231]}])

        result = websocket_roundtrip(
            ws_url="wss://ws.fortnox.se/topics-v1",
            timeout_s=30.0,
            payload={"command": "list-tenants-v1"},
            connection_factory=lambda **_: connection,
        )

        self.assertEqual(result["response"], "list-tenants-v1")
        self.assertEqual(connection.sent, [{"command": "list-tenants-v1"}])
        self.assertTrue(connection.closed)

    def test_websocket_subscribe_session_sends_full_sequence_and_collects_events(self) -> None:
        connection = _FakeConnection(
            [
                {"response": "add-tenants-v1", "result": "ok", "tenantIds": {"Bearer token": 34231}},
                {"response": "add-topics-v1", "result": "ok"},
                {"response": "subscribe-v1", "result": "ok"},
                {"topic": "invoices", "type": "invoice-created-v1", "tenantId": 34231, "entityId": "1"},
                {"topic": "customers", "type": "customer-updated-v2", "tenantId": 34231, "entityId": "2"},
            ]
        )

        result = websocket_subscribe_session(
            ws_url="wss://ws.fortnox.se/topics-v1",
            timeout_s=30.0,
            add_tenants_payload={
                "command": "add-tenants-v1",
                "includeChildTenants": False,
                "clientSecret": "secret",
                "accessTokens": ["Bearer token"],
            },
            add_topics_payload={
                "command": "add-topics-v1",
                "topics": [{"topic": "invoices"}, {"topic": "customers", "offset": "abc"}],
            },
            max_events=2,
            idle_timeout_s=12.5,
            connection_factory=lambda **_: connection,
        )

        self.assertEqual(
            connection.sent,
            [
                {
                    "command": "add-tenants-v1",
                    "includeChildTenants": False,
                    "clientSecret": "secret",
                    "accessTokens": ["Bearer token"],
                },
                {
                    "command": "add-topics-v1",
                    "topics": [{"topic": "invoices"}, {"topic": "customers", "offset": "abc"}],
                },
                {"command": "subscribe-v1"},
            ],
        )
        self.assertEqual(connection.timeout, 12.5)
        self.assertEqual(len(result["events"]), 2)
        self.assertEqual(result["stop_reason"], "max_events_reached")
        self.assertTrue(connection.closed)

    def test_websocket_subscribe_session_stops_on_idle_timeout(self) -> None:
        connection = _FakeConnection(
            [
                {"response": "add-tenants-v1", "result": "ok", "tenantIds": {"Bearer token": 34231}},
                {"response": "add-topics-v1", "result": "ok"},
                {"response": "subscribe-v1", "result": "ok"},
                _FakeTimeout("idle"),
            ]
        )

        result = websocket_subscribe_session(
            ws_url="wss://ws.fortnox.se/topics-v1",
            timeout_s=30.0,
            add_tenants_payload={
                "command": "add-tenants-v1",
                "includeChildTenants": False,
                "clientSecret": "secret",
                "accessTokens": ["Bearer token"],
            },
            add_topics_payload={"command": "add-topics-v1", "topics": [{"topic": "invoices"}]},
            max_events=10,
            idle_timeout_s=5.0,
            connection_factory=lambda **_: connection,
        )

        self.assertEqual(result["events"], [])
        self.assertEqual(result["stop_reason"], "idle_timeout")


class TestWebsocketCommands(unittest.TestCase):
    def _run(self, *, env_path: Path, args: list[str]) -> tuple[int, dict[str, object], str]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--env-file", str(env_path), *args])
        text = buf.getvalue().strip()
        self.assertTrue(text, "Command did not emit JSON output")
        return rc, json.loads(text), text

    def test_ws_tenants_add_uses_default_access_token_and_redacts_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n"
                "FORTNOX_WS_URL=wss://ws.fortnox.se/topics-v1\n"
                "FORTNOX_API_TOKEN=token-123\n"
                "FORTNOX_CLIENT_SECRET=secret-456\n",
                encoding="utf-8",
            )
            with patch("fortnox_api_tool.commands.ws.websocket_roundtrip") as websocket_roundtrip_mock:
                websocket_roundtrip_mock.return_value = {
                    "response": "add-tenants-v1",
                    "result": "ok",
                    "tenantIds": {"Bearer token-123": 34231},
                }
                rc, payload, raw = self._run(env_path=env_path, args=["ws", "tenants", "add"])

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["accessTokenCount"], 1)
        self.assertTrue(payload["request"]["clientSecretProvided"])
        self.assertEqual(payload["response"]["tenantIds"], [{"token_index": 0, "tenant_id": 34231}])
        sent_payload = websocket_roundtrip_mock.call_args.kwargs["payload"]
        self.assertEqual(sent_payload["command"], "add-tenants-v1")
        self.assertEqual(sent_payload["accessTokens"], ["Bearer token-123"])
        self.assertEqual(sent_payload["clientSecret"], "secret-456")
        self.assertNotIn("token-123", raw)
        self.assertNotIn("secret-456", raw)

    def test_ws_topics_add_sends_official_offset_shape(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_WS_URL=wss://ws.fortnox.se/topics-v1\n",
                encoding="utf-8",
            )
            with patch("fortnox_api_tool.commands.ws.websocket_roundtrip") as websocket_roundtrip_mock:
                websocket_roundtrip_mock.return_value = {"response": "add-topics-v1", "result": "ok"}
                rc, payload, _raw = self._run(
                    env_path=env_path,
                    args=[
                        "ws",
                        "topics",
                        "add",
                        "--topic",
                        "supplier-invoices",
                        "--topic-offset",
                        "invoices=hd72U",
                    ],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(
            websocket_roundtrip_mock.call_args.kwargs["payload"],
            {
                "command": "add-topics-v1",
                "topics": [
                    {"topic": "supplier-invoices"},
                    {"topic": "invoices", "offset": "hd72U"},
                ],
            },
        )

    def test_ws_subscribe_start_collects_events(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n"
                "FORTNOX_WS_URL=wss://ws.fortnox.se/topics-v1\n"
                "FORTNOX_API_TOKEN=token-123\n"
                "FORTNOX_CLIENT_SECRET=secret-456\n",
                encoding="utf-8",
            )
            with patch("fortnox_api_tool.commands.ws.websocket_subscribe_session") as session_mock:
                session_mock.return_value = {
                    "control_responses": [
                        {"response": "add-tenants-v1", "result": "ok", "tenantIds": {"Bearer token-123": 34231}},
                        {"response": "add-topics-v1", "result": "ok"},
                        {"response": "subscribe-v1", "result": "ok"},
                    ],
                    "events": [
                        {"topic": "invoices", "type": "invoice-created-v1", "tenantId": 34231, "entityId": "1001"}
                    ],
                    "stop_reason": "max_events_reached",
                }
                rc, payload, raw = self._run(
                    env_path=env_path,
                    args=[
                        "ws",
                        "subscribe",
                        "start",
                        "--topic",
                        "invoices",
                        "--max-events",
                        "1",
                        "--idle-timeout-s",
                        "15",
                    ],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["event_count"], 1)
        self.assertEqual(payload["events"][0]["type"], "invoice-created-v1")
        self.assertEqual(payload["responses"]["addTenants"]["tenantIds"], [{"token_index": 0, "tenant_id": 34231}])
        self.assertNotIn("token-123", raw)
        self.assertNotIn("secret-456", raw)
        self.assertEqual(session_mock.call_args.kwargs["add_topics_payload"]["topics"], [{"topic": "invoices"}])

    def test_ws_topics_add_rejects_bad_offset_shape(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_WS_URL=wss://ws.fortnox.se/topics-v1\n",
                encoding="utf-8",
            )
            rc, payload, _raw = self._run(
                env_path=env_path,
                args=["ws", "topics", "add", "--topic-offset", "invoices"],
            )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("topic", str(payload["error"]).lower())

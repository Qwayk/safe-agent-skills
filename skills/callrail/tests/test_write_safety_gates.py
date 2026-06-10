from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from callrail_safe_agent_cli.cli import main


class _DummyResponse:
    def __init__(self, *, status: int, url: str, payload: object) -> None:
        self.status_code = int(status)
        self.url = str(url)
        self.content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.headers: dict[str, str] = {}


def _write_env_file(path: Path, *, base_url: str, token: str = "tok_test", timeout_s: int = 30) -> None:
    path.write_text(
        "\n".join(
            [
                f"CALLRAIL_API_BASE_URL={base_url}",
                f"CALLRAIL_API_TOKEN={token}",
                f"CALLRAIL_TIMEOUT_S={timeout_s}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


class TestCallrailWriteSafetyGates(unittest.TestCase):
    def _run_main(
        self,
        *,
        env_path: Path,
        argv: list[str],
        fake_request,
    ) -> tuple[int, dict[str, Any], list[tuple[str, str, dict[str, Any], Any]]]:
        calls: list[tuple[str, str, dict[str, Any], Any]] = []

        def wrapped_fake_request(self_obj, method: str, url: str, **kwargs: Any) -> Any:  # noqa: ANN001, ARG001
            calls.append((method, str(url), dict(kwargs.get("headers") or {}), kwargs.get("json")))
            return fake_request(method=method, url=url, **kwargs)

        with tempfile.TemporaryDirectory():
            buf = io.StringIO()
            with patch.dict(os.environ, {"CALLRAIL_DEFAULT_ACCOUNT_ID": "acc_default"}):
                with patch("requests.Session.request", new=wrapped_fake_request):
                    with redirect_stdout(buf):
                        rc = main(["--output", "json", "--env-file", str(env_path), *argv])

        payload = json.loads(buf.getvalue())
        return rc, payload, calls

    def test_tags_create_apply_without_yes_is_refusal_and_no_http(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            def fake_request(**_kwargs: Any) -> Any:
                self.fail("should not be called when apply requires --yes")

            rc, payload, calls = self._run_main(
                env_path=env_path,
                argv=["--apply", "tags", "create", "--payload-json", "{}"],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("refused"))
            self.assertTrue(payload.get("ok"))
            self.assertNotIn("response", payload)
            self.assertEqual(calls, [])
            self.assertIn("--yes", " ".join(str(reason) for reason in payload.get("reasons", [])))

    def test_tags_create_apply_with_yes_requires_ack_no_snapshot_and_no_http(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            def fake_request(**_kwargs: Any) -> Any:
                self.fail("should not be called when apply lacks --ack-no-snapshot")

            rc, payload, calls = self._run_main(
                env_path=env_path,
                argv=["--apply", "--yes", "tags", "create", "--payload-json", "{}"],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("refused"))
            self.assertTrue(payload.get("ok"))
            self.assertNotIn("response", payload)
            self.assertEqual(calls, [])
            self.assertIn("--ack-no-snapshot", " ".join(str(reason) for reason in payload.get("reasons", [])))

    def test_tags_create_apply_with_ack_no_snapshot_executes_and_redacts_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            def fake_request(method: str, url: str, **kwargs: Any) -> _DummyResponse:
                _ = (method, url)
                return _DummyResponse(status=201, url=str(url), payload={"ok": True, "id": "tag_123"})

            rc, payload, calls = self._run_main(
                env_path=env_path,
                argv=["--apply", "--yes", "--ack-no-snapshot", "tags", "create", "--payload-json", "{}"],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("ok"))
            self.assertFalse(payload.get("refused", False))
            self.assertEqual(payload.get("request", {}).get("method"), "POST")
            self.assertEqual(payload.get("request", {}).get("url"), "https://api.callrail.test/v3/a/acc_default/tags.json")
            self.assertEqual(len(calls), 1)
            request_headers = {str(k).lower(): str(v) for _, _, headers, _ in calls for k, v in headers.items()}
            self.assertEqual(request_headers.get("authorization"), "Token token=tok_test")
            self.assertEqual(
                str(payload.get("request", {}).get("headers", {}).get("Authorization")).strip(),
                "***REDACTED***",
            )
            self.assertEqual(payload.get("response", {}).get("status"), 201)
            self.assertEqual(payload.get("receipt", {}).get("before_state", {}).get("status"), "no_snapshot_available")
            self.assertTrue(payload.get("receipt", {}).get("no_snapshot_approval", {}).get("acknowledged"))

    def test_calls_create_outbound_apply_requires_ack_irr_then_executes_with_ack(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            def fake_request(**_kwargs: Any) -> Any:
                self.fail("should not be called when apply lacks --ack-irreversible")

            rc, payload, calls = self._run_main(
                env_path=env_path,
                argv=["--apply", "--yes", "calls", "create-outbound", "--payload-json", "{}"],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("refused"))
            self.assertTrue(payload.get("ok"))
            self.assertNotIn("response", payload)
            self.assertEqual(calls, [])
            self.assertIn("--ack-irreversible", " ".join(str(reason) for reason in payload.get("reasons", [])))

            def fake_request_approved(method: str, url: str, **kwargs: Any) -> _DummyResponse:
                _ = (method, url)
                return _DummyResponse(status=200, url=str(url), payload={"ok": True, "id": "call_123"})

            rc_approved, payload_approved, calls_approved = self._run_main(
                env_path=env_path,
                argv=[
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "--ack-irreversible",
                    "calls",
                    "create-outbound",
                    "--payload-json",
                    "{}",
                ],
                fake_request=fake_request_approved,
            )

            self.assertEqual(rc_approved, 0)
            self.assertTrue(payload_approved.get("ok"))
            self.assertFalse(payload_approved.get("refused", False))
            self.assertEqual(payload_approved.get("request", {}).get("method"), "POST")
            self.assertEqual(payload_approved.get("request", {}).get("url"), "https://api.callrail.test/v3/a/acc_default/calls.json")
            self.assertEqual(len(calls_approved), 1)
            self.assertEqual(payload_approved.get("response", {}).get("status"), 200)
            approved_headers = {str(k).lower(): str(v) for _, _, headers, _ in calls_approved for k, v in headers.items()}
            self.assertEqual(approved_headers.get("authorization"), "Token token=tok_test")
            self.assertEqual(
                str(payload_approved.get("request", {}).get("headers", {}).get("Authorization")).strip(),
                "***REDACTED***",
            )

    def test_text_messages_send_apply_requires_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            def fake_request(**_kwargs: Any) -> Any:
                self.fail("should not be called when apply lacks --ack-irreversible")

            rc, payload, calls = self._run_main(
                env_path=env_path,
                argv=["--apply", "--yes", "text-messages", "send", "--payload-json", "{}"],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("refused"))
            self.assertTrue(payload.get("ok"))
            self.assertNotIn("response", payload)
            self.assertEqual(calls, [])
            self.assertIn("--ack-irreversible", " ".join(str(reason) for reason in payload.get("reasons", [])))

    def test_text_messages_send_with_media_url_uses_json_body(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            captured: dict[str, Any] = {}

            def fake_request(method: str, url: str, **kwargs: Any) -> _DummyResponse:
                captured["method"] = method
                captured["url"] = str(url)
                captured["json"] = kwargs.get("json")
                captured["files"] = kwargs.get("files")
                captured["data"] = kwargs.get("data")
                return _DummyResponse(status=201, url=str(url), payload={"ok": True, "id": "msg_123"})

            payload = json.dumps(
                {
                    "to": {"number": "+15550001111"},
                    "from": {"number": "+15552223333"},
                    "media_url": "https://cdn.example.com/hello.jpg",
                }
            )

            rc, out_payload, calls = self._run_main(
                env_path=env_path,
                argv=[
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "--ack-irreversible",
                    "text-messages",
                    "send",
                    "--payload-json",
                    payload,
                ],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(out_payload.get("ok"))
            self.assertFalse(out_payload.get("refused", False))
            self.assertEqual(out_payload.get("request", {}).get("method"), "POST")
            self.assertEqual(out_payload.get("request", {}).get("url"), "https://api.callrail.test/v3/a/acc_default/text-messages.json")
            self.assertEqual(calls[0][0], "POST")
            self.assertEqual(calls[0][1], "https://api.callrail.test/v3/a/acc_default/text-messages.json")
            self.assertEqual(calls[0][3], json.loads(payload))
            self.assertEqual(captured.get("json"), json.loads(payload))
            self.assertIsNone(captured.get("data"))
            self.assertIsNone(captured.get("files"))
            self.assertEqual(out_payload.get("request", {}).get("json"), json.loads(payload))

    def test_text_messages_send_with_media_file_uses_multipart_form(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")
            media_path = Path(td) / "sample.png"
            media_path.write_bytes(b"png-bytes")

            captured: dict[str, Any] = {}

            def fake_request(method: str, url: str, **kwargs: Any) -> _DummyResponse:
                captured["method"] = method
                captured["url"] = str(url)
                captured["json"] = kwargs.get("json")
                captured["data"] = kwargs.get("data")
                captured["files"] = kwargs.get("files")
                return _DummyResponse(status=201, url=str(url), payload={"ok": True, "id": "msg_123"})

            payload = json.dumps(
                {
                    "to": {"number": "+15550001111"},
                    "from": {"number": "+15552223333"},
                    "body": "hello",
                }
            )
            rc, out_payload, calls = self._run_main(
                env_path=env_path,
                argv=[
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "--ack-irreversible",
                    "text-messages",
                    "send",
                    "--payload-json",
                    payload,
                    "--media-file",
                    str(media_path),
                ],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(out_payload.get("ok"))
            self.assertFalse(out_payload.get("refused", False))
            self.assertEqual(out_payload.get("request", {}).get("method"), "POST")
            self.assertEqual(out_payload.get("request", {}).get("url"), "https://api.callrail.test/v3/a/acc_default/text-messages.json")
            self.assertEqual(calls[0][0], "POST")
            self.assertEqual(calls[0][1], "https://api.callrail.test/v3/a/acc_default/text-messages.json")
            self.assertIsNone(calls[0][3])
            self.assertIsNone(captured.get("json"))
            self.assertIsNotNone(captured.get("files"))
            self.assertIn("media_file", captured.get("files"))
            self.assertEqual(captured["files"]["media_file"][0], media_path.name)
            self.assertEqual(captured["data"], {"to": json.dumps({"number": "+15550001111"}), "from": json.dumps({"number": "+15552223333"}), "body": "hello"})
            self.assertEqual(
                out_payload.get("request", {}).get("form"),
                {"to": json.dumps({"number": "+15550001111"}), "from": json.dumps({"number": "+15552223333"}), "body": "hello"},
            )
            self.assertEqual(out_payload.get("request", {}).get("media_file"), {"filename": media_path.name})

    def test_text_messages_send_refuses_media_url_and_media_file_together(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")
            media_path = Path(td) / "sample.png"
            media_path.write_bytes(b"png-bytes")

            def fake_request(**_kwargs: Any) -> Any:
                self.fail("should not be called when media_url and media_file are both provided")

            payload = json.dumps(
                {
                    "to": {"number": "+15550001111"},
                    "from": {"number": "+15552223333"},
                    "media_url": "https://cdn.example.com/hello.jpg",
                }
            )
            rc, out_payload, calls = self._run_main(
                env_path=env_path,
                argv=[
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "--ack-irreversible",
                    "text-messages",
                    "send",
                    "--payload-json",
                    payload,
                    "--media-file",
                    str(media_path),
                ],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(out_payload.get("refused"))
            self.assertTrue(out_payload.get("ok"))
            self.assertNotIn("response", out_payload)
            self.assertEqual(calls, [])
            self.assertIn("either media_url or media_file", " ".join(str(reason) for reason in out_payload.get("reasons", [])))

    def test_integrations_create_refuses_unsafe_payload_type(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            def fake_request(**_kwargs: Any) -> Any:
                self.fail("should not be called when integration type is unsafe")

            rc, payload, calls = self._run_main(
                env_path=env_path,
                argv=[
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "integrations",
                    "create",
                    "--payload-json",
                    '{"type":"zapier","name":"zap"}',
                ],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("refused"))
            self.assertTrue(payload.get("ok"))
            self.assertNotIn("response", payload)
            self.assertEqual(calls, [])
            self.assertIn("webhooks and custom", " ".join(str(reason) for reason in payload.get("reasons", [])))

    def test_integrations_create_allows_webhooks_type(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            def fake_request(method: str, url: str, **kwargs: Any) -> _DummyResponse:
                _ = (method, url, kwargs)
                return _DummyResponse(status=201, url=str(url), payload={"ok": True, "id": "int_123"})

            rc, payload, calls = self._run_main(
                env_path=env_path,
                argv=[
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "integrations",
                    "create",
                    "--payload-json",
                    '{"type":"webhooks","name":"safe"}',
                ],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("ok"))
            self.assertFalse(payload.get("refused", False))
            self.assertEqual(payload.get("request", {}).get("method"), "POST")
            self.assertEqual(payload.get("request", {}).get("url"), "https://api.callrail.test/v3/a/acc_default/integrations.json")
            self.assertEqual(payload.get("request", {}).get("json", {}).get("type"), "webhooks")
            self.assertEqual(len(calls), 1)
            self.assertEqual(payload.get("response", {}).get("status"), 201)

    def test_integrations_update_allows_custom_type(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            def fake_request(method: str, url: str, **kwargs: Any) -> _DummyResponse:
                _ = (method, url, kwargs)
                return _DummyResponse(status=200, url=str(url), payload={"ok": True, "id": "int_123"})

            rc, payload, calls = self._run_main(
                env_path=env_path,
                argv=[
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "integrations",
                    "update",
                    "--integration-id",
                    "int_123",
                    "--payload-json",
                    '{"type":"custom","name":"safe"}',
                ],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("ok"))
            self.assertFalse(payload.get("refused", False))
            self.assertEqual(payload.get("request", {}).get("method"), "PUT")
            self.assertEqual(
                payload.get("request", {}).get("url"), "https://api.callrail.test/v3/a/acc_default/integrations/int_123.json"
            )
            self.assertEqual(payload.get("request", {}).get("json", {}).get("type"), "custom")
            self.assertEqual(len(calls), 1)
            self.assertEqual(payload.get("response", {}).get("status"), 200)

    def test_trackers_create_session_refuses_wrong_type(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            def fake_request(**_kwargs: Any) -> Any:
                self.fail("should not be called when tracker payload type is wrong")

            rc, payload, calls = self._run_main(
                env_path=env_path,
                argv=[
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "trackers",
                    "create-session",
                    "--payload-json",
                    '{"type":"source","name":"lead"}',
                ],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("refused"))
            self.assertTrue(payload.get("ok"))
            self.assertNotIn("response", payload)
            self.assertEqual(calls, [])
            self.assertIn("requires payload.type 'session'", " ".join(str(reason) for reason in payload.get("reasons", [])))

    def test_trackers_create_session_sets_type_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            def fake_request(method: str, url: str, **kwargs: Any) -> _DummyResponse:
                _ = (method, url)
                return _DummyResponse(status=201, url=str(url), payload={"id": "trk_123"})

            rc, payload, calls = self._run_main(
                env_path=env_path,
                argv=[
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "trackers",
                    "create-session",
                    "--payload-json",
                    "{}",
                ],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("ok"))
            self.assertFalse(payload.get("refused", False))
            self.assertEqual(payload.get("request", {}).get("json", {}).get("type"), "session")
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0][1], "https://api.callrail.test/v3/a/acc_default/trackers.json")

    def test_trackers_update_source_refuses_wrong_type(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            def fake_request(**_kwargs: Any) -> Any:
                self.fail("should not be called when tracker payload type is wrong")

            rc, payload, calls = self._run_main(
                env_path=env_path,
                argv=[
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "trackers",
                    "update-source",
                    "--tracker-id",
                    "trk_123",
                    "--payload-json",
                    '{"type":"session","name":"changed"}',
                ],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("refused"))
            self.assertTrue(payload.get("ok"))
            self.assertNotIn("response", payload)
            self.assertEqual(calls, [])
            self.assertIn(
                "only supports existing source trackers",
                " ".join(str(reason) for reason in payload.get("reasons", [])),
            )

    def test_trackers_update_source_allows_missing_type_without_injecting_one(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            def fake_request(method: str, url: str, **kwargs: Any) -> _DummyResponse:
                _ = (method, url)
                return _DummyResponse(status=200, url=str(url), payload={"id": "trk_123"})

            rc, payload, calls = self._run_main(
                env_path=env_path,
                argv=[
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "trackers",
                    "update-source",
                    "--tracker-id",
                    "trk_123",
                    "--payload-json",
                    "{}",
                ],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("ok"))
            self.assertFalse(payload.get("refused", False))
            self.assertNotIn("type", payload.get("request", {}).get("json", {}))
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0][1], "https://api.callrail.test/v3/a/acc_default/trackers/trk_123.json")

    def test_tags_create_dry_run_writes_plan_out_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            plan_path = Path(td) / "plan.json"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            def fake_request(**_kwargs: Any) -> Any:
                self.fail("should not be called during dry-run plan generation")

            rc, payload, calls = self._run_main(
                env_path=env_path,
                argv=[
                    "--plan-out",
                    str(plan_path),
                    "tags",
                    "create",
                    "--payload-json",
                    '{"name":"VIP Lead","color":"blue"}',
                ],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertEqual(calls, [])
            self.assertTrue(payload.get("dry_run"))
            self.assertEqual(payload.get("plan_out"), str(plan_path))
            self.assertTrue(plan_path.exists())
            plan_obj = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(plan_obj.get("command"), "tags create")
            self.assertEqual(
                plan_obj.get("request", {}).get("url"),
                "https://api.callrail.test/v3/a/acc_default/tags.json",
            )

    def test_tags_create_apply_with_matching_plan_in_writes_receipt_out_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            plan_path = Path(td) / "plan.json"
            receipt_path = Path(td) / "receipt.json"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            plan_obj = {
                "command": "tags create",
                "env_fingerprint": "https://api.callrail.test",
                "request": {
                    "method": "POST",
                    "url": "https://api.callrail.test/v3/a/acc_default/tags.json",
                    "json": {"name": "VIP Lead", "color": "blue"},
                },
            }
            plan_path.write_text(json.dumps(plan_obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            def fake_request(method: str, url: str, **kwargs: Any) -> _DummyResponse:
                _ = (method, url, kwargs)
                return _DummyResponse(status=201, url=str(url), payload={"id": "tag_123", "name": "VIP Lead", "color": "blue"})

            rc, payload, calls = self._run_main(
                env_path=env_path,
                argv=[
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "--plan-in",
                    str(plan_path),
                    "--receipt-out",
                    str(receipt_path),
                    "tags",
                    "create",
                    "--payload-json",
                    '{"name":"VIP Lead","color":"blue"}',
                ],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("ok"))
            self.assertFalse(payload.get("refused", False))
            self.assertEqual(len(calls), 1)
            self.assertEqual(payload.get("receipt_out"), str(receipt_path))
            self.assertTrue(receipt_path.exists())
            receipt_obj = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt_obj.get("command"), "tags create")
            self.assertEqual(receipt_obj.get("response", {}).get("status"), 201)

    def test_tags_create_apply_refuses_when_plan_in_request_does_not_match(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            plan_path = Path(td) / "plan.json"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            plan_obj = {
                "command": "tags create",
                "env_fingerprint": "https://api.callrail.test",
                "request": {
                    "method": "POST",
                    "url": "https://api.callrail.test/v3/a/acc_default/tags.json",
                    "json": {"name": "Different", "color": "blue"},
                },
            }
            plan_path.write_text(json.dumps(plan_obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            def fake_request(**_kwargs: Any) -> Any:
                self.fail("should not be called when plan-in request does not match current request")

            rc, payload, calls = self._run_main(
                env_path=env_path,
                argv=[
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "--plan-in",
                    str(plan_path),
                    "tags",
                    "create",
                    "--payload-json",
                    '{"name":"VIP Lead","color":"blue"}',
                ],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("refused"))
            self.assertTrue(payload.get("ok"))
            self.assertEqual(calls, [])
            self.assertIn("plan request json", " ".join(str(reason) for reason in payload.get("reasons", [])))

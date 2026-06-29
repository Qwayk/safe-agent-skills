from __future__ import annotations

import argparse
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from gemini_api_tool import gemini_commands
from gemini_api_tool.cli import main
from gemini_api_tool.gemini_runtime import GeminiClient, execute_operation
from gemini_api_tool.operation_registry import OPERATION_BY_COMMAND, OPERATIONS


class GeminiOperationRegistryTests(unittest.TestCase):
    def test_registry_accounts_for_official_discovery_operations(self) -> None:
        v1beta = [op for op in OPERATIONS if "v1beta" in op.versions]
        v1 = [op for op in OPERATIONS if "v1" in op.versions]

        self.assertEqual(79, len(v1beta))
        self.assertEqual(32, len(v1))
        self.assertIn(("models", "generate-content"), OPERATION_BY_COMMAND)
        self.assertIn(("file-search-stores-documents", "list"), OPERATION_BY_COMMAND)
        self.assertIn(("tuned-models-operations", "cancel"), OPERATION_BY_COMMAND)

    def test_parser_has_named_commands_and_no_raw_bridge(self) -> None:
        parser = argparse.ArgumentParser(prog="gemini-api-tool")
        sub = parser.add_subparsers(dest="cmd", required=True)
        gemini_commands.register(sub)

        help_text = parser.format_help()
        self.assertIn("models", help_text)
        self.assertIn("file-search-stores", help_text)
        self.assertNotIn("raw-request", help_text)
        self.assertNotIn("generic", help_text.lower())


class GeminiRuntimeSafetyTests(unittest.TestCase):
    def test_safe_read_builds_authenticated_request_without_printing_secret(self) -> None:
        client = GeminiClient(api_key="sk-secret-test-key", timeout_s=5)
        request = client.build_request(
            OPERATION_BY_COMMAND[("models", "get")],
            path_values={"name": "models/gemini-3.5-flash"},
            query_values={},
            body=None,
        )

        self.assertEqual("GET", request.method)
        self.assertEqual("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash", request.url)
        self.assertEqual("sk-secret-test-key", request.headers["x-goog-api-key"])
        self.assertNotIn("sk-secret-test-key", json.dumps(request.redacted(), sort_keys=True))

    def test_state_changing_operation_creates_plan_before_apply(self) -> None:
        op = OPERATION_BY_COMMAND[("cached-contents", "delete")]
        result = execute_operation(
            op,
            client=GeminiClient(api_key="secret", timeout_s=5),
            path_values={"name": "cachedContents/abc"},
            query_values={},
            body=None,
            media_file=None,
            apply=False,
            yes=False,
            ack_no_snapshot=False,
            ack_irreversible=False,
            plan_in=None,
            receipt_out=None,
        )

        self.assertTrue(result["ok"])
        self.assertTrue(result["dry_run"])
        self.assertEqual("review_required", result["status"])
        self.assertEqual("generativelanguage.cachedContents.delete", result["plan"]["operation_id"])
        self.assertIn("no_snapshot_available", result["plan"]["warnings"])

    def test_state_changing_apply_requires_reviewed_plan_and_acknowledgement(self) -> None:
        op = OPERATION_BY_COMMAND[("cached-contents", "delete")]
        result = execute_operation(
            op,
            client=GeminiClient(api_key="secret", timeout_s=5),
            path_values={"name": "cachedContents/abc"},
            query_values={},
            body=None,
            media_file=None,
            apply=True,
            yes=True,
            ack_no_snapshot=False,
            ack_irreversible=False,
            plan_in=None,
            receipt_out=None,
        )

        self.assertFalse(result["ok"])
        self.assertTrue(result["refused"])
        self.assertIn("--plan-in", result["error"])

    def test_apply_uses_reviewed_plan_and_writes_receipt(self) -> None:
        op = OPERATION_BY_COMMAND[("cached-contents", "delete")]
        plan = {
            "operation_id": op.operation_id,
            "method": "DELETE",
            "url": "https://generativelanguage.googleapis.com/v1beta/cachedContents/abc",
            "path_values": {"name": "cachedContents/abc"},
            "query_values": {},
            "body": None,
            "warnings": ["no_snapshot_available"],
        }
        tmp = Path(self.id().replace(".", "_"))
        plan_path = tmp.with_suffix(".plan.json")
        receipt_path = tmp.with_suffix(".receipt.json")
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        try:
            client = GeminiClient(api_key="secret", timeout_s=5)
            client.send = Mock(return_value={"ok": True, "status_code": 200, "json": {"name": "cachedContents/abc"}})  # type: ignore[method-assign]

            result = execute_operation(
                op,
                client=client,
                path_values={"name": "cachedContents/abc"},
                query_values={},
                body=None,
                media_file=None,
                apply=True,
                yes=True,
                ack_no_snapshot=True,
                ack_irreversible=True,
                plan_in=str(plan_path),
                receipt_out=str(receipt_path),
            )

            self.assertTrue(result["ok"])
            self.assertFalse(result["dry_run"])
            self.assertTrue(receipt_path.exists())
            self.assertNotIn("secret", receipt_path.read_text(encoding="utf-8"))
        finally:
            plan_path.unlink(missing_ok=True)
            receipt_path.unlink(missing_ok=True)

    def test_apply_refuses_when_body_differs_from_reviewed_plan(self) -> None:
        op = OPERATION_BY_COMMAND[("cached-contents", "patch")]
        plan = {
            "operation_id": op.operation_id,
            "method": "PATCH",
            "url": "https://generativelanguage.googleapis.com/v1beta/cachedContents/abc",
            "path_values": {"name": "cachedContents/abc"},
            "query_values": {},
            "body": {"ttl": "60s"},
            "media_file": None,
            "warnings": ["no_snapshot_available"],
        }
        tmp = Path(self.id().replace(".", "_"))
        plan_path = tmp.with_suffix(".plan.json")
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        try:
            result = execute_operation(
                op,
                client=GeminiClient(api_key="secret", timeout_s=5),
                path_values={"name": "cachedContents/abc"},
                query_values={},
                body={"ttl": "120s"},
                media_file=None,
                apply=True,
                yes=True,
                ack_no_snapshot=True,
                ack_irreversible=False,
                plan_in=str(plan_path),
                receipt_out=None,
            )

            self.assertFalse(result["ok"])
            self.assertTrue(result["refused"])
            self.assertIn("reviewed plan", result["error"])
        finally:
            plan_path.unlink(missing_ok=True)

    def test_media_upload_uses_official_simple_upload_path(self) -> None:
        client = GeminiClient(api_key="secret", timeout_s=5)
        request = client.build_request(
            OPERATION_BY_COMMAND[("media", "upload-to-file-search-store")],
            path_values={"fileSearchStoreName": "fileSearchStores/store-123"},
            query_values={},
            body={"file": {"displayName": "example.pdf"}},
            media_file="example.pdf",
        )

        self.assertEqual(
            "https://generativelanguage.googleapis.com/upload/v1beta/fileSearchStores/store-123:uploadToFileSearchStore",
            request.url,
        )
        self.assertEqual("multipart", request.params["uploadType"])

    def test_media_upload_without_metadata_uses_raw_media_protocol(self) -> None:
        client = GeminiClient(api_key="secret", timeout_s=5)
        request = client.build_request(
            OPERATION_BY_COMMAND[("media", "upload")],
            path_values={},
            query_values={},
            body=None,
            media_file="example.pdf",
        )

        self.assertEqual("https://generativelanguage.googleapis.com/upload/v1beta/files", request.url)
        self.assertEqual("media", request.params["uploadType"])

    def test_metadata_media_upload_sends_multipart_related_body(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            media_path = Path(td) / "example.txt"
            media_path.write_bytes(b"hello gemini")
            client = GeminiClient(api_key="secret", timeout_s=5)
            request = client.build_request(
                OPERATION_BY_COMMAND[("media", "upload")],
                path_values={},
                query_values={},
                body={"file": {"displayName": "example.txt"}},
                media_file=str(media_path),
            )
            fake_response = Mock()
            fake_response.status_code = 200
            fake_response.url = request.url
            fake_response.json.return_value = {"file": {"name": "files/example"}}

            with patch(
                "gemini_api_tool.gemini_runtime.requests.request",
                return_value=fake_response,
            ) as request_mock:
                result = client.send(request)

            self.assertTrue(result["ok"])
            kwargs = request_mock.call_args.kwargs
            self.assertNotIn("files", kwargs)
            self.assertEqual("secret", kwargs["headers"]["x-goog-api-key"])
            self.assertRegex(
                kwargs["headers"]["Content-Type"],
                r"^multipart/related; boundary=gemini-api-tool-[0-9a-f]+$",
            )

            body = kwargs["data"]
            self.assertIsInstance(body, bytes)
            metadata_at = body.index(b'{"file":{"displayName":"example.txt"}}')
            media_at = body.index(b"hello gemini")
            self.assertLess(metadata_at, media_at)
            self.assertIn(b"Content-Type: application/json; charset=UTF-8", body)
            self.assertIn(b"Content-Type: text/plain", body)

    def test_documented_irreversible_ack_after_subcommand_is_accepted_with_mocked_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env_path = root / ".env"
            plan_path = root / "plan.json"
            receipt_path = root / "receipt.json"
            env_path.write_text(
                "GEMINI_API_KEY=replace-with-your-local-key\n"
                "GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com\n",
                encoding="utf-8",
            )
            plan_path.write_text(
                json.dumps(
                    {
                        "operation_id": "generativelanguage.cachedContents.delete",
                        "method": "DELETE",
                        "url": "https://generativelanguage.googleapis.com/v1beta/cachedContents/example",
                        "path_values": {"name": "cachedContents/example"},
                        "query_values": {},
                        "body": None,
                        "media_file": None,
                    }
                ),
                encoding="utf-8",
            )

            buf = io.StringIO()
            fake_response = Mock()
            fake_response.status_code = 200
            fake_response.url = "https://generativelanguage.googleapis.com/v1beta/cachedContents/example"
            fake_response.json.return_value = {"name": "cachedContents/example"}

            with patch("gemini_api_tool.gemini_runtime.requests.request", return_value=fake_response) as request_mock:
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "--apply",
                            "--yes",
                            "--plan-in",
                            str(plan_path),
                            "--receipt-out",
                            str(receipt_path),
                            "cached-contents",
                            "delete",
                            "--name",
                            "cachedContents/example",
                            "--ack-no-snapshot",
                            "--ack-irreversible",
                        ]
                    )

            request_mock.assert_called_once()
            self.assertEqual(0, rc)
            self.assertTrue(receipt_path.exists())
            self.assertNotIn("replace-with-your-local-key", receipt_path.read_text(encoding="utf-8"))
            self.assertNotIn("unrecognized arguments", buf.getvalue())

    def test_apply_shaped_cli_refuses_mismatched_plan_before_network(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env_path = root / ".env"
            plan_path = root / "plan.json"
            receipt_path = root / "receipt.json"
            env_path.write_text(
                "GEMINI_API_KEY=replace-with-your-local-key\n"
                "GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com\n",
                encoding="utf-8",
            )
            plan_path.write_text(
                json.dumps(
                    {
                        "operation_id": "generativelanguage.cachedContents.delete",
                        "method": "DELETE",
                        "url": "https://generativelanguage.googleapis.com/v1beta/cachedContents/different",
                        "path_values": {"name": "cachedContents/different"},
                        "query_values": {},
                        "body": None,
                        "media_file": None,
                    }
                ),
                encoding="utf-8",
            )

            buf = io.StringIO()
            with patch("gemini_api_tool.gemini_runtime.requests.request") as request_mock:
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "--apply",
                            "--yes",
                            "--plan-in",
                            str(plan_path),
                            "--receipt-out",
                            str(receipt_path),
                            "cached-contents",
                            "delete",
                            "--name",
                            "cachedContents/example",
                            "--ack-no-snapshot",
                            "--ack-irreversible",
                        ]
                    )

            request_mock.assert_not_called()
            output = json.loads(buf.getvalue())
            self.assertEqual(0, rc)
            self.assertTrue(output["refused"])
            self.assertIn("reviewed plan", output["error"])

    def test_public_example_outputs_do_not_include_local_paths(self) -> None:
        examples_root = Path("docs/examples")
        leaked: list[str] = []
        for path in examples_root.rglob("*.json"):
            text = path.read_text(encoding="utf-8")
            if any(marker in text for marker in ("/home/ubuntu", "/Users/", "api-tools-for-ai-agents")):
                leaked.append(str(path))

        self.assertEqual([], leaked)


if __name__ == "__main__":
    unittest.main()

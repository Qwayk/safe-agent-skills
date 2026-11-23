from __future__ import annotations

import argparse
import io
import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from pathlib import Path
from threading import Event
from unittest.mock import Mock, patch

from requests.exceptions import ReadTimeout

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
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            args = ["cached-contents", "delete", "--name", "cachedContents/example"]
            plan = root / "plan.json"
            receipt = root / "receipt.json"
            code, result = self.run_cli(root, ["--plan-out", str(plan), *args])
            self.assertEqual(0, code)
            self.assertTrue(result["dry_run"])

            apply = ["--plan-in", str(plan), "--apply", "--yes", "--receipt-out", str(receipt)]
            with patch("gemini_api_tool.gemini_runtime.requests.request", return_value=self.fake_reply()) as send:
                code, result = self.run_cli(root, [
                    *apply, *args, "--ack-no-snapshot", "--ack-irreversible",
                ])
                send.assert_called_once()
            self.assertEqual(0, code)
            self.assertTrue(result["applied"])
            self.assertEqual(result["plan_id"], json.loads(plan.read_text())["plan_id"])
            self.assertNotIn("fake-gemini-key", receipt.read_text())

    def test_apply_refuses_when_body_differs_from_reviewed_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            args = ["cached-contents", "patch", "--name", "cachedContents/example"]
            plan = root / "plan.json"
            with patch("gemini_api_tool.gemini_runtime.requests.request") as send:
                code, result = self.run_cli(root, ["--plan-out", str(plan), *args, "--request-json", '{"ttl":"60s"}'])
                self.assertEqual(0, code)
                self.assertTrue(result["dry_run"])
                code, result = self.run_cli(root, [
                    "--plan-in", str(plan), "--apply", "--yes", "--ack-spend-money",
                    *args, "--request-json", '{"ttl":"120s"}', "--ack-no-snapshot",
                ])
                send.assert_not_called()
            self.assertEqual(0, code)
            self.assertTrue(result["refused"])
            self.assertIn("reviewed plan", result["error"])

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

    def run_cli(self, root: Path, args: list[str], *, key: str = "fake-gemini-key") -> tuple[int, dict]:
        out = io.StringIO()
        with patch.dict("os.environ", {"GEMINI_API_KEY": key}, clear=True), redirect_stdout(out):
            code = main(["--output", "json", "--env-file", str(root / "settings.env"), *args])
        return code, json.loads(out.getvalue())

    def fake_reply(self) -> Mock:
        reply = Mock()
        reply.status_code = 200
        reply.url = "https://generativelanguage.googleapis.com/v1beta/mock"
        reply.json.return_value = {}
        return reply

    def test_paid_requests_need_approval_and_reads_still_send(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with patch("gemini_api_tool.gemini_runtime.requests.request", return_value=self.fake_reply()) as send:
                for method in ("generate-content", "stream-generate-content", "embed-content", "predict"):
                    args = ["models", method, "--model", "models/example", "--request-json", "{}"]
                    _, denied = self.run_cli(root, args)
                    self.assertTrue(denied["refused"])
                    self.assertIn("--ack-spend-money", denied["error"])
                    send.assert_not_called()
                code, result = self.run_cli(root, ["models", "list"])
                self.assertEqual(0, code)
                self.assertTrue(result["ok"])
                code, result = self.run_cli(root, [
                    "models", "count-tokens", "--model", "models/example", "--request-json", "{}",
                ])
                self.assertEqual(0, code)
                self.assertTrue(result["ok"])
                code, result = self.run_cli(root, [
                    "models", "generate-content", "--model", "models/example",
                    "--request-json", "{}", "--ack-spend-money",
                ])
                self.assertEqual(0, code)
                self.assertTrue(result["ok"])
                self.assertEqual(3, send.call_count)

    def test_paid_batch_needs_both_a_saved_plan_and_spending_approval(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = root / "plan.json"
            args = ["models", "batch-generate-content", "--model", "models/example", "--request-json", "{}"]
            with patch("gemini_api_tool.gemini_runtime.requests.request", return_value=self.fake_reply()) as send:
                _, preview = self.run_cli(root, ["--plan-out", str(plan), *args])
                self.assertIn("can_cost_money", preview["plan"]["warnings"])
                self.assertIn("no_snapshot_available", preview["plan"]["warnings"])
                _, missing_plan = self.run_cli(root, ["--apply", "--yes", "--ack-spend-money", *args])
                self.assertIn("--plan-in", missing_plan["error"])
                apply = ["--apply", "--yes", "--plan-in", str(plan), *args, "--ack-no-snapshot"]
                _, missing_spend = self.run_cli(root, apply)
                self.assertIn("--ack-spend-money", missing_spend["error"])
                send.assert_not_called()
                _, result = self.run_cli(root, [*apply, "--ack-spend-money"])
                self.assertTrue(result["applied"])
                send.assert_called_once()

    def test_upload_binds_bytes_and_key_and_uses_plan_only_once(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            media = root / "sample.txt"
            media.write_bytes(b"reviewed bytes")
            plan = root / "plan.json"
            args = ["media", "upload", "--media-file", str(media)]
            apply = ["--plan-in", str(plan), "--apply", "--yes", *args, "--ack-no-snapshot"]
            with patch("gemini_api_tool.gemini_runtime.requests.request", return_value=self.fake_reply()) as send:
                _, preview = self.run_cli(root, ["--plan-out", str(plan), *args])
                self.assertTrue(preview["dry_run"])
                self.assertNotIn("reviewed bytes", plan.read_text())

                _, result = self.run_cli(root, apply, key="another-key")
                self.assertTrue(result["refused"])
                media.write_bytes(b"changed bytes")
                _, result = self.run_cli(root, apply)
                self.assertTrue(result["refused"])
                send.assert_not_called()

                media.write_bytes(b"reviewed bytes")
                _, result = self.run_cli(root, apply)
                self.assertTrue(result["applied"])
                self.assertEqual(b"reviewed bytes", send.call_args.kwargs["data"])
                copied = root / "copied.json"
                copied.write_bytes(plan.read_bytes())
                _, result = self.run_cli(root, ["--plan-in", str(copied), *apply[2:]])
                self.assertIn("already attempted", result["error"])
                send.assert_called_once()

    def test_apply_shaped_cli_refuses_mismatched_targets_and_old_plans(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            args = ["cached-contents", "delete", "--name", "cachedContents/example"]
            plan = root / "plan.json"
            with patch("gemini_api_tool.gemini_runtime.requests.request") as send:
                self.run_cli(root, ["--plan-out", str(plan), *args])
                apply = ["--plan-in", str(plan), "--apply", "--yes"]
                flags = ["--ack-no-snapshot", "--ack-irreversible"]
                _, missing_ack = self.run_cli(root, [*apply, *args, "--ack-no-snapshot"])
                self.assertIn("--ack-irreversible", missing_ack["error"])
                _, wrong_target = self.run_cli(root, [*apply, *args[:-1], "cachedContents/other", *flags])
                self.assertIn("reviewed plan", wrong_target["error"])
                plan.write_text('{"operation_id":"generativelanguage.cachedContents.delete"}')
                _, old_plan = self.run_cli(root, [*apply, *args, *flags])
                self.assertIn("new plan", old_plan["error"])
                send.assert_not_called()

    def test_lost_reply_leaves_receipt_and_blocks_resend(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = root / "plan.json"
            receipt = root / "receipt.json"
            args = ["cached-contents", "delete", "--name", "cachedContents/example"]
            apply = ["--plan-in", str(plan), "--apply", "--yes", "--receipt-out", str(receipt)]
            with patch("gemini_api_tool.gemini_runtime.requests.request", side_effect=ReadTimeout) as send:
                self.run_cli(root, ["--plan-out", str(plan), *args])
                code, result = self.run_cli(root, [*apply, *args, "--ack-no-snapshot", "--ack-irreversible"])
                self.assertEqual(1, code)
                self.assertIsNone(result["applied"])
                self.assertEqual("outcome_unknown", json.loads(receipt.read_text())["status"])
                _, blocked = self.run_cli(root, [*apply, *args, "--ack-no-snapshot", "--ack-irreversible"])
                self.assertIn("already attempted", blocked["error"])
                send.assert_called_once()

    def test_two_applies_of_the_same_plan_only_send_once(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            plan = str(Path(td) / "plan.json")
            client = GeminiClient(api_key="fake-gemini-key", timeout_s=5)
            op = OPERATION_BY_COMMAND[("cached-contents", "delete")]
            args = {
                "client": client,
                "path_values": {"name": "cachedContents/example"},
                "query_values": {},
                "body": None,
                "media_file": None,
                "yes": True,
                "ack_no_snapshot": True,
                "ack_irreversible": True,
                "receipt_out": None,
            }
            execute_operation(op, **args, apply=False, plan_out=plan, plan_in=None)
            sending = Event()
            finish = Event()

            def reply(_request):
                sending.set()
                if not finish.wait(5):
                    raise AssertionError("Test did not finish the first send")
                return {"ok": True}

            with patch.object(client, "send", side_effect=reply) as send, ThreadPoolExecutor() as workers:
                first = workers.submit(execute_operation, op, **args, apply=True, plan_in=plan)
                try:
                    self.assertTrue(sending.wait(5))
                    second = execute_operation(op, **args, apply=True, plan_in=plan)
                    self.assertTrue(second["refused"])
                    self.assertIn("already attempted", second["error"])
                finally:
                    finish.set()
                self.assertTrue(first.result()["applied"])
                send.assert_called_once()

    def test_plan_and_run_logs_omit_inline_request_text(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            private_text = "example private prompt"
            audit = root / "audit.jsonl"
            with patch("gemini_api_tool.gemini_runtime.requests.request") as send:
                _, result = self.run_cli(root, [
                    "--log-file", str(audit), "cached-contents", "create",
                    "--request-json", json.dumps({"displayName": private_text}),
                ])
                send.assert_not_called()
            self.assertNotIn(private_text, json.dumps(result))
            self.assertTrue(audit.exists())
            self.assertTrue(Path(result["runs_index"]).exists())
            for path in [audit, *root.joinpath(".state").rglob("*")]:
                if path.is_file():
                    self.assertNotIn(private_text, path.read_text())

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

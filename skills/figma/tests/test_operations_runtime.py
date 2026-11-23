from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from figma_safe_agent_cli.cli import main
from figma_safe_agent_cli.http import HttpResponse
from figma_safe_agent_cli.operation_specs import list_operations


class TestOperationsRuntime(unittest.TestCase):
    def _run(self, *args: str) -> tuple[int, dict]:
        output = io.StringIO()
        with redirect_stdout(output):
            rc = main(["--no-artifacts", *args])
        return rc, json.loads(output.getvalue())

    def _write_env(self, path: Path) -> None:
        path.write_text(
            "\n".join(
                [
                    "FIGMA_BASE_URL=http://example.invalid",
                    "FIGMA_AUTH_MODE=personal",
                    "FIGMA_ACCESS_TOKEN=tok-test",
                    "FIGMA_TIMEOUT_S=30",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    def _assert_blocked_before_state(self, plan: dict[str, object]) -> None:
        before_state = plan["before_state"]
        self.assertIsInstance(before_state, dict)
        self.assertIs(before_state["required"], True)
        self.assertIs(before_state["supported"], False)
        self.assertEqual(before_state["status"], "no_snapshot_available")
        self.assertIsNone(before_state["saved_path"])
        self.assertIsNone(before_state["provider_backup_id"])
        self.assertEqual(plan["verification_plan"]["type"], "best_effort_after_apply")

    def test_operations_list_and_show(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["operations", "list", "--area", "files", "--method", "GET"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertGreater(payload["count"], 0)
        self.assertTrue(all(item["area"] == "files" for item in payload["operations"]))
        self.assertTrue(all(item["method"] == "GET" for item in payload["operations"]))

        buf2 = io.StringIO()
        with redirect_stdout(buf2):
            rc2 = main(["operations", "show", "files", "get-file"])
        self.assertEqual(rc2, 0)
        payload2 = json.loads(buf2.getvalue())
        self.assertTrue(payload2["ok"])
        self.assertEqual(payload2["operation"]["area"], "files")
        self.assertEqual(payload2["operation"]["op_key"], "get-file")
        self.assertEqual(payload2["operation"]["method"], "GET")

    def test_operations_run_is_refused(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["operations", "run", "files", "get-file", "--file-key", "file_123"])
        self.assertNotEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])

    def test_generic_execution_aliases_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            self._write_env(env_path)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc_path_alias = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations",
                        "comments",
                        "get-comments",
                        "--path-param",
                        "unused",
                    ]
                )
            self.assertNotEqual(rc_path_alias, 0)

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc_query_alias = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations",
                        "comments",
                        "get-comments",
                        "--file-key",
                        "file_123",
                        "--query",
                        "ids=1",
                    ]
            )
            self.assertNotEqual(rc_query_alias, 0)

    def test_optional_query_flags_are_forwarded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            self._write_env(env_path)
            captured: dict[str, dict[str, str] | None] = {}

            class FakeHttpClient:
                def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str) -> None:
                    _ = (timeout_s, verbose, user_agent)

                def request(
                    self,
                    method: str,
                    url: str,
                    *,
                    headers: dict[str, str],
                    params: dict[str, str] | None,
                    json_body: dict | None,
                    data: dict | None = None,
                    retries: int = 0,
                    retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
                ) -> HttpResponse:
                    _ = (method, url, headers, data, retries, retry_on)
                    captured["query"] = params or {}
                    return HttpResponse(
                        status=200,
                        headers={"content-type": "application/json"},
                        body=b'{"ok":true}',
                        url=url,
                    )

            def run(cmd: list[str]) -> dict[str, str]:
                captured["query"] = None
                with patch("figma_safe_agent_cli.commands.operations.HttpClient", FakeHttpClient):
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = main(["--env-file", str(env_path), *cmd])
                    self.assertEqual(rc, 0)
                    payload = json.loads(buf.getvalue())
                    self.assertFalse(payload["dry_run"])
                self.assertIsNotNone(captured["query"])
                return payload["request"]["query"]

            self.assertEqual(
                run(
                    [
                        "operations",
                        "files",
                        "get-file",
                        "--file-key",
                        "file_123",
                        "--version-id",
                        "3",
                        "--ids",
                        "1,2",
                        "--depth",
                        "2",
                        "--geometry",
                        "paths",
                        "--plugin-data",
                        "pluginMeta",
                        "--branch-data",
                        "true",
                    ]
                ),
                {"version": "3", "ids": "1,2", "depth": "2", "geometry": "paths", "plugin_data": "pluginMeta", "branch_data": "true"},
            )
            self.assertEqual(
                run(
                    [
                        "operations",
                        "webhooks",
                        "get-webhooks",
                        "--context",
                        "file",
                        "--context-id",
                        "file_123",
                        "--plan-api-id",
                        "plan_1",
                        "--cursor",
                        "cur_1",
                    ]
                ),
                {
                    "context": "file",
                    "context_id": "file_123",
                    "plan_api_id": "plan_1",
                    "cursor": "cur_1",
                },
            )
            self.assertEqual(
                run(
                    [
                        "operations",
                        "oembed",
                        "get-oembed",
                        "--url",
                        "https://www.figma.com/file/abc/Example",
                        "--maxwidth",
                        "640",
                        "--maxheight",
                        "480",
                    ]
                ),
                {"url": "https://www.figma.com/file/abc/Example", "maxwidth": "640", "maxheight": "480"},
            )

    def test_optional_query_flags_are_declared_in_specs(self) -> None:
        specs = {
            ("files", "get-file"): {"version", "ids", "depth", "geometry", "plugin_data", "branch_data"},
            ("comments", "get-comment-reactions"): {"cursor"},
            ("activity-logs", "get-activity-logs"): {"events", "start_time", "end_time", "limit", "order"},
            ("discovery", "get-discovery"): {"end_date", "file_ttl_in_seconds"},
        }
        for (area, op_key), expected in specs.items():
            op = next(
                (s for s in list_operations(area=area, include_writes=True) if s.op_key == op_key),
                None,
            )
            self.assertIsNotNone(op)
            opt_set = set(op.optional_query_params) if op else set()
            self.assertTrue(expected.issubset(opt_set), f"{area}:{op_key} missing: {expected - opt_set}")

    def test_read_operation_runs_with_expected_request(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            self._write_env(env_path)

            captured: dict[str, object] = {}

            class FakeHttpClient:
                def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str) -> None:
                    _ = (timeout_s, verbose, user_agent)

                def request(
                    self,
                    method: str,
                    url: str,
                    *,
                    headers: dict[str, str],
                    params: dict[str, str] | None,
                    json_body: dict | None,
                    data: dict | None = None,
                    retries: int = 0,
                    retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
                ) -> HttpResponse:
                    captured["method"] = method
                    captured["url"] = url
                    captured["headers"] = headers
                    captured["params"] = params or {}
                    captured["body"] = json_body
                    return HttpResponse(
                        status=200,
                        headers={"content-type": "application/json"},
                        body=b'{"ok":true}',
                        url=url,
                    )

            with patch("figma_safe_agent_cli.commands.operations.HttpClient", FakeHttpClient):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "operations",
                            "files",
                            "get-file-nodes",
                            "--file-key",
                            "file_123",
                            "--ids",
                            "1",
                        ]
                    )
                self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["ok"], True)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["request"]["method"], "GET")
            self.assertEqual(payload["request"]["path"], "/v1/files/file_123/nodes")
            self.assertEqual(payload["request"]["query"], {"ids": "1"})
            self.assertEqual(payload["response_status"], 200)
            self.assertEqual(
                payload["verification_note"],
                "Read response is the verification signal for this operation.",
            )

            self.assertEqual(captured["method"], "GET")
            self.assertEqual(captured["url"], "http://example.invalid/v1/files/file_123/nodes")
            self.assertEqual(captured["params"], {"ids": "1"})
            self.assertIn("X-Figma-Token", captured["headers"])

    def test_write_operation_is_dry_run_until_apply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            self._write_env(env_path)

            body_path = Path(d) / "body.json"
            body_path.write_text('{"comment":"hello"}', encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "operations",
                            "comments",
                            "post-comment",
                            "--file-key",
                            "file_123",
                            "--body-json-file",
                            str(body_path),
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["operation"]["op_key"], "post-comment")
            self.assertEqual(payload["request"]["method"], "POST")
            self.assertIn("plan", payload)
            self.assertEqual(payload["plan"]["operation_id"], "comments:post-comment")
            self.assertEqual(payload["plan"]["env_fingerprint"], "http://example.invalid|personal")
            self._assert_blocked_before_state(payload["plan"])

    def test_write_operation_apply_refuses_without_before_state(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            self._write_env(env_path)

            body_path = Path(d) / "body.json"
            body_path.write_text('{"comment":"hello"}', encoding="utf-8")
            captured: dict[str, object] = {}

            class FakeHttpClient:
                def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str) -> None:
                    _ = (timeout_s, verbose, user_agent)

                def request(
                    self,
                    method: str,
                    url: str,
                    *,
                    headers: dict[str, str],
                    params: dict[str, str] | None,
                    json_body: dict | None,
                    data: dict | None = None,
                    retries: int = 0,
                    retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
                ) -> HttpResponse:
                    captured["method"] = method
                    captured["url"] = url
                    captured["json_body"] = json_body
                    return HttpResponse(
                        status=201,
                        headers={"content-type": "application/json"},
                        body=b'{"ok":true}',
                        url=url,
                    )

            with patch("figma_safe_agent_cli.commands.operations.HttpClient", FakeHttpClient):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--apply",
                            "--yes",
                            "operations",
                            "comments",
                            "post-comment",
                            "--file-key",
                            "file_123",
                            "--body-json-file",
                            str(body_path),
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["verification_plan"]["type"], "best_effort_after_apply")
            self.assertIn("before-state", payload["reasons"][0])
            self.assertEqual(payload["request"]["method"], "POST")
            self.assertEqual(payload["request"]["headers"], {})
            self._assert_blocked_before_state(payload["plan"])
            self.assertEqual(captured, {})

    def test_write_operation_without_readback_strategy_refuses_without_before_state(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            self._write_env(env_path)

            body_path = Path(d) / "variables_body.json"
            body_path.write_text('{"variables":[]}', encoding="utf-8")

            class FakeHttpClient:
                def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str) -> None:
                    _ = (timeout_s, verbose, user_agent)

                def request(
                    self,
                    method: str,
                    url: str,
                    *,
                    headers: dict[str, str],
                    params: dict[str, str] | None,
                    json_body: dict | None,
                    data: dict | None = None,
                    retries: int = 0,
                    retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
                ) -> HttpResponse:
                    _ = (method, url, headers, params, json_body, data, retries, retry_on)
                    return HttpResponse(
                        status=200,
                        headers={"content-type": "application/json"},
                        body=b'{"status":200,"error":false,"meta":{"tempIdToRealId":{}}}',
                        url=url,
                    )

            with patch("figma_safe_agent_cli.commands.operations.HttpClient", FakeHttpClient):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--apply",
                            "--yes",
                            "operations",
                            "variables",
                            "post-variables",
                            "--file-key",
                            "file_123",
                            "--body-json-file",
                            str(body_path),
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["refused"])
            self._assert_blocked_before_state(payload["plan"])

    def test_write_operation_plan_in_rejects_drift(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            self._write_env(env_path)

            body_path = Path(d) / "body.json"
            body_path.write_text('{"comment":"hello"}', encoding="utf-8")

            plan_path = Path(d) / "plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "request": {
                            "method": "POST",
                            "path": "/v1/files/file_123/comments",
                            "url": "http://example.invalid/v1/files/file_123/comments",
                            "query": {"unexpected": "value"},
                            "body": {"comment": "hello"},
                        }
                    }
                ),
                encoding="utf-8",
            )

            class FakeHttpClient:
                def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str) -> None:
                    _ = (timeout_s, verbose, user_agent)

                def request(
                    self,
                    method: str,
                    url: str,
                    *,
                    headers: dict[str, str],
                    params: dict[str, str] | None,
                    json_body: dict | None,
                    data: dict | None = None,
                    retries: int = 0,
                    retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
                ) -> HttpResponse:
                    return HttpResponse(
                        status=201,
                        headers={"content-type": "application/json"},
                        body=b'{"ok":true}',
                        url=url,
                    )

            with patch("figma_safe_agent_cli.commands.operations.HttpClient", FakeHttpClient):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--apply",
                            "--yes",
                            "--plan-in",
                            str(plan_path),
                            "operations",
                            "comments",
                            "post-comment",
                            "--file-key",
                            "file_123",
                            "--body-json-file",
                            str(body_path),
                        ]
                    )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertIn("Plan drift for query", payload["error"])

    def test_saved_comment_plan_requires_the_same_request_and_connection(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = root / "figma.env"
            self._write_env(env)
            body = root / "comment.json"
            body.write_text('{"message":"Please check the title."}', encoding="utf-8")
            plan = root / "plan.json"
            receipt = root / "receipt.json"
            settings = ["--env-file", str(env)]
            comment = [
                "operations", "comments", "post-comment", "--file-key", "file_123",
                "--body-json-file", str(body),
            ]
            review = [*settings, "--plan-out", str(plan), *comment]
            apply = [*settings, "--apply", "--yes", "--ack-no-snapshot"]
            reviewed = [*apply, "--plan-in", str(plan)]

            with patch("figma_safe_agent_cli.commands.operations.HttpClient") as client:
                self.assertTrue(self._run(*review)[1]["dry_run"])
                self.assertNotIn("tok-test", plan.read_text(encoding="utf-8"))
                self.assertTrue(self._run(*apply, *comment)[1]["refused"])
                for change, replacement in (("file_123", "file_456"), (str(body), str(root / "changed.json"))):
                    with self.subTest(change=change):
                        (root / "changed.json").write_text('{"message":"Different text"}', encoding="utf-8")
                        altered = [replacement if item == change else item for item in comment]
                        self.assertNotEqual(self._run(*reviewed, *altered)[0], 0)
                original_env = env.read_text(encoding="utf-8")
                env.write_text(original_env.replace("tok-test", "another-token"), encoding="utf-8")
                self.assertNotEqual(self._run(*reviewed, *comment)[0], 0)
                env.write_text(original_env, encoding="utf-8")
                client.assert_not_called()

                send = client.return_value.request
                send.side_effect = [
                    HttpResponse(200, {}, b'{"id":"comment_1"}', "https://example.invalid"),
                    HttpResponse(
                        200, {}, b'{"comments":[{"id":"comment_1","message":"Please check the title."}]}',
                        "https://example.invalid",
                    ),
                ]
                rc, result = self._run(*reviewed, "--receipt-out", str(receipt), *comment)
                self.assertEqual(rc, 0)
                self.assertIn("text matches", result["verification_note"])
                self.assertEqual(send.call_count, 2)
                saved = json.loads(receipt.read_text(encoding="utf-8"))
                self.assertTrue(saved["plan"]["no_snapshot_approval"]["approved"])
                self.assertNotIn("tok-test", receipt.read_text(encoding="utf-8"))

    def test_comment_receipts_distinguish_accepted_from_verified(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = root / "figma.env"
            self._write_env(env)
            body = root / "comment.json"
            body.write_text('{"message":"Reviewed text"}', encoding="utf-8")
            plan = root / "plan.json"
            for action, args, initial, listing, expected in (
                ("post-comment", ["--body-json-file", str(body)], b'{"id":"c1"}',
                 b'{"comments":[{"id":"c1","message":"Different text"}]}', "could not be confirmed"),
                ("delete-comment", ["--comment-id", "c1"], b"", b'{}', "usable comment list"),
                ("delete-comment", ["--comment-id", "c1"], b"", b'{"comments":[]}', "is not visible"),
            ):
                with self.subTest(action=action, listing=listing):
                    command = ["operations", "comments", action, "--file-key", "file_123", *args]
                    settings = ["--env-file", str(env)]
                    self.assertEqual(self._run(*settings, "--plan-out", str(plan), *command)[0], 0)
                    with patch("figma_safe_agent_cli.commands.operations.HttpClient") as client:
                        send = client.return_value.request
                        send.side_effect = [HttpResponse(200, {}, reply, "https://example.invalid")
                                            for reply in (initial, listing)]
                        rc, result = self._run(
                            *settings, "--apply", "--yes", "--ack-no-snapshot", "--ack-irreversible",
                            "--plan-in", str(plan), *command,
                        )
                    self.assertEqual(rc, 0)
                    self.assertIn(expected, result["verification_note"])
                    self.assertEqual(send.call_count, 2)

    def test_image_renders_report_which_nodes_got_links(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            self._write_env(env)
            images_file = Path(d) / "images.json"
            for status, images, failed in (
                ("complete", {"1:2": "https://example.invalid/a", "1:3": "https://example.invalid/b"}, []),
                ("partial", {"1:2": "https://example.invalid/a", "1:3": None}, ["1:3"]),
                ("failed", {"1:2": None}, ["1:2", "1:3"]),
            ):
                with self.subTest(status=status):
                    body = {"images": images}
                    with patch("figma_safe_agent_cli.commands.operations.HttpClient") as client:
                        client.return_value.request.return_value = HttpResponse(
                            200, {}, json.dumps(body).encode(), "https://example.invalid"
                        )
                        rc, result = self._run(
                            "--env-file", str(env), "operations", "files", "render-images",
                            "--file-key", "file_123", "--ids", "1:2,1:3", "--out", str(images_file),
                            "--overwrite",
                        )
                    self.assertEqual(rc, int(status == "failed"))
                    self.assertEqual(result["render"]["status"], status)
                    self.assertEqual(result["render"]["failed_node_ids"], failed)
                    self.assertEqual(json.loads(images_file.read_text(encoding="utf-8")), body)

    def test_discovery_requires_start_date(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            self._write_env(env_path)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations",
                        "discovery",
                        "get-discovery",
                    ]
                )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertIn("start_date", payload["error"])

    def test_payments_user_resource_requires_exactly_one_resource_id(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            self._write_env(env_path)

            class FakeHttpClient:
                def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str) -> None:
                    _ = (timeout_s, verbose, user_agent)

                def request(
                    self,
                    method: str,
                    url: str,
                    *,
                    headers: dict[str, str],
                    params: dict[str, str] | None,
                    json_body: dict | None,
                    data: dict | None = None,
                    retries: int = 0,
                    retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
                ) -> HttpResponse:
                    return HttpResponse(
                        status=200,
                        headers={"content-type": "application/json"},
                        body=b'{"ok":true}',
                        url=url,
                    )

            with patch("figma_safe_agent_cli.commands.operations.HttpClient", FakeHttpClient):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc_ok = main(
                        [
                            "--env-file",
                            str(env_path),
                            "operations",
                            "payments",
                            "get-payments-by-user-resource",
                            "--user-id",
                            "USER-1",
                            "--plugin-id",
                            "PLUGIN-1",
                        ]
                    )
            self.assertEqual(rc_ok, 0)
            payload_ok = json.loads(buf.getvalue())
            self.assertTrue(payload_ok["ok"])
            self.assertFalse(payload_ok["dry_run"])

            buf_missing = io.StringIO()
            with redirect_stdout(buf_missing):
                    rc_missing = main(
                        [
                            "--env-file",
                            str(env_path),
                            "operations",
                            "payments",
                            "get-payments-by-user-resource",
                            "--user-id",
                            "USER-1",
                        ]
                    )
            self.assertEqual(rc_missing, 1)
            payload_missing = json.loads(buf_missing.getvalue())
            self.assertFalse(payload_missing["ok"])
            self.assertIn("Missing required query group", payload_missing["error"])

            buf_multi = io.StringIO()
            with redirect_stdout(buf_multi):
                    rc_multi = main(
                        [
                            "--env-file",
                            str(env_path),
                            "operations",
                            "payments",
                            "get-payments-by-user-resource",
                            "--user-id",
                            "USER-1",
                            "--community-file-id",
                            "FILE-1",
                            "--widget-id",
                            "WIDGET-1",
                        ]
                    )
            self.assertEqual(rc_multi, 1)
            payload_multi = json.loads(buf_multi.getvalue())
            self.assertFalse(payload_multi["ok"])
            self.assertIn("Provide exactly one of query parameters", payload_multi["error"])

    def test_irreversible_writes_require_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            self._write_env(env_path)

            cases = [
                (
                    "comments",
                    "delete-comment",
                    ["--file-key", "file_123", "--comment-id", "comment_1"],
                ),
                (
                    "webhooks",
                    "delete-webhook",
                    ["--webhook-id", "webhook_1"],
                ),
                (
                    "dev-resources",
                    "delete-dev-resource",
                    ["--file-key", "file_123", "--dev-resource-id", "devres_1"],
                ),
            ]

            for area, op_key, flags in cases:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--apply",
                            "--yes",
                            "operations",
                            area,
                            op_key,
                            *flags,
                        ]
                    )
                self.assertEqual(rc, 0, msg=f"expected safe refusal for {area}:{op_key}")
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertTrue(payload["refused"])
                self.assertEqual(payload["refusal_type"], "SafetyError")
                self.assertIn("--ack-irreversible", payload["reasons"][0])

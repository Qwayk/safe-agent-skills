from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import requests

from x_api_tool.api_dispatch import build_api_call_plan
from x_api_tool.cli import main
from x_api_tool.openapi_inventory import extract_operations, load_openapi_snapshot


def _tool_root() -> Path:
    return Path(__file__).resolve().parents[1]


class TestApiCallPlanability(unittest.TestCase):
    def test_every_operation_is_plannable_offline(self) -> None:
        root = _tool_root()
        snap = root / "src/x_api_tool/official_openapi_x_api_v2.json"
        obj = load_openapi_snapshot(snap)
        ops = extract_operations(obj)

        original_request = requests.Session.request

        def _no_network(*args, **kwargs):  # type: ignore[no-untyped-def]
            raise AssertionError("Network call attempted during plan build")

        requests.Session.request = _no_network  # type: ignore[assignment]
        try:
            for op in ops:
                dummy_path = {k: "1" for k in op.required_path_params}
                plan = build_api_call_plan(
                    tool="x-api-tool",
                    tool_version="0.0.0",
                    env_fingerprint="https://api.x.com/2",
                    op=op,
                    base_url="https://api.x.com/2",
                    env_file=str(root / ".env"),
                    env_bearer_token=None,
                    auth="none",
                    path_json=json.dumps(dummy_path),
                    query_json=json.dumps({}),
                    body_json=None,
                    path_pairs=None,
                    query_pairs=None,
                    file_pairs=None,
                )
                self.assertTrue(plan["dry_run"])
                self.assertEqual(plan["operation"]["operation_id"], op.operation_id)
                self.assertIn("method", plan["operation"])
                self.assertIn("url", plan["operation"])
                self.assertIn("headers", plan)
        finally:
            requests.Session.request = original_request  # type: ignore[assignment]

    def test_safety_gates_refuse_apply_without_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("X_API_BASE_URL=https://api.x.com/2\nX_API_BEARER_TOKEN=\nX_API_TIMEOUT_S=30\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env),
                        "--apply",
                        "api",
                        "createPosts",
                        "--auth",
                        "none",
                        "--body-json",
                        "{}",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload.get("refused"))

    def test_delete_requires_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("X_API_BASE_URL=https://api.x.com/2\nX_API_BEARER_TOKEN=\nX_API_TIMEOUT_S=30\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env),
                        "--apply",
                        "--yes",
                        "api",
                        "deletePosts",
                        "--auth",
                        "none",
                        "--path",
                        "id=1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload.get("refused"))

    def test_write_apply_refuses_before_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("X_API_BASE_URL=https://api.x.com/2\nX_API_BEARER_TOKEN=\nX_API_TIMEOUT_S=30\n", encoding="utf-8")

            buf = io.StringIO()
            with patch("x_api_tool.commands.api._execute_live_http") as mock_http:
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env),
                            "--apply",
                            "--yes",
                            "api",
                            "createPosts",
                            "--auth",
                            "none",
                            "--body-json",
                            "{}",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload["verification_plan"]["status"], "best_effort_after_apply")
            self.assertFalse(mock_http.called)

    def test_post_apply_requires_a_saved_connected_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("X_API_BASE_URL=https://api.x.com/2\n", encoding="utf-8")
            buf = io.StringIO()
            with patch("x_api_tool.commands.api._execute_live_http") as mock_http, redirect_stdout(buf):
                rc = main([
                    "--env-file", str(env), "--no-artifacts", "--apply", "--yes",
                    "--ack-no-snapshot", "api", "createPosts", "--body-json", '{"text":"Sample"}',
                ])
            self.assertEqual(rc, 0)
            result = json.loads(buf.getvalue())
            self.assertTrue(result["refused"])
            self.assertIn("--plan-in", result["reasons"][0])
            mock_http.assert_not_called()

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from cloudflare_api_tool.cli import main
from cloudflare_api_tool.operation_keys import allowlisted_operation_command_by_operation_id


def _write_env(root: Path, *, token: str = "T") -> Path:
    p = root / ".env"
    p.write_text(
        "\n".join(
            [
                "CLOUDFLARE_API_BASE_URL=http://example.invalid/client/v4",
                f"CLOUDFLARE_API_TOKEN={token}",
                "CLOUDFLARE_TIMEOUT_S=30",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return p


class TestWorkersTailsTokenSensitivity(unittest.TestCase):
    def test_operations_call_plan_marks_start_tail_as_sensitive_write_result(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_operation_id("worker-tail-logs-start-tail")
            self.assertIsNotNone(cmd)
            assert cmd is not None
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations",
                        cmd.area,
                        cmd.op_key,
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "script_name=s1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["request"]["sensitivity"], "sensitive_write_result")

    def test_operations_call_apply_refuses_without_out_for_sensitive_write_result(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_operation_id("worker-tail-logs-start-tail")
            self.assertIsNotNone(cmd)
            assert cmd is not None
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "operations",
                        cmd.area,
                        cmd.op_key,
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "script_name=s1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            reasons = " ".join(payload.get("reasons") or [])
            self.assertIn("Provide --out", reasons)

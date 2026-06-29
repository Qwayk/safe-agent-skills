from __future__ import annotations

import io
import json
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock
import unittest

from zapier_safe_agent_cli.cli import _build_plan, main
from zapier_safe_agent_cli.config import load_config
from zapier_safe_agent_cli.operations import load_operations


class TestAuthAndSecrets(unittest.TestCase):
    def _env_missing(self, td: str) -> Path:
        env = Path(td) / ".env"
        env.write_text("\n".join(["ZAPIER_BASE_URL=https://api.zapier.com", "ZAPIER_TIMEOUT_S=30"]) + "\n", encoding="utf-8")
        return env

    def _env_with_secret(self, td: str) -> Path:
        env = Path(td) / ".env"
        env.write_text(
            "\n".join(
                [
                    "ZAPIER_BASE_URL=https://api.zapier.com",
                    "ZAPIER_AI_ACTIONS_BASE_URL=https://actions.zapier.com",
                    "ZAPIER_TRIGGER_INBOX_BASE_URL=https://api.zapier.com",
                    "ZAPIER_ACCESS_TOKEN=TOP_SECRET_TOKEN_123",
                    "ZAPIER_TIMEOUT_S=30",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return env

    def test_missing_auth_errors(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = self._env_missing(td)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env), "--output", "json", "auth", "check"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_secret_not_in_output_on_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = self._env_with_secret(td)
            cmd = [
                "--env-file",
                str(env),
                "--output",
                "json",
                "partner",
                "post-zaps",
                "--body-json",
                '{"name":"x"}',
            ]
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(cmd)
            payload_text = buf.getvalue()
            self.assertEqual(rc, 0)
            self.assertNotIn("TOP_SECRET_TOKEN_123", payload_text)
            payload = json.loads(payload_text)
            self.assertTrue(payload["ok"])

    def test_config_errors_return_single_redacted_json_object(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            env.write_text(
                "\n".join(
                    [
                        "ZAPIER_BASE_URL=https://api.zapier.com",
                        "ZAPIER_AI_ACTIONS_BASE_URL=https://actions.zapier.com",
                        "ZAPIER_TRIGGER_INBOX_BASE_URL=https://api.zapier.com",
                        "ZAPIER_ACCESS_TOKEN=TOP_SECRET_TOKEN_456",
                        "ZAPIER_TIMEOUT_S=not-a-number",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env), "--output", "json", "partner", "post-zaps", "--body-json", '{"name":"x"}'])

            payload_text = buf.getvalue()
            self.assertEqual(rc, 1)
            payload = json.loads(payload_text)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "RuntimeError")
            self.assertNotIn("TOP_SECRET_TOKEN_456", payload_text)
            self.assertNotIn("Traceback", payload_text)

    def test_provider_errors_return_single_redacted_json_object(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = self._env_with_secret(td)
            cfg = load_config(str(env))
            op = next(op for op in load_operations() if op.group == "partner" and op.command == "post-zaps")
            secret = "TOP_SECRET_TOKEN_123"
            body = {"name": "runtime_error", "secret": secret}
            plan = _build_plan(
                cfg=cfg,
                command="qwayk-zapier-safe-agent-cli partner post-zaps --body-json <redacted-body-json>",
                op=op,
                path_params={},
                query={},
                body=body,
                risk="high",
            )
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            with mock.patch("zapier_safe_agent_cli.cli.HttpClient.request") as req:
                req.side_effect = RuntimeError('provider failed token=TOP_SECRET_TOKEN_123 {"access_token":"TOP_SECRET_TOKEN_123"}\nbody also had TOP_SECRET_TOKEN_123')
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env),
                            "--output",
                            "json",
                            "--apply",
                            "--plan-in",
                            str(plan_path),
                            "--yes",
                            "partner",
                            "post-zaps",
                            "--body-json",
                            json.dumps(body),
                        ]
                    )

            payload_text = buf.getvalue()
            self.assertEqual(rc, 1)
            payload = json.loads(payload_text)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "RuntimeError")
            self.assertIn("***REDACTED***", str(payload.get("error", "")))
            self.assertIn("<redacted-body-json>", str(payload.get("command", "")))
            self.assertNotIn("TOP_SECRET_TOKEN_123", payload_text)
            self.assertNotIn("Traceback", payload_text)

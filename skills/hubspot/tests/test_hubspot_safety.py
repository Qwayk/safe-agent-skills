from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from hubspot_safe_agent_cli.cli import main


class _FakeHttpResponse:
    status = 200
    body = b'{"results": []}'

    def json(self) -> object:
        return {"results": []}

    def text(self) -> str:
        return self.body.decode("utf-8")


class TestHubspotSafetyGates(unittest.TestCase):
    def _env(self, root: Path) -> Path:
        env = root / ".env"
        env.write_text(
            "\n".join(
                [
                    "HUBSPOT_API_BASE_URL=http://example.invalid",
                    "HUBSPOT_ACCESS_TOKEN=token",
                    "HUBSPOT_TIMEOUT_S=30",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return env

    def test_read_command_is_no_apply_path(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._env(root)
            with patch("hubspot_safe_agent_cli.commands.hubspot.HttpClient.request", return_value=_FakeHttpResponse()):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env), "hubspot", "objects", "list", "--object-type", "contacts"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("dry_run", True))
            self.assertEqual(payload["path"], "/crm/objects/2026-03/{object_type}")

    def test_write_command_without_apply_returns_dry_run_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._env(root)
            body = root / "body.json"
            body.write_text('{"properties": {"name": "x"}}', encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env),
                        "hubspot",
                        "objects",
                        "create",
                        "--object-type",
                        "contacts",
                        "--body-file",
                        str(body),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertIn("plan", payload)
            self.assertEqual(payload["plan"].get("before_state", {}).get("required"), True)
            self.assertEqual(payload["plan"].get("before_state", {}).get("supported"), False)
            self.assertEqual(payload["plan"].get("rollback_plan", {}).get("possible"), False)
            self.assertIn("restorable snapshots", payload["plan"]["rollback_plan"]["statement"])
            self.assertEqual(payload["method"], "POST")

    def test_write_command_dry_run_plan_marks_no_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._env(root)
            body = root / "body.json"
            body.write_text('{"properties": {"name": "rollback"}}', encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env),
                        "hubspot",
                        "properties",
                        "create",
                        "--object-type",
                        "contacts",
                        "--body-file",
                        str(body),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["plan"].get("rollback_plan", {}).get("possible") is False)
            self.assertEqual(payload["plan"].get("before_state", {}).get("required"), True)
            self.assertEqual(payload["plan"].get("before_state", {}).get("supported"), False)
            self.assertIn("No automatic rollback", payload["plan"]["rollback_plan"]["statement"])

    def test_write_command_requires_yes_for_batch(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._env(root)
            body = root / "body.json"
            body.write_text('{"results": []}', encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env),
                        "--apply",
                        "hubspot",
                        "objects",
                        "batch-create",
                        "--object-type",
                        "contacts",
                        "--body-file",
                        str(body),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertIn("requires --yes", " ".join(payload["reasons"]))

    def test_write_command_requires_ack_for_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._env(root)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env),
                        "--apply",
                        "--yes",
                        "hubspot",
                        "objects",
                        "archive",
                        "--object-type",
                        "contacts",
                        "--object-id",
                        "c-1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertIn("requires --ack-irreversible", " ".join(payload["reasons"]))

    def test_apply_with_full_gates_refuses_before_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._env(root)

            with patch("hubspot_safe_agent_cli.commands.hubspot.HttpClient.request", return_value=_FakeHttpResponse()) as request:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env),
                            "--apply",
                            "--yes",
                            "--ack-irreversible",
                            "hubspot",
                            "objects",
                            "archive",
                            "--object-type",
                            "contacts",
                            "--object-id",
                            "c-1",
                        ]
                    )
            self.assertEqual(rc, 0)
            request.assert_not_called()
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            joined = " ".join(payload["reasons"])
            self.assertIn("before-state snapshot", joined)
            self.assertIn("ack-no-snapshot", joined)

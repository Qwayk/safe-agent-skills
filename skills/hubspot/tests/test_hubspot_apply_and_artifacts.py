from __future__ import annotations

import io
import json
import shlex
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from hubspot_safe_agent_cli.cli import main


class _FakeHttpResponse:
    status = 200
    body = b'{"ok": true}'

    def __init__(self, payload: dict, status: int = 200) -> None:
        self.status = self.status_code = status
        self._payload = payload
        self.body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    def json(self) -> object:
        return self._payload

    def text(self) -> str:
        return self.body.decode("utf-8")


class TestHubspotApplyAndArtifacts(unittest.TestCase):
    def _run(self, env: Path, *args: object) -> tuple[int, dict]:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            rc = main(["--env-file", str(env), "--no-artifacts", *map(str, args)])
        return rc, json.loads(buffer.getvalue())

    def _env(self, root: Path) -> Path:
        env = root / ".env"
        env.write_text(
            "\n".join(
                [
                    "HUBSPOT_API_BASE_URL=http://example.invalid",
                    "HUBSPOT_ACCESS_TOKEN=fixture-token",
                    "HUBSPOT_TIMEOUT_S=30",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return env

    def test_gdpr_delete_apply_refuses_without_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._env(root)
            request = root / "request.json"
            request.write_text('{"id": "c-1"}', encoding="utf-8")
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
                        "gdpr-delete",
                        "--object-type",
                        "contacts",
                        "--body-file",
                        str(request),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertIn("requires --plan-in", " ".join(payload["reasons"]))

    def test_gdpr_delete_apply_with_plan_refuses_before_http_and_writes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._env(root)
            request = root / "request.json"
            request.write_text('{"id": "c-1"}', encoding="utf-8")
            plan = root / "plan.json"
            receipt = root / "receipt.json"
            run_id = "2026-01-19T120000Z_hubspot_apply"

            with io.StringIO() as dryrun_buf:
                with redirect_stdout(dryrun_buf):
                    dry_rc = main(
                        [
                            "--env-file",
                            str(env),
                            "--plan-out",
                            str(plan),
                            "hubspot",
                            "objects",
                            "gdpr-delete",
                            "--object-type",
                            "contacts",
                            "--body-file",
                            str(request),
                        ]
                    )
                self.assertEqual(dry_rc, 0)
                dry_payload = json.loads(dryrun_buf.getvalue())
            self.assertTrue(dry_payload["dry_run"])
            self.assertTrue(plan.exists())

            with patch(
                "hubspot_safe_agent_cli.commands.hubspot.HttpClient.request",
                return_value=_FakeHttpResponse({"status": "deleted"}),
            ) as request_call:
                apply_buf = io.StringIO()
                with redirect_stdout(apply_buf):
                    apply_rc = main(
                        [
                            "--env-file",
                            str(env),
                            "--apply",
                            "--yes",
                            "--ack-irreversible",
                            "--plan-in",
                            str(plan),
                            "--receipt-out",
                            str(receipt),
                            "--run-id",
                            run_id,
                            "hubspot",
                            "objects",
                            "gdpr-delete",
                            "--object-type",
                            "contacts",
                            "--body-file",
                            str(request),
                        ]
                    )
            self.assertEqual(apply_rc, 0)
            request_call.assert_not_called()
            payload = json.loads(apply_buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("before-state snapshot", " ".join(payload["reasons"]))
            self.assertFalse(receipt.exists())

            artifacts_dir = Path(payload["artifacts_dir"])
            runs_index = Path(payload["runs_index"])
            self.assertTrue(artifacts_dir.exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertTrue((artifacts_dir / "audit.jsonl").exists())
            self.assertTrue(runs_index.exists())
            self.assertIn(run_id, runs_index.read_text(encoding="utf-8"))
            self.assertEqual(payload["run_id"], run_id)
            self.assertEqual(payload["artifacts_dir"], str(artifacts_dir))

    def test_bulk_write_checks_reviewed_request_and_connection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = self._env(root)
            body = root / "body.json"
            body.write_text('{"inputs": [{"id": "1"}]}')
            plan = root / "plan.json"
            command = ("hubspot", "objects", "batch-update", "--body-file", body, "--object-type")
            approve = ("--apply", "--yes", "--ack-no-snapshot")

            with patch("hubspot_safe_agent_cli.commands.hubspot.HttpClient.request") as request:
                rc, result = self._run(env, *approve, *command, "contacts")
                self.assertEqual(rc, 0)
                self.assertIn("requires --plan-in", result["reasons"][0])
                rc, result = self._run(env, "--plan-out", plan, *command, "contacts")
                self.assertEqual(rc, 0)
                self.assertTrue(result["plan"]["path"].endswith("/contacts/batch/update"))
                self.assertNotIn("fixture-token", plan.read_text())
                apply = (*approve, "--plan-in", plan, *command)
                self.assertTrue(self._run(env, *apply, "companies")[1]["refused"])
                body.write_text('{"inputs": [{"id": "2"}]}')
                self.assertTrue(self._run(env, *apply, "contacts")[1]["refused"])
                body.write_text('{"inputs": [{"id": "1"}]}')
                original = env.read_text()
                env.write_text(original.replace("fixture-token", "other-fixture-token"))
                self.assertIn("connection changed", self._run(env, *apply, "contacts")[1]["reasons"][0])
                env.write_text(original)
                request.assert_not_called()
                request.return_value = _FakeHttpResponse(
                    {"status": "COMPLETE", "results": [{"id": "1"}], "numErrors": 1}, status=207
                )
                rc, result = self._run(env, *apply, "contacts")
                self.assertEqual(rc, 1)
                self.assertEqual(result["receipt"]["verification"]["status"], "partial")
                self.assertFalse(result["receipt"]["verification"]["ok"])
                request.assert_called_once()

    def test_import_uses_reviewed_file_and_saves_status_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = self._env(root)
            env = env.rename(root / "test settings.env")
            body = root / "import.json"
            body.write_text('{"name":"Example"}')
            sheet = root / "contacts.csv"
            original = b"Email\nfirst@example.invalid\n"
            sheet.write_bytes(original)
            plan = root / "plan.json"
            receipt = root / "receipt.json"
            command = ("hubspot", "imports", "create", "--request-file", body, "--file", sheet)
            approve = ("--apply", "--yes", "--ack-no-snapshot")
            apply = (*approve, "--plan-in", plan, "--receipt-out", receipt, *command)
            with patch("hubspot_safe_agent_cli.commands.hubspot.requests.post") as post:
                self.assertIn("requires --plan-in", self._run(env, *approve, *command)[1]["reasons"][0])
                self.assertEqual(self._run(env, "--plan-out", plan, *command)[0], 0)
                sheet.write_bytes(b"Email\nother@example.invalid\n")
                self.assertTrue(self._run(env, *apply)[1]["refused"])
                post.assert_not_called()
                sheet.write_bytes(original)
                post.return_value = _FakeHttpResponse({"importId": 123, "state": "PROCESSING"})
                rc, result = self._run(env, *apply)
                self.assertEqual(rc, 0)
                verification = result["receipt"]["verification"]
                self.assertEqual(verification["status"], "submitted")
                self.assertFalse(verification["ok"])
                self.assertEqual(verification["import_id"], 123)
                self.assertEqual(json.loads(receipt.read_text())["verification"], verification)
                for field, action in (("check_status", "get"), ("check_errors", "errors")):
                    args = shlex.split(verification[field])
                    self.assertIn(str(env), args)
                    self.assertEqual(args[-3:], [action, "--import-id", "123"])
                self.assertEqual(post.call_args.kwargs["files"][0][1][1], original)
                post.assert_called_once()

                for state, expected_status, expected_code in (
                    ("DONE", "completed", 0),
                    ("FAILED", "failed", 1),
                ):
                    with self.subTest(state=state):
                        post.return_value = _FakeHttpResponse({"importId": 123, "state": state})
                        rc, result = self._run(env, *apply)
                        self.assertEqual(rc, expected_code)
                        self.assertEqual(result["receipt"]["verification"]["status"], expected_status)

    def test_import_preview_without_credentials_needs_a_fresh_plan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = root / ".env"
            plan = root / "plan.json"
            body = root / "import.json"
            body.write_text('{"name":"Example"}')
            sheet = root / "contacts.csv"
            sheet.write_text("Email\nfirst@example.invalid\n")
            command = ("hubspot", "imports", "create", "--request-file", body, "--file", sheet)
            self.assertEqual(self._run(env, "--plan-out", plan, *command)[0], 0)
            self._env(root)
            with patch("hubspot_safe_agent_cli.commands.hubspot.requests.post") as post:
                rc, result = self._run(
                    env, "--apply", "--yes", "--ack-no-snapshot", "--plan-in", plan, *command
                )
                self.assertEqual(rc, 0)
                self.assertTrue(result["refused"])
                self.assertIn("fresh preview", result["reasons"][0])
                post.assert_not_called()

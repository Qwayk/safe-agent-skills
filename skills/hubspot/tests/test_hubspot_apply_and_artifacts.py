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
    body = b'{"ok": true}'

    def __init__(self, payload: dict) -> None:
        self._payload = payload
        self.body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    def json(self) -> object:
        return self._payload

    def text(self) -> str:
        return self.body.decode("utf-8")


class TestHubspotApplyAndArtifacts(unittest.TestCase):
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

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tests import bootstrap  # noqa: F401

from salesforce_platform_safe_agent_cli.cli import main
from salesforce_platform_safe_agent_cli.http import HttpResponse


class TestSalesforceSafety(unittest.TestCase):
    def _write_env(self, root: Path) -> Path:
        env_path = root / ".env"
        env_path.write_text(
            (
                "SALESFORCE_INSTANCE_URL=https://example.my.salesforce.com\n"
                "SALESFORCE_ACCESS_TOKEN=test-token\n"
                "SALESFORCE_API_VERSION=67.0\n"
                "SALESFORCE_TIMEOUT_S=30\n"
            ),
            encoding="utf-8",
        )
        return env_path

    def _run_main(self, argv: list[str]) -> tuple[int, dict[str, object]]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(argv)
        return rc, json.loads(buf.getvalue())

    def test_write_command_defaults_to_dry_run_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._write_env(root)
            body_path = root / "composite.json"
            body_path.write_text('{"allOrNone": false, "compositeRequest": []}\n', encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "composite",
                        "execute",
                        "--body-file",
                        str(body_path),
                    ]
                )

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            plan = payload["plan"]
            self.assertEqual(plan["request"]["method"], "POST")
            self.assertTrue(plan["before_state"]["required"])
            self.assertFalse(plan["before_state"]["supported"])
            self.assertEqual(plan["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(plan["verification_plan"]["type"], "best_effort_after_apply")

    def test_plan_drift_is_refused_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._write_env(root)
            body_path = root / "composite.json"
            plan_path = root / "plan.json"
            body_path.write_text('{"allOrNone": false, "compositeRequest": []}\n', encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "composite",
                        "execute",
                        "--body-file",
                        str(body_path),
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(plan_path.exists())

            body_path.write_text('{"allOrNone": true, "compositeRequest": []}\n', encoding="utf-8")

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                        "composite",
                        "execute",
                        "--body-file",
                        str(body_path),
                    ]
                )

            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])
            self.assertIn("request drift", payload2["reasons"][0])

    def test_password_set_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._write_env(root)
            body_path = root / "password.json"
            body_path.write_text('{"NewPassword":"NeverPrinted123!"}\n', encoding="utf-8")

            rc, payload = self._run_main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "sobjects-user-password",
                    "set",
                    "--user-id",
                    "005000000000001AAA",
                    "--body-file",
                    str(body_path),
                ]
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("--plan-in", payload["reasons"][0])

    def test_high_risk_actions_require_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._write_env(root)
            body_path = root / "body.json"
            body_path.write_text('{"sample":true}\n', encoding="utf-8")

            cases = [
                (
                    "consent write",
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "consent",
                        "write",
                        "--action-name",
                        "collect",
                        "--body-file",
                        str(body_path),
                    ],
                ),
                (
                    "portability create",
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "portability",
                        "create",
                        "--body-file",
                        str(body_path),
                    ],
                ),
                (
                    "jobs-ingest create",
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "jobs-ingest",
                        "create",
                        "--body-file",
                        str(body_path),
                    ],
                ),
                (
                    "process-rules trigger",
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "process-rules",
                        "trigger",
                        "--body-file",
                        str(body_path),
                    ],
                ),
            ]

            for label, argv in cases:
                with self.subTest(label=label):
                    rc, payload = self._run_main(argv)
                    self.assertEqual(rc, 0)
                    self.assertTrue(payload["ok"])
                    self.assertTrue(payload["refused"])
                    self.assertIn("--yes", payload["reasons"][0])

    def test_irreversible_actions_require_ack(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._write_env(root)

            cases = [
                (
                    "jobs-query delete",
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "jobs-query",
                        "delete",
                        "--job-id",
                        "750000000000001AAA",
                    ],
                ),
                (
                    "product-schedules delete",
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "product-schedules",
                        "delete",
                        "--opportunity-line-item-id",
                        "00k000000000001AAA",
                    ],
                ),
                (
                    "surveys-translation delete",
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "surveys-translation",
                        "delete",
                        "--developer-name",
                        "Flow.Flow.MySurvey.1.Label",
                        "--language",
                        "en_US",
                    ],
                ),
            ]

            for label, argv in cases:
                with self.subTest(label=label):
                    rc, payload = self._run_main(argv)
                    self.assertEqual(rc, 0)
                    self.assertTrue(payload["ok"])
                    self.assertTrue(payload["refused"])
                    self.assertIn("--ack-irreversible", payload["reasons"][0])

    def test_self_service_password_reset_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._write_env(root)

            rc, payload = self._run_main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "sobjects-self-service-user-password",
                    "reset",
                    "--self-service-user-id",
                    "005000000000001AAA",
                ]
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("--plan-in", payload["reasons"][0])

    def test_multipart_manifest_is_supported_for_blob_upload_plans(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._write_env(root)
            metadata_path = root / "document.json"
            metadata_path.write_text('{"Name":"Brochure","Type":"pdf"}\n', encoding="utf-8")
            binary_path = root / "brochure.pdf"
            binary_path.write_bytes(b"%PDF-1.4 test brochure\n")
            manifest_path = root / "multipart.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "parts": [
                            {
                                "name": "entity_content",
                                "content_type": "application/json",
                                "json_file": str(metadata_path),
                            },
                            {
                                "name": "Body",
                                "file": str(binary_path),
                                "filename": "brochure.pdf",
                                "content_type": "application/pdf",
                            },
                        ]
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "sobjects-object",
                        "create",
                        "--sobject",
                        "Document",
                        "--multipart-file",
                        str(manifest_path),
                    ]
                )

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            request_body = payload["plan"]["request"]["body"]
            self.assertTrue(request_body["multipart"])
            self.assertEqual(len(request_body["parts"]), 2)

    def test_dry_run_plan_includes_explicit_no_recovery_contract(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                (
                    "SALESFORCE_INSTANCE_URL=https://example.invalid\n"
                    "SALESFORCE_ACCESS_TOKEN=test-token\n"
                    "SALESFORCE_TIMEOUT_S=30\n"
                ),
                encoding="utf-8",
            )
            body_path = root / "body.json"
            body_path.write_text('{"Name":"No Recovery Account"}\n', encoding="utf-8")

            rc, payload = self._run_main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "sobjects-object",
                    "create",
                    "--sobject",
                    "Account",
                    "--body-file",
                    str(body_path),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            plan = payload["plan"]
            recovery = plan["recovery"]
            self.assertIsInstance(recovery, dict)
            self.assertFalse(recovery["automatic_rollback"])
            self.assertEqual(recovery["backups"], [])
            self.assertEqual(recovery["snapshots"], [])
            self.assertIsNone(recovery["rollback_plan"])
            self.assertIn("No automatic rollback", str(recovery["restore_note"]))

            before_state = plan["before_state"]
            self.assertTrue(before_state["required"])
            self.assertFalse(before_state["supported"])
            self.assertEqual(before_state["status"], "no_snapshot_available")
            self.assertIn("no reliable generic before-state snapshot", str(before_state["notes"]))
            self.assertEqual(plan["verification_plan"]["type"], "best_effort_after_apply")

            rollback = plan["rollback"]
            self.assertFalse(rollback["supported"])
            self.assertIn("No automatic rollback", str(rollback["notes"]))

    def test_apply_refuses_before_provider_write_without_before_state(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._write_env(root)
            body_path = root / "body.json"
            body_path.write_text('{"Name":"Recoverable Preview"}\n', encoding="utf-8")
            plan_path = root / "plan.json"
            receipt_path = root / "receipt.json"

            plan_rc, plan_payload = self._run_main(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "--plan-out",
                    str(plan_path),
                    "sobjects-object",
                    "create",
                    "--sobject",
                    "Account",
                    "--body-file",
                    str(body_path),
                ]
            )
            self.assertEqual(plan_rc, 0)
            self.assertTrue(plan_payload["ok"])
            self.assertTrue(plan_payload["dry_run"])
            self.assertTrue(plan_path.exists())

            with patch("salesforce_platform_safe_agent_cli.commands.salesforce.HttpClient.request") as request_mock:
                apply_rc, apply_payload = self._run_main(
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
                        "sobjects-object",
                        "create",
                        "--sobject",
                        "Account",
                        "--body-file",
                        str(body_path),
                    ]
                )

            self.assertEqual(apply_rc, 0)
            self.assertTrue(apply_payload["ok"])
            self.assertTrue(apply_payload["refused"])
            self.assertIn("before-state snapshot", apply_payload["reasons"][0])
            self.assertIn("ack-no-snapshot", apply_payload["reasons"][0])
            self.assertNotIn("receipt", apply_payload)
            self.assertFalse(receipt_path.exists())
            request_mock.assert_not_called()

    def test_openapi_create_runs_without_apply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._write_env(root)
            body_path = root / "openapi.json"
            body_path.write_text('{"resources":["/sobjects"]}\n', encoding="utf-8")
            response = HttpResponse(
                status=202,
                headers={"content-type": "application/json"},
                body=json.dumps(
                    {
                        "results": "/v67.0/async/specifications/oas3/abc123/results",
                        "details": "/v67.0/async/specifications/oas3/abc123",
                    }
                ).encode("utf-8"),
                url="https://example.my.salesforce.com/services/data/v67.0/async/specifications/oas3",
            )

            with patch("salesforce_platform_safe_agent_cli.commands.salesforce.HttpClient.request", return_value=response):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "openapi-sobjects",
                            "create",
                            "--body-file",
                            str(body_path),
                        ]
                    )

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["request"]["method"], "POST")
            self.assertEqual(payload["response"]["status"], 202)

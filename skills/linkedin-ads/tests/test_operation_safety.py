from __future__ import annotations

import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import requests

from linkedin_ads_api_tool.cli import main
from linkedin_ads_api_tool.operation_catalog import OPERATIONS_BY_FAMILY, RISKY


_PATH_PLACEHOLDER_RE = re.compile(r"{([^{}]+)}")


class TestOperationRuntimeSafety(unittest.TestCase):
    def test_campaign_update_sends_partial_update_after_approval_and_records_only_reply(self) -> None:
        with tempfile.TemporaryDirectory() as td, patch.dict("os.environ", {}, clear=True):
            env_file = Path(td) / ".env"
            env_file.write_text("LINKEDIN_ADS_TOKEN=fixture-token\n", encoding="utf-8")
            receipt_file = Path(td) / "receipt.json"
            plan_file = Path(td) / "plan.json"
            response = requests.Response()
            response.status_code = 204
            response._content = b""
            base = ["--env-file", str(env_file), "--output", "json"]
            command = [
                "ad-campaigns", "update", "--ad-account-id", "123456", "--campaign-id", "789",
                "--body-json", '{"patch":{"$set":{"status":"PAUSED"}}}',
            ]

            with patch.object(requests.Session, "send", return_value=response) as send:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    self.assertEqual(main(base + ["--plan-out", str(plan_file)] + command), 0)
                self.assertTrue(json.loads(buf.getvalue())["dry_run"])
                self.assertEqual(json.loads(plan_file.read_text())["request"]["restli_method"], "PARTIAL_UPDATE")

                buf = io.StringIO()
                with redirect_stdout(buf):
                    self.assertEqual(main(base + ["--apply", "--ack-irreversible"] + command), 0)
                self.assertTrue(json.loads(buf.getvalue())["refused"])
                send.assert_not_called()

                buf = io.StringIO()
                args = base + [
                    "--apply", "--ack-irreversible", "--ack-no-snapshot", "--receipt-out", str(receipt_file),
                ]
                with redirect_stdout(buf):
                    self.assertEqual(main(args + command), 0)
                send.assert_called_once()

            request = send.call_args.args[0]
            self.assertEqual(request.method, "POST")
            self.assertEqual(request.url, "https://api.linkedin.com/rest/adAccounts/123456/adCampaigns/789")
            self.assertEqual(request.headers["X-RestLi-Method"], "PARTIAL_UPDATE")
            self.assertEqual(json.loads(request.body), {"patch": {"$set": {"status": "PAUSED"}}})
            receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
            self.assertEqual(json.loads(buf.getvalue())["receipt"], receipt)
            self.assertEqual(receipt["response"]["status"], 204)
            self.assertTrue(receipt["no_snapshot_approval"]["acknowledged"])
            self.assertIsNone(receipt["changed"])
            self.assertIsNone(receipt["verification"]["ok"])
            self.assertEqual(receipt["verification"]["details"]["check"], "http_response_only")

    def _build_argv_for_spec(self, family: str, spec) -> list[str]:
        argv = [family, spec.command]
        placeholders = sorted(set(_PATH_PLACEHOLDER_RE.findall(spec.path)))
        for placeholder in placeholders:
            argv.append(f"--{placeholder.replace('_', '-')}")
            argv.append(f"urn:li:test:{placeholder}")
        return argv

    def test_non_read_operations_can_dry_run_without_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("LINKEDIN_ADS_TIMEOUT_S=30\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--output", "json", "ad-accounts", "create"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertIn("plan", payload)
            self.assertEqual(payload["plan"]["operation"]["method"], "POST")
            self.assertEqual(payload["plan"]["operation"]["command"], "create")
            self.assertEqual(payload["plan"]["rollback"]["mode"], "irreversible_and_clearly_labeled")
            self.assertTrue(payload["plan"]["rollback"]["requires_ack_irreversible"])
            self.assertIn("live apply requires --ack-irreversible", payload["plan"]["preconditions"])
            self.assertTrue(payload["plan"]["before_state"]["required"])
            self.assertFalse(payload["plan"]["before_state"]["supported"])
            self.assertEqual(payload["plan"]["verification_plan"]["type"], "best_effort_after_apply")

    def test_read_like_post_operations_run_live_without_apply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("LINKEDIN_ADS_TIMEOUT_S=30\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "ad-previews",
                        "live-preview-for-creative",
                    ]
                )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("Missing LinkedIn token", payload["error"])

    def test_read_like_post_operations_do_not_require_ack_when_token_exists(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "LINKEDIN_ADS_TOKEN=TEST_TOKEN",
                        "LINKEDIN_ADS_LINKEDIN_VERSION=202605",
                        "LINKEDIN_ADS_RESTLI_PROTOCOL_VERSION=2.0.0",
                        "LINKEDIN_ADS_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            class _Response:
                status = 200

                def json(self):
                    return {"ok": True}

                def text(self):
                    return "{}"

            with patch("linkedin_ads_api_tool.commands.operations.HttpClient.request", return_value=_Response()) as request_mock:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "ad-previews",
                            "live-preview-for-creative",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            request_mock.assert_called_once()

    def test_high_risk_apply_requires_apply_yes_and_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "LINKEDIN_ADS_TOKEN=TEST_TOKEN",
                        "LINKEDIN_ADS_LINKEDIN_VERSION=202605",
                        "LINKEDIN_ADS_RESTLI_PROTOCOL_VERSION=2.0.0",
                        "LINKEDIN_ADS_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            risky_specs = [
                (family, spec)
                for family, specs in OPERATIONS_BY_FAMILY.items()
                for spec in specs
                if spec.safety == RISKY
            ]
            self.assertGreater(len(risky_specs), 0)

            for family, spec in risky_specs:
                with self.subTest(f"{family}:{spec.command} requires --yes"):
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = main(
                            [
                                "--env-file",
                                str(env_path),
                                "--apply",
                                "--output",
                                "json",
                                *self._build_argv_for_spec(family, spec),
                            ]
                        )
                    self.assertEqual(rc, 0)
                    payload = json.loads(buf.getvalue())
                    self.assertTrue(payload["ok"])
                    self.assertTrue(payload["refused"])
                    self.assertEqual(payload["refusal_type"], "SafetyError")
                    self.assertTrue(any("--yes" in reason for reason in payload["reasons"]))

                with self.subTest(f"{family}:{spec.command} requires --plan-in"):
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = main(
                            [
                                "--env-file",
                                str(env_path),
                                "--apply",
                                "--yes",
                                "--output",
                                "json",
                                *self._build_argv_for_spec(family, spec),
                            ]
                        )
                    self.assertEqual(rc, 0)
                    payload = json.loads(buf.getvalue())
                    self.assertTrue(payload["ok"])
                    self.assertTrue(payload["refused"])
                    self.assertEqual(payload["refusal_type"], "SafetyError")
                    self.assertTrue(any("--plan-in" in reason for reason in payload["reasons"]))

    def test_medium_write_apply_requires_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "LINKEDIN_ADS_TOKEN=TEST_TOKEN",
                        "LINKEDIN_ADS_LINKEDIN_VERSION=202605",
                        "LINKEDIN_ADS_RESTLI_PROTOCOL_VERSION=2.0.0",
                        "LINKEDIN_ADS_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--output",
                        "json",
                        "ad-accounts",
                        "create",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertTrue(any("--ack-irreversible" in reason for reason in payload["reasons"]))

    def test_medium_write_apply_with_ack_refuses_before_provider_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "LINKEDIN_ADS_TOKEN=TEST_TOKEN",
                        "LINKEDIN_ADS_LINKEDIN_VERSION=202605",
                        "LINKEDIN_ADS_RESTLI_PROTOCOL_VERSION=2.0.0",
                        "LINKEDIN_ADS_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            with patch("linkedin_ads_api_tool.commands.operations.HttpClient.request") as request_mock:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--apply",
                            "--ack-irreversible",
                            "--output",
                            "json",
                            "ad-accounts",
                            "create",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertIn("before-state snapshot", " ".join(payload["reasons"]))
            self.assertIn("ack-no-snapshot", " ".join(payload["reasons"]))
            request_mock.assert_not_called()

    def test_high_risk_apply_requires_ack_irreversible_after_plan_validation(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "LINKEDIN_ADS_TOKEN=TEST_TOKEN",
                        "LINKEDIN_ADS_LINKEDIN_VERSION=202605",
                        "LINKEDIN_ADS_RESTLI_PROTOCOL_VERSION=2.0.0",
                        "LINKEDIN_ADS_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            plan_path = root / "delete.plan.json"

            plan_buf = io.StringIO()
            with redirect_stdout(plan_buf):
                plan_rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "--output",
                        "json",
                        "ad-accounts",
                        "delete",
                        "--ad-account-id",
                        "123456",
                    ]
                )
            self.assertEqual(plan_rc, 0)
            plan_payload = json.loads(plan_buf.getvalue())
            self.assertTrue(plan_payload["ok"])
            self.assertTrue(plan_payload["dry_run"])
            self.assertTrue(plan_path.exists())

            with patch("linkedin_ads_api_tool.commands.operations.HttpClient.request") as request_mock:
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
                            "--output",
                            "json",
                            "ad-accounts",
                            "delete",
                            "--ad-account-id",
                            "123456",
                        ]
                    )
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertTrue(payload["refused"])
                self.assertEqual(payload["refusal_type"], "SafetyError")
                self.assertTrue(any("--ack-irreversible" in reason for reason in payload["reasons"]))
                request_mock.assert_not_called()

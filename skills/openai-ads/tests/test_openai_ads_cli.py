from __future__ import annotations

import importlib
import io
import json
import pkgutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from qwayk_openai_ads.audit_log import AuditLogger
from qwayk_openai_ads.cli import main
from qwayk_openai_ads.http import HttpResponse
from qwayk_openai_ads.inventory import load_inventory
from qwayk_openai_ads.output import Output


def _payload(argv: list[str]) -> tuple[int, dict]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(argv)
    return rc, json.loads(buf.getvalue())


def _assert_no_leaks(testcase: unittest.TestCase, text: str) -> None:
    for leaked in (
        "person@example.com",
        "raw@example.com",
        "cust_private_123",
        "external_private_456",
        "https://shop.example/thank-you",
    ):
        testcase.assertNotIn(leaked, text)


class TestOpenAIAdsCli(unittest.TestCase):
    def _env(self, root: Path) -> Path:
        env_path = root / ".env"
        env_path.write_text(
            "OPENAI_ADS_BASE_URL=https://api.ads.openai.com/v1\n"
            "OPENAI_ADS_API_KEY=test-key\n"
            "OPENAI_ADS_TIMEOUT_S=30\n"
            "OPENAI_ADS_PIXEL_ID=px_test_secret\n"
            "OPENAI_ADS_CONVERSIONS_API_KEY=conv-key\n"
            "OPENAI_ADS_CONVERSIONS_BASE_URL=https://bzr.openai.com/v1\n",
            encoding="utf-8",
        )
        return env_path

    def test_package_modules_importable(self) -> None:
        pkg = importlib.import_module("qwayk_openai_ads")
        errors: list[str] = []
        for mod in pkgutil.walk_packages(pkg.__path__, prefix="qwayk_openai_ads."):
            try:
                importlib.import_module(mod.name)
            except Exception as e:  # noqa: BLE001
                errors.append(f"{mod.name}: {type(e).__name__}: {e}")
        self.assertEqual(errors, [])

    def test_version_json_no_env_needed(self) -> None:
        rc, payload = _payload(["--output", "json", "--version"])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["tool"], "openai-ads-safe-agent-cli")

    def test_inventory_covers_pinned_spec_and_manual_surfaces(self) -> None:
        inventory = load_inventory()
        self.assertEqual(inventory["operation_count"], 41)
        self.assertEqual(inventory["path_count"], 33)
        self.assertEqual(inventory["server_url"], "https://api.ads.openai.com/v1")
        self.assertIn("campaigns", inventory["families"])
        self.assertIn("measurement", {row["family_slug"] for row in inventory["manual_surfaces"]})

    def test_api_list_needs_no_env(self) -> None:
        rc, payload = _payload(["--output", "json", "api", "list"])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["operation_count"], 41)

    def test_write_dry_run_creates_reviewed_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._env(root)
            plan_path = root / "plan.json"
            body = json.dumps({"name": "Launch test", "status": "paused"})
            rc, payload = _payload(
                [
                    "--env-file",
                    str(env_path),
                    "--plan-out",
                    str(plan_path),
                    "api",
                    "campaigns",
                    "create-campaign",
                    "--header",
                    "Idempotency-Key=test-plan-1",
                    "--body-json",
                    body,
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertTrue(plan_path.exists())
            self.assertIn("openai-ads-write", payload["plan"]["risk_reasons"])
            self.assertEqual(payload["plan"]["target"]["headers"]["Idempotency-Key"], "[REDACTED]")
            self.assertNotIn("test-key", json.dumps(payload))

    def test_write_plan_redacts_private_ads_body_everywhere(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._env(root)
            plan_path = root / "plan.json"
            log_path = root / "audit.jsonl"
            run_id = "2026-07-06T130000Z_privacy"
            body = {
                "name": "Private audience test",
                "customer_id": "cust_private_123",
                "external_id": "external_private_456",
                "email": "person@example.com",
                "audience": {
                    "rows": [
                        {
                            "email": "raw@example.com",
                            "external_id": "external_private_456",
                            "source_url": "https://shop.example/thank-you?oppref=secret",
                        }
                    ]
                },
            }
            rc, payload = _payload(
                [
                    "--env-file",
                    str(env_path),
                    "--run-id",
                    run_id,
                    "--plan-out",
                    str(plan_path),
                    "--log-file",
                    str(log_path),
                    "api",
                    "custom-audiences",
                    "create-custom-audience",
                    "--body-json",
                    json.dumps(body),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(plan_path.exists())
            artifacts_dir = Path(payload["artifacts_dir"])
            combined = "\n".join(
                [
                    json.dumps(payload, sort_keys=True),
                    plan_path.read_text(encoding="utf-8"),
                    log_path.read_text(encoding="utf-8"),
                    (artifacts_dir / "summary.md").read_text(encoding="utf-8"),
                    Path(payload["runs_index"]).read_text(encoding="utf-8"),
                ]
            )
            _assert_no_leaks(self, combined)
            self.assertEqual(payload["plan"]["request_body"]["customer_id"], "[REDACTED]")
            self.assertEqual(payload["plan"]["request_body"]["audience"], "[REDACTED]")

    def test_apply_refuses_without_reviewed_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env(Path(d))
            body = json.dumps({"name": "Launch test", "status": "paused"})
            rc, payload = _payload(
                [
                    "--env-file",
                    str(env_path),
                    "--apply",
                    "--yes",
                    "api",
                    "campaigns",
                    "create-campaign",
                    "--body-json",
                    body,
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("--plan-in", payload["reasons"][0])

    def test_body_risk_requires_irreversible_acknowledgement(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._env(root)
            plan_path = root / "plan.json"
            body = {
                "name": "Risky launch",
                "daily_budget": 50000,
                "status": "active",
                "targeting": {"geo_locations": ["US"]},
            }
            rc, payload = _payload(
                [
                    "--env-file",
                    str(env_path),
                    "--plan-out",
                    str(plan_path),
                    "api",
                    "campaigns",
                    "create-campaign",
                    "--body-json",
                    json.dumps(body),
                ]
            )
            self.assertEqual(rc, 0)
            reasons = set(payload["plan"]["risk_reasons"])
            self.assertIn("spend-risk", reasons)
            self.assertIn("serving-status-change", reasons)
            self.assertIn("targeting-change", reasons)

            with patch("qwayk_openai_ads.commands.api.HttpClient.request") as request:
                rc, apply_payload = _payload(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "api",
                        "campaigns",
                        "create-campaign",
                        "--body-json",
                        json.dumps(body),
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(apply_payload["refused"])
            self.assertIn("--ack-irreversible", apply_payload["reasons"][0])
            request.assert_not_called()

    def test_provider_error_redacts_private_ads_values(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env(Path(d))
            body = (
                b'{"error":"email person@example.com customer_id=cust_private_123 '
                b'external_id=external_private_456 source_url=https://shop.example/thank-you"}'
            )
            response = HttpResponse(
                status=400,
                headers={},
                body=body,
                url="https://api.ads.openai.com/v1/campaigns?customer_id=cust_private_123",
            )
            with patch("qwayk_openai_ads.http.requests.Session.request") as request:
                request.return_value.status_code = response.status
                request.return_value.headers = response.headers
                request.return_value.content = response.body
                request.return_value.text = response.text()
                request.return_value.url = response.url
                rc, payload = _payload(
                    [
                        "--env-file",
                        str(env_path),
                        "api",
                        "campaigns",
                        "list-campaigns",
                    ]
                )
            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            _assert_no_leaks(self, json.dumps(payload, sort_keys=True))

    def test_apply_receipt_redacts_private_provider_response(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._env(root)
            plan_path = root / "plan.json"
            receipt_path = root / "receipt.json"
            body = {
                "name": "Private audience test",
                "customer_id": "cust_private_123",
                "external_id": "external_private_456",
                "email": "person@example.com",
            }
            rc, payload = _payload(
                [
                    "--env-file",
                    str(env_path),
                    "--plan-out",
                    str(plan_path),
                    "api",
                    "custom-audiences",
                    "create-custom-audience",
                    "--body-json",
                    json.dumps(body),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            response_body = json.dumps(
                {
                    "id": "aud_123",
                    "customer_id": "cust_private_123",
                    "external_id": "external_private_456",
                    "email": "person@example.com",
                    "source_url": "https://shop.example/thank-you?oppref=secret",
                }
            ).encode("utf-8")
            with patch("qwayk_openai_ads.http.requests.Session.request") as request:
                request.return_value.status_code = 200
                request.return_value.headers = {}
                request.return_value.content = response_body
                request.return_value.text = response_body.decode("utf-8")
                request.return_value.url = "https://api.ads.openai.com/v1/custom_audiences/aud_123"
                rc, apply_payload = _payload(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                        "--receipt-out",
                        str(receipt_path),
                        "api",
                        "custom-audiences",
                        "create-custom-audience",
                        "--body-json",
                        json.dumps(body),
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(apply_payload["ok"])
            self.assertTrue(receipt_path.exists())
            combined = json.dumps(apply_payload, sort_keys=True) + receipt_path.read_text(encoding="utf-8")
            _assert_no_leaks(self, combined)

    def test_measurement_dry_run_redacts_pixel_and_event_data(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._env(root)
            plan_path = root / "conversion-plan.json"
            events = [{"id": "evt_1", "type": "order_created", "source_url": "https://shop.example/thank-you?token=secret"}]
            rc, payload = _payload(
                [
                    "--env-file",
                    str(env_path),
                    "--plan-out",
                    str(plan_path),
                    "measurement",
                    "conversions-send",
                    "--events-json",
                    json.dumps(events),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            text = json.dumps(payload)
            self.assertNotIn("px_test_secret", text)
            self.assertNotIn("conv-secret-key", text)
            self.assertNotIn("https://shop.example/thank-you", text)

    def test_run_artifacts_for_write_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._env(root)
            run_id = "2026-07-06T120000Z_ads001"
            rc, payload = _payload(
                [
                    "--env-file",
                    str(env_path),
                    "--run-id",
                    run_id,
                    "api",
                    "campaigns",
                    "create-campaign",
                    "--body-json",
                    json.dumps({"name": "Plan only", "status": "paused"}),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue((artifacts_dir / "plan.json").exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertIn(run_id, Path(payload["runs_index"]).read_text(encoding="utf-8"))

    def test_audit_log_redacts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "audit.jsonl"
            audit = AuditLogger(path=str(p), enabled=True)
            audit.bind_context({"tool": "openai-ads-safe-agent-cli", "command": "x", "api_key": "secret"})
            audit.write("test.event", {"token": "SECRET", "nested": {"api_key": "K", "safe": "ok"}})
            audit.close()
            obj = json.loads(p.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(obj["api_key"], "[REDACTED]")
            self.assertEqual(obj["payload"]["nested"]["api_key"], "[REDACTED]")

    def test_output_constructs(self) -> None:
        self.assertIsNotNone(Output(mode="json"))

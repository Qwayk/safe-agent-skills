from __future__ import annotations

import io
import hashlib
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

from msads_api_tool.cli import main


@dataclass(frozen=True)
class _FakeSoapResult:
    ok: bool
    status: int | None
    url: str
    started_at_utc: str
    finished_at_utc: str
    response_text: str | None
    error: str | None


class _FakeSoapClient:
    last_build_plan: tuple[str, str] | None = None
    last_call: tuple[str, str] | None = None

    def __init__(self, **_kwargs) -> None:  # noqa: ANN003
        pass

    def build_plan(self, *, service: str, operation: str, request_obj, live: bool):  # noqa: ANN001
        _ = request_obj, live
        type(self).last_build_plan = (service, operation)
        return {"service": service, "operation": operation, "live": live}

    def call(self, *, service: str, operation: str, request_obj):  # noqa: ANN001
        _ = request_obj
        type(self).last_call = (service, operation)
        return _FakeSoapResult(
            ok=True,
            status=200,
            url="http://example.invalid",
            started_at_utc="2026-01-01T00:00:00Z",
            finished_at_utc="2026-01-01T00:00:01Z",
            response_text="<ok/>",
            error=None,
        )


class TestServiceOperations(unittest.TestCase):
    def _json_sha256(self, obj: object) -> str:
        raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def _run(self, argv: list[str]) -> dict:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", *argv])
        self.assertEqual(rc, 0)
        return json.loads(buf.getvalue())

    @patch("msads_api_tool.commands.operations.MsAdsSoapClient", _FakeSoapClient)
    def test_each_service_family_emits_a_plan(self) -> None:
        cases = [
            ("campaign-management", "get-campaigns-by-account-id"),
            ("bulk", "get-bulk-download-status"),
            ("reporting", "submit-generate-report"),
            ("ad-insight", "get-bid-opportunities"),
            ("customer-management", "get-accounts-info"),
        ]
        for service, op_kebab in cases:
            payload = self._run([service, op_kebab])
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["operation"]["service"], service)
            self.assertEqual(payload["plan"]["operation"]["operation_kebab"], op_kebab)

    @patch("msads_api_tool.commands.operations.MsAdsSoapClient", _FakeSoapClient)
    def test_calls_client_build_plan_with_expected_service_and_operation(self) -> None:
        payload = self._run(["campaign-management", "get-campaigns-by-account-id"])
        self.assertTrue(payload["ok"])
        self.assertEqual(_FakeSoapClient.last_build_plan, ("campaign-management", "GetCampaignsByAccountId"))

    @patch("msads_api_tool.commands.operations.MsAdsSoapClient", _FakeSoapClient)
    def test_live_read_calls_client_without_apply_for_read_ops(self) -> None:
        payload = self._run(["--live", "campaign-management", "get-campaigns-by-account-id"])
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["read"])
        self.assertEqual(_FakeSoapClient.last_call, ("campaign-management", "GetCampaignsByAccountId"))

    @patch("msads_api_tool.commands.operations.MsAdsSoapClient", _FakeSoapClient)
    def test_apply_requires_live(self) -> None:
        payload = self._run(["--apply", "customer-management", "add-account"])
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["refused"])
        self.assertIn("without --live", " ".join(payload["reasons"]))

    @patch("msads_api_tool.commands.operations.MsAdsSoapClient", _FakeSoapClient)
    def test_live_apply_refuses_before_soap_write_without_before_state(self) -> None:
        _FakeSoapClient.last_call = None
        payload = self._run(["--live", "--apply", "customer-management", "add-account"])
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["refused"])
        self.assertIn("before-state snapshot", " ".join(payload["reasons"]))
        self.assertIn("ack-no-snapshot", " ".join(payload["reasons"]))
        self.assertIsNone(_FakeSoapClient.last_call)

    @patch("msads_api_tool.commands.operations.MsAdsSoapClient", _FakeSoapClient)
    def test_plan_in_requires_matching_env_fingerprint(self) -> None:
        _FakeSoapClient.last_call = None
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            plan_path = td_path / "plan.json"
            req_path = td_path / "req.json"
            req_path.write_text(json.dumps({"example": 1}), encoding="utf-8")

            plan_path.write_text(
                json.dumps(
                    {
                        "env_fingerprint": "msads:sandbox",
                        "operation": {"service": "customer-management", "operation": "AddAccount"},
                        "request_sha256": self._json_sha256({"example": 1}),
                    }
                ),
                encoding="utf-8",
            )

            payload = self._run(
                [
                    "--apply",
                    "--live",
                    "--plan-in",
                    str(plan_path),
                    "customer-management",
                    "add-account",
                    "--request-json",
                    str(req_path),
                ]
            )
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("env_fingerprint mismatch", " ".join(payload["reasons"]))
            self.assertIsNone(_FakeSoapClient.last_call)

    @patch("msads_api_tool.commands.operations.MsAdsSoapClient", _FakeSoapClient)
    def test_plan_in_requires_matching_request_sha256(self) -> None:
        _FakeSoapClient.last_call = None
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            plan_path = td_path / "plan.json"
            req_apply_path = td_path / "req_apply.json"

            req_apply_path.write_text(json.dumps({"example": 2}), encoding="utf-8")

            plan_path.write_text(
                json.dumps(
                    {
                        "env_fingerprint": "msads:prod",
                        "operation": {"service": "customer-management", "operation": "AddAccount"},
                        "request_sha256": self._json_sha256({"example": 1}),
                    }
                ),
                encoding="utf-8",
            )

            payload = self._run(
                [
                    "--apply",
                    "--live",
                    "--plan-in",
                    str(plan_path),
                    "customer-management",
                    "add-account",
                    "--request-json",
                    str(req_apply_path),
                ]
            )
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("request_sha256 differs", " ".join(payload["reasons"]))
            self.assertIsNone(_FakeSoapClient.last_call)

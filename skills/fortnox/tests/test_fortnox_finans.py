from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from fortnox_api_tool.cli import main


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _api_response(*, status: int, path: str, body: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "status": status,
        "url": f"https://api.fortnox.se/3{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


class TestFortnoxFinans(unittest.TestCase):
    def _run(self, *, env_path: Path, args: list[str]) -> tuple[int, dict[str, Any]]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--env-file", str(env_path), *args])
        text = buf.getvalue().strip()
        self.assertTrue(text, "Command did not emit JSON output")
        return rc, json.loads(text)

    def _plan_from_output(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan = payload.get("plan")
        if isinstance(plan, dict):
            return plan
        plan_out = payload.get("plan_out") or payload.get("plan_path")
        self.assertTrue(plan_out)
        self.assertIsInstance(plan_out, str)
        return json.loads(Path(plan_out).read_text(encoding="utf-8"))

    def _write_env(self, td: str) -> Path:
        env_path = Path(td) / ".env"
        env_path.write_text(
            "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
            encoding="utf-8",
        )
        return env_path

    def _make_create_payload_file(self, path: Path, *, invoice_number: str = "2001") -> None:
        payload = {
            "NoxFinansInvoice": {
                "InvoiceNumber": invoice_number,
                "SendMethod": "EMAIL",
                "Service": "REMINDER",
            }
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _make_pause_payload_file(self, path: Path, *, invoice_number: str = "2001") -> None:
        payload = {
            "NoxFinansInvoice": {
                "InvoiceNumber": invoice_number,
                "PausedUntilDate": "2026-07-01",
            }
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _make_report_payment_payload_file(self, path: Path, *, invoice_number: str = "2001") -> None:
        payload = {
            "NoxFinansInvoice": {
                "InvoiceNumber": invoice_number,
                "PaymentAmount": 1250.0,
                "PaymentMethodCode": "BG",
                "PaymentMethodAccount": "1930",
                "ClientTakesFees": True,
                "BookkeepPaymentInFortnox": True,
                "ReportToFinance": True,
            }
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_get_reads_one_fortnox_finans_invoice(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch(
                "fortnox_api_tool.commands.fortnox_finans.get_json",
                return_value=_api_response(
                    status=200,
                    path="/noxfinansinvoices/2001",
                    body={"NoxFinansInvoice": {"InvoiceNumber": "2001"}},
                ),
            ):
                rc, payload = self._run(
                    env_path=env_path,
                    args=["fortnox-finans", "get", "--invoice-number", "2001"],
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], "/noxfinansinvoices/2001")

    def test_send_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "send.json"
            self._make_create_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.fortnox_finans.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "fortnox-finans",
                        "send-an-invoice-with-fortnox-finans",
                        "--json-file",
                        str(payload_path),
                    ],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), _sha256(payload_path))
            self.assertEqual(request_json.call_count, 0)

    def test_send_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "send.json"
            self._make_create_payload_file(payload_path)

            rc, plan_payload = self._run(
                env_path=env_path,
                args=[
                    "fortnox-finans",
                    "send-an-invoice-with-fortnox-finans",
                    "--json-file",
                    str(payload_path),
                ],
            )
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.fortnox_finans.request_json") as request_json:
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "fortnox-finans",
                        "send-an-invoice-with-fortnox-finans",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply["refused"])
            self.assertIn("--apply --yes", " ".join(payload_apply["reasons"]))
            self.assertEqual(request_json.call_count, 0)

    def test_send_apply_performs_post_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "send.json"
            self._make_create_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.fortnox_finans.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "fortnox-finans",
                        "send-an-invoice-with-fortnox-finans",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=201,
                        path="/noxfinansinvoices",
                        body={"NoxFinansInvoice": {"InvoiceNumber": "2001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/noxfinansinvoices/2001",
                        body={"NoxFinansInvoice": {"InvoiceNumber": "2001", "Status": "UNKNOWN"}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "fortnox-finans",
                        "send-an-invoice-with-fortnox-finans",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("ok", False))
            self.assertEqual(request_json.call_args_list[0].kwargs["method"], "POST")
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/noxfinansinvoices")
            self.assertEqual(
                request_json.call_args_list[0].kwargs["json_body"],
                {
                    "NoxFinansInvoice": {
                        "InvoiceNumber": "2001",
                        "SendMethod": "EMAIL",
                        "Service": "REMINDER",
                    }
                },
            )
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/noxfinansinvoices/2001")

    def test_action_pause_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "pause.json"
            self._make_pause_payload_file(payload_path)

            rc, plan_payload = self._run(
                env_path=env_path,
                args=[
                    "fortnox-finans",
                    "action-pause",
                    "--invoice-number",
                    "2001",
                    "--json-file",
                    str(payload_path),
                ],
            )
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.fortnox_finans.request_json") as request_json:
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "fortnox-finans",
                        "action-pause",
                        "--invoice-number",
                        "2001",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply["refused"])
            self.assertIn("--apply --yes", " ".join(payload_apply["reasons"]))
            self.assertEqual(request_json.call_count, 0)

    def test_action_pause_apply_performs_put_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "pause.json"
            self._make_pause_payload_file(payload_path)

            rc, plan_payload = self._run(
                env_path=env_path,
                args=[
                    "fortnox-finans",
                    "action-pause",
                    "--invoice-number",
                    "2001",
                    "--json-file",
                    str(payload_path),
                ],
            )
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.fortnox_finans.request_json") as request_json:
                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/noxfinansinvoices/2001/pause",
                        body={"NoxFinansInvoice": {"InvoiceNumber": "2001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/noxfinansinvoices/2001",
                        body={"NoxFinansInvoice": {"InvoiceNumber": "2001", "Status": "OPEN"}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "fortnox-finans",
                        "action-pause",
                        "--invoice-number",
                        "2001",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("ok", False))
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/noxfinansinvoices/2001/pause")
            self.assertEqual(
                request_json.call_args_list[0].kwargs["json_body"],
                {"NoxFinansInvoice": {"InvoiceNumber": "2001", "PausedUntilDate": "2026-07-01"}},
            )

    def test_action_report_payment_apply_performs_put_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "report-payment.json"
            self._make_report_payment_payload_file(payload_path)

            rc, plan_payload = self._run(
                env_path=env_path,
                args=[
                    "fortnox-finans",
                    "action-report-payment",
                    "--invoice-number",
                    "2001",
                    "--json-file",
                    str(payload_path),
                ],
            )
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.fortnox_finans.request_json") as request_json:
                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/noxfinansinvoices/2001/report-payment",
                        body={"NoxFinansInvoice": {"InvoiceNumber": "2001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/noxfinansinvoices/2001",
                        body={"NoxFinansInvoice": {"InvoiceNumber": "2001", "Status": "OPEN"}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "fortnox-finans",
                        "action-report-payment",
                        "--invoice-number",
                        "2001",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("ok", False))
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/noxfinansinvoices/2001/report-payment")

    def test_action_stop_apply_sends_empty_body_when_no_json_file_is_given(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            rc, plan_payload = self._run(
                env_path=env_path,
                args=["fortnox-finans", "action-stop", "--invoice-number", "2001"],
            )
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.fortnox_finans.request_json") as request_json:
                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/noxfinansinvoices/2001/stop",
                        body={"NoxFinansInvoice": {"InvoiceNumber": "2001"}},
                    ),
                    _api_response(
                        status=200,
                        path="/noxfinansinvoices/2001",
                        body={"NoxFinansInvoice": {"InvoiceNumber": "2001", "Status": "OPEN"}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "fortnox-finans",
                        "action-stop",
                        "--invoice-number",
                        "2001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("ok", False))
            self.assertIsNone(request_json.call_args_list[0].kwargs["json_body"])
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/noxfinansinvoices/2001/stop")

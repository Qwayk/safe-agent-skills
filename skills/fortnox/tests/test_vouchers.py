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


def _api_response(*, status: int, path: str, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": status,
        "url": f"https://api.fortnox.se/3{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


class TestVouchers(unittest.TestCase):
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

    def _make_payload_file(
        self,
        path: Path,
        *,
        voucher_series: str = "A",
        voucher_number: int = 101,
        financial_year: int | None = 2026,
    ) -> None:
        voucher: dict[str, Any] = {
            "VoucherSeries": voucher_series,
            "VoucherNumber": voucher_number,
        }
        if financial_year is not None:
            voucher["FinancialYear"] = financial_year
        path.write_text(json.dumps({"Voucher": voucher}, indent=2), encoding="utf-8")

    def test_vouchers_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path)
            expected_hash = _sha256(payload_path)

            rc, payload = self._run(
                env_path=env_path,
                args=["vouchers", "create", "--json-file", str(payload_path), "--financial-year", "2026"],
            )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), expected_hash)

    def test_vouchers_create_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.vouchers.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["vouchers", "create", "--json-file", str(payload_path), "--financial-year", "2026"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                self.assertEqual(request_json.call_count, 0)

                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                payload_path.write_text(
                    json.dumps(
                        {
                            "Voucher": {
                                "VoucherSeries": "A",
                                "VoucherNumber": 102,
                                "FinancialYear": 2026,
                            }
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "vouchers",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--financial-year",
                        "2026",
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertIn("hash", " ".join(payload_apply["reasons"]).lower())
        self.assertEqual(request_json.call_count, 0)

    def test_vouchers_create_apply_performs_post_get_verify_with_financial_year(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, financial_year=2026)

            with patch("fortnox_api_tool.commands.vouchers.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["vouchers", "create", "--json-file", str(payload_path), "--financial-year", "2025"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=201,
                        path="/vouchers",
                        body={
                            "Voucher": {
                                "VoucherSeries": "A",
                                "VoucherNumber": 101,
                                "FinancialYear": 2027,
                            }
                        },
                    ),
                    _api_response(
                        status=200,
                        path="/vouchers/A/101",
                        body={
                            "Voucher": {
                                "VoucherSeries": "A",
                                "VoucherNumber": 101,
                                "FinancialYear": 2027,
                            }
                        },
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "vouchers",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--financial-year",
                        "2025",
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[0].kwargs["method"], "POST")
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/vouchers")
        self.assertEqual(request_json.call_args_list[0].kwargs["query_params"], {"financialyear": 2025})
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/vouchers/A/101")
        self.assertEqual(request_json.call_args_list[1].kwargs["query_params"], {"financialyear": 2027})

    def test_vouchers_create_apply_fails_without_financial_year(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, financial_year=None)

            with patch("fortnox_api_tool.commands.vouchers.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["vouchers", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=201,
                        path="/vouchers",
                        body={"Voucher": {"VoucherSeries": "A", "VoucherNumber": 101}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "vouchers",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 1)
        self.assertFalse(payload_apply.get("ok", True))
        self.assertEqual(payload_apply.get("error_type"), "ValidationError")
        self.assertIn("FinancialYear", payload_apply.get("error", ""))
        self.assertEqual(request_json.call_count, 1)

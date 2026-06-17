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


def _api_response(*, status: int, path: str, body: Any) -> dict[str, Any]:
    return {
        "status": status,
        "url": f"https://api.fortnox.se/3{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


FILE_CONNECTION_FAMILIES: list[dict[str, Any]] = [
    {
        "slug": "article-file-connections",
        "path": "/articlefileconnections",
        "list_key": "ArticleFileConnections",
        "item_key": "ArticleFileConnection",
        "payload_key": "ArticleFileConnection",
        "list_args": ["--article-number", "ART-1"],
        "list_query": {"articlenumber": "ART-1"},
        "payload_body": {"ArticleNumber": "ART-1", "FileId": "FILE-1"},
        "wrapped_body": {"@url": "https://api.fortnox.se/3/articlefileconnections/FILE-1", "ArticleNumber": "ART-1", "FileId": "FILE-1"},
    },
    {
        "slug": "supplier-invoice-file-connections",
        "path": "/supplierinvoicefileconnections",
        "list_key": "SupplierInvoiceFileConnections",
        "item_key": "SupplierInvoiceFileConnection",
        "payload_key": "SupplierInvoiceFileConnection",
        "list_args": ["--supplier-invoice-number", "17"],
        "list_query": {"supplierinvoicenumber": 17},
        "payload_body": {
            "FileId": "FILE-2",
            "Name": "Invoice file",
            "SupplierInvoiceNumber": "17",
            "SupplierName": "Supplier",
        },
        "wrapped_body": {
            "@url": "https://api.fortnox.se/3/supplierinvoicefileconnections/FILE-2",
            "FileId": "FILE-2",
            "Name": "Invoice file",
            "SupplierInvoiceNumber": "17",
            "SupplierName": "Supplier",
        },
    },
    {
        "slug": "voucher-file-connections",
        "path": "/voucherfileconnections",
        "list_key": "VoucherFileConnections",
        "item_key": "VoucherFileConnection",
        "payload_key": "VoucherFileConnection",
        "list_args": [
            "--voucher-year",
            "2024",
            "--voucher-description",
            "Voucher file",
            "--voucher-number",
            "321",
            "--voucher-series",
            "A",
        ],
        "list_query": {
            "voucheryear": 2024,
            "voucherdescription": "Voucher file",
            "vouchernumber": 321,
            "voucherseries": "A",
        },
        "payload_body": {
            "FileId": "FILE-3",
            "VoucherDescription": "Voucher file",
            "VoucherNumber": 321,
            "VoucherSeries": "A",
            "VoucherYear": 2024,
        },
        "wrapped_body": {
            "@url": "https://api.fortnox.se/3/voucherfileconnections/FILE-3",
            "FileId": "FILE-3",
            "VoucherDescription": "Voucher file",
            "VoucherNumber": 321,
            "VoucherSeries": "A",
            "VoucherYear": 2024,
        },
    },
]


class TestWrappedFileConnections(unittest.TestCase):
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

    def _make_payload_file(self, path: Path, *, wrapper_key: str, body: dict[str, Any]) -> None:
        path.write_text(json.dumps({wrapper_key: body}, indent=2), encoding="utf-8")

    def test_list_wires_the_documented_query_params(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")

            with patch("fortnox_api_tool.commands.wrapped_file_connections.request_json") as request_json:
                for family in FILE_CONNECTION_FAMILIES:
                    request_json.reset_mock()
                    request_json.return_value = _api_response(
                        status=200,
                        path=family["path"],
                        body={family["list_key"]: [{"FileId": family["payload_body"]["FileId"]}]},
                    )
                    rc, payload = self._run(
                        env_path=env_path,
                        args=[family["slug"], "list", *family["list_args"]],
                    )
                    self.assertEqual(rc, 0, family["slug"])
                    self.assertTrue(payload["ok"], family["slug"])
                    self.assertEqual(payload["path"], family["path"], family["slug"])
                    self.assertEqual(request_json.call_args.kwargs["path"], family["path"], family["slug"])
                    self.assertEqual(request_json.call_args.kwargs.get("query_params"), family["list_query"], family["slug"])

    def test_get_reads_the_documented_single_item_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")

            with patch("fortnox_api_tool.commands.wrapped_file_connections.request_json") as request_json:
                for family in FILE_CONNECTION_FAMILIES:
                    request_json.reset_mock()
                    request_json.return_value = _api_response(
                        status=200,
                        path=f'{family["path"]}/{family["payload_body"]["FileId"]}',
                        body={family["item_key"]: family["wrapped_body"]},
                    )
                    rc, payload = self._run(
                        env_path=env_path,
                        args=[family["slug"], "get", "--file-id", family["payload_body"]["FileId"]],
                    )
                    self.assertEqual(rc, 0, family["slug"])
                    self.assertTrue(payload["ok"], family["slug"])
                    self.assertEqual(payload["path"], f'{family["path"]}/{family["payload_body"]["FileId"]}', family["slug"])
                    self.assertEqual(
                        request_json.call_args.kwargs["path"],
                        f'{family["path"]}/{family["payload_body"]["FileId"]}',
                        family["slug"],
                    )

    def test_create_dry_run_emits_plans_for_all_three_families(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")

            for family in FILE_CONNECTION_FAMILIES:
                payload_path = Path(td) / f'{family["slug"]}.json'
                self._make_payload_file(payload_path, wrapper_key=family["payload_key"], body=family["payload_body"])

                with patch("fortnox_api_tool.commands.wrapped_file_connections.request_json") as request_json:
                    rc, payload = self._run(
                        env_path=env_path,
                        args=[family["slug"], "create", "--json-file", str(payload_path)],
                    )

                self.assertEqual(rc, 0, family["slug"])
                self.assertTrue(payload["ok"], family["slug"])
                self.assertTrue(payload["dry_run"], family["slug"])
                self.assertEqual(payload["plan"]["baseline"]["payload_sha256"], _sha256(payload_path), family["slug"])
                self.assertEqual(request_json.call_count, 0, family["slug"])

    def test_create_apply_posts_then_reads_back_the_same_file_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")

            for family in FILE_CONNECTION_FAMILIES:
                payload_path = Path(td) / f'{family["slug"]}.json'
                self._make_payload_file(payload_path, wrapper_key=family["payload_key"], body=family["payload_body"])

                with patch("fortnox_api_tool.commands.wrapped_file_connections.request_json") as request_json:
                    rc, plan_payload = self._run(
                        env_path=env_path,
                        args=[family["slug"], "create", "--json-file", str(payload_path)],
                    )
                    self.assertEqual(rc, 0, family["slug"])
                    plan = self._plan_from_output(plan_payload)
                    plan_path = Path(td) / f'{family["slug"]}.plan.json'
                    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                    request_json.side_effect = [
                        _api_response(
                            status=201,
                            path=family["path"],
                            body={family["item_key"]: family["wrapped_body"]},
                        ),
                        _api_response(
                            status=200,
                            path=f'{family["path"]}/{family["payload_body"]["FileId"]}',
                            body={family["item_key"]: family["wrapped_body"]},
                        ),
                    ]
                    rc_apply, payload_apply = self._run(
                        env_path=env_path,
                        args=[
                            family["slug"],
                            "create",
                            "--json-file",
                            str(payload_path),
                            "--apply",
                            "--plan-in",
                            str(plan_path),
                        ],
                    )

                self.assertEqual(rc_apply, 0, family["slug"])
                self.assertTrue(payload_apply["ok"], family["slug"])
                self.assertEqual(request_json.call_args_list[0].kwargs["method"], "POST", family["slug"])
                self.assertEqual(request_json.call_args_list[0].kwargs["path"], family["path"], family["slug"])
                self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET", family["slug"])
                self.assertEqual(
                    request_json.call_args_list[1].kwargs["path"],
                    f'{family["path"]}/{family["payload_body"]["FileId"]}',
                    family["slug"],
                )

    def test_remove_dry_run_then_apply_removes_and_proves_absence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")

            for family in FILE_CONNECTION_FAMILIES:
                with patch("fortnox_api_tool.commands.wrapped_file_connections.request_json") as request_json:
                    rc, plan_payload = self._run(
                        env_path=env_path,
                        args=[family["slug"], "remove", "--file-id", family["payload_body"]["FileId"]],
                    )
                    self.assertEqual(rc, 0, family["slug"])
                    plan = self._plan_from_output(plan_payload)
                    plan_path = Path(td) / f'{family["slug"]}.remove.plan.json'
                    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                    request_json.side_effect = [
                        _api_response(
                            status=204,
                            path=f'{family["path"]}/{family["payload_body"]["FileId"]}',
                            body=None,
                        ),
                        RuntimeError("HTTP 404 Not Found"),
                    ]
                    rc_apply, payload_apply = self._run(
                        env_path=env_path,
                        args=[
                            family["slug"],
                            "remove",
                            "--file-id",
                            family["payload_body"]["FileId"],
                            "--apply",
                            "--yes",
                            "--ack-irreversible",
                            "--plan-in",
                            str(plan_path),
                        ],
                    )

                self.assertEqual(rc_apply, 0, family["slug"])
                self.assertTrue(payload_apply["ok"], family["slug"])
                self.assertEqual(request_json.call_args_list[0].kwargs["method"], "DELETE", family["slug"])
                self.assertEqual(
                    request_json.call_args_list[0].kwargs["path"],
                    f'{family["path"]}/{family["payload_body"]["FileId"]}',
                    family["slug"],
                )
                self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET", family["slug"])

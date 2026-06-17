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


class TestAssets(unittest.TestCase):
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

    def _make_asset_payload_file(self, path: Path, *, asset_id: int | None = 1, number: str = "AST-1") -> None:
        payload = {
            "Asset": {
                "Id": asset_id,
                "Number": number,
                "Description": "Machine",
            }
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _make_changeob_payload_file(self, path: Path) -> None:
        payload = {
            "Amount": 2500,
            "Comment": "Adjust OB",
            "Date": "2026-06-15",
            "TransactionDate": "2026-06-15",
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_assets_list_reads_the_official_collection(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")

            with patch("fortnox_api_tool.commands.assets.get_json") as get_json:
                get_json.return_value = _api_response(status=200, path="/assets", body={"Assets": []})
                rc, payload = self._run(env_path=env_path, args=["assets", "list"])

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/assets")

    def test_assets_get_reads_one_asset(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")

            with patch("fortnox_api_tool.commands.assets.get_json") as get_json:
                get_json.return_value = _api_response(status=200, path="/assets/1", body={"Assets": {"Id": 1}})
                rc, payload = self._run(env_path=env_path, args=["assets", "get", "--id", "1"])

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/assets/1")

    def test_assets_depreciation_list_reads_the_report_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")

            with patch("fortnox_api_tool.commands.assets.get_json") as get_json:
                get_json.return_value = _api_response(
                    status=200,
                    path="/assets/depreciations/2026-06-15",
                    body={"AssetsDepreciation": []},
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=["assets", "assets-depreciation-list", "--to-date", "2026-06-15"],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/assets/depreciations/2026-06-15")

    def test_assets_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "create.json"
            self._make_asset_payload_file(payload_path, asset_id=None, number="AST-NEW")
            expected_hash = _sha256(payload_path)

            with patch("fortnox_api_tool.commands.assets.request_json") as request_json:
                rc, payload = self._run(env_path=env_path, args=["assets", "create", "--json-file", str(payload_path)])

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), expected_hash)
        self.assertEqual(request_json.call_count, 0)

    def test_assets_create_apply_uses_response_id_for_verification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "create.json"
            self._make_asset_payload_file(payload_path, asset_id=None, number="AST-NEW")

            with patch("fortnox_api_tool.commands.assets.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["assets", "create", "--json-file", str(payload_path)])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=200, path="/assets", body={"Assets": {"Id": 9, "Number": "AST-NEW"}}),
                    _api_response(status=200, path="/assets/9", body={"Assets": {"Id": 9, "Number": "AST-NEW"}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=["assets", "create", "--json-file", str(payload_path), "--apply", "--plan-in", str(plan_path)],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[0].kwargs["method"], "POST")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/assets/9")

    def test_assets_update_rejects_payload_id_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "update.json"
            self._make_asset_payload_file(payload_path, asset_id=2, number="AST-2")

            rc, payload = self._run(env_path=env_path, args=["assets", "update", "--id", "1", "--json-file", str(payload_path)])

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("Asset.Id", payload["error"])

    def test_assets_delete_apply_performs_delete_and_404_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")

            with patch("fortnox_api_tool.commands.assets.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["assets", "delete", "--id", "1"])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=204, path="/assets/1", body=None),
                    Exception("HTTP 404 for GET /assets/1"),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=["assets", "delete", "--id", "1", "--apply", "--yes", "--ack-irreversible", "--plan-in", str(plan_path)],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[0].kwargs["method"], "DELETE")

    def test_assets_change_manual_ob_apply_requires_yes_and_detects_change(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "changeob.json"
            self._make_changeob_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.assets.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["assets", "change-manual-ob-value-of-an-asset", "--id", "1", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=200, path="/assets/1", body={"Assets": {"Id": 1, "ManualOb": 1000}}),
                    _api_response(status=200, path="/assets/changeob/1", body={"Assets": {"Id": 1, "ManualOb": 2500}}),
                    _api_response(status=200, path="/assets/1", body={"Assets": {"Id": 1, "ManualOb": 2500}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "assets",
                        "change-manual-ob-value-of-an-asset",
                        "--id",
                        "1",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/assets/changeob/1")

    def test_assets_depreciate_apply_requires_yes_and_checks_response_rows(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "depreciate.json"
            self._make_asset_payload_file(payload_path, asset_id=1, number="AST-1")

            with patch("fortnox_api_tool.commands.assets.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["assets", "perform-a-depreciation-of-an-asset", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.return_value = _api_response(
                    status=200,
                    path="/assets/depreciate",
                    body={"AssetsDepreciation": [{"VoucherNumber": 1001}]},
                )
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "assets",
                        "perform-a-depreciation-of-an-asset",
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
        self.assertEqual(request_json.call_args.kwargs["method"], "POST")

    def test_assets_scrap_apply_requires_ack_and_detects_change(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "scrap.json"
            self._make_asset_payload_file(payload_path, asset_id=1, number="AST-1")

            with patch("fortnox_api_tool.commands.assets.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["assets", "scrap-an-asset", "--id", "1", "--json-file", str(payload_path)])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=200, path="/assets/1", body={"Assets": {"Id": 1, "Status": "active"}}),
                    _api_response(status=200, path="/assets/scrap/1", body={"Assets": {"Id": 1, "Status": "scrapped"}}),
                    _api_response(status=200, path="/assets/1", body={"Assets": {"Id": 1, "Status": "scrapped"}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "assets",
                        "scrap-an-asset",
                        "--id",
                        "1",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/assets/scrap/1")

    def test_assets_scrap_apply_without_ack_no_snapshot_refuses_before_any_http(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "scrap.json"
            self._make_asset_payload_file(payload_path, asset_id=1, number="AST-1")

            with patch("fortnox_api_tool.commands.assets.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["assets", "scrap-an-asset", "--id", "1", "--json-file", str(payload_path)])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "assets",
                        "scrap-an-asset",
                        "--id",
                        "1",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertIn("--ack-no-snapshot", " ".join(payload_apply["reasons"]))
        self.assertEqual(request_json.call_count, 0)

    def test_assets_sell_apply_requires_ack_and_detects_change(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "sell.json"
            self._make_asset_payload_file(payload_path, asset_id=1, number="AST-1")

            with patch("fortnox_api_tool.commands.assets.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["assets", "sell-an-asset", "--id", "1", "--json-file", str(payload_path)])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=200, path="/assets/1", body={"Assets": {"Id": 1, "Status": "active"}}),
                    _api_response(status=200, path="/assets/sell/1", body={"Assets": {"Id": 1, "Status": "sold"}}),
                    _api_response(status=200, path="/assets/1", body={"Assets": {"Id": 1, "Status": "sold"}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "assets",
                        "sell-an-asset",
                        "--id",
                        "1",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/assets/sell/1")

    def test_assets_write_down_apply_detects_change(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "writedown.json"
            self._make_asset_payload_file(payload_path, asset_id=1, number="AST-1")

            with patch("fortnox_api_tool.commands.assets.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["assets", "write-down-an-asset", "--id", "1", "--json-file", str(payload_path)])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=200, path="/assets/1", body={"Assets": {"Id": 1, "Status": "active"}}),
                    _api_response(status=200, path="/assets/writedown/1", body={"Assets": {"Id": 1, "Status": "written-down"}}),
                    _api_response(status=200, path="/assets/1", body={"Assets": {"Id": 1, "Status": "written-down"}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "assets",
                        "write-down-an-asset",
                        "--id",
                        "1",
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

    def test_assets_write_up_apply_detects_change(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "writeup.json"
            self._make_asset_payload_file(payload_path, asset_id=1, number="AST-1")

            with patch("fortnox_api_tool.commands.assets.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["assets", "write-up-an-asset", "--id", "1", "--json-file", str(payload_path)])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=200, path="/assets/1", body={"Assets": {"Id": 1, "Status": "written-down"}}),
                    _api_response(status=200, path="/assets/writeup/1", body={"Assets": {"Id": 1, "Status": "active"}}),
                    _api_response(status=200, path="/assets/1", body={"Assets": {"Id": 1, "Status": "active"}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "assets",
                        "write-up-an-asset",
                        "--id",
                        "1",
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

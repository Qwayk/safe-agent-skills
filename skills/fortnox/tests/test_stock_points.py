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
        "url": f"https://api.fortnox.se{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


class TestStockPoints(unittest.TestCase):
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
        self.assertIsInstance(plan_out, str)
        return json.loads(Path(plan_out).read_text(encoding="utf-8"))

    def _write_env(self, td: str) -> Path:
        env_path = Path(td) / ".env"
        env_path.write_text(
            "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
            encoding="utf-8",
        )
        return env_path

    def _write_json(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_stock_points_list_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_points.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/warehouse/stockpoints-v1",
                    body=[{"id": "sp-1"}],
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=["stock-points", "list", "--q", "Main", "--state", "ACTIVE"],
                )

        self.assertEqual(rc, 0)
        self.assertEqual(payload["path"], "/api/warehouse/stockpoints-v1")
        self.assertEqual(request_data.call_args.kwargs["query_params"], {"q": "Main", "state": "ACTIVE"})

    def test_stock_points_list_multi_uses_ids_query(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_points.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/warehouse/stockpoints-v1/multi",
                    body=[{"id": "sp-1"}, {"id": "sp-2"}],
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=["stock-points", "list-multi", "--id", "sp-1", "--id", "sp-2", "--state", "ALL"],
                )

        self.assertEqual(rc, 0)
        self.assertEqual(payload["path"], "/api/warehouse/stockpoints-v1/multi")
        self.assertEqual(request_data.call_args.kwargs["query_params"], {"ids": "sp-1,sp-2", "state": "ALL"})

    def test_stock_points_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_points.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/warehouse/stockpoints-v1/main",
                    body={"id": "sp-1", "code": "MAIN"},
                )
                rc, payload = self._run(env_path=env_path, args=["stock-points", "get", "--id", "MAIN"])

        self.assertEqual(rc, 0)
        self.assertEqual(payload["path"], "/api/warehouse/stockpoints-v1/MAIN")
        self.assertEqual(request_data.call_args.kwargs["path"], "/api/warehouse/stockpoints-v1/MAIN")

    def test_stock_points_get_stock_locations_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_points.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/warehouse/stockpoints-v1/MAIN/stocklocations",
                    body=[{"code": "A-1"}],
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=["stock-points", "get-stock-locations", "--id", "MAIN", "--q", "A"],
                )

        self.assertEqual(rc, 0)
        self.assertEqual(payload["path"], "/api/warehouse/stockpoints-v1/MAIN/stocklocations")
        self.assertEqual(request_data.call_args.kwargs["query_params"], {"q": "A"})

    def test_stock_points_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "stock_point.json"
            self._write_json(payload_path, {"code": "MAIN", "name": "Main warehouse"})
            expected_hash = _sha256(payload_path)

            with patch("fortnox_api_tool.commands.stock_points.request_data") as request_data:
                rc, payload = self._run(
                    env_path=env_path,
                    args=["stock-points", "create", "--json-file", str(payload_path)],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["baseline"]["payload_sha256"], expected_hash)
        self.assertEqual(request_data.call_count, 0)

    def test_stock_points_create_apply_uses_response_id_for_verification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "stock_point.json"
            self._write_json(payload_path, {"code": "MAIN", "name": "Main warehouse"})

            with patch("fortnox_api_tool.commands.stock_points.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["stock-points", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=201, path="/api/warehouse/stockpoints-v1", body={"id": "sp-1", "code": "MAIN"}),
                    _api_response(status=200, path="/api/warehouse/stockpoints-v1/sp-1", body={"id": "sp-1", "code": "MAIN"}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-points",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertEqual(request_data.call_args_list[0].kwargs["path"], "/api/warehouse/stockpoints-v1")
        self.assertEqual(request_data.call_args_list[1].kwargs["path"], "/api/warehouse/stockpoints-v1/sp-1")
        self.assertEqual(payload_apply["receipt"]["target_id_or_code"], "sp-1")

    def test_stock_points_update_rejects_payload_id_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "stock_point_update.json"
            self._write_json(payload_path, {"id": "sp-2", "code": "MAIN", "name": "Main warehouse"})

            rc, payload = self._run(
                env_path=env_path,
                args=["stock-points", "update", "--id", "sp-1", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("must match --id", payload["error"])

    def test_stock_points_update_apply_verifies_selected_fields(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "stock_point_update.json"
            self._write_json(
                payload_path,
                {"id": "sp-1", "code": "MAIN", "name": "Main warehouse", "active": True, "usingCompanyAddress": False},
            )

            with patch("fortnox_api_tool.commands.stock_points.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["stock-points", "update", "--id", "sp-1", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=200, path="/api/warehouse/stockpoints-v1/sp-1", body={"id": "sp-1"}),
                    _api_response(
                        status=200,
                        path="/api/warehouse/stockpoints-v1/sp-1",
                        body={"id": "sp-1", "code": "MAIN", "name": "Main warehouse", "active": True, "usingCompanyAddress": False},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-points",
                        "update",
                        "--id",
                        "sp-1",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertTrue(payload_apply["receipt"]["verification"]["verification_selected_fields_match"])

    def test_stock_points_append_stock_locations_rejects_wrapped_payload(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "stock_locations_wrapped.json"
            self._write_json(payload_path, {"stockLocations": [{"code": "A-1"}]})

            rc, payload = self._run(
                env_path=env_path,
                args=["stock-points", "append-stock-locations", "--id", "sp-1", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("raw top-level array", payload["error"])

    def test_stock_points_append_stock_locations_apply_posts_raw_array(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "stock_locations.json"
            payload_rows = [{"code": "A-1", "name": "Aisle 1"}]
            self._write_json(payload_path, payload_rows)

            with patch("fortnox_api_tool.commands.stock_points.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["stock-points", "append-stock-locations", "--id", "sp-1", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=201, path="/api/warehouse/stockpoints-v1/sp-1", body=[{"code": "A-1"}]),
                    _api_response(status=200, path="/api/warehouse/stockpoints-v1/sp-1/stocklocations", body=[{"code": "A-1"}]),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-points",
                        "append-stock-locations",
                        "--id",
                        "sp-1",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertEqual(request_data.call_args_list[0].kwargs["json_body"], payload_rows)
        self.assertTrue(payload_apply["receipt"]["verification"]["verification_stock_location_codes_present"])

    def test_stock_points_delete_refuses_without_ack(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_points.request_data") as request_data:
                rc, plan_payload = self._run(env_path=env_path, args=["stock-points", "delete", "--id", "sp-1"])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=["stock-points", "delete", "--id", "sp-1", "--apply", "--yes", "--plan-in", str(plan_path)],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertEqual(request_data.call_count, 0)
        self.assertIn("ack-irreversible", " ".join(payload_apply["reasons"]).lower())

    def test_stock_points_delete_apply_verifies_absence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_points.request_data") as request_data:
                rc, plan_payload = self._run(env_path=env_path, args=["stock-points", "delete", "--id", "sp-1"])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=200, path="/api/warehouse/stockpoints-v1/sp-1", body={"id": "sp-1"}),
                    Exception("HTTP 404 for GET /api/warehouse/stockpoints-v1/sp-1"),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-points",
                        "delete",
                        "--id",
                        "sp-1",
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertEqual(request_data.call_args_list[0].kwargs["method"], "DELETE")
        self.assertTrue(payload_apply["receipt"]["verification"]["verification_absent"])

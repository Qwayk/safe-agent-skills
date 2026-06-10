from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ._helpers import FakeResponse, assert_blocked_before_state, run_cli, write_env


class TestOperationSafety(unittest.TestCase):
    def test_path_params_are_percent_encoded_before_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = write_env(root, product_context=True, product_auth=True)
            seen: dict[str, str] = {}

            def _request(*args, **kwargs):
                seen["url"] = str(kwargs.get("url") or "")
                return FakeResponse(payload={"asset_id": "asset-1"}, url=seen["url"])

            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "operations",
                    "admin",
                    "resources-get-details-of-a-single-resource-by-public-id",
                    "--path-param",
                    "resource_type=image",
                    "--path-param",
                    "type=upload",
                    "--path-param",
                    "public_id=folder/a b",
                ],
                request_side_effect=_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertIn("/folder%2Fa%20b", seen["url"])
            self.assertNotIn("/folder/a b", seen["url"])

    def test_delete_like_operations_require_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = write_env(root, product_context=True)
            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "--apply",
                    "--yes",
                    "operations",
                    "admin",
                    "folders-delete-folder",
                    "--path-param",
                    "folder=archive/old",
                ]
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("--ack-irreversible", payload["reasons"][0])

    def test_plan_in_rejects_path_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = write_env(root, product_context=True)
            plan_path = root / "delete-folder-plan.json"

            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "--plan-out",
                    str(plan_path),
                    "operations",
                    "admin",
                    "folders-delete-folder",
                    "--path-param",
                    "folder=archive/old",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertTrue(plan_path.exists())
            assert_blocked_before_state(self, payload["plan"])

            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "--plan-in",
                    str(plan_path),
                    "operations",
                    "admin",
                    "folders-delete-folder",
                    "--path-param",
                    "folder=archive/new",
                ]
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("plan method or path does not match", payload["reasons"][0])

    def test_sensitive_reads_require_out(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = write_env(root, product_context=True)
            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "operations",
                    "live_streaming",
                    "getlivestreams",
                ]
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("Re-run with --out", payload["reasons"][0])

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cloudinary_safe_agent_cli.inventory import find_operation

from ._helpers import assert_blocked_before_state, build_cli_args_for_spec, env_for_spec, run_cli, spec_for_area, write_env


def _restore_by_public_id_plan_args() -> list[str]:
    return [
        "operations",
        "admin",
        "resources-restore-resources-by-public-id",
        "--path-param",
        "resource_type=image",
        "--path-param",
        "type=upload",
        "--path-param",
        "public_id=sample-public-id",
    ]


class TestAdminOperations(unittest.TestCase):
    def test_restore_operations_are_wired_and_write_capable(self) -> None:
        by_public_id = find_operation(area="admin", op_key="resources-restore-resources-by-public-id")
        by_asset_id = find_operation(area="admin", op_key="resources-restore-resources-by-asset-id")
        delete_backed_up = find_operation(
            area="admin", op_key="resources-delete-backed-up-versions-of-a-resource"
        )

        self.assertIsNotNone(by_public_id)
        self.assertIsNotNone(by_asset_id)
        self.assertIsNotNone(delete_backed_up)
        self.assertTrue(by_public_id.is_write)
        self.assertTrue(by_asset_id.is_write)
        self.assertTrue(delete_backed_up.is_write)
        self.assertEqual(by_public_id.method, "POST")
        self.assertEqual(by_asset_id.method, "POST")
        self.assertEqual(delete_backed_up.method, "DELETE")

    def test_admin_area_has_a_runnable_explicit_command(self) -> None:
        spec = spec_for_area("admin")
        self.assertTrue(spec.is_write)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = env_for_spec(root, spec)
            rc, payload = run_cli(build_cli_args_for_spec(root, spec, env_path))
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            assert_blocked_before_state(self, payload["plan"])

    def test_restore_by_public_id_apply_refuses_without_before_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = find_operation(area="admin", op_key="resources-restore-resources-by-public-id")
            self.assertIsNotNone(spec)
            env_path = env_for_spec(root, spec)
            env_path_auth = write_env(root, product_context=True, product_auth=True)
            plan_path = root / "restore-plan.json"

            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "--plan-out",
                    str(plan_path),
                    *_restore_by_public_id_plan_args(),
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
                    str(env_path_auth),
                    "--apply",
                    "--yes",
                    "--plan-in",
                    str(plan_path),
                    *_restore_by_public_id_plan_args(),
                ],
                request_side_effect=AssertionError("Cloudinary HTTP should not run without before-state"),
            )
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["refused"])
            assert_blocked_before_state(self, payload["plan"])

    def test_restore_by_public_id_requires_yes_for_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = find_operation(area="admin", op_key="resources-restore-resources-by-public-id")
            self.assertIsNotNone(spec)
            env_path = env_for_spec(root, spec)
            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--apply",
                    "--env-file",
                    str(env_path),
                    *_restore_by_public_id_plan_args(),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("writes require --yes", payload["reasons"][0])

    def test_delete_backed_up_versions_of_a_resource_is_write_like(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = find_operation(area="admin", op_key="resources-delete-backed-up-versions-of-a-resource")
            self.assertIsNotNone(spec)
            env_path = env_for_spec(root, spec)
            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "operations",
                    "admin",
                    "resources-delete-backed-up-versions-of-a-resource",
                    "--path-param",
                    "asset_id=sample-asset-id",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertTrue(payload["ok"])
            assert_blocked_before_state(self, payload["plan"])

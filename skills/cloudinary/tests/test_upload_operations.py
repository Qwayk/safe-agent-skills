from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cloudinary_safe_agent_cli.inventory import find_operation

from ._helpers import FakeResponse, assert_blocked_before_state, build_cli_args_for_spec, env_for_spec, run_cli, spec_for_area, write_env


class TestUploadOperations(unittest.TestCase):
    def test_upload_area_has_a_runnable_explicit_command(self) -> None:
        spec = spec_for_area("upload")
        self.assertTrue(spec.is_write)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = env_for_spec(root, spec)
            rc, payload = run_cli(build_cli_args_for_spec(root, spec, env_path))
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            assert_blocked_before_state(self, payload["plan"])

    def test_download_backup_requires_output_file(self) -> None:
        spec = find_operation(area="upload", op_key="download-backup")
        self.assertIsNotNone(spec)
        self.assertFalse(spec.is_write)
        self.assertTrue(spec.requires_out)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = env_for_spec(root, spec)
            env_path_auth = write_env(root, product_context=True, product_auth=True)
            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "--project-dir",
                    str(root),
                    "operations",
                    "upload",
                    "download-backup",
                    "--query",
                    "public_id=sample-public-id",
                    "--query",
                    "version_id=123",
                    "--query",
                    "resource_type=image",
                    "--query",
                    "type=upload",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("Re-run with --out", payload["reasons"][0])

            output_path = root / "sample-backup.bin"
            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path_auth),
                    "--project-dir",
                    str(root),
                    "operations",
                    "upload",
                    "download-backup",
                    "--query",
                    "public_id=sample-public-id",
                    "--query",
                    "version_id=123",
                    "--query",
                    "resource_type=image",
                    "--query",
                    "type=upload",
                    "--out",
                    str(output_path),
                    "--overwrite",
                ],
                request_side_effect=lambda *args, **kwargs: FakeResponse(status_code=200, text="backup-binary"),
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertTrue(output_path.exists())

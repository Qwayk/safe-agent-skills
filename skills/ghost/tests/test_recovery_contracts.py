import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from ghost_api_tool.cli import main as cli_main


class RecoveryContractTests(unittest.TestCase):
    def _write_env(self, root: str) -> str:
        env_path = os.path.join(root, ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("GHOST_ADMIN_API_URL=https://example.com/ghost/api/admin/\n")
            f.write("GHOST_ADMIN_API_KEY=abc:" + "00" * 32 + "\n")
            f.write("GHOST_ACCEPT_VERSION=v5.0\n")
            f.write("GHOST_TIMEOUT_S=5\n")
        return env_path

    def test_post_patch_plan_and_receipt_expose_snapshot_restore_contract(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            patch_path = os.path.join(td, "patch.json")
            with open(patch_path, "w", encoding="utf-8") as f:
                json.dump({"title": "After"}, f)

            def fake_post_patch(args, ctx):
                if not ctx["apply"]:
                    ctx["out"].print(
                        {
                            "apply": False,
                            "refused": False,
                            "plan": {
                                "target": {"id": "p1", "slug": "example-post"},
                                "changes": {"title": "After"},
                                "writes": [
                                    {
                                        "type": "ghost_admin_api",
                                        "method": "PUT",
                                        "path": "/posts/p1/",
                                    }
                                ],
                            },
                        }
                    )
                    return 0

                backup = ctx.get("backup")
                if backup is not None:
                    backup.write_before_after(
                        kind="post",
                        resource_id="p1",
                        slug="example-post",
                        action="post.patch",
                        before={"posts": [{"id": "p1", "title": "Before"}]},
                        after={"posts": [{"id": "p1", "title": "After"}]},
                        meta={"stage": "after", "correlation_id": "test-post-patch"},
                    )
                ctx["out"].print(
                    {
                        "ok": True,
                        "receipt": {
                            "target": {"id": "p1", "slug": "example-post"},
                            "applied": [
                                {
                                    "type": "ghost_admin_api",
                                    "method": "PUT",
                                    "path": "/posts/p1/",
                                    "status": "ok",
                                }
                            ],
                            "verification": {
                                "method": "read_back",
                                "note": "Re-fetched the post after apply and confirmed requested fields match.",
                            },
                        },
                    }
                )
                return 0

            with patch("ghost_api_tool.commands.post.cmd_post_patch", fake_post_patch):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cli_main(["--env-file", env_path, "--output", "json", "post", "patch", "--id", "p1", "--file", patch_path])
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertEqual(payload["recovery"]["end_state"], "snapshot_plus_restore")
                self.assertFalse(payload["recovery"]["rollback_ready"])
                self.assertEqual(payload["plan"]["recovery"]["end_state"], "snapshot_plus_restore")
                self.assertEqual(
                    os.path.realpath(payload["plan"]["recovery"]["backups"][0]["path"]),
                    os.path.realpath(os.path.join(td, "backup-snapshots")),
                )

                plan_path = os.path.join(payload["artifacts_dir"], "plan.json")
                with open(plan_path, encoding="utf-8") as f:
                    plan_obj = json.load(f)
                self.assertEqual(plan_obj["recovery"]["end_state"], "snapshot_plus_restore")
                self.assertFalse(plan_obj["recovery"]["rollback_ready"])

                buf2 = io.StringIO()
                with redirect_stdout(buf2):
                    rc2 = cli_main(
                        [
                            "--env-file",
                            env_path,
                            "--output",
                            "json",
                            "--apply",
                            "post",
                            "patch",
                            "--id",
                            "p1",
                            "--file",
                            patch_path,
                        ]
                    )
                self.assertEqual(rc2, 0)
                payload2 = json.loads(buf2.getvalue())
                self.assertEqual(payload2["recovery"]["end_state"], "snapshot_plus_restore")
                self.assertTrue(payload2["recovery"]["rollback_ready"])
                self.assertEqual(payload2["rollback_plan"]["type"], "manual_restore_from_snapshot")
                self.assertEqual(payload2["receipt"]["recovery"]["end_state"], "snapshot_plus_restore")
                self.assertTrue(payload2["receipt"]["recovery"]["rollback_ready"])
                self.assertEqual(len(payload2["backups"]), 1)
                self.assertEqual(len(payload2["receipt"]["recovery"]["snapshots"]), 1)
                self.assertTrue(payload2["receipt"]["recovery"]["snapshots"][0]["before"].endswith("__before.json"))
                self.assertTrue(payload2["receipt"]["recovery"]["snapshots"][0]["after"].endswith("__after.json"))

                receipt_path = os.path.join(payload2["artifacts_dir"], "receipt.json")
                with open(receipt_path, encoding="utf-8") as f:
                    receipt_obj = json.load(f)
                self.assertEqual(receipt_obj["recovery"]["end_state"], "snapshot_plus_restore")
                self.assertTrue(receipt_obj["recovery"]["rollback_ready"])
                self.assertEqual(len(receipt_obj["backups"]), 1)
                self.assertEqual(len(receipt_obj["recovery"]["snapshots"]), 1)

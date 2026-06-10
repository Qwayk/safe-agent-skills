import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from ghost_api_tool.cli import main as cli_main


class BeforeStateApplyGateTests(unittest.TestCase):
    def _write_env(self, root: str) -> str:
        env_path = os.path.join(root, ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("GHOST_ADMIN_API_URL=https://example.com/ghost/api/admin/\n")
            f.write("GHOST_ADMIN_API_KEY=abc:" + "00" * 32 + "\n")
            f.write("GHOST_ACCEPT_VERSION=v5.0\n")
            f.write("GHOST_TIMEOUT_S=5\n")
        return env_path

    def test_post_copy_apply_is_blocked_before_live_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)

            def fake_post_copy(args, ctx):
                if ctx["apply"]:
                    raise AssertionError("live apply should be requires explicit no-snapshot approval before cmd_post_copy runs")
                ctx["out"].print(
                    {
                        "apply": False,
                        "refused": False,
                        "copy": {"from_id": "p1", "from_slug": "from", "from_title": "From"},
                    }
                )
                return 0

            with patch("ghost_api_tool.commands.post.cmd_post_copy", fake_post_copy):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cli_main(["--env-file", env_path, "--output", "json", "--apply", "post", "copy", "--id", "p1"])
                self.assertEqual(rc, 0)
                obj = json.loads(buf.getvalue())
                self.assertTrue(obj["refused"])
                self.assertIn("post.copy", obj["reasons"][0])

            buf2 = io.StringIO()
            with patch("ghost_api_tool.commands.post.cmd_post_copy", fake_post_copy):
                with redirect_stdout(buf2):
                    rc2 = cli_main(["--env-file", env_path, "--output", "json", "post", "copy", "--id", "p1"])
                self.assertEqual(rc2, 0)
                obj2 = json.loads(buf2.getvalue())
                plan_path = os.path.join(obj2["artifacts_dir"], "plan.json")
                with open(plan_path, encoding="utf-8") as f:
                    plan_obj = json.load(f)
                gate = plan_obj["raw_plan"]["before_state_apply_gate"]
                self.assertTrue(gate["blocked"])
                self.assertIn("post.copy", gate["reason"])

    def test_page_sync_md_create_apply_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            md_path = os.path.join(td, "page.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write("# Hello\n")

            def fake_page_sync_md(args, ctx):
                if ctx["apply"]:
                    raise AssertionError("live apply should be requires explicit no-snapshot approval before cmd_page_sync_md runs")
                ctx["out"].print(
                    {
                        "apply": False,
                        "refused": False,
                        "reasons": [],
                        "actions": [
                            {
                                "action": "create",
                                "title": "Hello",
                                "slug": "hello",
                                "status": "draft",
                                "visibility": "public",
                            }
                        ],
                    }
                )
                return 0

            with patch("ghost_api_tool.commands.page.cmd_page_sync_md", fake_page_sync_md):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cli_main(
                        [
                            "--env-file",
                            env_path,
                            "--output",
                            "json",
                            "--apply",
                            "page",
                            "sync-md",
                            "--slug",
                            "hello",
                            "--title",
                            "Hello",
                            "--md-file",
                            md_path,
                        ]
                    )
                self.assertEqual(rc, 0)
                obj = json.loads(buf.getvalue())
                self.assertTrue(obj["refused"])
                self.assertIn("page.sync-md", obj["reasons"][0])

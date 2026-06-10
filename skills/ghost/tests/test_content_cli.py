import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

import ghost_api_tool.commands.content as content_cmd
from ghost_api_tool.cli import main as cli_main


class ContentCliTests(unittest.TestCase):
    def _write_env(self, root: str, *, include_content: bool) -> str:
        env_path = os.path.join(root, ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            if include_content:
                f.write("GHOST_CONTENT_API_URL=https://example.com/ghost/api/content/\n")
                f.write("GHOST_CONTENT_API_KEY=deadbeef\n")
            f.write("GHOST_ACCEPT_VERSION=v5.0\n")
            f.write("GHOST_TIMEOUT_S=5\n")
        return env_path

    def test_content_help_is_single_json_object_in_json_mode(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli_main(["--output", "json", "content", "--help"])
        self.assertEqual(rc, 0)
        obj = json.loads(buf.getvalue())
        self.assertTrue(obj["ok"])
        self.assertEqual(obj.get("kind"), "help")
        self.assertIn("usage: ghost-api-tool content", obj.get("help") or "")

    def test_content_commands_require_content_env_vars_not_admin_env_vars(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td, include_content=False)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli_main(["--env-file", env_path, "--output", "json", "content", "posts", "list", "--limit", "1"])
            self.assertNotEqual(rc, 0)
            obj = json.loads(buf.getvalue())
            self.assertFalse(obj["ok"])
            self.assertIn("GHOST_CONTENT_API_URL", obj.get("error") or "")
            self.assertNotIn("GHOST_ADMIN_API_URL", obj.get("error") or "")

    def test_content_commands_do_not_require_admin_config(self):
        original = content_cmd.get_content_api

        class FakeContentApi:
            def posts_browse(self, *, params=None):
                return {"posts": [], "meta": {"pagination": {"page": 1, "limit": 1, "pages": 1, "total": 0}}}

        try:
            content_cmd.get_content_api = lambda _ctx: FakeContentApi()  # type: ignore[assignment]
            with tempfile.TemporaryDirectory() as td:
                env_path = self._write_env(td, include_content=True)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cli_main(
                        ["--env-file", env_path, "--output", "json", "content", "posts", "list", "--limit", "1", "--page", "1"]
                    )
                self.assertEqual(rc, 0)
                obj = json.loads(buf.getvalue())
                self.assertTrue(obj["ok"])
                self.assertEqual(obj.get("kind"), "content.posts.list")
        finally:
            content_cmd.get_content_api = original  # type: ignore[assignment]


from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from youtube_api_tool.cli import main


class TestChannelsResolvePlanOnly(unittest.TestCase):
    def _env_file(self, root: Path) -> Path:
        env_path = root / ".env"
        env_path.write_text("YOUTUBE_API_BASE_URL=http://example.invalid\nYOUTUBE_TIMEOUT_S=30\n", encoding="utf-8")
        return env_path

    def test_plan_only_channel_id_uses_channels_list(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._env_file(root)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "channels",
                        "resolve",
                        "--channel",
                        "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["request"]["method"], "channels.list")

    def test_plan_only_query_uses_search_list(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._env_file(root)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "channels",
                        "resolve",
                        "--channel",
                        "Some Channel Name",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["request"]["method"], "search.list")


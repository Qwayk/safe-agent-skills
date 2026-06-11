from __future__ import annotations

import unittest
from pathlib import Path

from youtube_api_tool.api_call import build_api_call_plan
from youtube_api_tool.config import Config


class TestApiCallability(unittest.TestCase):
    def test_build_plan_for_every_official_method(self) -> None:
        root = Path(__file__).resolve().parents[1]
        methods_txt = root / "docs" / "official_methods.txt"
        methods = [ln.strip() for ln in methods_txt.read_text(encoding="utf-8").splitlines() if ln.strip()]
        self.assertGreater(len(methods), 0)

        cfg = Config(
            base_url="https://www.googleapis.com",
            api_key=None,
            oauth_client_secrets_file=None,
            oauth_scopes=("https://www.googleapis.com/auth/youtube",),
            timeout_s=30.0,
        )
        ctx = {
            "tool": "youtube-api-tool",
            "tool_version": "0.1.0",
            "command_str": "youtube-api-tool api <resource.method> ...",
            "cfg": cfg,
        }

        for m in methods:
            plan = build_api_call_plan(ctx=ctx, method=m, params={}, body=None, upload=None, download=None)
            self.assertEqual(plan["request"]["method"], m)

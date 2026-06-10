from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from pinterest_api_tool.commands.boards import cmd_board_pins_list
from pinterest_api_tool.config import Config
from pinterest_api_tool.http import HttpResponse
from pinterest_api_tool.output import Output


class _FakeHttp:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def request(self, method: str, url: str, **kwargs):  # noqa: ANN001
        self.calls.append({"method": method, "url": url, "params": kwargs.get("params")})
        return HttpResponse(
            status=200,
            headers={},
            body=json.dumps({"items": [], "bookmark": None}).encode("utf-8"),
            url=url,
        )


class _Audit:
    def write(self, event: str, payload):  # noqa: ANN001
        _ = event, payload


class TestBoardPinsSection(unittest.TestCase):
    def test_section_id_uses_section_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp()
            ctx = {
                "cfg": Config(
                    base_url="https://api.pinterest.com/v5",
                    access_token=None,
                    app_id=None,
                    app_secret=None,
                    refresh_token=None,
                    timeout_s=30,
                ),
                "http": http,
                "env_file": str(tool_dir / ".env"),
                "out": Output(mode="json"),
                "audit": _Audit(),
            }
            args = SimpleNamespace(
                board_id="b1",
                section_id="s1",
                ad_account_id=None,
                creative_types=None,
                pin_metrics=False,
                limit=10,
                page_size=100,
                bookmark=None,
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_board_pins_list(args, ctx)
            self.assertEqual(rc, 0)
            self.assertEqual(len(http.calls), 1)
            self.assertIn("/boards/b1/sections/s1/pins", http.calls[0]["url"])

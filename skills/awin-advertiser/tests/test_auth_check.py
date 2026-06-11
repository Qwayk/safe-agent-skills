from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from pathlib import Path

from unittest.mock import patch

from awin_advertiser_safe_agent_cli.cli import main
from awin_advertiser_safe_agent_cli.http import HttpResponse, HttpClient


class TestAuthCheck(unittest.TestCase):
    def test_missing_token_returns_setup_needed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_ADVERTISER_ID=123\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "auth", "check"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertTrue(payload["setup_needed"])

    @patch.object(HttpClient, "request")
    def test_auth_check_success(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"publishers":[{"id":1},{"id":2}]}',
            url="https://api.awin.com/advertisers/123/publishers?accessToken=token",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\nAWIN_ADVERTISER_ID=123\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "auth", "check"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["publisher_count"], 2)

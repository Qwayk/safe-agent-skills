from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from fortnox_api_tool.cli import main


class _FakeResp:
    def __init__(self, status_code: int, payload: dict[str, object]):
        self.status_code = status_code
        self._payload = payload
        self.text = json.dumps(payload)


class TestAuthRefresh(unittest.TestCase):
    def test_auth_refresh_rotates_and_persists_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "FORTNOX_API_BASE_URL=https://api.fortnox.se/3",
                        "FORTNOX_CLIENT_ID=test-client",
                        "FORTNOX_CLIENT_SECRET=test-secret",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            token_path = Path(d) / ".state" / "token.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text(
                json.dumps({"access_token": "OLD", "refresh_token": "KEEP", "expires_at": 1}),
                encoding="utf-8",
            )
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.auth_runtime.requests.post",
                return_value=_FakeResp(
                    200,
                    {
                        "access_token": "NEW",
                        "expires_in": 3600,
                        "token_type": "bearer",
                    },
                ),
            ):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "auth", "refresh"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["token_refreshed"])
            saved = json.loads(token_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["access_token"], "NEW")
            self.assertEqual(saved["refresh_token"], "KEEP")
            self.assertEqual(saved["token_source"], "refresh_token")

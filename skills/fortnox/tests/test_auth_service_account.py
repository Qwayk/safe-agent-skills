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


class TestAuthServiceAccount(unittest.TestCase):
    def test_service_account_token_requires_tenant(self) -> None:
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
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "auth", "service-account-token"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_service_account_token_fetch_writes_token_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "FORTNOX_API_BASE_URL=https://api.fortnox.se/3",
                        "FORTNOX_CLIENT_ID=test-client",
                        "FORTNOX_CLIENT_SECRET=test-secret",
                        "FORTNOX_SERVICE_TENANT_ID=12345",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.auth_runtime.requests.post",
                return_value=_FakeResp(
                    200,
                    {
                        "access_token": "SERVICE",
                        "expires_in": 3600,
                        "scope": "companyinformation",
                        "token_type": "bearer",
                    },
                ),
            ):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "auth", "service-account-token"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["service_account_token_fetched"])
            self.assertEqual(payload["tenant_id"], "12345")
            self.assertTrue(Path(payload["stored_to"]).exists())

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from google_merchant_api_tool.cli import main


class TestDiscoveryApplyReceipt(unittest.TestCase):
    def test_apply_refuses_before_provider_write_without_before_state(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "GOOGLE_MERCHANT_API_BASE_URL=http://example.invalid",
                        "GOOGLE_MERCHANT_API_AUTH_MODE=service_account_json",
                        "GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_JSON=/tmp/fake.json",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with patch(
                "google_merchant_api_tool.commands.discovery.load_credentials_from_config",
            ) as mock_load_creds, patch("google_merchant_api_tool.commands.discovery.HttpClient") as mock_http_client, redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        "2026-06-04T000054Z_example",
                        "--apply",
                        "accounts",
                        "product-inputs",
                        "insert",
                        "--parent",
                        "accounts/123456",
                        "--body-json",
                        json.dumps(
                            {
                                "channel": "ONLINE",
                                "contentLanguage": "en",
                                "offerId": "SKU-RED-123",
                                "feedLabel": "US",
                            }
                        ),
                    ]
                )

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("before-state snapshot", payload["reasons"][0])
            self.assertIn("ack-no-snapshot", payload["reasons"][0])
            self.assertNotIn("receipt", payload)
            mock_load_creds.assert_not_called()
            mock_http_client.assert_not_called()

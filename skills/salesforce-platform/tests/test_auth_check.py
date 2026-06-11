from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tests import bootstrap  # noqa: F401

from salesforce_platform_safe_agent_cli.cli import main
from salesforce_platform_safe_agent_cli.http import HttpResponse


class TestAuthCheck(unittest.TestCase):
    def test_auth_check_reports_sample_limits(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                (
                    "SALESFORCE_INSTANCE_URL=https://example.my.salesforce.com\n"
                    "SALESFORCE_ACCESS_TOKEN=test-token\n"
                    "SALESFORCE_API_VERSION=67.0\n"
                ),
                encoding="utf-8",
            )

            response = HttpResponse(
                status=200,
                headers={"sforce-limit-info": "api-usage=1/5000", "content-type": "application/json"},
                body=json.dumps(
                    {
                        "DailyApiRequests": {"Max": 5000, "Remaining": 4999},
                        "DailyBulkApiBatches": {"Max": 10000, "Remaining": 9999},
                    }
                ).encode("utf-8"),
                url="https://example.my.salesforce.com/services/data/v67.0/limits/",
            )

            with patch("salesforce_platform_safe_agent_cli.commands.auth.HttpClient.request", return_value=response):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "auth", "check"])

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["instance_url"], "https://example.my.salesforce.com")
            self.assertEqual(payload["api_version"], "67.0")
            self.assertEqual(payload["token_source"], "env")
            self.assertEqual(payload["sforce_limit_info"], "api-usage=1/5000")
            self.assertIn("DailyApiRequests", payload["sample_limits"])

    def test_auth_check_requires_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("SALESFORCE_INSTANCE_URL=https://example.my.salesforce.com\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "auth", "check"])

            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

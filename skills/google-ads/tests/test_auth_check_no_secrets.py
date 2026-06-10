from __future__ import annotations

import io
import json
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from google_ads_api_tool.cli import main


class TestAuthCheckNoSecrets(unittest.TestCase):
    def test_auth_check_error_redacts_env_secrets(self) -> None:
        os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"] = "DEV_TOKEN_SUPER_SECRET"
        os.environ["GOOGLE_ADS_CLIENT_ID"] = "CLIENT_ID_SUPER_SECRET"
        os.environ["GOOGLE_ADS_CLIENT_SECRET"] = "CLIENT_SECRET_SUPER_SECRET"
        os.environ["GOOGLE_ADS_REFRESH_TOKEN"] = "REFRESH_TOKEN_SUPER_SECRET"
        try:
            with patch("google_ads_api_tool.google_ads_client.GoogleAdsClient.load_from_dict") as m:
                m.side_effect = RuntimeError(
                    "boom DEV_TOKEN_SUPER_SECRET CLIENT_SECRET_SUPER_SECRET REFRESH_TOKEN_SUPER_SECRET"
                )
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "auth", "check"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            s = json.dumps(payload)
            self.assertNotIn("DEV_TOKEN_SUPER_SECRET", s)
            self.assertNotIn("CLIENT_SECRET_SUPER_SECRET", s)
            self.assertNotIn("REFRESH_TOKEN_SUPER_SECRET", s)
        finally:
            for k in [
                "GOOGLE_ADS_DEVELOPER_TOKEN",
                "GOOGLE_ADS_CLIENT_ID",
                "GOOGLE_ADS_CLIENT_SECRET",
                "GOOGLE_ADS_REFRESH_TOKEN",
            ]:
                os.environ.pop(k, None)


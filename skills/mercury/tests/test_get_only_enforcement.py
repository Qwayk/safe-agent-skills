from __future__ import annotations

import unittest
from unittest.mock import Mock

from mercury_api_tool.config import Config
from mercury_api_tool.errors import SafetyError
from mercury_api_tool.mercury_client import MercuryClient


class TestGetOnlyEnforcement(unittest.TestCase):
    def test_non_get_request_is_refused(self) -> None:
        cfg = Config(
            base_url="https://api.mercury.com/api/v1",
            token="secret-token:TEST_TOKEN_DO_NOT_LEAK",
            auth_scheme="bearer",
            timeout_s=30.0,
        )
        http = Mock()
        client = MercuryClient(cfg=cfg, http=http)

        with self.assertRaises(SafetyError):
            client.request("POST", "/organization")

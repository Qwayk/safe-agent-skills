from __future__ import annotations

import importlib
import unittest

from google_ads_api_tool.google_ads_client import SUPPORTED_API_VERSION


class TestSupportedApiVersion(unittest.TestCase):
    def test_supported_version_module_exists(self) -> None:
        importlib.import_module(f"google.ads.googleads.{SUPPORTED_API_VERSION}")


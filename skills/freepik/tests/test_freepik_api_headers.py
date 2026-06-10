from __future__ import annotations

import unittest
from unittest.mock import Mock

from freepik_api_tool.config import Config
from freepik_api_tool.freepik_api import FreepikApi


class TestFreepikApiHeaders(unittest.TestCase):
    def test_accept_language_header_is_included_when_configured(self) -> None:
        cfg = Config(
            base_url="https://api.freepik.com/v1",
            api_key="k",
            timeout_s=1.0,
            auth_header="x-freepik-api-key",
            auth_prefix="",
            accept_language="fr-FR",
            image_size=None,
            download_url_jsonpath=None,
            license_url_jsonpath=None,
        )
        api = FreepikApi(cfg=cfg, http=Mock())
        headers = api._auth_headers()
        self.assertEqual(headers["Accept-Language"], "fr-FR")

    def test_accept_language_header_is_omitted_when_unset(self) -> None:
        cfg = Config(
            base_url="https://api.freepik.com/v1",
            api_key="k",
            timeout_s=1.0,
            auth_header="x-freepik-api-key",
            auth_prefix="",
            accept_language=None,
            image_size=None,
            download_url_jsonpath=None,
            license_url_jsonpath=None,
        )
        api = FreepikApi(cfg=cfg, http=Mock())
        headers = api._auth_headers()
        self.assertNotIn("Accept-Language", headers)


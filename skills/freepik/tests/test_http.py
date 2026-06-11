from __future__ import annotations

import unittest
from unittest import mock

import requests

from freepik_api_tool.http import HttpClient


class TestHttp(unittest.TestCase):
    def test_connection_exception_includes_method_url(self) -> None:
        client = HttpClient(timeout_s=1.0, verbose=False, user_agent="t")
        with mock.patch.object(client._session, "request", side_effect=requests.ConnectionError("nope")):
            with self.assertRaises(RuntimeError) as ctx:
                client.request("GET", "https://example.com/x", params={"a": "b"})
        msg = str(ctx.exception)
        self.assertIn("GET", msg)
        self.assertIn("https://example.com/x", msg)


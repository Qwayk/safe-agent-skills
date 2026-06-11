from __future__ import annotations

import unittest
from unittest.mock import patch

from dynadot_api_tool.dynadot_api import DynadotApi, DynadotApiError


class _Resp:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class _Http:
    def __init__(self, payloads: list[dict]) -> None:
        self._payloads = list(payloads)
        self.calls: list[tuple[str, str, dict]] = []

    def request(self, method: str, url: str, *, params: dict, retries: int = 0):  # type: ignore[no-untyped-def]
        self.calls.append((method, url, dict(params)))
        if not self._payloads:
            raise AssertionError("no more payloads")
        return _Resp(self._payloads.pop(0))


class TestDynadotApiRateLimitRetry(unittest.TestCase):
    def test_rate_limit_message_retries_once(self) -> None:
        http = _Http(
            [
                {
                    "AnyResponse": {
                        "ResponseCode": "-1",
                        "Status": "error",
                        "Error": "Too many requests. Please try again in 1 minute after.",
                    }
                },
                {"AnyResponse": {"ResponseCode": "0", "Status": "success"}},
            ]
        )
        api = DynadotApi(base_url="http://example.invalid/api3.json", api_key="K", http=http)  # type: ignore[arg-type]
        with patch("dynadot_api_tool.dynadot_api.time.sleep") as sleep:
            res = api.call(command="list_domain", params={"page_index": 1})
        self.assertEqual(res.status, "success")
        self.assertEqual(len(http.calls), 2)
        sleep.assert_called()

    def test_non_rate_limit_error_does_not_retry(self) -> None:
        http = _Http(
            [
                {"AnyResponse": {"ResponseCode": "-1", "Status": "error", "Error": "Some other error"}},
                {"AnyResponse": {"ResponseCode": "0", "Status": "success"}},
            ]
        )
        api = DynadotApi(base_url="http://example.invalid/api3.json", api_key="K", http=http)  # type: ignore[arg-type]
        with patch("dynadot_api_tool.dynadot_api.time.sleep") as sleep:
            with self.assertRaises(DynadotApiError):
                _ = api.call(command="list_domain", params={"page_index": 1})
        self.assertEqual(len(http.calls), 1)
        sleep.assert_not_called()


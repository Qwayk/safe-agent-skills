from __future__ import annotations

import json
import unittest
from dataclasses import dataclass
from typing import Any

from dynadot_api_tool.dynadot_api import DynadotApi, DynadotApiError


@dataclass
class _Resp:
    body: bytes

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


class _Http:
    def __init__(self, payload: dict[str, Any]):
        self._payload = payload

    def request(self, method: str, url: str, **kwargs: Any) -> _Resp:  # noqa: ARG002
        return _Resp(body=json.dumps(self._payload).encode("utf-8"))


class TestDynadotApi(unittest.TestCase):
    def test_success_response_code_zero(self) -> None:
        http = _Http({"IsProcessingResponse": {"Status": "success", "ResponseCode": "0", "isprocessing": "no"}})
        api = DynadotApi(base_url="https://api.dynadot.com/api3.json", api_key="K", http=http)  # type: ignore[arg-type]
        res = api.call(command="is_processing")
        self.assertEqual(res.response_code, "0")
        self.assertEqual(res.status, "success")

    def test_success_response_code_zero_int(self) -> None:
        http = _Http({"ListDomainInfoResponse": {"Status": "success", "ResponseCode": 0, "MainDomains": []}})
        api = DynadotApi(base_url="https://api.dynadot.com/api3.json", api_key="K", http=http)  # type: ignore[arg-type]
        res = api.call(command="list_domain", params={"page_index": 1})
        self.assertEqual(res.response_code, "0")
        self.assertEqual(res.status, "success")

    def test_error_response_code_nonzero_raises(self) -> None:
        http = _Http({"PushResponse": {"Status": "error", "ResponseCode": "5", "Error": "Invalid key"}})
        api = DynadotApi(base_url="https://api.dynadot.com/api3.json", api_key="K", http=http)  # type: ignore[arg-type]
        with self.assertRaises(DynadotApiError):
            api.call(command="push", params={"domain": "a.com", "receiver_push_username": "x"})

    def test_missing_response_code_raises(self) -> None:
        http = _Http({"PushResponse": {"Status": "success"}})
        api = DynadotApi(base_url="https://api.dynadot.com/api3.json", api_key="K", http=http)  # type: ignore[arg-type]
        with self.assertRaises(DynadotApiError):
            api.call(command="push", params={"domain": "a.com", "receiver_push_username": "x"})

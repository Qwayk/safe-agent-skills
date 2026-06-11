from __future__ import annotations

import dataclasses
import re
import time
from typing import Any

from .errors import ToolError, ValidationError
from .http import HttpClient


class DynadotApiError(ToolError):
    pass


@dataclasses.dataclass(frozen=True)
class DynadotApiResult:
    command: str
    response: dict[str, Any]

    @property
    def response_code(self) -> str:
        v = self.response.get("ResponseCode")
        return "" if v is None else str(v)

    @property
    def status(self) -> str:
        v = self.response.get("Status")
        return "" if v is None else str(v)


def _coerce_dict(obj: Any, *, what: str) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise DynadotApiError(f"Unexpected Dynadot API response shape: {what} must be an object")
    return obj


def _find_response_payload(raw: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    # Dynadot API3 JSON wraps payloads like:
    #   {"PushResponse": {"Status": "...", "ResponseCode": "0", ...}}
    for k, v in raw.items():
        if str(k).endswith("Response") and isinstance(v, dict):
            return str(k), v
    for k, v in raw.items():
        if isinstance(v, dict):
            return str(k), v
    raise DynadotApiError("Unexpected Dynadot API response: missing *Response object")


class DynadotApi:
    def __init__(self, *, base_url: str, api_key: str, http: HttpClient):
        self._base_url = base_url
        self._api_key = api_key
        self._http = http

    def call(self, *, command: str, params: dict[str, Any] | None = None) -> DynadotApiResult:
        cmd = str(command or "").strip()
        if not cmd:
            raise ValidationError("Missing Dynadot API command")

        p: dict[str, Any] = {}
        if params:
            for k, v in params.items():
                if v is None:
                    continue
                p[str(k)] = v
        p["key"] = self._api_key
        p["command"] = cmd

        def _retry_sleep_seconds(msg: str) -> float:
            m = (msg or "").lower()
            # Common Dynadot message: "Too many requests. Please try again in 1 minute after."
            mm = re.search(r"in\\s+(\\d+)\\s+minute", m)
            if mm:
                return float(int(mm.group(1)) * 60 + 5)
            ss = re.search(r"in\\s+(\\d+)\\s+second", m)
            if ss:
                return float(int(ss.group(1)) + 2)
            return 65.0

        for attempt in range(0, 2):
            resp = self._http.request("GET", self._base_url, params=p, retries=2)
            try:
                raw = resp.json()
            except Exception as e:  # noqa: BLE001
                raise DynadotApiError(f"Dynadot API returned non-JSON: {type(e).__name__}") from None

            raw_obj = _coerce_dict(raw, what="top-level")
            _, payload = _find_response_payload(raw_obj)
            payload_obj = _coerce_dict(payload, what="*Response")

            if "ResponseCode" not in payload_obj:
                raise DynadotApiError("Dynadot API response missing ResponseCode")
            code_raw = payload_obj.get("ResponseCode")
            code = "" if code_raw is None else str(code_raw)
            if code and code != "0":
                msg = (
                    payload_obj.get("Error")
                    or payload_obj.get("Message")
                    or payload_obj.get("Status")
                    or "Dynadot API error"
                )
                msg_s = str(msg or "")
                if "too many requests" in msg_s.lower() and attempt == 0:
                    time.sleep(_retry_sleep_seconds(msg_s))
                    continue
                raise DynadotApiError(f"Dynadot API error (ResponseCode={code}): {msg_s}")

            if not code:
                raise DynadotApiError("Dynadot API response missing ResponseCode")

            return DynadotApiResult(command=cmd, response=payload_obj)

        raise DynadotApiError("Dynadot API error: rate limit retries exhausted")

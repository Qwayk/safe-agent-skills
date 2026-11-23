from __future__ import annotations

import dataclasses
import re
import time
from typing import Any

from .errors import ToolError, ValidationError
from .http import HttpClient


class DynadotApiError(ToolError):
    pass


class UncertainWriteError(DynadotApiError):
    """The provider may have received the request. Inspect state before retrying."""


def is_write_command(cmd: str) -> bool:
    c = str(cmd).strip().lower()
    # Dynadot's request examples for get_transfer_auth_code include optional params
    # that can mutate state (e.g. new_code=1, unlock_domain_for_transfer=1), so we
    # treat it as write-capable and gate it behind the write safety contract.
    if c == "get_transfer_auth_code":
        return True
    if c.startswith("get_") or c.startswith("list_") or c in {"account_info", "contact_list", "folder_list", "domain_info", "order_list", "search", "server_list", "tld_price", "is_processing", "transfer_domain_list", "backorder_request_list"}:
        return False
    return True


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


def _without_transfer_secrets(value: Any, secrets: tuple[str, ...]) -> Any:
    if isinstance(value, dict):
        return {
            k: _without_transfer_secrets(v, secrets)
            for k, v in value.items()
            if str(k).lower().replace("_", "") not in {"auth", "authcode", "transferauthcode", "eppcode"}
        }
    if isinstance(value, list):
        return [_without_transfer_secrets(item, secrets) for item in value]
    if isinstance(value, str):
        for secret in secrets:
            value = value.replace(secret, "[private]")
    return value


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
            mm = re.search(r"in\s+(\d+)\s+minute", m)
            if mm:
                return float(int(mm.group(1)) * 60 + 5)
            ss = re.search(r"in\s+(\d+)\s+second", m)
            if ss:
                return float(int(ss.group(1)) + 2)
            return 65.0

        read_only = not is_write_command(cmd) or (cmd == "renew" and p.get("price_check") == "1")
        uncertain = (
            "Dynadot did not confirm the change. Check the domain or order in Dynadot before trying again."
        )
        for attempt in range(2 if read_only else 1):
            try:
                resp = self._http.request(
                    "GET", self._base_url, params=p, retries=2 if read_only else 0
                )
                raw = resp.json()
                raw_obj = _coerce_dict(raw, what="top-level")
                _, payload = _find_response_payload(raw_obj)
                payload_obj = _coerce_dict(payload, what="*Response")
                if payload_obj.get("ResponseCode") in (None, ""):
                    raise DynadotApiError("Dynadot API response missing ResponseCode")
            except (RuntimeError, ValueError, DynadotApiError) as exc:
                if not read_only:
                    raise UncertainWriteError(uncertain) from None
                message = str(exc).replace(self._api_key, "[private]") if self._api_key else str(exc)
                raise DynadotApiError(message) from None

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
                if "too many requests" in msg_s.lower() and read_only and attempt == 0:
                    time.sleep(_retry_sleep_seconds(msg_s))
                    continue
                for secret in (p.get("key"), p.get("auth"), p.get("auth_code")):
                    if secret:
                        msg_s = msg_s.replace(str(secret), "[private]")
                raise DynadotApiError(f"Dynadot API error (ResponseCode={code}): {msg_s}")

            if not code:
                raise DynadotApiError("Dynadot API response missing ResponseCode")

            secret_values = tuple(str(p[key]) for key in ("key", "auth", "auth_code") if p.get(key))
            safe_response = payload_obj if cmd == "get_transfer_auth_code" else _without_transfer_secrets(
                payload_obj, secret_values
            )
            return DynadotApiResult(command=cmd, response=safe_response)

        raise DynadotApiError("Dynadot API error: rate limit retries exhausted")

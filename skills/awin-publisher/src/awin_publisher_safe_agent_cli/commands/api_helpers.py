from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..errors import ToolError, ValidationError


_ACCOUNTS_PATH = "/accounts"
_PUBLISHER_KEY_CANDIDATES = (
    "type",
    "accountType",
    "account_type",
    "kind",
    "role",
    "accountRole",
    "model",
)
_PUBLISHER_VALUES = {"publisher", "publisher_account", "publisheraccount", "publisher account"}


def _to_str(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value).strip()


def build_bearer_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def build_access_token_query(token: str) -> dict[str, str]:
    return {"accessToken": token}


def extract_list_payload(payload: object) -> list[Mapping[str, object]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, Mapping)]
    if not isinstance(payload, Mapping):
        raise ValidationError("GET /accounts returned unexpected JSON shape")
    for key in ("accounts", "data", "items"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, Mapping)]
    raise ValidationError("GET /accounts did not return a list of accounts")


def looks_like_publisher(account: Mapping[str, object]) -> bool:
    for key in _PUBLISHER_KEY_CANDIDATES:
        value = account.get(key)
        if value is None:
            continue
        if _to_str(value).lower() in _PUBLISHER_VALUES:
            return True
    return False


def summarize_account(account: Mapping[str, object]) -> dict[str, object]:
    return {
        "id": account.get("id") or account.get("accountId") or account.get("publisherId") or "<unknown>",
        "name": account.get("name") or account.get("accountName") or "<unknown>",
        "status": account.get("status") or account.get("state") or account.get("isActive") or "<unknown>",
    }


def _parse_json_response(response: object) -> object:
    try:
        return response.json()
    except Exception as exc:  # noqa: BLE001
        raise ToolError(f"Response from {getattr(response, 'url', '<unknown>')} was not JSON: {exc}") from exc


def fetch_accounts(cfg, http_client) -> tuple[list[Mapping[str, object]], int]:
    if not cfg.token:
        raise ValidationError("AWIN_API_TOKEN is required for auth check")

    headers = build_bearer_headers(cfg.token)
    params = build_access_token_query(cfg.token)
    resp = http_client.request(
        "GET",
        f"{cfg.api_host}{_ACCOUNTS_PATH}",
        headers=headers,
        params=params,
    )
    payload = _parse_json_response(resp)
    return extract_list_payload(payload), resp.status


def filtered_publisher_accounts(accounts: list[Mapping[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    publisher_accounts = [summarize_account(a) for a in accounts if looks_like_publisher(a)]
    non_publisher_accounts = [summarize_account(a) for a in accounts if not looks_like_publisher(a)]
    return publisher_accounts, non_publisher_accounts


def safe_query_meta(params: dict[str, Any]) -> list[str]:
    return sorted(params.keys())

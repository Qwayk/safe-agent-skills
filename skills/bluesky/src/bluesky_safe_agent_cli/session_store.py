from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .oauth_tokens import TokenStatus, get_token_status, read_token_json, token_path_for_env_file


def session_path_for_env_file(env_file: str) -> Path:
    return token_path_for_env_file(env_file)


def read_session_json(env_file: str) -> dict[str, Any] | None:
    path = session_path_for_env_file(env_file)
    return read_token_json(path)


def write_session_json(env_file: str, session_obj: dict[str, Any]) -> TokenStatus:
    path = session_path_for_env_file(env_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(session_obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return get_token_status(path)


def clear_session_json(env_file: str) -> dict[str, Any]:
    path = session_path_for_env_file(env_file)
    existed = path.exists()
    if existed:
        path.unlink()
    return {"cleared": existed, "path": str(path)}


def access_token_from_session(session_obj: dict[str, Any] | None) -> str | None:
    if not isinstance(session_obj, dict):
        return None
    value = session_obj.get("accessJwt") or session_obj.get("access_token")
    text = str(value or "").strip()
    return text or None


def refresh_token_from_session(session_obj: dict[str, Any] | None) -> str | None:
    if not isinstance(session_obj, dict):
        return None
    value = session_obj.get("refreshJwt") or session_obj.get("refresh_token")
    text = str(value or "").strip()
    return text or None


def pds_url_from_session(session_obj: dict[str, Any] | None) -> str | None:
    if not isinstance(session_obj, dict):
        return None
    did_doc = session_obj.get("didDoc")
    if not isinstance(did_doc, dict):
        return None
    services = did_doc.get("service")
    if not isinstance(services, list):
        return None
    for item in services:
        if not isinstance(item, dict):
            continue
        service_id = str(item.get("id") or "")
        service_type = str(item.get("type") or "")
        endpoint = str(item.get("serviceEndpoint") or "").strip()
        if not endpoint:
            continue
        if service_id.endswith("#atproto_pds") or service_type == "AtprotoPersonalDataServer":
            return endpoint.rstrip("/")
    return None

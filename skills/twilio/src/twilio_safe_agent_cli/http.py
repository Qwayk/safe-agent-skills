from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class HttpResult:
    status_code: int
    data: Any
    content_type: str


def send_request(
    request: Any,
    *,
    session: Any | None = None,
    timeout_s: float,
    retry_safe: bool,
    verbose: bool = False,
) -> HttpResult:
    client = session or requests.Session()
    attempts = 3 if retry_safe else 1
    response = None
    for attempt in range(attempts):
        response = client.request(
            request.method,
            request.url,
            params=request.query or None,
            data=request.form or None,
            json=request.json_body,
            headers=request.headers or None,
            auth=request.auth,
            timeout=timeout_s,
        )
        if verbose:
            print(
                f"Twilio HTTP {request.method} {request.public_host} -> {response.status_code}",
                file=sys.stderr,
            )
        if not retry_safe or response.status_code not in {429, 500, 502, 503, 504}:
            break
        if attempt + 1 >= attempts:
            break
    assert response is not None
    content_type = str(response.headers.get("Content-Type", "")).split(";", 1)[0].lower()
    try:
        data = response.json()
    except Exception:  # noqa: BLE001
        data = {"text": str(response.text or "")}
    return HttpResult(status_code=int(response.status_code), data=data, content_type=content_type)

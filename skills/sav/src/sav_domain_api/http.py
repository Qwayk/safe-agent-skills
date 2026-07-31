from __future__ import annotations

import json
from dataclasses import dataclass

import requests

from .errors import HttpResponseError, ToolError


@dataclass(frozen=True)
class HttpResponse:
    status: int
    json_body: object
    url: str


class _JsonDecoder:
    @staticmethod
    def load(text: str) -> object:
        return json.loads(
            text,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError("invalid json number")),
        )


class HttpClient:
    def __init__(self, *, timeout_s: float) -> None:
        self._timeout_s = timeout_s
        self._session = requests.Session()

    def get(self, *, url: str, headers: dict[str, str], params: dict[str, str]) -> HttpResponse:
        try:
            response = self._session.get(
                url,
                headers=headers,
                params=params,
                timeout=self._timeout_s,
                allow_redirects=False,
            )
        except requests.RequestException as exc:
            raise ToolError("SAV request failed before a response was received") from exc

        status = int(response.status_code)
        payload_text = response.text if response.text else ""
        try:
            payload = _JsonDecoder.load(payload_text)
        except (json.JSONDecodeError, ValueError):
            message = (
                f"Provider request failed: HTTP {status}"
                if not (200 <= status <= 299)
                else "Unable to parse provider response as JSON"
            )
            raise HttpResponseError(
                message,
                status=status,
                response={"unparsed_response": "<redacted>"},
            ) from None

        if not (200 <= status <= 299):
            raise HttpResponseError(
                f"Provider request failed: HTTP {status}", status=status, response=payload
            )

        return HttpResponse(
            status=status,
            json_body=payload,
            url=response.url,
        )

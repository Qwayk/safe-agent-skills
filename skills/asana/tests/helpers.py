from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from asana_safe_agent_cli.config import Config
from asana_safe_agent_cli.http import HttpResponse


class CaptureOut:
    def __init__(self) -> None:
        self.last: Any = None

    def emit(self, value: Any) -> None:
        self.last = value


class FakeAudit:
    def __init__(self) -> None:
        self.rows: list[tuple[str, dict[str, Any]]] = []

    def write(self, event: str, payload: dict[str, Any]) -> None:
        self.rows.append((event, payload))


class FakeClient:
    def __init__(self, responses: list[HttpResponse]) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def request(self, method: str, url: str, **kwargs: Any) -> HttpResponse:
        self.calls.append({"method": method, "url": url, **kwargs})
        if not self.responses:
            raise AssertionError("FakeClient has no response left")
        return self.responses.pop(0)


def response(status: int, payload: Any = None) -> HttpResponse:
    import json

    body = b"" if payload is None else json.dumps(payload).encode()
    return HttpResponse(
        status=status,
        headers={"content-type": "application/json", "x-request-id": "test-request"},
        body=body,
        url="https://app.asana.com/api/1.0/test",
    )


def args(**overrides: Any) -> SimpleNamespace:
    values: dict[str, Any] = {
        "operation": "get-workspaces",
        "param": [],
        "data_json": None,
        "data_file": None,
        "file": [],
        "paginate": False,
        "max_pages": 20,
        "download_to": None,
        "plan_out": None,
        "plan_in": None,
        "apply": False,
        "approve": None,
        "acknowledge_no_snapshot": False,
        "acknowledge_risk": False,
        "receipt_out": None,
        "wait": False,
        "wait_timeout_s": 1.0,
        "poll_interval_s": 0.001,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def context(tmp_path: str, client: FakeClient) -> tuple[dict[str, Any], CaptureOut, FakeAudit]:
    out = CaptureOut()
    audit = FakeAudit()
    ctx = {
        "cfg": Config(
            base_url="https://app.asana.com/api/1.0",
            token="test-token-not-printed",
            timeout_s=1.0,
        ),
        "out": out,
        "audit": audit,
        "tool_version": "0.1.0",
        "env_file": f"{tmp_path}/.env",
        "verbose": False,
        "http_client": client,
    }
    return ctx, out, audit

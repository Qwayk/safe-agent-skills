from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
from typing import Any

import requests

from jira_safe_agent_cli.cli import main


def run_cli(argv: list[str]) -> tuple[int, dict[str, Any], str]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        rc = main(argv)
    raw = stdout.getvalue()
    return rc, json.loads(raw), raw


def write_basic_env(root: Path, token: str = "test-secret-token") -> Path:
    path = root / ".env"
    path.write_text(
        "JIRA_BASE_URL=https://example.atlassian.net\n"
        "JIRA_EMAIL=tester@example.com\n"
        f"JIRA_API_TOKEN={token}\n",
        encoding="utf-8",
    )
    return path


def write_oauth_env(root: Path, token: str = "oauth-secret-token") -> Path:
    path = root / ".env"
    path.write_text(
        "JIRA_BASE_URL=https://api.atlassian.com/ex/jira/cloud-id\n"
        f"JIRA_OAUTH_ACCESS_TOKEN={token}\n",
        encoding="utf-8",
    )
    return path


def fake_response(
    status: int = 200,
    body: Any = None,
    *,
    url: str = "https://example.atlassian.net/rest/api/3/example",
    content_type: str = "application/json",
) -> requests.Response:
    response = requests.Response()
    response.status_code = status
    response.url = url
    response.headers["Content-Type"] = content_type
    if isinstance(body, bytes):
        response._content = body
    elif body is None:
        response._content = b""
    else:
        response._content = json.dumps(body).encode("utf-8")
    return response

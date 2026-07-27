from __future__ import annotations

import dataclasses
import os
import re
from pathlib import Path
from urllib.parse import urlparse

from .errors import ValidationError


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def _get(env: dict[str, str], key: str) -> str:
    return str(os.environ.get(key, env.get(key, ""))).strip()


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    email: str | None
    api_token: str | None
    oauth_access_token: str | None
    timeout_s: float

    @property
    def auth_mode(self) -> str | None:
        if self.oauth_access_token:
            return "bearer"
        if self.email and self.api_token:
            return "basic"
        return None

    @property
    def fingerprint(self) -> str:
        parsed = urlparse(self.base_url)
        return f"{parsed.scheme}://{parsed.netloc}"


def load_config(env_file: str | None, *, require_auth: bool = True) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))
    base_url = _get(env, "JIRA_BASE_URL").rstrip("/")
    email = _get(env, "JIRA_EMAIL") or None
    api_token = _get(env, "JIRA_API_TOKEN") or None
    oauth_access_token = _get(env, "JIRA_OAUTH_ACCESS_TOKEN") or None
    timeout_raw = _get(env, "JIRA_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_raw)
    except ValueError:
        raise ValidationError("JIRA_TIMEOUT_S must be a number of seconds") from None

    if not base_url:
        raise ValidationError("Missing JIRA_BASE_URL")
    parsed = urlparse(base_url)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        raise ValidationError("JIRA_BASE_URL must be an absolute HTTP or HTTPS URL")
    hostname = (parsed.hostname or "").lower()
    is_local_test = hostname in {"127.0.0.1", "localhost"}
    if parsed.username or parsed.password:
        raise ValidationError("JIRA_BASE_URL must not contain embedded credentials")
    try:
        port = parsed.port
    except ValueError:
        raise ValidationError("JIRA_BASE_URL has an invalid port") from None
    if port is not None and not is_local_test:
        raise ValidationError("JIRA_BASE_URL must not use a custom production port")
    if parsed.query or parsed.fragment:
        raise ValidationError("JIRA_BASE_URL must not contain a query string or fragment")
    if is_local_test:
        if parsed.path not in {"", "/"}:
            raise ValidationError("Local test JIRA_BASE_URL must not contain an API path")
    elif oauth_access_token:
        if parsed.scheme != "https" or hostname != "api.atlassian.com":
            raise ValidationError(
                "OAuth JIRA_BASE_URL must use https://api.atlassian.com/ex/jira/<cloudId>"
            )
        if not re.fullmatch(r"/ex/jira/[A-Za-z0-9_-]+", parsed.path):
            raise ValidationError(
                "OAuth JIRA_BASE_URL must use exactly /ex/jira/<cloudId> with no extra path"
            )
    else:
        if parsed.scheme != "https" or not hostname.endswith(".atlassian.net"):
            raise ValidationError(
                "Basic-auth JIRA_BASE_URL must be an HTTPS Jira Cloud site such as https://your-domain.atlassian.net"
            )
        site_name = hostname[: -len(".atlassian.net")]
        if not site_name or "." in site_name or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", site_name):
            raise ValidationError("Basic-auth JIRA_BASE_URL has an invalid Jira Cloud site host")
        if parsed.path not in {"", "/"}:
            raise ValidationError("Basic-auth JIRA_BASE_URL must not contain an API path")
    if timeout_s <= 0:
        raise ValidationError("JIRA_TIMEOUT_S must be greater than zero")
    if not oauth_access_token and bool(email) != bool(api_token):
        raise ValidationError("JIRA_EMAIL and JIRA_API_TOKEN must be set together")

    config = Config(
        base_url=base_url,
        email=email,
        api_token=api_token,
        oauth_access_token=oauth_access_token,
        timeout_s=timeout_s,
    )
    if require_auth and not config.auth_mode:
        raise ValidationError(
            "Missing Jira credentials: set JIRA_EMAIL with JIRA_API_TOKEN, or set JIRA_OAUTH_ACCESS_TOKEN"
        )
    return config

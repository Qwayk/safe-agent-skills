from __future__ import annotations

import dataclasses
import hashlib
import json
import os
from pathlib import Path


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key:
            out[key] = value
    return out


def _get(env: dict[str, str], key: str) -> str:
    if key in os.environ:
        return os.environ[key].strip()
    return (env.get(key) or "").strip()


def _default_user_agent(contact_username: str) -> str:
    username = (contact_username or "qwaykbot").strip() or "qwaykbot"
    return f"linux:qwayk-reddit-safe-agent-cli:v0.1.0 (by /u/{username})"


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    authorize_url: str
    token_url: str
    client_id: str | None
    client_secret: str | None
    redirect_uri: str | None
    oauth_scopes: str
    bearer_token: str | None
    user_agent: str
    timeout_s: float


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = (_get(env, "REDDIT_API_BASE_URL") or "https://oauth.reddit.com").rstrip("/")
    authorize_url = (_get(env, "REDDIT_OAUTH_AUTHORIZE_URL") or "https://www.reddit.com/api/v1/authorize").strip()
    token_url = (_get(env, "REDDIT_OAUTH_TOKEN_URL") or "https://www.reddit.com/api/v1/access_token").strip()
    client_id = _get(env, "REDDIT_CLIENT_ID") or None
    client_secret = _get(env, "REDDIT_CLIENT_SECRET") or None
    redirect_uri = _get(env, "REDDIT_REDIRECT_URI") or None
    oauth_scopes = (
        _get(env, "REDDIT_OAUTH_SCOPES")
        or "identity read history mysubreddits privatemessages save submit subscribe vote edit modcontributors "
        "modconfig modflair modlog modposts modwiki account report wikiedit wikiread structuredstyles flair"
    ).strip()
    bearer_token = _get(env, "REDDIT_ACCESS_TOKEN") or None
    contact_username = _get(env, "REDDIT_CONTACT_USERNAME")
    user_agent = _get(env, "REDDIT_USER_AGENT") or _default_user_agent(contact_username)

    timeout_s_raw = _get(env, "REDDIT_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("REDDIT_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("REDDIT_TIMEOUT_S must be > 0")
    if not authorize_url.startswith("http"):
        raise RuntimeError("REDDIT_OAUTH_AUTHORIZE_URL must be an absolute URL")
    if not token_url.startswith("http"):
        raise RuntimeError("REDDIT_OAUTH_TOKEN_URL must be an absolute URL")
    if not user_agent:
        raise RuntimeError("REDDIT_USER_AGENT must not be empty")

    return Config(
        base_url=base_url,
        authorize_url=authorize_url,
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        oauth_scopes=oauth_scopes,
        bearer_token=bearer_token,
        user_agent=user_agent,
        timeout_s=timeout_s,
    )


def build_env_fingerprint(cfg: Config) -> str:
    payload = {
        "api_base_url": cfg.base_url,
        "authorize_url": cfg.authorize_url,
        "token_url": cfg.token_url,
        "redirect_uri": (cfg.redirect_uri or ""),
        "oauth_scopes": " ".join(cfg.oauth_scopes.split()),
        "client_id": (cfg.client_id or ""),
        "user_agent": cfg.user_agent,
    }
    material = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import subprocess
import time
from dataclasses import dataclass
from urllib.parse import urlsplit

from .config import Config
from .errors import SafetyError, ValidationError
from .oauth_tokens import read_token_json, token_path_for_env_file


def https_origin(url: str) -> tuple[str, int]:
    try:
        target = urlsplit(url)
        if target.scheme == "https" and target.hostname and target.username is None and target.password is None:
            return target.hostname.lower(), target.port or 443
    except ValueError:
        pass
    raise ValidationError("Use an HTTPS Azure endpoint without a username or password.")


@dataclass(frozen=True)
class AzureConnection:
    token: str
    subscription: str | None
    tenant: str | None
    identity: str
    endpoint: str
    source: str

    def review_details(self) -> dict[str, str | None]:
        return {
            "subscription": self.subscription,
            "tenant": self.tenant,
            "identity": self.identity,
            "endpoint": self.endpoint,
            "credential_source": self.source,
        }


def _az_json(args: list[str], *, timeout: float):
    try:
        completed = subprocess.run(
            ["az", *args, "--only-show-errors", "--output", "json"],
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except FileNotFoundError:
        raise ValidationError("Install Azure CLI and run az login, or use a local Azure token.") from None
    except subprocess.TimeoutExpired:
        raise ValidationError("Azure CLI did not answer in time. Check your Azure sign-in.") from None
    if completed.returncode:
        raise ValidationError("Azure CLI could not load the sign-in or selected subscription. Check az account show and az login.")
    try:
        return json.loads(completed.stdout)
    except ValueError:
        raise ValidationError("Azure CLI returned an unreadable response.") from None


def _claims(token: str) -> dict:
    # These fields help match a plan to the same CLI sign-in. Azure decides if the token is valid.
    try:
        _, payload, _ = token.split(".")
        claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        return claims if isinstance(claims, dict) else {}
    except (ValueError, binascii.Error):
        return {}


def _data_resource(cfg: Config, endpoint: str) -> str | None:
    if cfg.data_plane_resource:
        https_origin(cfg.data_plane_resource)
        return cfg.data_plane_resource
    host, _ = https_origin(endpoint)
    if host.endswith(".vault.azure.net"):
        return "https://vault.azure.net"
    if any(host.endswith(f".{service}.core.windows.net") for service in ("blob", "dfs", "file", "queue", "table")):
        return "https://storage.azure.com/"
    return None


def _same_id(left: str | None, right: str | None) -> bool:
    return not (left and right) or left.casefold() == right.casefold()


def resolve_connection(
    cfg: Config, *, env_file: str, subscription: str | None = None, data_plane: bool = False,
    timeout: float | None = None,
) -> AzureConnection:
    timeout = timeout if timeout is not None else cfg.timeout_s
    endpoint = cfg.data_plane_endpoint if data_plane else cfg.management_endpoint
    if not endpoint:
        raise ValidationError("Set AZURE_DATA_PLANE_ENDPOINT for this service.")
    https_origin(endpoint)
    if urlsplit(endpoint).query or urlsplit(endpoint).fragment:
        raise ValidationError("Use the Azure endpoint without a query string or fragment.")
    audience = _data_resource(cfg, endpoint) if data_plane else None
    target = subscription or cfg.subscription_id

    imported = None if cfg.token else read_token_json(token_path_for_env_file(env_file))
    token = cfg.token
    if imported is not None:
        token = imported.get("access_token") or imported.get("accessToken")
        if not isinstance(token, str) or not token.strip():
            raise ValidationError("The imported token file has no Azure access token.")
    if token:
        claims = _claims(token)
        if audience and isinstance(claims.get("aud"), str) and claims["aud"].rstrip("/") != audience.rstrip("/"):
            raise ValidationError("The access token is for a different Azure service.")
        if isinstance(claims.get("exp"), (int, float)) and claims["exp"] <= time.time():
            raise ValidationError("The local Azure access token expired. Replace it or sign in with Azure CLI.")
        tid = claims.get("tid") or (imported or {}).get("tenant")
        subscription = target or (imported or {}).get("subscription")
        if not _same_id(target, (imported or {}).get("subscription")):
            raise SafetyError("The imported Azure token was saved for a different subscription.")
        identity = "local credential " + hashlib.sha256(token.encode()).hexdigest()
        source = "imported token" if imported is not None else "settings token"
    else:
        if not data_plane:
            cloud = _az_json(["cloud", "show", "--query", "endpoints.resourceManager"], timeout=timeout)
            if not isinstance(cloud, str) or https_origin(cloud) != https_origin(endpoint):
                raise SafetyError("The Azure management endpoint differs from the signed-in Azure cloud.")
        elif not audience:
            raise ValidationError("Set AZURE_DATA_PLANE_RESOURCE to the Microsoft Entra resource for this service.")
        selector = ["--subscription", target] if target else []
        account = _az_json(["account", "show", *selector], timeout=timeout)
        if not isinstance(account, dict) or not account.get("id") or not account.get("tenantId"):
            raise ValidationError("Azure CLI returned no subscription or tenant.")
        subscription = str(account["id"])
        tid = str(account["tenantId"])
        if not _same_id(target, subscription) or not _same_id(cfg.tenant_id, tid):
            raise SafetyError("The signed-in Azure account does not match the requested subscription or tenant.")
        resource = ["--resource", audience] if audience else ["--resource-type", "arm"]
        result = _az_json(["account", "get-access-token", "--subscription", subscription, *resource], timeout=timeout)
        token = result.get("accessToken") if isinstance(result, dict) else None
        if not isinstance(token, str) or not token.strip():
            raise ValidationError("Azure CLI did not return an access token.")
        claims = _claims(token)
        if not _same_id(tid, result.get("tenant")) or not _same_id(tid, claims.get("tid")) or not _same_id(subscription, result.get("subscription")):
            raise SafetyError("Azure returned a token for a different subscription or tenant.")
        object_id = claims.get("oid") or claims.get("sub")
        identity = str(object_id) if object_id else "CLI credential " + hashlib.sha256(token.encode()).hexdigest()
        source = "Azure CLI"
    if cfg.tenant_id and (not tid or not _same_id(tid, cfg.tenant_id)):
        raise SafetyError("The connected Azure tenant differs from AZURE_TENANT_ID.")
    if cfg.allowed_tenants and (not tid or str(tid).casefold() not in {t.casefold() for t in cfg.allowed_tenants}):
        raise SafetyError("The connected Azure tenant is outside AZURE_ALLOWED_TENANTS.")
    if cfg.allowed_subscriptions and subscription and subscription.casefold() not in {s.casefold() for s in cfg.allowed_subscriptions}:
        raise SafetyError("The selected Azure subscription is outside AZURE_ALLOWED_SUBSCRIPTIONS.")
    return AzureConnection(token, subscription, str(tid) if tid else None, identity, endpoint, source)

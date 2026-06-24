from __future__ import annotations

from dataclasses import dataclass

import boto3
from botocore.config import Config as BotoConfig

from .config import Config
from .errors import ValidationError


@dataclass(frozen=True)
class CallerIdentity:
    account: str
    arn: str
    user_id: str


def make_sts_client(cfg: Config):
    session_kwargs: dict[str, str] = {"region_name": cfg.region_name}
    if cfg.profile_name:
        session_kwargs["profile_name"] = cfg.profile_name
    session = boto3.Session(**session_kwargs)
    client_cfg = BotoConfig(
        connect_timeout=cfg.timeout_s,
        read_timeout=cfg.timeout_s,
        retries={"max_attempts": 0},
    )
    return session.client("sts", region_name=cfg.region_name, config=client_cfg)


def fetch_caller_identity(cfg: Config, *, client=None) -> CallerIdentity:
    sts_client = client or make_sts_client(cfg)
    try:
        response = sts_client.get_caller_identity()
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"STS get-caller-identity failed: {type(e).__name__}: {e}") from None
    account = str(response.get("Account") or "").strip()
    arn = str(response.get("Arn") or "").strip()
    user_id = str(response.get("UserId") or "").strip()
    if not account or not arn or not user_id:
        raise ValidationError("STS get-caller-identity returned an incomplete response")
    return CallerIdentity(account=account, arn=arn, user_id=user_id)


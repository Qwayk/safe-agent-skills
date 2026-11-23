from __future__ import annotations

from dataclasses import dataclass

import boto3
from botocore.config import Config as BotoConfig

from .config import Config
from .errors import ValidationError
from .model_loader import pinned_session


@dataclass(frozen=True)
class CallerIdentity:
    account: str
    arn: str
    user_id: str

    def for_plan(self) -> dict[str, str]:
        # An assumed role can have a new session name without changing the role.
        if ":assumed-role/" in self.arn and self.arn.count("/") >= 2:
            return {"account": self.account, "arn": self.arn.rsplit("/", 1)[0],
                    "id": self.user_id.partition(":")[0]}
        return {"account": self.account, "arn": self.arn, "id": self.user_id}


def make_session(cfg: Config):
    return boto3.Session(
        botocore_session=pinned_session(), profile_name=cfg.profile_name, region_name=cfg.region_name,
    )


def make_client(cfg: Config, service: str, *, session=None, api_version: str | None = None):
    session = session if session is not None else make_session(cfg)
    client_cfg = BotoConfig(
        connect_timeout=cfg.timeout_s,
        read_timeout=cfg.timeout_s,
        retries={"max_attempts": 0},
    )
    return session.client(service, region_name=cfg.region_name, api_version=api_version, config=client_cfg)


def fetch_caller_identity(cfg: Config, *, client=None) -> CallerIdentity:
    sts_client = client if client is not None else make_client(cfg, "sts")
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


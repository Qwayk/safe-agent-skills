from __future__ import annotations

from ..allowlists import AllowLists
from ..redaction import redact_obj
from ..sts_identity import fetch_caller_identity


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    identity = fetch_caller_identity(cfg)
    allowlists = AllowLists(accounts=cfg.allowed_accounts, regions=cfg.allowed_regions)
    reasons = allowlists.check(account_id=identity.account, region_name=cfg.region_name)
    out = {
        "ok": True,
        "auth": {
            "region": cfg.region_name,
            "profile": cfg.profile_name,
            "timeout_s": cfg.timeout_s,
            "caller_identity": {
                "account": identity.account,
                "arn": identity.arn,
                "user_id": identity.user_id,
            },
            "allowlists": {
                "allowed_accounts": list(cfg.allowed_accounts),
                "allowed_regions": list(cfg.allowed_regions),
                "allowed": not reasons,
                "reasons": reasons,
            },
        },
    }
    out = redact_obj(out)
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0

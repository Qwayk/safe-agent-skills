from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from ..errors import ValidationError


def cmd_build(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    domain_specific_id = str(getattr(args, "id", None) or cfg.link_wrapper_id or "").strip()
    target_url = str(getattr(args, "url", "") or "").strip()
    if not domain_specific_id:
        raise ValidationError("Missing Link Wrapper id. Set SKIMLINKS_LINK_WRAPPER_ID or pass --id.")
    if not target_url:
        raise ValidationError("Missing --url.")
    if not (target_url.startswith("http://") or target_url.startswith("https://")):
        raise ValidationError("--url must start with http:// or https://.")

    params = {"id": domain_specific_id, "url": target_url}
    if getattr(args, "xcust", None):
        params["xcust"] = str(args.xcust)
    if getattr(args, "sref", None):
        params["sref"] = str(args.sref)

    base = cfg.link_wrapper_base_url
    if not base.endswith("/"):
        base += "/"
    wrapped_url = base + "?" + urlencode(params)
    out = {
        "ok": True,
        "family": "link_wrapper",
        "operation": "build",
        "method": "URL construction",
        "base_url": base,
        "wrapped_url": wrapped_url,
        "followed_redirect": False,
        "params": {
            "id": domain_specific_id,
            "url": target_url,
            "xcust": params.get("xcust"),
            "sref": params.get("sref"),
        },
        "note": "This command builds the official Link Wrapper URL locally and does not click it.",
    }
    ctx["audit"].write("link_wrapper.build", {"ok": True, "followed_redirect": False})
    ctx["out"].emit(out)
    return 0

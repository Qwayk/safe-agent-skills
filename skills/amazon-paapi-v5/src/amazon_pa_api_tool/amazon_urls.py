from __future__ import annotations

import re
from urllib.parse import urlparse


_ASIN_PATTERNS = [
    re.compile(r"/dp/([A-Z0-9]{10})(?:[/?]|$)"),
    re.compile(r"/gp/product/([A-Z0-9]{10})(?:[/?]|$)"),
    re.compile(r"/product/([A-Z0-9]{10})(?:[/?]|$)"),
    re.compile(r"/ASIN/([A-Z0-9]{10})(?:[/?]|$)", re.IGNORECASE),
]


def extract_asin_from_url(url: str) -> str | None:
    raw = (url or "").strip()
    if not raw:
        return None
    try:
        parsed = urlparse(raw)
    except Exception:
        return None

    host = (parsed.netloc or "").lower()
    if host.endswith("amzn.to"):
        return None

    path = parsed.path or ""
    for pat in _ASIN_PATTERNS:
        m = pat.search(path)
        if m:
            return m.group(1).upper()
    return None


def build_affiliate_dp_link(*, marketplace: str, asin: str, partner_tag: str) -> str:
    a = (asin or "").strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{10}", a):
        raise ValueError("Invalid ASIN (expected 10 alphanumeric characters)")
    tag = (partner_tag or "").strip()
    if not tag:
        raise ValueError("Missing partner tag")
    mp = (marketplace or "").strip()
    if not mp:
        raise ValueError("Missing marketplace")
    return f"https://{mp}/dp/{a}/?tag={tag}"


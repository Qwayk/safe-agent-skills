from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, urlparse


@dataclass(frozen=True)
class AmazonLinkInfo:
    url: str
    host: str | None
    is_amzn_short: bool
    is_amazon: bool
    affiliate_tag: str | None


def _host_from_url(raw: str) -> str | None:
    s = (raw or "").strip()
    if not s:
        return None
    try:
        p = urlparse(s)
    except Exception:
        return None
    if p.hostname:
        return p.hostname.lower()
    return None


def _is_amazon_host(host: str) -> bool:
    h = (host or "").lower().strip(".")
    if not h:
        return False
    if h == "amzn.to" or h.endswith(".amzn.to"):
        return True
    # Handle country TLDs: amazon.com, amazon.co.uk, amazon.de, etc.
    if h == "amazon.com" or h.endswith(".amazon.com"):
        return True
    if ".amazon." in h and not h.endswith(".amazonaws.com"):
        return True
    return False


def parse_amazon_link(url: str) -> AmazonLinkInfo | None:
    raw = (url or "").strip()
    if not raw:
        return None
    host = _host_from_url(raw)
    if host is None or not _is_amazon_host(host):
        return None

    is_amzn_short = host == "amzn.to" or host.endswith(".amzn.to")

    tag = None
    if not is_amzn_short:
        try:
            q = urlparse(raw).query
            qs = parse_qs(q)
            v = qs.get("tag")
            if isinstance(v, list) and v:
                tag = str(v[0]).strip() or None
        except Exception:
            tag = None

    return AmazonLinkInfo(
        url=raw,
        host=host,
        is_amzn_short=is_amzn_short,
        is_amazon=True,
        affiliate_tag=tag,
    )


def is_amazon_link(url: str) -> bool:
    return parse_amazon_link(url) is not None


def is_amazon_affiliate_link(url: str) -> bool:
    info = parse_amazon_link(url)
    return bool(info and info.affiliate_tag)


def amazon_link_row(info: AmazonLinkInfo) -> dict[str, Any]:
    return {
        "url": info.url,
        "host": info.host or "",
        "is_amzn_short": "true" if info.is_amzn_short else "false",
        "affiliate_tag": info.affiliate_tag or "",
        "is_affiliate": "true" if bool(info.affiliate_tag) else "false",
    }


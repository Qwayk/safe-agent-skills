from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ..freepik_api import FreepikApi
from ..http import HttpClient
from ..jsonpath import find_url_by_keywords


def _preview_suffix(url: str) -> str:
    suffix = Path(urlparse(url).path).suffix
    return suffix if suffix else ".preview"


def cmd_preview(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"], user_agent="freepik-api-tool/0.1")
    api = FreepikApi(cfg=cfg, http=http)

    rid = args.id
    detail = api.get_resource(rid)
    preview_url = find_url_by_keywords(detail, include=("preview", "thumbnail", "thumb", "image"), exclude=("license",))
    if not preview_url:
        raise RuntimeError("Refused: could not find a preview URL in resource detail response")

    save_dir = args.save_preview
    if not save_dir:
        ctx["out"].emit({"resource_id": rid, "preview_url": preview_url})
        return 0

    # Download preview image (this should not consume license/download, but relies on Freepik providing a direct URL).
    out_dir = Path(save_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{rid}{_preview_suffix(preview_url)}"
    http.download_to_path(preview_url, out_path, retries=2)
    ctx["out"].emit({"resource_id": rid, "preview_url": preview_url, "saved_to": str(out_path)})
    return 0

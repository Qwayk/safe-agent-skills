from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from ..api_call import build_api_call_plan, write_plan_if_requested
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..youtube_discovery import get_method_info, load_official_discovery_doc
from .api import _oauth_access_token


_CHANNEL_ID_RE = re.compile(r"^UC[a-zA-Z0-9_-]{22}$")


def _channel_url(channel_id: str) -> str:
    return f"https://www.youtube.com/channel/{channel_id}"


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass(frozen=True)
class ChannelInput:
    raw: str
    kind: str
    value: str

    def to_dict(self) -> dict[str, Any]:
        return {"raw": self.raw, "kind": self.kind, "value": self.value}


def parse_channel_input(raw: str) -> ChannelInput:
    s = str(raw or "").strip()
    if not s:
        raise ValidationError("Missing channel input")

    # Raw forms.
    if _CHANNEL_ID_RE.match(s):
        return ChannelInput(raw=s, kind="channel_id", value=s)
    if s.startswith("@") and len(s) > 1:
        return ChannelInput(raw=s, kind="handle", value=s[1:])

    # URL-ish forms.
    if "://" in s:
        parts = urlsplit(s)
        path = unquote(parts.path or "").strip()
        if not path:
            return ChannelInput(raw=s, kind="query", value=s)

        segs = [x for x in path.split("/") if x]
        if not segs:
            return ChannelInput(raw=s, kind="query", value=s)

        # Common canonical: /channel/UC...
        if len(segs) >= 2 and segs[0] == "channel" and _CHANNEL_ID_RE.match(segs[1]):
            return ChannelInput(raw=s, kind="channel_id", value=segs[1])

        # Handle URLs: /@handle or /@handle/...
        for seg in segs:
            if seg.startswith("@") and len(seg) > 1:
                return ChannelInput(raw=s, kind="handle", value=seg[1:])

        # Legacy username: /user/<name>
        if len(segs) >= 2 and segs[0] == "user" and segs[1]:
            return ChannelInput(raw=s, kind="username", value=segs[1])

        # Custom channel URL: /c/<name>
        if len(segs) >= 2 and segs[0] == "c" and segs[1]:
            return ChannelInput(raw=s, kind="query", value=segs[1])

        return ChannelInput(raw=s, kind="query", value=s)

    # Anything else: treat as an ambiguous query string.
    return ChannelInput(raw=s, kind="query", value=s)


def _snippet_preview(snippet: Any) -> dict[str, Any] | None:
    if not isinstance(snippet, dict):
        return None
    thumbs = snippet.get("thumbnails")
    default_thumb = None
    if isinstance(thumbs, dict):
        t = thumbs.get("default") or thumbs.get("medium") or thumbs.get("high")
        if isinstance(t, dict) and isinstance(t.get("url"), str):
            default_thumb = {"url": t.get("url")}
    return {
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "customUrl": snippet.get("customUrl"),
        "publishedAt": snippet.get("publishedAt"),
        "thumbnails": {"default": default_thumb} if default_thumb else None,
    }


def _sha256_hex(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def _canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _auth_headers_and_params(*, ctx: dict[str, Any], params: dict[str, Any]) -> tuple[dict[str, str], dict[str, Any]]:
    cfg = ctx["cfg"]

    token: str | None
    if getattr(cfg, "api_key", None):
        try:
            token = _oauth_access_token(ctx=ctx)
        except Exception:
            token = None
    else:
        try:
            token = _oauth_access_token(ctx=ctx)
        except Exception:
            token = None

    if not token and not getattr(cfg, "api_key", None):
        raise ValidationError("Missing credentials: set YOUTUBE_API_KEY or run `youtube-api-tool auth login --console`")

    headers: dict[str, str] = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    query_params = dict(params)
    if getattr(cfg, "api_key", None) and not token and "key" not in query_params:
        query_params["key"] = cfg.api_key

    return headers, query_params


def _api_get_json(*, ctx: dict[str, Any], method: str, params: dict[str, Any]) -> dict[str, Any]:
    cfg = ctx["cfg"]
    discovery = load_official_discovery_doc()
    info = get_method_info(discovery_obj=discovery, method_name=method)

    headers, query_params = _auth_headers_and_params(ctx=ctx, params=params)

    client = HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx["verbose"]),
        user_agent=f"youtube-api-tool/{ctx.get('tool_version')}",
    )

    base_url = str(cfg.base_url).rstrip("/")
    url = base_url + "/" + str(info.path).lstrip("/")
    resp = client.request("GET", url, headers=headers, params=query_params, json_body=None, retries=3)
    try:
        data = resp.json()
    except Exception:
        data = None
    return {"status": resp.status, "url": resp.url, "json": data}


def _resolve_with_channels_list(
    *,
    ctx: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    resp = _api_get_json(ctx=ctx, method="channels.list", params=params)
    data = resp.get("json")

    items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items, list):
        items = []

    if len(items) != 1:
        return {
            "ok": True,
            "refused": True,
            "reasons": ["No channel found for input" if len(items) == 0 else "Selection required: multiple channels matched"],
            "refusal_type": "SelectionRequired" if len(items) > 1 else "NotFound",
            "matches": len(items),
        }

    it = items[0] if isinstance(items[0], dict) else {}
    channel_id = str(it.get("id") or "").strip()
    snippet = it.get("snippet")
    title = str(snippet.get("title") or "").strip() if isinstance(snippet, dict) else ""
    return {
        "ok": True,
        "channel_id": channel_id or None,
        "channel_url": _channel_url(channel_id) if channel_id else None,
        "title": title or None,
        "snippet": _snippet_preview(snippet),
        "raw": it,
    }


def _resolve_with_search_list(
    *,
    ctx: dict[str, Any],
    query: str,
    max_results: int,
    pick: int | None,
) -> dict[str, Any]:
    resp = _api_get_json(
        ctx=ctx,
        method="search.list",
        params={"part": "snippet", "type": "channel", "q": query, "maxResults": int(max_results)},
    )
    data = resp.get("json")

    items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items, list):
        items = []

    candidates: list[dict[str, Any]] = []
    for idx, raw in enumerate(items, start=1):
        if not isinstance(raw, dict):
            continue
        rid = raw.get("id")
        channel_id = None
        if isinstance(rid, dict) and isinstance(rid.get("channelId"), str):
            channel_id = str(rid.get("channelId") or "").strip() or None
        snippet = raw.get("snippet")
        title = str(snippet.get("title") or "").strip() if isinstance(snippet, dict) else ""
        candidates.append(
            {
                "index": idx,
                "channel_id": channel_id,
                "channel_url": _channel_url(channel_id) if channel_id else None,
                "title": title or None,
                "snippet": _snippet_preview(snippet),
                "raw": raw,
            }
        )

    if not candidates:
        return {
            "ok": True,
            "refused": True,
            "reasons": ["No channel found for input"],
            "refusal_type": "NotFound",
            "candidates": [],
        }

    if len(candidates) == 1:
        one = candidates[0]
        return {
            "ok": True,
            "channel_id": one.get("channel_id"),
            "channel_url": one.get("channel_url"),
            "title": one.get("title"),
            "snippet": one.get("snippet"),
            "raw": one.get("raw"),
            "source": {"method": "search.list"},
        }

    if pick is None:
        suggested = []
        for c in candidates[:3]:
            cid = c.get("channel_id")
            if isinstance(cid, str) and cid:
                suggested.append(f"youtube-api-tool --output json channels resolve --channel {cid} --live")
        return {
            "ok": True,
            "refused": True,
            "reasons": ["Selection required: multiple channels matched"],
            "refusal_type": "SelectionRequired",
            "candidates": candidates,
            "selection": {
                "required": True,
                "mechanisms": [
                    {"type": "pick", "example": "youtube-api-tool --output json channels resolve --channel \"<QUERY>\" --live --pick 1"},
                    {"type": "channel_id", "note": "Re-run resolve with an explicit channelId for an unambiguous result."},
                ],
            },
            "suggested_next_commands": suggested,
        }

    if pick <= 0 or pick > len(candidates):
        return {
            "ok": True,
            "refused": True,
            "reasons": [f"Invalid --pick: {pick} (must be between 1 and {len(candidates)})"],
            "refusal_type": "SelectionRequired",
            "candidates": candidates,
        }

    chosen = candidates[pick - 1]
    return {
        "ok": True,
        "channel_id": chosen.get("channel_id"),
        "channel_url": chosen.get("channel_url"),
        "title": chosen.get("title"),
        "snippet": chosen.get("snippet"),
        "raw": chosen.get("raw"),
        "source": {"method": "search.list", "picked_index": int(pick)},
    }


def cmd_channels_resolve(args: Any, ctx: dict[str, Any]) -> int:
    raw = str(getattr(args, "channel", "") or "").strip()
    max_results = int(getattr(args, "max_results", 5) or 5)
    if max_results <= 0 or max_results > 50:
        raise ValidationError("--max-results must be between 1 and 50")
    pick = getattr(args, "pick", None)
    if pick is not None:
        pick = int(pick)

    inp = parse_channel_input(raw)
    live = bool(getattr(args, "live", False))

    if inp.kind == "channel_id":
        method = "channels.list"
        params = {"part": "snippet", "id": inp.value}
    elif inp.kind == "handle":
        method = "channels.list"
        params = {"part": "snippet", "forHandle": inp.value}
    elif inp.kind == "username":
        method = "channels.list"
        params = {"part": "snippet", "forUsername": inp.value}
    else:
        method = "search.list"
        params = {"part": "snippet", "type": "channel", "q": inp.value, "maxResults": max_results}

    plan = build_api_call_plan(ctx=ctx, method=method, params=params, body=None, upload=None, download=None)
    plan_path = write_plan_if_requested(ctx=ctx, plan=plan)

    if not live:
        ctx["audit"].write(
            "channels.resolve.plan",
            {"input": inp.to_dict(), "method": method, "plan_out": plan_path},
        )
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    if method == "channels.list":
        resolved = _resolve_with_channels_list(ctx=ctx, params=params)
        if resolved.get("refused"):
            ctx["audit"].write("channels.resolve.refused", {"input": inp.to_dict(), "method": method})
            ctx["out"].emit(
                {
                    "ok": True,
                    "refused": True,
                    "reasons": resolved.get("reasons") or ["Refused"],
                    "refusal_type": resolved.get("refusal_type"),
                    "input": inp.to_dict(),
                    "live": True,
                    "plan_out": plan_path,
                }
            )
            return 0
        ctx["audit"].write("channels.resolve.live", {"input": inp.to_dict(), "method": method})
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": False,
                "live": True,
                "method": method,
                "input": inp.to_dict(),
                "channel": resolved,
                "plan_out": plan_path,
            }
        )
        return 0

    resolved2 = _resolve_with_search_list(ctx=ctx, query=inp.value, max_results=max_results, pick=pick)
    if resolved2.get("refused"):
        ctx["audit"].write("channels.resolve.refused", {"input": inp.to_dict(), "method": method})
        ctx["out"].emit(
            {
                "ok": True,
                "refused": True,
                "reasons": resolved2.get("reasons") or ["Refused"],
                "refusal_type": resolved2.get("refusal_type"),
                "input": inp.to_dict(),
                "live": True,
                "method": method,
                "candidates": resolved2.get("candidates") or [],
                "selection": resolved2.get("selection"),
                "suggested_next_commands": resolved2.get("suggested_next_commands"),
                "plan_out": plan_path,
            }
        )
        return 0

    ctx["audit"].write("channels.resolve.live", {"input": inp.to_dict(), "method": method})
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "live": True,
            "method": method,
            "input": inp.to_dict(),
            "channel": resolved2,
            "plan_out": plan_path,
        }
    )
    return 0


def _dir_has_any_files(p: Path) -> bool:
    try:
        if not p.exists() or not p.is_dir():
            return False
        for _ in p.iterdir():
            return True
        return False
    except Exception:
        return True


def _read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [ln.rstrip("\n") for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _append_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:  # noqa: PTH123
        for ln in lines:
            f.write(str(ln).rstrip("\n") + "\n")


def _write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:  # noqa: PTH123
        for ln in lines:
            f.write(str(ln).rstrip("\n") + "\n")


def _checkpoint_path(out_dir: Path) -> Path:
    return out_dir / "checkpoint.json"


def _dataset_paths(out_dir: Path) -> dict[str, Path]:
    return {
        "manifest": out_dir / "manifest.json",
        "channel": out_dir / "channel.json",
        "video_ids": out_dir / "video_ids.txt",
        "video_urls": out_dir / "video_urls.txt",
        "videos_jsonl": out_dir / "videos.jsonl",
        "checkpoint": _checkpoint_path(out_dir),
    }


def _checkpoint_default(*, channel_input: ChannelInput, out_dir: Path) -> dict[str, Any]:
    p = _dataset_paths(out_dir)
    return {
        "schema_version": 1,
        "created_at_utc": _utc_now(),
        "updated_at_utc": _utc_now(),
        "stage": "playlist_items",
        "channel_input": channel_input.to_dict(),
        "resolved_channel_id": None,
        "uploads_playlist_id": None,
        "playlist_items": {
            "next_page_token": None,
            "pages_fetched": 0,
            "video_ids_path": str(p["video_ids"]),
        },
        "videos": {
            "video_parts": None,
            "next_index": 0,
            "videos_jsonl_path": str(p["videos_jsonl"]),
        },
    }


def _write_checkpoint(out_dir: Path, checkpoint: dict[str, Any]) -> str:
    checkpoint["updated_at_utc"] = _utc_now()
    return write_json_file(_checkpoint_path(out_dir), checkpoint)


def _load_checkpoint(out_dir: Path) -> dict[str, Any]:
    obj = read_json_file(_checkpoint_path(out_dir))
    if not isinstance(obj, dict):
        raise ValidationError("checkpoint.json must be a JSON object")
    if int(obj.get("schema_version") or 0) != 1:
        raise ValidationError("Unsupported checkpoint schema_version")
    return obj


def _build_channels_export_plan(
    *,
    ctx: dict[str, Any],
    channel_input: ChannelInput,
    out_dir: str,
    overwrite: bool,
    resume: bool,
    max_pages: int,
    video_parts: str,
    max_results: int,
    pick: int | None,
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "youtube-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url if ctx.get("cfg") else None,
        "command": ctx.get("command_str") or None,
        "selector": {"kind": "youtube_channel_export", "value": channel_input.to_dict()},
        "risk_level": "low",
        "risk_reasons": ["Read-only API methods (GET) + local dataset files"],
        "preconditions": [
            "Pass --live to execute network reads and write the dataset",
            "Output directory must be empty unless --overwrite/--yes or --resume is used",
        ],
        "inputs": {
            "channel": channel_input.to_dict(),
            "out_dir": out_dir,
            "overwrite": bool(overwrite),
            "resume": bool(resume),
            "max_pages": int(max_pages),
            "video_parts": str(video_parts),
            "max_results": int(max_results),
            "pick": int(pick) if pick is not None else None,
        },
        "official_methods": [
            {
                "method": "channels.list",
                "purpose": "Resolve channel and read uploads playlist (contentDetails.relatedPlaylists.uploads)",
            },
            {"method": "playlistItems.list", "purpose": "Enumerate uploads playlist to collect video IDs"},
            {"method": "videos.list", "purpose": "Fetch metadata/statistics for video IDs in batches of 50"},
        ],
        "output_layout": {
            "manifest.json": "Export summary (inputs, counts, errors, and notes)",
            "channel.json": "Resolved channel resource",
            "video_ids.txt": "One videoId per line",
            "video_urls.txt": "One watch URL per line (https://www.youtube.com/watch?v=<id>)",
            "videos.jsonl": "One JSON object per video (analysis-friendly; stable JSON keys)",
            "checkpoint.json": "Resume checkpoint (do not edit manually)",
        },
        "notes": [
            "Transcripts/captions are not exported: the official YouTube Data API v3 does not allow downloading captions for arbitrary public channels without owner permission.",
        ],
        "verification_plan": {
            "type": "local_files",
            "notes": "On completion, the tool writes a manifest with counts and SHA256 fingerprints for key outputs.",
        },
    }


def _resolve_channel_for_export(
    *,
    ctx: dict[str, Any],
    channel_input: ChannelInput,
    max_results: int,
    pick: int | None,
) -> dict[str, Any]:
    """
    Return a `channels.list` item (dict) with part=snippet,contentDetails.
    """
    if channel_input.kind in {"channel_id", "handle", "username"}:
        params: dict[str, Any] = {"part": "snippet,contentDetails"}
        if channel_input.kind == "channel_id":
            params["id"] = channel_input.value
        elif channel_input.kind == "handle":
            params["forHandle"] = channel_input.value
        else:
            params["forUsername"] = channel_input.value
    else:
        resolved = _resolve_with_search_list(ctx=ctx, query=channel_input.value, max_results=max_results, pick=pick)
        if resolved.get("refused"):
            return resolved
        cid = resolved.get("channel_id")
        if not isinstance(cid, str) or not cid.strip():
            return {"ok": True, "refused": True, "reasons": ["No channelId available from search results"], "refusal_type": "NotFound"}
        params = {"part": "snippet,contentDetails", "id": cid.strip()}

    resp = _api_get_json(ctx=ctx, method="channels.list", params=params)
    data = resp.get("json")
    items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items, list):
        items = []
    if len(items) != 1 or not isinstance(items[0], dict):
        return {
            "ok": True,
            "refused": True,
            "reasons": ["No channel found for input" if len(items) == 0 else "Selection required: multiple channels matched"],
            "refusal_type": "SelectionRequired" if len(items) > 1 else "NotFound",
        }
    return {"ok": True, "channel": items[0]}


def _uploads_playlist_id(channel_item: dict[str, Any]) -> str | None:
    cd = channel_item.get("contentDetails")
    if not isinstance(cd, dict):
        return None
    rp = cd.get("relatedPlaylists")
    if not isinstance(rp, dict):
        return None
    up = rp.get("uploads")
    return str(up).strip() if isinstance(up, str) and up.strip() else None


def _watch_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def _write_manifest(
    *,
    out_dir: Path,
    paths: dict[str, Path],
    started_at_utc: str,
    finished_at_utc: str | None,
    completed: bool,
    channel_input: ChannelInput,
    resolved_channel_id: str | None,
    uploads_playlist_id: str | None,
    pages_fetched: int,
    video_ids_count: int,
    videos_emitted_count: int,
    video_parts: str,
    errors: list[dict[str, Any]],
) -> None:
    video_ids_sha256 = None
    if paths["video_ids"].exists():
        video_ids_sha256 = _sha256_hex(paths["video_ids"].read_bytes())
    videos_jsonl_sha256 = None
    if paths["videos_jsonl"].exists():
        videos_jsonl_sha256 = _sha256_hex(paths["videos_jsonl"].read_bytes())

    manifest = {
        "schema_version": 1,
        "started_at_utc": started_at_utc,
        "finished_at_utc": finished_at_utc,
        "completed": bool(completed),
        "inputs": {
            "channel": channel_input.to_dict(),
            "resolved_channel_id": resolved_channel_id,
            "uploads_playlist_id": uploads_playlist_id,
        },
        "counts": {
            "playlist_pages_fetched": int(pages_fetched),
            "video_ids": int(video_ids_count),
            "videos_jsonl_rows": int(videos_emitted_count),
        },
        "files": {
            "manifest_json": str(paths["manifest"]),
            "channel_json": str(paths["channel"]),
            "video_ids_txt": str(paths["video_ids"]),
            "video_urls_txt": str(paths["video_urls"]),
            "videos_jsonl": str(paths["videos_jsonl"]),
            "checkpoint_json": str(paths["checkpoint"]),
        },
        "sha256": {
            "video_ids_txt": video_ids_sha256,
            "videos_jsonl": videos_jsonl_sha256,
        },
        "video_parts": str(video_parts),
        "notes": [
            "Transcripts/captions are not included. The official YouTube Data API v3 does not allow downloading captions for arbitrary public channels without owner permission.",
        ],
        "errors": errors,
    }
    write_json_file(paths["manifest"], manifest)


def _videos_jsonl_line(*, video_id: str, video_obj: dict[str, Any] | None, missing: bool) -> str:
    row = {
        "video_id": video_id,
        "watch_url": _watch_url(video_id),
        "missing": bool(missing),
        "video": video_obj,
    }
    return _canonical_json_bytes(row).decode("utf-8") + "\n"


def cmd_channels_export(args: Any, ctx: dict[str, Any]) -> int:
    if bool(ctx.get("apply")):
        raise ValidationError("channels export is read-only; do not pass --apply (use --live instead)")

    raw = str(getattr(args, "channel", "") or "").strip()
    out_dir = Path(str(getattr(args, "out_dir", "") or "").strip())
    if not raw:
        raise ValidationError("Missing --channel")
    if not str(out_dir):
        raise ValidationError("Missing --out-dir")

    live = bool(getattr(args, "live", False))
    overwrite = bool(getattr(args, "overwrite", False)) or bool(ctx.get("yes"))
    resume = bool(getattr(args, "resume", False))
    max_pages = int(getattr(args, "max_pages", 2000) or 2000)
    if max_pages <= 0:
        raise ValidationError("--max-pages must be >= 1")
    video_parts = str(getattr(args, "video_parts", "") or "").strip() or "snippet,contentDetails,statistics"
    max_results = int(getattr(args, "max_results", 5) or 5)
    if max_results <= 0 or max_results > 50:
        raise ValidationError("--max-results must be between 1 and 50")
    pick = getattr(args, "pick", None)
    if pick is not None:
        pick = int(pick)

    channel_input = parse_channel_input(raw)

    plan = _build_channels_export_plan(
        ctx=ctx,
        channel_input=channel_input,
        out_dir=str(out_dir),
        overwrite=overwrite,
        resume=resume,
        max_pages=max_pages,
        video_parts=video_parts,
        max_results=max_results,
        pick=pick,
    )
    plan_path = write_plan_if_requested(ctx=ctx, plan=plan)

    if not live:
        ctx["audit"].write("channels.export.plan", {"input": channel_input.to_dict(), "out_dir": str(out_dir), "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    if resume and not out_dir.exists():
        raise SafetyError("Refused: --resume requires an existing --out-dir with checkpoint.json")

    if out_dir.exists() and out_dir.is_dir() and _dir_has_any_files(out_dir) and not (overwrite or resume):
        raise SafetyError("Refused: output directory is not empty (pass --overwrite/--yes or use --resume)")

    out_dir.mkdir(parents=True, exist_ok=True)
    paths = _dataset_paths(out_dir)

    started_at_utc = _utc_now()
    errors: list[dict[str, Any]] = []

    checkpoint: dict[str, Any]
    if resume:
        checkpoint = _load_checkpoint(out_dir)
    else:
        checkpoint = _checkpoint_default(channel_input=channel_input, out_dir=out_dir)
        if overwrite:
            # Ensure we start clean for deterministic exports.
            for k in ("videos_jsonl", "video_ids", "video_urls"):
                try:
                    if paths[k].exists():
                        paths[k].unlink()
                except Exception:
                    pass
        _write_checkpoint(out_dir, checkpoint)

    stage = str(checkpoint.get("stage") or "playlist_items")

    # Stage 1: resolve channel and collect video IDs from uploads playlist.
    resolved_channel_id: str | None = checkpoint.get("resolved_channel_id") if isinstance(checkpoint.get("resolved_channel_id"), str) else None
    uploads_pid: str | None = checkpoint.get("uploads_playlist_id") if isinstance(checkpoint.get("uploads_playlist_id"), str) else None
    pages_fetched = int(((checkpoint.get("playlist_items") or {}).get("pages_fetched") or 0))
    next_page_token = (checkpoint.get("playlist_items") or {}).get("next_page_token")
    next_page_token = str(next_page_token).strip() if isinstance(next_page_token, str) and next_page_token.strip() else None

    seen_ids: set[str] = set()
    ordered_ids: list[str] = []
    for ln in _read_lines(paths["video_ids"]):
        if ln not in seen_ids:
            seen_ids.add(ln)
            ordered_ids.append(ln)

    if stage == "playlist_items":
        resolved = _resolve_channel_for_export(ctx=ctx, channel_input=channel_input, max_results=max_results, pick=pick)
        if resolved.get("refused"):
            ctx["audit"].write("channels.export.refused", {"input": channel_input.to_dict(), "out_dir": str(out_dir)})
            ctx["out"].emit(
                {
                    "ok": True,
                    "refused": True,
                    "reasons": resolved.get("reasons") or ["Refused"],
                    "refusal_type": resolved.get("refusal_type"),
                    "candidates": resolved.get("candidates") or [],
                    "selection": resolved.get("selection"),
                    "suggested_next_commands": resolved.get("suggested_next_commands") or [],
                    "input": channel_input.to_dict(),
                    "out_dir": str(out_dir),
                    "plan_out": plan_path,
                }
            )
            return 0

        channel_item = resolved.get("channel")
        if not isinstance(channel_item, dict):
            raise RuntimeError("Internal error: resolved channel missing channel object")

        resolved_channel_id = str(channel_item.get("id") or "").strip() or None
        uploads_pid = _uploads_playlist_id(channel_item)
        if not resolved_channel_id or not uploads_pid:
            raise RuntimeError("Resolved channel missing id or uploads playlist id")

        checkpoint["resolved_channel_id"] = resolved_channel_id
        checkpoint["uploads_playlist_id"] = uploads_pid
        _write_checkpoint(out_dir, checkpoint)

        # Write channel.json early so partial runs still have context.
        write_json_file(paths["channel"], channel_item)

        # Continue playlistItems pagination.
        while True:
            if pages_fetched >= max_pages:
                # Stop early for safety; allow resume.
                checkpoint["stage"] = "playlist_items"
                checkpoint["playlist_items"]["pages_fetched"] = pages_fetched
                checkpoint["playlist_items"]["next_page_token"] = next_page_token
                _write_checkpoint(out_dir, checkpoint)
                _write_manifest(
                    out_dir=out_dir,
                    paths=paths,
                    started_at_utc=started_at_utc,
                    finished_at_utc=None,
                    completed=False,
                    channel_input=channel_input,
                    resolved_channel_id=resolved_channel_id,
                    uploads_playlist_id=uploads_pid,
                    pages_fetched=pages_fetched,
                    video_ids_count=len(ordered_ids),
                    videos_emitted_count=0,
                    video_parts=video_parts,
                    errors=errors,
                )
                ctx["out"].emit(
                    {
                        "ok": True,
                        "dry_run": False,
                        "live": True,
                        "completed": False,
                        "partial_reason": f"Reached --max-pages limit ({max_pages}) before exhausting playlistItems",
                        "out_dir": str(out_dir),
                        "checkpoint": str(paths["checkpoint"]),
                        "counts": {"pages_fetched": pages_fetched, "video_ids": len(ordered_ids)},
                        "next_safe_step": "Re-run with --resume to continue (or increase --max-pages).",
                        "plan_out": plan_path,
                    }
                )
                return 0

            params: dict[str, Any] = {"part": "contentDetails", "playlistId": uploads_pid, "maxResults": 50}
            if next_page_token:
                params["pageToken"] = next_page_token
            resp = _api_get_json(ctx=ctx, method="playlistItems.list", params=params)
            data = resp.get("json")
            items = data.get("items") if isinstance(data, dict) else None
            if not isinstance(items, list):
                items = []

            new_ids: list[str] = []
            for it in items:
                if not isinstance(it, dict):
                    continue
                cd = it.get("contentDetails")
                if not isinstance(cd, dict):
                    continue
                vid = cd.get("videoId")
                if isinstance(vid, str) and vid.strip():
                    v = vid.strip()
                    if v not in seen_ids:
                        seen_ids.add(v)
                        ordered_ids.append(v)
                        new_ids.append(v)
            if new_ids:
                _append_lines(paths["video_ids"], new_ids)

            next_page_token = data.get("nextPageToken") if isinstance(data, dict) else None
            next_page_token = str(next_page_token).strip() if isinstance(next_page_token, str) and next_page_token.strip() else None
            pages_fetched += 1

            checkpoint["playlist_items"]["pages_fetched"] = pages_fetched
            checkpoint["playlist_items"]["next_page_token"] = next_page_token
            _write_checkpoint(out_dir, checkpoint)

            if not next_page_token:
                break

        # Playlist enumeration complete. Move to videos stage.
        checkpoint["stage"] = "videos"
        checkpoint["videos"]["video_parts"] = video_parts
        checkpoint["videos"]["next_index"] = 0
        _write_checkpoint(out_dir, checkpoint)
        stage = "videos"

    if stage == "videos":
        if not uploads_pid or not resolved_channel_id:
            resolved_channel_id = str(checkpoint.get("resolved_channel_id") or "").strip() or None
            uploads_pid = str(checkpoint.get("uploads_playlist_id") or "").strip() or None
        if not resolved_channel_id:
            raise RuntimeError("Checkpoint missing resolved_channel_id")

        # Ensure URLs file is always deterministic and complete for collected IDs so far.
        _write_lines(paths["video_urls"], [_watch_url(v) for v in ordered_ids])

        next_index = int(((checkpoint.get("videos") or {}).get("next_index") or 0))
        checkpoint_video_parts = str(((checkpoint.get("videos") or {}).get("video_parts") or "")).strip()
        if checkpoint_video_parts and checkpoint_video_parts != video_parts:
            raise SafetyError("Refused: --video-parts differs from checkpoint (start a new export or keep the same value)")
        checkpoint["videos"]["video_parts"] = video_parts

        videos_emitted = 0
        if paths["videos_jsonl"].exists():
            videos_emitted = len(_read_lines(paths["videos_jsonl"]))

        mode = "a" if (resume and paths["videos_jsonl"].exists()) else "w"
        paths["videos_jsonl"].parent.mkdir(parents=True, exist_ok=True)
        with open(paths["videos_jsonl"], mode, encoding="utf-8") as f:  # noqa: PTH123
            i = next_index
            while i < len(ordered_ids):
                chunk = ordered_ids[i : i + 50]
                resp = _api_get_json(
                    ctx=ctx,
                    method="videos.list",
                    params={"part": video_parts, "id": ",".join(chunk)},
                )
                data = resp.get("json")
                items = data.get("items") if isinstance(data, dict) else None
                if not isinstance(items, list):
                    items = []
                by_id: dict[str, dict[str, Any]] = {}
                for it in items:
                    if isinstance(it, dict) and isinstance(it.get("id"), str):
                        by_id[str(it.get("id"))] = it

                for vid in chunk:
                    obj = by_id.get(vid)
                    f.write(_videos_jsonl_line(video_id=vid, video_obj=obj, missing=obj is None))
                    videos_emitted += 1

                i += len(chunk)
                checkpoint["videos"]["next_index"] = i
                _write_checkpoint(out_dir, checkpoint)

    finished_at_utc = _utc_now()
    checkpoint["stage"] = "done"
    checkpoint["completed_at_utc"] = finished_at_utc
    _write_checkpoint(out_dir, checkpoint)

    # Ensure urls/manifest are up-to-date and deterministic on completion.
    _write_lines(paths["video_urls"], [_watch_url(v) for v in ordered_ids])
    videos_emitted_final = len(_read_lines(paths["videos_jsonl"]))
    _write_manifest(
        out_dir=out_dir,
        paths=paths,
        started_at_utc=started_at_utc,
        finished_at_utc=finished_at_utc,
        completed=True,
        channel_input=channel_input,
        resolved_channel_id=resolved_channel_id,
        uploads_playlist_id=uploads_pid,
        pages_fetched=pages_fetched,
        video_ids_count=len(ordered_ids),
        videos_emitted_count=videos_emitted_final,
        video_parts=video_parts,
        errors=errors,
    )

    ctx["audit"].write(
        "channels.export.live",
        {"input": channel_input.to_dict(), "out_dir": str(out_dir), "video_ids": len(ordered_ids), "pages_fetched": pages_fetched},
    )
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "live": True,
            "completed": True,
            "out_dir": str(out_dir),
            "resolved_channel_id": resolved_channel_id,
            "channel_url": _channel_url(resolved_channel_id) if resolved_channel_id else None,
            "counts": {
                "pages_fetched": pages_fetched,
                "video_ids": len(ordered_ids),
                "videos_jsonl_rows": videos_emitted_final,
            },
            "files": {k: str(v) for k, v in paths.items()},
            "plan_out": plan_path,
        }
    )
    return 0

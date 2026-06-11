from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


def tool_root_dir() -> Path:
    # .../this skill folder/src/youtube_api_tool/youtube_discovery.py
    return Path(__file__).resolve().parents[2]


def official_discovery_doc_path() -> Path:
    return tool_root_dir() / "docs" / "official_discovery_youtube_v3_rest.json"


def load_official_discovery_doc() -> dict[str, Any]:
    p = official_discovery_doc_path()
    if not p.exists():
        raise RuntimeError(f"Missing discovery snapshot: {p}")
    obj = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError("Discovery snapshot must be a JSON object")
    return obj


def _walk_method_ids(*, discovery_obj: dict[str, Any]) -> Iterable[str]:
    """
    Yield method ids like `search.list`, `videos.insert`, etc.

    Source of truth: the discovery document's `resources`/`methods` graph.
    """
    resources = discovery_obj.get("resources")
    if isinstance(resources, dict):
        yield from _walk_resources(resource_prefix="", resources_obj=resources)

    # Some discovery docs may include top-level methods.
    top_methods = discovery_obj.get("methods")
    if isinstance(top_methods, dict):
        for mname in top_methods.keys():
            if isinstance(mname, str) and mname:
                yield mname


def _walk_resources(*, resource_prefix: str, resources_obj: dict[str, Any]) -> Iterable[str]:
    for rname, robj in resources_obj.items():
        if not isinstance(rname, str) or not rname:
            continue
        if not isinstance(robj, dict):
            continue
        prefix = f"{resource_prefix}.{rname}" if resource_prefix else rname
        methods = robj.get("methods")
        if isinstance(methods, dict):
            for mname in methods.keys():
                if isinstance(mname, str) and mname:
                    yield f"{prefix}.{mname}"
        subresources = robj.get("resources")
        if isinstance(subresources, dict):
            yield from _walk_resources(resource_prefix=prefix, resources_obj=subresources)


def extract_official_method_names(*, discovery_obj: dict[str, Any]) -> list[str]:
    methods = sorted(set(_walk_method_ids(discovery_obj=discovery_obj)))
    return methods


@dataclass(frozen=True)
class DiscoveryMethod:
    name: str
    http_method: str | None
    path: str | None
    has_media_upload: bool


def extract_method_metadata(*, discovery_obj: dict[str, Any]) -> dict[str, DiscoveryMethod]:
    """
    Minimal metadata used by the CLI surface to classify methods.

    This intentionally keeps a narrow surface so it remains easy to unit test.
    """
    out: dict[str, DiscoveryMethod] = {}
    resources = discovery_obj.get("resources")
    if isinstance(resources, dict):
        _walk_resources_for_metadata(resource_prefix="", resources_obj=resources, out=out)

    top_methods = discovery_obj.get("methods")
    if isinstance(top_methods, dict):
        for mname, mobj in top_methods.items():
            if not isinstance(mname, str) or not mname:
                continue
            if not isinstance(mobj, dict):
                continue
            out[mname] = DiscoveryMethod(
                name=mname,
                http_method=str(mobj.get("httpMethod") or "") or None,
                path=str(mobj.get("path") or "") or None,
                has_media_upload=bool(mobj.get("mediaUpload")),
            )
    return out


def _walk_resources_for_metadata(*, resource_prefix: str, resources_obj: dict[str, Any], out: dict[str, DiscoveryMethod]) -> None:
    for rname, robj in resources_obj.items():
        if not isinstance(rname, str) or not rname:
            continue
        if not isinstance(robj, dict):
            continue
        prefix = f"{resource_prefix}.{rname}" if resource_prefix else rname

        methods = robj.get("methods")
        if isinstance(methods, dict):
            for mname, mobj in methods.items():
                if not isinstance(mname, str) or not mname:
                    continue
                if not isinstance(mobj, dict):
                    continue
                full = f"{prefix}.{mname}"
                out[full] = DiscoveryMethod(
                    name=full,
                    http_method=str(mobj.get("httpMethod") or "") or None,
                    path=str(mobj.get("path") or "") or None,
                    has_media_upload=bool(mobj.get("mediaUpload")),
                )

        subresources = robj.get("resources")
        if isinstance(subresources, dict):
            _walk_resources_for_metadata(resource_prefix=prefix, resources_obj=subresources, out=out)


@dataclass(frozen=True)
class DiscoveryParam:
    name: str
    location: str | None
    required: bool


@dataclass(frozen=True)
class MethodInfo:
    name: str
    http_method: str
    path: str
    params: tuple[DiscoveryParam, ...]
    scopes: tuple[str, ...]
    media_simple_path: str | None
    media_resumable_path: str | None
    media_multipart: bool
    supports_media_download: bool
    use_media_download_service: bool

    @property
    def has_media_upload(self) -> bool:
        return bool(self.media_simple_path or self.media_resumable_path)


def find_method_obj(*, discovery_obj: dict[str, Any], method_name: str) -> dict[str, Any]:
    """
    Find the raw discovery method object for a full method id like `search.list`.
    """
    m = str(method_name or "").strip()
    if not m:
        raise KeyError("method_name must not be empty")
    parts = [p for p in m.split(".") if p]
    if not parts:
        raise KeyError("method_name must not be empty")

    # Top-level methods (rare).
    if len(parts) == 1:
        top = discovery_obj.get("methods")
        if isinstance(top, dict) and isinstance(top.get(parts[0]), dict):
            return top[parts[0]]  # type: ignore[return-value]
        raise KeyError(f"Method not found: {m}")

    cur: dict[str, Any] = discovery_obj
    for r in parts[:-1]:
        resources = cur.get("resources")
        if not isinstance(resources, dict):
            raise KeyError(f"Method not found: {m}")
        nxt = resources.get(r)
        if not isinstance(nxt, dict):
            raise KeyError(f"Method not found: {m}")
        cur = nxt

    methods = cur.get("methods")
    if not isinstance(methods, dict):
        raise KeyError(f"Method not found: {m}")
    mobj = methods.get(parts[-1])
    if not isinstance(mobj, dict):
        raise KeyError(f"Method not found: {m}")
    return mobj


def get_method_info(*, discovery_obj: dict[str, Any], method_name: str) -> MethodInfo:
    mobj = find_method_obj(discovery_obj=discovery_obj, method_name=method_name)
    http_method = str(mobj.get("httpMethod") or "").strip()
    path = str(mobj.get("path") or "").strip()
    if not http_method:
        raise RuntimeError(f"Discovery method missing httpMethod: {method_name}")
    if not path:
        raise RuntimeError(f"Discovery method missing path: {method_name}")

    params: list[DiscoveryParam] = []
    pobj = mobj.get("parameters")
    if isinstance(pobj, dict):
        for pname, p in pobj.items():
            if not isinstance(pname, str) or not pname:
                continue
            if not isinstance(p, dict):
                continue
            params.append(
                DiscoveryParam(
                    name=pname,
                    location=str(p.get("location") or "") or None,
                    required=bool(p.get("required")),
                )
            )
    params = sorted(params, key=lambda x: x.name)

    scopes: tuple[str, ...] = tuple(
        s for s in (mobj.get("scopes") or []) if isinstance(s, str) and s.strip()
    )

    media_simple_path = None
    media_resumable_path = None
    media_multipart = False
    media = mobj.get("mediaUpload")
    if isinstance(media, dict):
        protocols = media.get("protocols")
        if isinstance(protocols, dict):
            simple = protocols.get("simple")
            if isinstance(simple, dict):
                media_simple_path = str(simple.get("path") or "").strip() or None
                media_multipart = media_multipart or bool(simple.get("multipart"))
            resumable = protocols.get("resumable")
            if isinstance(resumable, dict):
                media_resumable_path = str(resumable.get("path") or "").strip() or None
                media_multipart = media_multipart or bool(resumable.get("multipart"))

    supports_media_download = bool(mobj.get("supportsMediaDownload"))
    use_media_download_service = bool(mobj.get("useMediaDownloadService"))

    return MethodInfo(
        name=str(method_name),
        http_method=http_method,
        path=path,
        params=tuple(params),
        scopes=scopes,
        media_simple_path=media_simple_path,
        media_resumable_path=media_resumable_path,
        media_multipart=media_multipart,
        supports_media_download=supports_media_download,
        use_media_download_service=use_media_download_service,
    )

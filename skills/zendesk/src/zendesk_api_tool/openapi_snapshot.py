from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .project_config import OPENAPI_SNAPSHOT_FILENAME


def tool_root_dir() -> Path:
    # .../this skill folder/src/zendesk_api_tool/openapi_snapshot.py
    # parents: [zendesk_api_tool, src, tool_root, ...]
    return Path(__file__).resolve().parents[2]


def pinned_openapi_snapshot_path() -> Path:
    return tool_root_dir() / OPENAPI_SNAPSHOT_FILENAME


class _IgnoreUnknownTagsLoader(yaml.SafeLoader):
    """YAML loader that tolerates unknown tags by treating tagged nodes as plain values."""


def _construct_unknown_tag(loader: _IgnoreUnknownTagsLoader, node: yaml.Node) -> Any:  # type: ignore[name-defined]
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


_IgnoreUnknownTagsLoader.add_constructor(None, _construct_unknown_tag)


@dataclass(frozen=True)
class OpenApiSnapshot:
    path: Path
    obj: dict[str, Any]

    @property
    def version(self) -> str | None:
        info = self.obj.get("info") or {}
        if isinstance(info, dict):
            v = info.get("version")
            return str(v).strip() if v is not None else None
        return None


def load_pinned_openapi_snapshot() -> OpenApiSnapshot:
    p = pinned_openapi_snapshot_path()
    if not p.exists():
        raise RuntimeError(f"Pinned OpenAPI snapshot not found: {p}")
    obj = yaml.load(p.read_text(encoding="utf-8"), Loader=_IgnoreUnknownTagsLoader)
    if not isinstance(obj, dict):
        raise RuntimeError("Pinned OpenAPI snapshot must be a YAML mapping/object")
    if str(obj.get("openapi") or "").strip() == "":
        raise RuntimeError("Pinned OpenAPI snapshot missing 'openapi' field")
    info = obj.get("info") or {}
    if not isinstance(info, dict):
        raise RuntimeError("Pinned OpenAPI snapshot missing 'info' object")
    if str(info.get("title") or "").strip() == "":
        raise RuntimeError("Pinned OpenAPI snapshot missing info.title")
    return OpenApiSnapshot(path=p, obj=obj)

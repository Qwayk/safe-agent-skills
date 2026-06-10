from __future__ import annotations

import csv
import json
from typing import Any


def _parse_int_id(v: Any) -> int:
    if isinstance(v, int):
        return v
    s = str(v).strip()
    if not s:
        raise ValueError("Empty id")
    return int(s)


def load_json_file(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_caption_map(path: str) -> dict[int, str]:
    """
    Supports:
      - JSON object: {"123": "caption", "456": "caption"}
      - JSON array: [{"id": 123, "caption": "caption"}, ...]
    """
    doc = load_json_file(path)
    out: dict[int, str] = {}
    if isinstance(doc, dict):
        for k, v in doc.items():
            if v is None:
                continue
            out[_parse_int_id(k)] = str(v)
        return out
    if isinstance(doc, list):
        for row in doc:
            if not isinstance(row, dict):
                raise ValueError("Caption map list must contain objects.")
            if "id" not in row:
                raise ValueError("Caption map item missing 'id'.")
            if "caption" not in row or row["caption"] is None:
                continue
            out[_parse_int_id(row["id"])] = str(row["caption"])
        return out
    raise ValueError("Caption map JSON must be an object or a list.")


def load_media_updates(path: str) -> list[dict[str, str | None]]:
    """
    Supports:
      - JSON array of update objects:
        [{"id": 123, "caption": "...", "alt_text": "...", "title": "..."}, ...]
      - JSON object mapping id->caption for caption-only updates.
    """
    doc = load_json_file(path)
    out: list[dict[str, str | None]] = []
    if isinstance(doc, dict):
        for k, v in doc.items():
            if v is None:
                continue
            out.append(
                {"id": str(_parse_int_id(k)), "caption": str(v), "alt_text": None, "title": None}
            )
        return out
    if isinstance(doc, list):
        for row in doc:
            if not isinstance(row, dict):
                raise ValueError("Media updates list must contain objects.")
            if "id" not in row:
                raise ValueError("Media update item missing 'id'.")
            out.append(
                {
                    "id": str(_parse_int_id(row["id"])),
                    "caption": None if row.get("caption") is None else str(row.get("caption")),
                    "alt_text": None if row.get("alt_text") is None else str(row.get("alt_text")),
                    "title": None if row.get("title") is None else str(row.get("title")),
                }
            )
        return out
    raise ValueError("Media updates JSON must be an object or a list.")


def load_media_download_items(path: str) -> list[dict[str, str | None]]:
    """
    Supports:
      - CSV file with headers: id,url,filename (unknown columns ignored)
      - JSON array of objects:
        [{"id": 123, "url": "...", "filename": "..."}, ...]
    Each item must include at least one of id or url. Filename is optional.
    """
    if path.lower().endswith(".json"):
        doc = load_json_file(path)
        if not isinstance(doc, list):
            raise ValueError("Media download JSON must be a list.")
        out: list[dict[str, str | None]] = []
        for row in doc:
            if not isinstance(row, dict):
                raise ValueError("Media download JSON list must contain objects.")
            out.append(
                {
                    "id": None if row.get("id") is None else str(row.get("id")),
                    "url": None if row.get("url") is None else str(row.get("url")),
                    "filename": None if row.get("filename") is None else str(row.get("filename")),
                }
            )
        return out

    if path.lower().endswith(".csv"):
        out: list[dict[str, str | None]] = []
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row:
                    continue
                raw_id = (row.get("id") or "").strip()
                raw_url = (row.get("url") or "").strip()
                raw_filename = (row.get("filename") or "").strip()
                out.append(
                    {
                        "id": raw_id if raw_id else None,
                        "url": raw_url if raw_url else None,
                        "filename": raw_filename if raw_filename else None,
                    }
                )
        return out

    raise ValueError("Unsupported media download file type. Use .csv or .json")

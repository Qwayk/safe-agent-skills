from __future__ import annotations

from dataclasses import dataclass
from typing import Final

STOCK_SUFFIX: Final[str] = "(stock image; for illustration only)."
INFOGRAPHIC_SUFFIX: Final[str] = "(original infographic by the publisher)."


@dataclass(frozen=True)
class CaptionPolicyExpectation:
    kind: str  # "infographic" | "stock"
    expected_suffix: str


def _haystack(src: str, alt: str | None, title: str | None, caption_text: str | None) -> str:
    parts = [src, alt or "", title or "", caption_text or ""]
    return " ".join(p for p in parts if p).casefold()


def guess_caption_policy(src: str, *, alt: str | None, title: str | None, caption_text: str | None) -> CaptionPolicyExpectation:
    """
    Best-effort heuristic:
    - If "infographic" appears in filename/alt/title/caption: treat as infographic (original).
    - Otherwise treat as stock.
    """
    h = _haystack(src, alt, title, caption_text)
    if "infographic" in h:
        return CaptionPolicyExpectation(kind="infographic", expected_suffix=INFOGRAPHIC_SUFFIX)
    return CaptionPolicyExpectation(kind="stock", expected_suffix=STOCK_SUFFIX)


def caption_matches_expected(caption_text: str | None, *, expected_suffix: str) -> bool:
    if not isinstance(caption_text, str) or not caption_text.strip():
        return False
    return caption_text.strip().endswith(expected_suffix)

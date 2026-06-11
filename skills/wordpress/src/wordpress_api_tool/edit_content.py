from __future__ import annotations

import dataclasses
import difflib
import json
import re
from html import escape as html_escape

_IMG_TAG_RE = re.compile(r"<img\b[^>]*>", flags=re.I)
_ALT_ATTR_RE = re.compile(r"\balt\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)", flags=re.I)
_WP_IMAGE_ID_IN_HTML_RE = re.compile(r"\bwp-image-(\d+)\b", flags=re.I)


@dataclasses.dataclass(frozen=True)
class ContentEditReport:
    matched_blocks: int
    updated_blocks: int
    refused_blocks: int
    reasons: list[str]
    diff: str | None


def update_gutenberg_image_captions(
    content_raw: str,
    *,
    caption_text: str | None,
    caption_html: str | None,
    alt_text: str | None,
    caption_text_by_id: dict[int, str] | None = None,
    caption_html_by_id: dict[int, str] | None = None,
    alt_text_by_id: dict[int, str] | None = None,
    only_ids: set[int] | None,
    include_diff: bool,
) -> tuple[ContentEditReport, str]:
    """
    Strict policy:
    - Only edits Gutenberg `wp:image` blocks with JSON attrs containing integer `id`.
    - If the structure isn't clear, it refuses and explains why.
    """
    if caption_text is not None and caption_html is not None:
        raise ValueError("Provide only one of caption_text or caption_html.")
    if caption_text_by_id is not None and caption_html_by_id is not None:
        raise ValueError("Provide only one of caption_text_by_id or caption_html_by_id.")
    if caption_text is not None and caption_text_by_id is not None:
        raise ValueError("Provide only one of caption_text or caption_text_by_id.")
    if caption_html is not None and caption_html_by_id is not None:
        raise ValueError("Provide only one of caption_html or caption_html_by_id.")
    if alt_text is not None and alt_text_by_id is not None:
        raise ValueError("Provide only one of alt_text or alt_text_by_id.")

    reasons: list[str] = []
    matched = 0
    updated = 0
    refused = 0

    out_parts: list[str] = []
    idx = 0
    while True:
        start = content_raw.find("<!-- wp:image", idx)
        if start == -1:
            out_parts.append(content_raw[idx:])
            break
        out_parts.append(content_raw[idx:start])

        header_end = content_raw.find("-->", start)
        if header_end == -1:
            out_parts.append(content_raw[start:])
            break
        header_full = content_raw[start: header_end + 3]
        header_payload = content_raw[start + len("<!-- wp:image") : header_end].strip()

        block_close = content_raw.find("<!-- /wp:image -->", header_end + 3)
        if block_close == -1:
            out_parts.append(content_raw[start:])
            break
        body = content_raw[header_end + 3 : block_close]
        footer = "<!-- /wp:image -->"

        idx = block_close + len(footer)
        matched += 1

        # Parse attrs JSON (strict).
        if not header_payload.startswith("{"):
            refused += 1
            reasons.append("Refused: wp:image block has no JSON attrs")
            out_parts.append(header_full + body + footer)
            continue
        try:
            attrs = json.loads(header_payload)
        except Exception:
            refused += 1
            reasons.append("Refused: wp:image attrs JSON could not be parsed")
            out_parts.append(header_full + body + footer)
            continue

        block_id = attrs.get("id")
        if not isinstance(block_id, int):
            m = _WP_IMAGE_ID_IN_HTML_RE.search(body)
            if m:
                try:
                    block_id = int(m.group(1))
                except Exception:
                    block_id = None
            if not isinstance(block_id, int):
                # If we're in per-id mapping mode, skipping blocks we can't identify is safer than
                # refusing the entire operation (common for external/affiliate images).
                if caption_text_by_id is not None or caption_html_by_id is not None or alt_text_by_id is not None:
                    out_parts.append(header_full + body + footer)
                    continue
                refused += 1
                reasons.append("Refused: wp:image block missing integer id")
                out_parts.append(header_full + body + footer)
                continue
        if only_ids is not None and block_id not in only_ids:
            out_parts.append(header_full + body + footer)
            continue

        new_body = body

        cap_text_for_id = caption_text_by_id.get(block_id) if caption_text_by_id is not None else None
        cap_html_for_id = caption_html_by_id.get(block_id) if caption_html_by_id is not None else None
        alt_for_id = alt_text_by_id.get(block_id) if alt_text_by_id is not None else None

        # Caption edit (figcaption inside body).
        if (
            caption_text is not None
            or caption_html is not None
            or cap_text_for_id is not None
            or cap_html_for_id is not None
        ):
            if cap_text_for_id is not None and cap_html_for_id is not None:
                refused += 1
                reasons.append(f"Refused: wp:image id={block_id} has both caption text and html mappings")
                out_parts.append(header_full + body + footer)
                continue

            cap = None
            if cap_html_for_id is not None:
                cap = cap_html_for_id
            elif cap_text_for_id is not None:
                cap = html_escape(cap_text_for_id, quote=False)
            elif caption_html is not None:
                cap = caption_html
            elif caption_text is not None:
                cap = html_escape(caption_text, quote=False)

            if cap is not None:
                lower = new_body.lower()
                if "<figure" not in lower:
                    refused += 1
                    reasons.append(f"Refused: wp:image id={block_id} has no <figure>")
                elif "<figcaption" in lower:
                    new_body = _replace_first_figcaption(new_body, cap)
                else:
                    new_body = _insert_figcaption_before_figure_close(new_body, cap)

        # Alt edit (img alt attr).
        alt_to_set = alt_for_id if alt_for_id is not None else alt_text
        if alt_to_set is not None:
            if "<img" not in new_body.lower():
                refused += 1
                reasons.append(f"Refused: wp:image id={block_id} has no <img>")
            else:
                new_body = _set_first_img_alt(new_body, alt_to_set)

        if new_body != body:
            updated += 1
        out_parts.append(header_full + new_body + footer)

    new_content = "".join(out_parts)
    diff = None
    if include_diff and new_content != content_raw:
        diff = "\n".join(
            difflib.unified_diff(
                content_raw.splitlines(),
                new_content.splitlines(),
                fromfile="before",
                tofile="after",
                lineterm="",
            )
        )

    return (
        ContentEditReport(
            matched_blocks=matched,
            updated_blocks=updated,
            refused_blocks=refused,
            reasons=reasons,
            diff=diff,
        ),
        new_content,
    )


def _replace_first_figcaption(body: str, caption_html: str) -> str:
    lower = body.lower()
    start = lower.find("<figcaption")
    if start == -1:
        return body
    open_end = body.find(">", start)
    if open_end == -1:
        return body
    close = lower.find("</figcaption>", open_end)
    if close == -1:
        return body
    return body[: open_end + 1] + caption_html + body[close:]


def _insert_figcaption_before_figure_close(body: str, caption_html: str) -> str:
    lower = body.lower()
    close = lower.rfind("</figure>")
    if close == -1:
        return body
    insert = f'<figcaption class="wp-element-caption">{caption_html}</figcaption>'
    return body[:close] + insert + body[close:]


def _set_first_img_alt(body: str, alt_text: str) -> str:
    m = _IMG_TAG_RE.search(body)
    if not m:
        return body
    tag = m.group(0)
    alt_escaped = html_escape(alt_text, quote=True)

    if _ALT_ATTR_RE.search(tag):
        new_tag = _ALT_ATTR_RE.sub(f'alt="{alt_escaped}"', tag, count=1)
    else:
        stripped = tag.rstrip()
        if stripped.endswith("/>"):
            base = stripped[:-2].rstrip()
            new_tag = f'{base} alt="{alt_escaped}" />'
        else:
            base = stripped[:-1].rstrip()
            new_tag = f'{base} alt="{alt_escaped}">'

    return body[: m.start()] + new_tag + body[m.end() :]

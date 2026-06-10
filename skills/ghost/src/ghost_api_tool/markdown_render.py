from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RenderedMarkdown:
    html: str
    dropped_h1: str | None


def _strip_leading_h1(md_text: str) -> tuple[str, str | None]:
    lines = md_text.splitlines()
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1

    if i < len(lines) and lines[i].startswith("# "):
        title = lines[i][2:].strip() or None
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        return "\n".join(lines[i:]).lstrip("\n"), title

    return md_text, None


def render_markdown(md_text: str, *, strip_h1: bool = True) -> RenderedMarkdown:
    body, dropped = _strip_leading_h1(md_text) if strip_h1 else (md_text, None)
    try:
        import markdown  # type: ignore[import-untyped]
    except ModuleNotFoundError as e:
        raise RuntimeError(
            "Missing dependency: 'markdown'. Install with: pip install markdown"
        ) from e
    html = markdown.markdown(
        body,
        extensions=[
            "extra",
            "tables",
            "sane_lists",
        ],
        output_format="html5",
    )
    return RenderedMarkdown(html=html, dropped_h1=dropped)

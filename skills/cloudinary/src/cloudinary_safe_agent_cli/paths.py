from __future__ import annotations

from pathlib import Path

from .errors import SafetyError, ValidationError


def resolve_safe_out_path(*, project_dir: Path, out_path: str, overwrite: bool) -> Path:
    raw = str(out_path or "").strip()
    if not raw:
        raise ValidationError("Missing --out")
    root = project_dir.resolve()
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = root / candidate
    target = candidate.resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise SafetyError("Refusing to write outside --project-dir.") from exc
    if target.exists() and not overwrite:
        raise SafetyError(f"Refusing to overwrite existing file: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    return target

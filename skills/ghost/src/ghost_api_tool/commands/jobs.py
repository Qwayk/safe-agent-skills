from __future__ import annotations

import csv
from typing import Any

from ..commands import bodylex as bodylex_cmd
from ..commands import bodymob as bodymob_cmd
from ..commands import post as post_cmd
from ..errors import ValidationError


def cmd_jobs_run(args, ctx) -> int:
    if ctx["apply"] and not ctx["yes"]:
        ctx["out"].print(
            {
                "ok": True,
                "apply": True,
                "refused": True,
                "reasons": ["Refused: batch jobs require --yes when using --apply"],
            }
        )
        return 0

    path = args.file
    if not path.endswith(".csv"):
        raise ValidationError("Only .csv job files are supported for now")

    results: list[dict[str, Any]] = []
    processed = 0
    errors = 0
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=1):
            if not row:
                continue
            if args.limit is not None and processed >= args.limit:
                break
            processed += 1

            action = (row.get("action") or "").strip()
            slug = (row.get("slug") or "").strip() or None
            post_id = (row.get("id") or "").strip() or None

            try:
                cap = _CaptureOutput()
                row_ctx = dict(ctx)
                row_ctx["out"] = cap

                if action == "post.patch":
                    file_path = (row.get("file") or "").strip()
                    if not file_path:
                        raise RuntimeError("jobs: post.patch requires file column")
                    post_cmd.cmd_post_patch(
                        _FakeArgs(
                            slug=slug,
                            id=post_id,
                            file=file_path,
                            require_current=(row.get("require_current") or "").strip() or None,
                            source=(row.get("source") or "").strip() or None,
                        ),
                        row_ctx,
                    )
                elif action == "post.set-status":
                    to = (row.get("to") or "").strip()
                    if not to:
                        raise RuntimeError("jobs: post.set-status requires to column")
                    post_cmd.cmd_post_set_status(
                        _FakeArgs(
                            slug=slug,
                            id=post_id,
                            to=to,
                            require_current=(row.get("require_current") or "").strip() or None,
                            published_at=(row.get("published_at") or "").strip() or None,
                            newsletter=(row.get("newsletter") or "").strip() or None,
                            email_segment=(row.get("email_segment") or "").strip() or None,
                            email_only=_parse_bool(row.get("email_only")),
                        ),
                        row_ctx,
                    )
                elif action == "post.body.set-captions":
                    captions_file = (row.get("captions_file") or "").strip()
                    if not captions_file:
                        raise RuntimeError("jobs: post.body.set-captions requires captions_file column")
                    diff = _parse_bool(row.get("diff"))
                    post_cmd.cmd_post_body_set_captions(
                        _FakeArgs(slug=slug, id=post_id, captions_file=captions_file, diff=diff),
                        row_ctx,
                    )
                elif action == "post.bodylex.image.replace-many":
                    map_path = (row.get("map") or "").strip()
                    if not map_path:
                        raise RuntimeError("jobs: post.bodylex.image.replace-many requires map column")
                    diff = _parse_bool(row.get("diff"))
                    bodylex_cmd.cmd_bodylex_image_replace_many(
                        _FakeArgs(
                            slug=slug,
                            id=post_id,
                            map=map_path,
                            diff=diff,
                            require_current=(row.get("require_current") or "").strip() or None,
                            allow_published=_parse_bool(row.get("allow_published")),
                        ),
                        row_ctx,
                    )
                elif action == "post.bodymob.image.replace-many":
                    map_path = (row.get("map") or "").strip()
                    if not map_path:
                        raise RuntimeError("jobs: post.bodymob.image.replace-many requires map column")
                    diff = _parse_bool(row.get("diff"))
                    bodymob_cmd.cmd_bodymob_image_replace_many(
                        _FakeArgs(
                            slug=slug,
                            id=post_id,
                            map=map_path,
                            diff=diff,
                            require_current=(row.get("require_current") or "").strip() or None,
                            allow_published=_parse_bool(row.get("allow_published")),
                        ),
                        row_ctx,
                    )
                else:
                    raise RuntimeError(f"Unknown jobs action: {action or '<empty>'}")

                out_obj = cap.one()
                results.append({"row": row_num, "action": action, "input": row, "result": out_obj})
            except Exception as e:
                errors += 1
                results.append({"row": row_num, "action": action, "input": row, "error": str(e)})
                break

    out = {
        "ok": errors == 0,
        "apply": bool(ctx["apply"]),
        "count": processed,
        "errors": errors,
        "results": results,
    }
    ctx["audit"].write("jobs.run", out)
    ctx["out"].print(out)
    return 1 if errors else 0


def _parse_bool(val: str | None) -> bool:
    if val is None:
        return False
    s = str(val).strip().lower()
    return s in ("1", "true", "yes", "y", "on")


class _FakeArgs:
    def __init__(self, **kwargs: Any):
        for k, v in kwargs.items():
            setattr(self, k, v)


class _CaptureOutput:
    def __init__(self) -> None:
        self.items: list[Any] = []

    def print(self, obj: Any) -> None:
        self.items.append(obj)

    def one(self) -> Any:
        if len(self.items) != 1:
            raise RuntimeError(f"Internal error: expected exactly 1 output object, got {len(self.items)}")
        return self.items[0]

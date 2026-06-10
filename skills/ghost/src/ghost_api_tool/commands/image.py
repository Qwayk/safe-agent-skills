from __future__ import annotations

import time

from ..runtime import get_api


def add_image_commands(image_sub) -> None:
    image_upload = image_sub.add_parser("upload", help="Upload an image to Ghost storage")
    image_upload.add_argument("--file", required=True, help="Local file path")
    image_upload.add_argument(
        "--upload-name",
        default=None,
        help="Optional filename to use in Ghost storage (affects URL path)",
    )
    image_upload.add_argument(
        "--purpose",
        default="image",
        choices=("image", "profile_image", "icon"),
        help="Upload purpose (default: image)",
    )
    image_upload.add_argument("--ref", default=None, help="Optional ref value")
    image_upload.set_defaults(func=cmd_image_upload)


def cmd_image_upload(args, ctx) -> int:
    api = get_api(ctx)

    if not ctx["apply"]:
        ctx["out"].print(
            {
                "apply": False,
                "would_upload": {
                    "file": args.file,
                    "upload_name": args.upload_name,
                    "purpose": args.purpose,
                    "ref": args.ref,
                },
            }
        )
        return 0

    backup = ctx.get("backup")
    correlation_id = None
    if backup is not None:
        correlation_id = f"{int(time.time() * 1000)}-image.upload"
        backup.write_before_after(
            kind="image",
            resource_id="upload",
            slug=str(args.upload_name or args.file),
            action="image.upload",
            before=None,
            after=None,
            meta={
                "stage": "before",
                "correlation_id": correlation_id,
                "upload": {
                    "file": args.file,
                    "upload_name": args.upload_name,
                    "purpose": args.purpose,
                    "ref": args.ref,
                },
            },
        )

    try:
        res = api.upload_image(
            file_path=args.file,
            purpose=args.purpose,
            ref=args.ref,
            upload_name=args.upload_name,
        )
    except Exception as e:
        if backup is not None:
            backup.write_before_after(
                kind="image",
                resource_id="upload",
                slug=str(args.upload_name or args.file),
                action="image.upload",
                before=None,
                after=None,
                meta={"stage": "error", "correlation_id": correlation_id, "error": str(e)},
            )
        raise

    if backup is not None:
        backup.write_before_after(
            kind="image",
            resource_id="upload",
            slug=str(args.upload_name or args.file),
            action="image.upload",
            before=None,
            after=res,
            meta={"stage": "after", "correlation_id": correlation_id},
        )
    ctx["out"].print({"apply": True, "result": res})
    return 0

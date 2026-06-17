from __future__ import annotations

from typing import Any

from .wrapped_file_connections import (
    WrappedFileConnectionSpec,
    cmd_create as _cmd_create,
    cmd_get as _cmd_get,
    cmd_list as _cmd_list,
    cmd_remove as _cmd_remove,
)

SPEC = WrappedFileConnectionSpec(
    family_slug="voucher-file-connections",
    item_slug="voucher-file-connection",
    collection_key="VoucherFileConnections",
    item_key="VoucherFileConnection",
    payload_key="VoucherFileConnection",
    path="/voucherfileconnections",
    list_query_params=(
        ("voucher_year", "voucheryear"),
        ("voucher_description", "voucherdescription"),
        ("voucher_number", "vouchernumber"),
        ("voucher_series", "voucherseries"),
    ),
    payload_required_keys=("FileId", "VoucherNumber", "VoucherSeries"),
    singular_label="voucher file connection",
    plural_label="voucher file connections",
)


def cmd_voucher_file_connections_list(args: Any, ctx: dict[str, Any]) -> int:
    return _cmd_list(args, ctx, spec=SPEC)


def cmd_voucher_file_connections_get(args: Any, ctx: dict[str, Any]) -> int:
    return _cmd_get(args, ctx, spec=SPEC)


def cmd_voucher_file_connections_create(args: Any, ctx: dict[str, Any]) -> int:
    return _cmd_create(args, ctx, spec=SPEC)


def cmd_voucher_file_connections_remove(args: Any, ctx: dict[str, Any]) -> int:
    return _cmd_remove(args, ctx, spec=SPEC)

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
    family_slug="supplier-invoice-file-connections",
    item_slug="supplier-invoice-file-connection",
    collection_key="SupplierInvoiceFileConnections",
    item_key="SupplierInvoiceFileConnection",
    payload_key="SupplierInvoiceFileConnection",
    path="/supplierinvoicefileconnections",
    list_query_params=(("supplier_invoice_number", "supplierinvoicenumber"),),
    payload_required_keys=("FileId",),
    singular_label="supplier invoice file connection",
    plural_label="supplier invoice file connections",
)


def cmd_supplier_invoice_file_connections_list(args: Any, ctx: dict[str, Any]) -> int:
    return _cmd_list(args, ctx, spec=SPEC)


def cmd_supplier_invoice_file_connections_get(args: Any, ctx: dict[str, Any]) -> int:
    return _cmd_get(args, ctx, spec=SPEC)


def cmd_supplier_invoice_file_connections_create(args: Any, ctx: dict[str, Any]) -> int:
    return _cmd_create(args, ctx, spec=SPEC)


def cmd_supplier_invoice_file_connections_remove(args: Any, ctx: dict[str, Any]) -> int:
    return _cmd_remove(args, ctx, spec=SPEC)

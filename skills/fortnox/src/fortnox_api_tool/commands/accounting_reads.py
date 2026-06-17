from __future__ import annotations

import base64
import hashlib
from pathlib import Path
from typing import Any

from ..api_runtime import get_json, request_data, request_json, request_raw


def _emit_read(ctx: dict[str, Any], *, audit_key: str, path: str, payload: dict[str, Any]) -> int:
    out = {
        "ok": True,
        "path": path,
        "http_status": payload["status"],
        "token_source": payload["token_source"],
        "token_expired": payload["token_expired"],
        "data": payload["body"],
    }
    ctx["audit"].write(
        audit_key,
        {
            "ok": True,
            "path": path,
            "http_status": payload["status"],
            "token_source": payload["token_source"],
            "token_expired": payload["token_expired"],
        },
    )
    ctx["out"].emit(out)
    return 0


def _emit_request_read(
    ctx: dict[str, Any],
    *,
    audit_key: str,
    path: str,
    query_params: dict[str, Any] | None = None,
) -> int:
    payload = request_json(
        ctx=ctx,
        method="GET",
        path=path,
        query_params=query_params,
        expect_json=True,
    )
    return _emit_read(ctx, audit_key=audit_key, path=path, payload=payload)


def _emit_binary_request_read(
    ctx: dict[str, Any],
    *,
    audit_key: str,
    path: str,
    output_file: str | None = None,
) -> int:
    payload = request_raw(
        ctx=ctx,
        method="GET",
        path=path,
        accept="application/pdf, application/octet-stream;q=0.9, application/json;q=0.3",
    )
    body = payload["body_bytes"]
    sha256 = hashlib.sha256(body).hexdigest()
    out = {
        "ok": True,
        "path": path,
        "http_status": payload["status"],
        "token_source": payload["token_source"],
        "token_expired": payload["token_expired"],
        "content_type": payload["content_type"],
        "byte_count": len(body),
        "sha256": sha256,
    }
    audit = {
        "ok": True,
        "path": path,
        "http_status": payload["status"],
        "token_source": payload["token_source"],
        "token_expired": payload["token_expired"],
        "content_type": payload["content_type"],
        "byte_count": len(body),
        "sha256": sha256,
    }
    output_path = str(output_file or "").strip()
    if output_path:
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        out["output_file"] = str(target)
        audit["output_file"] = str(target)
    else:
        out["data_base64"] = base64.b64encode(body).decode("ascii")
        out["data_encoding"] = "base64"
        audit["data_encoding"] = "base64"
    ctx["audit"].write(audit_key, audit)
    ctx["out"].emit(out)
    return 0


def _string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    items = [str(value).strip() for value in values if str(value).strip()]
    return items


def _set_query_param(query_params: dict[str, Any], query_name: str, value: Any) -> None:
    text = str(value or "").strip()
    if text:
        query_params[query_name] = text


def cmd_company_information_get(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/companyinformation"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="company_information.get", path=path, payload=payload)


def cmd_company_settings_get(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/settings/company"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="company_settings.get", path=path, payload=payload)


def cmd_archive_get_root(args: Any, ctx: dict[str, Any]) -> int:
    query_params: dict[str, Any] = {}
    folder_path = str(getattr(args, "path", "") or "").strip()
    file_id = str(getattr(args, "file_id", "") or "").strip()
    if folder_path:
        query_params["path"] = folder_path
    if file_id:
        query_params["fileid"] = file_id
    return _emit_request_read(
        ctx,
        audit_key="archive.get_root",
        path="/archive",
        query_params=query_params or None,
    )


def cmd_archive_get_file(args: Any, ctx: dict[str, Any]) -> int:
    archive_id = str(getattr(args, "id", "") or "").strip()
    return _emit_request_read(
        ctx,
        audit_key="archive.get_file",
        path=f"/archive/{archive_id}",
    )


def cmd_inbox_get_root(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    return _emit_request_read(ctx, audit_key="inbox.get_root", path="/inbox")


def cmd_inbox_get_file(args: Any, ctx: dict[str, Any]) -> int:
    inbox_id = str(getattr(args, "id", "") or "").strip()
    return _emit_request_read(
        ctx,
        audit_key="inbox.get_file",
        path=f"/inbox/{inbox_id}",
    )


def cmd_custom_document_types_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    return _emit_request_read(
        ctx,
        audit_key="custom_document_types.list",
        path="/api/warehouse/documentdeliveries/custom/documenttypes-v1",
    )


def cmd_custom_document_types_get(args: Any, ctx: dict[str, Any]) -> int:
    doc_type = str(getattr(args, "doc_type", "") or "").strip()
    return _emit_request_read(
        ctx,
        audit_key="custom_document_types.get",
        path=f"/api/warehouse/documentdeliveries/custom/documenttypes-v1/{doc_type}",
    )


def cmd_custom_inbound_documents_get(args: Any, ctx: dict[str, Any]) -> int:
    doc_type = str(getattr(args, "doc_type", "") or "").strip()
    document_id = str(getattr(args, "id", "") or "").strip()
    return _emit_request_read(
        ctx,
        audit_key="custom_inbound_documents.get",
        path=f"/api/warehouse/documentdeliveries/custom/inbound-v1/{doc_type}/{document_id}",
    )


def cmd_custom_outbound_documents_get(args: Any, ctx: dict[str, Any]) -> int:
    doc_type = str(getattr(args, "doc_type", "") or "").strip()
    document_id = str(getattr(args, "id", "") or "").strip()
    return _emit_request_read(
        ctx,
        audit_key="custom_outbound_documents.get",
        path=f"/api/warehouse/documentdeliveries/custom/outbound-v1/{doc_type}/{document_id}",
    )


def cmd_manual_documents_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    return _emit_request_read(
        ctx,
        audit_key="manual_documents.list",
        path="/api/warehouse/deliveries-v1",
    )


def cmd_manual_inbound_documents_get(args: Any, ctx: dict[str, Any]) -> int:
    document_id = str(getattr(args, "id", "") or "").strip()
    return _emit_request_read(
        ctx,
        audit_key="manual_inbound_documents.get",
        path=f"/api/warehouse/deliveries-v1/inbounddeliveries/{document_id}",
    )


def cmd_manual_outbound_documents_get(args: Any, ctx: dict[str, Any]) -> int:
    document_id = str(getattr(args, "id", "") or "").strip()
    return _emit_request_read(
        ctx,
        audit_key="manual_outbound_documents.get",
        path=f"/api/warehouse/deliveries-v1/outbounddeliveries/{document_id}",
    )


def cmd_email_senders_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    return _emit_request_read(
        ctx,
        audit_key="email_senders.list",
        path="/emailsenders",
    )


def cmd_locked_period_get(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/settings/lockedperiod"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="locked_period.get", path=path, payload=payload)


def cmd_print_templates_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/printtemplates"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="print_templates.list", path=path, payload=payload)


def cmd_customers_list(args: Any, ctx: dict[str, Any]) -> int:
    query_params: dict[str, Any] = {}
    for attr_name, query_name in (
        ("filter", "filter"),
        ("sort_by", "sortby"),
        ("customer_number", "customernumber"),
        ("name", "name"),
        ("zip_code", "zipcode"),
        ("city", "city"),
        ("email", "email"),
        ("phone", "phone"),
        ("organisation_number", "organisationnumber"),
        ("gln", "gln"),
        ("gln_delivery", "glndelivery"),
        ("last_modified", "lastmodified"),
    ):
        _set_query_param(query_params, query_name, getattr(args, attr_name, None))
    return _emit_request_read(
        ctx,
        audit_key="customers.list",
        path="/customers",
        query_params=query_params or None,
    )


def cmd_customers_get(args: Any, ctx: dict[str, Any]) -> int:
    customer_number = str(getattr(args, "customer_number", "") or "").strip()
    path = f"/customers/{customer_number}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="customers.get", path=path, payload=payload)


def cmd_suppliers_list(args: Any, ctx: dict[str, Any]) -> int:
    query_params: dict[str, Any] = {}
    for attr_name, query_name in (
        ("supplier_number", "suppliernumber"),
        ("name", "name"),
        ("organisation_number", "organisationnumber"),
        ("phone", "phone"),
        ("zip_code", "zipcode"),
        ("city", "city"),
        ("email", "email"),
        ("last_modified", "lastmodified"),
    ):
        _set_query_param(query_params, query_name, getattr(args, attr_name, None))
    return _emit_request_read(
        ctx,
        audit_key="suppliers.list",
        path="/suppliers",
        query_params=query_params or None,
    )


def cmd_suppliers_get(args: Any, ctx: dict[str, Any]) -> int:
    supplier_number = str(getattr(args, "supplier_number", "") or "").strip()
    path = f"/suppliers/{supplier_number}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="suppliers.get", path=path, payload=payload)


def cmd_employees_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/employees"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="employees.list", path=path, payload=payload)


def cmd_employees_get(args: Any, ctx: dict[str, Any]) -> int:
    employee_id = str(getattr(args, "employee_id", "") or "").strip()
    path = f"/employees/{employee_id}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="employees.get", path=path, payload=payload)


def cmd_absence_transactions_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/absencetransactions"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="absence_transactions.list", path=path, payload=payload)


def cmd_absence_transactions_get(args: Any, ctx: dict[str, Any]) -> int:
    transaction_id = str(getattr(args, "id", "") or "").strip()
    path = f"/absencetransactions/{transaction_id}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="absence_transactions.get", path=path, payload=payload)


def cmd_absence_transactions_get_by_employee_date_code(args: Any, ctx: dict[str, Any]) -> int:
    employee_id = str(getattr(args, "employee_id", "") or "").strip()
    date = str(getattr(args, "date", "") or "").strip()
    code = str(getattr(args, "code", "") or "").strip()
    path = f"/absencetransactions/{employee_id}/{date}/{code}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="absence_transactions.get_by_employee_date_code", path=path, payload=payload)


def cmd_attendance_transactions_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/attendancetransactions"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="attendance_transactions.list", path=path, payload=payload)


def cmd_attendance_transactions_get(args: Any, ctx: dict[str, Any]) -> int:
    transaction_id = str(getattr(args, "id", "") or "").strip()
    path = f"/attendancetransactions/{transaction_id}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="attendance_transactions.get", path=path, payload=payload)


def cmd_attendance_transactions_get_by_employee_date_code(args: Any, ctx: dict[str, Any]) -> int:
    employee_id = str(getattr(args, "employee_id", "") or "").strip()
    date = str(getattr(args, "date", "") or "").strip()
    code = str(getattr(args, "code", "") or "").strip()
    path = f"/attendancetransactions/{employee_id}/{date}/{code}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="attendance_transactions.get_by_employee_date_code", path=path, payload=payload)


def cmd_salary_transactions_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/salarytransactions"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="salary_transactions.list", path=path, payload=payload)


def cmd_salary_transactions_get(args: Any, ctx: dict[str, Any]) -> int:
    salary_row = str(getattr(args, "salary_row", "") or "").strip()
    path = f"/salarytransactions/{salary_row}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="salary_transactions.get", path=path, payload=payload)


def cmd_schedule_times_get(args: Any, ctx: dict[str, Any]) -> int:
    employee_id = str(getattr(args, "employee_id", "") or "").strip()
    date = str(getattr(args, "date", "") or "").strip()
    path = f"/scheduletimes/{employee_id}/{date}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="schedule_times.get", path=path, payload=payload)


def cmd_registrations_get(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/api/time/registrations-v2"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="registrations.get", path=path, payload=payload)


def cmd_vacation_debt_basis_get(args: Any, ctx: dict[str, Any]) -> int:
    year = str(getattr(args, "year", "") or "").strip()
    month = str(getattr(args, "month", "") or "").strip()
    path = f"/vacationdebtbasis/{year}/{month}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="vacation_debt_basis.get", path=path, payload=payload)


def cmd_articles_list(args: Any, ctx: dict[str, Any]) -> int:
    query_params: dict[str, Any] = {}
    for attr_name, query_name in (
        ("filter", "filter"),
        ("sort_by", "sortby"),
        ("article_number", "articlenumber"),
        ("description", "description"),
        ("ean", "ean"),
        ("supplier_number", "suppliernumber"),
        ("manufacturer", "manufacturer"),
        ("manufacturer_article_number", "manufacturerarticlenumber"),
        ("webshop", "webshop"),
        ("last_modified", "lastmodified"),
    ):
        _set_query_param(query_params, query_name, getattr(args, attr_name, None))
    return _emit_request_read(
        ctx,
        audit_key="articles.list",
        path="/articles",
        query_params=query_params or None,
    )


def cmd_articles_get(args: Any, ctx: dict[str, Any]) -> int:
    article_number = str(getattr(args, "article_number", "") or "").strip()
    path = f"/articles/{article_number}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="articles.get", path=path, payload=payload)


def cmd_articles_list_time_article_registrations(args: Any, ctx: dict[str, Any]) -> int:
    query_params: dict[str, Any] = {}
    from_date = str(getattr(args, "from_date", "") or "").strip()
    to_date = str(getattr(args, "to_date", "") or "").strip()
    if from_date:
        query_params["fromDate"] = from_date
    if to_date:
        query_params["toDate"] = to_date

    for attr_name, query_name in (
        ("customer_id", "customerIds"),
        ("project_id", "projectIds"),
        ("item_id", "itemIds"),
        ("cost_center_id", "costCenterIds"),
        ("owner_id", "ownerIds"),
    ):
        values = _string_list(getattr(args, attr_name, None))
        if values:
            query_params[query_name] = values

    for attr_name, query_name in (
        ("include_registrations_without_project", "includeRegistrationsWithoutProject"),
        ("invoiced", "invoiced"),
        ("in_invoice_basis", "inInvoiceBasis"),
        ("internal_articles", "internalArticles"),
        ("non_invoiceable", "nonInvoiceable"),
        ("include_non_invoiceable_price", "includeNonInvoiceablePrice"),
    ):
        value = str(getattr(args, attr_name, "") or "").strip()
        if value:
            query_params[query_name] = value

    payload = request_data(
        ctx=ctx,
        method="GET",
        path="/api/time/articles-v1",
        query_params=query_params or None,
        expect_json=True,
        expect_json_object=False,
    )
    return _emit_read(
        ctx,
        audit_key="articles.list_time_article_registrations",
        path="/api/time/articles-v1",
        payload=payload,
    )


def cmd_price_lists_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/pricelists"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="price_lists.list", path=path, payload=payload)


def cmd_price_lists_get(args: Any, ctx: dict[str, Any]) -> int:
    code = str(getattr(args, "code", "") or "").strip()
    path = f"/pricelists/{code}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="price_lists.get", path=path, payload=payload)


def cmd_prices_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/prices"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="prices.list", path=path, payload=payload)


def cmd_prices_get(args: Any, ctx: dict[str, Any]) -> int:
    price_list = str(getattr(args, "price_list", "") or "").strip()
    article_number = str(getattr(args, "article_number", "") or "").strip()
    path = f"/prices/{price_list}/{article_number}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="prices.get", path=path, payload=payload)


def cmd_prices_get_by_from_quantity(args: Any, ctx: dict[str, Any]) -> int:
    price_list = str(getattr(args, "price_list", "") or "").strip()
    article_number = str(getattr(args, "article_number", "") or "").strip()
    from_quantity = str(getattr(args, "from_quantity", "") or "").strip()
    path = f"/prices/{price_list}/{article_number}/{from_quantity}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="prices.get_by_from_quantity", path=path, payload=payload)


def cmd_prices_list_sublist(args: Any, ctx: dict[str, Any]) -> int:
    price_list = str(getattr(args, "price_list", "") or "").strip()
    article_number = str(getattr(args, "article_number", "") or "").strip()
    path = f"/prices/sublist/{price_list}/{article_number}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="prices.list_sublist", path=path, payload=payload)


def cmd_projects_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/projects"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="projects.list", path=path, payload=payload)


def cmd_projects_get(args: Any, ctx: dict[str, Any]) -> int:
    project_number = str(getattr(args, "project_number", "") or "").strip()
    path = f"/projects/{project_number}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="projects.get", path=path, payload=payload)


def cmd_cost_centers_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/costcenters"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="cost_centers.list", path=path, payload=payload)


def cmd_cost_centers_get(args: Any, ctx: dict[str, Any]) -> int:
    code = str(getattr(args, "code", "") or "").strip()
    path = f"/costcenters/{code}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="cost_centers.get", path=path, payload=payload)


def cmd_currencies_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/currencies"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="currencies.list", path=path, payload=payload)


def cmd_currencies_get(args: Any, ctx: dict[str, Any]) -> int:
    code = str(getattr(args, "code", "") or "").strip()
    path = f"/currencies/{code}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="currencies.get", path=path, payload=payload)


def cmd_units_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/units"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="units.list", path=path, payload=payload)


def cmd_units_get(args: Any, ctx: dict[str, Any]) -> int:
    code = str(getattr(args, "code", "") or "").strip()
    path = f"/units/{code}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="units.get", path=path, payload=payload)


def cmd_terms_of_deliveries_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/termsofdeliveries"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="terms_of_deliveries.list", path=path, payload=payload)


def cmd_terms_of_deliveries_get(args: Any, ctx: dict[str, Any]) -> int:
    code = str(getattr(args, "code", "") or "").strip()
    path = f"/termsofdeliveries/{code}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="terms_of_deliveries.get", path=path, payload=payload)


def cmd_way_of_deliveries_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/wayofdeliveries"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="way_of_deliveries.list", path=path, payload=payload)


def cmd_way_of_deliveries_get(args: Any, ctx: dict[str, Any]) -> int:
    code = str(getattr(args, "code", "") or "").strip()
    path = f"/wayofdeliveries/{code}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="way_of_deliveries.get", path=path, payload=payload)


def cmd_terms_of_payments_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/termsofpayments"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="terms_of_payments.list", path=path, payload=payload)


def cmd_terms_of_payments_get(args: Any, ctx: dict[str, Any]) -> int:
    code = str(getattr(args, "code", "") or "").strip()
    path = f"/termsofpayments/{code}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="terms_of_payments.get", path=path, payload=payload)


def cmd_account_charts_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/accountcharts"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="account_charts.list", path=path, payload=payload)


def cmd_accounts_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/accounts"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="accounts.list", path=path, payload=payload)


def cmd_accounts_get(args: Any, ctx: dict[str, Any]) -> int:
    number = str(getattr(args, "number", "") or "").strip()
    path = f"/accounts/{number}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="accounts.get", path=path, payload=payload)


def cmd_financial_years_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/financialyears"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="financial_years.list", path=path, payload=payload)


def cmd_financial_years_get(args: Any, ctx: dict[str, Any]) -> int:
    year_id = str(getattr(args, "year_id", "") or "").strip()
    path = f"/financialyears/{year_id}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="financial_years.get", path=path, payload=payload)


def cmd_predefined_accounts_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/predefinedaccounts"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="predefined_accounts.list", path=path, payload=payload)


def cmd_predefined_accounts_get(args: Any, ctx: dict[str, Any]) -> int:
    name = str(getattr(args, "name", "") or "").strip()
    path = f"/predefinedaccounts/{name}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="predefined_accounts.get", path=path, payload=payload)


def cmd_predefined_voucher_series_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/predefinedvoucherseries"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="predefined_voucher_series.list", path=path, payload=payload)


def cmd_predefined_voucher_series_get(args: Any, ctx: dict[str, Any]) -> int:
    name = str(getattr(args, "name", "") or "").strip()
    path = f"/predefinedvoucherseries/{name}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="predefined_voucher_series.get", path=path, payload=payload)


def cmd_modes_of_payments_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/modesofpayments"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="modes_of_payments.list", path=path, payload=payload)


def cmd_modes_of_payments_get(args: Any, ctx: dict[str, Any]) -> int:
    code = str(getattr(args, "code", "") or "").strip()
    path = f"/modesofpayments/{code}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="modes_of_payments.get", path=path, payload=payload)


def cmd_voucher_series_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/voucherseries"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="voucher_series.list", path=path, payload=payload)


def cmd_voucher_series_get(args: Any, ctx: dict[str, Any]) -> int:
    code = str(getattr(args, "code", "") or "").strip()
    path = f"/voucherseries/{code}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="voucher_series.get", path=path, payload=payload)


def cmd_vouchers_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/vouchers"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="vouchers.list", path=path, payload=payload)


def cmd_vouchers_get(args: Any, ctx: dict[str, Any]) -> int:
    voucher_series = str(getattr(args, "voucher_series", "") or "").strip()
    voucher_number = str(getattr(args, "voucher_number", "") or "").strip()
    path = f"/vouchers/{voucher_series}/{voucher_number}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="vouchers.get", path=path, payload=payload)


def cmd_vouchers_list_by_series(args: Any, ctx: dict[str, Any]) -> int:
    voucher_series = str(getattr(args, "voucher_series", "") or "").strip()
    path = f"/vouchers/sublist/{voucher_series}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="vouchers.list_by_series", path=path, payload=payload)


def cmd_vouchers_list_current_financial_year(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/vouchers/sublist"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="vouchers.list_current_financial_year", path=path, payload=payload)


def cmd_invoice_payments_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/invoicepayments"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="invoice_payments.list", path=path, payload=payload)


def cmd_invoice_payments_get(args: Any, ctx: dict[str, Any]) -> int:
    number = str(getattr(args, "number", "") or "").strip()
    path = f"/invoicepayments/{number}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="invoice_payments.get", path=path, payload=payload)


def cmd_invoices_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/invoices"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="invoices.list", path=path, payload=payload)


def cmd_invoices_get(args: Any, ctx: dict[str, Any]) -> int:
    document_number = str(getattr(args, "document_number", "") or "").strip()
    path = f"/invoices/{document_number}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="invoices.get", path=path, payload=payload)


def cmd_invoices_preview(args: Any, ctx: dict[str, Any]) -> int:
    document_number = str(getattr(args, "document_number", "") or "").strip()
    return _emit_binary_request_read(
        ctx,
        audit_key="invoices.preview",
        path=f"/invoices/{document_number}/preview",
        output_file=getattr(args, "output_file", None),
    )


def cmd_invoices_print(args: Any, ctx: dict[str, Any]) -> int:
    document_number = str(getattr(args, "document_number", "") or "").strip()
    return _emit_binary_request_read(
        ctx,
        audit_key="invoices.print",
        path=f"/invoices/{document_number}/print",
        output_file=getattr(args, "output_file", None),
    )


def cmd_invoices_print_reminder(args: Any, ctx: dict[str, Any]) -> int:
    document_number = str(getattr(args, "document_number", "") or "").strip()
    return _emit_binary_request_read(
        ctx,
        audit_key="invoices.print_reminder",
        path=f"/invoices/{document_number}/printreminder",
        output_file=getattr(args, "output_file", None),
    )


def cmd_offers_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/offers"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="offers.list", path=path, payload=payload)


def cmd_offers_get(args: Any, ctx: dict[str, Any]) -> int:
    document_number = str(getattr(args, "document_number", "") or "").strip()
    path = f"/offers/{document_number}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="offers.get", path=path, payload=payload)


def cmd_offers_preview(args: Any, ctx: dict[str, Any]) -> int:
    document_number = str(getattr(args, "document_number", "") or "").strip()
    return _emit_binary_request_read(
        ctx,
        audit_key="offers.preview",
        path=f"/offers/{document_number}/preview",
        output_file=getattr(args, "output_file", None),
    )


def cmd_offers_print(args: Any, ctx: dict[str, Any]) -> int:
    document_number = str(getattr(args, "document_number", "") or "").strip()
    return _emit_binary_request_read(
        ctx,
        audit_key="offers.print",
        path=f"/offers/{document_number}/print",
        output_file=getattr(args, "output_file", None),
    )


def cmd_orders_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    path = "/orders"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="orders.list", path=path, payload=payload)


def cmd_orders_get(args: Any, ctx: dict[str, Any]) -> int:
    document_number = str(getattr(args, "document_number", "") or "").strip()
    path = f"/orders/{document_number}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(ctx, audit_key="orders.get", path=path, payload=payload)


def cmd_orders_preview(args: Any, ctx: dict[str, Any]) -> int:
    document_number = str(getattr(args, "document_number", "") or "").strip()
    return _emit_binary_request_read(
        ctx,
        audit_key="orders.preview",
        path=f"/orders/{document_number}/preview",
        output_file=getattr(args, "output_file", None),
    )


def cmd_orders_print(args: Any, ctx: dict[str, Any]) -> int:
    document_number = str(getattr(args, "document_number", "") or "").strip()
    return _emit_binary_request_read(
        ctx,
        audit_key="orders.print",
        path=f"/orders/{document_number}/print",
        output_file=getattr(args, "output_file", None),
    )

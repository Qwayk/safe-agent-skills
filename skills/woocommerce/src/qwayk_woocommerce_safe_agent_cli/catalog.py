from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import re


_PATH_PARAM_RE = re.compile(r"{([^}]+)}")
_DOCS_BASE_URL = "https://developer.woocommerce.com/docs/apis/rest-api/v3"


RAW_OPERATIONS: tuple[tuple[str, str, str], ...] = (
    ("GET", "/", "api-reference"),
    ("POST", "/coupons", "coupons"),
    ("GET", "/coupons/{id}", "coupons"),
    ("GET", "/coupons", "coupons"),
    ("PUT", "/coupons/{id}", "coupons"),
    ("DELETE", "/coupons/{id}", "coupons"),
    ("POST", "/coupons/batch", "coupons"),
    ("POST", "/customers", "customers"),
    ("GET", "/customers/{id}", "customers"),
    ("GET", "/customers", "customers"),
    ("PUT", "/customers/{id}", "customers"),
    ("DELETE", "/customers/{id}", "customers"),
    ("POST", "/customers/batch", "customers"),
    ("GET", "/customers/{id}/downloads", "customers"),
    ("POST", "/orders", "orders"),
    ("GET", "/orders/{id}", "orders"),
    ("GET", "/orders", "orders"),
    ("PUT", "/orders/{id}", "orders"),
    ("DELETE", "/orders/{id}", "orders"),
    ("POST", "/orders/batch", "orders"),
    ("POST", "/orders/{id}/actions/send_order_details", "order-actions"),
    ("POST", "/orders/{id}/actions/send_email", "order-actions"),
    ("GET", "/orders/{id}/actions/email_templates", "order-actions"),
    ("POST", "/orders/{id}/notes", "order-notes"),
    ("GET", "/orders/{id}/notes/{note_id}", "order-notes"),
    ("GET", "/orders/{id}/notes", "order-notes"),
    ("DELETE", "/orders/{id}/notes/{note_id}", "order-notes"),
    ("POST", "/orders/{id}/refunds", "order-refunds"),
    ("GET", "/orders/{id}/refunds/{refund_id}", "order-refunds"),
    ("GET", "/orders/{id}/refunds", "order-refunds"),
    ("DELETE", "/orders/{id}/refunds/{refund_id}", "order-refunds"),
    ("POST", "/products", "products"),
    ("GET", "/products/{id}", "products"),
    ("GET", "/products", "products"),
    ("POST", "/products/{product_id}/duplicate", "products"),
    ("PUT", "/products/{id}", "products"),
    ("DELETE", "/products/{id}", "products"),
    ("POST", "/products/batch", "products"),
    ("POST", "/products/{product_id}/variations", "product-variations"),
    ("GET", "/products/{product_id}/variations/{id}", "product-variations"),
    ("GET", "/products/{product_id}/variations", "product-variations"),
    ("PUT", "/products/{product_id}/variations/{id}", "product-variations"),
    ("DELETE", "/products/{product_id}/variations/{id}", "product-variations"),
    ("POST", "/products/{product_id}/variations/batch", "product-variations"),
    ("POST", "/products/attributes", "product-attributes"),
    ("GET", "/products/attributes/{id}", "product-attributes"),
    ("GET", "/products/attributes", "product-attributes"),
    ("PUT", "/products/attributes/{id}", "product-attributes"),
    ("DELETE", "/products/attributes/{id}", "product-attributes"),
    ("POST", "/products/attributes/batch", "product-attributes"),
    ("POST", "/products/attributes/{attribute_id}/terms", "product-attribute-terms"),
    ("GET", "/products/attributes/{attribute_id}/terms/{id}", "product-attribute-terms"),
    ("GET", "/products/attributes/{attribute_id}/terms", "product-attribute-terms"),
    ("PUT", "/products/attributes/{attribute_id}/terms/{id}", "product-attribute-terms"),
    ("DELETE", "/products/attributes/{attribute_id}/terms/{id}", "product-attribute-terms"),
    ("POST", "/products/attributes/{attribute_id}/terms/batch", "product-attribute-terms"),
    ("POST", "/products/categories", "product-categories"),
    ("GET", "/products/categories/{id}", "product-categories"),
    ("GET", "/products/categories", "product-categories"),
    ("PUT", "/products/categories/{id}", "product-categories"),
    ("DELETE", "/products/categories/{id}", "product-categories"),
    ("POST", "/products/categories/batch", "product-categories"),
    ("GET", "/products/custom-fields/names", "product-custom-fields"),
    ("POST", "/products/shipping_classes", "product-shipping-classes"),
    ("GET", "/products/shipping_classes/{id}", "product-shipping-classes"),
    ("GET", "/products/shipping_classes", "product-shipping-classes"),
    ("PUT", "/products/shipping_classes/{id}", "product-shipping-classes"),
    ("DELETE", "/products/shipping_classes/{id}", "product-shipping-classes"),
    ("POST", "/products/shipping_classes/batch", "product-shipping-classes"),
    ("POST", "/products/tags", "product-tags"),
    ("GET", "/products/tags/{id}", "product-tags"),
    ("GET", "/products/tags", "product-tags"),
    ("PUT", "/products/tags/{id}", "product-tags"),
    ("DELETE", "/products/tags/{id}", "product-tags"),
    ("POST", "/products/tags/batch", "product-tags"),
    ("POST", "/products/reviews", "product-reviews"),
    ("GET", "/products/reviews/{id}", "product-reviews"),
    ("GET", "/products/reviews", "product-reviews"),
    ("PUT", "/products/reviews/{id}", "product-reviews"),
    ("DELETE", "/products/reviews/{id}", "product-reviews"),
    ("POST", "/products/reviews/batch", "product-reviews"),
    ("GET", "/reports", "reports"),
    ("GET", "/reports/sales", "reports"),
    ("GET", "/reports/top_sellers", "reports"),
    ("GET", "/reports/coupons/totals", "reports"),
    ("GET", "/reports/customers/totals", "reports"),
    ("GET", "/reports/orders/totals", "reports"),
    ("GET", "/reports/products/totals", "reports"),
    ("GET", "/reports/reviews/totals", "reports"),
    ("GET", "/refunds", "refunds"),
    ("POST", "/taxes", "taxes"),
    ("GET", "/taxes/{id}", "taxes"),
    ("GET", "/taxes", "taxes"),
    ("PUT", "/taxes/{id}", "taxes"),
    ("DELETE", "/taxes/{id}", "taxes"),
    ("POST", "/taxes/batch", "taxes"),
    ("POST", "/taxes/classes", "tax-classes"),
    ("GET", "/taxes/classes", "tax-classes"),
    ("DELETE", "/taxes/classes/{slug}", "tax-classes"),
    ("POST", "/webhooks", "webhooks"),
    ("GET", "/webhooks/{id}", "webhooks"),
    ("GET", "/webhooks", "webhooks"),
    ("PUT", "/webhooks/{id}", "webhooks"),
    ("DELETE", "/webhooks/{id}", "webhooks"),
    ("POST", "/webhooks/batch", "webhooks"),
    ("GET", "/settings", "settings"),
    ("GET", "/settings/{group_id}/{id}", "setting-options"),
    ("GET", "/settings/{group_id}", "setting-options"),
    ("PUT", "/settings/{group_id}/{id}", "setting-options"),
    ("POST", "/settings/{group_id}/batch", "setting-options"),
    ("GET", "/payment_gateways/{id}", "payment-gateways"),
    ("GET", "/payment_gateways", "payment-gateways"),
    ("PUT", "/payment_gateways/{id}", "payment-gateways"),
    ("POST", "/shipping/zones", "shipping-zones"),
    ("GET", "/shipping/zones/{id}", "shipping-zones"),
    ("GET", "/shipping/zones", "shipping-zones"),
    ("PUT", "/shipping/zones/{id}", "shipping-zones"),
    ("DELETE", "/shipping/zones/{id}", "shipping-zones"),
    ("GET", "/shipping/zones/{zone_id}/locations", "shipping-zone-locations"),
    ("PUT", "/shipping/zones/{zone_id}/locations", "shipping-zone-locations"),
    ("POST", "/shipping/zones/{zone_id}/methods", "shipping-zone-methods"),
    ("GET", "/shipping/zones/{zone_id}/methods/{id}", "shipping-zone-methods"),
    ("GET", "/shipping/zones/{zone_id}/methods", "shipping-zone-methods"),
    ("PUT", "/shipping/zones/{zone_id}/methods/{id}", "shipping-zone-methods"),
    ("DELETE", "/shipping/zones/{zone_id}/methods/{id}", "shipping-zone-methods"),
    ("GET", "/shipping_methods/{id}", "shipping-methods"),
    ("GET", "/shipping_methods", "shipping-methods"),
    ("GET", "/system_status", "system-status"),
    ("GET", "/system_status/tools/{id}", "system-status-tools"),
    ("GET", "/system_status/tools", "system-status-tools"),
    ("PUT", "/system_status/tools/{id}", "system-status-tools"),
    ("GET", "/data", "data"),
    ("GET", "/data/continents", "data"),
    ("GET", "/data/continents/{location}", "data"),
    ("GET", "/data/countries", "data"),
    ("GET", "/data/countries/{location}", "data"),
    ("GET", "/data/currencies", "data"),
    ("GET", "/data/currencies/{currency}", "data"),
    ("GET", "/data/currencies/current", "data"),
)


CRUD_BASE_PATHS = {
    "coupons": "/coupons",
    "customers": "/customers",
    "orders": "/orders",
    "order-notes": "/orders/{id}/notes",
    "order-refunds": "/orders/{id}/refunds",
    "products": "/products",
    "product-variations": "/products/{product_id}/variations",
    "product-attributes": "/products/attributes",
    "product-attribute-terms": "/products/attributes/{attribute_id}/terms",
    "product-categories": "/products/categories",
    "product-shipping-classes": "/products/shipping_classes",
    "product-tags": "/products/tags",
    "product-reviews": "/products/reviews",
    "taxes": "/taxes",
    "webhooks": "/webhooks",
    "shipping-zones": "/shipping/zones",
    "shipping-zone-methods": "/shipping/zones/{zone_id}/methods",
}


PAGINATED_KEYS = {
    "coupons list",
    "customers list",
    "customers list-downloads",
    "orders list",
    "order-notes list",
    "order-refunds list",
    "products list",
    "product-variations list",
    "product-attributes list",
    "product-attribute-terms list",
    "product-categories list",
    "product-shipping-classes list",
    "product-tags list",
    "product-reviews list",
    "refunds list",
    "taxes list",
    "webhooks list",
    "shipping-zones list",
    "shipping-zone-methods list",
}


OPTIONAL_BODY_KEYS = {
    "products duplicate",
    "order-actions send-order-details",
    "order-actions send-email",
    "system-status-tools run",
}


READ_BACK_PATHS = {
    "coupons": "/coupons/{id}",
    "customers": "/customers/{id}",
    "orders": "/orders/{id}",
    "order-notes": "/orders/{id}/notes/{note_id}",
    "order-refunds": "/orders/{id}/refunds/{refund_id}",
    "products": "/products/{id}",
    "product-variations": "/products/{product_id}/variations/{id}",
    "product-attributes": "/products/attributes/{id}",
    "product-attribute-terms": "/products/attributes/{attribute_id}/terms/{id}",
    "product-categories": "/products/categories/{id}",
    "product-shipping-classes": "/products/shipping_classes/{id}",
    "product-tags": "/products/tags/{id}",
    "product-reviews": "/products/reviews/{id}",
    "taxes": "/taxes/{id}",
    "webhooks": "/webhooks/{id}",
    "setting-options": "/settings/{group_id}/{id}",
    "payment-gateways": "/payment_gateways/{id}",
    "shipping-zones": "/shipping/zones/{id}",
    "shipping-zone-locations": "/shipping/zones/{zone_id}/locations",
    "shipping-zone-methods": "/shipping/zones/{zone_id}/methods/{id}",
    "system-status-tools": "/system_status/tools/{id}",
}


@dataclass(frozen=True)
class OperationSpec:
    key: str
    family: str
    action: str
    command_tokens: tuple[str, ...]
    method: str
    path: str
    docs_page: str
    docs_url: str
    path_parameters: tuple[str, ...]
    supports_pagination: bool
    body_mode: str
    risk_level: str
    yes_required: bool
    auth_required: bool
    verification_mode: str
    verify_get_path: str | None


def _docs_url_for(page: str) -> str:
    return f"{_DOCS_BASE_URL}/{page}/"


def _path_parameters_for(path: str) -> tuple[str, ...]:
    return tuple(_PATH_PARAM_RE.findall(path))


def _command_tokens_for(method: str, path: str, docs_page: str) -> tuple[str, str]:
    family = docs_page
    if docs_page == "api-reference":
        return ("index", "get")
    if docs_page == "order-actions":
        if path.endswith("/send_order_details"):
            return ("order-actions", "send-order-details")
        if path.endswith("/send_email"):
            return ("order-actions", "send-email")
        return ("order-actions", "list-email-templates")
    if docs_page == "product-custom-fields":
        return ("product-custom-fields", "list-names")
    if docs_page == "reports":
        report_map = {
            "/reports": "list",
            "/reports/sales": "sales",
            "/reports/top_sellers": "top-sellers",
            "/reports/coupons/totals": "coupon-totals",
            "/reports/customers/totals": "customer-totals",
            "/reports/orders/totals": "order-totals",
            "/reports/products/totals": "product-totals",
            "/reports/reviews/totals": "review-totals",
        }
        return ("reports", report_map[path])
    if docs_page == "refunds":
        return ("refunds", "list")
    if docs_page == "tax-classes":
        if path == "/taxes/classes" and method == "GET":
            return ("tax-classes", "list")
        if path == "/taxes/classes" and method == "POST":
            return ("tax-classes", "create")
        return ("tax-classes", "delete")
    if docs_page == "settings":
        return ("settings", "list-groups")
    if docs_page == "setting-options":
        if path == "/settings/{group_id}/{id}" and method == "GET":
            return ("setting-options", "get")
        if path == "/settings/{group_id}" and method == "GET":
            return ("setting-options", "list-group")
        if path == "/settings/{group_id}/{id}" and method == "PUT":
            return ("setting-options", "update")
        return ("setting-options", "batch")
    if docs_page == "payment-gateways":
        if path == "/payment_gateways":
            return ("payment-gateways", "list")
        if method == "GET":
            return ("payment-gateways", "get")
        return ("payment-gateways", "update")
    if docs_page == "shipping-zone-locations":
        return ("shipping-zone-locations", "get" if method == "GET" else "update")
    if docs_page == "shipping-methods":
        return ("shipping-methods", "get" if "{id}" in path else "list")
    if docs_page == "system-status":
        return ("system-status", "get")
    if docs_page == "system-status-tools":
        if path == "/system_status/tools":
            return ("system-status-tools", "list")
        if method == "GET":
            return ("system-status-tools", "get")
        return ("system-status-tools", "run")
    if docs_page == "data":
        data_map = {
            "/data": "list",
            "/data/continents": "list-continents",
            "/data/continents/{location}": "get-continent",
            "/data/countries": "list-countries",
            "/data/countries/{location}": "get-country",
            "/data/currencies": "list-currencies",
            "/data/currencies/{currency}": "get-currency",
            "/data/currencies/current": "current-currency",
        }
        return ("data", data_map[path])
    if docs_page == "customers" and path.endswith("/downloads"):
        return ("customers", "list-downloads")

    base_path = CRUD_BASE_PATHS.get(docs_page)
    if not base_path:
        raise ValueError(f"Unsupported docs page for command mapping: {docs_page}")
    if path.endswith("/batch"):
        return (family, "batch")
    if path.endswith("/duplicate"):
        return ("products", "duplicate")
    if method == "POST" and path == base_path:
        return (family, "create")
    if method == "GET" and path == base_path:
        return (family, "list")
    if method == "GET":
        return (family, "get")
    if method == "PUT":
        return (family, "update")
    if method == "DELETE":
        return (family, "delete")
    raise ValueError(f"Unsupported operation mapping: {method} {path}")


def _supports_pagination(key: str) -> bool:
    return key in PAGINATED_KEYS


def _body_mode_for(method: str, key: str) -> str:
    if method in {"GET", "DELETE"}:
        return "none"
    if key in OPTIONAL_BODY_KEYS:
        return "optional"
    return "required"


def _risk_level_for(method: str, family: str, key: str, path: str) -> str:
    if method == "GET":
        return "read"
    if method == "DELETE":
        return "high"
    if path.endswith("/batch"):
        return "high"
    if family == "order-actions":
        return "high"
    if family == "webhooks":
        return "high"
    if family == "payment-gateways":
        return "high"
    if family == "shipping-zone-locations":
        return "high"
    if family == "system-status-tools":
        return "high"
    return "medium"


def _verification_for(method: str, family: str, action: str, path: str) -> tuple[str, str | None]:
    if method == "GET":
        return ("none", None)
    if method == "DELETE":
        return ("delete-response", None)
    if path.endswith("/batch"):
        return ("response", None)
    if family == "order-actions":
        return ("response", None)
    if family == "tax-classes":
        return ("response", None)
    if family == "setting-options" and action == "batch":
        return ("response", None)
    verify_get_path = READ_BACK_PATHS.get(family)
    if verify_get_path:
        return ("read-back", verify_get_path)
    return ("response", None)


def _build_spec(method: str, path: str, docs_page: str) -> OperationSpec:
    command_tokens = _command_tokens_for(method, path, docs_page)
    family, action = command_tokens
    key = " ".join(command_tokens)
    risk_level = _risk_level_for(method, family, key, path)
    verification_mode, verify_get_path = _verification_for(method, family, action, path)
    return OperationSpec(
        key=key,
        family=family,
        action=action,
        command_tokens=command_tokens,
        method=method,
        path=path,
        docs_page=docs_page,
        docs_url=_docs_url_for(docs_page),
        path_parameters=_path_parameters_for(path),
        supports_pagination=_supports_pagination(key),
        body_mode=_body_mode_for(method, key),
        risk_level=risk_level,
        yes_required=risk_level == "high",
        auth_required=key != "index get",
        verification_mode=verification_mode,
        verify_get_path=verify_get_path,
    )


@lru_cache(maxsize=1)
def load_operation_catalog() -> tuple[OperationSpec, ...]:
    return tuple(_build_spec(method, path, docs_page) for method, path, docs_page in RAW_OPERATIONS)


@lru_cache(maxsize=1)
def operations_by_key() -> dict[str, OperationSpec]:
    return {spec.key: spec for spec in load_operation_catalog()}


@lru_cache(maxsize=1)
def operations_by_family() -> dict[str, tuple[OperationSpec, ...]]:
    grouped: dict[str, list[OperationSpec]] = {}
    for spec in load_operation_catalog():
        grouped.setdefault(spec.family, []).append(spec)
    return {family: tuple(specs) for family, specs in grouped.items()}


def find_operation(key: str) -> OperationSpec:
    spec = operations_by_key().get(key)
    if spec is None:
        raise KeyError(f"Unknown WooCommerce operation key: {key}")
    return spec

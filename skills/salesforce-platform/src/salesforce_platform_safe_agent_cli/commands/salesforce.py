from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..http import HttpClient, HttpResponse
from ..json_files import read_json_file, write_json_file


_TOOL_NAME = "qwayk-salesforce-platform-safe-agent-cli"
_USER_AGENT = f"{_TOOL_NAME}/safe-apis"
_PATH_RE = re.compile(r"\{([A-Za-z0-9_]+)\}")
_SENSITIVE_KEY_RE = re.compile(r"(secret|token|password|authorization|aws_access_key|aws_secret)", re.I)
_BEFORE_STATE_REFUSAL_REASON = (
    "Refused: this Salesforce write has no reliable generic before-state snapshot in this runtime. "
    "Review the dry-run plan, then rerun with --ack-no-snapshot if you approve applying without a snapshot."
)
_MULTIPART_ALLOWED = {
    ("sobjects-object", "create"),
    ("sobjects-row", "update"),
    ("sobjects-external-id", "create"),
    ("sobjects-external-id", "upsert"),
    ("composite-collections", "create"),
    ("composite-collections", "update"),
    ("composite-collections", "upsert"),
}


@dataclass(frozen=True)
class CliArgSpec:
    name: str
    help: str
    query_name: str | None = None
    required: bool = False
    type_name: str = "str"
    choices: tuple[str, ...] | None = None
    multiple: bool = False


@dataclass(frozen=True)
class ActionSpec:
    method: str
    path: str
    summary: str
    write: bool
    display_path: str | None = None
    query_args: tuple[CliArgSpec, ...] = ()
    requires_body_file: bool = False
    requires_data_file: bool = False
    response_kind: str = "json"
    accept: str | None = None
    content_type: str | None = None
    require_yes: bool = False
    require_ack: bool = False
    require_plan_in: bool = False
    auth_required: bool = True
    fixed_json_body: Any = None


def _arg(
    name: str,
    *,
    help: str,
    query_name: str | None = None,
    required: bool = False,
    type_name: str = "str",
    choices: tuple[str, ...] | None = None,
    multiple: bool = False,
) -> CliArgSpec:
    return CliArgSpec(
        name=name,
        help=help,
        query_name=query_name,
        required=required,
        type_name=type_name,
        choices=choices,
        multiple=multiple,
    )


def _spec(
    method: str,
    path: str,
    summary: str,
    *,
    write: bool,
    display_path: str | None = None,
    query_args: tuple[CliArgSpec, ...] = (),
    requires_body_file: bool = False,
    requires_data_file: bool = False,
    response_kind: str = "json",
    accept: str | None = None,
    content_type: str | None = None,
    require_yes: bool = False,
    require_ack: bool = False,
    require_plan_in: bool = False,
    auth_required: bool = True,
    fixed_json_body: Any = None,
) -> ActionSpec:
    return ActionSpec(
        method=method,
        path=path,
        display_path=display_path,
        summary=summary,
        write=write,
        query_args=query_args,
        requires_body_file=requires_body_file,
        requires_data_file=requires_data_file,
        response_kind=response_kind,
        accept=accept,
        content_type=content_type,
        require_yes=require_yes,
        require_ack=require_ack,
        require_plan_in=require_plan_in,
        auth_required=auth_required,
        fixed_json_body=fixed_json_body,
    )


_ACTIONS: dict[str, dict[str, ActionSpec]] = {
    "versions": {
        "list": _spec(
            "GET",
            "/services/data/",
            "List available Salesforce REST API versions",
            write=False,
            auth_required=False,
        ),
    },
    "resources": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/",
            "List resources for one API version",
            write=False,
        ),
    },
    "openapi-sobjects": {
        "list-selectors": _spec(
            "GET",
            "/services/data/{api_version}/async/specifications/oas3",
            "List valid selector roots for the sObjects OpenAPI beta",
            write=False,
        ),
        "create": _spec(
            "POST",
            "/services/data/{api_version}/async/specifications/oas3",
            "Start generating an OpenAPI 3.0 document for sObjects REST API (Beta)",
            write=False,
            requires_body_file=True,
        ),
        "details": _spec(
            "GET",
            "/services/data/{api_version}/async/specifications/oas3/{locator_id}",
            "Get OpenAPI generation job details",
            write=False,
        ),
        "results": _spec(
            "GET",
            "/services/data/{api_version}/async/specifications/oas3/{locator_id}/results",
            "Get the generated OpenAPI 3.0 document",
            write=False,
        ),
    },
    "limits": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/limits/",
            "List org limits",
            write=False,
        ),
        "record-count": _spec(
            "GET",
            "/services/data/{api_version}/limits/recordCount",
            "List approximate record counts",
            write=False,
            query_args=(
                _arg("sobjects", help="Comma-separated object names", query_name="sObjects"),
            ),
        ),
    },
    "query": {
        "run": _spec(
            "GET",
            "/services/data/{api_version}/query",
            "Run a SOQL query",
            write=False,
            query_args=(
                _arg("soql", help="SOQL query text", query_name="q", required=True),
            ),
        ),
        "more": _spec(
            "GET",
            "/services/data/{api_version}/query/{query_locator}",
            "Get the next SOQL query page",
            write=False,
        ),
        "explain": _spec(
            "GET",
            "/services/data/{api_version}/query",
            "Get query performance feedback (Beta)",
            write=False,
            query_args=(
                _arg("explain", help="SOQL query, report ID, or list view ID", query_name="explain", required=True),
            ),
        ),
    },
    "query-all": {
        "run": _spec(
            "GET",
            "/services/data/{api_version}/queryAll",
            "Run a SOQL query that includes deleted and archived records",
            write=False,
            query_args=(
                _arg("soql", help="SOQL query text", query_name="q", required=True),
            ),
        ),
        "more": _spec(
            "GET",
            "/services/data/{api_version}/queryAll/{query_locator}",
            "Get the next QueryAll page",
            write=False,
        ),
    },
    "search": {
        "sosl": _spec(
            "GET",
            "/services/data/{api_version}/search/",
            "Run a SOSL search",
            write=False,
            query_args=(
                _arg("sosl", help="SOSL search string", query_name="q", required=True),
            ),
        ),
        "scope-order": _spec(
            "GET",
            "/services/data/{api_version}/search/scopeOrder",
            "Get search scope and order",
            write=False,
        ),
        "layouts": _spec(
            "GET",
            "/services/data/{api_version}/search/layout/",
            "Get search result layouts",
            write=False,
            query_args=(
                _arg("object-list", help="Comma-separated object names", query_name="q", required=True),
            ),
        ),
        "autocomplete": _spec(
            "GET",
            "/services/data/{api_version}/search/suggestions",
            "Get autocomplete and instant search results",
            write=False,
            query_args=(
                _arg("query", help="Search text", query_name="q", required=True),
                _arg("sobject", help="Comma-separated object names"),
                _arg("type", help="Feed item type such as question"),
                _arg("limit", help="Max suggestions", type_name="int"),
                _arg("use-search-scope", help="Include the user's search scope", query_name="useSearchScope", type_name="bool"),
                _arg("ignore-unsupported-sobjects", help="Ignore unsupported objects", query_name="ignoreUnsupportedSObjects", type_name="bool"),
            ),
        ),
        "suggested-title": _spec(
            "GET",
            "/services/data/{api_version}/search/suggestTitleMatches",
            "Get suggested Knowledge article title matches",
            write=False,
            query_args=(
                _arg("query", help="Search text", query_name="q", required=True),
                _arg("language", help="Article language such as en_US", required=True),
                _arg("publish-status", help="Draft, Online, or Archived", query_name="publishStatus", required=True),
                _arg("limit", help="Max articles", type_name="int"),
                _arg("channel", help="Article channel"),
                _arg("validation-status", help="Article validation status", query_name="validationStatus"),
                _arg("article-type", help="Article type prefix", query_name="articleTypes", multiple=True),
                _arg("topic", help="Article topic", query_name="topics", multiple=True),
            ),
        ),
        "suggested-queries": _spec(
            "GET",
            "/services/data/{api_version}/search/suggestSearchQueries",
            "Get suggested Knowledge searches",
            write=False,
            query_args=(
                _arg("query", help="Search text", query_name="q", required=True),
                _arg("language", help="Query language such as en_US", required=True),
                _arg("channel", help="Knowledge channel"),
                _arg("limit", help="Max suggestions", type_name="int"),
            ),
        ),
    },
    "parameterized-search": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/parameterizedSearch/",
            "Run parameterized search with URI parameters",
            write=False,
            query_args=(
                _arg("query", help="Search text", query_name="q", required=True),
            ),
        ),
        "post": _spec(
            "POST",
            "/services/data/{api_version}/parameterizedSearch/",
            "Run parameterized search with a JSON request body",
            write=False,
            requires_body_file=True,
        ),
    },
    "recent": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/recent",
            "List recently viewed items",
            write=False,
            query_args=(
                _arg("limit", help="Max items", type_name="int"),
            ),
        ),
    },
    "record-count": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/limits/recordCount",
            "List approximate record counts",
            write=False,
            query_args=(
                _arg("sobjects", help="Comma-separated object names", query_name="sObjects"),
            ),
        ),
    },
    "tabs": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/tabs/",
            "List tabs available to the current user",
            write=False,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/tabs/",
            "Return tab response headers",
            write=False,
        ),
    },
    "themes": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/theme",
            "List Salesforce theme icons and colors",
            write=False,
        ),
    },
    "app-menu": {
        "types": _spec(
            "GET",
            "/services/data/{api_version}/appMenu/",
            "List app menu types",
            write=False,
        ),
        "items": _spec(
            "GET",
            "/services/data/{api_version}/appMenu/AppSwitcher/",
            "List app switcher items",
            write=False,
        ),
        "mobile-items": _spec(
            "GET",
            "/services/data/{api_version}/appMenu/Salesforce1/",
            "List mobile app menu items",
            write=False,
        ),
    },
    "compact-layouts": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/compactLayouts",
            "List compact layouts for multiple objects",
            write=False,
            query_args=(
                _arg("object-list", help="Comma-separated object names", query_name="q", required=True),
            ),
        ),
    },
    "sobjects-global": {
        "describe": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/",
            "Describe all available sObjects",
            write=False,
        ),
    },
    "sobjects-object": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}",
            "Get basic information for one object",
            write=False,
        ),
        "create": _spec(
            "POST",
            "/services/data/{api_version}/sobjects/{sobject}",
            "Create a record using object basic information resource",
            write=True,
            requires_body_file=True,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/sobjects/{sobject}",
            "Return object basic information headers",
            write=False,
        ),
    },
    "sobjects-describe": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/describe",
            "Describe one object",
            write=False,
        ),
    },
    "sobjects-deleted": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/deleted/",
            "List deleted records for one object",
            write=False,
            query_args=(
                _arg("start", help="Start datetime", query_name="start", required=True),
                _arg("end", help="End datetime", query_name="end", required=True),
            ),
        ),
    },
    "sobjects-updated": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/updated/",
            "List updated records for one object",
            write=False,
            query_args=(
                _arg("start", help="Start datetime", query_name="start", required=True),
                _arg("end", help="End datetime", query_name="end", required=True),
            ),
        ),
    },
    "sobjects-named-layouts": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/describe/namedLayouts/{layout_name}",
            "Get named layout information",
            write=False,
        ),
    },
    "sobjects-row": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/{record_id}",
            "Get one record by ID",
            write=False,
        ),
        "update": _spec(
            "PATCH",
            "/services/data/{api_version}/sobjects/{sobject}/{record_id}",
            "Update one record by ID",
            write=True,
            requires_body_file=True,
        ),
        "delete": _spec(
            "DELETE",
            "/services/data/{api_version}/sobjects/{sobject}/{record_id}",
            "Delete one record by ID",
            write=True,
            require_yes=True,
            require_ack=True,
        ),
    },
    "sobjects-event-series": {
        "delete": _spec(
            "DELETE",
            "/services/data/{api_version}/sobjects/Event/{record_id}/fromThisEventOnwards",
            "Delete one Lightning event series from the chosen occurrence onward",
            write=True,
            require_yes=True,
            require_ack=True,
        ),
    },
    "sobjects-external-id": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/{field_name}/{field_value}",
            "Get one record by external ID",
            write=False,
        ),
        "create": _spec(
            "POST",
            "/services/data/{api_version}/sobjects/{sobject}/{field_name}/{field_value}",
            "Create a record using an external ID path",
            write=True,
            requires_body_file=True,
        ),
        "upsert": _spec(
            "PATCH",
            "/services/data/{api_version}/sobjects/{sobject}/{field_name}/{field_value}",
            "Upsert a record using an external ID path",
            write=True,
            requires_body_file=True,
        ),
        "delete": _spec(
            "DELETE",
            "/services/data/{api_version}/sobjects/{sobject}/{field_name}/{field_value}",
            "Delete a record using an external ID path",
            write=True,
            require_yes=True,
            require_ack=True,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/sobjects/{sobject}/{field_name}/{field_value}",
            "Return external ID response headers",
            write=False,
        ),
    },
    "sobjects-blob": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/{record_id}/{blob_field}",
            "Download one blob field",
            write=False,
            response_kind="binary",
        ),
    },
    "sobjects-approval-layouts": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/describe/approvalLayouts/",
            "List approval layouts",
            write=False,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/sobjects/{sobject}/describe/approvalLayouts/",
            "Return approval layout headers",
            write=False,
        ),
    },
    "sobjects-approval-process": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/describe/approvalLayouts/{approval_process_name}",
            "Get one approval process layout",
            write=False,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/sobjects/{sobject}/describe/approvalLayouts/{approval_process_name}",
            "Return one approval process layout headers",
            write=False,
        ),
    },
    "sobjects-compact-layouts": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/describe/compactLayouts/",
            "List compact layouts for one object",
            write=False,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/sobjects/{sobject}/describe/compactLayouts/",
            "Return compact layout headers",
            write=False,
        ),
    },
    "sobjects-layouts": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/describe/layouts/",
            "List layouts for one object",
            write=False,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/sobjects/{sobject}/describe/layouts/",
            "Return layout headers for one object",
            write=False,
        ),
    },
    "sobjects-layouts-record-type": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/describe/layouts/{record_type_id}",
            "Get one layout by record type",
            write=False,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/sobjects/{sobject}/describe/layouts/{record_type_id}",
            "Return layout headers by record type",
            write=False,
        ),
    },
    "sobjects-global-layouts": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/Global/describe/layouts/",
            "List global publisher layouts",
            write=False,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/sobjects/Global/describe/layouts/",
            "Return global publisher layout headers",
            write=False,
        ),
    },
    "sobjects-platform-actions": {
        "query": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/PlatformAction",
            "Query platform actions",
            write=False,
        ),
    },
    "sobjects-quick-actions": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/quickActions/",
            "List object quick actions",
            write=False,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/sobjects/{sobject}/quickActions/",
            "Return object quick action headers",
            write=False,
        ),
    },
    "sobjects-quick-action": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/quickActions/{action_name}",
            "Get one object quick action",
            write=False,
        ),
        "create": _spec(
            "POST",
            "/services/data/{api_version}/sobjects/{sobject}/quickActions/{action_name}",
            "Execute one object quick action",
            write=True,
            requires_body_file=True,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/sobjects/{sobject}/quickActions/{action_name}",
            "Return one object quick action headers",
            write=False,
        ),
    },
    "sobjects-quick-action-describe": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/quickActions/{action_name}/describe/",
            "Describe one object quick action",
            write=False,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/sobjects/{sobject}/quickActions/{action_name}/describe/",
            "Return object quick action describe headers",
            write=False,
        ),
    },
    "sobjects-quick-action-defaults": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/quickActions/{action_name}/defaultValues/",
            "Get quick action default values",
            write=False,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/sobjects/{sobject}/quickActions/{action_name}/defaultValues/",
            "Return quick action default value headers",
            write=False,
        ),
    },
    "sobjects-quick-action-defaults-context": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/quickActions/{action_name}/defaultValues/{context_id}",
            "Get quick action default values for one context record",
            write=False,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/sobjects/{sobject}/quickActions/{action_name}/defaultValues/{context_id}",
            "Return quick action default value headers for one context record",
            write=False,
        ),
    },
    "sobjects-rich-text-image": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/{record_id}/{field_name}/{content_reference_id}",
            "Download one rich text image",
            write=False,
            response_kind="binary",
            display_path="/services/data/vXX.X/sobjects/sObject/id/richTextImageFields/fieldName/contentReferenceId",
        ),
    },
    "sobjects-relationships": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/{record_id}/{relationship_field_name}",
            "Get a related record by friendly URL",
            write=False,
        ),
        "update": _spec(
            "PATCH",
            "/services/data/{api_version}/sobjects/{sobject}/{record_id}/{relationship_field_name}",
            "Update a related record by friendly URL",
            write=True,
            requires_body_file=True,
        ),
        "delete": _spec(
            "DELETE",
            "/services/data/{api_version}/sobjects/{sobject}/{record_id}/{relationship_field_name}",
            "Delete a related record by friendly URL",
            write=True,
            require_yes=True,
            require_ack=True,
        ),
    },
    "sobjects-suggested-articles": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/suggestedArticles",
            "Get suggested articles for a new record",
            write=False,
            query_args=(
                _arg("language", help="Article language such as en_US", required=True),
                _arg("subject", help="Subject text"),
                _arg("description", help="Description text"),
                _arg("limit", help="Max articles", type_name="int"),
            ),
        ),
    },
    "sobjects-suggested-articles-id": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/{record_id}/suggestedArticles",
            "Get suggested articles for an existing record",
            write=False,
            query_args=(
                _arg("language", help="Article language such as en_US", required=True),
                _arg("limit", help="Max articles", type_name="int"),
            ),
        ),
    },
    "sobjects-user-password": {
        "status": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/User/{user_id}/password",
            "Get a user's password expiration status",
            write=False,
        ),
        "set": _spec(
            "POST",
            "/services/data/{api_version}/sobjects/User/{user_id}/password",
            "Set a user's password",
            write=True,
            requires_body_file=True,
            require_yes=True,
            require_ack=True,
            require_plan_in=True,
        ),
        "reset": _spec(
            "DELETE",
            "/services/data/{api_version}/sobjects/User/{user_id}/password",
            "Reset a user's password",
            write=True,
            require_yes=True,
            require_ack=True,
            require_plan_in=True,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/sobjects/User/{user_id}/password",
            "Return user password headers",
            write=False,
        ),
    },
    "sobjects-self-service-user-password": {
        "status": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/SelfServiceUser/{self_service_user_id}/password",
            "Get a self-service user's password expiration status",
            write=False,
        ),
        "set": _spec(
            "POST",
            "/services/data/{api_version}/sobjects/SelfServiceUser/{self_service_user_id}/password",
            "Set a self-service user's password",
            write=True,
            requires_body_file=True,
            require_yes=True,
            require_ack=True,
            require_plan_in=True,
        ),
        "reset": _spec(
            "DELETE",
            "/services/data/{api_version}/sobjects/SelfServiceUser/{self_service_user_id}/password",
            "Reset a self-service user's password",
            write=True,
            require_yes=True,
            require_ack=True,
            require_plan_in=True,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/sobjects/SelfServiceUser/{self_service_user_id}/password",
            "Return self-service user password headers",
            write=False,
        ),
    },
    "sobjects-relevant-items": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/relevantItems",
            "Get relevant items",
            write=False,
            query_args=(
                _arg("last-updated-id", help="Previous lastUpdatedId", query_name="lastUpdatedId"),
                _arg("sobjects", help="Comma-separated object names"),
            ),
        ),
    },
    "sobjects-lightning-metrics": {
        "toggle": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/LightningToggleMetrics",
            "Get Lightning toggle metrics",
            write=False,
        ),
        "app-type": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/LightningUsageByAppTypeMetrics",
            "Get Lightning usage by app type",
            write=False,
        ),
        "browser": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/LightningUsageByBrowserMetrics",
            "Get Lightning usage by browser",
            write=False,
        ),
        "page": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/LightningUsageByPageMetrics",
            "Get Lightning usage by page",
            write=False,
        ),
        "flexipage": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/LightningUsageByFlexiPageMetrics",
            "Get Lightning usage by FlexiPage",
            write=False,
        ),
        "exit-page": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/LightningExitByPageMetrics",
            "Get Lightning exit by page metrics",
            write=False,
        ),
    },
    "platform-events": {
        "schema-by-name": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{event_name}/eventSchema",
            "Get platform event schema by event name",
            write=False,
            query_args=(
                _arg("payload-format", help="EXPANDED or COMPACT", query_name="payloadFormat", choices=("EXPANDED", "COMPACT")),
            ),
        ),
        "schema-by-id": _spec(
            "GET",
            "/services/data/{api_version}/event/eventSchema/{schema_id}",
            "Get platform event schema by schema ID",
            write=False,
            query_args=(
                _arg("payload-format", help="EXPANDED or COMPACT", query_name="payloadFormat", choices=("EXPANDED", "COMPACT")),
            ),
        ),
    },
    "support": {
        "root": _spec(
            "GET",
            "/services/data/{api_version}/support",
            "Get support resource links",
            write=False,
        ),
        "data-category-groups": _spec(
            "GET",
            "/services/data/{api_version}/support/dataCategoryGroups",
            "List visible data category groups",
            write=False,
        ),
        "data-category-detail": _spec(
            "GET",
            "/services/data/{api_version}/support/dataCategoryGroups/{group_name}/dataCategories/{category_name}",
            "Get one data category branch",
            write=False,
        ),
        "knowledge-articles": _spec(
            "GET",
            "/services/data/{api_version}/support/knowledgeArticles",
            "List Knowledge articles",
            write=False,
        ),
        "knowledge-article": _spec(
            "GET",
            "/services/data/{api_version}/support/knowledgeArticles/{article_key}",
            "Get one Knowledge article by ID or URL name",
            write=False,
        ),
    },
    "knowledge": {
        "settings": _spec(
            "GET",
            "/services/data/{api_version}/knowledgeManagement/settings",
            "Get Knowledge language settings",
            write=False,
        ),
    },
    "consent": {
        "compile": _spec(
            "GET",
            "/services/data/{api_version}/consent/action/{action_name}",
            "Compile consent for one action",
            write=False,
            query_args=(
                _arg("ids", help="Comma-separated record IDs or email addresses", required=True),
            ),
        ),
        "multiaction": _spec(
            "GET",
            "/services/data/{api_version}/consent/multiaction",
            "Compile consent for multiple actions",
            write=False,
            query_args=(
                _arg("actions", help="Comma-separated actions", required=True),
                _arg("ids", help="Comma-separated record IDs or email addresses", required=True),
            ),
        ),
        "data360-read": _spec(
            "GET",
            "/services/data/{api_version}/consent/action/{action_name}",
            "Read Data 360 consent state for processing, portability, or shouldforget",
            write=False,
            query_args=(
                _arg("ids", help="Comma-separated Individual IDs", required=True),
                _arg("mode", help="Use cdp for Data 360", required=True),
            ),
        ),
        "write": _spec(
            "PATCH",
            "/services/data/{api_version}/consent/action/{action_name}",
            "Write consent values",
            write=True,
            requires_body_file=True,
            require_yes=True,
        ),
        "data360-write": _spec(
            "PATCH",
            "/services/data/{api_version}/consent/action/{action_name}",
            "Write Data 360 consent values",
            write=True,
            requires_body_file=True,
            require_yes=True,
            query_args=(
                _arg("ids", help="Comma-separated Individual IDs", required=True),
                _arg("mode", help="Use cdp for Data 360", required=True),
                _arg("status", help="Consent status", required=True),
            ),
        ),
    },
    "embedded-service": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/support/embeddedservice/configuration/{embedded_service_config_developer_name}",
            "Get embedded service configuration",
            write=False,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/support/embeddedservice/configuration/{embedded_service_config_developer_name}",
            "Return embedded service configuration headers",
            write=False,
        ),
    },
    "actions": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/actions",
            "List invocable action resource roots",
            write=False,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/actions",
            "Return invocable action root headers",
            write=False,
        ),
    },
    "actions-custom": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/actions/custom",
            "List custom invocable actions",
            write=False,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/actions/custom",
            "Return custom invocable action headers",
            write=False,
        ),
    },
    "actions-standard": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/actions/standard",
            "List standard invocable actions",
            write=False,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/actions/standard",
            "Return standard invocable action headers",
            write=False,
        ),
    },
    "listviews": {
        "object-list": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/listviews",
            "List list views for one object",
            write=False,
        ),
        "basic": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/listviews/{list_view_id}",
            "Get basic list view information",
            write=False,
        ),
        "describe": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/listviews/{list_view_id}/describe",
            "Describe one list view",
            write=False,
            display_path="/services/data/vXX.X/sobjects/sObject/listviews/queryLocator/describe",
        ),
        "results": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/listviews/{list_view_id}/results",
            "Get one list view result set",
            write=False,
            query_args=(
                _arg("limit", help="Max records", type_name="int"),
                _arg("offset", help="Starting row offset", type_name="int"),
            ),
        ),
        "recent": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/{sobject}/listviews/recent",
            "List recently used list views",
            write=False,
        ),
    },
    "named-query": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/named/query/{named_query_name}",
            "Execute a Named Query API",
            write=False,
        ),
    },
    "portability": {
        "create": _spec(
            "POST",
            "/services/data/{api_version}/consent/dsr/rtp/execute",
            "Compile portability data",
            write=True,
            requires_body_file=True,
            require_yes=True,
        ),
        "status": _spec(
            "GET",
            "/services/data/{api_version}/consent/dsr/rtp/execute",
            "Get portability request status",
            write=False,
            query_args=(
                _arg("policy-file-id", help="Policy file ID", query_name="policyFileId", required=True),
            ),
        ),
    },
    "process-approvals": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/process/approvals/",
            "List approval processes",
            write=False,
        ),
        "act": _spec(
            "POST",
            "/services/data/{api_version}/process/approvals/",
            "Submit, approve, or reject approval items",
            write=True,
            requires_body_file=True,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/process/approvals/",
            "Return approval process headers",
            write=False,
        ),
    },
    "process-rules": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/process/rules/",
            "List active workflow rules",
            write=False,
        ),
        "trigger": _spec(
            "POST",
            "/services/data/{api_version}/process/rules/",
            "Trigger all active workflow rules",
            write=True,
            requires_body_file=True,
            require_yes=True,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/process/rules/",
            "Return workflow rule headers",
            write=False,
        ),
    },
    "process-rule": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/process/rules/{sobject}/{workflow_rule_id}",
            "Get one workflow rule",
            write=False,
        ),
        "trigger": _spec(
            "POST",
            "/services/data/{api_version}/process/rules/{sobject}/{workflow_rule_id}",
            "Trigger one workflow rule",
            write=True,
            require_yes=True,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/process/rules/{sobject}/{workflow_rule_id}",
            "Return one workflow rule headers",
            write=False,
        ),
    },
    "process-object-rules": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/process/rules/{sobject}",
            "List workflow rules for one object",
            write=False,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/process/rules/{sobject}",
            "Return workflow rule headers for one object",
            write=False,
        ),
    },
    "product-schedules": {
        "get": _spec(
            "GET",
            "/services/data/{api_version}/sobjects/OpportunityLineItem/{opportunity_line_item_id}/OpportunityLineItemSchedules",
            "Get product schedules",
            write=False,
        ),
        "create": _spec(
            "PUT",
            "/services/data/{api_version}/sobjects/OpportunityLineItem/{opportunity_line_item_id}/OpportunityLineItemSchedules",
            "Create or reestablish product schedules",
            write=True,
            requires_body_file=True,
            require_yes=True,
        ),
        "delete": _spec(
            "DELETE",
            "/services/data/{api_version}/sobjects/OpportunityLineItem/{opportunity_line_item_id}/OpportunityLineItemSchedules",
            "Delete all product schedules",
            write=True,
            require_yes=True,
            require_ack=True,
        ),
    },
    "quick-actions": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/quickActions/",
            "List global quick actions",
            write=False,
        ),
        "create": _spec(
            "POST",
            "/services/data/{api_version}/quickActions/{action_name}",
            "Execute a global quick action",
            write=True,
            requires_body_file=True,
        ),
        "headers": _spec(
            "HEAD",
            "/services/data/{api_version}/quickActions/",
            "Return global quick action headers",
            write=False,
        ),
    },
    "scheduler": {
        "slots": _spec(
            "POST",
            "/services/data/{api_version}/scheduling/getAppointmentSlots",
            "Get appointment slots",
            write=False,
            requires_body_file=True,
        ),
        "candidates": _spec(
            "POST",
            "/services/data/{api_version}/scheduling/getAppointmentCandidates",
            "Get appointment candidates",
            write=False,
            requires_body_file=True,
        ),
    },
    "surveys-translation": {
        "upsert": _spec(
            "POST",
            "/services/data/{api_version}/localizedvalue/record/{developer_name}/{language}",
            "Add or change one survey translation",
            write=True,
            requires_body_file=True,
        ),
        "get": _spec(
            "GET",
            "/services/data/{api_version}/localizedvalue/record/{developer_name}/{language}",
            "Get one survey translation",
            write=False,
        ),
        "delete": _spec(
            "DELETE",
            "/services/data/{api_version}/localizedvalue/record/{developer_name}/{language}",
            "Delete one survey translation",
            write=True,
            require_yes=True,
            require_ack=True,
        ),
        "upsert-multi": _spec(
            "POST",
            "/services/data/{api_version}/localizedvalue/records/upsert",
            "Add or update many survey translations",
            write=True,
            requires_body_file=True,
            require_yes=True,
        ),
        "delete-multi": _spec(
            "POST",
            "/services/data/{api_version}/localizedvalue/records/delete",
            "Delete many survey translations",
            write=True,
            requires_body_file=True,
            require_yes=True,
            require_ack=True,
        ),
        "get-multi": _spec(
            "POST",
            "/services/data/{api_version}/localizedvalue/records/get",
            "Get many survey translations",
            write=False,
            requires_body_file=True,
        ),
    },
    "composite": {
        "list": _spec(
            "GET",
            "/services/data/{api_version}/composite",
            "List composite resources",
            write=False,
        ),
        "execute": _spec(
            "POST",
            "/services/data/{api_version}/composite",
            "Execute a composite request",
            write=True,
            requires_body_file=True,
            require_yes=True,
        ),
    },
    "composite-graph": {
        "execute": _spec(
            "POST",
            "/services/data/{api_version}/composite/graph",
            "Execute a composite graph request",
            write=True,
            requires_body_file=True,
            require_yes=True,
        ),
    },
    "composite-batch": {
        "execute": _spec(
            "POST",
            "/services/data/{api_version}/composite/batch",
            "Execute a composite batch request",
            write=True,
            requires_body_file=True,
            require_yes=True,
        ),
    },
    "composite-tree": {
        "create": _spec(
            "POST",
            "/services/data/{api_version}/composite/tree/{sobject}",
            "Create an sObject tree",
            write=True,
            requires_body_file=True,
            require_yes=True,
        ),
    },
    "composite-collections": {
        "create": _spec(
            "POST",
            "/services/data/{api_version}/composite/sobjects",
            "Create records with sObject Collections",
            write=True,
            requires_body_file=True,
            require_yes=True,
        ),
        "get": _spec(
            "GET",
            "/services/data/{api_version}/composite/sobjects/{sobject}",
            "Get records with sObject Collections",
            write=False,
            query_args=(
                _arg("ids", help="Comma-separated record IDs", required=True),
            ),
        ),
        "get-body": _spec(
            "POST",
            "/services/data/{api_version}/composite/sobjects/{sobject}",
            "Get records with sObject Collections request body",
            write=False,
            requires_body_file=True,
        ),
        "update": _spec(
            "PATCH",
            "/services/data/{api_version}/composite/sobjects",
            "Update records with sObject Collections",
            write=True,
            requires_body_file=True,
            require_yes=True,
        ),
        "upsert": _spec(
            "PATCH",
            "/services/data/{api_version}/composite/sobjects/{sobject}/{external_id_field_name}",
            "Upsert records with sObject Collections",
            write=True,
            requires_body_file=True,
            require_yes=True,
        ),
        "delete": _spec(
            "DELETE",
            "/services/data/{api_version}/composite/sobjects",
            "Delete records with sObject Collections",
            write=True,
            require_yes=True,
            require_ack=True,
            query_args=(
                _arg("ids", help="Comma-separated record IDs", required=True),
            ),
        ),
    },
    "jobs-ingest": {
        "create": _spec(
            "POST",
            "/services/data/{api_version}/jobs/ingest",
            "Create a Bulk API 2.0 ingest job",
            write=True,
            requires_body_file=True,
            require_yes=True,
        ),
        "upload": _spec(
            "PUT",
            "/services/data/{api_version}/jobs/ingest/{job_id}/batches",
            "Upload CSV data for an ingest job",
            write=True,
            requires_data_file=True,
            content_type="text/csv",
            response_kind="none",
            require_yes=True,
        ),
        "upload-complete": _spec(
            "PATCH",
            "/services/data/{api_version}/jobs/ingest/{job_id}",
            "Mark an ingest job UploadComplete",
            write=True,
            require_yes=True,
            fixed_json_body={"state": "UploadComplete"},
        ),
        "get": _spec(
            "GET",
            "/services/data/{api_version}/jobs/ingest/{job_id}",
            "Get ingest job information",
            write=False,
        ),
        "successful-results": _spec(
            "GET",
            "/services/data/{api_version}/jobs/ingest/{job_id}/successfulResults/",
            "Download successful ingest rows",
            write=False,
            response_kind="csv",
            accept="text/csv",
        ),
        "failed-results": _spec(
            "GET",
            "/services/data/{api_version}/jobs/ingest/{job_id}/failedResults/",
            "Download failed ingest rows",
            write=False,
            response_kind="csv",
            accept="text/csv",
        ),
        "unprocessed": _spec(
            "GET",
            "/services/data/{api_version}/jobs/ingest/{job_id}/unprocessedrecords/",
            "Download unprocessed ingest rows",
            write=False,
            response_kind="csv",
            accept="text/csv",
        ),
        "delete": _spec(
            "DELETE",
            "/services/data/{api_version}/jobs/ingest/{job_id}",
            "Delete an ingest job",
            write=True,
            require_yes=True,
            require_ack=True,
        ),
        "abort": _spec(
            "PATCH",
            "/services/data/{api_version}/jobs/ingest/{job_id}",
            "Abort an ingest job",
            write=True,
            require_yes=True,
            fixed_json_body={"state": "Aborted"},
        ),
        "list": _spec(
            "GET",
            "/services/data/{api_version}/jobs/ingest",
            "List ingest jobs",
            write=False,
            query_args=(
                _arg("is-pk-chunking-enabled", help="Filter jobs with PK chunking", query_name="isPkChunkingEnabled", type_name="bool"),
                _arg("job-type", help="Classic, BigObjectIngest, or V2Ingest", query_name="jobType"),
                _arg("query-locator", help="Next page locator", query_name="queryLocator"),
            ),
        ),
    },
    "jobs-query": {
        "create": _spec(
            "POST",
            "/services/data/{api_version}/jobs/query",
            "Create a Bulk API 2.0 query job",
            write=True,
            requires_body_file=True,
            require_yes=True,
        ),
        "get": _spec(
            "GET",
            "/services/data/{api_version}/jobs/query/{job_id}",
            "Get query job information",
            write=False,
        ),
        "results": _spec(
            "GET",
            "/services/data/{api_version}/jobs/query/{job_id}/results",
            "Download query job results",
            write=False,
            response_kind="csv",
            accept="text/csv",
            query_args=(
                _arg("locator", help="Result locator"),
                _arg("max-records", help="Max records per chunk", query_name="maxRecords", type_name="int"),
            ),
        ),
        "result-pages": _spec(
            "GET",
            "/services/data/{api_version}/jobs/query/{job_id}/resultPages",
            "List query job result page URIs",
            write=False,
        ),
        "delete": _spec(
            "DELETE",
            "/services/data/{api_version}/jobs/query/{job_id}",
            "Delete a query job",
            write=True,
            require_yes=True,
            require_ack=True,
        ),
        "abort": _spec(
            "PATCH",
            "/services/data/{api_version}/jobs/query/{job_id}",
            "Abort a query job",
            write=True,
            require_yes=True,
            fixed_json_body={"state": "Aborted"},
        ),
        "list": _spec(
            "GET",
            "/services/data/{api_version}/jobs/query",
            "List query jobs",
            write=False,
            query_args=(
                _arg("is-pk-chunking-enabled", help="Filter classic jobs with PK chunking", query_name="isPkChunkingEnabled", type_name="bool"),
                _arg("job-type", help="Classic, V2Query, or V2Ingest", query_name="jobType"),
                _arg("concurrency-mode", help="parallel or serial", query_name="concurrencyMode"),
                _arg("query-locator", help="Next page locator", query_name="queryLocator"),
            ),
        ),
    },
}


def actions() -> dict[str, dict[str, ActionSpec]]:
    return _ACTIONS


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _path_names(path: str) -> list[str]:
    return [name for name in _PATH_RE.findall(path) if name != "api_version"]


def _body_sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _merge_param(params: dict[str, Any], name: str, value: Any) -> None:
    if value is None:
        return
    if isinstance(value, bool):
        params[name] = "true" if value else "false"
        return
    existing = params.get(name)
    if existing is None:
        params[name] = value
        return
    if isinstance(existing, list):
        existing.append(value)
        return
    params[name] = [existing, value]


def _coerce_cli_arg(spec: CliArgSpec, value: Any) -> Any:
    if value is None:
        return None
    if spec.type_name == "bool":
        return bool(value)
    return value


def _read_input_file(path_value: str) -> bytes:
    path = Path(path_value).expanduser()
    if not path.exists():
        raise ValidationError(f"Multipart source file not found: {path}")
    return path.read_bytes()


def _guess_content_type(*, filename: str | None, fallback: str) -> str:
    if filename:
        guessed, _ = mimetypes.guess_type(filename)
        if guessed:
            return guessed
    return fallback


def _load_multipart_payload(args: Any, *, family: str, action: str) -> tuple[Any, bytes, str, Path, str]:
    if (family, action) not in _MULTIPART_ALLOWED:
        raise ValidationError(f"--multipart-file is not supported for {family} {action}")

    manifest_path = Path(str(args.multipart_file)).expanduser()
    manifest_obj = read_json_file(manifest_path)
    if not isinstance(manifest_obj, dict):
        raise ValidationError("Multipart manifest must be a JSON object")

    raw_parts = manifest_obj.get("parts")
    if not isinstance(raw_parts, list) or not raw_parts:
        raise ValidationError("Multipart manifest must contain a non-empty parts list")

    prepared_parts: list[tuple[dict[str, Any], bytes]] = []
    summary_parts: list[dict[str, Any]] = []
    boundary_seed: list[dict[str, Any]] = []

    for index, raw_part in enumerate(raw_parts, start=1):
        if not isinstance(raw_part, dict):
            raise ValidationError(f"Multipart part #{index} must be a JSON object")
        name = str(raw_part.get("name") or "").strip()
        if not name:
            raise ValidationError(f"Multipart part #{index} is missing a non-empty name")

        source_keys = [key for key in ("json_body", "json_file", "text", "text_file", "file") if key in raw_part]
        if len(source_keys) != 1:
            raise ValidationError(
                f"Multipart part {name!r} must define exactly one source: json_body, json_file, text, text_file, or file"
            )
        source_key = source_keys[0]

        filename = raw_part.get("filename")
        if filename is not None:
            filename = str(filename)

        if source_key == "json_body":
            content_bytes = json.dumps(raw_part["json_body"], ensure_ascii=False).encode("utf-8")
            content_type = str(raw_part.get("content_type") or "application/json")
            source_ref = "<inline-json>"
        elif source_key == "json_file":
            source_ref = str(raw_part["json_file"])
            json_obj = read_json_file(source_ref)
            content_bytes = json.dumps(json_obj, ensure_ascii=False).encode("utf-8")
            content_type = str(raw_part.get("content_type") or "application/json")
            if not filename:
                filename = Path(source_ref).name
        elif source_key == "text":
            source_ref = "<inline-text>"
            content_bytes = str(raw_part["text"]).encode("utf-8")
            content_type = str(raw_part.get("content_type") or "text/plain; charset=utf-8")
        elif source_key == "text_file":
            source_ref = str(raw_part["text_file"])
            content_bytes = _read_input_file(source_ref)
            content_type = str(raw_part.get("content_type") or "text/plain; charset=utf-8")
            if not filename:
                filename = Path(source_ref).name
        else:
            source_ref = str(raw_part["file"])
            content_bytes = _read_input_file(source_ref)
            content_type = str(
                raw_part.get("content_type")
                or _guess_content_type(filename=filename or Path(source_ref).name, fallback="application/octet-stream")
            )
            if not filename:
                filename = Path(source_ref).name

        sha256 = _body_sha256_bytes(content_bytes)
        summary_part = {
            "name": name,
            "filename": filename,
            "content_type": content_type,
            "bytes": len(content_bytes),
            "sha256": sha256,
            "source": source_ref,
        }
        summary_parts.append(summary_part)
        boundary_seed.append({k: summary_part[k] for k in ("name", "filename", "content_type", "sha256")})
        prepared_parts.append((summary_part, content_bytes))

    boundary = str(manifest_obj.get("boundary") or "")
    if not boundary:
        raw_seed = json.dumps(boundary_seed, ensure_ascii=False, sort_keys=True).encode("utf-8")
        boundary = "qwayk-" + hashlib.sha256(raw_seed).hexdigest()[:24]

    body_chunks: list[bytes] = []
    boundary_bytes = boundary.encode("utf-8")
    for part_summary, content_bytes in prepared_parts:
        body_chunks.append(b"--" + boundary_bytes + b"\r\n")
        disposition = f'Content-Disposition: form-data; name="{part_summary["name"]}"'
        filename = part_summary.get("filename")
        if filename:
            disposition += f'; filename="{filename}"'
        body_chunks.append(disposition.encode("utf-8") + b"\r\n")
        body_chunks.append(f'Content-Type: {part_summary["content_type"]}'.encode("utf-8") + b"\r\n\r\n")
        body_chunks.append(content_bytes)
        body_chunks.append(b"\r\n")
    body_chunks.append(b"--" + boundary_bytes + b"--\r\n")
    body_bytes = b"".join(body_chunks)

    summary = {
        "multipart": True,
        "manifest_path": str(manifest_path),
        "parts": summary_parts,
    }
    return summary, body_bytes, f"multipart/form-data; boundary={boundary}", manifest_path, _body_sha256_bytes(body_bytes)


def _parse_kv_items(items: list[str], *, label: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for raw in items:
        candidate = str(raw or "").strip()
        if not candidate:
            continue
        if "=" not in candidate:
            raise ValidationError(f"Invalid {label}: expected key=value, got {candidate!r}")
        key, value = candidate.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValidationError(f"Invalid {label}: missing key in {candidate!r}")
        _merge_param(out, key, value)
    return out


def _normalize_headers(
    items: list[str],
    *,
    spec: ActionSpec,
    content_type_override: str | None = None,
) -> dict[str, str]:
    extra = _parse_kv_items(items, label="--header")
    out: dict[str, str] = {}
    for key, value in extra.items():
        if isinstance(value, list):
            raise ValidationError(f"Duplicate header is not supported: {key}")
        lk = key.lower()
        if lk in {"authorization", "content-type", "accept"}:
            raise ValidationError(f"Do not pass {key}; this tool manages it directly")
        out[key] = str(value)
    if spec.accept:
        out["Accept"] = spec.accept
    elif spec.response_kind == "csv":
        out["Accept"] = "text/csv"
    elif spec.response_kind == "binary":
        out["Accept"] = "*/*"
    else:
        out["Accept"] = "application/json"
    if content_type_override:
        out["Content-Type"] = content_type_override
    elif spec.content_type:
        out["Content-Type"] = spec.content_type
    elif spec.requires_body_file or spec.fixed_json_body is not None:
        out["Content-Type"] = "application/json"
    return out


def _redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        safe: dict[str, Any] = {}
        for key, value in obj.items():
            if _SENSITIVE_KEY_RE.search(str(key)):
                safe[key] = "***REDACTED***"
            else:
                safe[key] = _redact(value)
        return safe
    if isinstance(obj, list):
        return [_redact(v) for v in obj]
    return obj


def _response_summary(resp: HttpResponse, *, response_kind: str, download_to: str | None) -> dict[str, Any]:
    headers = {
        name: value
        for name, value in resp.headers.items()
        if name in {"content-type", "sforce-limit-info", "sforce-locator", "sforce-numberofrecords"}
    }
    if download_to:
        dest = Path(download_to)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(resp.body)
        return {
            "status": resp.status,
            "url": resp.url,
            "headers": headers,
            "downloaded_to": str(dest),
            "bytes": len(resp.body),
        }
    if response_kind == "none" or resp.status == 204:
        return {"status": resp.status, "url": resp.url, "headers": headers}
    if response_kind == "binary":
        return {
            "status": resp.status,
            "url": resp.url,
            "headers": headers,
            "body_base64": base64.b64encode(resp.body).decode("ascii"),
            "bytes": len(resp.body),
        }
    content_type = resp.headers.get("content-type", "")
    if "application/json" in content_type:
        return {"status": resp.status, "url": resp.url, "headers": headers, "body": resp.json()}
    if not resp.body:
        return {"status": resp.status, "url": resp.url, "headers": headers}
    return {"status": resp.status, "url": resp.url, "headers": headers, "body_text": resp.text()}


def _canonical_request_fingerprint(
    *,
    method: str,
    path: str,
    params: dict[str, Any],
    body_sha256: str | None,
    data_sha256: str | None,
) -> str:
    payload = {
        "method": method,
        "path": path,
        "params": params,
        "body_sha256": body_sha256,
        "data_sha256": data_sha256,
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _no_recovery_contract() -> dict[str, Any]:
    return {
        "automatic_rollback": False,
        "backups": [],
        "snapshots": [],
        "rollback_plan": None,
        "restore_note": "No automatic rollback, snapshots, or backups are created. If a restore action is available, run a separate explicit restore command as its own command.",
    }


def _before_state_contract(spec: ActionSpec) -> dict[str, Any]:
    if not spec.write:
        return {
            "required": False,
            "supported": False,
            "status": "not-required",
            "notes": "This is a read or read-like operation, so no before-state capture is required.",
        }
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "notes": (
            "This Salesforce command has no reliable generic before-state snapshot. "
            "Apply may continue only after explicit no-snapshot approval."
        ),
    }


def _verification_plan(spec: ActionSpec) -> dict[str, Any]:
    if spec.write:
        return {
            "type": "best_effort_after_apply",
            "expected_outcome": "provider-response-recorded",
            "notes": "Record the Salesforce API response and explicit no-snapshot approval in the receipt.",
        }
    return {
        "type": "response-check",
        "notes": "Capture the API response and review the returned Salesforce data.",
    }


def _require_no_snapshot_approval(ctx: dict[str, Any]) -> None:
    if bool(ctx.get("ack_no_snapshot")):
        return
    raise SafetyError(_BEFORE_STATE_REFUSAL_REASON)


def _build_plan(
    *,
    spec: ActionSpec,
    args: Any,
    ctx: dict[str, Any],
    path: str,
    params: dict[str, Any],
    body_obj: Any,
    body_sha256: str | None,
    data_file: Path | None,
    data_sha256: str | None,
    headers: dict[str, str],
) -> dict[str, Any]:
    reasons: list[str] = []
    if spec.method in {"DELETE"}:
        reasons.append("delete")
    if spec.require_yes:
        reasons.append("bulk-or-operational-write")
    if spec.require_ack:
        reasons.append("irreversible")
    if spec.method in {"POST", "PATCH", "PUT"}:
        reasons.append("write")
    risk_level = "high" if spec.require_ack or spec.require_yes else "medium"
    if spec.method == "POST" and not spec.require_yes and not spec.require_ack:
        risk_level = "medium"
    selector = {"family": args.salesforce_family, "action": args.salesforce_action, "path": path}
    return {
        "tool": ctx["tool"],
        "version": ctx["tool_version"],
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].instance_url,
        "command": ctx["command_str"],
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": reasons or ["write"],
        "request": {
            "method": spec.method,
            "path": path,
            "params": params,
            "headers": _redact(headers),
            "body": _redact(body_obj),
            "data_file": str(data_file) if data_file else None,
            "data_sha256": data_sha256,
        },
        "baseline": {
            "env_fingerprint": ctx["cfg"].instance_url,
            "request_fingerprint": _canonical_request_fingerprint(
                method=spec.method,
                path=path,
                params=params,
                body_sha256=body_sha256,
                data_sha256=data_sha256,
            ),
        },
        "before_state": _before_state_contract(spec),
        "verification_plan": _verification_plan(spec),
        "rollback": {
            "supported": False,
            "notes": "No automatic rollback is available in this CLI. It does not create snapshots, backups, or a generated rollback plan.",
        },
        "recovery": _no_recovery_contract(),
    }


def _validate_plan_for_apply(plan_obj: dict[str, Any], *, ctx: dict[str, Any], fingerprint: str) -> None:
    baseline = plan_obj.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan file missing baseline object")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].instance_url):
        raise SafetyError("Refused: plan env_fingerprint does not match the current Salesforce instance")
    if str(baseline.get("request_fingerprint") or "") != fingerprint:
        raise SafetyError("Refused: request drift detected between plan and apply inputs")


def _build_path(spec: ActionSpec, *, args: Any, api_version: str) -> str:
    values: dict[str, Any] = {"api_version": f"v{api_version}"}
    for name in _path_names(spec.path):
        value = getattr(args, name, None)
        if value is None or str(value).strip() == "":
            raise ValidationError(f"Missing required path argument --{name.replace('_', '-')}")
        values[name] = str(value)
    return spec.path.format(**values)


def _collect_query_params(spec: ActionSpec, args: Any) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for arg in spec.query_args:
        value = getattr(args, arg.name.replace("-", "_"), None)
        value = _coerce_cli_arg(arg, value)
        if arg.type_name == "bool" and value is False:
            continue
        if arg.required and (value is None or value == "" or value == []):
            raise ValidationError(f"Missing required argument --{arg.name}")
        if value in (None, "", []):
            continue
        target = arg.query_name or arg.name.replace("-", "_")
        if arg.multiple and isinstance(value, list):
            for item in value:
                _merge_param(params, target, item)
            continue
        _merge_param(params, target, value)
    extra = _parse_kv_items(getattr(args, "query_param", []) or [], label="--query-param")
    for name, value in extra.items():
        if isinstance(value, list):
            for item in value:
                _merge_param(params, name, item)
        else:
            _merge_param(params, name, value)
    return params


def _load_body(spec: ActionSpec, args: Any) -> tuple[Any, str | None]:
    if spec.fixed_json_body is not None:
        raw = json.dumps(spec.fixed_json_body, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return spec.fixed_json_body, _body_sha256_bytes(raw)
    if not spec.requires_body_file:
        return None, None
    body_file = getattr(args, "body_file", None)
    if not body_file:
        if getattr(args, "multipart_file", None):
            return None, None
        raise ValidationError("Missing required argument --body-file")
    body = read_json_file(body_file)
    raw = json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return body, _body_sha256_bytes(raw)


def _load_data_file(spec: ActionSpec, args: Any) -> tuple[bytes | None, Path | None, str | None]:
    if not spec.requires_data_file:
        return None, None, None
    path = Path(args.data_file)
    if not path.exists():
        raise ValidationError(f"Data file not found: {path}")
    data = path.read_bytes()
    return data, path, _sha256_file(path)


def _build_client(ctx: dict[str, Any]) -> HttpClient:
    return HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent=_USER_AGENT,
    )


def cmd_salesforce_api(args: Any, ctx: dict[str, Any]) -> int:
    family = str(getattr(args, "salesforce_family", "") or "")
    action = str(getattr(args, "salesforce_action", "") or "")
    spec = _ACTIONS[family][action]

    cfg = ctx["cfg"]
    if not cfg.instance_url:
        raise ValidationError("Missing SALESFORCE_INSTANCE_URL")
    if spec.auth_required and not cfg.token:
        raise ValidationError("Missing Salesforce access token. Set SALESFORCE_ACCESS_TOKEN or use auth token set.")

    path = _build_path(spec, args=args, api_version=cfg.api_version)
    params = _collect_query_params(spec, args)
    body_obj, body_sha256 = _load_body(spec, args)
    data_bytes, data_file, data_sha256 = _load_data_file(spec, args)
    request_json_body = body_obj
    request_data = data_bytes
    content_type_override = None

    multipart_file = str(getattr(args, "multipart_file", "") or "").strip()
    if multipart_file:
        if body_obj is not None:
            raise ValidationError("Do not combine --multipart-file with --body-file")
        if data_bytes is not None:
            raise ValidationError("Do not combine --multipart-file with --data-file")
        multipart_summary, multipart_bytes, content_type_override, manifest_path, multipart_sha256 = _load_multipart_payload(
            args,
            family=family,
            action=action,
        )
        body_obj = multipart_summary
        body_sha256 = multipart_sha256
        request_json_body = None
        request_data = multipart_bytes
        data_file = manifest_path
        data_sha256 = _sha256_file(manifest_path)

    if family == "sobjects-suggested-articles" and not (params.get("subject") or params.get("description")):
        raise ValidationError("Suggested articles requires at least one of --subject or --description")

    headers = _normalize_headers(getattr(args, "header", []) or [], spec=spec, content_type_override=content_type_override)
    if cfg.token:
        headers["Authorization"] = f"Bearer {cfg.token}"

    fingerprint = _canonical_request_fingerprint(
        method=spec.method,
        path=path,
        params=params,
        body_sha256=body_sha256,
        data_sha256=data_sha256,
    )

    if spec.write and not bool(ctx.get("apply")):
        plan = _build_plan(
            spec=spec,
            args=args,
            ctx=ctx,
            path=path,
            params=params,
            body_obj=body_obj,
            body_sha256=body_sha256,
            data_file=data_file,
            data_sha256=data_sha256,
            headers=headers,
        )
        plan_out = ctx.get("plan_out")
        plan_path = write_json_file(plan_out, plan) if plan_out else None
        payload = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(f"{family}.{action}.plan", {"plan_out": plan_path, "path": path})
        ctx["out"].emit(payload)
        return 0

    if spec.write:
        if spec.require_yes and not bool(ctx.get("yes")):
            raise SafetyError(f"Refused: {family} {action} requires --apply --yes")
        if spec.require_ack and not bool(ctx.get("ack_irreversible")):
            raise SafetyError(f"Refused: {family} {action} requires --ack-irreversible")
        if spec.require_plan_in and not ctx.get("plan_in"):
            raise SafetyError(f"Refused: {family} {action} requires --plan-in for apply")
        if ctx.get("plan_in"):
            plan_obj = read_json_file(ctx["plan_in"])
            if not isinstance(plan_obj, dict):
                raise ValidationError("Plan file must be a JSON object")
            _validate_plan_for_apply(plan_obj, ctx=ctx, fingerprint=fingerprint)
        _require_no_snapshot_approval(ctx)

    client = _build_client(ctx)
    response = client.request(
        spec.method,
        cfg.instance_url.rstrip("/") + path,
        headers=headers,
        params=params or None,
        json_body=request_json_body,
        data=request_data,
    )
    response_summary = _response_summary(
        response,
        response_kind=spec.response_kind,
        download_to=getattr(args, "download_to", None),
    )

    if not spec.write:
        payload = {"ok": True, "request": {"method": spec.method, "path": path, "params": params}, "response": response_summary}
        ctx["audit"].write(f"{family}.{action}.read", {"path": path, "status": response.status})
        ctx["out"].emit(payload)
        return 0

    receipt = {
        "tool": ctx["tool"],
        "version": ctx["tool_version"],
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].instance_url,
        "command": ctx["command_str"],
        "selector": {"family": family, "action": action, "path": path},
        "request": {
            "method": spec.method,
            "path": path,
            "params": params,
            "headers": _redact(headers),
            "body": _redact(body_obj),
            "data_file": str(data_file) if data_file else None,
            "data_sha256": data_sha256,
        },
        "risk_level": "high" if spec.require_ack or spec.require_yes else "medium",
        "before_state": _before_state_contract(spec),
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable generic before-state snapshot is available for this Salesforce command.",
        },
        "changed": 200 <= int(response.status) < 300,
        "response": response_summary,
        "verification": {
            "ok": 200 <= int(response.status) < 300,
            "mode": "provider-response",
            "details": {"status": response.status},
        },
        "recovery": _no_recovery_contract(),
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    payload = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(f"{family}.{action}.apply", {"path": path, "status": response.status, "receipt_out": receipt_path})
    ctx["out"].emit(payload)
    return 0

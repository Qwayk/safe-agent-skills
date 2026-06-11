from __future__ import annotations

from pathlib import Path
from typing import Any

from ..api_client import GoogleBusinessProfileApiClient
from ..api_client import ACCOUNT_MANAGEMENT_HOST
from ..api_client import BUSINESS_INFORMATION_HOST
from ..json_files import read_json_file
from .business_info import (
    _build_plan,
    _build_receipt,
    _emit_write_output,
    _optional_text,
    _require_matching_plan_in,
    _write_plan_if_needed,
    _write_receipt_if_needed,
)
from ..errors import SafetyError
from ..errors import ValidationError


_CREATE_ACCOUNT_REQUIRED_FIELDS = {"accountName", "primaryOwner", "type"}
_CREATE_ACCOUNT_ALLOWED_FIELDS = set(_CREATE_ACCOUNT_REQUIRED_FIELDS)
_ALLOWED_PATCH_FIELDS = {"accountName", "name"}
_ALLOWED_PATCH_MASKS = {"accountName"}
_ALLOWED_CREATE_ACCOUNT_TYPES = {"LOCATION_GROUP", "USER_GROUP"}
_CREATE_ACCOUNT_ADMIN_REQUIRED_FIELDS = {"admin", "role"}
_CREATE_ACCOUNT_ADMIN_ALLOWED_FIELDS = {"admin", "role"}
_ALLOWED_ACCOUNT_ADMIN_PATCH_MASKS = {"role"}
_ALLOWED_ACCOUNT_ADMIN_PATCH_FIELDS = {"role", "name"}
_SUPPORTED_ACCOUNT_ADMIN_ROLES = {"OWNER", "MANAGER"}
_CREATE_LOCATION_ADMIN_REQUIRED_FIELDS = {"role"}
_ALLOWED_LOCATION_ADMIN_CREATE_FIELDS = {"admin", "account", "role"}
_ALLOWED_LOCATION_ADMIN_PATCH_FIELDS = {"role", "name"}
_ALLOWED_LOCATION_ADMIN_PATCH_MASKS = {"role"}
_SUPPORTED_LOCATION_ADMIN_ROLES = {"OWNER", "MANAGER", "SITE_MANAGER"}
_LOCATION_TRANSFER_READ_MASK = "name"
_LOCATION_TRANSFER_PAGE_SIZE = 200
_LOCATION_TRANSFER_PLAN_MASK = "name,source_account,destination_account"


def _normalize_account_parent(value: str) -> str:
    parts = [part.strip() for part in value.strip().strip("/").split("/") if part.strip()]
    if len(parts) != 2 or parts[0] != "accounts":
        raise ValidationError("--parent must be in accounts/{account} format.")
    return f"{parts[0]}/{parts[1]}"


def _normalize_account_name_for_transfer(value: str, *, arg_name: str) -> str:
    parts = [part.strip() for part in value.strip().strip("/").split("/") if part.strip()]
    if len(parts) != 2 or parts[0] != "accounts":
        raise ValidationError(f"{arg_name} must be in accounts/{'{'}account{'}'} format.")
    return f"{parts[0]}/{parts[1]}"


def _normalize_location_parent(value: str) -> str:
    parts = [part.strip() for part in value.strip().strip("/").split("/") if part.strip()]
    if len(parts) != 2 or parts[0] != "locations":
        raise ValidationError("--parent must be in locations/{location} format.")
    return f"{parts[0]}/{parts[1]}"


def _normalize_location_name(value: str) -> str:
    parts = [part.strip() for part in value.strip().strip("/").split("/") if part.strip()]
    if len(parts) != 2 or parts[0] != "locations":
        raise ValidationError("--name must be in locations/{location} format.")
    return f"{parts[0]}/{parts[1]}"


def _location_present_in_account(
    *,
    client: GoogleBusinessProfileApiClient,
    account_name: str,
    location_name: str,
) -> tuple[dict[str, Any], bool | None]:
    page_token = None
    request = {
        "operation": "business-info.accounts.locations.list",
        "method": "GET",
        "host": BUSINESS_INFORMATION_HOST,
        "path": f"v1/{account_name}/locations",
        "params": {
            "readMask": _LOCATION_TRANSFER_READ_MASK,
            "pageSize": _LOCATION_TRANSFER_PAGE_SIZE,
        },
    }

    while True:
        try:
            response, request = client.list_business_info_locations(
                parent=account_name,
                read_mask=_LOCATION_TRANSFER_READ_MASK,
                page_size=_LOCATION_TRANSFER_PAGE_SIZE,
                page_token=page_token,
                filter=None,
                order_by=None,
            )
        except Exception as exc:  # noqa: BLE001
            return (
                {
                    "ok": False,
                    "operation": "business-info.accounts.locations.list",
                    "request": request,
                    "response": {
                        "request_error": True,
                        "error_type": type(exc).__name__,
                        "message": str(exc),
                    },
                    "note": f"Could not read location list for {account_name}.",
                },
                None,
            )

        items = response.get("locations")
        if not isinstance(items, list):
            return (
                {
                    "ok": False,
                    "operation": "business-info.accounts.locations.list",
                    "request": request,
                    "response": response,
                    "note": (
                        f"Could not verify location presence because {account_name} location list is malformed."
                    ),
                },
                None,
            )

        for item in items:
            if not isinstance(item, dict):
                continue
            if str(item.get("name") or "").strip() == location_name:
                return (
                    {
                        "ok": True,
                        "operation": "business-info.accounts.locations.list",
                        "request": request,
                        "response": response,
                    },
                    True,
                )

        page_token = str(response.get("nextPageToken") or "").strip() or None
        if not page_token:
            return (
                {
                    "ok": True,
                    "operation": "business-info.accounts.locations.list",
                    "request": request,
                    "response": response,
                },
                False,
            )


def _client_for_ctx(ctx: dict[str, Any]) -> GoogleBusinessProfileApiClient:
    return GoogleBusinessProfileApiClient(
        cfg=ctx["cfg"],
        env_file=ctx["env_file"],
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx["verbose"]),
        ack_no_snapshot=bool(ctx.get("ack_no_snapshot")),
    )


def _emit(ctx: dict[str, Any], operation: str, request: dict[str, Any], response: dict[str, Any]) -> int:
    payload = {
        "ok": True,
        "operation": operation,
        "request": request,
        "response": response,
    }
    ctx["audit"].write(f"api.{operation}", payload)
    ctx["out"].emit(payload)
    return 0


def _require_resource(value: object, *, arg_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValidationError(f"{arg_name} is required and must not be blank.")
    return text


def _normalize_mask(value: str) -> str:
    parts = [part.strip() for part in value.split(",")]
    return ",".join(part for part in parts if part)


def _validate_json_account_file(path: str, *, label: str) -> dict[str, Any]:
    data = read_json_file(path)
    if not isinstance(data, dict):
        raise ValidationError(f"{label} file must be a JSON object: {Path(path)}")
    if not data:
        raise ValidationError(f"{label} file must not be empty: {Path(path)}")
    return data


def _require_scalar_text(value: Any, *, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValidationError(f"{field_name} must be a non-empty string.")
    return text


def _validate_create_account_payload(payload: dict[str, Any], *, account_file: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError(f"Account file must be a JSON object: {Path(account_file)}")

    keys = set(payload.keys())
    extra_keys = sorted(keys.difference(_CREATE_ACCOUNT_ALLOWED_FIELDS))
    if extra_keys:
        raise ValidationError(
            "Account create payload contains unsupported fields for this CLI: "
            + ", ".join(extra_keys)
        )

    missing = sorted(_CREATE_ACCOUNT_REQUIRED_FIELDS.difference(keys))
    if missing:
        raise ValidationError(
            "Account create payload is missing required fields: " + ", ".join(missing)
        )

    account_name = _require_scalar_text(payload["accountName"], field_name="accountName")
    primary_owner = _require_scalar_text(payload["primaryOwner"], field_name="primaryOwner")
    if not primary_owner.startswith("accounts/"):
        raise ValidationError("primaryOwner must be a resource name like accounts/{account_id}.")

    account_type = _require_scalar_text(payload["type"], field_name="type").upper()
    if account_type not in _ALLOWED_CREATE_ACCOUNT_TYPES:
        raise ValidationError(
            f"Cannot create account type '{payload['type']}'. "
            "Use LOCATION_GROUP or USER_GROUP."
        )

    return {
        "accountName": account_name,
        "primaryOwner": primary_owner,
        "type": account_type,
    }


def _validate_role_in_slice(role_value: str, *, context: str) -> str:
    role = role_value.strip().upper()
    if not role:
        raise ValidationError(f"{context} must be a non-empty string.")
    if role not in _SUPPORTED_ACCOUNT_ADMIN_ROLES:
        raise ValidationError(
            "Unsupported admin role. This slice supports only OWNER and MANAGER for account admins."
        )
    return role


def _validate_account_admin_email(value: str) -> str:
    admin_email = value.strip()
    if not admin_email:
        raise ValidationError("admin must be a non-empty string.")
    if "@" not in admin_email or admin_email.startswith("accounts/"):
        raise ValidationError(
            "admin must be the invitee email address for account-management accounts admins create."
        )
    return admin_email


def _validate_create_account_admin_payload(
    payload: dict[str, Any], *, admin_file: str
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError(f"Account admin file must be a JSON object: {Path(admin_file)}")
    if not payload:
        raise ValidationError(f"Account admin file must not be empty: {Path(admin_file)}")

    keys = set(payload.keys())
    extra_keys = sorted(keys.difference(_CREATE_ACCOUNT_ADMIN_ALLOWED_FIELDS))
    if extra_keys:
        raise ValidationError(
            "Account admin create payload contains unsupported fields for this CLI: "
            + ", ".join(extra_keys)
        )

    missing = sorted(_CREATE_ACCOUNT_ADMIN_REQUIRED_FIELDS.difference(keys))
    if missing:
        raise ValidationError(
            "Account admin create payload is missing required fields: " + ", ".join(missing)
        )

    admin = _validate_account_admin_email(_require_scalar_text(payload["admin"], field_name="admin"))
    role = _validate_role_in_slice(_require_scalar_text(payload["role"], field_name="role"), context="role")
    return {"admin": admin, "role": role}


def _validate_account_resource(value: str, *, field_name: str) -> str:
    account = _require_scalar_text(value, field_name=field_name)
    parts = [part.strip() for part in account.split("/") if part.strip()]
    if len(parts) != 2 or parts[0] != "accounts":
        raise ValidationError(f"{field_name} must be a resource name like accounts/{{account_id}}.")
    return f"{parts[0]}/{parts[1]}"


def _validate_location_admin_role(role_value: str) -> str:
    role = role_value.strip().upper()
    if not role:
        raise ValidationError("role must be a non-empty string.")
    if role == "PRIMARY_OWNER" or role == "ADMIN_ROLE_UNSPECIFIED":
        raise ValidationError(
            "Unsupported admin role. This slice rejects PRIMARY_OWNER and ADMIN_ROLE_UNSPECIFIED."
        )
    if role not in _SUPPORTED_LOCATION_ADMIN_ROLES:
        raise ValidationError(
            "Unsupported admin role. This slice supports only OWNER, MANAGER, and SITE_MANAGER for location admins."
        )
    return role


def _validate_create_location_admin_payload(
    payload: dict[str, Any], *, admin_file: str
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError(f"LocationAdmin file must be a JSON object: {Path(admin_file)}")
    if not payload:
        raise ValidationError(f"LocationAdmin file must not be empty: {Path(admin_file)}")

    keys = set(payload.keys())
    extra_keys = sorted(keys.difference(_ALLOWED_LOCATION_ADMIN_CREATE_FIELDS))
    if extra_keys:
        raise ValidationError(
            "Location admin create payload contains unsupported fields for this CLI: "
            + ", ".join(extra_keys)
        )

    missing = sorted(_CREATE_LOCATION_ADMIN_REQUIRED_FIELDS.difference(keys))
    if missing:
        raise ValidationError(
            "Location admin create payload is missing required fields: " + ", ".join(missing)
        )

    has_admin = "admin" in keys
    has_account = "account" in keys
    if has_admin == has_account:
        raise ValidationError(
            "Location admin create supports exactly one identity field: either admin (email) or account."
        )

    if has_admin:
        admin = _validate_account_admin_email(_require_scalar_text(payload["admin"], field_name="admin"))
        role = _validate_location_admin_role(_require_scalar_text(payload["role"], field_name="role"))
        return {"admin": admin, "role": role}

    account = _validate_account_resource(payload["account"], field_name="account")
    role = _validate_location_admin_role(_require_scalar_text(payload["role"], field_name="role"))
    return {"account": account, "role": role}


def _validate_patch_location_admin_payload(
    payload: dict[str, Any], *, admin_name: str, admin_file: str
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError(f"LocationAdmin file must be a JSON object: {Path(admin_file)}")
    if not payload:
        raise ValidationError("LocationAdmin file must not be empty.")

    keys = set(payload.keys())
    extra_keys = sorted(keys.difference(_ALLOWED_LOCATION_ADMIN_PATCH_FIELDS))
    if extra_keys:
        raise ValidationError(
            "Location admin patch payload contains unsupported fields for this CLI: "
            + ", ".join(extra_keys)
        )

    if "role" not in payload:
        raise ValidationError("Location admin patch payload must include role because --update-mask is role.")

    role = _validate_location_admin_role(_require_scalar_text(payload["role"], field_name="role"))

    if "name" in payload:
        body_name = _require_scalar_text(payload["name"], field_name="name")
        if body_name != admin_name:
            raise ValidationError("--name must match name when name is included in --admin-file.")
        return {"role": role, "name": body_name}
    return {"role": role}


def _normalize_and_validate_location_admin_update_mask(value: str) -> str:
    mask = _normalize_mask(value)
    if not mask:
        raise ValidationError("--update-mask is required.")

    fields = [field for field in (part.strip() for part in mask.split(",")) if field]
    if not fields:
        raise ValidationError("--update-mask is required.")

    invalid = sorted(set(fields).difference(_ALLOWED_LOCATION_ADMIN_PATCH_MASKS))
    if invalid:
        raise ValidationError(
            "Only role is editable for locations.admins.patch. Remove unsupported fields from --update-mask."
        )
    return "role"


def _validate_patch_account_admin_payload(
    payload: dict[str, Any], *, admin_name: str, admin_file: str
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError(f"Account admin file must be a JSON object: {Path(admin_file)}")
    if not payload:
        raise ValidationError("Account admin file must not be empty.")

    keys = set(payload.keys())
    extra_keys = sorted(keys.difference(_ALLOWED_ACCOUNT_ADMIN_PATCH_FIELDS))
    if extra_keys:
        raise ValidationError(
            "Account admin patch payload contains unsupported fields for this CLI: "
            + ", ".join(extra_keys)
        )

    if "role" not in payload:
        raise ValidationError("Account admin patch payload must include role because --update-mask is role.")

    role = _validate_role_in_slice(_require_scalar_text(payload["role"], field_name="role"), context="role")

    if "name" in payload:
        body_name = _require_scalar_text(payload["name"], field_name="name")
        if body_name != admin_name:
            raise ValidationError("--name must match name when name is included in --admin-file.")
        return {"role": role, "name": body_name}
    return {"role": role}


def _normalize_and_validate_account_admin_update_mask(value: str) -> str:
    mask = _normalize_mask(value)
    if not mask:
        raise ValidationError("--update-mask is required.")

    fields = [field for field in (part.strip() for part in mask.split(",")) if field]
    if not fields:
        raise ValidationError("--update-mask is required.")

    invalid = sorted(set(fields).difference(_ALLOWED_ACCOUNT_ADMIN_PATCH_MASKS))
    if invalid:
        raise ValidationError(
            "Only role is editable for accounts.admins.patch. Remove unsupported fields from --update-mask."
        )
    return "role"


def _validate_patch_account_payload(payload: dict[str, Any], *, account_name: str, account_file: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError(f"Account file must be a JSON object: {Path(account_file)}")
    if not payload:
        raise ValidationError("Account file must not be empty.")

    keys = set(payload.keys())
    extra_keys = sorted(keys.difference(_ALLOWED_PATCH_FIELDS))
    if extra_keys:
        raise ValidationError(
            "Account patch payload contains unsupported fields for this CLI: " + ", ".join(extra_keys)
        )

    if "accountName" not in payload:
        raise ValidationError("Account patch payload must include accountName because --update-mask is accountName.")

    account_name_field = _require_scalar_text(payload["accountName"], field_name="accountName")
    if "name" in payload:
        body_name = _require_scalar_text(payload["name"], field_name="name")
        if body_name != account_name:
            raise ValidationError("--name must match account.name when name is included in --account-file.")
        return payload

    return {"accountName": account_name_field}


def _normalize_and_validate_patch_mask(value: str) -> str:
    mask = _normalize_mask(value)
    if not mask:
        raise ValidationError("--update-mask is required.")

    fields = [field for field in (part.strip() for part in mask.split(",")) if field]
    if not fields:
        raise ValidationError("--update-mask is required.")
    invalid = sorted(set(fields).difference(_ALLOWED_PATCH_MASKS))
    if invalid:
        raise ValidationError(
            "Only accountName is editable for accounts.patch. Remove unsupported fields from --update-mask."
        )
    return "accountName"
def _parent_from_invitation_name(name: str) -> str:
    marker = "/invitations/"
    if marker not in name:
        raise ValidationError("--name must be in accounts/{account}/invitations/{invitation} format.")
    parent, invitation_id = name.split(marker, 1)
    if not parent or not invitation_id:
        raise ValidationError("--name must be in accounts/{account}/invitations/{invitation} format.")
    if not parent.startswith("accounts/"):
        raise ValidationError("--name must be in accounts/{account}/invitations/{invitation} format.")
    return parent


def _parent_from_admin_name(name: str) -> str:
    parts = [part.strip() for part in name.strip().strip("/").split("/") if part.strip()]
    if len(parts) != 4 or parts[0] != "accounts" or parts[2] != "admins":
        raise ValidationError("--name must be in accounts/{account}/admins/{admin} format.")
    return f"{parts[0]}/{parts[1]}"


def _admin_matches(
    item: dict[str, Any],
    *,
    expected_admin: str | None,
    expected_account: str | None,
    expected_role: str | None,
    expected_name: str | None = None,
) -> bool:
    actual_name = str(item.get("name") or "").strip()
    actual_admin = str(item.get("admin") or "").strip()
    actual_account = str(item.get("account") or "").strip()
    actual_role = str(item.get("role") or "").strip()
    if expected_name and actual_name != expected_name:
        return False
    if expected_admin and actual_admin != expected_admin:
        return False
    if expected_account and actual_account != expected_account:
        return False
    if expected_role and actual_role != expected_role:
        return False
    return True


def _verify_admin_in_list(
    *,
    client: GoogleBusinessProfileApiClient,
    parent: str,
    expected_admin: str | None = None,
    expected_account: str | None = None,
    expected_role: str | None = None,
    expected_name: str | None = None,
    admin_list_operation: str = "account-management.accounts.admins.list",
    expect_absent: bool = False,
) -> tuple[dict[str, Any], bool]:
    request = {
        "method": "GET",
        "host": ACCOUNT_MANAGEMENT_HOST,
        "path": f"v1/{parent}/admins",
    }
    try:
        if parent.startswith("locations/"):
            verify_response, verify_request = client.list_location_admins(parent=parent)
        else:
            verify_response, verify_request = client.list_account_admins(parent=parent)
        request = verify_request
    except Exception as exc:  # noqa: BLE001
        return (
            {
                "ok": False,
                "operation": admin_list_operation,
                "request": request,
                "response": {
                    "request_error": True,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                },
                "note": "Could not verify admin state because the admins list call failed.",
            },
            False,
        )

    admins = verify_response.get("admins")
    if not isinstance(admins, list):
        return (
            {
                "ok": False,
                "operation": admin_list_operation,
                "request": verify_request,
                "response": verify_response,
                "note": "Could not verify admin state because the admins list response is missing or malformed.",
            },
            False,
        )

    for candidate in admins:
        if not isinstance(candidate, dict):
            continue
        if _admin_matches(
            candidate,
            expected_admin=expected_admin,
            expected_account=expected_account,
            expected_role=expected_role,
            expected_name=expected_name,
        ):
            if expect_absent:
                return (
                    {
                        "ok": False,
                        "operation": admin_list_operation,
                        "request": verify_request,
                        "response": verify_response,
                        "note": "Expected admin still appears in the list after the delete request.",
                    },
                    False,
                )
            return (
                {
                    "ok": True,
                    "operation": admin_list_operation,
                    "request": verify_request,
                    "response": verify_response,
                },
                True,
            )

    if expected_name and not expected_admin and not expected_role:
        note = f"Admin name {expected_name} was not found in list response."
    elif expected_admin and expected_role:
        note = f"Admin {expected_admin} with role {expected_role} was not found in the list response."
    elif expected_account and expected_role:
        note = (
            f"Location account admin account {expected_account} with role {expected_role} was not found in the list response."
        )
    elif expect_absent and expected_name:
        note = f"Admin name {expected_name} was not found in the list response."
    else:
        note = "Expected admin record was not found in the list response."

    return (
        {
            "ok": expect_absent,
        "operation": admin_list_operation,
        "request": verify_request,
        "response": verify_response,
        "note": note,
    },
    expect_absent,
)


def _verify_account_admin_deleted(
    *,
    client: GoogleBusinessProfileApiClient,
    name: str,
) -> tuple[dict[str, Any], bool]:
    parent = _parent_from_admin_name(name)
    verification, changed = _verify_admin_in_list(
        client=client,
        parent=parent,
        expected_name=name,
        admin_list_operation="account-management.accounts.admins.list",
        expect_absent=True,
    )
    if changed:
        return (
            {
                "ok": True,
                "operation": "account-management.accounts.admins.list",
                "request": verification.get("request", {}),
                "response": verification.get("response", {}),
                "note": "Follow-up list confirmed the admin no longer appears.",
            },
            True,
        )
    verification["note"] = str(verification.get("note") or "Could not verify admin deletion.")
    return verification, False


def _parent_from_location_admin_name(name: str) -> str:
    parts = [part.strip() for part in name.strip().strip("/").split("/") if part.strip()]
    if len(parts) != 4 or parts[0] != "locations" or parts[2] != "admins":
        raise ValidationError("--name must be in locations/{location}/admins/{admin} format.")
    return f"{parts[0]}/{parts[1]}"


def _verify_location_admin_deleted(
    *,
    client: GoogleBusinessProfileApiClient,
    name: str,
) -> tuple[dict[str, Any], bool]:
    parent = _parent_from_location_admin_name(name)
    verification, changed = _verify_admin_in_list(
        client=client,
        parent=parent,
        expected_name=name,
        admin_list_operation="account-management.locations.admins.list",
        expect_absent=True,
    )
    if changed:
        return (
            {
                "ok": True,
                "operation": "account-management.locations.admins.list",
                "request": verification.get("request", {}),
                "response": verification.get("response", {}),
                "note": "Follow-up list confirmed the admin no longer appears.",
            },
            True,
        )
    verification["note"] = str(verification.get("note") or "Could not verify location admin deletion.")
    return verification, False


def _invitation_still_present(
    *,
    list_response: dict[str, Any],
    invitation_name: str,
) -> bool | None:
    items = list_response.get("invitations")
    if not isinstance(items, list):
        return None
    for item in items:
        if isinstance(item, dict) and str(item.get("name") or "").strip() == invitation_name:
            return True
    return False


def _verify_invitation_gone(
    *,
    client: GoogleBusinessProfileApiClient,
    invitation_name: str,
    parent: str,
) -> tuple[dict[str, Any], bool]:
    try:
        verify_response, verify_request = client.list_account_invitations(parent=parent)
    except Exception as exc:  # noqa: BLE001
        return (
            {
                "ok": False,
                "operation": "account-management.accounts.invitations.list",
                "request": {
                    "method": "GET",
                    "host": ACCOUNT_MANAGEMENT_HOST,
                    "path": f"v1/{parent}/invitations",
                },
                "response": {
                    "request_error": True,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                },
                "note": "Could not run invitations list follow-up; keeping change state as unconfirmed.",
            },
            False,
        )

    still_present = _invitation_still_present(list_response=verify_response, invitation_name=invitation_name)
    if still_present is None:
        return (
            {
                "ok": False,
                "operation": "account-management.accounts.invitations.list",
                "request": verify_request,
                "response": verify_response,
                "note": "Could not verify invitation disappearance because invitations list is missing or malformed.",
            },
            False,
        )

    if still_present:
        return (
            {
                "ok": False,
                "operation": "account-management.accounts.invitations.list",
                "request": verify_request,
                "response": verify_response,
                "note": "Invitation is still present in pending invitations list; it may not have changed.",
            },
            False,
        )

    return (
        {
            "ok": True,
            "operation": "account-management.accounts.invitations.list",
            "request": verify_request,
            "response": verify_response,
            "note": "Follow-up list confirmed invitation is no longer present.",
        },
        True,
    )


def _verify_location_transfer(
    *,
    client: GoogleBusinessProfileApiClient,
    name: str,
    source_account: str,
    destination_account: str,
) -> tuple[dict[str, Any], bool]:
    source_result, source_has = _location_present_in_account(
        client=client,
        account_name=source_account,
        location_name=name,
    )
    if source_has is None:
        source_result["note"] = source_result.get("note") or (
            f"Could not verify transfer because source account {source_account} list check failed."
        )
        return source_result, False

    destination_result, destination_has = _location_present_in_account(
        client=client,
        account_name=destination_account,
        location_name=name,
    )
    if destination_has is None:
        destination_result["note"] = destination_result.get("note") or (
            f"Could not verify transfer because destination account {destination_account} list check failed."
        )
        return destination_result, False

    verification = {
        "ok": False,
        "operation": "account-management.locations.transfer",
        "request": {
            "source": source_result.get("request"),
            "destination": destination_result.get("request"),
        },
        "response": {
            "source": {
                "contains": source_has,
                "operation": "business-info.accounts.locations.list",
                "request": source_result.get("request"),
                "response": source_result.get("response"),
            },
            "destination": {
                "contains": destination_has,
                "operation": "business-info.accounts.locations.list",
                "request": destination_result.get("request"),
                "response": destination_result.get("response"),
            },
        },
    }

    if source_has:
        verification["note"] = (
            f"Transfer did not remove location {name} from source account {source_account}."
        )
        return verification, False
    if not destination_has:
        verification["note"] = (
            f"Transfer did not place location {name} in destination account {destination_account}."
        )
        return verification, False

    verification["ok"] = True
    verification["note"] = (
        "Transfer read-back verification succeeded: source account no longer lists location "
        "and destination now lists it."
    )
    return verification, True


def _verify_account(
    *,
    client: GoogleBusinessProfileApiClient,
    name: str,
    expected_account_name: str | None = None,
) -> tuple[dict[str, Any], bool]:
    request = {
        "method": "GET",
        "host": ACCOUNT_MANAGEMENT_HOST,
        "path": f"v1/{name}",
    }
    try:
        verify_response, verify_request = client.get_account(name=name)
        request = verify_request
    except Exception as exc:
        return (
            {
                "ok": False,
                "operation": "account-management.accounts.get",
                "request": request,
                "response": {
                    "request_error": True,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                },
                "note": "Unable to verify account update by read-back.",
            },
            False,
        )

    actual_name = str(verify_response.get("name") or "").strip()
    if not actual_name:
        return (
            {
                "ok": False,
                "operation": "account-management.accounts.get",
                "request": verify_request,
                "response": verify_response,
                "note": "Read-back response did not include an account name; change confidence is unknown.",
            },
            False,
        )
    if actual_name != name:
        return (
            {
                "ok": False,
                "operation": "account-management.accounts.get",
                "request": verify_request,
                "response": verify_response,
                "note": "Read-back returned a different account name than requested.",
            },
            False,
        )

    if expected_account_name is not None:
        response_account_name = str(verify_response.get("accountName") or "").strip()
        if response_account_name != expected_account_name:
            return (
                {
                    "ok": False,
                    "operation": "account-management.accounts.get",
                    "request": verify_request,
                    "response": verify_response,
                    "note": "Read-back response accountName did not match the requested accountName.",
                },
                False,
            )

    return (
        {
            "ok": True,
            "operation": "account-management.accounts.get",
            "request": verify_request,
            "response": verify_response,
        },
        True,
    )


def cmd_accounts_list(args: Any, ctx: dict[str, Any]) -> int:
    client = _client_for_ctx(ctx)
    response, request = client.list_accounts(
        parent_account=str(args.parent_account).strip() or None,
        page_size=args.page_size,
        page_token=args.page_token,
        filter=str(args.filter).strip() or None,
    )
    return _emit(ctx, "account-management.accounts.list", request, response)


def cmd_accounts_create(args: Any, ctx: dict[str, Any]) -> int:
    operation = "account-management.accounts.create"
    account_file = _require_resource(args.account_file, arg_name="--account-file")
    account_body = _validate_create_account_payload(
        _validate_json_account_file(account_file, label="Account"),
        account_file=account_file,
    )

    selector = account_body.get("accountName", "")
    if not selector:
        raise ValidationError("accountName is required for selector generation.")

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=selector,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
        body=account_body,
        mask="accountName,primaryOwner,type",
        risk_level="high",
        risk_reasons=["Account creation changes account ownership and control state."],
        preconditions=["OAuth access"],
        verification_plan=["Read back the created account with accounts get."],
    )

    if bool(ctx.get("apply")):
        client = _client_for_ctx(ctx)
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for account-management accounts create.")

        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=selector,
            body=account_body,
            mask="accountName,primaryOwner,type",
            plan_in_label="--plan-in",
        )

        create_response, _ = client.create_account(body=account_body)
        created_name = str(create_response.get("name") or "").strip()
        if not created_name:
            verification = {
                "ok": False,
                "operation": "account-management.accounts.get",
                "request": {
                    "method": "GET",
                    "host": ACCOUNT_MANAGEMENT_HOST,
                    "path": "v1/<missing-name>",
                },
                "response": create_response,
                "note": "Create response did not include a usable name. Could not run read-back verification.",
            }
            changed = False
            selector = "accounts/<missing-name>"
        else:
            verification, changed = _verify_account(
                client=client,
                name=created_name,
                expected_account_name=account_body.get("accountName"),
            )
            selector = created_name

        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=selector,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
            changed=changed,
            verification=verification,
            diff_applied=["accountName", "primaryOwner", "type"],
        )
        receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
        return _emit_write_output(
            ctx,
            operation=operation,
            dry_run=False,
            payload_obj=receipt,
            artifact_path=receipt_path,
        )

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )


def cmd_accounts_patch(args: Any, ctx: dict[str, Any]) -> int:
    operation = "account-management.accounts.patch"
    name = _require_resource(args.name, arg_name="--name")
    update_mask = _normalize_and_validate_patch_mask(_require_resource(args.update_mask, arg_name="--update-mask"))

    account_file = _require_resource(args.account_file, arg_name="--account-file")
    account_body = _validate_patch_account_payload(
        _validate_json_account_file(account_file, label="Account"),
        account_name=name,
        account_file=account_file,
    )

    validate_only = bool(args.validate_only)
    if validate_only and bool(ctx.get("apply")):
        raise ValidationError("--validate-only cannot be used with --apply.")

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
        body=account_body,
        mask=update_mask,
        risk_level="medium",
        risk_reasons=["Account patch updates accountName."],
        preconditions=["OAuth access"],
        verification_plan=["Read back the account with accounts get."],
    )

    if bool(ctx.get("apply")):
        client = _client_for_ctx(ctx)
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for account-management accounts patch.")

        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=name,
            body=account_body,
            mask=update_mask,
            plan_in_label="--plan-in",
        )

        _, _ = client.patch_account(
            name=name,
            update_mask=update_mask,
            body=account_body,
            validate_only=False,
        )
        verification, changed = _verify_account(
            client=client,
            name=name,
            expected_account_name=account_body.get("accountName"),
        )
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
            changed=changed,
            verification=verification,
            diff_applied=[field.strip() for field in update_mask.split(",") if field.strip()],
        )
        receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
        return _emit_write_output(
            ctx,
            operation=operation,
            dry_run=False,
            payload_obj=receipt,
            artifact_path=receipt_path,
        )

    if validate_only:
        client = _client_for_ctx(ctx)
        _, _ = client.patch_account(
            name=name,
            update_mask=update_mask,
            body=account_body,
            validate_only=True,
        )

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )


def cmd_account_get(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    client = _client_for_ctx(ctx)
    response, request = client.get_account(name=name)
    return _emit(ctx, "account-management.accounts.get", request, response)


def cmd_accounts_admins_list(args: Any, ctx: dict[str, Any]) -> int:
    parent = _require_resource(args.parent, arg_name="--parent")
    client = _client_for_ctx(ctx)
    response, request = client.list_account_admins(parent=parent)
    return _emit(ctx, "account-management.accounts.admins.list", request, response)


def cmd_accounts_admins_create(args: Any, ctx: dict[str, Any]) -> int:
    operation = "account-management.accounts.admins.create"
    parent = _normalize_account_parent(_require_resource(args.parent, arg_name="--parent"))
    admin_file = _require_resource(args.admin_file, arg_name="--admin-file")
    admin_body = _validate_create_account_admin_payload(
        _validate_json_account_file(admin_file, label="Admin"),
        admin_file=admin_file,
    )

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=parent,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
        body=admin_body,
        mask="admin,role",
        risk_level="high",
        risk_reasons=["Account admin creation invites a user to an account."],
        preconditions=["OAuth access"],
        verification_plan=["Read back the admin list from accounts.admins.list and confirm the admin appears with the requested role."],
    )

    if bool(ctx.get("apply")):
        client = _client_for_ctx(ctx)
        if not bool(ctx.get("yes")):
            raise SafetyError("--apply requires --yes for account-management accounts admins create.")
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for account-management accounts admins create.")

        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=parent,
            body=admin_body,
            mask="admin,role",
            plan_in_label="--plan-in",
        )

        create_response, _ = client.create_account_admin(parent=parent, body=admin_body)
        created_name = str(create_response.get("name") or "").strip()
        verification, changed = _verify_admin_in_list(
            client=client,
            parent=parent,
            expected_admin=admin_body.get("admin", ""),
            expected_role=admin_body.get("role", ""),
            expected_name=created_name or None,
        )
        selector = created_name or parent
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=selector,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
            changed=changed,
            verification=verification,
            diff_applied=["admin", "role"],
        )
        receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
        return _emit_write_output(
            ctx,
            operation=operation,
            dry_run=False,
            payload_obj=receipt,
            artifact_path=receipt_path,
        )

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )


def cmd_accounts_admins_delete(args: Any, ctx: dict[str, Any]) -> int:
    operation = "account-management.accounts.admins.delete"
    name = _require_resource(args.name, arg_name="--name")
    parent = _parent_from_admin_name(name)

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
        body={},
        mask="name",
        risk_level="high",
        risk_reasons=["Account admin deletion can change account access."],
        preconditions=["OAuth access"],
        verification_plan=["Read back the admin list from accounts.admins.list and confirm the admin no longer appears."],
    )

    if bool(ctx.get("apply")):
        client = _client_for_ctx(ctx)
        if not bool(ctx.get("yes")):
            raise SafetyError("--apply requires --yes for account-management accounts admins delete.")
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for account-management accounts admins delete.")

        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=name,
            body={},
            mask="name",
            plan_in_label="--plan-in",
        )

        _, _ = client.delete_account_admin(name=name)
        verification, changed = _verify_account_admin_deleted(client=client, name=name)
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
            changed=changed,
            verification=verification,
            diff_applied=["name"],
        )
        receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
        return _emit_write_output(
            ctx,
            operation=operation,
            dry_run=False,
            payload_obj=receipt,
            artifact_path=receipt_path,
        )

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )


def cmd_accounts_admins_patch(args: Any, ctx: dict[str, Any]) -> int:
    operation = "account-management.accounts.admins.patch"
    name = _require_resource(args.name, arg_name="--name")
    parent = _parent_from_admin_name(name)
    update_mask = _normalize_and_validate_account_admin_update_mask(
        _require_resource(args.update_mask, arg_name="--update-mask")
    )
    admin_file = _require_resource(args.admin_file, arg_name="--admin-file")
    admin_body = _validate_patch_account_admin_payload(
        _validate_json_account_file(admin_file, label="Admin"),
        admin_name=name,
        admin_file=admin_file,
    )

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
        body=admin_body,
        mask=update_mask,
        risk_level="medium",
        risk_reasons=["Account admin patch updates role."],
        preconditions=["OAuth access"],
        verification_plan=["Read back the admin list from accounts.admins.list and confirm the admin has the updated role."],
    )

    if bool(ctx.get("apply")):
        client = _client_for_ctx(ctx)
        if not bool(ctx.get("yes")):
            raise SafetyError("--apply requires --yes for account-management accounts admins patch.")
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for account-management accounts admins patch.")

        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=name,
            body=admin_body,
            mask=update_mask,
            plan_in_label="--plan-in",
        )

        _, _ = client.patch_account_admin(name=name, update_mask=update_mask, body=admin_body)
        verification, changed = _verify_admin_in_list(
            client=client,
            parent=parent,
            expected_name=name,
            expected_role=admin_body.get("role"),
        )
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
            changed=changed,
            verification=verification,
            diff_applied=[field.strip() for field in update_mask.split(",") if field.strip()],
        )
        receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
        return _emit_write_output(
            ctx,
            operation=operation,
            dry_run=False,
            payload_obj=receipt,
            artifact_path=receipt_path,
        )

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )


def cmd_accounts_invitations_list(args: Any, ctx: dict[str, Any]) -> int:
    parent = _require_resource(args.parent, arg_name="--parent")
    client = _client_for_ctx(ctx)
    response, request = client.list_account_invitations(
        parent=parent,
        filter=str(args.filter).strip() or None,
    )
    return _emit(ctx, "account-management.accounts.invitations.list", request, response)


def cmd_accounts_invitations_accept(args: Any, ctx: dict[str, Any]) -> int:
    invitation_name = _require_resource(args.name, arg_name="--name")
    parent_account = _parent_from_invitation_name(invitation_name)
    operation = "account-management.accounts.invitations.accept"

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=invitation_name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
        body={},
        mask="name",
        risk_level="medium",
        risk_reasons=["Account invitation acceptance changes account access state."],
        preconditions=["OAuth access"],
        verification_plan=[
            "Read pending invitations for the parent account and confirm the invitation no longer appears.",
        ],
    )

    if bool(ctx.get("apply")):
        client = _client_for_ctx(ctx)
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for account-management accounts invitations accept.")
        if not bool(ctx.get("yes")):
            raise SafetyError("--apply requires --yes for account-management accounts invitations accept.")
        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=invitation_name,
            body={},
            mask="name",
            plan_in_label="--plan-in",
        )

        _, _ = client.accept_account_invitation(name=invitation_name)
        verification, changed = _verify_invitation_gone(
            client=client,
            invitation_name=invitation_name,
            parent=parent_account,
        )
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=invitation_name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
            changed=changed,
            verification=verification,
            diff_applied=["name"],
        )
        receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
        return _emit_write_output(
            ctx,
            operation=operation,
            dry_run=False,
            payload_obj=receipt,
            artifact_path=receipt_path,
        )

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )


def cmd_accounts_invitations_decline(args: Any, ctx: dict[str, Any]) -> int:
    invitation_name = _require_resource(args.name, arg_name="--name")
    parent_account = _parent_from_invitation_name(invitation_name)
    operation = "account-management.accounts.invitations.decline"

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=invitation_name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
        body={},
        mask="name",
        risk_level="medium",
        risk_reasons=["Account invitation decline changes account access state."],
        preconditions=["OAuth access"],
        verification_plan=[
            "Read pending invitations for the parent account and confirm the invitation no longer appears.",
        ],
    )

    if bool(ctx.get("apply")):
        client = _client_for_ctx(ctx)
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for account-management accounts invitations decline.")
        if not bool(ctx.get("yes")):
            raise SafetyError("--apply requires --yes for account-management accounts invitations decline.")
        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=invitation_name,
            body={},
            mask="name",
            plan_in_label="--plan-in",
        )

        _, _ = client.decline_account_invitation(name=invitation_name)
        verification, changed = _verify_invitation_gone(
            client=client,
            invitation_name=invitation_name,
            parent=parent_account,
        )
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=invitation_name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
            changed=changed,
            verification=verification,
            diff_applied=["name"],
        )
        receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
        return _emit_write_output(
            ctx,
            operation=operation,
            dry_run=False,
            payload_obj=receipt,
            artifact_path=receipt_path,
        )

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )


def cmd_locations_admins_list(args: Any, ctx: dict[str, Any]) -> int:
    parent = _require_resource(args.parent, arg_name="--parent")
    client = _client_for_ctx(ctx)
    response, request = client.list_location_admins(parent=parent)
    return _emit(ctx, "account-management.locations.admins.list", request, response)


def cmd_locations_admins_create(args: Any, ctx: dict[str, Any]) -> int:
    operation = "account-management.locations.admins.create"
    parent = _normalize_location_parent(_require_resource(args.parent, arg_name="--parent"))
    admin_file = _require_resource(args.admin_file, arg_name="--admin-file")
    admin_body = _validate_create_location_admin_payload(
        _validate_json_account_file(admin_file, label="LocationAdmin"),
        admin_file=admin_file,
    )

    create_mask = "account,role" if "account" in admin_body else "admin,role"
    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=parent,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
        body=admin_body,
        mask=create_mask,
        risk_level="high",
        risk_reasons=["Location admin creation changes access for a location."],
        preconditions=["OAuth access"],
        verification_plan=["Read back the admin list from locations.admins.list and confirm the admin appears with the requested role."],
    )

    if bool(ctx.get("apply")):
        client = _client_for_ctx(ctx)
        if not bool(ctx.get("yes")):
            raise SafetyError("--apply requires --yes for account-management locations admins create.")
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for account-management locations admins create.")

        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=parent,
            body=admin_body,
            mask=create_mask,
            plan_in_label="--plan-in",
        )

        create_response, _ = client.create_location_admin(parent=parent, body=admin_body)
        created_name = str(create_response.get("name") or "").strip()
        verification, changed = _verify_admin_in_list(
            client=client,
            parent=parent,
            expected_admin=admin_body.get("admin", ""),
            expected_account=admin_body.get("account", ""),
            expected_role=admin_body.get("role", ""),
            expected_name=created_name or None,
            admin_list_operation="account-management.locations.admins.list",
        )
        selector = created_name or parent
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=selector,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
            changed=changed,
            verification=verification,
            diff_applied=[field.strip() for field in create_mask.split(",") if field.strip()],
        )
        receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
        return _emit_write_output(
            ctx,
            operation=operation,
            dry_run=False,
            payload_obj=receipt,
            artifact_path=receipt_path,
        )

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )


def cmd_locations_admins_delete(args: Any, ctx: dict[str, Any]) -> int:
    operation = "account-management.locations.admins.delete"
    name = _require_resource(args.name, arg_name="--name")
    _parent_from_location_admin_name(name)

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
        body={},
        mask="name",
        risk_level="high",
        risk_reasons=["Location admin deletion can change location access."],
        preconditions=["OAuth access"],
        verification_plan=["Read back the admin list from locations.admins.list and confirm the admin no longer appears."],
    )

    if bool(ctx.get("apply")):
        client = _client_for_ctx(ctx)
        if not bool(ctx.get("yes")):
            raise SafetyError("--apply requires --yes for account-management locations admins delete.")
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for account-management locations admins delete.")

        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=name,
            body={},
            mask="name",
            plan_in_label="--plan-in",
        )

        _, _ = client.delete_location_admin(name=name)
        verification, changed = _verify_location_admin_deleted(client=client, name=name)
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
            changed=changed,
            verification=verification,
            diff_applied=["name"],
        )
        receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
        return _emit_write_output(
            ctx,
            operation=operation,
            dry_run=False,
            payload_obj=receipt,
            artifact_path=receipt_path,
        )

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )


def cmd_locations_admins_patch(args: Any, ctx: dict[str, Any]) -> int:
    operation = "account-management.locations.admins.patch"
    name = _require_resource(args.name, arg_name="--name")
    _parent_from_location_admin_name(name)
    update_mask = _normalize_and_validate_location_admin_update_mask(
        _require_resource(args.update_mask, arg_name="--update-mask")
    )
    admin_file = _require_resource(args.admin_file, arg_name="--admin-file")
    admin_body = _validate_patch_location_admin_payload(
        _validate_json_account_file(admin_file, label="LocationAdmin"),
        admin_name=name,
        admin_file=admin_file,
    )

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
        body=admin_body,
        mask=update_mask,
        risk_level="medium",
        risk_reasons=["Location admin patch updates role."],
        preconditions=["OAuth access"],
        verification_plan=["Read back the admin list from locations.admins.list and confirm the admin has the updated role."],
    )

    if bool(ctx.get("apply")):
        client = _client_for_ctx(ctx)
        if not bool(ctx.get("yes")):
            raise SafetyError("--apply requires --yes for account-management locations admins patch.")
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for account-management locations admins patch.")

        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=name,
            body=admin_body,
            mask=update_mask,
            plan_in_label="--plan-in",
        )

        _, _ = client.patch_location_admin(name=name, update_mask=update_mask, body=admin_body)
        parent = _parent_from_location_admin_name(name)
        verification, changed = _verify_admin_in_list(
            client=client,
            parent=parent,
            expected_name=name,
            expected_role=admin_body.get("role"),
            admin_list_operation="account-management.locations.admins.list",
        )
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
            changed=changed,
            verification=verification,
            diff_applied=[field.strip() for field in update_mask.split(",") if field.strip()],
        )
        receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
        return _emit_write_output(
            ctx,
            operation=operation,
            dry_run=False,
            payload_obj=receipt,
            artifact_path=receipt_path,
        )

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )


def cmd_locations_transfer(args: Any, ctx: dict[str, Any]) -> int:
    operation = "account-management.locations.transfer"
    name = _normalize_location_name(_require_resource(args.name, arg_name="--name"))
    source_account = _normalize_account_name_for_transfer(
        _require_resource(args.source_account, arg_name="--source-account"),
        arg_name="--source-account",
    )
    destination_account = _normalize_account_name_for_transfer(
        _require_resource(args.destination_account, arg_name="--destination-account"),
        arg_name="--destination-account",
    )
    if source_account == destination_account:
        raise ValidationError("--source-account and --destination-account must be different accounts.")

    transfer_body = {
        "name": name,
        "source_account": source_account,
        "destination_account": destination_account,
    }

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
        body=transfer_body,
        mask=_LOCATION_TRANSFER_PLAN_MASK,
        risk_level="high",
        risk_reasons=["Location transfer changes account ownership for a location."],
        preconditions=["OAuth access"],
        verification_plan=[
            "List source and destination account locations with readMask=name. Transfer succeeds only if location disappears from source and appears in destination.",
        ],
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for account-management locations transfer.")
        if not bool(ctx.get("yes")):
            raise SafetyError("--apply requires --yes for account-management locations transfer.")
        if not bool(ctx.get("ack_irreversible")):
            raise SafetyError("--apply requires --ack-irreversible for account-management locations transfer.")

        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=name,
            body=transfer_body,
            mask=_LOCATION_TRANSFER_PLAN_MASK,
            plan_in_label="--plan-in",
        )

        client = _client_for_ctx(ctx)
        _, _ = client.transfer_location(name=name, destination_account=destination_account)
        verification, changed = _verify_location_transfer(
            client=client,
            name=name,
            source_account=source_account,
            destination_account=destination_account,
        )
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=ACCOUNT_MANAGEMENT_HOST,
            changed=changed,
            verification=verification,
            diff_applied=[part for part in _LOCATION_TRANSFER_PLAN_MASK.split(",") if part],
        )
        receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
        return _emit_write_output(
            ctx,
            operation=operation,
            dry_run=False,
            payload_obj=receipt,
            artifact_path=receipt_path,
        )

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )

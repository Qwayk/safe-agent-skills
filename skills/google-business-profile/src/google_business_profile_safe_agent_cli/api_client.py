from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Union

from .config import Config
from .errors import SafetyError, ValidationError
from .http import HttpClient
from .oauth_tokens import read_token_json, token_path_for_env_file


AccountManagementFamily = Literal["account-management"]
BusinessInfoFamily = Literal["business-info"]
BusinessCallsFamily = Literal["business-calls"]
NotificationFamily = Literal["notifications"]
MediaUploadFamily = Literal["media-upload-v1"]
LegacyV49Family = Literal["legacy-v49"]
PerformanceFamily = Literal["performance"]
LodgingFamily = Literal["lodging"]
PlaceActionsFamily = Literal["place-actions"]
VerificationsFamily = Literal["verifications"]
ApiFamily = Union[
    AccountManagementFamily,
    BusinessInfoFamily,
    BusinessCallsFamily,
    NotificationFamily,
    MediaUploadFamily,
    LegacyV49Family,
    PerformanceFamily,
    LodgingFamily,
    PlaceActionsFamily,
    VerificationsFamily,
]

ACCOUNT_MANAGEMENT_HOST = "https://mybusinessaccountmanagement.googleapis.com"
BUSINESS_INFORMATION_HOST = "https://mybusinessbusinessinformation.googleapis.com"
BUSINESS_CALLS_HOST = "https://mybusinessbusinesscalls.googleapis.com"
NOTIFICATIONS_HOST = "https://mybusinessnotifications.googleapis.com"
MEDIA_UPLOAD_HOST = "https://mybusiness.googleapis.com"
LEGACY_V49_HOST = "https://mybusiness.googleapis.com"
LODGING_HOST = "https://mybusinesslodging.googleapis.com"
PERFORMANCE_HOST = "https://businessprofileperformance.googleapis.com"
PLACE_ACTIONS_HOST = "https://mybusinessplaceactions.googleapis.com"
VERIFICATIONS_HOST = "https://mybusinessverifications.googleapis.com"
USER_AGENT = "google-business-profile-safe-agent-cli/0.1.0"
READ_LIKE_POST_OPERATIONS = {
    "business-info.google-locations.search",
    "verifications.locations.fetch-verification-options",
}


def _is_validate_only_request(method: str, params: dict[str, Any] | None) -> bool:
    if method.upper() not in {"POST", "PATCH", "PUT", "DELETE"}:
        return False
    if not isinstance(params, dict):
        return False
    return bool(params.get("validateOnly") or params.get("validate_only"))


def _require_provider_write_no_snapshot_approval(
    *,
    operation: str,
    method: str,
    params: dict[str, Any] | None,
    ack_no_snapshot: bool,
) -> None:
    if operation in READ_LIKE_POST_OPERATIONS:
        return
    if method.upper() in {"GET", "HEAD", "OPTIONS"}:
        return
    if _is_validate_only_request(method, params):
        return
    if ack_no_snapshot:
        return
    raise SafetyError(
        "Refused: this Google Business Profile write has no reliable generic before-state snapshot. "
        "Review the dry-run plan, then rerun with --ack-no-snapshot if you approve applying without a snapshot."
    )


@dataclass(frozen=True)
class ApiRequest:
    operation: str
    method: str
    host: str
    path: str
    params: dict[str, Any] | None = None
    body: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "operation": self.operation,
            "method": self.method,
            "host": self.host,
            "path": self.path,
        }
        if self.params:
            payload["params"] = self.params
        if self.body is not None:
            payload["body"] = self.body
        return payload


def _clean_params(values: dict[str, Any] | None) -> dict[str, Any] | None:
        if not values:
            return None
        out = {k: v for k, v in values.items() if v is not None}
        return out or None


def _load_credentials_from_token_data(token_data: dict[str, Any]):
    from google.oauth2 import credentials as google_credentials  # type: ignore

    return google_credentials.Credentials.from_authorized_user_info(token_data)


def _resource_path(resource: str, suffix: str | None = None) -> str:
    base = resource.strip().strip("/")
    return f"v1/{base}{'' if not suffix else '/' + suffix.strip('/')}"


def _lodging_resource_path(name: str) -> str:
    base = name.strip().strip("/")
    if not base.endswith("/lodging"):
        raise ValidationError("lodging name must be in the form locations/{location}/lodging")
    return _resource_path(base)


def _business_calls_resource_path(name: str) -> str:
    base = name.strip().strip("/")
    if not base.endswith("/businesscallssettings"):
        raise ValidationError(
            "business calls settings name must be in the form locations/{location}/businesscallssettings"
        )
    return _resource_path(base)


class GoogleBusinessProfileApiClient:
    def __init__(
        self,
        *,
        cfg: Config,
        env_file: str,
        timeout_s: float,
        verbose: bool,
        ack_no_snapshot: bool = False,
    ) -> None:
        self._cfg = cfg
        self._env_file = env_file
        self._http = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent=USER_AGENT)
        self._token = self._load_access_token()
        self._ack_no_snapshot = ack_no_snapshot

    def _load_access_token(self) -> str:
        token_path = token_path_for_env_file(self._env_file)
        token_data = read_token_json(token_path)
        if token_data is None:
            raise ValidationError(f"OAuth credentials not found: {token_path}")
        if not isinstance(token_data, dict):
            raise ValidationError(f"OAuth credentials are invalid: {token_path}")

        creds = _load_credentials_from_token_data(token_data)
        if not getattr(creds, "valid", False):
            try:
                from google.auth.transport.requests import Request as GoogleAuthRequest  # type: ignore

                creds.refresh(GoogleAuthRequest())
            except Exception as exc:
                raise ValidationError("OAuth credentials cannot be refreshed. Run auth login again.") from exc

        token = getattr(creds, "token", None)
        if not token:
            raise ValidationError("OAuth credentials do not contain a token. Run auth login again.")
        return str(token)

    def _request(
        self,
        *,
        family: ApiFamily,
        operation: str,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        allow_empty_response: bool = False,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        host = self._host_for(family)
        cleaned_params = _clean_params(params)
        _require_provider_write_no_snapshot_approval(
            operation=operation,
            method=method,
            params=cleaned_params,
            ack_no_snapshot=self._ack_no_snapshot,
        )
        url = f"{host}/{path}"
        headers = {"Authorization": f"Bearer {self._token}", "Accept": "application/json"}

        response = self._http.request(
            method,
            url,
            headers=headers,
            params=cleaned_params,
            json_body=body,
        )
        try:
            payload = response.json()
        except Exception as exc:  # noqa: BLE001
            if allow_empty_response and isinstance(response.body, bytes) and response.body.strip() == b"":
                payload = {}
            else:
                if response.body:
                    raise ValidationError(f"Provider response was not JSON for {operation}") from exc
                raise ValidationError(f"Empty provider response for {operation}") from exc

        req = ApiRequest(
            operation=operation,
            method=method,
            host=host,
            path=path.lstrip("/"),
            params=cleaned_params,
            body=body,
        ).as_dict()

        if body is None and not req.get("body"):
            req.pop("body", None)
        return payload, req

    def _request_with_data(
        self,
        *,
        family: ApiFamily,
        operation: str,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        data: bytes | None = None,
        content_type: str | None = None,
        request_body: dict[str, Any] | None = None,
        allow_empty_response: bool = False,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        host = self._host_for(family)
        cleaned_params = _clean_params(params)
        _require_provider_write_no_snapshot_approval(
            operation=operation,
            method=method,
            params=cleaned_params,
            ack_no_snapshot=self._ack_no_snapshot,
        )
        url = f"{host}/{path}"
        headers = {"Authorization": f"Bearer {self._token}", "Accept": "application/json"}
        if content_type:
            headers["Content-Type"] = content_type

        response = self._http.request(
            method,
            url,
            headers=headers,
            params=cleaned_params,
            data=data,
        )

        try:
            payload = response.json()
        except Exception as exc:  # noqa: BLE001
            if allow_empty_response and isinstance(response.body, bytes) and response.body.strip() == b"":
                payload = {}
            else:
                if response.body:
                    raise ValidationError(f"Provider response was not JSON for {operation}") from exc
                raise ValidationError(f"Empty provider response for {operation}") from exc

        req = ApiRequest(
            operation=operation,
            method=method,
            host=host,
            path=path.lstrip("/"),
            params=cleaned_params,
            body=request_body,
        ).as_dict()

        if request_body is None:
            req.pop("body", None)
        return payload, req

    @staticmethod
    def _host_for(family: ApiFamily) -> str:
        if family == "account-management":
            return ACCOUNT_MANAGEMENT_HOST
        if family == "business-info":
            return BUSINESS_INFORMATION_HOST
        if family == "notifications":
            return NOTIFICATIONS_HOST
        if family == "business-calls":
            return BUSINESS_CALLS_HOST
        if family == "media-upload-v1":
            return MEDIA_UPLOAD_HOST
        if family == "legacy-v49":
            return LEGACY_V49_HOST
        if family == "performance":
            return PERFORMANCE_HOST
        if family == "lodging":
            return LODGING_HOST
        if family == "place-actions":
            return PLACE_ACTIONS_HOST
        if family == "verifications":
            return VERIFICATIONS_HOST
        raise ValidationError(f"Unknown API family: {family}")

    def fetch_verification_options(
        self,
        *,
        location: str,
        language_code: str,
        context: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        body: dict[str, Any] = {"languageCode": language_code}
        if context is not None:
            body["context"] = context
        return self._request(
            family="verifications",
            operation="verifications.locations.fetch-verification-options",
            method="POST",
            path=f"{_resource_path(location)}:fetchVerificationOptions",
            body=body,
        )

    def get_voice_of_merchant_state(
        self,
        *,
        name: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="verifications",
            operation="verifications.locations.get-voice-of-merchant-state",
            method="GET",
            path=f"{_resource_path(name)}/VoiceOfMerchantState",
        )

    def list_verifications(
        self,
        *,
        parent: str,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="verifications",
            operation="verifications.locations.verifications.list",
            method="GET",
            path=f"{_resource_path(parent)}/verifications",
            params={"pageSize": page_size, "pageToken": page_token},
        )

    def verify_location(
        self,
        *,
        name: str,
        method: str,
        language_code: str | None = None,
        mailer_contact: str | None = None,
        phone_number: str | None = None,
        email_address: str | None = None,
        context: dict[str, Any] | None = None,
        token: dict[str, Any] | None = None,
        trusted_partner_token: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        body: dict[str, Any] = {"method": method}
        if language_code is not None:
            body["languageCode"] = language_code
        if mailer_contact is not None:
            body["mailerContact"] = mailer_contact
        if phone_number is not None:
            body["phoneNumber"] = phone_number
        if email_address is not None:
            body["emailAddress"] = email_address
        if context is not None:
            body["context"] = context
        if token is not None:
            body["token"] = token
        if trusted_partner_token is not None:
            body["trustedPartnerToken"] = trusted_partner_token
        return self._request(
            family="verifications",
            operation="verifications.locations.verify",
            method="POST",
            path=f"{_resource_path(name)}:verify",
            body=body,
        )

    def generate_verification_token(
        self,
        *,
        location_id: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="verifications",
            operation="verifications.verification-tokens.generate",
            method="POST",
            path="v1/verificationTokens:generate",
            body={"locationId": location_id},
        )

    def complete_verification(
        self,
        *,
        name: str,
        pin: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="verifications",
            operation="verifications.locations.verifications.complete",
            method="POST",
            path=f"{_resource_path(name)}:complete",
            body={"pin": pin},
        )

    def fetch_multi_daily_metrics_time_series(
        self,
        *,
        location: str,
        daily_metrics: list[str],
        daily_range_start_year: int,
        daily_range_start_month: int,
        daily_range_start_day: int,
        daily_range_end_year: int,
        daily_range_end_month: int,
        daily_range_end_day: int,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="performance",
            operation="performance.locations.fetch-multi-daily-metrics-time-series",
            method="GET",
            path=f"{_resource_path(location)}:fetchMultiDailyMetricsTimeSeries",
            params={
                "dailyMetrics": daily_metrics,
                "dailyRange.startDate.year": daily_range_start_year,
                "dailyRange.startDate.month": daily_range_start_month,
                "dailyRange.startDate.day": daily_range_start_day,
                "dailyRange.endDate.year": daily_range_end_year,
                "dailyRange.endDate.month": daily_range_end_month,
                "dailyRange.endDate.day": daily_range_end_day,
            },
        )

    def get_daily_metrics_time_series(
        self,
        *,
        name: str,
        daily_metric: str,
        daily_range_start_year: int,
        daily_range_start_month: int,
        daily_range_start_day: int,
        daily_range_end_year: int,
        daily_range_end_month: int,
        daily_range_end_day: int,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="performance",
            operation="performance.locations.get-daily-metrics-time-series",
            method="GET",
            path=f"{_resource_path(name)}:getDailyMetricsTimeSeries",
            params={
                "dailyMetric": daily_metric,
                "dailyRange.startDate.year": daily_range_start_year,
                "dailyRange.startDate.month": daily_range_start_month,
                "dailyRange.startDate.day": daily_range_start_day,
                "dailyRange.endDate.year": daily_range_end_year,
                "dailyRange.endDate.month": daily_range_end_month,
                "dailyRange.endDate.day": daily_range_end_day,
            },
        )

    def list_search_keywords_impressions_monthly(
        self,
        *,
        parent: str,
        monthly_range_start_year: int,
        monthly_range_start_month: int,
        monthly_range_end_year: int,
        monthly_range_end_month: int,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="performance",
            operation="performance.locations.search-keywords.impressions.monthly.list",
            method="GET",
            path=_resource_path(parent, "searchkeywords/impressions/monthly"),
            params={
                "monthlyRange.startMonth.year": monthly_range_start_year,
                "monthlyRange.startMonth.month": monthly_range_start_month,
                "monthlyRange.endMonth.year": monthly_range_end_year,
                "monthlyRange.endMonth.month": monthly_range_end_month,
                "pageSize": page_size,
                "pageToken": page_token,
            },
        )

    def get_lodging(
        self,
        *,
        name: str,
        read_mask: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="lodging",
            operation="lodging.locations.get-lodging",
            method="GET",
            path=_lodging_resource_path(name),
            params={"readMask": read_mask},
        )

    def update_lodging(
        self,
        *,
        name: str,
        update_mask: str,
        body: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="lodging",
            operation="lodging.locations.update-lodging",
            method="PATCH",
            path=_lodging_resource_path(name),
            params={"updateMask": update_mask},
            body=body,
        )

    def get_lodging_google_updated(
        self,
        *,
        name: str,
        read_mask: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="lodging",
            operation="lodging.locations.lodging.get-google-updated",
            method="GET",
            path=f"{_lodging_resource_path(name)}:getGoogleUpdated",
            params={"readMask": read_mask},
        )

    def get_business_calls_settings(
        self,
        *,
        name: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="business-calls",
            operation="business-calls.locations.get-business-calls-settings",
            method="GET",
            path=_business_calls_resource_path(name),
        )

    def update_business_calls_settings(
        self,
        *,
        name: str,
        update_mask: str,
        body: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="business-calls",
            operation="business-calls.locations.update-business-calls-settings",
            method="PATCH",
            path=_business_calls_resource_path(name),
            params={"updateMask": update_mask},
            body=body,
        )

    def list_business_calls_insights(
        self,
        *,
        parent: str,
        page_size: int | None = None,
        page_token: str | None = None,
        filter: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="business-calls",
            operation="business-calls.locations.business-calls-insights.list",
            method="GET",
            path=_resource_path(parent, "businesscallsinsights"),
            params={"pageSize": page_size, "pageToken": page_token, "filter": filter},
        )

    def start_upload_location_media(
        self,
        *,
        parent: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="legacy-v49",
            operation="legacy-v49.accounts.locations.media.start-upload",
            method="POST",
            path=f"v4/{parent}:startUpload",
        )

    def list_legacy_reviews(
        self,
        *,
        parent: str,
        page_size: int | None = None,
        page_token: str | None = None,
        order_by: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="legacy-v49",
            operation="legacy-v49.accounts.locations.reviews.list",
            method="GET",
            path=f"v4/{parent}/reviews",
            params={"pageSize": page_size, "pageToken": page_token, "orderBy": order_by},
        )

    def list_legacy_verifications(
        self,
        *,
        parent: str,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="legacy-v49",
            operation="legacy-v49.accounts.locations.verifications.list",
            method="GET",
            path=f"v4/{parent}/verifications",
            params={"pageSize": page_size, "pageToken": page_token},
        )

    def get_legacy_review(
        self,
        *,
        name: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="legacy-v49",
            operation="legacy-v49.accounts.locations.reviews.get",
            method="GET",
            path=f"v4/{name}",
        )

    def update_review_reply(
        self,
        *,
        name: str,
        review_reply: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="legacy-v49",
            operation="legacy-v49.accounts.locations.reviews.update-reply",
            method="PUT",
            path=f"v4/{name}/reply",
            body=review_reply,
        )

    def delete_review_reply(
        self,
        *,
        name: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="legacy-v49",
            operation="legacy-v49.accounts.locations.reviews.delete-reply",
            method="DELETE",
            path=f"v4/{name}/reply",
            allow_empty_response=True,
        )

    def complete_legacy_verification(
        self,
        *,
        name: str,
        pin: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="legacy-v49",
            operation="legacy-v49.accounts.locations.verifications.complete",
            method="POST",
            path=f"v4/{name}:complete",
            body={"pin": pin},
        )

    def create_location_media(
        self,
        *,
        parent: str,
        media_item: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="legacy-v49",
            operation="legacy-v49.accounts.locations.media.create",
            method="POST",
            path=f"v4/{parent}/media",
            body=media_item,
        )

    def transfer_legacy_location(
        self,
        *,
        name: str,
        to_account: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="legacy-v49",
            operation="legacy-v49.accounts.locations.transfer",
            method="POST",
            path=f"v4/{name}:transfer",
            body={"toAccount": to_account},
        )

    def list_accounts(
        self,
        *,
        parent_account: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
        filter: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        params: dict[str, Any] = {"parentAccount": parent_account, "pageSize": page_size, "pageToken": page_token, "filter": filter}
        return self._request(
            family="account-management",
            operation="account-management.accounts.list",
            method="GET",
            path="v1/accounts",
            params=params,
        )

    def create_account(
        self,
        *,
        body: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="account-management",
            operation="account-management.accounts.create",
            method="POST",
            path="v1/accounts",
            body=body,
        )

    def create_account_admin(
        self,
        *,
        parent: str,
        body: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="account-management",
            operation="account-management.accounts.admins.create",
            method="POST",
            path=f"{_resource_path(parent)}/admins",
            body=body,
        )

    def create_location_admin(
        self,
        *,
        parent: str,
        body: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="account-management",
            operation="account-management.locations.admins.create",
            method="POST",
            path=f"{_resource_path(parent)}/admins",
            body=body,
        )

    def delete_account_admin(
        self,
        *,
        name: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="account-management",
            operation="account-management.accounts.admins.delete",
            method="DELETE",
            path=_resource_path(name),
            allow_empty_response=True,
        )

    def delete_location_admin(
        self,
        *,
        name: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="account-management",
            operation="account-management.locations.admins.delete",
            method="DELETE",
            path=_resource_path(name),
            allow_empty_response=True,
        )

    def transfer_location(
        self,
        *,
        name: str,
        destination_account: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="account-management",
            operation="account-management.locations.transfer",
            method="POST",
            path=f"{_resource_path(name)}:transfer",
            body={"destinationAccount": destination_account},
            allow_empty_response=True,
        )

    def patch_account_admin(
        self,
        *,
        name: str,
        update_mask: str,
        body: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="account-management",
            operation="account-management.accounts.admins.patch",
            method="PATCH",
            path=_resource_path(name),
            params={"updateMask": update_mask},
            body=body,
        )

    def patch_location_admin(
        self,
        *,
        name: str,
        update_mask: str,
        body: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="account-management",
            operation="account-management.locations.admins.patch",
            method="PATCH",
            path=_resource_path(name),
            params={"updateMask": update_mask},
            body=body,
        )

    def get_account(self, *, name: str) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="account-management",
            operation="account-management.accounts.get",
            method="GET",
            path=_resource_path(name),
        )

    def patch_account(
        self,
        *,
        name: str,
        update_mask: str,
        body: dict[str, Any],
        validate_only: bool,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="account-management",
            operation="account-management.accounts.patch",
            method="PATCH",
            path=_resource_path(name),
            params={"updateMask": update_mask, "validateOnly": validate_only},
            body=body,
        )

    def list_account_admins(self, *, parent: str) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="account-management",
            operation="account-management.accounts.admins.list",
            method="GET",
            path=_resource_path(parent, "admins"),
        )

    def list_account_invitations(
        self, *, parent: str, filter: str | None = None
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="account-management",
            operation="account-management.accounts.invitations.list",
            method="GET",
            path=_resource_path(parent, "invitations"),
            params={"filter": filter},
        )

    def accept_account_invitation(
        self,
        *,
        name: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="account-management",
            operation="account-management.accounts.invitations.accept",
            method="POST",
            path=f"{_resource_path(name)}:accept",
            body={},
            allow_empty_response=True,
        )

    def decline_account_invitation(
        self,
        *,
        name: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="account-management",
            operation="account-management.accounts.invitations.decline",
            method="POST",
            path=f"{_resource_path(name)}:decline",
            body={},
            allow_empty_response=True,
        )

    def list_location_admins(self, *, parent: str) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="account-management",
            operation="account-management.locations.admins.list",
            method="GET",
            path=_resource_path(parent, "admins"),
        )

    def list_business_info_locations(
        self,
        *,
        parent: str,
        read_mask: str,
        page_size: int | None = None,
        page_token: str | None = None,
        filter: str | None = None,
        order_by: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        params = {
            "readMask": read_mask,
            "pageSize": page_size,
            "pageToken": page_token,
            "filter": filter,
            "orderBy": order_by,
        }
        return self._request(
            family="business-info",
            operation="business-info.accounts.locations.list",
            method="GET",
            path=_resource_path(parent, "locations"),
            params=params,
        )

    def get_location(self, *, name: str, read_mask: str) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="business-info",
            operation="business-info.locations.get",
            method="GET",
            path=_resource_path(name),
            params={"readMask": read_mask},
        )

    def get_location_attributes(self, *, name: str) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="business-info",
            operation="business-info.locations.get-attributes",
            method="GET",
            path=_resource_path(name),
        )

    def get_location_google_updated(
        self, *, name: str, read_mask: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="business-info",
            operation="business-info.locations.get-google-updated",
            method="GET",
            path=f"{_resource_path(name)}:getGoogleUpdated",
            params={"readMask": read_mask},
        )

    def list_attributes(
        self,
        *,
        parent: str | None = None,
        category_name: str | None = None,
        region_code: str | None = None,
        language_code: str | None = None,
        show_all: bool = False,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        params: dict[str, Any] = {
            "parent": parent,
            "categoryName": category_name,
            "regionCode": region_code,
            "languageCode": language_code,
            "showAll": bool(show_all),
            "pageSize": page_size,
            "pageToken": page_token,
        }
        return self._request(
            family="business-info",
            operation="business-info.attributes.list",
            method="GET",
            path="v1/attributes",
            params=params,
        )

    def batch_get_categories(
        self,
        *,
        names: list[str],
        language_code: str,
        view: str,
        region_code: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="business-info",
            operation="business-info.categories.batch-get",
            method="GET",
            path="v1/categories:batchGet",
            params={
                "names": names,
                "languageCode": language_code,
                "view": view,
                "regionCode": region_code,
            },
        )

    def list_categories(
        self,
        *,
        region_code: str,
        language_code: str,
        view: str,
        filter: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="business-info",
            operation="business-info.categories.list",
            method="GET",
            path="v1/categories",
            params={
                "regionCode": region_code,
                "languageCode": language_code,
                "view": view,
                "filter": filter,
                "pageSize": page_size,
                "pageToken": page_token,
            },
        )

    def search_chains(
        self,
        *,
        chain_name: str,
        page_size: int | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="business-info",
            operation="business-info.chains.search",
            method="GET",
            path="v1/chains:search",
            params={"chainName": chain_name, "pageSize": page_size},
        )

    def get_chain(self, *, name: str) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="business-info",
            operation="business-info.chains.get",
            method="GET",
            path=_resource_path(name),
        )

    def search_google_locations(
        self,
        *,
        page_size: int | None = None,
        query: str | None = None,
        location: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        body: dict[str, Any] = {}
        if query is not None:
            body["query"] = query
        if location is not None:
            body["location"] = location
        if page_size is not None:
            body["pageSize"] = page_size

        return self._request(
            family="business-info",
            operation="business-info.google-locations.search",
            method="POST",
            path="v1/googleLocations:search",
            body=body,
        )

    def get_location_attributes_google_updated(self, *, name: str) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="business-info",
            operation="business-info.locations.attributes.get-google-updated",
            method="GET",
            path=f"{_resource_path(name)}:getGoogleUpdated",
        )

    def patch_location(
        self,
        *,
        name: str,
        update_mask: str,
        body: dict[str, Any],
        validate_only: bool,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="business-info",
            operation="business-info.locations.patch",
            method="PATCH",
            path=_resource_path(name),
            params={"updateMask": update_mask, "validateOnly": validate_only},
            body=body,
        )

    def create_location(
        self,
        *,
        parent: str,
        body: dict[str, Any],
        validate_only: bool,
        request_id: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="business-info",
            operation="business-info.accounts.locations.create",
            method="POST",
            path=_resource_path(parent, "locations"),
            params={"validateOnly": validate_only, "requestId": request_id},
            body=body,
        )

    def update_attributes(
        self,
        *,
        name: str,
        attribute_mask: str,
        body: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="business-info",
            operation="business-info.locations.update-attributes",
            method="PATCH",
            path=_resource_path(name),
            params={"attributeMask": attribute_mask},
            body=body,
        )

    def get_notification_setting(
        self, *, name: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="notifications",
            operation="notifications.accounts.get-notification-setting",
            method="GET",
            path=_resource_path(name),
        )

    def update_notification_setting(
        self,
        *,
        name: str,
        update_mask: str,
        body: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="notifications",
            operation="notifications.accounts.update-notification-setting",
            method="PATCH",
            path=_resource_path(name),
            params={"updateMask": update_mask},
            body=body,
        )

    def create_place_action_link(
        self,
        *,
        parent: str,
        body: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="place-actions",
            operation="place-actions.locations.place-action-links.create",
            method="POST",
            path=_resource_path(parent, "placeActionLinks"),
            body=body,
        )

    def get_place_action_link(
        self,
        *,
        name: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="place-actions",
            operation="place-actions.locations.place-action-links.get",
            method="GET",
            path=_resource_path(name),
        )

    def list_place_action_links(
        self,
        *,
        parent: str,
        page_size: int | None = None,
        page_token: str | None = None,
        filter: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="place-actions",
            operation="place-actions.locations.place-action-links.list",
            method="GET",
            path=_resource_path(parent, "placeActionLinks"),
            params={"filter": filter, "pageSize": page_size, "pageToken": page_token},
        )

    def patch_place_action_link(
        self,
        *,
        name: str,
        update_mask: str,
        body: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="place-actions",
            operation="place-actions.locations.place-action-links.patch",
            method="PATCH",
            path=_resource_path(name),
            params={"updateMask": update_mask},
            body=body,
        )

    def delete_place_action_link(
        self,
        *,
        name: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="place-actions",
            operation="place-actions.locations.place-action-links.delete",
            method="DELETE",
            path=_resource_path(name),
            allow_empty_response=True,
        )

    def list_place_action_type_metadata(
        self,
        *,
        language_code: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
        filter: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="place-actions",
            operation="place-actions.place-action-type-metadata.list",
            method="GET",
            path="v1/placeActionTypeMetadata",
            params={
                "languageCode": language_code,
                "pageSize": page_size,
                "pageToken": page_token,
                "filter": filter,
            },
        )

    def delete_location(self, *, name: str) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="business-info",
            operation="business-info.locations.delete",
            method="DELETE",
            path=_resource_path(name),
            allow_empty_response=True,
        )

    def upload_media_metadata(
        self,
        *,
        resource_name: str,
        body: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request(
            family="media-upload-v1",
            operation="media-upload-v1.media.upload",
            method="POST",
            path=f"v1/media/{resource_name.strip('/')}",
            body=body,
        )

    def upload_media_file(
        self,
        *,
        resource_name: str,
        data: bytes,
        content_type: str | None = None,
        request_body: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._request_with_data(
            family="media-upload-v1",
            operation="media-upload-v1.media.upload",
            method="POST",
            path=f"upload/v1/media/{resource_name.strip('/')}",
            params={"upload_type": "media"},
            data=data,
            content_type=content_type or "application/octet-stream",
            request_body=request_body,
            allow_empty_response=False,
        )

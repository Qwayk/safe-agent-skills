from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import google.auth
from google.auth.transport.requests import Request

ADC_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


@dataclass(frozen=True)
class AdcState:
    credentials: Any
    project_id: str | None
    quota_project_id: str | None
    refreshed: bool


def credential_identity(state: AdcState) -> tuple[str, str]:
    credentials = state.credentials
    email = getattr(credentials, "service_account_email", None)
    refresh_token = getattr(credentials, "refresh_token", None)
    if isinstance(email, str) and email and email != "default":
        subject = getattr(credentials, "_subject", None) or email
        identity = f"service-account:{email}:{subject}"
        label = str(subject)
    elif isinstance(refresh_token, str) and refresh_token:
        identity = f"user-adc:{refresh_token}"
        label = getattr(credentials, "account", "") or "Google user credentials on this machine"
    else:
        raise RuntimeError("Google credentials do not identify a stable account for a write plan. Use ADC for a Google user or a named service account.")
    return label, hashlib.sha256(identity.encode("utf-8")).hexdigest()


def load_adc_credentials(*, quota_project_id: str | None) -> AdcState:
    creds, project_id = google.auth.default(scopes=ADC_SCOPES, quota_project_id=quota_project_id or None)
    refreshed = False
    if not getattr(creds, "valid", False) or not getattr(creds, "token", None):
        creds.refresh(Request())
        refreshed = True
    if not getattr(creds, "token", None):
        raise RuntimeError("ADC credentials did not produce an access token")
    resolved_quota_project = quota_project_id or getattr(creds, "quota_project_id", None)
    return AdcState(
        credentials=creds,
        project_id=project_id,
        quota_project_id=resolved_quota_project,
        refreshed=refreshed,
    )


from __future__ import annotations


class ToolError(Exception):
    """Controlled runtime error used to generate structured output."""


class ValidationError(ToolError):
    """Invalid user input or local state."""


class SafetyError(ToolError):
    """Safe refusal due to missing approvals or mismatch checks."""


class AuthError(ToolError):
    """Missing or invalid API credentials for an authenticated operation."""


class ProviderError(ToolError):
    """A provider-level error that should expose code/message cleanly."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status: int | None = None,
        request_id: str | None = None,
        api_version: str | None = None,
        rate_limits: dict[str, str] | None = None,
        retry_after: str | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.request_id = request_id
        self.api_version = api_version
        self.rate_limits = rate_limits or {}
        self.retry_after = retry_after

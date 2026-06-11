from __future__ import annotations


class ToolError(Exception):
    """
    Base class for predictable errors we want to surface cleanly in JSON output.
    """


class ValidationError(ToolError):
    """
    Invalid user input (bad flags, missing required fields, malformed files).
    """


class SafetyError(ToolError):
    """
    Refused operation due to safety gates (missing --apply/--yes/ack, drift detected, etc.).
    """


class NotSupportedError(ToolError):
    """
    The tool/API does not support the requested operation (or it's intentionally not implemented yet).
    """


class HttpError(ToolError):
    """
    Non-2xx HTTP response metadata without leaking response bodies.
    """

    def __init__(
        self,
        *,
        status_code: int,
        url: str,
        reason: str | None = None,
        request_id: str | None = None,
    ) -> None:
        parts = [f"HTTP {status_code}"]
        if reason:
            parts.append(reason)
        parts.append(f"for {url}")
        if request_id:
            parts.append(f"(request_id={request_id})")
        super().__init__(" ".join(parts))
        self.status_code = status_code
        self.url = url
        self.reason = reason
        self.request_id = request_id

from __future__ import annotations


class ToolError(Exception):
    """Base class for user-facing and runtime failures."""


class ValidationError(ToolError):
    """Invalid input, bad flags, malformed plan, or bad response parsing."""


class SafetyError(ToolError):
    """Intentional safety refusal before any write is applied."""


class StateError(ToolError):
    """State persistence, permissions, or path safety failure."""


class HttpResponseError(ValidationError):
    """Provider returned a non-success status code."""

    def __init__(self, message: str, *, status: int, response: object) -> None:
        self.status = status
        self.response = response
        super().__init__(message)

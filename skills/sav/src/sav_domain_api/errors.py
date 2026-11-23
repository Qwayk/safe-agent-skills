from __future__ import annotations


class ToolError(Exception):
    """Base class for user-facing and runtime failures."""


class ValidationError(ToolError):
    """Invalid input, bad flags, malformed plan, or bad response parsing."""


class SafetyError(ToolError):
    """Intentional safety refusal before any write is applied."""


class StateError(ToolError):
    """State persistence, permissions, or path safety failure."""


class StateFileExistsError(StateError):
    """A private file that must be new already exists."""


class HttpResponseError(ValidationError):
    """Provider returned an error or a reply the CLI could not read."""

    def __init__(
        self, message: str, *, status: int, response: object, parsed: bool = True
    ) -> None:
        self.status = status
        self.response = response
        self.parsed = parsed
        super().__init__(message)

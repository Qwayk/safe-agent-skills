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
    Refused operation due to safety gates (missing confirmations, unsafe params, etc.).
    """


class NotSupportedError(ToolError):
    """
    The tool/API does not support the requested operation (or it's intentionally not implemented yet).
    """


class RemoteApiError(ToolError):
    """
    A remote API returned a structured error response.

    Keep messages non-secret and safe for stdout.
    """

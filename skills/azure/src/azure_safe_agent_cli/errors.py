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


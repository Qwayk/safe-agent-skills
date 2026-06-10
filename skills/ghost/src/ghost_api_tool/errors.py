from __future__ import annotations


class ToolError(Exception):
    """
    Base class for expected, user-facing tool errors.

    The CLI wrapper converts these into a single JSON error object (or a refusal),
    without stack traces unless --debug is set.
    """


class SafetyError(ToolError):
    """
    Safety refusal (safe no-op).

    Must exit 0 with: {"ok": true, "refused": true, ...}
    """


class ValidationError(ToolError):
    """
    Invalid user input (non-zero exit, ok=false).
    """


class NotSupported(ToolError):
    """
    Feature/API not supported (non-zero exit, ok=false).
    """


class VerificationError(ToolError):
    """
    Post-apply verification failed (non-zero exit, ok=false).
    """

from __future__ import annotations


class ToolError(Exception):
    """Base class for predictable CLI errors."""


class ValidationError(ToolError):
    """Input or argument validation failures."""


class NotSupportedError(ToolError):
    """Unsupported operation."""

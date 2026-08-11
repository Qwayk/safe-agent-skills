class ToolError(Exception):
    """Controlled errors surfaced to structured JSON output."""


class ValidationError(ToolError):
    """Invalid inputs or local config."""

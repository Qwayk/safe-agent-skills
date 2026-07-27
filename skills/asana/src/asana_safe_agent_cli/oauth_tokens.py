"""OAuth lifecycle and token storage are outside this tool's product boundary."""

from __future__ import annotations


def oauth_lifecycle_supported() -> bool:
    """Return the explicit product decision for callers inspecting the package."""
    return False

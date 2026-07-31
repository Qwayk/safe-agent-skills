"""SAV Domain APIs v1 CLI package."""

from typing import Any, cast

from .operations_generated import OPERATIONS as INVENTORY

__version__ = "0.1.4"
OPERATIONS = cast(list[dict[str, Any]], INVENTORY["operations"])

__all__ = ["INVENTORY", "OPERATIONS", "__version__"]

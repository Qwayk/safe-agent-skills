from __future__ import annotations

import re

_CAMEL_BOUNDARY_1 = re.compile(r"(.)([A-Z][a-z]+)")
_CAMEL_BOUNDARY_2 = re.compile(r"([a-z0-9])([A-Z])")


def camel_to_kebab(s: str) -> str:
    s = str(s or "").strip()
    if not s:
        return s
    s = _CAMEL_BOUNDARY_1.sub(r"\1-\2", s)
    s = _CAMEL_BOUNDARY_2.sub(r"\1-\2", s)
    return s.replace("_", "-").lower()


def method_id_to_command_tokens(method_id: str) -> list[str]:
    """
    Google Discovery `method.id` values include a service prefix (example: `webmasters.`).

    Canonical CLI rule:
    - drop the first segment (service prefix)
    - split remaining segments by `.`
    - convert each segment from camelCase to kebab-case
    """
    method_id = str(method_id or "").strip()
    if not method_id or "." not in method_id:
        raise ValueError(f"Invalid discovery method id: {method_id!r}")
    _service, rest = method_id.split(".", 1)
    segments = [camel_to_kebab(seg) for seg in rest.split(".") if seg]
    if not segments:
        raise ValueError(f"Invalid discovery method id: {method_id!r}")
    return segments


def method_id_to_command_str(method_id: str) -> str:
    return " ".join(method_id_to_command_tokens(method_id))


def param_name_to_flag(param_name: str) -> str:
    return "--" + camel_to_kebab(param_name)


def param_name_to_dest(param_name: str) -> str:
    # Argparse dest must be a valid attribute name.
    safe = re.sub(r"[^a-zA-Z0-9_]+", "_", str(param_name))
    return f"p_{safe}"


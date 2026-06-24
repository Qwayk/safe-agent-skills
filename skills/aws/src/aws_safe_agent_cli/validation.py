from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from botocore.validate import ParamValidator

from .errors import ValidationError
from .model_loader import load_operation_model


def load_input_json(raw: str | None) -> Any:
    if raw is None:
        return {}
    text = str(raw).strip()
    if not text:
        return {}
    path = Path(text)
    if path.exists() and path.is_file():
        text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Invalid JSON input: {type(e).__name__}: {e}") from None


def validate_operation_input(*, service_name: str, operation_name: str, input_obj: Any) -> dict[str, Any]:
    if input_obj is None:
        input_obj = {}
    if not isinstance(input_obj, dict):
        raise ValidationError("Input JSON must decode to an object")
    operation = load_operation_model(service_name, operation_name)
    input_shape = operation.input_shape
    if input_shape is None:
        if input_obj:
            raise ValidationError("This AWS operation does not accept input JSON")
        return input_obj
    errors = ParamValidator().validate(input_obj, input_shape)
    if errors.has_errors():
        report = errors.generate_report().strip()
        raise ValidationError(report or "Invalid input JSON")
    return input_obj


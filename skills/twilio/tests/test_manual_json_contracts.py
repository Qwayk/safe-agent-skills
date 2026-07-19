from __future__ import annotations

import json
import unittest

from twilio_safe_agent_cli.errors import ValidationError
from twilio_safe_agent_cli.openapi_inventory import has_unbounded_request_schema
from twilio_safe_agent_cli.runtime import _validate_schema_value


class TestManualJsonContracts(unittest.TestCase):
    def test_exact_named_native_flexible_object_is_bounded_and_validated(self) -> None:
        schema = {
            "type": "object",
            "x-qwayk-documented-flexible-json": True,
        }
        self.assertFalse(has_unbounded_request_schema(schema))
        _validate_schema_value(
            {"nested": {"value": 1}},
            schema,
            location="body.data",
            fail_closed_object=True,
        )
        with self.assertRaisesRegex(ValidationError, "JSON object"):
            _validate_schema_value([], schema, location="body.data", fail_closed_object=True)

    def test_stringified_json_contract_checks_parse_shape_and_size(self) -> None:
        schema = {
            "type": "string",
            "x-qwayk-json-string": {
                "max_bytes": 64,
                "schema": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
            },
        }
        _validate_schema_value(
            json.dumps({"region": "us1"}),
            schema,
            location="body.Attributes",
            fail_closed_object=False,
        )
        with self.assertRaisesRegex(ValidationError, "valid JSON"):
            _validate_schema_value("{broken", schema, location="body.Attributes", fail_closed_object=False)
        with self.assertRaisesRegex(ValidationError, "JSON object"):
            _validate_schema_value("[]", schema, location="body.Attributes", fail_closed_object=False)
        with self.assertRaisesRegex(ValidationError, "64 bytes"):
            _validate_schema_value(
                json.dumps({"value": "x" * 80}),
                schema,
                location="body.Attributes",
                fail_closed_object=False,
            )


if __name__ == "__main__":
    unittest.main()

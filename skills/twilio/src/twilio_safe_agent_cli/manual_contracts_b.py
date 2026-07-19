"""Manual public request contracts for the second Twilio audit group.

These supplements are intentionally operation-specific.  A flexible JSON value is
allowed only where the cited Twilio contract names that value, and the marker is
kept on that exact schema node so the inventory generator can remain fail closed.
"""

from __future__ import annotations

from typing import Any

Contract = dict[str, Any]
Path = tuple[str, ...]
SchemaPatch = tuple[Path, Any]

_OAI_COMMIT = "1a9189c79a73781ddf45afcd0afd1f210742d68c"
_OAI_ROOT = f"https://github.com/twilio/twilio-oai/blob/{_OAI_COMMIT}/spec/json"


def _sid(prefix: str) -> dict[str, Any]:
    return {
        "type": "string",
        "pattern": rf"^{prefix}[0-9a-fA-F]{{32}}$",
        "minLength": 34,
        "maxLength": 34,
    }


def _flex_object(*, values: dict[str, Any] | bool = True) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": values,
        "x-qwayk-documented-flexible-json": True,
    }


def _json_string(schema: dict[str, Any], *, max_bytes: int) -> dict[str, Any]:
    return {
        "type": "string",
        "x-qwayk-json-string": {"schema": schema, "max_bytes": max_bytes},
    }


def _entry(
    *,
    sources: tuple[str, ...],
    disposition: str,
    reason: str,
    restrictions: tuple[str, ...],
    duplicate_of: str | None = None,
    schema_patches: dict[str, tuple[SchemaPatch, ...]] | None = None,
    drop_paths: dict[str, tuple[Path, ...]] | None = None,
    risk_add: tuple[str, ...] = (),
    risk_remove: tuple[str, ...] = (),
    snapshot_strategy: str | None = None,
    verification_strategy: str | None = None,
    snapshot_required: bool = False,
    expected_effect: str | None = None,
    pii_fields_add: tuple[str, ...] = (),
) -> Contract:
    value: Contract = {
        "sources": sources,
        "disposition": disposition,
        "reason": reason,
        "restrictions": restrictions,
    }
    if duplicate_of is not None:
        value["duplicate_of"] = duplicate_of
    if schema_patches:
        value["schema_patches"] = schema_patches
    if drop_paths:
        value["drop_paths"] = drop_paths
    if risk_add:
        value["risk_add"] = risk_add
    if risk_remove:
        value["risk_remove"] = risk_remove
    if snapshot_strategy:
        value["snapshot_strategy"] = snapshot_strategy
    if verification_strategy:
        value["verification_strategy"] = verification_strategy
    if snapshot_required:
        value["snapshot_required"] = True
    if expected_effect:
        value["expected_effect"] = expected_effect
    if pii_fields_add:
        value["pii_fields_add"] = pii_fields_add
    return value


def _patches(
    *items: SchemaPatch,
    media_type: str = "application/x-www-form-urlencoded",
) -> dict[str, tuple[SchemaPatch, ...]]:
    return {media_type: items}


_E164 = {"type": "string", "pattern": r"^\+[1-9][0-9]{1,14}$"}
_STRING_MAP = _flex_object(values={"type": "string"})
_FLEX_OBJECT_STRING_16K = _json_string(_flex_object(), max_bytes=16 * 1024)
_STRING_MAP_1K = _json_string(_STRING_MAP, max_bytes=1024)

_ELIGIBILITY_ITEM = {
    "type": "object",
    "properties": {
        "phone_number": _E164,
        "hosting_account_sid": _sid("AC"),
    },
    "required": ["phone_number"],
    "additionalProperties": False,
}

_STUDIO_WIDGET_PROPERTY_TYPES: dict[str, dict[str, str]] = {
    "trigger": {},
    "capture-payments": {
        "timeout": "integer", "max_attempts": "integer", "security_code": "boolean",
        "postal_code": "string", "payment_connector": "string", "payment_token_type": "string",
        "payment_amount": "string", "currency": "string", "description": "string",
        "valid_card_types": "array", "language": "string", "min_postal_code_length": "integer",
        "payment_method": "string", "bank_account_type": "string", "parameters": "array",
    },
    "connect-call-to": {
        "to": "string", "caller_id": "string", "record": "boolean", "noun": "string",
        "sip_endpoint": "string", "sip_username": "string", "sip_password": "string",
        "timeout": "integer", "time_limit": "string",
    },
    "enqueue-call": {
        "workflow_sid": "string", "queue_name": "string", "priority": "integer",
        "timeout": "integer", "task_attributes": "string", "wait_url": "string",
        "wait_url_method": "string",
    },
    "connect-virtual-agent": {
        "connector": "string", "language": "string", "sentiment_analysis": "string",
        "status_callback": "string",
    },
    "connect-virtual-agent-v2": {
        "configurations": "array", "connector_name": "string", "connector_details": "object",
        "channel": "string", "parameters": "array", "status_callback": "string",
        "status_callback_method": "string", "timeout": "integer", "session_behavior": "string",
        "resume_session_identification_method": "string",
        "resume_session_identification_value": "string", "resume_session_event_name": "string",
    },
    "fork-stream": {
        "stream_action": "string", "stream_name": "string", "stream_transport_type": "string",
        "stream_connector": "string", "stream_url": "string", "stream_track": "string",
        "stream_parameters": "array",
    },
    "gather-input-on-call": {
        "timeout": "integer", "finish_on_key": "string", "stop_gather": "boolean",
        "number_of_digits": "integer", "save_response_as": "string", "say": "string",
        "play": "string", "voice": "string", "language": "string", "loop": "integer",
        "hints": "string", "gather_language": "string", "speech_timeout": "string",
        "speech_model": "string", "profanity_filter": "string",
    },
    "make-http-request": {
        "method": "string", "url": "string", "body": "string", "parameters": "array",
        "content_type": "string", "add_twilio_auth": "boolean",
    },
    "make-outgoing-call-v1": {
        "from": "string", "to": "string", "record": "boolean", "timeout": "integer",
    },
    "make-outgoing-call-v2": {
        "from": "string", "to": "string", "record": "boolean",
        "recording_channels": "string", "recording_status_callback": "string", "trim": "string",
        "detect_answering_machine": "boolean", "machine_detection": "string",
        "machine_detection_timeout": "string", "machine_detection_speech_threshold": "string",
        "machine_detection_speech_end_threshold": "string",
        "machine_detection_silence_timeout": "string", "send_digits": "string",
        "timeout": "integer", "sip_auth_username": "string", "sip_auth_password": "string",
    },
    "record-call": {
        "record_call": "boolean", "recording_status_callback": "string",
        "recording_status_callback_method": "string", "recording_status_callback_events": "string",
        "recording_channels": "string", "trim": "string",
    },
    "record-voicemail": {
        "timeout": "integer", "finish_on_key": "string", "max_length": "integer",
        "transcribe": "boolean", "transcription_callback_url": "string", "trim": "string",
        "play_beep": "string", "recording_status_callback_url": "string",
    },
    "run-function": {"url": "string", "parameters": "array"},
    "say-play": {
        "say": "string", "play": "string", "voice": "string", "language": "string",
        "loop": "integer", "digits": "string",
    },
    "send-and-wait-for-reply": {
        "body": "string", "from": "string", "timeout": "string", "save_response_as": "string",
        "media_url": "string", "service": "string", "channel": "string", "attributes": "string",
        "content_sid": "string", "content_variables": "array", "message_type": "string",
    },
    "send-message": {
        "body": "string", "from": "string", "to": "string", "media_url": "string",
        "service": "string", "channel": "string", "attributes": "string",
        "content_sid": "string", "content_variables": "array", "message_type": "string",
    },
    "send-to-flex": {
        "workflow": "string", "channel": "string", "attributes": "string", "timeout": "string",
        "priority": "string", "waitUrl": "string", "waitUrlMethod": "string",
    },
    "set-variables": {"variables": "array"},
    "split-based-on": {"input": "string"},
}

_STUDIO_REQUIRED_WIDGET_PROPERTIES: dict[str, tuple[str, ...]] = {
    "connect-call-to": ("noun",),
    "connect-virtual-agent": ("connector",),
    "make-http-request": ("url",),
    "make-outgoing-call-v1": ("from", "to"),
    "make-outgoing-call-v2": ("from", "to"),
    "run-function": ("url",),
    "send-and-wait-for-reply": ("from",),
    "send-message": ("from",),
    "send-to-flex": ("workflow", "channel"),
    "split-based-on": ("input",),
}

_STUDIO_TRANSITION = {
    "type": "object",
    "properties": {
        "event": {"type": "string", "minLength": 1},
        "next": {"type": "string", "minLength": 1, "nullable": True},
        "conditions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "friendly_name": {"type": "string"},
                    "arguments": {"type": "array", "items": {"type": "string"}},
                    "type": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["friendly_name", "arguments", "type", "value"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["event"],
    "additionalProperties": False,
}


_STUDIO_PARAMETER = {
    "type": "object",
    "properties": {"key": {"type": "string"}, "value": {"type": "string"}},
    "required": ["key", "value"],
    "additionalProperties": False,
}


def _studio_property_schema(widget: str, name: str, type_name: str) -> dict[str, Any]:
    if type_name == "array":
        if widget == "capture-payments" and name == "valid_card_types":
            return {
                "type": "array",
                "maxItems": 10,
                "uniqueItems": True,
                "items": {
                    "type": "string",
                    "enum": [
                        "amex", "diners-club", "discover", "enroute", "jcb", "maestro",
                        "master-card", "mastercard", "optima", "visa",
                    ],
                },
            }
        return {"type": "array", "maxItems": 1000, "items": _STUDIO_PARAMETER}
    if type_name == "object":
        return {
            "type": "object",
            "properties": {
                "addon_sid": {"type": "string"},
                "installed_addon_sid": {"type": "string"},
                "name": {"type": "string"},
            },
            "required": ["addon_sid", "installed_addon_sid", "name"],
            "additionalProperties": False,
        }
    return {"type": type_name}


def _studio_widget_state(widget: str) -> dict[str, Any]:
    property_types = _STUDIO_WIDGET_PROPERTY_TYPES[widget]
    widget_properties = {
        name: _studio_property_schema(widget, name, type_name)
        for name, type_name in property_types.items()
    }
    properties_schema: dict[str, Any] = {
        "type": "object",
        "properties": widget_properties,
        "additionalProperties": False,
    }
    required_properties = _STUDIO_REQUIRED_WIDGET_PROPERTIES.get(widget)
    if required_properties:
        properties_schema["required"] = list(required_properties)
    state_required = ["type", "transitions"]
    if widget != "trigger":
        state_required.extend(["name", "properties"])
    return {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": [widget]},
            "name": {"type": "string", "minLength": 1},
            "properties": properties_schema,
            "transitions": {"type": "array", "items": _STUDIO_TRANSITION},
        },
        "required": state_required,
        "additionalProperties": False,
    }

_STUDIO_DEFINITION = {
    "type": "object",
    "properties": {
        "$schema": {
            "type": "string",
            "enum": ["https://schemas.twilio.com/studio/draft/2019-09/flow-definition"],
        },
        "description": {"type": "string"},
        "initial_state": {"type": "string", "minLength": 1},
        "flags": {
            "type": "object",
            "properties": {"allow_concurrent_calls": {"type": "boolean"}},
            "required": ["allow_concurrent_calls"],
            "additionalProperties": False,
        },
        "states": {
            "type": "array",
            "minItems": 1,
            "maxItems": 1000,
            "items": {
                "oneOf": [
                    _studio_widget_state(widget)
                    for widget in _STUDIO_WIDGET_PROPERTY_TYPES
                ]
            },
        },
    },
    "required": ["initial_state", "states"],
    "additionalProperties": False,
}
_STUDIO_DEFINITION_STRING = _json_string(_STUDIO_DEFINITION, max_bytes=1024 * 1024)
_STUDIO_PARAMETERS_STRING = _json_string(_flex_object(), max_bytes=1024 * 1024)

_VIDEO_REGION = {
    "type": "object",
    "properties": {
        "video_sources": {"type": "array", "items": {"type": "string"}},
        "x_pos": {"type": "integer", "minimum": 0},
        "y_pos": {"type": "integer", "minimum": 0},
        "z_pos": {"type": "integer", "minimum": -99, "maximum": 99},
        "width": {"type": "integer", "minimum": 16},
        "height": {"type": "integer", "minimum": 16},
        "max_columns": {"type": "integer", "minimum": 1, "maximum": 1000},
        "max_rows": {"type": "integer", "minimum": 1, "maximum": 1000},
        "cells_excluded": {
            "type": "array",
            "items": {"type": "integer", "minimum": 0, "maximum": 999999},
        },
        "reuse": {"type": "string", "enum": ["none", "show_oldest", "show_newest"]},
        "video_sources_excluded": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["video_sources"],
    "additionalProperties": False,
}
_VIDEO_LAYOUT_STRING = _json_string(
    {"type": "object", "minProperties": 1, "additionalProperties": _VIDEO_REGION},
    max_bytes=1024 * 1024,
)


def _video_rule(kind: tuple[str, ...]) -> dict[str, Any]:
    rule_type = {"type": "string", "enum": ["include", "exclude"]}
    return {
        "oneOf": [
            {
                "type": "object",
                "properties": {
                    "type": rule_type,
                    "all": {"type": "boolean", "enum": [True]},
                },
                "required": ["type", "all"],
                "additionalProperties": False,
            },
            {
                "type": "object",
                "properties": {
                    "type": rule_type,
                    "kind": {"type": "string", "enum": list(kind)},
                    "publisher": {"type": "string", "minLength": 1},
                    "track": {"type": "string", "minLength": 1},
                },
                "required": ["type"],
                "anyOf": [
                    {"required": ["kind"], "x-qwayk-condition-only": True},
                    {"required": ["publisher"], "x-qwayk-condition-only": True},
                    {"required": ["track"], "x-qwayk-condition-only": True},
                ],
                "additionalProperties": False,
            },
        ]
    }


def _video_rules(kind: tuple[str, ...]) -> dict[str, Any]:
    return _json_string(
        {
            "type": "array",
            "minItems": 1,
            "maxItems": 20,
            "uniqueItems": True,
            "items": _video_rule(kind),
        },
        max_bytes=1024 * 1024,
    )


_TRANSCRIPTION_CONFIGURATION = {
    "type": "object",
    "properties": {
        "transcriptionEngine": {"type": "string", "enum": ["google", "deepgram"]},
        "speechModel": {
            "type": "string",
            "enum": [
                "nova-3",
                "nova-3-medical",
                "nova-2",
                "telephony",
                "medical_conversation",
                "long",
                "short",
                "telephony_short",
                "medical_dictation",
                "chirp_telephony",
                "chirp",
            ],
        },
        "languageCode": {"type": "string", "minLength": 2},
        "partialResults": {"type": "boolean"},
        "profanityFilter": {"type": "boolean"},
        "enableAutomaticPunctuation": {"type": "boolean"},
        "hints": {"type": "string"},
    },
    "additionalProperties": False,
}
_TRANSCRIPTION_CONFIGURATION_STRING = _json_string(
    _TRANSCRIPTION_CONFIGURATION, max_bytes=16 * 1024
)

_NUMBERS_V1_SCHEMA = f"{_OAI_ROOT}/twilio_numbers_v1.json"
_NUMBERS_V2_SCHEMA = f"{_OAI_ROOT}/twilio_numbers_v2.json"
_PREVIEW_SCHEMA = f"{_OAI_ROOT}/twilio_preview.json"
_PROXY_SCHEMA = f"{_OAI_ROOT}/twilio_proxy_v1.json"
_STUDIO_V1_SCHEMA = f"{_OAI_ROOT}/twilio_studio_v1.json"
_STUDIO_V2_SCHEMA = f"{_OAI_ROOT}/twilio_studio_v2.json"
_SYNC_SCHEMA = f"{_OAI_ROOT}/twilio_sync_v1.json"
_TASKROUTER_SCHEMA = f"{_OAI_ROOT}/twilio_taskrouter_v1.json"
_TRUSTHUB_SCHEMA = f"{_OAI_ROOT}/twilio_trusthub_v1.json"
_VERIFY_SCHEMA = f"{_OAI_ROOT}/twilio_verify_v2.json"
_VIDEO_SCHEMA = f"{_OAI_ROOT}/twilio_video_v1.json"

_NUMBERS_ELIGIBILITY_SOURCES = (
    "https://www.twilio.com/docs/phone-numbers/hosted-numbers/hosted-numbers-api/eligibility-resource",
    _NUMBERS_V1_SCHEMA,
)
_REGULATORY_END_USER_SOURCES = (
    "https://www.twilio.com/docs/phone-numbers/regulatory/api/end-users",
    "https://www.twilio.com/docs/phone-numbers/regulatory/api/end-user-types",
    _NUMBERS_V2_SCHEMA,
)
_REGULATORY_DOCUMENT_SOURCES = (
    "https://www.twilio.com/docs/phone-numbers/regulatory/api/supporting-documents",
    "https://www.twilio.com/docs/phone-numbers/regulatory/api/supporting-document-types",
    _NUMBERS_V2_SCHEMA,
)
_MARKETPLACE_SOURCES = (
    "https://www.twilio.com/docs/marketplace/api/installed-add-ons",
    _PREVIEW_SCHEMA,
)
_PROXY_SOURCES = (
    "https://www.twilio.com/docs/proxy/api/session",
    "https://www.twilio.com/docs/proxy/quickstart",
    "https://www.twilio.com/docs/proxy/proxy-limits",
    _PROXY_SCHEMA,
)
_STUDIO_V1_SOURCES = (
    "https://www.twilio.com/docs/studio/rest-api",
    _STUDIO_V1_SCHEMA,
)
_STUDIO_FLOW_SOURCES = (
    "https://www.twilio.com/docs/studio/rest-api/v2/flow",
    "https://www.twilio.com/docs/studio/rest-api/v2/flow-validate",
    "https://www.twilio.com/docs/studio/rest-api/v2/schemas",
    _STUDIO_V2_SCHEMA,
)
_STUDIO_EXECUTION_SOURCES = (
    "https://www.twilio.com/docs/studio/rest-api/v2/execution",
    _STUDIO_V2_SCHEMA,
)
_SYNC_DOCUMENT_SOURCES = (
    "https://www.twilio.com/docs/sync/api/document-resource",
    _SYNC_SCHEMA,
)
_SYNC_LIST_SOURCES = (
    "https://www.twilio.com/docs/sync/api/listitem-resource",
    _SYNC_SCHEMA,
)
_SYNC_MAP_SOURCES = (
    "https://www.twilio.com/docs/sync/api/map-item-resource",
    _SYNC_SCHEMA,
)
_SYNC_STREAM_SOURCES = (
    "https://www.twilio.com/docs/sync/api/stream-message-resource",
    _SYNC_SCHEMA,
)
_TRUSTHUB_END_USER_SOURCES = (
    "https://www.twilio.com/docs/trust-hub/trusthub-rest-api/enduser-resource",
    "https://www.twilio.com/docs/trust-hub/trusthub-rest-api/endusertype-resource",
    _TRUSTHUB_SCHEMA,
)
_TRUSTHUB_DOCUMENT_SOURCES = (
    "https://www.twilio.com/docs/trust-hub/trusthub-rest-api/supportingdocument-resource",
    "https://www.twilio.com/docs/trust-hub/trusthub-rest-api/supportingdocumentdype-resource",
    _TRUSTHUB_SCHEMA,
)
_VERIFY_CHALLENGE_SOURCES = (
    "https://www.twilio.com/docs/verify/api/challenge",
    _VERIFY_SCHEMA,
)
_VERIFY_FACTOR_SOURCES = (
    "https://www.twilio.com/docs/verify/api/factor",
    _VERIFY_SCHEMA,
)
_VERIFY_VERIFICATION_SOURCES = (
    "https://www.twilio.com/docs/verify/api/verification",
    _VERIFY_SCHEMA,
)
_VIDEO_COMPOSITION_HOOK_SOURCES = (
    "https://www.twilio.com/docs/video/api/composition-hooks",
    _VIDEO_SCHEMA,
)
_VIDEO_COMPOSITION_SOURCES = (
    "https://www.twilio.com/docs/video/api/compositions-resource",
    _VIDEO_SCHEMA,
)
_VIDEO_ROOM_SOURCES = (
    "https://www.twilio.com/docs/video/api/rooms-resource",
    _VIDEO_SCHEMA,
)
_VIDEO_SUBSCRIBE_SOURCES = (
    "https://www.twilio.com/docs/video/api/track-subscriptions",
    _VIDEO_SCHEMA,
)
_VIDEO_RECORDING_SOURCES = (
    "https://www.twilio.com/docs/video/api/recording-rules",
    _VIDEO_SCHEMA,
)
_VIDEO_TRANSCRIPTION_SOURCES = (
    "https://www.twilio.com/docs/video/api/transcriptions",
    _VIDEO_SCHEMA,
)


CONTRACTS: dict[tuple[str, str], Contract] = {
    # Numbers v1
    ("twilio_numbers_v1.json", "CreateEligibility"): _entry(
        sources=_NUMBERS_ELIGIBILITY_SOURCES,
        disposition="command",
        reason="Twilio publishes the complete single-number eligibility request.",
        restrictions=("Exactly one E.164 phone number is accepted.", "Treat the response as an eligibility read."),
        schema_patches=_patches(
            (
                ("properties",),
                {
                    "phone_numbers": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 1,
                        "items": _ELIGIBILITY_ITEM,
                    },
                    "friendly_name": {"type": "string", "minLength": 1, "maxLength": 128},
                },
            ),
            (("required",), ["phone_numbers"]),
            media_type="application/json",
        ),
        risk_add=("read", "sensitive_data", "preview"),
        risk_remove=("write",),
    ),
    ("twilio_numbers_v1.json", "CreateBulkEligibility"): _entry(
        sources=_NUMBERS_ELIGIBILITY_SOURCES,
        disposition="command",
        reason="Twilio publishes the complete asynchronous bulk eligibility request.",
        restrictions=("Twilio accepts up to 1000 numbers, but this tool caps one reviewed plan at 25.", "Poll until the provider reports SUCCESSFUL; queued is not completion."),
        schema_patches=_patches(
            (
                ("properties",),
                {
                    "phone_numbers": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 25,
                        "items": _ELIGIBILITY_ITEM,
                    },
                    "friendly_name": {"type": "string", "minLength": 1, "maxLength": 128},
                },
            ),
            (("required",), ["phone_numbers", "friendly_name"]),
            media_type="application/json",
        ),
        risk_add=("read", "sensitive_data", "preview", "bulk"),
        risk_remove=("write",),
    ),
    ("twilio_numbers_v1.json", "CreatePortingWebhookConfiguration"): _entry(
        sources=(
            "https://www.twilio.com/docs/phone-numbers/port-in/porting-webhooks",
            _NUMBERS_V1_SCHEMA,
        ),
        disposition="command",
        reason="Twilio publishes the complete Public Beta overwrite contract and paired GET.",
        restrictions=(
            "At least one HTTPS target URL is required so an empty request cannot overwrite the current configuration.",
            "notifications_of accepts only the 12 values published in the POST request example; an empty array remains valid.",
        ),
        schema_patches=_patches(
            (
                (),
                {
                    "type": "object",
                    "properties": {
                        "port_in_target_url": {"type": "string", "maxLength": 2048, "x-qwayk-https-url": True},
                        "port_out_target_url": {"type": "string", "maxLength": 2048, "x-qwayk-https-url": True},
                        "notifications_of": {
                            "type": "array",
                            "maxItems": 12,
                            "uniqueItems": True,
                            "items": {
                                "type": "string",
                                "enum": [
                                    "PortInWaitingForSignature",
                                    "PortInInProgress",
                                    "PortInCompleted",
                                    "PortInActionRequired",
                                    "PortInCanceled",
                                    "PortInPhoneNumberWaitingForSignature",
                                    "PortInPhoneNumberSubmitted",
                                    "PortInPhoneNumberPending",
                                    "PortInPhoneNumberCompleted",
                                    "PortInPhoneNumberRejected",
                                    "PortInPhoneNumberCanceled",
                                    "PortOutPhoneNumberCompleted",
                                ],
                            },
                        },
                    },
                    "anyOf": [
                        {"required": ["port_in_target_url"], "x-qwayk-condition-only": True},
                        {"required": ["port_out_target_url"], "x-qwayk-condition-only": True},
                    ],
                    "additionalProperties": False,
                },
            ),
            media_type="application/json",
        ),
        risk_add=("preview",),
        snapshot_strategy="fetch_before_change",
        verification_strategy="refetch_changed_resource",
        snapshot_required=True,
        expected_effect="POST overwrites the existing Porting webhook configuration.",
        pii_fields_add=("port_in_target_url", "port_out_target_url", "url"),
    ),
    ("twilio_numbers_v1.json", "CreateSenderIdRegistration"): _entry(
        sources=(_NUMBERS_V1_SCHEMA,),
        disposition="command",
        reason="The official schema publishes the fixed registration envelope and names data as its flexible object.",
        restrictions=("Flexible JSON is accepted only in data.", "Review all compliance and PII fields; never retry automatically."),
        schema_patches=_patches(
            (("properties", "data"), _flex_object()),
            media_type="application/json",
        ),
        risk_add=("identity_or_compliance", "sensitive_data", "preview"),
    ),
    ("twilio_numbers_v1.json", "CreateSigningRequestConfiguration"): _entry(
        sources=(_NUMBERS_V1_SCHEMA,),
        disposition="private_or_unavailable",
        reason="No public request properties exist in current Twilio docs or schema.",
        restrictions=("Do not expose this account-level signing configuration as a command.",),
    ),
    # Numbers v2
    ("twilio_numbers_v2.json", "CreateBulkHostedNumberOrder"): _entry(
        sources=(
            "https://www.twilio.com/docs/phone-numbers/hosted-numbers",
            _NUMBERS_V2_SCHEMA,
        ),
        disposition="developer_preview",
        reason="Twilio publishes no request properties and says this developing API is not intended for new customers.",
        restrictions=("Keep unavailable until a complete public bulk-order contract is published.",),
    ),
    ("twilio_numbers_v2.json", "CreateEndUser"): _entry(
        sources=_REGULATORY_END_USER_SOURCES,
        disposition="command",
        reason="Twilio publishes the fixed End User envelope and the type-derived Attributes JSON field.",
        restrictions=("Flexible JSON is accepted only in Attributes.", "Fetch the current End User Type before planning."),
        schema_patches=_patches((("properties", "Attributes"), _FLEX_OBJECT_STRING_16K)),
        risk_add=("identity_or_compliance", "sensitive_data", "preview"),
    ),
    ("twilio_numbers_v2.json", "UpdateEndUser"): _entry(
        sources=_REGULATORY_END_USER_SOURCES,
        disposition="command",
        reason="Twilio publishes the update envelope and the type-derived Attributes JSON field.",
        restrictions=("Flexible JSON is accepted only in Attributes.", "Fetch the current End User Type before planning."),
        schema_patches=_patches((("properties", "Attributes"), _FLEX_OBJECT_STRING_16K)),
        risk_add=("identity_or_compliance", "sensitive_data", "preview"),
    ),
    ("twilio_numbers_v2.json", "CreateSupportingDocument"): _entry(
        sources=_REGULATORY_DOCUMENT_SOURCES,
        disposition="command",
        reason="Twilio publishes the fixed Supporting Document envelope and type-derived Attributes JSON field.",
        restrictions=("Flexible JSON is accepted only in Attributes.", "Fetch the current Supporting Document Type before planning."),
        schema_patches=_patches((("properties", "Attributes"), _FLEX_OBJECT_STRING_16K)),
        risk_add=("identity_or_compliance", "sensitive_data", "preview"),
    ),
    ("twilio_numbers_v2.json", "UpdateSupportingDocument"): _entry(
        sources=_REGULATORY_DOCUMENT_SOURCES,
        disposition="command",
        reason="Twilio publishes the update envelope and type-derived Attributes JSON field.",
        restrictions=("Flexible JSON is accepted only in Attributes.", "Fetch the current Supporting Document Type before planning."),
        schema_patches=_patches((("properties", "Attributes"), _FLEX_OBJECT_STRING_16K)),
        risk_add=("identity_or_compliance", "sensitive_data", "preview"),
    ),
    # Deprecated Marketplace Preview aliases
    ("twilio_preview.json", "CreateMarketplaceInstalledAddOn"): _entry(
        sources=_MARKETPLACE_SOURCES,
        disposition="canonical_duplicate",
        duplicate_of="marketplace-v1.create-installed-add-on",
        reason="The Preview route is deprecated and superseded by the stable Marketplace v1 command.",
        restrictions=("Never accept terms through the deprecated alias; use the stable explicit command.",),
    ),
    ("twilio_preview.json", "UpdateMarketplaceInstalledAddOn"): _entry(
        sources=_MARKETPLACE_SOURCES,
        disposition="canonical_duplicate",
        duplicate_of="marketplace-v1.update-installed-add-on",
        reason="The Preview route is deprecated and superseded by the stable Marketplace v1 command.",
        restrictions=("Use the stable explicit command.",),
    ),
    # Proxy
    ("twilio_proxy_v1.json", "CreateSession"): _entry(
        sources=_PROXY_SOURCES,
        disposition="command",
        reason="The Session envelope is public after removing the undocumented Participants array.",
        restrictions=("Participants is rejected; add participants with the fixed participant-create command.", "UniqueName must not contain PII; never retry creation automatically."),
        drop_paths={"application/x-www-form-urlencoded": (("properties", "Participants"),)},
        risk_add=("preview", "production_change"),
    ),
    # Studio v1
    ("twilio_studio_v1.json", "CreateEngagement"): _entry(
        sources=_STUDIO_V1_SOURCES,
        disposition="legacy_eol",
        reason="Twilio removed the Studio v1 Engagement endpoint in January 2019.",
        restrictions=("Do not create a callable command from historical fields.",),
    ),
    ("twilio_studio_v1.json", "CreateExecution"): _entry(
        sources=_STUDIO_V1_SOURCES,
        disposition="command",
        reason="Twilio publishes the fixed execution envelope and named Parameters JSON field.",
        restrictions=("Flexible JSON is accepted only in Parameters.", "Execution can contact people and spend money; never retry automatically and prefer v2."),
        schema_patches=_patches((("properties", "Parameters"), _STUDIO_PARAMETERS_STRING)),
        risk_add=("outbound_contact", "spend", "production_change", "sensitive_data"),
    ),
    # Studio v2
    ("twilio_studio_v2.json", "CreateFlow"): _entry(
        sources=_STUDIO_FLOW_SOURCES,
        disposition="command",
        reason="Twilio publishes the fixed Flow envelope and the official Definition JSON contract.",
        restrictions=("Definition is limited to the official 1 MB flow schema and widgets with a complete current published child schema.", "Publishing may invoke communications or external services; review the plan first."),
        schema_patches=_patches((("properties", "Definition"), _STUDIO_DEFINITION_STRING)),
        risk_add=("production_change",),
    ),
    ("twilio_studio_v2.json", "UpdateFlowValidate"): _entry(
        sources=_STUDIO_FLOW_SOURCES,
        disposition="command",
        reason="Twilio publishes the fixed validation envelope and official Definition JSON contract.",
        restrictions=("Definition is limited to the official 1 MB flow schema and widgets with a complete current published child schema.",),
        schema_patches=_patches((("properties", "Definition"), _STUDIO_DEFINITION_STRING)),
        risk_add=("production_change",),
    ),
    ("twilio_studio_v2.json", "CreateExecution"): _entry(
        sources=_STUDIO_EXECUTION_SOURCES,
        disposition="command",
        reason="Twilio publishes the fixed execution envelope and named Parameters JSON field.",
        restrictions=("Flexible JSON is accepted only in Parameters.", "Do not accept undocumented ExternalId; never retry execution creation automatically."),
        schema_patches=_patches((("properties", "Parameters"), _STUDIO_PARAMETERS_STRING)),
        risk_add=("outbound_contact", "spend", "production_change", "sensitive_data"),
    ),
    ("twilio_studio_v2.json", "UpdateFlow"): _entry(
        sources=_STUDIO_FLOW_SOURCES,
        disposition="command",
        reason="Twilio publishes the fixed Flow update envelope and official Definition JSON contract.",
        restrictions=("Definition is limited to the official 1 MB flow schema and widgets with a complete current published child schema.", "Publishing may invoke communications or external services; review the plan first."),
        schema_patches=_patches((("properties", "Definition"), _STUDIO_DEFINITION_STRING)),
        risk_add=("production_change",),
    ),
    # Sync
    ("twilio_sync_v1.json", "CreateDocument"): _entry(
        sources=_SYNC_DOCUMENT_SOURCES,
        disposition="command",
        reason="Twilio explicitly defines Data as a schema-less JSON object up to 16 KiB.",
        restrictions=("Flexible JSON is accepted only in Data.", "Data may contain PII and creation is not automatically retried."),
        schema_patches=_patches((("properties", "Data"), _FLEX_OBJECT_STRING_16K)),
        risk_add=("sensitive_data",),
    ),
    ("twilio_sync_v1.json", "UpdateDocument"): _entry(
        sources=_SYNC_DOCUMENT_SOURCES,
        disposition="command",
        reason="Twilio explicitly defines Data as a schema-less JSON object up to 16 KiB.",
        restrictions=("Flexible JSON is accepted only in Data.", "Use If-Match optimistic concurrency; do not accept undocumented UniqueName."),
        schema_patches=_patches((("properties", "Data"), _FLEX_OBJECT_STRING_16K)),
        risk_add=("sensitive_data",),
    ),
    ("twilio_sync_v1.json", "CreateSyncListItem"): _entry(
        sources=_SYNC_LIST_SOURCES,
        disposition="command",
        reason="Twilio explicitly defines Data as a schema-less JSON object up to 16 KiB.",
        restrictions=("Flexible JSON is accepted only in Data.", "Ttl aliases ItemTtl and is ignored when both are supplied."),
        schema_patches=_patches((("properties", "Data"), _FLEX_OBJECT_STRING_16K)),
        risk_add=("sensitive_data",),
    ),
    ("twilio_sync_v1.json", "UpdateSyncListItem"): _entry(
        sources=_SYNC_LIST_SOURCES,
        disposition="command",
        reason="Twilio explicitly defines Data as a schema-less JSON object up to 16 KiB.",
        restrictions=("Flexible JSON is accepted only in Data.", "Use If-Match; CollectionTtl is valid only with a data or item-TTL update."),
        schema_patches=_patches((("properties", "Data"), _FLEX_OBJECT_STRING_16K)),
        risk_add=("sensitive_data",),
    ),
    ("twilio_sync_v1.json", "CreateSyncMapItem"): _entry(
        sources=_SYNC_MAP_SOURCES,
        disposition="command",
        reason="Twilio explicitly defines Data as a schema-less JSON object up to 16 KiB.",
        restrictions=("Flexible JSON is accepted only in Data.", "Ttl aliases ItemTtl and is ignored when both are supplied."),
        schema_patches=_patches((("properties", "Data"), _FLEX_OBJECT_STRING_16K)),
        risk_add=("sensitive_data",),
    ),
    ("twilio_sync_v1.json", "UpdateSyncMapItem"): _entry(
        sources=_SYNC_MAP_SOURCES,
        disposition="command",
        reason="Twilio explicitly defines Data as a schema-less JSON object up to 16 KiB.",
        restrictions=("Flexible JSON is accepted only in Data.", "Use If-Match; CollectionTtl is valid only with a data or item-TTL update."),
        schema_patches=_patches((("properties", "Data"), _FLEX_OBJECT_STRING_16K)),
        risk_add=("sensitive_data",),
    ),
    ("twilio_sync_v1.json", "CreateStreamMessage"): _entry(
        sources=_SYNC_STREAM_SOURCES,
        disposition="command",
        reason="Twilio explicitly defines Data as a schema-less JSON object up to 4 KiB.",
        restrictions=("Flexible JSON is accepted only in Data.", "Delivery and order are not guaranteed; never retry automatically."),
        schema_patches=_patches(
            (("properties", "Data"), _json_string(_flex_object(), max_bytes=4 * 1024))
        ),
        risk_add=("sensitive_data", "production_change"),
    ),
    # TaskRouter read-through-POST
    ("twilio_taskrouter_v1.json", "CreateTaskQueueBulkRealTimeStatistics"): _entry(
        sources=(
            "https://www.twilio.com/docs/taskrouter/api/taskqueue-statistics",
            _TASKROUTER_SCHEMA,
        ),
        disposition="command",
        reason="Twilio publishes the complete bulk statistics request; POST is read-only here.",
        restrictions=("queueSids accepts 1 to 50 WQ SIDs.", "Respect the five-requests-per-second limit."),
        schema_patches=_patches(
            (
                ("properties",),
                {
                    "queueSids": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 50,
                        "items": _sid("WQ"),
                    }
                },
            ),
            (("required",), ["queueSids"]),
            media_type="application/json",
        ),
        risk_add=("read",),
        risk_remove=("write", "bulk", "production_change"),
    ),
    # TrustHub
    ("twilio_trusthub_v1.json", "CreateEndUser"): _entry(
        sources=_TRUSTHUB_END_USER_SOURCES,
        disposition="command",
        reason="Twilio publishes the fixed End User envelope and type-derived Attributes JSON field.",
        restrictions=("Flexible JSON is accepted only in Attributes.", "Fetch the current TrustHub End User Type before planning."),
        schema_patches=_patches((("properties", "Attributes"), _FLEX_OBJECT_STRING_16K)),
        risk_add=("identity_or_compliance", "sensitive_data"),
    ),
    ("twilio_trusthub_v1.json", "UpdateEndUser"): _entry(
        sources=_TRUSTHUB_END_USER_SOURCES,
        disposition="command",
        reason="Twilio publishes the update envelope and type-derived Attributes JSON field.",
        restrictions=("Flexible JSON is accepted only in Attributes.", "Fetch the current TrustHub End User Type before planning."),
        schema_patches=_patches((("properties", "Attributes"), _FLEX_OBJECT_STRING_16K)),
        risk_add=("identity_or_compliance", "sensitive_data"),
    ),
    ("twilio_trusthub_v1.json", "CreateSupportingDocument"): _entry(
        sources=_TRUSTHUB_DOCUMENT_SOURCES,
        disposition="command",
        reason="Twilio publishes the fixed Supporting Document envelope and type-derived Attributes JSON field.",
        restrictions=("Flexible JSON is accepted only in Attributes.", "Fetch the current Supporting Document Type before planning."),
        schema_patches=_patches((("properties", "Attributes"), _FLEX_OBJECT_STRING_16K)),
        risk_add=("identity_or_compliance", "sensitive_data"),
    ),
    ("twilio_trusthub_v1.json", "UpdateSupportingDocument"): _entry(
        sources=_TRUSTHUB_DOCUMENT_SOURCES,
        disposition="command",
        reason="Twilio publishes the update envelope and type-derived Attributes JSON field.",
        restrictions=("Flexible JSON is accepted only in Attributes.", "Fetch the current Supporting Document Type before planning."),
        schema_patches=_patches((("properties", "Attributes"), _FLEX_OBJECT_STRING_16K)),
        risk_add=("identity_or_compliance", "sensitive_data"),
    ),
    # Verify
    ("twilio_verify_v2.json", "CreateChallenge"): _entry(
        sources=_VERIFY_CHALLENGE_SOURCES,
        disposition="command",
        reason="Twilio publishes the missing push-field item and HiddenDetails string-map contracts.",
        restrictions=("HiddenDetails accepts only string values and at most 1024 bytes.", "Never retry challenge creation automatically."),
        schema_patches=_patches(
            (
                ("properties", "Details.Fields", "items"),
                {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string", "maxLength": 36},
                        "value": {"type": "string", "maxLength": 128},
                    },
                    "required": ["label", "value"],
                    "additionalProperties": False,
                },
            ),
            (("properties", "Details.Fields", "maxItems"), 20),
            (("properties", "Details.Message", "maxLength"), 256),
            (("properties", "AuthPayload", "minLength"), 3),
            (("properties", "AuthPayload", "maxLength"), 8),
            (("properties", "HiddenDetails"), _STRING_MAP_1K),
        ),
        risk_add=("outbound_contact", "spend", "sensitive_data", "identity_or_compliance"),
    ),
    ("twilio_verify_v2.json", "UpdateChallenge"): _entry(
        sources=_VERIFY_CHALLENGE_SOURCES,
        disposition="command",
        reason="Twilio publishes the missing Metadata string-map contract.",
        restrictions=("Metadata accepts only string values and at most 1024 bytes.",),
        schema_patches=_patches(
            (("properties", "AuthPayload", "minLength"), 3),
            (("properties", "AuthPayload", "maxLength"), 5456),
            (("properties", "Metadata"), _STRING_MAP_1K),
        ),
        risk_add=("sensitive_data", "identity_or_compliance"),
    ),
    ("twilio_verify_v2.json", "CreateNewFactor"): _entry(
        sources=_VERIFY_FACTOR_SOURCES,
        disposition="command",
        reason="Twilio publishes the fixed push/TOTP factor envelope and Metadata string map.",
        restrictions=("Expose only proven factor types push and totp; passkeys remains excluded.", "Never retry factor creation automatically."),
        schema_patches=_patches(
            (("properties", "FactorType", "enum"), ["push", "totp"]),
            (("properties", "FriendlyName", "maxLength"), 64),
            (("properties", "Binding.Alg", "enum"), ["ES256"]),
            (("properties", "Config.AppId", "maxLength"), 100),
            (("properties", "Config.NotificationToken", "minLength"), 32),
            (("properties", "Config.NotificationToken", "maxLength"), 255),
            (("properties", "Config.TimeStep", "minimum"), 20),
            (("properties", "Config.TimeStep", "maximum"), 60),
            (("properties", "Config.Skew", "minimum"), 0),
            (("properties", "Config.Skew", "maximum"), 2),
            (("properties", "Config.CodeLength", "minimum"), 3),
            (("properties", "Config.CodeLength", "maximum"), 8),
            (("properties", "Metadata"), _STRING_MAP_1K),
        ),
        risk_add=("sensitive_data", "identity_or_compliance", "auth_or_permission"),
    ),
    ("twilio_verify_v2.json", "CreateVerification"): _entry(
        sources=_VERIFY_VERIFICATION_SOURCES,
        disposition="command",
        reason="Twilio publishes the fixed verification envelope and exact JSON fields.",
        restrictions=("Flexible JSON is accepted only in the named rate-limit, channel, template-substitution, and tag fields.", "RiskCheck=disable bypasses fraud controls and requires explicit auth review; never retry sends automatically."),
        schema_patches=_patches(
            (("properties", "Channel", "enum"), ["email", "sms", "whatsapp", "call", "sna", "auto"]),
            (("properties", "CustomCode", "minLength"), 4),
            (("properties", "CustomCode", "maxLength"), 10),
            (("properties", "DeviceIp", "format"), "ip"),
            (("properties", "RateLimits"), _json_string(_STRING_MAP, max_bytes=16 * 1024)),
            (
                ("properties", "ChannelConfiguration"),
                _json_string(
                    {
                        "type": "object",
                        "properties": {
                            "from": {"type": "string", "format": "email"},
                            "from_name": {"type": "string"},
                            "template_id": {"type": "string"},
                            "substitutions": _flex_object(),
                        },
                        "additionalProperties": False,
                    },
                    max_bytes=16 * 1024,
                ),
            ),
            (("properties", "TemplateCustomSubstitutions"), _FLEX_OBJECT_STRING_16K),
            (
                ("properties", "Tags"),
                _json_string(
                    {
                        "type": "object",
                        "maxProperties": 10,
                        "additionalProperties": {"type": "string", "maxLength": 128},
                        "x-qwayk-documented-flexible-json": True,
                    },
                    max_bytes=16 * 1024,
                ),
            ),
        ),
        risk_add=("outbound_contact", "spend", "sensitive_data", "auth_or_permission"),
    ),
    # Video
    ("twilio_video_v1.json", "CreateCompositionHook"): _entry(
        sources=_VIDEO_COMPOSITION_HOOK_SOURCES,
        disposition="command",
        reason="Twilio publishes the structured VideoLayout region contract.",
        restrictions=("Either VideoLayout or AudioSources is required.", "Enabling a hook can affect every completed Group Room; review before writing."),
        schema_patches=_patches(
            (("properties", "VideoLayout"), _VIDEO_LAYOUT_STRING),
            (
                ("anyOf",),
                [
                    {"required": ["VideoLayout"], "x-qwayk-condition-only": True},
                    {"required": ["AudioSources"], "x-qwayk-condition-only": True},
                ],
            ),
        ),
        risk_add=("spend", "production_change", "sensitive_data"),
    ),
    ("twilio_video_v1.json", "UpdateCompositionHook"): _entry(
        sources=_VIDEO_COMPOSITION_HOOK_SOURCES,
        disposition="command",
        reason="Twilio publishes the structured VideoLayout region contract.",
        restrictions=("Updates fully replace the hook and omitted properties reset to defaults.", "Either VideoLayout or AudioSources is required."),
        schema_patches=_patches(
            (("properties", "VideoLayout"), _VIDEO_LAYOUT_STRING),
            (
                ("anyOf",),
                [
                    {"required": ["VideoLayout"], "x-qwayk-condition-only": True},
                    {"required": ["AudioSources"], "x-qwayk-condition-only": True},
                ],
            ),
        ),
        risk_add=("spend", "production_change", "sensitive_data", "destructive"),
    ),
    ("twilio_video_v1.json", "CreateComposition"): _entry(
        sources=_VIDEO_COMPOSITION_SOURCES,
        disposition="command",
        reason="Twilio publishes the structured VideoLayout region contract.",
        restrictions=("Either VideoLayout or AudioSources is required.", "Composition is billable and must not be retried automatically."),
        schema_patches=_patches(
            (("properties", "VideoLayout"), _VIDEO_LAYOUT_STRING),
            (
                ("anyOf",),
                [
                    {"required": ["VideoLayout"], "x-qwayk-condition-only": True},
                    {"required": ["AudioSources"], "x-qwayk-condition-only": True},
                ],
            ),
        ),
        risk_add=("spend", "production_change", "sensitive_data"),
    ),
    ("twilio_video_v1.json", "CreateRoom"): _entry(
        sources=_VIDEO_ROOM_SOURCES,
        disposition="command",
        reason="Twilio publishes the Room envelope plus structured recording and transcription fields.",
        restrictions=("Only the supported group room type is exposed for new work.", "Recording or transcription requires documented participant consent; never retry room creation automatically."),
        schema_patches=_patches(
            (("properties", "Type", "enum"), ["group"]),
            (("properties", "MaxParticipants", "minimum"), 1),
            (("properties", "MaxParticipants", "maximum"), 50),
            (("properties", "MaxParticipantDuration", "minimum"), 1),
            (("properties", "MaxParticipantDuration", "maximum"), 86400),
            (("properties", "EmptyRoomTimeout", "minimum"), 1),
            (("properties", "EmptyRoomTimeout", "maximum"), 60),
            (("properties", "UnusedRoomTimeout", "minimum"), 1),
            (("properties", "UnusedRoomTimeout", "maximum"), 60),
            (("properties", "RecordingRules"), _video_rules(("audio", "video"))),
            (("properties", "TranscriptionsConfiguration"), _TRANSCRIPTION_CONFIGURATION_STRING),
        ),
        risk_add=("spend", "production_change", "sensitive_data"),
    ),
    ("twilio_video_v1.json", "UpdateRoomParticipantSubscribeRule"): _entry(
        sources=_VIDEO_SUBSCRIBE_SOURCES,
        disposition="command",
        reason="Twilio publishes the fixed subscribe-rule array and filter contract.",
        restrictions=("Each rule needs at least one filter; all=true is exclusive and duplicate rules are rejected.",),
        schema_patches=_patches(
            (("properties", "Rules"), _video_rules(("audio", "video", "data")))
        ),
        risk_add=("production_change", "sensitive_data"),
    ),
    ("twilio_video_v1.json", "UpdateRoomRecordingRule"): _entry(
        sources=_VIDEO_RECORDING_SOURCES,
        disposition="command",
        reason="Twilio publishes the fixed recording-rule array and filter contract.",
        restrictions=("POST replaces all rules and order matters; snapshot the current rules first.", "Recording changes require participant consent and extra approval."),
        schema_patches=_patches((("properties", "Rules"), _video_rules(("audio", "video")))),
        risk_add=("production_change", "sensitive_data", "destructive"),
    ),
    ("twilio_video_v1.json", "CreateRoomTranscriptions"): _entry(
        sources=_VIDEO_TRANSCRIPTION_SOURCES,
        disposition="command",
        reason="Twilio publishes the transcription Configuration contract.",
        restrictions=("Starting transcription requires participant consent and extra approval.", "Never retry automatically."),
        schema_patches=_patches(
            (("properties", "Configuration"), _TRANSCRIPTION_CONFIGURATION_STRING)
        ),
        risk_add=("spend", "production_change", "sensitive_data"),
    ),
    ("twilio_video_v1.json", "UpdateRoomTranscriptions"): _entry(
        sources=_VIDEO_TRANSCRIPTION_SOURCES,
        disposition="command",
        reason="Twilio publishes the transcription Configuration contract and writable statuses.",
        restrictions=("Only started and stopped are writable; failed is response-only.", "Starting or stopping transcription requires participant-consent review."),
        schema_patches=_patches(
            (("properties", "Configuration"), _TRANSCRIPTION_CONFIGURATION_STRING),
            (("properties", "Status", "enum"), ["started", "stopped"]),
        ),
        risk_add=("spend", "production_change", "sensitive_data"),
    ),
}

if len(CONTRACTS) != 43:  # pragma: no cover - import-time integrity guard
    raise RuntimeError(f"manual_contracts_b must contain 43 entries, got {len(CONTRACTS)}")

"""Audited manual request contracts for the first 38 Twilio schema gaps.

The pinned Twilio OpenAPI files remain the primary source.  These entries only
replace request-schema nodes that the pin leaves untyped, or record an explicit
non-command disposition when Twilio does not publish a safe request contract.
"""

from __future__ import annotations

from typing import Any

OAI_COMMIT = "ef1d81e7b6e49e602530601e913eedc21aedd6da"
OAI_ROOT = f"https://github.com/twilio/twilio-oai/blob/{OAI_COMMIT}/spec/json"


def _object(
    properties: dict[str, Any],
    *,
    required: tuple[str, ...] = (),
    additional_properties: bool = False,
) -> dict[str, Any]:
    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "additionalProperties": additional_properties,
    }
    if required:
        schema["required"] = list(required)
    return schema


def _flexible_object() -> dict[str, Any]:
    return {"type": "object", "x-qwayk-documented-flexible-json": True}


def _json_string(schema: dict[str, Any], *, max_bytes: int = 65_536) -> dict[str, Any]:
    # Twilio does not publish a smaller operation limit for these fields.  The
    # cap is a deliberate safe-CLI subset, not a claim about provider capacity.
    return {
        "type": "string",
        "x-qwayk-json-string": {"schema": schema, "max_bytes": max_bytes},
    }


def _entry(
    *sources: str,
    disposition: str = "command",
    reason: str = "Current official Twilio documentation supplies a fixed request contract.",
    schema_patches: dict[str, tuple[tuple[tuple[Any, ...], dict[str, Any]], ...]] | None = None,
    drop_paths: dict[str, tuple[tuple[Any, ...], ...]] | None = None,
    risk_add: tuple[str, ...] = (),
    risk_remove: tuple[str, ...] = (),
    restrictions: tuple[str, ...] = (),
    parameter_patches: dict[tuple[str, str], dict[str, Any]] | None = None,
    snapshot_strategy: str | None = None,
    verification_strategy: str | None = None,
    snapshot_required: bool = False,
    expected_effect: str | None = None,
    pii_fields_add: tuple[str, ...] = (),
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "sources": tuple(sources),
        "disposition": disposition,
        "reason": reason,
        "restrictions": restrictions,
    }
    if schema_patches:
        entry["schema_patches"] = schema_patches
    if drop_paths:
        entry["drop_paths"] = drop_paths
    if risk_add:
        entry["risk_add"] = risk_add
    if risk_remove:
        entry["risk_remove"] = risk_remove
    if parameter_patches:
        entry["parameter_patches"] = parameter_patches
    if snapshot_strategy:
        entry["snapshot_strategy"] = snapshot_strategy
    if verification_strategy:
        entry["verification_strategy"] = verification_strategy
    if snapshot_required:
        entry["snapshot_required"] = True
    if expected_effect:
        entry["expected_effect"] = expected_effect
    if pii_fields_add:
        entry["pii_fields_add"] = pii_fields_add
    return entry


FORM = "application/x-www-form-urlencoded"
JSON = "application/json"
SCIM_JSON = "application/scim+json"

E164 = {"type": "string", "pattern": r"^\+[1-9][0-9]{1,14}$"}
STRING = {"type": "string"}

CONSENT_ITEM = _object(
    {
        "contact_id": E164,
        "correlation_id": {"type": "string", "format": "uuid"},
        "sender_id": STRING,
        "status": {"type": "string", "enum": ["opt-in", "opt-out"]},
        "source": {
            "type": "string",
            "enum": ["website", "offline", "opt-in-message", "opt-out-message", "others"],
        },
        "date_of_consent": {"type": "string", "format": "date-time"},
    },
    required=("contact_id", "correlation_id", "sender_id", "status", "source"),
)

CONTACT_ITEM = _object(
    {
        "contact_id": E164,
        "correlation_id": {"type": "string", "format": "uuid"},
        "country_iso_code": {"type": "string", "pattern": "^[A-Z]{2}$"},
        "zip_code": STRING,
    },
    required=("contact_id", "correlation_id", "country_iso_code", "zip_code"),
)

FLEX_ROUTING_PROPERTIES = _object(
    {
        "workspace_sid": {"type": "string", "pattern": "^WS[0-9a-fA-F]{32}$"},
        "workflow_sid": {"type": "string", "pattern": "^WW[0-9a-fA-F]{32}$"},
        "queue_sid": {"type": "string", "pattern": "^WQ[0-9a-fA-F]{32}$"},
        "worker_sid": {"type": "string", "pattern": "^WK[0-9a-fA-F]{32}$"},
        "task_channel_unique_name": STRING,
        "attributes": _flexible_object(),
    }
)
FLEX_ROUTING = _object({"properties": FLEX_ROUTING_PROPERTIES}, required=("properties",))
FLEX_CHANNEL = _object(
    {
        "type": {
            "type": "string",
            "enum": ["voice", "sms", "email", "web", "whatsapp", "chat", "messenger", "gbm"],
        },
        "initiated_by": {"type": "string", "enum": ["agent", "customer"]},
        "properties": _object(
            {
                "media_channel_sid": STRING,
                "participant_proxy_address": STRING,
                "participant_target_address": STRING,
            }
        ),
    },
    required=("type", "initiated_by", "properties"),
)

IAM_POLICY = _object(
    {"allow": {"type": "array", "items": STRING, "minItems": 1}},
    required=("allow",),
)

_SCIM_PATCH_SCHEMA = "urn:ietf:params:scim:api:messages:2.0:PatchOp"
_SCIM_USERNAME_EMAIL = {
    "type": "string",
    "minLength": 3,
    "maxLength": 255,
    "pattern": r"^[^\s@]+@[^\s@]+\.[^\s@]+$",
}
_SCIM_PRIMARY_EMAIL = {
    "type": "string",
    "minLength": 3,
    "maxLength": 160,
    "pattern": r"^[^\s@]+@[^\s@]+\.[^\s@]+$",
}


def _scim_replace(path: str, value: dict[str, Any]) -> dict[str, Any]:
    return _object(
        {
            "op": {"type": "string", "enum": ["replace"]},
            "path": {"type": "string", "enum": [path]},
            "value": value,
        },
        required=("op", "path", "value"),
    )


_SCIM_PATCH_REQUEST = _object(
    {
        "schemas": {
            "type": "array",
            "minItems": 1,
            "maxItems": 1,
            "uniqueItems": True,
            "items": {"type": "string", "enum": [_SCIM_PATCH_SCHEMA]},
        },
        "Operations": {
            "type": "array",
            "minItems": 1,
            "maxItems": 8,
            "x-qwayk-unique-by": "path",
            "items": {
                "oneOf": [
                    _scim_replace("active", {"type": "boolean"}),
                    _scim_replace("name.givenName", {"type": "string", "minLength": 1, "maxLength": 255}),
                    _scim_replace("name.familyName", {"type": "string", "minLength": 1, "maxLength": 255}),
                    _scim_replace("displayName", {"type": "string", "minLength": 1, "maxLength": 255}),
                    _scim_replace("timezone", {"type": "string", "minLength": 1, "maxLength": 64}),
                    _scim_replace("locale", {"type": "string", "minLength": 1, "maxLength": 64}),
                    _scim_replace("userName", _SCIM_USERNAME_EMAIL),
                    _scim_replace("emails[primary eq true].value", _SCIM_PRIMARY_EMAIL),
                ]
            },
        },
    },
    required=("schemas", "Operations"),
)

KNOWLEDGE_DETAILS = {
    "oneOf": [
        _object(
            {
                "source": {"type": "string", "format": "uri"},
                "crawl_depth": {"type": "integer", "minimum": 0},
                "crawl_period_min": {"type": "integer", "minimum": 1},
            },
            required=("source",),
        ),
        _object({"content": STRING}, required=("content",)),
        _object(
            {"content_type": STRING, "content_url": {"type": "string", "format": "uri"}},
            required=("content_type", "content_url"),
        ),
    ]
}

TRAIT_VALUE: dict[str, Any] = {
    "oneOf": [
        {"type": "string"},
        {"type": "integer"},
        {"type": "number"},
        {"type": "boolean"},
        {
            "type": "array",
            "items": {
                "oneOf": [
                    {"type": "string"},
                    {"type": "integer"},
                    {"type": "number"},
                    {"type": "boolean"},
                ]
            },
        },
    ]
}

KNOWLEDGE_DROP: dict[str, tuple[tuple[Any, ...], ...]] = {
    JSON: (
        ("properties", "policy"),
        ("properties", "embedding_model"),
    )
}


CONTRACTS: dict[tuple[str, str], dict[str, Any]] = {
    ("twilio_accounts_v1.json", "CreateBulkConsents"): _entry(
        f"{OAI_ROOT}/twilio_accounts_v1.json",
        schema_patches={FORM: ((
            ("properties", "Items", "items"),
            CONSENT_ITEM,
        ),)},
        risk_add=("identity_or_compliance",),
        restrictions=("Every item uses the documented consent fields; unknown item fields are refused.",),
    ),
    ("twilio_accounts_v1.json", "CreateBulkContacts"): _entry(
        f"{OAI_ROOT}/twilio_accounts_v1.json",
        schema_patches={FORM: ((
            ("properties", "Items", "items"),
            CONTACT_ITEM,
        ),)},
        restrictions=("Every item uses the documented contact fields; unknown item fields are refused.",),
    ),
    ("twilio_accounts_v1.json", "UpdateMessagingGeopermissions"): _entry(
        f"{OAI_ROOT}/twilio_accounts_v1.json",
        disposition="private_or_unavailable",
        reason="Twilio publishes field names but not the complete current Geo Permissions item contract.",
        restrictions=("No command is exposed until Twilio publishes the complete public request contract.",),
    ),
    ("twilio_api_v2010.json", "CreatePayments"): _entry(
        "https://www.twilio.com/docs/voice/api/payment-resource",
        f"{OAI_ROOT}/twilio_api_v2010.json",
        schema_patches={FORM: ((
            ("properties", "Parameter"),
            _json_string(_flexible_object()),
        ),)},
        risk_add=("sensitive_data",),
        restrictions=(
            "Parameter is the only flexible payment-connector JSON field and is capped at 64 KiB by the CLI.",
            "The existing idempotency key remains required; payment writes are never automatically retried.",
        ),
    ),
    ("twilio_voice_v2.json", "UpdateConfiguration"): _entry(
        "https://www.twilio.com/docs/voice/api/configuration-resource",
        f"{OAI_ROOT}/twilio_voice_v2.json",
        schema_patches={JSON: (
            (("properties", "unique_name"), {"type": "string", "maxLength": 256}),
            (("properties", "description"), {"type": "string", "maxLength": 256}),
            (("properties", "configuration"), _flexible_object()),
        )},
        risk_add=("production_change",),
        restrictions=(
            "Only unique_name, description, and the documented configuration object are accepted; arbitrary top-level fields are refused.",
            "Configuration is the sole documented flexible JSON field and is bounded by the CLI request-size limit.",
        ),
    ),
    ("twilio_voice_v2.json", "CreateConfiguration"): _entry(
        "https://www.twilio.com/docs/voice/api/configuration-resource",
        f"{OAI_ROOT}/twilio_voice_v2.json",
        schema_patches={JSON: (
            (("properties", "unique_name"), {"type": "string", "maxLength": 256}),
            (("properties", "description"), {"type": "string", "maxLength": 256}),
            (("properties", "configuration"), _flexible_object()),
        )},
        risk_add=("production_change",),
        restrictions=("Only the documented configuration fields are accepted; configuration is the sole flexible JSON field.",),
    ),
    ("twilio_voice_v2.json", "CreateAccountDefaultConfiguration"): _entry(
        "https://www.twilio.com/docs/voice/api/configuration-resource",
        f"{OAI_ROOT}/twilio_voice_v2.json",
        schema_patches={JSON: (
            (("properties", "description"), {"type": "string", "maxLength": 256}),
            (("properties", "configuration"), _flexible_object()),
        )},
        risk_add=("production_change",),
        restrictions=("Configuration is the sole documented flexible JSON field.",),
    ),
    ("twilio_voice_v2.json", "UpdateAccountDefaultConfiguration"): _entry(
        "https://www.twilio.com/docs/voice/api/configuration-resource",
        f"{OAI_ROOT}/twilio_voice_v2.json",
        schema_patches={JSON: (
            (("properties", "description"), {"type": "string", "maxLength": 256}),
            (("properties", "configuration"), _flexible_object()),
        )},
        risk_add=("production_change",),
        restrictions=("Configuration is the sole documented flexible JSON field.",),
    ),
    ("twilio_conversations_v2.json", "CreateConversationAction"): _entry(
        "https://www.twilio.com/docs/api/conversations/v2/action/create-conversation-action",
        f"{OAI_ROOT}/twilio_conversations_v2.json",
        schema_patches={JSON: ((
            ("oneOf", 0, "properties", "payload", "properties", "channelSettings"),
            _flexible_object(),
        ),)},
        risk_add=("outbound_contact", "production_change", "sensitive_data", "spend"),
        restrictions=(
            "Only payload.channelSettings is flexible; the action discriminator and all other payload fields stay fixed.",
            "Message-like actions are never automatically retried.",
        ),
    ),
    ("twilio_events_v1.json", "CreateSink"): _entry(
        "https://www.twilio.com/docs/events/event-streams/sink-resource",
        f"{OAI_ROOT}/twilio_events_v1.json",
        schema_patches={FORM: (
            (
                ("properties", "SinkConfiguration"),
                _json_string(
                    {
                        "oneOf": [
                            _object(
                                {"arn": STRING, "role_arn": STRING, "external_id": STRING},
                                required=("arn", "role_arn", "external_id"),
                            ),
                            _object(
                                {
                                    "destination": {"type": "string", "format": "uri"},
                                    "method": {"type": "string", "enum": ["GET", "POST"]},
                                    "batch_events": {"type": "boolean"},
                                },
                                required=("destination", "method"),
                            ),
                            _object({"write_key": STRING}, required=("write_key",)),
                        ]
                    }
                ),
            ),
            (("properties", "SinkType"), {"type": "string", "enum": ["kinesis", "webhook", "segment"]}),
        )},
        risk_add=("sensitive_data",),
        restrictions=(
            "Only kinesis, webhook, and segment sinks are accepted; the unproved email branch is refused.",
            "SinkConfiguration accepts only the documented Kinesis, Webhook, or Segment shape and is capped at 64 KiB.",
        ),
    ),
    ("twilio_events_v1.json", "CreateSubscription"): _entry(
        "https://www.twilio.com/docs/events/event-streams/subscription",
        f"{OAI_ROOT}/twilio_events_v1.json",
        schema_patches={FORM: ((
            ("properties", "Types", "items"),
            _object(
                {"type": STRING, "schema_version": {"type": "integer", "minimum": 1}},
                required=("type",),
            ),
        ),)},
        restrictions=("Every Types entry is a fixed object with type and optional schema_version.",),
    ),
    ("twilio_flex_v1.json", "UpdateConfiguration"): _entry(
        "https://www.twilio.com/docs/flex/developer/config/flex-configuration-rest-api",
        f"{OAI_ROOT}/twilio_flex_v1.json",
        disposition="private_or_unavailable",
        reason="The current endpoint publishes an empty request body and no complete public replacement contract.",
        restrictions=("No generic Flex configuration object is accepted.",),
    ),
    ("twilio_flex_v1.json", "CreateInteraction"): _entry(
        "https://www.twilio.com/docs/flex/developer/conversations/interactions-api/interactions",
        f"{OAI_ROOT}/twilio_flex_v1.json",
        schema_patches={FORM: (
            (("properties", "Channel"), _json_string(FLEX_CHANNEL)),
            (("properties", "Routing"), _json_string(FLEX_ROUTING)),
        )},
        risk_add=("outbound_contact", "sensitive_data", "spend"),
        restrictions=(
            "Channel and Routing use only documented keys; only Routing.properties.attributes is flexible.",
            "Interaction creation is never automatically retried.",
        ),
    ),
    ("twilio_flex_v1.json", "CreateInteractionChannelInvite"): _entry(
        "https://www.twilio.com/docs/flex/developer/conversations/interactions-api/invites-subresource",
        f"{OAI_ROOT}/twilio_flex_v1.json",
        schema_patches={FORM: ((
            ("properties", "Routing"),
            _json_string(FLEX_ROUTING),
        ),)},
        risk_add=("outbound_contact", "sensitive_data", "spend"),
        restrictions=("Only Routing.properties.attributes is flexible; unknown Routing keys are refused.",),
    ),
    ("twilio_flex_v1.json", "CreateInteractionChannelParticipant"): _entry(
        "https://www.twilio.com/docs/flex/developer/conversations/interactions-api/interaction-channel-participants",
        f"{OAI_ROOT}/twilio_flex_v1.json",
        disposition="private_or_unavailable",
        reason="Twilio does not publish a complete fixed MediaProperties/RoutingProperties request contract.",
        restrictions=("Use the documented participant-specific API after its contract is complete.",),
    ),
    ("twilio_flex_v1.json", "CreateInteractionTransfer"): _entry(
        "https://www.twilio.com/docs/flex/admin-guide/setup/conversations/messaging-transfers",
        f"{OAI_ROOT}/twilio_flex_v1.json",
        disposition="private_or_unavailable",
        reason="Twilio publishes an empty request schema for this transfer write.",
        restrictions=("No arbitrary transfer body is accepted.",),
    ),
    ("twilio_flex_v1.json", "UpdateInteractionTransfer"): _entry(
        "https://www.twilio.com/docs/flex/admin-guide/setup/conversations/messaging-transfers",
        f"{OAI_ROOT}/twilio_flex_v1.json",
        disposition="private_or_unavailable",
        reason="Twilio publishes an empty request schema for this transfer write.",
        restrictions=("No arbitrary transfer body is accepted.",),
    ),
    ("twilio_flex_v1.json", "UpdateInteractionChannel"): _entry(
        "https://www.twilio.com/docs/flex/developer/conversations/interactions-api/channels-subresource",
        f"{OAI_ROOT}/twilio_flex_v1.json",
        schema_patches={FORM: ((
            ("properties", "Routing"),
            _json_string(_object({"status": {"type": "string", "enum": ["closed"]}}, required=("status",))),
        ),)},
        restrictions=("Routing accepts only the documented closed task status and is relevant only when Status is inactive.",),
    ),
    ("twilio_flex_v1.json", "CreatePluginConfiguration"): _entry(
        "https://www.twilio.com/docs/flex/developer/plugins/api/plugin-configuration",
        f"{OAI_ROOT}/twilio_flex_v1.json",
        schema_patches={FORM: ((
            ("properties", "Plugins", "items"),
            _object(
                {"plugin_version": {"type": "string", "pattern": "^FV[0-9a-fA-F]{32}$"}},
                required=("plugin_version",),
            ),
        ),)},
        restrictions=("Each plugin item accepts only plugin_version; the undocumented phase field is refused.",),
    ),
    ("twilio_iam_organizations.json", "PatchOrganizationUser"): _entry(
        "https://www.twilio.com/docs/iam/scim/api-reference",
        f"{OAI_ROOT}/twilio_iam_organizations.json",
        reason="Twilio publishes the SCIM PatchOp envelope, fixed patchable paths, and path-specific value contracts.",
        schema_patches={
            JSON: (((), _SCIM_PATCH_REQUEST),),
            SCIM_JSON: (((), _SCIM_PATCH_REQUEST),),
        },
        parameter_patches={
            ("header", "If-Match"): {
                "required": True,
                "schema": {"type": "string", "pattern": r'^W/(?:[0-9]+|"[0-9]+")$'},
            }
        },
        risk_add=("identity_or_compliance", "production_change", "sensitive_data", "preview"),
        snapshot_strategy="fetch_before_change",
        verification_strategy="refetch_changed_resource",
        snapshot_required=True,
        pii_fields_add=("id", "externalId", "UserSid", "userName", "displayName", "givenName", "familyName", "emails", "value"),
        restrictions=(
            "Only replace is accepted for eight documented scalar paths; whole emails objects and unknown paths are refused.",
            "Username and primary email changes must be paired and equal.",
            "A protected before-state snapshot and its exact meta.version through If-Match are required.",
        ),
    ),
    ("twilio_iam_v1.json", "CreateNewKey"): _entry(
        "https://www.twilio.com/docs/iam/api-keys/restricted-api-keys",
        "https://www.twilio.com/docs/iam/api-keys/key-resource-v1",
        f"{OAI_ROOT}/twilio_iam_v1.json",
        schema_patches={FORM: ((
            ("properties", "Policy"),
            _json_string(IAM_POLICY),
        ),)},
        restrictions=("Policy accepts only a non-empty allow array of documented permission strings.",),
    ),
    ("twilio_iam_v1.json", "UpdateKey"): _entry(
        "https://www.twilio.com/docs/iam/api-keys/restricted-api-keys",
        "https://www.twilio.com/docs/iam/api-keys/key-resource-v1",
        f"{OAI_ROOT}/twilio_iam_v1.json",
        schema_patches={FORM: ((
            ("properties", "Policy"),
            _json_string(IAM_POLICY),
        ),)},
        restrictions=("Policy accepts only a non-empty allow array of documented permission strings.",),
    ),
    ("twilio_intelligence_v2.json", "CreateCustomOperator"): _entry(
        "https://www.twilio.com/docs/conversation-intelligence-classic/api/custom-operator-subresource",
        f"{OAI_ROOT}/twilio_intelligence_v2.json",
        schema_patches={FORM: ((
            ("properties", "Config"),
            _json_string(_flexible_object()),
        ),)},
        risk_add=("sensitive_data",),
        restrictions=("Config is validated against the selected current Operator Type before apply.",),
    ),
    ("twilio_intelligence_v2.json", "UpdateCustomOperator"): _entry(
        "https://www.twilio.com/docs/conversation-intelligence-classic/api/custom-operator-subresource",
        f"{OAI_ROOT}/twilio_intelligence_v2.json",
        schema_patches={FORM: ((
            ("properties", "Config"),
            _json_string(_flexible_object()),
        ),)},
        risk_add=("sensitive_data",),
        restrictions=("Config is validated against the selected current Operator Type before apply.",),
    ),
    ("twilio_intelligence_v2.json", "CreateTranscript"): _entry(
        "https://www.twilio.com/docs/conversation-intelligence-classic/api/transcript-resource",
        f"{OAI_ROOT}/twilio_intelligence_v2.json",
        schema_patches={FORM: ((
            ("properties", "Channel"),
            _json_string(
                _object(
                    {
                        "media_properties": _object(
                            {"media_url": {"type": "string", "format": "uri"}},
                            required=("media_url",),
                        )
                    },
                    required=("media_properties",),
                )
            ),
        ),)},
        risk_add=("sensitive_data", "spend"),
        restrictions=("The safe subset accepts the documented external media URL channel shape only.",),
    ),
    ("twilio_intelligence_v3.json", "CreateConfiguration"): _entry(
        "https://www.twilio.com/docs/api/intelligence/v3/configurations/create-configuration",
        f"{OAI_ROOT}/twilio_intelligence_v3.json",
        schema_patches={JSON: ((
            ("properties", "rules", "items", "properties", "operators", "items", "properties", "parameters"),
            _flexible_object(),
        ),)},
        risk_add=("sensitive_data",),
        restrictions=("Each parameters map is checked against the referenced current Operator schema before apply.",),
    ),
    ("twilio_intelligence_v3.json", "UpdateConfiguration"): _entry(
        "https://www.twilio.com/docs/api/intelligence/v3/configurations/update-configuration",
        f"{OAI_ROOT}/twilio_intelligence_v3.json",
        schema_patches={JSON: ((
            ("properties", "rules", "items", "properties", "operators", "items", "properties", "parameters"),
            _flexible_object(),
        ),)},
        risk_add=("sensitive_data",),
        restrictions=("Each parameters map is checked against the referenced current Operator schema before apply.",),
    ),
    ("twilio_intelligence_v3.json", "CreateOperator"): _entry(
        "https://www.twilio.com/docs/api/intelligence/v3/operators/create-operator",
        f"{OAI_ROOT}/twilio_intelligence_v3.json",
        schema_patches={JSON: (
            (("allOf", 0, "properties", "outputSchema"), _flexible_object()),
            (
                ("allOf", 0, "properties", "parameters", "additionalProperties", "properties", "default"),
                {"oneOf": ({"type": "string"}, {"type": "integer"}, {"type": "number"}, {"type": "boolean"})},
            ),
        )},
        risk_add=("production_change", "sensitive_data"),
        restrictions=("Only the exact outputSchema field may contain a flexible JSON Schema object.",),
    ),
    ("twilio_intelligence_v3.json", "UpdateOperator"): _entry(
        "https://www.twilio.com/docs/api/intelligence/v3/operators/update-operator",
        f"{OAI_ROOT}/twilio_intelligence_v3.json",
        schema_patches={JSON: (
            (("allOf", 0, "properties", "outputSchema"), _flexible_object()),
            (
                ("allOf", 0, "properties", "parameters", "additionalProperties", "properties", "default"),
                {"oneOf": ({"type": "string"}, {"type": "integer"}, {"type": "number"}, {"type": "boolean"})},
            ),
        )},
        risk_add=("production_change", "sensitive_data"),
        restrictions=("Only the exact outputSchema field may contain a flexible JSON Schema object.",),
    ),
    ("twilio_knowledge_v1.json", "CreateKnowledge"): _entry(
        "https://www.twilio.com/docs/flex/developer/copilot/api-knowledge",
        "https://www.twilio.com/docs/flex/developer/copilot/upload-source-api",
        f"{OAI_ROOT}/twilio_knowledge_v1.json",
        schema_patches={JSON: (
            (("properties", "knowledge_source_details"), KNOWLEDGE_DETAILS),
            (("properties", "type"), {"type": "string", "enum": ["Web", "Text", "File"]}),
        )},
        drop_paths=KNOWLEDGE_DROP,
        risk_add=("sensitive_data",),
        restrictions=(
            "Safe subset supports documented Web, Text, and File details only.",
            "Database, embedding_model, and the incomplete policy branch are refused.",
            "This product is Public Beta and is not HIPAA Eligible or PCI compliant.",
        ),
    ),
    ("twilio_knowledge_v1.json", "UpdateKnowledge"): _entry(
        "https://www.twilio.com/docs/flex/developer/copilot/api-knowledge",
        "https://www.twilio.com/docs/flex/developer/copilot/upload-source-api",
        f"{OAI_ROOT}/twilio_knowledge_v1.json",
        schema_patches={JSON: (
            (("properties", "knowledge_source_details"), KNOWLEDGE_DETAILS),
            (("properties", "type"), {"type": "string", "enum": ["Web", "Text", "File"]}),
        )},
        drop_paths=KNOWLEDGE_DROP,
        risk_add=("sensitive_data",),
        restrictions=(
            "Safe subset supports documented Web, Text, and File details only.",
            "Database, embedding_model, and the incomplete policy branch are refused.",
            "This product is Public Beta and is not HIPAA Eligible or PCI compliant.",
        ),
    ),
    ("twilio_marketplace_v1.json", "CreateInstalledAddOn"): _entry(
        "https://www.twilio.com/docs/marketplace/api/installed-add-ons",
        f"{OAI_ROOT}/twilio_marketplace_v1.json",
        schema_patches={FORM: ((
            ("properties", "Configuration"),
            _json_string(_flexible_object()),
        ),)},
        risk_add=("sensitive_data", "spend"),
        restrictions=(
            "Configuration is checked against the selected Available Add-on schema before apply.",
            "Terms of Service acceptance must be explicit and is never inferred by the CLI.",
        ),
    ),
    ("twilio_marketplace_v1.json", "UpdateInstalledAddOn"): _entry(
        "https://www.twilio.com/docs/marketplace/api/installed-add-ons",
        f"{OAI_ROOT}/twilio_marketplace_v1.json",
        schema_patches={FORM: ((
            ("properties", "Configuration"),
            _json_string(_flexible_object()),
        ),)},
        risk_add=("sensitive_data", "spend"),
        restrictions=("Configuration is checked against the selected Available Add-on schema before apply.",),
    ),
    ("twilio_memory_v1.json", "CreateProfile"): _entry(
        "https://www.twilio.com/docs/api/memory/v1/profile/create-profile",
        f"{OAI_ROOT}/twilio_memory_v1.json",
        schema_patches={JSON: ((
            ("properties", "traits", "additionalProperties", "additionalProperties"),
            TRAIT_VALUE,
        ),)},
        risk_add=("sensitive_data",),
        restrictions=("Trait values may be scalar strings, numbers, booleans, or one-dimensional arrays of those scalars.",),
    ),
    ("twilio_memory_v1.json", "UpdateProfilesBulk"): _entry(
        "https://www.twilio.com/docs/api/memory/v1/profile/update-profiles-bulk",
        f"{OAI_ROOT}/twilio_memory_v1.json",
        schema_patches={JSON: ((
            (
                "properties",
                "profiles",
                "items",
                "properties",
                "traits",
                "additionalProperties",
                "additionalProperties",
            ),
            TRAIT_VALUE,
        ),)},
        risk_add=("sensitive_data",),
        restrictions=("Nested trait arrays and arbitrary objects are refused.",),
    ),
    ("twilio_memory_v1.json", "PatchProfileTraits"): _entry(
        "https://www.twilio.com/docs/api/memory/v1/profile/patch-profile-traits",
        f"{OAI_ROOT}/twilio_memory_v1.json",
        schema_patches={JSON: ((
            ("properties", "traits", "additionalProperties", "additionalProperties"),
            TRAIT_VALUE,
        ),)},
        risk_add=("sensitive_data",),
        restrictions=("Nested trait arrays and arbitrary objects are refused.",),
    ),
    ("twilio_messaging_v2.json", "CreateChannelsSender"): _entry(
        "https://www.twilio.com/docs/whatsapp/api/senders",
        f"{OAI_ROOT}/twilio_messaging_v2.json",
        schema_patches={JSON: (
            (("properties", "profile", "properties", "emails"), {"type": "array", "items": {"type": "string", "format": "email"}}),
            (("properties", "profile", "properties", "phone_numbers"), {"type": "array", "items": E164}),
            (("properties", "profile", "properties", "websites"), {"type": "array", "items": {"type": "string", "format": "uri"}}),
        )},
        risk_add=("identity_or_compliance", "production_change", "sensitive_data"),
        restrictions=("Profile email, phone-number, and website lists use only documented string entries.",),
    ),
    ("twilio_messaging_v2.json", "UpdateChannelsSender"): _entry(
        "https://www.twilio.com/docs/whatsapp/api/senders",
        f"{OAI_ROOT}/twilio_messaging_v2.json",
        schema_patches={JSON: (
            (("properties", "profile", "properties", "emails"), {"type": "array", "items": {"type": "string", "format": "email"}}),
            (("properties", "profile", "properties", "phone_numbers"), {"type": "array", "items": E164}),
            (("properties", "profile", "properties", "websites"), {"type": "array", "items": {"type": "string", "format": "uri"}}),
        )},
        risk_add=("identity_or_compliance", "production_change", "sensitive_data"),
        restrictions=("Profile email, phone-number, and website lists use only documented string entries.",),
    ),
}


if len(CONTRACTS) != 38:  # pragma: no cover - import-time integrity guard
    raise RuntimeError(f"manual contract table A must contain 38 entries, found {len(CONTRACTS)}")

"""Credential-free, bounded local contracts for Twilio voice integrations."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import parse_qs, urlparse

from .errors import ValidationError

_MAX_XML = 16 * 1024
_CONNECT_ATTRS = {"action", "method"}
_LANGUAGE_ATTRS = {"code", "ttsProvider", "voice", "transcriptionProvider", "speechModel"}
_MAX_LANGUAGES = 5
_MAX_FORM_PARAMS = 50
_MAX_FORM_VALUES = 20
_RELAY_ATTRS = {"url", "welcomeGreeting", "welcomeGreetingInterruptible", "language", "ttsLanguage", "ttsProvider", "voice", "transcriptionLanguage", "transcriptionProvider", "speechModel", "eotThreshold", "partialPrompts", "deepgramSmartFormat", "interruptible", "interruptSensitivity", "speechTimeout", "dtmfDetection", "reportInputDuringAgentSpeech", "ignoreBackchannel", "preemptible", "hints", "events", "elevenlabsTextNormalization", "intelligenceService", "conversationConfiguration", "conversationId", "debug"}
_PARAM_ATTRS = {"name", "value"}
_INPUT_ALIASES = {"welcome_greeting": "welcomeGreeting", "dtmf_detection": "dtmfDetection", "tts_language": "ttsLanguage", "tts_provider": "ttsProvider", "transcription_provider": "transcriptionProvider", "custom_parameters": "customParameters"}
_BOOLS = {"true", "false"}
_INTERRUPTION_MODES = {"none", "dtmf", "speech", "any"}
_BOOLEAN_ATTRS = {"dtmfDetection", "ignoreBackchannel", "preemptible", "partialPrompts", "deepgramSmartFormat"}
_INBOUND = {
    "setup": {"type", "sessionId", "accountSid", "parentCallSid", "callSid", "from", "to", "forwardedFrom", "callType", "callerName", "direction", "callStatus", "customParameters"},
    "prompt": {"type", "voicePrompt", "lang", "last"},
    "dtmf": {"type", "digit"},
    "interrupt": {"type", "utteranceUntilInterrupt", "durationUntilInterruptMs"},
    "error": {"type", "description"},
}
_OUTBOUND = {
    "text": {"type", "token", "last", "lang", "interruptible", "preemptible"},
    "play": {"type", "source", "loop", "preemptible", "interruptible"},
    "sendDigits": {"type", "digits"},
    "language": {"type", "ttsLanguage", "transcriptionLanguage"},
    "end": {"type", "handoffData"},
}


def _obj(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must be a JSON object")
    return value


def _unknown(value: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = set(value) - allowed
    if unknown:
        raise ValidationError(f"Unknown {label} field(s): {', '.join(sorted(unknown))}")


def _bounded_string(value: Any, label: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise ValidationError(f"{label} must be a non-empty string of at most {maximum} characters")
    return value


def _absolute_wss(value: Any) -> str:
    url = _bounded_string(value, "url", 4096)
    try:
        parsed = urlparse(url)
    except ValueError:
        raise ValidationError("url is required and must be an absolute wss URL") from None
    if parsed.scheme != "wss" or not parsed.netloc:
        raise ValidationError("url is required and must be an absolute wss URL")
    return url


def _action_reference(value: Any) -> str:
    action = _bounded_string(value, "action", 2048)
    if any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in action):
        raise ValidationError("action must not contain whitespace or control characters")
    try:
        parsed = urlparse(action)
    except ValueError:
        raise ValidationError("action must be a relative path or absolute HTTP(S) URL") from None
    if parsed.scheme:
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
            raise ValidationError("action must be a relative path or absolute HTTP(S) URL")
        return action
    if parsed.netloc or action.startswith("//") or not parsed.path:
        raise ValidationError("action must be a relative path or absolute HTTP(S) URL")
    return action


def _relay_attribute(key: str, value: Any, *, xml_input: bool = False) -> str:
    if key == "url":
        return _absolute_wss(value)
    if key in _BOOLEAN_ATTRS:
        if isinstance(value, bool) and not xml_input:
            return str(value).lower()
        text = _bounded_string(value, key)
        if text not in _BOOLS:
            raise ValidationError(f"{key} must be true or false")
        return text
    if key == "welcomeGreetingInterruptible" or key == "reportInputDuringAgentSpeech":
        text = _bounded_string(value, key)
        if text not in _INTERRUPTION_MODES:
            raise ValidationError(f"{key} has an unsupported value")
        return text
    if key == "interruptible":
        if isinstance(value, bool) and not xml_input:
            return str(value).lower()
        text = _bounded_string(value, key)
        if text not in _INTERRUPTION_MODES | _BOOLS:
            raise ValidationError("interruptible has an unsupported value")
        return text
    if key == "interruptSensitivity":
        text = _bounded_string(value, key)
        if text not in {"high", "medium", "low"}:
            raise ValidationError("interruptSensitivity has an unsupported value")
        return text
    if key == "speechTimeout":
        text = str(value) if isinstance(value, int) and not isinstance(value, bool) else _bounded_string(value, key)
        if text != "auto" and (not text.isdigit() or not 600 <= int(text) <= 5000):
            raise ValidationError("speechTimeout must be auto or an integer from 600 to 5000")
        return text
    if key == "eotThreshold":
        if isinstance(value, bool):
            raise ValidationError("eotThreshold must be a number from 0.5 to 0.9")
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValidationError("eotThreshold must be a number from 0.5 to 0.9") from None
        if not 0.5 <= number <= 0.9:
            raise ValidationError("eotThreshold must be a number from 0.5 to 0.9")
        return str(value)
    text = _bounded_string(value, key, 4096)
    if key == "ttsProvider" and text not in {"Google", "Amazon", "ElevenLabs"}:
        raise ValidationError("unsupported ttsProvider")
    if key == "transcriptionProvider" and text not in {"Google", "Deepgram"}:
        raise ValidationError("unsupported transcriptionProvider")
    if key == "elevenlabsTextNormalization" and text not in {"on", "auto", "off"}:
        raise ValidationError("unsupported elevenlabsTextNormalization")
    if key == "events":
        events = text.split()
        if not events or len(events) != len(set(events)) or any(item not in {"speaker-events", "tokens-played"} for item in events):
            raise ValidationError("events must be a space-separated subset of speaker-events and tokens-played")
    if key == "debug" and text != "debugging":
        raise ValidationError("debug must equal debugging")
    return text


def generate_conversation_relay(spec: dict[str, Any]) -> dict[str, Any]:
    spec = _obj(spec, "input")
    spec = {_INPUT_ALIASES.get(key, key): value for key, value in spec.items()}
    allowed = _CONNECT_ATTRS | _RELAY_ATTRS | {"parameters", "languages"}
    _unknown(spec, allowed, "ConversationRelay")
    if "url" not in spec:
        raise ValidationError("url is required and must be an absolute wss URL")
    root = ET.Element("Response")
    connect = ET.SubElement(root, "Connect")
    if "action" in spec:
        connect.set("action", _action_reference(spec["action"]))
    if "method" in spec:
        method = _bounded_string(spec["method"], "method", 4)
        if method not in {"GET", "POST"}:
            raise ValidationError("method must be GET or POST")
        connect.set("method", method)
    relay = ET.SubElement(connect, "ConversationRelay")
    for key in _RELAY_ATTRS & set(spec):
        relay.set(key, _relay_attribute(key, spec[key]))
    languages = spec.get("languages", [])
    if not isinstance(languages, list) or len(languages) > _MAX_LANGUAGES:
        raise ValidationError(f"languages must be an array of at most {_MAX_LANGUAGES} items")
    for item in languages:
        item = _obj(item, "languages item")
        _unknown(item, _LANGUAGE_ATTRS, "Language")
        code = _bounded_string(item.get("code"), "Language.code", 64)
        attrs = {"code": code}
        for key in ("ttsProvider", "voice", "transcriptionProvider", "speechModel"):
            if key in item:
                attrs[key] = _bounded_string(item[key], f"Language.{key}", 128)
        ET.SubElement(relay, "Language", attrs)
    params = spec.get("parameters", [])
    if not isinstance(params, list) or len(params) > 20:
        raise ValidationError("parameters must be an array of at most 20 items")
    for item in params:
        item = _obj(item, "parameters item")
        _unknown(item, _PARAM_ATTRS, "Parameter")
        name = _bounded_string(item.get("name"), "Parameter.name", 128)
        value = _bounded_string(item.get("value"), "Parameter.value", 1024)
        ET.SubElement(relay, "Parameter", {"name": name, "value": value})
    xml = ET.tostring(root, encoding="unicode", short_empty_elements=True)
    if len(xml.encode()) > _MAX_XML:
        raise ValidationError("generated XML exceeds the 16 KiB limit")
    return {"ok": True, "xml": xml, "bounded": True}


def validate_conversation_relay(xml: str) -> dict[str, Any]:
    if not isinstance(xml, str) or not xml.strip() or len(xml.encode()) > _MAX_XML:
        raise ValidationError("xml must be non-empty and at most 16 KiB")
    if "<!DOCTYPE" in xml.upper() or "<!ENTITY" in xml.upper() or "<!--" in xml or "<?" in xml or "<![CDATA[" in xml:
        raise ValidationError("XML declarations and entities are not allowed")
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        raise ValidationError("xml is not well-formed") from None
    if root.tag != "Response" or root.attrib or (root.text and root.text.strip()) or (root.tail and root.tail.strip()) or len(root) != 1 or root[0].tag != "Connect":
        raise ValidationError("only Response containing one Connect and ConversationRelay is allowed")
    connect = root[0]
    if set(connect.attrib) - _CONNECT_ATTRS or (connect.text and connect.text.strip()) or (connect.tail and connect.tail.strip()) or len(connect) != 1 or connect[0].tag != "ConversationRelay":
        raise ValidationError("only Response containing one Connect and ConversationRelay is allowed")
    if "method" in connect.attrib and connect.attrib["method"] not in {"GET", "POST"}:
        raise ValidationError("method must be GET or POST")
    if "action" in connect.attrib:
        _action_reference(connect.attrib["action"])
    relay = connect[0]
    if set(relay.attrib) - _RELAY_ATTRS or (relay.text and relay.text.strip()) or (relay.tail and relay.tail.strip()):
        raise ValidationError("unknown ConversationRelay attribute")
    for key, val in relay.attrib.items():
        _relay_attribute(key, val, xml_input=True)
    if any(len(key) > 256 or len(val) > 4096 for key, val in relay.attrib.items()):
        raise ValidationError("ConversationRelay attribute value is too long")
    parameters = [child for child in relay if child.tag == "Parameter"]
    languages = [child for child in relay if child.tag == "Language"]
    if len(parameters) > 20 or len(languages) > _MAX_LANGUAGES or len(parameters) + len(languages) != len(relay):
        raise ValidationError("unsupported child or child cardinality")
    for child in parameters:
        if set(child.attrib) != _PARAM_ATTRS or len(child) or (child.text and child.text.strip()) or (child.tail and child.tail.strip()):
            raise ValidationError("Parameter children require only name and value")
        if not child.attrib["name"] or not child.attrib["value"] or len(child.attrib["name"]) > 128 or len(child.attrib["value"]) > 1024:
            raise ValidationError("Parameter name or value is invalid")
    for child in languages:
        if set(child.attrib) - _LANGUAGE_ATTRS or "code" not in child.attrib or len(child) or (child.text and child.text.strip()) or (child.tail and child.tail.strip()):
            raise ValidationError("Language children require code and documented attributes only")
        for key, val in child.attrib.items():
            if not val or len(val) > (64 if key == "code" else 128):
                raise ValidationError("Language attribute is invalid")
    return {"ok": True, "valid": True, "bounded": True, "element": "Connect/ConversationRelay"}


def validate_conversation_relay_message(value: dict[str, Any]) -> dict[str, Any]:
    value = _obj(value, "input")
    _unknown(value, {"direction", "message"}, "message envelope")
    direction = value.get("direction")
    if direction not in {"inbound", "outbound"}:
        raise ValidationError("direction must be explicitly inbound or outbound")
    message = _obj(value.get("message"), "message")
    kind = message.get("type")
    schemas = _INBOUND if direction == "inbound" else _OUTBOUND
    if kind not in schemas:
        raise ValidationError("unsupported ConversationRelay message type for direction")
    _unknown(message, schemas[kind], f"{kind} message")
    required = {
        "setup": {"sessionId", "accountSid", "parentCallSid", "callSid", "from", "to", "forwardedFrom", "callType", "callerName", "direction", "callStatus", "customParameters"},
        "prompt": {"voicePrompt", "lang", "last"},
        "dtmf": {"digit"},
        "interrupt": {"utteranceUntilInterrupt", "durationUntilInterruptMs"},
        "error": {"description"},
        "text": {"token"},
        "play": {"source"},
        "sendDigits": {"digits"},
        "language": set(),
        "end": set(),
    }.get(kind, set())
    if not required.issubset(message):
        raise ValidationError(f"{kind} message is missing required fields")
    bool_fields = {"last", "interruptible", "preemptible"}
    if any(key in message and not isinstance(message[key], bool) for key in bool_fields):
        raise ValidationError("message boolean fields must be true or false")
    if kind == "setup":
        string_fields = required - {"customParameters"}
        if any(not isinstance(message[key], str) or len(message[key]) > 4096 for key in string_fields):
            raise ValidationError("setup string fields are invalid")
        custom = message["customParameters"]
        if not isinstance(custom, dict) or any(not isinstance(key, str) or not isinstance(item, str) for key, item in custom.items()):
            raise ValidationError("setup.customParameters must be a string map")
    elif kind == "prompt":
        if not all(isinstance(message[key], str) and message[key] for key in {"voicePrompt", "lang"}):
            raise ValidationError("prompt voicePrompt and lang must be non-empty strings")
    elif kind == "dtmf":
        if not isinstance(message["digit"], str) or len(message["digit"]) != 1 or message["digit"] not in "0123456789#*":
            raise ValidationError("dtmf.digit must be one DTMF character")
    elif kind == "interrupt":
        duration = message["durationUntilInterruptMs"]
        if not isinstance(message["utteranceUntilInterrupt"], str) or not isinstance(duration, int) or isinstance(duration, bool) or duration < 0:
            raise ValidationError("interrupt fields are invalid")
    elif kind == "error":
        _bounded_string(message["description"], "error.description", 4096)
    elif kind == "text":
        if not isinstance(message["token"], str) or len(message["token"]) > 16_384:
            raise ValidationError("text.token must be a string of at most 16 KiB")
        if "lang" in message:
            _bounded_string(message["lang"], "text.lang", 64)
    elif kind == "sendDigits" and (not isinstance(message["digits"], str) or not message["digits"] or any(char not in "0123456789w#*" for char in message["digits"])):
        raise ValidationError("sendDigits.digits must contain only 0-9, w, #, or *")
    elif kind == "play":
        source = message["source"]
        parsed = urlparse(source) if isinstance(source, str) else None
        if parsed is None or parsed.scheme not in {"https", "http"} or not parsed.netloc:
            raise ValidationError("play.source must be an absolute HTTP(S) URL")
        if "loop" in message and (not isinstance(message["loop"], int) or isinstance(message["loop"], bool) or message["loop"] < 0):
            raise ValidationError("play.loop must be a non-negative integer")
    if kind == "language" and not (message.get("ttsLanguage") or message.get("transcriptionLanguage")):
        raise ValidationError("language requires ttsLanguage or transcriptionLanguage")
    if kind == "language":
        for key in {"ttsLanguage", "transcriptionLanguage"} & set(message):
            _bounded_string(message[key], f"language.{key}", 64)
    if kind == "end" and "handoffData" in message:
        _bounded_string(message["handoffData"], "end.handoffData", 4096)
    result: dict[str, Any] = {"ok": True, "valid": True, "direction": direction, "type": kind}
    if kind == "end" and "handoffData" in message:
        result["warnings"] = ["Do not include PCI data in handoffData."]
    return result


def _token_from_env(name: Any) -> str:
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise ValidationError("auth_token_env must be a valid environment variable name")
    token = os.environ.get(name)
    if not token:
        raise ValidationError("named auth token environment variable is missing")
    return token


def validate_twilio_signature(value: dict[str, Any]) -> dict[str, Any]:
    value = _obj(value, "input")
    _unknown(value, {"kind", "url", "params", "body", "body_sha256", "signature", "auth_token_env"}, "signature")
    kind = value.get("kind")
    url = _bounded_string(value.get("url"), "url", 4096)
    signature = _bounded_string(value.get("signature"), "signature", 512)
    token = _token_from_env(value.get("auth_token_env"))
    if kind == "form":
        params = _obj(value.get("params", {}), "params")
        if len(params) > _MAX_FORM_PARAMS or any(not isinstance(key, str) for key in params):
            raise ValidationError(f"form params must contain at most {_MAX_FORM_PARAMS} names")
        parts: list[str] = []
        for key in sorted(params):
            if not isinstance(key, str) or not key or len(key) > 128:
                raise ValidationError("form parameter names must be non-empty strings of at most 128 characters")
            raw = params[key]
            values = raw if isinstance(raw, list) else [raw]
            if not values or len(values) > _MAX_FORM_VALUES:
                raise ValidationError(f"each form parameter must have 1 to {_MAX_FORM_VALUES} values")
            if any(not isinstance(item, (str, int, float, bool)) or isinstance(item, (dict, list, tuple, set)) for item in values):
                raise ValidationError("form params must contain only scalar string, integer, float, or boolean values")
            strings = sorted({str(item) for item in values})
            if any(not item or len(item) > 1024 for item in strings):
                raise ValidationError("form parameter values must be non-empty strings of at most 1024 characters")
            parts.extend(key + item for item in strings)
        payload = url + "".join(parts)
    elif kind == "json":
        body = value.get("body")
        if not isinstance(body, str):
            raise ValidationError("JSON signature body must be the raw body string")
        digest = hashlib.sha256(body.encode()).hexdigest()
        if value.get("body_sha256") != digest:
            raise ValidationError("body_sha256 does not match the raw body")
        query = parse_qs(urlparse(url).query)
        if query.get("bodySHA256") != [digest]:
            raise ValidationError("full URL must contain the matching bodySHA256 query parameter")
        payload = url
    else:
        raise ValidationError("kind must be form or json")
    expected = base64.b64encode(hmac.new(token.encode(), payload.encode(), hashlib.sha1).digest()).decode()
    return {"ok": True, "valid": hmac.compare_digest(expected, signature), "kind": kind}


def agent_connect_contract(value: dict[str, Any]) -> dict[str, Any]:
    value = _obj(value, "input")
    _unknown(value, set(), "Agent Connect")
    return {
        "ok": True,
        "local_only": True,
        "contract": "Agent Connect metadata",
        "channels": ["voice", "sms", "whatsapp", "rcs", "chat"],
        "routes": ["/twiml", "/ws", "/conversation-relay-callback", "/webhook"],
        "optional_routes": ["/ci-webhook"],
        "note": "This is an SDK/middleware integration contract, not a REST or TwiML operation.",
    }

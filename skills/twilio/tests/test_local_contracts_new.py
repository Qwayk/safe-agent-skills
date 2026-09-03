from __future__ import annotations

import base64
import contextlib
import hashlib
import hmac
import io
import json
import os
import unittest

from twilio_safe_agent_cli.cli import main
from twilio_safe_agent_cli.errors import ValidationError
from twilio_safe_agent_cli.local_contracts import (
    agent_connect_contract,
    generate_conversation_relay,
    validate_conversation_relay,
    validate_conversation_relay_message,
    validate_twilio_signature,
)


class TestLocalContracts(unittest.TestCase):
    def test_agent_connect_cli_requires_no_input_and_emits_one_json_object(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["agent-connect", "contract"]), 0)
        payload = json.loads(output.getvalue())
        self.assertTrue(payload["local_only"])

    def test_generate_and_validate_bounded_connect_xml(self) -> None:
        result = generate_conversation_relay({
            "url": "wss://example.test/relay",
            "welcome_greeting": "Hello",
            "reportInputDuringAgentSpeech": "speech",
            "events": "speaker-events tokens-played",
            "speechModel": "nova-3-general",
            "eotThreshold": 0.8,
            "partialPrompts": True,
            "deepgramSmartFormat": False,
            "parameters": [{"name": "tenant", "value": "demo"}],
        })
        self.assertTrue(result["ok"])
        self.assertTrue(result["xml"].startswith("<Response><Connect>"))
        self.assertIn('eotThreshold="0.8"', result["xml"])
        self.assertIn('partialPrompts="true"', result["xml"])
        self.assertTrue(validate_conversation_relay(result["xml"])["valid"])

    def test_languages_generate_and_validate_as_bounded_children(self) -> None:
        result = generate_conversation_relay({
            "url": "wss://example.test/relay",
            "languages": [{"code": "en-US", "ttsProvider": "Google", "voice": "Polly.Joanna"}],
            "parameters": [{"name": "tenant", "value": "demo"}],
        })
        self.assertIn('<Language code="en-US" ttsProvider="Google" voice="Polly.Joanna" />', result["xml"])
        self.assertTrue(validate_conversation_relay(result["xml"])["valid"])

    def test_languages_reject_missing_code_unknown_fields_text_descendants_and_cardinality(self) -> None:
        for languages in (
            [{"voice": "Polly.Joanna"}],
            [{"code": "en-US", "region": "US"}],
            [{"code": "en-US", "voice": ""}],
            [{"code": "en-US"}] * 6,
        ):
            with self.subTest(languages=languages), self.assertRaises(ValidationError):
                generate_conversation_relay({"url": "wss://example.test/relay", "languages": languages})
        with self.assertRaises(ValidationError):
            validate_conversation_relay('<Response><Connect><ConversationRelay url="wss://e.test"><Language voice="x" /></ConversationRelay></Connect></Response>')
        with self.assertRaises(ValidationError):
            validate_conversation_relay('<Response><Connect><ConversationRelay url="wss://e.test"><Language code="en-US">x</Language></ConversationRelay></Connect></Response>')

    def test_connect_method_allows_only_get_or_post_and_preserves_action(self) -> None:
        for method in ("GET", "POST"):
            xml = generate_conversation_relay({"url": "wss://e.test", "method": method, "action": "/done"})["xml"]
            self.assertIn(f'method="{method}"', xml)
            self.assertIn('action="/done"', xml)
            self.assertTrue(validate_conversation_relay(xml)["valid"])
        with self.assertRaises(ValidationError):
            generate_conversation_relay({"url": "wss://e.test", "method": "PUT"})
        self.assertTrue(validate_conversation_relay('<Response><Connect action="https://example.test/done" method="POST"><ConversationRelay url="wss://e.test" /></Connect></Response>')["valid"])

    def test_connect_action_requires_safe_relative_or_http_callback_reference(self) -> None:
        for action in ("/done", "done", "/done?x=1", "https://example.test/done"):
            with self.subTest(action=action):
                xml = generate_conversation_relay({"url": "wss://e.test", "action": action})["xml"]
                self.assertTrue(validate_conversation_relay(xml)["valid"])
        for action in ("", "   ", "/do ne", "/done\n", "javascript:alert(1)", "mailto:x@y.test", "file:///tmp/x", "//host/path", "?x=1", "#frag", "https:///done"):
            with self.subTest(action=action), self.assertRaises(ValidationError):
                generate_conversation_relay({"url": "wss://e.test", "action": action})
        with self.assertRaises(ValidationError):
            validate_conversation_relay('<Response><Connect action="javascript:alert(1)"><ConversationRelay url="wss://e.test" /></Connect></Response>')

    def test_xml_child_contract_rejects_descendants_unknown_attrs_tail_and_bad_method(self) -> None:
        with self.assertRaises(ValidationError):
            validate_conversation_relay('<Response><Connect><ConversationRelay url="wss://e.test"><Language code="en-US"><Voice /></Language></ConversationRelay></Connect></Response>')
        with self.assertRaises(ValidationError):
            validate_conversation_relay('<Response><Connect><ConversationRelay url="wss://e.test"><Language code="en-US" region="US" /></ConversationRelay></Connect></Response>')
        with self.assertRaises(ValidationError):
            validate_conversation_relay('<Response><Connect><ConversationRelay url="wss://e.test"><Parameter name="a" value="b" />unexpected</ConversationRelay></Connect></Response>')
        with self.assertRaises(ValidationError):
            validate_conversation_relay('<Response><Connect><ConversationRelay url="wss://e.test"><Language code="en-US" />unexpected</ConversationRelay></Connect></Response>')
        with self.assertRaises(ValidationError):
            validate_conversation_relay('<Response><Connect method="PUT"><ConversationRelay url="wss://e.test" /></Connect></Response>')

    def test_xml_rejects_structural_tails_but_allows_formatting_whitespace(self) -> None:
        valid = '<Response>\n  <Connect>\n    <ConversationRelay url="wss://e.test" />\n  </Connect>\n</Response>'
        self.assertTrue(validate_conversation_relay(valid)["valid"])
        for xml in (
            '<Response><Connect><ConversationRelay url="wss://e.test" /></Connect>BAD</Response>',
            '<Response><Connect><ConversationRelay url="wss://e.test" />BAD</Connect></Response>',
        ):
            with self.subTest(xml=xml), self.assertRaises(ValidationError):
                validate_conversation_relay(xml)

    def test_xml_rejects_empty_parameter_value(self) -> None:
        with self.assertRaises(ValidationError):
            validate_conversation_relay('<Response><Connect><ConversationRelay url="wss://e.test"><Parameter name="a" value="" /></ConversationRelay></Connect></Response>')

    def test_xml_rejects_discarded_markup_but_allows_formatting_whitespace(self) -> None:
        valid = '<Response>\n  <Connect>\n    <ConversationRelay url="wss://e.test" />\n  </Connect>\n</Response>'
        self.assertTrue(validate_conversation_relay(valid)["valid"])
        for marker in ("<!-- comment -->", "<?pi value?>", "<![CDATA[data]]>"):
            with self.subTest(marker=marker), self.assertRaises(ValidationError):
                validate_conversation_relay(f'<Response><Connect><ConversationRelay url="wss://e.test">{marker}</ConversationRelay></Connect></Response>')
        with self.assertRaises(ValidationError):
            validate_conversation_relay('<?xml version="1.0"?><Response><Connect><ConversationRelay url="wss://e.test" /></Connect></Response>')

    def test_malformed_action_url_is_a_validation_error(self) -> None:
        action = "https://[invalid/done"
        with self.assertRaises(ValidationError):
            generate_conversation_relay({"url": "wss://e.test", "action": action})
        with self.assertRaises(ValidationError):
            validate_conversation_relay(f'<Response><Connect action="{action}"><ConversationRelay url="wss://e.test" /></Connect></Response>')

    def test_generation_requires_an_absolute_wss_url(self) -> None:
        for value in ({}, {"url": "wss:relative"}, {"url": "https://example.test/relay"}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                generate_conversation_relay(value)

    def test_xml_rejects_arbitrary_twiML_and_unknown_attributes(self) -> None:
        with self.assertRaises(ValidationError):
            validate_conversation_relay("<Response><Say>no</Say></Response>")
        with self.assertRaises(ValidationError):
            generate_conversation_relay({"url": "wss://e.test", "raw": "<Say/>"})
        with self.assertRaises(ValidationError):
            generate_conversation_relay({"url": "https://e.test"})
        with self.assertRaises(ValidationError):
            generate_conversation_relay({"url": "wss://e.test", "timeout": "3"})
        with self.assertRaises(ValidationError):
            validate_conversation_relay('<Connect><ConversationRelay url="wss://e.test" /></Connect>')
        with self.assertRaises(ValidationError):
            generate_conversation_relay({"url": "wss://e.test", "events": "speaker-events,tokens-played"})
        with self.assertRaises(ValidationError):
            generate_conversation_relay({"url": "wss://e.test", "reportInputDuringAgentSpeech": True})

    def test_websocket_direction_and_unknown_fields_are_strict(self) -> None:
        valid = {"direction": "inbound", "message": {"type": "prompt", "voicePrompt": "Hi", "lang": "en-US", "last": True}}
        self.assertTrue(validate_conversation_relay_message(valid)["valid"])
        with self.assertRaises(ValidationError):
            validate_conversation_relay_message({"direction": "inbound", "message": {"type": "prompt", "voicePrompt": "Hi", "extra": 1}})
        with self.assertRaises(ValidationError):
            validate_conversation_relay_message({"message": {"type": "prompt", "voicePrompt": "Hi", "lang": "en-US"}})

    def test_websocket_outbound_optional_fields_and_types_match_twilio(self) -> None:
        self.assertTrue(validate_conversation_relay_message({
            "direction": "outbound",
            "message": {"type": "text", "token": "Hello ", "lang": "en-US"},
        })["valid"])
        self.assertTrue(validate_conversation_relay_message({
            "direction": "outbound",
            "message": {"type": "play", "source": "https://example.test/tone.mp3"},
        })["valid"])
        for message in (
            {"type": "text", "token": "Hi", "last": "false"},
            {"type": "play", "source": "https://example.test/a.mp3", "loop": True},
            {"type": "sendDigits", "digits": "9W"},
            {"type": "end", "handoffData": {"reason": "transfer"}},
        ):
            with self.subTest(message=message), self.assertRaises(ValidationError):
                validate_conversation_relay_message({"direction": "outbound", "message": message})

    def test_websocket_inbound_fields_have_strict_types(self) -> None:
        with self.assertRaises(ValidationError):
            validate_conversation_relay_message({
                "direction": "inbound",
                "message": {"type": "prompt", "voicePrompt": "Hi", "lang": "en-US", "last": "true"},
            })
        with self.assertRaises(ValidationError):
            validate_conversation_relay_message({
                "direction": "inbound",
                "message": {"type": "interrupt", "utteranceUntilInterrupt": "Hi", "durationUntilInterruptMs": -1},
            })

    def test_form_signature_uses_sorted_case_sensitive_params_and_named_env(self) -> None:
        os.environ["TEST_TWILIO_TOKEN"] = "secret"
        url = "https://example.test/hook?x=1"
        params = {"b": "two", "A": "one"}
        payload = url + "Aone" + "btwo"
        signature = base64.b64encode(hmac.new(b"secret", payload.encode(), hashlib.sha1).digest()).decode()
        self.assertTrue(validate_twilio_signature({"kind": "form", "url": url, "params": params, "signature": signature, "auth_token_env": "TEST_TWILIO_TOKEN"})["valid"])
        with self.assertRaises(ValidationError):
            validate_twilio_signature({"kind": "form", "url": url, "params": params, "signature": signature, "auth_token": "secret", "auth_token_env": "TEST_TWILIO_TOKEN"})

    def test_form_signature_canonicalizes_repeated_values_sorted_and_unique(self) -> None:
        os.environ["TEST_TWILIO_TOKEN"] = "secret"
        url = "https://example.test/hook"
        params = {"b": ["two", "one", "two"], "A": [2, 1, 2], "single": True}
        payload = url + "A1" + "A2" + "bone" + "btwo" + "singleTrue"
        signature = base64.b64encode(hmac.new(b"secret", payload.encode(), hashlib.sha1).digest()).decode()
        self.assertTrue(validate_twilio_signature({"kind": "form", "url": url, "params": params, "signature": signature, "auth_token_env": "TEST_TWILIO_TOKEN"})["valid"])
        for bad in ({"nested": [["x"]]}, {"empty": []}, {"nested": {"x": 1}}, {"empty": ""}):
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                validate_twilio_signature({"kind": "form", "url": url, "params": bad, "signature": signature, "auth_token_env": "TEST_TWILIO_TOKEN"})
        with self.assertRaises(ValidationError):
            validate_twilio_signature({"kind": "form", "url": url, "params": {"x": ["a"] * 21}, "signature": signature, "auth_token_env": "TEST_TWILIO_TOKEN"})
        with self.assertRaises(ValidationError):
            validate_twilio_signature({"kind": "form", "url": url, "params": {str(i): "v" for i in range(51)}, "signature": signature, "auth_token_env": "TEST_TWILIO_TOKEN"})
        with self.assertRaises(ValidationError):
            validate_twilio_signature({"kind": "form", "url": url, "params": {"x": "v" * 1025}, "signature": signature, "auth_token_env": "TEST_TWILIO_TOKEN"})

    def test_json_signature_checks_raw_body_hash(self) -> None:
        os.environ["TEST_TWILIO_TOKEN"] = "secret"
        body = '{"b":2}'
        digest = hashlib.sha256(body.encode()).hexdigest()
        url = "https://e.test/hook?bodySHA256=" + digest
        signature = base64.b64encode(hmac.new(b"secret", url.encode(), hashlib.sha1).digest()).decode()
        self.assertTrue(validate_twilio_signature({"kind": "json", "url": url, "body": body, "body_sha256": digest, "signature": signature, "auth_token_env": "TEST_TWILIO_TOKEN"})["valid"])

    def test_agent_connect_is_local_metadata(self) -> None:
        result = agent_connect_contract({})
        self.assertTrue(result["local_only"])
        self.assertEqual(result["channels"], ["voice", "sms", "whatsapp", "rcs", "chat"])


if __name__ == "__main__":
    unittest.main()

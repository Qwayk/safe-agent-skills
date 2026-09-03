from __future__ import annotations

import unittest

from elevenlabs_api_tool.operations import OPERATIONS


class TestOperationSafety(unittest.TestCase):
    def test_accepted_safety_audit_tags_are_present(self) -> None:
        expected = {
            "text_to_speech_full_with_timestamps": "sensitive_output",
            "text_to_speech_stream_with_timestamps": "sensitive_output",
            "text_to_dialogue_full_with_timestamps": "sensitive_output",
            "text_to_dialogue_stream_with_timestamps": "sensitive_output",
            "compose_detailed_stream": "sensitive_output",
            "dubbing_language_get": "sensitive_output",
            "get_knowledge_base_source_file_url": "sensitive_output",
            "get_dubbing_transcripts": "sensitive_output",
            "get_workspace_batch_calls": "sensitive_output",
            "get_batch_call": "sensitive_output",
            "export_batch_call": "sensitive_output",
            "stream_project_snapshot_archive_endpoint": "binary_output",
            "compose_detailed": "binary_output",
            "create_podcast": "spend_money",
            "audio_native_create": "spend_money",
            "retry_batch_call": "spend_money",
            "speech_to_text_realtime": "spend_money",
            "agents_conversation_wss": "spend_money",
            "remove_rules": "irreversible",
            "disable": "irreversible",
            "remove_member": "irreversible",
            "unshare_resource_endpoint": "irreversible",
            "cancel_crawl_job_route": "irreversible",
            "post_knowledge_base_bulk_delete_route": "irreversible",
            "cancel_batch_call": "irreversible",
            "handle_twilio_outbound_call": "irreversible",
            "handle_exotel_outbound_call": "irreversible",
            "handle_sip_trunk_outbound_call": "irreversible",
            "whatsapp_outbound_message": "irreversible",
            "public_remove_order_item": "irreversible",
            "get_similar_library_voices": "post_read",
            "get_knowledge_base_bulk_dependent_agents_route": "post_read",
        }
        by_name = {op.name: op for op in OPERATIONS}
        for name, tag in expected.items():
            self.assertIn(name, by_name)
            self.assertIn(tag, by_name[name].safety, msg=f"{name} must include {tag}")

        for name in (
            "text_to_speech_full_with_timestamps",
            "text_to_speech_stream_with_timestamps",
            "text_to_dialogue_full_with_timestamps",
            "text_to_dialogue_stream_with_timestamps",
        ):
            self.assertNotIn("binary_output", by_name[name].safety)

    def test_outbound_and_order_actions_require_spend_and_irreversible(self) -> None:
        required = {
            "handle_twilio_outbound_call", "handle_exotel_outbound_call",
            "handle_sip_trunk_outbound_call", "whatsapp_outbound_message",
            "whatsapp_outbound_call", "twilio_register_call", "retry_batch_call",
            "public_submit_order",
        }
        by_name = {op.name: set(op.safety) for op in OPERATIONS}
        for name in required:
            self.assertIn(name, by_name)
            self.assertIn("spend_money", by_name[name], msg=f"{name} must include spend_money")
            self.assertIn("irreversible", by_name[name], msg=f"{name} must include irreversible")

    def test_write_gate_requires_tagged_post_like_methods(self) -> None:
        override_tag = "post_read"
        gated_methods = {"POST", "PUT", "PATCH"}
        for op in OPERATIONS:
            method = op.method.upper()
            if method not in gated_methods:
                continue
            safety_tags = set(op.safety)
            has_write = "write" in safety_tags
            has_override = override_tag in safety_tags
            self.assertTrue(
                has_write or has_override,
                msg=f"{op.cli_command} ({method}) must include 'write' or '{override_tag}'",
            )
            self.assertFalse(
                has_write and has_override,
                msg=f"{op.cli_command} ({method}) must not mix 'write' and '{override_tag}'",
            )

    def test_delete_operations_require_write_and_irreversible(self) -> None:
        delete_tag = "DELETE"
        for op in OPERATIONS:
            method = op.method.upper()
            if method != delete_tag:
                continue
            safety_tags = set(op.safety)
            self.assertIn(
                "write",
                safety_tags,
                msg=f"{op.cli_command} ({method}) must include 'write'",
            )
            self.assertIn(
                "irreversible",
                safety_tags,
                msg=f"{op.cli_command} ({method}) must include 'irreversible'",
            )
            self.assertNotIn(
                "post_read",
                safety_tags,
                msg=f"{op.cli_command} ({method}) must not include 'post_read'",
            )

    def test_conversation_search_and_sip_reads_are_never_writes(self) -> None:
        expected_paths = {
            "/v1/convai/conversations/{conversation_id}/sip-messages",
            "/v1/convai/conversations/messages/text-search",
            "/v1/convai/conversations/messages/smart-search",
            "/v1/convai/phone-numbers/{phone_number_id}/sip-messages",
        }
        matched = [op for op in OPERATIONS if op.path in expected_paths]

        self.assertEqual({op.path for op in matched}, expected_paths)
        for op in matched:
            self.assertEqual(op.method.upper(), "GET", msg=op.path)
            self.assertEqual(set(op.safety), {"read", "sensitive_output"}, msg=op.path)

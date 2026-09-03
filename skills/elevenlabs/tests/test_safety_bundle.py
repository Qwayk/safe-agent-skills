from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from elevenlabs_api_tool.commands.operation_runner import _apply_operation
from elevenlabs_api_tool.errors import SafetyError, ToolError, ValidationError
from elevenlabs_api_tool.http import HttpResponse
from elevenlabs_api_tool.operations import OPERATIONS
from elevenlabs_api_tool.plans import (
    build_plan,
    default_verification,
    request_binding,
    validate_plan_for_apply,
    validate_request_contract,
)


class TestSafetyBundle(unittest.TestCase):
    def test_dual_verification_patch_receipt(self) -> None:
        op = next(op for op in OPERATIONS if op.name == "update_phone_number_route")
        self.assertEqual(default_verification(op=op)["type"], "composite")
        class Client:
            def __init__(self): self.calls = []
            def request(self, method, url, **kwargs):
                self.calls.append((method, kwargs.get("params")))
                return HttpResponse(status=200, headers={}, body=b'{"ok":true}', url=url)
        with tempfile.TemporaryDirectory() as tmp:
            client = Client()
            out = Path(tmp) / "result.json"
            receipt = Path(tmp) / "receipt.json"
            _, _, final = _apply_operation(ctx={"cfg": SimpleNamespace(base_url="http://example.invalid", token="t"), "http_client": client, "receipt_out": str(receipt)}, op=op, path_params={"phone_number_id":"p1"}, params={"write_only":"x"}, body={"agent_id":"a"}, files=None, args=SimpleNamespace(out=str(out), overwrite=False), plan={"request_binding":"a"})
        self.assertEqual(final["status"], "final")
        self.assertEqual(final["verification"]["type"], "composite")
        self.assertEqual(final["verification"]["local_output"]["status"], "verified")
        self.assertEqual(final["verification"]["paired_readback"]["status"], "readback_completed")
        self.assertFalse(final["verification"]["paired_readback"]["response_body_stored"])
    def test_sensitive_read_plans_local_output(self) -> None:
        op = next(op for op in OPERATIONS if op.name == "history_list")
        self.assertEqual(default_verification(op=op)["type"], "local_output")
    def setUp(self) -> None:
        self.op = next(op for op in OPERATIONS if op.name == "text_to_speech")
        self.ctx = {"cfg": SimpleNamespace(base_url="http://example.invalid", token="token")}

    def test_request_contract_rejects_missing_required_body(self) -> None:
        required = next(op for op in OPERATIONS if op.request_body_required)
        with self.assertRaises(ValidationError):
            validate_request_contract(op=required, request={"method": required.method, "path": required.path})

    def test_plan_binding_rejects_changed_path_or_body(self) -> None:
        selector = {"kind": self.op.name, "value": "voice-1", "path_params": {"voice_id": "voice-1"}}
        request = {"method": "POST", "path": self.op.path, "json": {"text": "hello"}}
        plan = build_plan(
            ctx={**self.ctx, "tool": "test", "tool_version": "1", "command_str": "test"},
            op=self.op,
            selector=selector,
            request=request,
            proposed_changes=[],
            verification_plan={},
            recovery={},
        )
        plan["reviewed"] = True
        changed = {**request, "json": {"text": "changed"}}
        with self.assertRaises(SafetyError):
            validate_plan_for_apply(plan=plan, op=self.op, ctx=self.ctx, selector=selector, request=changed)
        self.assertEqual(plan["request_binding"], request_binding(operation=self.op, selector=selector, request=request))

    def test_plan_requires_explicit_review_marker(self) -> None:
        selector = {"kind": self.op.name, "value": "voice-1", "path_params": {"voice_id": "voice-1"}}
        request = {"method": "POST", "path": self.op.path, "json": {"text": "hello"}}
        plan = build_plan(ctx={**self.ctx, "tool": "test", "tool_version": "1", "command_str": "test"}, op=self.op, selector=selector, request=request, proposed_changes=[], verification_plan={}, recovery={})
        with self.assertRaises(SafetyError):
            validate_plan_for_apply(plan=plan, op=self.op, ctx=self.ctx, selector=selector, request=request)

    def test_provider_attempt_has_durable_pending_receipt(self) -> None:
        class FailingClient:
            def request(self, *_args: object, **_kwargs: object) -> object:
                raise RuntimeError("network unavailable")

        with tempfile.TemporaryDirectory() as tmp:
            receipt = Path(tmp) / "receipt.json"
            plan = {"request_binding": "bound", "selector": {}}
            with self.assertRaises(ToolError):
                _apply_operation(
                    ctx={**self.ctx, "http_client": FailingClient(), "receipt_out": str(receipt)},
                    op=self.op,
                    path_params={"voice_id": "voice-1"},
                    params=None,
                    body={"text": "hello"},
                    files=None,
                    args=SimpleNamespace(out=str(Path(tmp) / "audio.mp3"), overwrite=False),
                    plan=plan,
                )
            self.assertIn("provider_attempt_pending", receipt.read_text(encoding="utf-8"))

    def test_real_file_contracts_and_free_form_labels(self) -> None:
        speech = next(op for op in OPERATIONS if op.name == "speech_to_text")
        voice = next(op for op in OPERATIONS if op.name == "add_voice")
        video = next(op for op in OPERATIONS if op.name == "video_to_music")
        self.assertIn("file", speech.request_file_fields)
        self.assertIn("files", voice.request_file_fields)
        self.assertIn("videos", video.request_file_fields)
        validate_request_contract(op=voice, request={"json": {"name": "x", "labels": {"team": "a"}}, "files": {"files": ["a", "b"]}})

    def test_optional_nested_required_child_is_not_global(self) -> None:
        op = next(op for op in OPERATIONS if op.name == "text_to_speech_full_with_timestamps")
        validate_request_contract(op=op, request={"json": {"text": "hello"}})
        with self.assertRaisesRegex(ValidationError, "pronunciation_dictionary_locators.pronunciation_dictionary_id"):
            validate_request_contract(
                op=op,
                request={"json": {"text": "hello", "pronunciation_dictionary_locators": {}}},
            )

    def test_required_children_are_checked_for_each_array_item(self) -> None:
        op = next(op for op in OPERATIONS if op.name == "text_to_dialogue")
        validate_request_contract(
            op=op,
            request={"json": {"inputs": [{"text": "hi", "voice_id": "v"}]}},
        )
        with self.assertRaisesRegex(ValidationError, "inputs.voice_id"):
            validate_request_contract(op=op, request={"json": {"inputs": [{"text": "hi"}]}})

    def test_nested_optional_branches_are_not_required(self) -> None:
        op = next(op for op in OPERATIONS if op.name == "create_agent_route")
        # The top-level conversation_config is required, but its optional
        # nested branches must not be demanded merely because their schemas
        # declare children as required.
        validate_request_contract(op=op, request={"json": {"conversation_config": {}}})

    def test_source_url_multipart_request_is_a_valid_form_contract(self) -> None:
        op = next(op for op in OPERATIONS if op.name == "speech_to_text")
        validate_request_contract(
            op=op,
            request={"json": {"model_id": "scribe_v1", "source_url": "https://example.invalid/a.wav"}},
        )

    def test_multipart_without_file_uses_form_data(self) -> None:
        class Client:
            def __init__(self) -> None:
                self.kwargs = None
            def request(self, *_args: object, **kwargs: object) -> object:
                self.kwargs = kwargs
                return SimpleNamespace(status=200, body=b"{}", text=lambda: "{}", json=lambda: {})
        op = next(op for op in OPERATIONS if op.name == "add_voice")
        client = Client()
        with tempfile.TemporaryDirectory() as tmp:
            _apply_operation(ctx={**self.ctx, "http_client": client, "receipt_out": str(Path(tmp) / "r.json")}, op=op, path_params={}, params=None, body={"name": "x"}, files=None, args=SimpleNamespace(out=None, overwrite=False), plan={"request_binding": "bound", "selector": {}})
        assert client.kwargs is not None
        self.assertIsNone(client.kwargs["json"])
        self.assertEqual(client.kwargs["data"], {"name": "x"})

    def test_local_output_verification_is_recorded(self) -> None:
        class Client:
            def request(self, *_args: object, **_kwargs: object) -> object:
                return SimpleNamespace(status=200, body=b"audio", text=lambda: "", json=lambda: {})
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "audio.mp3"
            result, outputs, receipt = _apply_operation(ctx={**self.ctx, "http_client": Client(), "receipt_out": str(Path(tmp) / "r.json")}, op=self.op, path_params={"voice_id": "voice-1"}, params=None, body={"text": "hello"}, files=None, args=SimpleNamespace(out=str(out), overwrite=False), plan={"request_binding": "bound", "selector": {}})
            self.assertTrue(out.exists())
            self.assertEqual(receipt["verification"]["type"], "local_output")

    def test_patch_performs_status_only_paired_get(self) -> None:
        op = next(op for op in OPERATIONS if op.name == "patch_agent_settings_route")
        class Client:
            def __init__(self) -> None: self.calls = []
            def request(self, method: str, *_args: object, **kwargs: object) -> object:
                self.calls.append((method, kwargs))
                return SimpleNamespace(status=200, body=b"{}", text=lambda: "", json=lambda: {})
        client = Client()
        with tempfile.TemporaryDirectory() as tmp:
            _, _, receipt = _apply_operation(ctx={**self.ctx, "http_client": client, "receipt_out": str(Path(tmp) / "r.json")}, op=op, path_params={"pronunciation_dictionary_id": "pd-1"}, params=None, body={"name": "x"}, files=None, args=SimpleNamespace(out=None, overwrite=False), plan={"request_binding": "bound", "selector": {}})
        self.assertEqual([x[0] for x in client.calls], ["PATCH", "GET"])
        self.assertEqual(receipt["verification"]["type"], "paired_readback")
        self.assertEqual(receipt["verification"]["status"], "readback_completed")
        self.assertFalse(receipt["verification"]["response_body_stored"])

    def test_plan_declares_paired_readback_contract(self) -> None:
        op = next(op for op in OPERATIONS if op.name == "patch_pronunciation_dictionary")
        verification = default_verification(op=op)
        self.assertEqual(verification["type"], "paired_readback")
        self.assertEqual(verification["status"], "planned")
        self.assertTrue(verification["status_only"])

    def test_paired_readback_filters_write_query_parameters(self) -> None:
        op = next(op for op in OPERATIONS if op.name == "patch_agent_settings_route")
        class Client:
            def __init__(self) -> None: self.calls = []
            def request(self, method: str, *_args: object, **kwargs: object) -> object:
                self.calls.append((method, kwargs))
                return SimpleNamespace(status=200, body=b"{}", text=lambda: "", json=lambda: {})
        client = Client()
        with tempfile.TemporaryDirectory() as tmp:
            _apply_operation(
                ctx={**self.ctx, "http_client": client, "receipt_out": str(Path(tmp) / "r.json")},
                op=op,
                path_params={"agent_id": "agent-1"},
                params={"enable_versioning_if_not_enabled": "true", "branch_id": "branch-1"},
                body={},
                files=None,
                args=SimpleNamespace(out=None, overwrite=False),
                plan={"request_binding": "bound", "selector": {}},
            )
        # The PATCH-only query field must not leak into the GET readback.
        self.assertEqual(client.calls[1][1]["params"], {"branch_id": "branch-1"})

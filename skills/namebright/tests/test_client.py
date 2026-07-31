from __future__ import annotations

import dataclasses
import unittest
from collections import deque

from namebright_safe_cli.client import NameBrightClient
from namebright_safe_cli.config import Config
from namebright_safe_cli.errors import NotSupportedError, ToolError
from namebright_safe_cli.operations import get_operation


class _FakeResponse:
    def __init__(self, status_code: int, payload: object | None = None, headers: dict[str, str] | None = None):
        self.status_code = status_code
        self.headers = headers or {}
        self.url = "https://api.namebright.com/rest/test"
        self.content = b"" if payload is None else str(_dumps_json(payload)).encode("utf-8")
        self.text = self.content.decode("utf-8", errors="replace")

    def json(self):
        import json

        return json.loads(self.text) if self.text else None


def _dumps_json(value: object) -> str:
    import json

    return json.dumps(value)


class _InvalidJsonResponse(_FakeResponse):
    def __init__(self):
        super().__init__(200)
        self.content = b"not-json"
        self.text = "not-json"

    def json(self):
        import json

        return json.loads(self.text)


class _FakeSession:
    def __init__(self, responses):
        self.responses = deque(responses)
        self.calls = []

    def request(self, *args, **kwargs):  # noqa: ANN003
        self.calls.append((args, kwargs))
        if not self.responses:
            raise RuntimeError("No responses left")
        return self.responses.popleft()


class TestNameBrightClient(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = Config(
            base_url="https://api.namebright.com/rest",
            token_url="https://api.namebright.com/auth/token",
            timeout_s=10.0,
            client_id="client-id",
            client_secret="client-secret",
        )

    def test_token_request_is_client_credentials_form(self) -> None:
        token_resp = _FakeResponse(200, {"access_token": "abc", "expires_in": 900})
        session = _FakeSession([token_resp])
        client = NameBrightClient(cfg=self.cfg, timeout_s=10.0, verbose=False, user_agent="u", transport=session)

        status = client.request_token_status()
        self.assertTrue(status["ok"])
        self.assertTrue(status["token_status"]["exists"])
        self.assertNotIn("access_token", str(status["token_status"]["fields"]))
        self.assertEqual(len(session.calls), 1)

        first_kwargs = session.calls[0][1]
        self.assertEqual(first_kwargs["method"], "POST")
        self.assertEqual(first_kwargs["url"], "https://api.namebright.com/auth/token")
        self.assertNotIn("Authorization", first_kwargs["headers"])
        self.assertEqual(
            first_kwargs["data"],
            {"grant_type": "client_credentials", "client_id": "client-id", "client_secret": "client-secret"},
        )

    def test_contacts_result_redacts_sensitive_fields(self) -> None:
        token_resp = _FakeResponse(200, {"access_token": "abc", "expires_in": 900})
        contact_resp = _FakeResponse(
            200,
            {
                "AuthCode": "abc",
                "Verification": "123",
                "AccountBalance": "$99",
                "contacts": [{"Email": "owner@example.com", "AuthCode": "x"}],
            },
        )
        session = _FakeSession([token_resp, contact_resp])
        client = NameBrightClient(cfg=self.cfg, timeout_s=10.0, verbose=False, user_agent="u", transport=session)

        spec = get_operation("contacts", "contacts get-all")
        self.assertIsNotNone(spec)
        result = client.execute_operation(spec, values={"domain": "example.com"})
        self.assertFalse(hasattr(result, "response"))
        self.assertEqual(result.payload["AuthCode"], "***REDACTED***")
        self.assertEqual(result.payload["Verification"], "***REDACTED***")
        self.assertEqual(result.payload["AccountBalance"], "***REDACTED***")
        self.assertEqual(result.payload["contacts"][0]["Email"], "***REDACTED***")
        self.assertEqual(result.payload["contacts"][0]["AuthCode"], "***REDACTED***")

    def test_contact_comparison_returns_only_safe_field_names(self) -> None:
        token_resp = _FakeResponse(200, {"access_token": "abc", "expires_in": 900})
        contact_resp = _FakeResponse(
            200,
            {
                "FirstName": "Alice",
                "LastName": "Owner",
                "Email": "owner@example.com",
                "Phone": "5125550101",
            },
        )
        session = _FakeSession([token_resp, contact_resp])
        client = NameBrightClient(
            cfg=self.cfg,
            timeout_s=10.0,
            verbose=False,
            user_agent="u",
            transport=session,
        )

        spec = get_operation("contacts", "contacts get-administrative")
        self.assertIsNotNone(spec)
        result = client.execute_operation(spec, values={"domain": "example.com"})
        comparison = result.compare_contact_fields(
            {
                "FirstName": "Alice",
                "LastName": "Different",
                "Email": "owner@example.com",
                "Fax": "5125550199",
            }
        )

        self.assertEqual(
            comparison,
            {
                "matched": ["Email", "FirstName"],
                "mismatched": ["LastName"],
                "unavailable": ["Fax"],
            },
        )
        comparison_text = str(comparison)
        self.assertNotIn("Alice", comparison_text)
        self.assertNotIn("owner@example.com", comparison_text)
        self.assertNotIn("5125550101", comparison_text)
        self.assertNotIn("owner@example.com", repr(result))

    def test_path_values_are_url_quoted(self) -> None:
        token_resp = _FakeResponse(200, {"access_token": "abc", "expires_in": 900})
        account_resp = _FakeResponse(200, {"ok": True})
        session = _FakeSession([token_resp, account_resp])
        client = NameBrightClient(cfg=self.cfg, timeout_s=10.0, verbose=False, user_agent="u", transport=session)

        spec = get_operation("contacts", "contacts get-administrative")
        self.assertIsNotNone(spec)
        client.execute_operation(spec, values={"domain": "bad/domain.com"})

        second_kwargs = session.calls[1][1]
        self.assertEqual(second_kwargs["method"], "GET")
        self.assertIn("bad%2Fdomain.com", second_kwargs["url"])
        self.assertNotIn("bad/domain.com", second_kwargs["url"])

    def test_cached_token_reused(self) -> None:
        token_resp = _FakeResponse(200, {"access_token": "abc", "expires_in": 900})
        first = _FakeResponse(200, {"ok": True})
        second = _FakeResponse(200, {"ok": True})
        session = _FakeSession([token_resp, first, second])
        client = NameBrightClient(cfg=self.cfg, timeout_s=10.0, verbose=False, user_agent="u", transport=session)

        spec = get_operation("account", "account show")
        self.assertIsNotNone(spec)
        client.execute_operation(spec)
        client.execute_operation(spec)
        self.assertEqual(len(session.calls), 3)

    def test_two_clients_do_not_share_token_cache(self) -> None:
        token_resp1 = _FakeResponse(200, {"access_token": "abc", "expires_in": 900})
        account1 = _FakeResponse(200, {"ok": True})
        token_resp2 = _FakeResponse(200, {"access_token": "xyz", "expires_in": 900})
        account2 = _FakeResponse(200, {"ok": True})
        session = _FakeSession([token_resp1, account1, token_resp2, account2])

        client_a = NameBrightClient(cfg=self.cfg, timeout_s=10.0, verbose=False, user_agent="u", transport=session)
        client_b = NameBrightClient(cfg=self.cfg, timeout_s=10.0, verbose=False, user_agent="u", transport=session)
        op = get_operation("account", "account show")
        self.assertIsNotNone(op)
        client_a.execute_operation(op)
        client_b.execute_operation(op)
        self.assertEqual(len(session.calls), 4)

    def test_reject_non_official_host(self) -> None:
        token_resp = _FakeResponse(200, {"access_token": "abc", "expires_in": 900})
        session = _FakeSession([token_resp])
        cfg = Config(
            base_url="https://evil.example.com/rest",
            token_url="https://api.namebright.com/auth/token",
            timeout_s=10.0,
            client_id="client-id",
            client_secret="client-secret",
        )
        client = NameBrightClient(cfg=cfg, timeout_s=10.0, verbose=False, user_agent="u", transport=session)
        spec = get_operation("account", "account show")
        self.assertIsNotNone(spec)
        with self.assertRaises(ToolError):
            client.execute_operation(spec)

    def test_429_retry_once_with_cap(self) -> None:
        import namebright_safe_cli.client as client_module

        sleep_calls: list[float] = []
        current = {"now": 1.0}

        def fake_sleep(seconds: float) -> None:
            sleep_calls.append(seconds)
            current["now"] += seconds

        def fake_time() -> float:
            return current["now"]

        token_resp = _FakeResponse(200, {"access_token": "abc", "expires_in": 900})
        rate_limited = _FakeResponse(
            429,
            {"error": "retry"},
            headers={"retry-after": "120"},
        )
        success = _FakeResponse(200, {"ok": True})
        session = _FakeSession([token_resp, rate_limited, success])
        client = NameBrightClient(cfg=self.cfg, timeout_s=10.0, verbose=False, user_agent="u", transport=session)

        try:
            original_time = client_module.time.time
            original_sleep = client_module.time.sleep
            client_module.time.sleep = fake_sleep
            client_module.time.time = fake_time

            spec = get_operation("account", "account show")
            self.assertIsNotNone(spec)
            out = client.execute_operation(spec)
            self.assertEqual(out.payload["ok"], True)
            self.assertIn(30.0, sleep_calls)
        finally:
            client_module.time.sleep = original_sleep
            client_module.time.time = original_time

    def test_retry_on_500_not_done(self) -> None:
        token_resp = _FakeResponse(200, {"access_token": "abc", "expires_in": 900})
        fail = _FakeResponse(500, {"error": "boom"})
        session = _FakeSession([token_resp, fail])
        client = NameBrightClient(cfg=self.cfg, timeout_s=10.0, verbose=False, user_agent="u", transport=session)
        spec = get_operation("account", "account show")
        self.assertIsNotNone(spec)
        with self.assertRaises(RuntimeError):
            client.execute_operation(spec)
        self.assertEqual(len(session.calls), 2)

    def test_rejects_unknown_fields_before_session_call(self) -> None:
        session = _FakeSession([])
        client = NameBrightClient(cfg=self.cfg, timeout_s=10.0, verbose=False, user_agent="u", transport=session)
        spec = get_operation("account", "account show")
        self.assertIsNotNone(spec)
        with self.assertRaises(RuntimeError):
            client.execute_operation(spec, values={"unexpected": "x"})
        self.assertEqual(len(session.calls), 0)

    def test_auth_config_fields_cannot_be_overridden(self) -> None:
        session = _FakeSession([])
        client = NameBrightClient(
            cfg=self.cfg,
            timeout_s=10.0,
            verbose=False,
            user_agent="u",
            transport=session,
        )
        spec = get_operation("auth", "auth token")
        self.assertIsNotNone(spec)
        with self.assertRaisesRegex(RuntimeError, "client_id"):
            client.execute_operation(spec, values={"client_id": "other-client"})
        self.assertEqual(len(session.calls), 0)

    def test_unknown_operation_rejected(self) -> None:
        token_resp = _FakeResponse(200, {"access_token": "abc", "expires_in": 900})
        session = _FakeSession([token_resp])
        client = NameBrightClient(cfg=self.cfg, timeout_s=10.0, verbose=False, user_agent="u", transport=session)
        fake = get_operation("account", "account show")
        self.assertIsNotNone(fake)
        fake_copy = dataclasses.replace(fake, path="different")
        with self.assertRaises(NotSupportedError):
            client.execute_operation(fake_copy)

    def test_invalid_json_error_does_not_include_url(self) -> None:
        session = _FakeSession([_InvalidJsonResponse()])
        client = NameBrightClient(cfg=self.cfg, timeout_s=10.0, verbose=False, user_agent="u", transport=session)
        with self.assertRaises(RuntimeError) as exc:
            client.request_token_status()
        self.assertNotIn("https://api.namebright.com/auth/token", str(exc.exception))
        self.assertIsNone(exc.exception.__cause__)

    def test_auth_spec_path_stays_official(self) -> None:
        token = _FakeResponse(200, {"access_token": "abc", "expires_in": 900})
        session = _FakeSession([token])
        client = NameBrightClient(cfg=self.cfg, timeout_s=10.0, verbose=False, user_agent="u", transport=session)
        spec = get_operation("auth", "auth token")
        self.assertIsNotNone(spec)
        client.execute_operation(spec)
        self.assertEqual(session.calls[0][1]["url"], "https://api.namebright.com/auth/token")

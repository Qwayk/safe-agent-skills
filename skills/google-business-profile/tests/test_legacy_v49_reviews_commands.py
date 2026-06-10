from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from google_business_profile_safe_agent_cli.cli import main
from google_business_profile_safe_agent_cli.http import HttpResponse


class _FakeCredentials:
    def __init__(self, token: str, valid: bool = True) -> None:
        self.token = token
        self.valid = valid

    def refresh(self, request: object) -> None:  # noqa: ANN001
        self.valid = True


def _make_request_file(root: Path) -> None:
    root.joinpath(".state").mkdir(parents=True, exist_ok=True)
    token = root / ".state" / "oauth_credentials.json"
    token.write_text("{}", encoding="utf-8")


def _body_fingerprint(body: object) -> str:
    return hashlib.sha256(
        json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _write_review_plan(path: Path, *, name: str, operation: str, body: dict, mask: str) -> None:
    path.write_text(
        json.dumps(
            {
                "operation": operation,
                "selector": name,
                "baseline": {
                    "mask": mask,
                    "body_fingerprint": _body_fingerprint(body),
                    "mask_fingerprint": hashlib.sha256(mask.encode("utf-8")).hexdigest(),
                },
                "proposed_changes": [
                    {
                        "operation": operation,
                        "selector": name,
                        "mask": mask,
                        "body_fingerprint": _body_fingerprint(body),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


class TestLegacyV49ReviewsCommands(unittest.TestCase):
    def setUp(self) -> None:
        obsolete_fragments = (
            "apply_verifies",
            "apply_marks_changed_false",
            "apply_requires_plan_in_and_yes",
        )
        if any(fragment in self._testMethodName for fragment in obsolete_fragments):
            self.skipTest("Live Google Business Profile writes are guarded by explicit no-snapshot approval.")
        self._env_text = "GBP_TIMEOUT_S=30\n"

    def test_reviews_list_honors_parent_paging_and_order_by(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            request_data: dict[str, object] = {}

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                request_data["data"] = data
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"reviews":[{"name":"accounts/123/locations/456/reviews/abc"}]}',
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "list",
                        "--parent",
                        "accounts/123/locations/456",
                        "--page-size",
                        "20",
                        "--page-token",
                        "next-page",
                        "--order-by",
                        "rating desc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "legacy-v49.accounts.locations.reviews.list")
            self.assertEqual(payload["request"]["path"], "v4/accounts/123/locations/456/reviews")
            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(
                request_data["url"],
                "https://mybusiness.googleapis.com/v4/accounts/123/locations/456/reviews",
            )
            self.assertEqual((request_data["params"] or {}).get("pageSize"), 20)
            self.assertEqual((request_data["params"] or {}).get("pageToken"), "next-page")
            self.assertEqual((request_data["params"] or {}).get("orderBy"), "rating desc")

    def test_reviews_list_rejects_large_page_size(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "list",
                        "--parent",
                        "accounts/123/locations/456",
                        "--page-size",
                        "51",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_reviews_list_rejects_invalid_order_by(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "list",
                        "--parent",
                        "accounts/123/locations/456",
                        "--order-by",
                        "bad",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_reviews_get_calls_get_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            request_data: dict[str, object] = {}

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                request_data["method"] = method
                request_data["url"] = url
                request_data["params"] = params
                request_data["body"] = json_body
                return HttpResponse(status=200, headers={}, body=b'{"name":"accounts/123/locations/456/reviews/abc"}', url=url)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "get",
                        "--name",
                        "accounts/123/locations/456/reviews/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "legacy-v49.accounts.locations.reviews.get")
            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(
                request_data["url"],
                "https://mybusiness.googleapis.com/v4/accounts/123/locations/456/reviews/abc",
            )

    def test_reviews_get_rejects_malformed_name(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "get",
                        "--name",
                        "accounts/123/reviews/bad",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_reviews_update_reply_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "plan.json"
            reply = {"comment": "Great place!"}
            reply_file = root / "reply.json"
            reply_file.write_text(json.dumps(reply), encoding="utf-8")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "update-reply",
                        "--name",
                        "accounts/123/locations/456/reviews/abc",
                        "--reply-file",
                        str(reply_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["selector"], "accounts/123/locations/456/reviews/abc")
            self.assertEqual(payload["plan"]["baseline"]["body_fingerprint"], _body_fingerprint(reply))
            self.assertTrue(plan_path.exists())

    def test_reviews_update_reply_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            reply_file = root / "reply.json"
            reply_file.write_text(json.dumps({"comment": "Good"}), encoding="utf-8")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "update-reply",
                        "--name",
                        "accounts/123/locations/456/reviews/abc",
                        "--reply-file",
                        str(reply_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")

    def test_reviews_update_reply_rejects_non_safe_review_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            reply_file = root / "reply.json"
            reply_file.write_text(json.dumps({"comment": "Good", "extra": 1}), encoding="utf-8")
            plan_path = root / "plan.json"
            plan_path.write_text("{}", encoding="utf-8")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--plan-in",
                        str(plan_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "update-reply",
                        "--name",
                        "accounts/123/locations/456/reviews/abc",
                        "--reply-file",
                        str(reply_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_reviews_update_reply_rejects_blank_comment(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            reply_file = root / "reply.json"
            reply_file.write_text(json.dumps({"comment": "   "}), encoding="utf-8")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "update-reply",
                        "--name",
                        "accounts/123/locations/456/reviews/abc",
                        "--reply-file",
                        str(reply_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_reviews_update_reply_rejects_comment_over_4096_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            reply_file = root / "reply.json"
            reply_file.write_text(json.dumps({"comment": "a" * 4097}), encoding="utf-8")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "update-reply",
                        "--name",
                        "accounts/123/locations/456/reviews/abc",
                        "--reply-file",
                        str(reply_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_reviews_update_reply_apply_refuses_plan_mismatch_without_http_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            reply = {"comment": "Thanks for the review"}
            reply_file = root / "reply.json"
            reply_file.write_text(json.dumps(reply), encoding="utf-8")
            plan_path = root / "plan.json"
            _write_review_plan(
                path=plan_path,
                name="accounts/123/locations/456/reviews/abc",
                operation="legacy-v49.accounts.locations.reviews.update-reply",
                body={"comment": "Different"},
                mask="reviewReply",
            )
            calls: list[str] = []

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                return HttpResponse(status=200, headers={}, body=b"{}", url=url)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "update-reply",
                        "--name",
                        "accounts/123/locations/456/reviews/abc",
                        "--reply-file",
                        str(reply_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertEqual(len(calls), 0)

    def test_reviews_update_reply_apply_verifies_comment(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            reply = {"comment": "Thanks for the review"}
            reply_file = root / "reply.json"
            reply_file.write_text(json.dumps(reply), encoding="utf-8")
            plan_path = root / "plan.json"
            _write_review_plan(
                path=plan_path,
                name="accounts/123/locations/456/reviews/abc",
                operation="legacy-v49.accounts.locations.reviews.update-reply",
                body=reply,
                mask="reviewReply",
            )
            calls: list[str] = []

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                if method == "PUT":
                    return HttpResponse(status=200, headers={}, body=b'{}', url=url)
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=b'{"reviewReply":{"comment":"Thanks for the review"}}',
                        url=url,
                    )
                return HttpResponse(status=200, headers={}, body=b"{}", url=url)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "update-reply",
                        "--name",
                        "accounts/123/locations/456/reviews/abc",
                        "--reply-file",
                        str(reply_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["operation"], "legacy-v49.accounts.locations.reviews.update-reply")
            self.assertTrue(payload["receipt"]["changed"])
            self.assertTrue(payload["receipt"]["verification"]["ok"])
            self.assertGreaterEqual(len(calls), 2)

    def test_reviews_update_reply_apply_marks_changed_false_when_follow_up_mismatches(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            reply = {"comment": "Thanks for the review"}
            reply_file = root / "reply.json"
            reply_file.write_text(json.dumps(reply), encoding="utf-8")
            plan_path = root / "plan.json"
            _write_review_plan(
                path=plan_path,
                name="accounts/123/locations/456/reviews/abc",
                operation="legacy-v49.accounts.locations.reviews.update-reply",
                body=reply,
                mask="reviewReply",
            )

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "PUT":
                    return HttpResponse(status=200, headers={}, body=b"{}", url=url)
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"reviewReply":{"comment":"Different reply"}}',
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "update-reply",
                        "--name",
                        "accounts/123/locations/456/reviews/abc",
                        "--reply-file",
                        str(reply_file),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["receipt"]["changed"])
            self.assertFalse(payload["receipt"]["verification"]["ok"])

    def test_reviews_delete_reply_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "plan.json"

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "delete-reply",
                        "--name",
                        "accounts/123/locations/456/reviews/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["selector"], "accounts/123/locations/456/reviews/abc")
            self.assertTrue(plan_path.exists())

    def test_reviews_delete_reply_apply_requires_plan_in_and_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "delete-reply",
                        "--name",
                        "accounts/123/locations/456/reviews/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")

            plan_path = root / "plan.json"
            _write_review_plan(
                path=plan_path,
                name="accounts/123/locations/456/reviews/abc",
                operation="legacy-v49.accounts.locations.reviews.delete-reply",
                body={},
                mask="reviewReply",
            )
            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                return HttpResponse(status=200, headers={}, body=b"", url=url)
            buf = io.StringIO()
            with (
                patch(
                    "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                    return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
                ),
                patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request),
                redirect_stdout(buf),
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "delete-reply",
                        "--name",
                        "accounts/123/locations/456/reviews/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertNotIn("refused", payload)

    def test_reviews_delete_reply_apply_requires_yes_and_makes_no_http_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "plan.json"
            _write_review_plan(
                path=plan_path,
                name="accounts/123/locations/456/reviews/abc",
                operation="legacy-v49.accounts.locations.reviews.delete-reply",
                body={},
                mask="reviewReply",
            )
            calls: list[str] = []

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                return HttpResponse(status=200, headers={}, body=b"", url=url)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "delete-reply",
                        "--name",
                        "accounts/123/locations/456/reviews/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertEqual(len(calls), 0)

    def test_reviews_delete_reply_apply_refuses_plan_mismatch_without_http_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "plan.json"
            _write_review_plan(
                path=plan_path,
                name="accounts/123/locations/456/reviews/abc",
                operation="legacy-v49.accounts.locations.reviews.delete-reply",
                body={"comment": "mismatch"},
                mask="reviewReply",
            )
            calls: list[str] = []

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                return HttpResponse(status=200, headers={}, body=b"", url=url)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "delete-reply",
                        "--name",
                        "accounts/123/locations/456/reviews/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertEqual(len(calls), 0)

    def test_reviews_delete_reply_apply_verifies_reply_gone(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "plan.json"
            _write_review_plan(
                path=plan_path,
                name="accounts/123/locations/456/reviews/abc",
                operation="legacy-v49.accounts.locations.reviews.delete-reply",
                body={},
                mask="reviewReply",
            )
            calls: list[str] = []

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                if method == "DELETE":
                    return HttpResponse(status=200, headers={}, body=b"", url=url)
                if method == "GET":
                    return HttpResponse(status=200, headers={}, body=b"{}", url=url)
                return HttpResponse(status=200, headers={}, body=b"{}", url=url)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "delete-reply",
                        "--name",
                        "accounts/123/locations/456/reviews/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["operation"], "legacy-v49.accounts.locations.reviews.delete-reply")
            self.assertTrue(payload["receipt"]["changed"])
            self.assertTrue(payload["receipt"]["verification"]["ok"])
            self.assertGreaterEqual(len(calls), 2)

    def test_reviews_delete_reply_apply_marks_changed_false_when_reply_still_exists(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)
            plan_path = root / "plan.json"
            _write_review_plan(
                path=plan_path,
                name="accounts/123/locations/456/reviews/abc",
                operation="legacy-v49.accounts.locations.reviews.delete-reply",
                body={},
                mask="reviewReply",
            )

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: bytes | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "DELETE":
                    return HttpResponse(status=200, headers={}, body=b"", url=url)
                return HttpResponse(
                    status=200,
                    headers={},
                    body=b'{"reviewReply":{"comment":"Still here"}}',
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "legacy-v49",
                        "accounts",
                        "locations",
                        "reviews",
                        "delete-reply",
                        "--name",
                        "accounts/123/locations/456/reviews/abc",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["receipt"]["changed"])
            self.assertFalse(payload["receipt"]["verification"]["ok"])

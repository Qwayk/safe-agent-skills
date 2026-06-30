from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.commands import data_collections
from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def __init__(self) -> None:
        self.writes: list[tuple[str, dict]] = []

    def write(self, action: str, payload: dict) -> None:
        self.writes.append((action, payload))


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestDataCollectionsCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, verbose: bool = False, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        if cfg_override:
            for key, value in cfg_override.items():
                setattr(cfg, key, value)
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": verbose,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }
        ctx.update(
            {
                "tool": "wix-safe-agent-cli",
                "tool_version": "0.0.0",
                "command_str": "wix-safe-agent-cli data-collections",
                "apply": False,
                "yes": False,
                "plan_in": None,
                "plan_out": None,
                "receipt_out": None,
                "ack_irreversible": False,
            }
        )
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_list_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"dataCollections": [], "pagingMetadata": {"count": 0}}
        )
        args = SimpleNamespace(
            fields_json='["name","count"]',
            limit=20,
            offset=2,
            sort_field_name="createdDate",
            sort_order="DESC",
            consistent_read=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_list(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "data-collections.list")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/wix-data/v2/collections")
        params = payload["request"]["params"]
        self.assertEqual(params["paging.limit"], 20)
        self.assertEqual(params["paging.offset"], 2)
        self.assertEqual(params["sort.fieldName"], "createdDate")
        self.assertEqual(params["sort.order"], "DESC")
        self.assertEqual(params["fields"], ["name", "count"])
        self.assertTrue(params["consistentRead"])

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"_id": "c1", "name": "Blog"})
        args = SimpleNamespace(data_collection_id="posts", fields_json='["name"]', consistent_read=True)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "data-collections.get")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/wix-data/v2/collections/posts")
        self.assertEqual(payload["request"]["params"]["fields"], ["name"])
        self.assertTrue(payload["request"]["params"]["consistentRead"])

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_create_dry_run_emits_plan_with_defaults(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [RuntimeError("HTTP 404 for https://www.wixapis.com/wix-data/v2/collections/blog")]
        args = SimpleNamespace(
            collection_id="blog",
            display_name=None,
            display_field=None,
            field_json=['{"key":"title","type":"text"}'],
            permission_insert="ADMIN",
            permission_update="ADMIN",
            permission_remove="ADMIN",
            permission_read="ADMIN",
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "data-collections.create")
        self.assertTrue(payload["dry_run"])
        self.assertIn("plan", payload)
        request = payload["plan"]["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/wix-data/v2/collections")
        body = request["body"]["collection"]
        self.assertEqual(body["id"], "blog")
        self.assertEqual(body["fields"], [{"key": "title", "type": "TEXT"}])
        self.assertEqual(
            body["permissions"],
            {"insert": "ADMIN", "update": "ADMIN", "remove": "ADMIN", "read": "ADMIN"},
        )

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_create_dry_run_refuses_when_collection_exists(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"collection": {"_id": "blog"}})
        args = SimpleNamespace(
            collection_id="blog",
            display_name=None,
            display_field=None,
            field_json=['{"key":"title","type":"text"}'],
            permission_insert="ADMIN",
            permission_update="ADMIN",
            permission_remove="ADMIN",
            permission_read="ADMIN",
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("already exists", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_create_apply_refuses_when_collection_already_exists(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"collection": {"_id": "blog"}})
        args = SimpleNamespace(
            collection_id="blog",
            display_name=None,
            display_field=None,
            field_json=['{"key":"title","type":"text"}'],
            permission_insert="ADMIN",
            permission_update="ADMIN",
            permission_remove="ADMIN",
            permission_read="ADMIN",
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertFalse(payload["dry_run"])
        self.assertIn("already exists", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_create_apply_reads_back_created_collection(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            RuntimeError("HTTP 404 for https://www.wixapis.com/wix-data/v2/collections/blog"),
            _DummyResponse({"collection": {"id": "blog"}}),
            _DummyResponse({"collection": {"id": "blog", "displayName": "Blog"}}),
        ]
        args = SimpleNamespace(
            collection_id="blog",
            display_name="Blog",
            display_field="title",
            field_json=['{"key":"title","type":"text"}'],
            permission_insert="ADMIN",
            permission_update="ADMIN",
            permission_remove="ADMIN",
            permission_read="ADMIN",
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["method"], "data-collections.create")
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        self.assertEqual(payload["receipt"]["verification"]["path"], "/wix-data/v2/collections/blog")
        self.assertEqual(payload["receipt"]["verification"]["response"]["collection"]["displayName"], "Blog")
        call_args_list = mock_client.return_value.request.call_args_list
        self.assertEqual(len(call_args_list), 3)
        self.assertEqual(call_args_list[1].kwargs["method"], "POST")
        self.assertEqual(call_args_list[1].kwargs["json_body"]["collection"]["fields"], [{"key": "title", "type": "TEXT"}])
        self.assertEqual(call_args_list[2].kwargs["method"], "GET")

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_update_dry_run_preserves_revision_and_snapshot_shape(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "collection": {
                    "id": "blog",
                    "revision": "rev-1",
                    "displayName": "Old Name",
                    "displayField": "title",
                    "fields": [{"key": "title", "type": "TEXT"}],
                    "permissions": {
                        "insert": "SITE_MEMBER",
                        "update": "SITE_MEMBER_AUTHOR",
                        "remove": "SITE_MEMBER",
                        "read": "ANYONE",
                    },
                    "plugins": [{"id": "plugin-a"}],
                }
            }
        )
        args = SimpleNamespace(
            data_collection_id="blog",
            display_name="New Name",
            display_field=None,
            field_json=None,
            permission_insert=None,
            permission_update=None,
            permission_remove=None,
            permission_read=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "data-collections.update")
        request = payload["plan"]["request"]["body"]["collection"]
        self.assertEqual(request["id"], "blog")
        self.assertEqual(request["revision"], "rev-1")
        self.assertEqual(request["displayName"], "New Name")
        self.assertEqual(request["displayField"], "title")
        self.assertEqual(request["fields"], [{"key": "title", "type": "TEXT"}])
        self.assertEqual(
            request["permissions"],
            {
                "insert": "SITE_MEMBER",
                "update": "SITE_MEMBER_AUTHOR",
                "remove": "SITE_MEMBER",
                "read": "ANYONE",
            },
        )
        self.assertEqual(request["plugins"], [{"id": "plugin-a"}])

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_update_refuses_noop_changes(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "collection": {
                    "id": "blog",
                    "revision": "rev-1",
                    "displayName": "Blog",
                    "displayField": "title",
                    "fields": [{"key": "title", "type": "TEXT"}],
                    "permissions": {
                        "insert": "ADMIN",
                        "update": "ADMIN",
                        "remove": "ADMIN",
                        "read": "ADMIN",
                    },
                    "plugins": [{"id": "plugin-a"}],
                }
            }
        )
        args = SimpleNamespace(
            data_collection_id="blog",
            display_name=None,
            display_field=None,
            field_json=None,
            permission_insert=None,
            permission_update=None,
            permission_remove=None,
            permission_read=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertTrue(payload["refused"])
        self.assertIn("no material changes", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_update_refuses_missing_collection(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            RuntimeError("HTTP 404 for https://www.wixapis.com/wix-data/v2/collections/blog")
        ]
        args = SimpleNamespace(
            data_collection_id="blog",
            display_name="Name",
            display_field=None,
            field_json=None,
            permission_insert=None,
            permission_update=None,
            permission_remove=None,
            permission_read=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("does not exist", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_update_apply_put_and_verify(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse(
                {
                    "collection": {
                        "id": "blog",
                        "revision": "rev-2",
                        "displayName": "Original",
                        "displayField": "title",
                        "fields": [{"key": "title", "type": "TEXT"}],
                        "permissions": {
                            "insert": "ADMIN",
                            "update": "ADMIN",
                            "remove": "ADMIN",
                            "read": "ADMIN",
                        },
                        "plugins": [{"id": "plugin-a"}],
                    }
                }
            ),
            _DummyResponse(
                {
                    "collection": {
                        "id": "blog",
                        "revision": "rev-3",
                        "displayName": "Updated",
                        "displayField": "title",
                        "fields": [{"key": "title", "type": "TEXT"}],
                        "permissions": {
                            "insert": "ADMIN",
                            "update": "ADMIN",
                            "remove": "ADMIN",
                            "read": "ADMIN",
                        },
                        "plugins": [{"id": "plugin-a"}],
                    }
                }
            ),
            _DummyResponse(
                {
                    "collection": {
                        "id": "blog",
                        "revision": "rev-3",
                        "displayName": "Updated",
                        "displayField": "title",
                        "fields": [{"key": "title", "type": "TEXT"}],
                        "permissions": {
                            "insert": "ADMIN",
                            "update": "ADMIN",
                            "remove": "ADMIN",
                            "read": "ADMIN",
                        },
                        "plugins": [{"id": "plugin-a"}],
                    }
                }
            ),
        ]
        args = SimpleNamespace(
            data_collection_id="blog",
            display_name="Updated",
            display_field=None,
            field_json=None,
            permission_insert=None,
            permission_update=None,
            permission_remove=None,
            permission_read=None,
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["method"], "data-collections.update")
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        self.assertEqual(payload["receipt"]["verification"]["method"], "GET")
        self.assertEqual(payload["receipt"]["verification"]["path"], "/wix-data/v2/collections/blog")
        calls = mock_client.return_value.request.call_args_list
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[1].kwargs["method"], "PUT")
        self.assertIn("/wix-data/v2/collections", calls[1].kwargs["url"])
        self.assertEqual(calls[1].kwargs["json_body"]["collection"]["revision"], "rev-2")
        self.assertEqual(calls[1].kwargs["json_body"]["collection"]["displayName"], "Updated")

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_delete_dry_run_plan_includes_before_state_and_risk_flags(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "collection": {
                    "id": "blog",
                    "revision": "rev-1",
                    "displayName": "Blog",
                    "displayField": "title",
                    "fields": [{"key": "title", "type": "TEXT"}],
                    "permissions": {
                        "insert": "ADMIN",
                        "update": "ADMIN",
                        "remove": "ADMIN",
                        "read": "ADMIN",
                    },
                    "plugins": [{"id": "plugin-a"}],
                }
            }
        )
        args = SimpleNamespace(data_collection_id="blog")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "data-collections.delete")
        plan = payload["plan"]
        self.assertEqual(plan["method"], "data-collections.delete")
        self.assertEqual(plan["risk_level"], "high")
        self.assertIn("irreversible", plan["risk_reasons"])
        self.assertIn("manage-data-collections", plan["risk_reasons"])
        self.assertIn("collection should be exported/archived before delete", plan["preconditions"])
        before_state = plan["baseline"]["before_state"]
        self.assertEqual(before_state["id"], "blog")
        self.assertEqual(before_state["revision"], "rev-1")
        self.assertEqual(before_state["displayName"], "Blog")
        self.assertEqual(before_state["plugins"], [{"id": "plugin-a"}])

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_delete_refuses_missing_collection(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            RuntimeError("HTTP 404 for https://www.wixapis.com/wix-data/v2/collections/blog")
        ]
        args = SimpleNamespace(data_collection_id="blog")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("does not exist", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_delete_apply_succeeds_with_404_verification(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse(
                {
                    "collection": {
                        "id": "blog",
                        "revision": "rev-1",
                        "displayName": "Blog",
                        "displayField": "title",
                        "fields": [{"key": "title", "type": "TEXT"}],
                        "permissions": {
                            "insert": "ADMIN",
                            "update": "ADMIN",
                            "remove": "ADMIN",
                            "read": "ADMIN",
                        },
                    }
                }
            ),
            _DummyResponse({}),
            RuntimeError("HTTP 404 for https://www.wixapis.com/wix-data/v2/collections/blog"),
        ]
        args = SimpleNamespace(data_collection_id="blog")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["method"], "data-collections.delete")
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        self.assertTrue(payload["receipt"]["verification"]["removed"])
        calls = mock_client.return_value.request.call_args_list
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[1].kwargs["method"], "DELETE")
        self.assertEqual(calls[1].kwargs["url"], "https://www.wixapis.com/wix-data/v2/collections/blog")
        self.assertEqual(calls[2].kwargs["method"], "GET")

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_delete_apply_refuses_drifted_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        before = {
            "collection": {
                "id": "blog",
                "revision": "rev-1",
                "displayName": "Blog",
                "displayField": "title",
                "fields": [{"key": "title", "type": "TEXT"}],
                "permissions": {
                    "insert": "ADMIN",
                    "update": "ADMIN",
                    "remove": "ADMIN",
                    "read": "ADMIN",
                },
            }
        }
        changed = {
            "collection": {
                "id": "blog",
                "revision": "rev-2",
                "displayName": "Changed Blog",
                "displayField": "title",
                "fields": [{"key": "title", "type": "TEXT"}],
                "permissions": {
                    "insert": "ADMIN",
                    "update": "ADMIN",
                    "remove": "ADMIN",
                    "read": "ADMIN",
                },
            }
        }
        args = SimpleNamespace(data_collection_id="blog")

        mock_client.return_value.request.return_value = _DummyResponse(before)
        dry_run_buf = io.StringIO()
        with redirect_stdout(dry_run_buf):
            dry_run_rc = data_collections.cmd_data_collections_delete(args, self._ctx())
        dry_payload = json.loads(dry_run_buf.getvalue())

        self.assertEqual(dry_run_rc, 0)
        self.assertTrue(dry_payload["dry_run"])

        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            plan_path.write_text(json.dumps(dry_payload["plan"]), encoding="utf-8")

            mock_client.return_value.request.side_effect = [_DummyResponse(changed)]
            apply_ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)
            apply_ctx["plan_in"] = str(plan_path)
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = data_collections.cmd_data_collections_delete(args, apply_ctx)
            apply_payload = json.loads(apply_buf.getvalue())

            self.assertEqual(apply_rc, 0)
            self.assertTrue(apply_payload["refused"])
            self.assertIn("changed since plan was created", apply_payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_delete_apply_refuses_without_ack_irreversible(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "collection": {
                    "id": "blog",
                    "revision": "rev-1",
                    "displayName": "Blog",
                    "displayField": "title",
                    "fields": [{"key": "title", "type": "TEXT"}],
                    "permissions": {
                        "insert": "ADMIN",
                        "update": "ADMIN",
                        "remove": "ADMIN",
                        "read": "ADMIN",
                    },
                }
            }
        )
        args = SimpleNamespace(data_collection_id="blog")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=False)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("ack-irreversible", payload["reasons"][0].lower())
        self.assertEqual(len(mock_client.return_value.request.call_args_list), 1)

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_patch_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "collection": {
                    "id": "blog",
                    "revision": "rev-1",
                    "displayName": "Blog",
                    "displayField": "title",
                    "permissions": {
                        "insert": "ADMIN",
                        "update": "ADMIN",
                        "remove": "ADMIN",
                        "read": "ADMIN",
                    },
                }
            }
        )
        args = SimpleNamespace(
            data_collection_id="blog",
            display_name="Updated",
            display_field=None,
            permission_insert=None,
            permission_update=None,
            permission_remove=None,
            permission_read=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_patch(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "data-collections.patch")
        self.assertTrue(payload["dry_run"])
        request = payload["plan"]["request"]
        self.assertEqual(request["method"], "PATCH")
        self.assertEqual(request["path"], "/wix-data/v2/collections/blog")
        body = request["body"]["dataCollection"]
        self.assertEqual(body["id"], "blog")
        self.assertEqual(body["displayName"], "Updated")
        self.assertNotIn("fields", body)
        self.assertNotIn("plugins", body)
        self.assertNotIn("revision", body)

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_patch_refuses_no_requested_fields(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "collection": {
                    "id": "blog",
                    "revision": "rev-1",
                    "displayName": "Blog",
                    "displayField": "title",
                    "permissions": {
                        "insert": "ADMIN",
                        "update": "ADMIN",
                        "remove": "ADMIN",
                        "read": "ADMIN",
                    },
                }
            }
        )
        args = SimpleNamespace(
            data_collection_id="blog",
            display_name=None,
            display_field=None,
            permission_insert=None,
            permission_update=None,
            permission_remove=None,
            permission_read=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_patch(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("no supported patch fields requested", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_patch_refuses_noop_requested_fields(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "collection": {
                    "id": "blog",
                    "revision": "rev-1",
                    "displayName": "Blog",
                    "displayField": "title",
                    "permissions": {
                        "insert": "ADMIN",
                        "update": "ADMIN",
                        "remove": "ADMIN",
                        "read": "ADMIN",
                    },
                }
            }
        )
        args = SimpleNamespace(
            data_collection_id="blog",
            display_name="Blog",
            display_field=None,
            permission_insert=None,
            permission_update=None,
            permission_remove=None,
            permission_read=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_patch(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("no material changes", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_patch_apply_uses_patch_and_verifies(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse(
                {
                    "collection": {
                        "id": "blog",
                        "revision": "rev-1",
                        "displayName": "Blog",
                        "displayField": "title",
                        "permissions": {
                            "insert": "ADMIN",
                            "update": "ADMIN",
                            "remove": "ADMIN",
                            "read": "ADMIN",
                        },
                    }
                }
            ),
            _DummyResponse(
                {
                    "collection": {
                        "id": "blog",
                        "revision": "rev-2",
                        "displayName": "Updated",
                        "displayField": "title",
                        "permissions": {
                            "insert": "ADMIN",
                            "update": "ADMIN",
                            "remove": "ADMIN",
                            "read": "ADMIN",
                        },
                    }
                }
            ),
            _DummyResponse(
                {
                    "collection": {
                        "id": "blog",
                        "revision": "rev-2",
                        "displayName": "Updated",
                        "displayField": "title",
                        "permissions": {
                            "insert": "ADMIN",
                            "update": "ADMIN",
                            "remove": "ADMIN",
                            "read": "ADMIN",
                        },
                    }
                }
            ),
        ]
        args = SimpleNamespace(
            data_collection_id="blog",
            display_name="Updated",
            display_field=None,
            permission_insert=None,
            permission_update=None,
            permission_remove=None,
            permission_read=None,
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_patch(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["method"], "data-collections.patch")
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        calls = mock_client.return_value.request.call_args_list
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[1].kwargs["method"], "PATCH")
        self.assertEqual(calls[1].kwargs["url"], "https://www.wixapis.com/wix-data/v2/collections/blog")
        self.assertEqual(calls[1].kwargs["json_body"]["dataCollection"]["displayName"], "Updated")
        self.assertEqual(calls[2].kwargs["method"], "GET")

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_patch_apply_refuses_drifted_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        before = {
            "collection": {
                "id": "blog",
                "revision": "rev-1",
                "displayName": "Old",
                "displayField": "title",
                "permissions": {
                    "insert": "ADMIN",
                    "update": "ADMIN",
                    "remove": "ADMIN",
                    "read": "ADMIN",
                },
            }
        }
        changed = {
            "collection": {
                "id": "blog",
                "revision": "rev-2",
                "displayName": "Changed",
                "displayField": "title",
                "permissions": {
                    "insert": "ADMIN",
                    "update": "ADMIN",
                    "remove": "ADMIN",
                    "read": "ADMIN",
                },
            }
        }
        args = SimpleNamespace(
            data_collection_id="blog",
            display_name="Updated",
            display_field=None,
            permission_insert=None,
            permission_update=None,
            permission_remove=None,
            permission_read=None,
        )

        mock_client.return_value.request.return_value = _DummyResponse(before)
        dry_run_buf = io.StringIO()
        with redirect_stdout(dry_run_buf):
            dry_run_rc = data_collections.cmd_data_collections_patch(args, self._ctx())
        dry_payload = json.loads(dry_run_buf.getvalue())

        self.assertEqual(dry_run_rc, 0)
        self.assertTrue(dry_payload["dry_run"])

        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            plan_path.write_text(json.dumps(dry_payload["plan"]), encoding="utf-8")

            mock_client.return_value.request.side_effect = [_DummyResponse(changed)]
            apply_ctx = self._ctx(apply=True, yes=True)
            apply_ctx["plan_in"] = str(plan_path)
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = data_collections.cmd_data_collections_patch(args, apply_ctx)
            apply_payload = json.loads(apply_buf.getvalue())

            self.assertEqual(apply_rc, 0)
            self.assertTrue(apply_payload["refused"])
            self.assertIn("changed since plan was created", apply_payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_patch_merges_permission_override(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "collection": {
                    "id": "blog",
                    "revision": "rev-1",
                    "displayName": "Blog",
                    "displayField": "title",
                    "permissions": {
                        "insert": "ADMIN",
                        "update": "SITE_MEMBER_AUTHOR",
                        "remove": "ADMIN",
                        "read": "ANYONE",
                    },
                }
            }
        )
        args = SimpleNamespace(
            data_collection_id="blog",
            display_name=None,
            display_field=None,
            permission_insert=None,
            permission_update="ANYONE",
            permission_remove=None,
            permission_read=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_patch(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        body = payload["plan"]["request"]["body"]["dataCollection"]
        self.assertIn("permissions", body)
        self.assertEqual(
            body["permissions"],
            {
                "insert": "ADMIN",
                "update": "ANYONE",
                "remove": "ADMIN",
                "read": "ANYONE",
            },
        )

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_patch_refuses_missing_collection(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            RuntimeError("HTTP 404 for https://www.wixapis.com/wix-data/v2/collections/blog")
        ]
        args = SimpleNamespace(
            data_collection_id="blog",
            display_name="Updated",
            display_field=None,
            permission_insert=None,
            permission_update=None,
            permission_remove=None,
            permission_read=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_patch(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("does not exist", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_update_plan_refuses_drift(self, mock_client: unittest.mock.MagicMock) -> None:
        before = {
            "collection": {
                "id": "blog",
                "revision": "rev-1",
                "displayName": "Old",
                "displayField": "title",
                "fields": [{"key": "title", "type": "TEXT"}],
                "permissions": {
                    "insert": "ADMIN",
                    "update": "ADMIN",
                    "remove": "ADMIN",
                    "read": "ADMIN",
                },
            }
        }
        changed = {
            "collection": {
                "id": "blog",
                "revision": "rev-2",
                "displayName": "Changed",
                "displayField": "title",
                "fields": [{"key": "title", "type": "TEXT"}],
                "permissions": {
                    "insert": "ADMIN",
                    "update": "ADMIN",
                    "remove": "ADMIN",
                    "read": "ADMIN",
                },
            }
        }
        args = SimpleNamespace(
            data_collection_id="blog",
            display_name="Plan Test",
            display_field=None,
            field_json=None,
            permission_insert=None,
            permission_update=None,
            permission_remove=None,
            permission_read=None,
        )

        mock_client.return_value.request.return_value = _DummyResponse(before)
        buf = io.StringIO()
        with redirect_stdout(buf):
            dry_run_rc = data_collections.cmd_data_collections_update(args, self._ctx())
        dry_payload = json.loads(buf.getvalue())

        self.assertEqual(dry_run_rc, 0)
        self.assertNotIn("refused", dry_payload)
        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            plan_path.write_text(json.dumps(dry_payload["plan"]), encoding="utf-8")

            mock_client.return_value.request.side_effect = [_DummyResponse(changed)]
            apply_ctx = self._ctx(apply=True, yes=True)
            apply_ctx["plan_in"] = str(plan_path)
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = data_collections.cmd_data_collections_update(args, apply_ctx)
            apply_payload = json.loads(apply_buf.getvalue())

            self.assertEqual(apply_rc, 0)
            self.assertTrue(apply_payload["refused"])
            self.assertIn("changed since plan was created", apply_payload["reasons"][0])

    def test_cli_parser_recognizes_data_collections_subcommands(self) -> None:
        parser = build_parser()
        list_cmd = parser.parse_args(["data-collections", "list"])
        self.assertEqual(list_cmd.data_collections_cmd, "list")
        self.assertFalse(list_cmd.write_capable)

        get_cmd = parser.parse_args(
            ["data-collections", "get", "--data-collection-id", "posts"]
        )
        self.assertEqual(get_cmd.data_collections_cmd, "get")
        self.assertFalse(get_cmd.write_capable)

        create_cmd = parser.parse_args(
            ["data-collections", "create", "--collection-id", "blog", "--field-json", '{"key":"title","type":"text"}']
        )
        self.assertEqual(create_cmd.data_collections_cmd, "create")
        self.assertTrue(create_cmd.write_capable)

        update_cmd = parser.parse_args(
            ["data-collections", "update", "--data-collection-id", "blog", "--display-name", "Blog"]
        )
        self.assertEqual(update_cmd.data_collections_cmd, "update")
        self.assertTrue(update_cmd.write_capable)

        patch_cmd = parser.parse_args(
            ["data-collections", "patch", "--data-collection-id", "blog", "--display-name", "Blog"]
        )
        self.assertEqual(patch_cmd.data_collections_cmd, "patch")
        self.assertTrue(patch_cmd.write_capable)

        delete_cmd = parser.parse_args(["data-collections", "delete", "--data-collection-id", "blog"])
        self.assertEqual(delete_cmd.data_collections_cmd, "delete")
        self.assertTrue(delete_cmd.write_capable)

        create_field_cmd = parser.parse_args(
            ["data-collections", "create-field", "--data-collection-id", "blog", "--field-json", '{"key":"title","type":"text"}']
        )
        self.assertEqual(create_field_cmd.data_collections_cmd, "create-field")
        self.assertTrue(create_field_cmd.write_capable)

        update_field_cmd = parser.parse_args(
            ["data-collections", "update-field", "--data-collection-id", "blog", "--field-json", '{"key":"title","type":"text"}']
        )
        self.assertEqual(update_field_cmd.data_collections_cmd, "update-field")
        self.assertTrue(update_field_cmd.write_capable)

        patch_field_cmd = parser.parse_args(
            ["data-collections", "patch-field", "--data-collection-id", "blog", "--field-json", '{"key":"title","displayName":"Title"}']
        )
        self.assertEqual(patch_field_cmd.data_collections_cmd, "patch-field")
        self.assertTrue(patch_field_cmd.write_capable)

        delete_field_cmd = parser.parse_args(
            ["data-collections", "delete-field", "--data-collection-id", "blog", "--field-key", "title"]
        )
        self.assertEqual(delete_field_cmd.data_collections_cmd, "delete-field")
        self.assertTrue(delete_field_cmd.write_capable)

        add_plugin_cmd = parser.parse_args(
            ["data-collections", "add-plugin", "--data-collection-id", "blog", "--plugin-json", '{"type":"hook"}']
        )
        self.assertEqual(add_plugin_cmd.data_collections_cmd, "add-plugin")
        self.assertTrue(add_plugin_cmd.write_capable)

        delete_plugin_cmd = parser.parse_args(
            ["data-collections", "delete-plugin", "--data-collection-id", "blog", "--plugin-type", "hook"]
        )
        self.assertEqual(delete_plugin_cmd.data_collections_cmd, "delete-plugin")
        self.assertTrue(delete_plugin_cmd.write_capable)

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_create_field_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "collection": {
                    "id": "blog",
                    "revision": "rev-1",
                    "fields": [],
                }
            }
        )
        args = SimpleNamespace(data_collection_id="blog", field_json='{"key":"title","type":"text"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_create_field(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "data-collections.create-field")
        request = payload["plan"]["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/wix-data/v2/collections/create-field")
        self.assertEqual(request["body"]["dataCollectionId"], "blog")
        self.assertEqual(request["body"]["field"], {"key": "title", "type": "TEXT"})

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_update_field_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "collection": {
                    "id": "blog",
                    "revision": "rev-1",
                    "fields": [{"key": "title", "type": "TEXT"}],
                }
            }
        )
        args = SimpleNamespace(
            data_collection_id="blog",
            field_json='{"key":"title","type":"rich_text","description":"updated"}',
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_update_field(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "data-collections.update-field")
        request = payload["plan"]["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/wix-data/v2/collections/update-field")
        self.assertEqual(request["body"]["field"], {"key": "title", "type": "RICH_TEXT", "description": "updated"})

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_add_plugin_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "collection": {
                    "id": "blog",
                    "revision": "rev-1",
                    "plugins": [],
                            "fields": [{"key": "title", "type": "TEXT"}],
                    "fields": [{"key": "title", "type": "TEXT"}],
                }
            }
        )
        args = SimpleNamespace(data_collection_id="blog", plugin_json='{"type":"hook","config":{"enabled":true}}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_add_plugin(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "data-collections.add-plugin")
        request = payload["plan"]["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/wix-data/v2/collections/add-plugin")
        self.assertEqual(
            request["body"],
            {
                "dataCollectionId": "blog",
                "plugin": {"type": "hook", "config": {"enabled": True}},
            },
        )

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_delete_plugin_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "collection": {
                    "id": "blog",
                    "revision": "rev-1",
                    "plugins": [{"type": "hook"}],
                    "fields": [{"key": "title", "type": "TEXT"}],
                }
            }
        )
        args = SimpleNamespace(data_collection_id="blog", plugin_type="hook")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_delete_plugin(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "data-collections.delete-plugin")
        request = payload["plan"]["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/wix-data/v2/collections/delete-plugin")
        self.assertEqual(
            request["body"],
            {"dataCollectionId": "blog", "pluginType": "hook"},
        )

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_create_field_apply_refuses_without_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"collection": {"id": "blog", "revision": "rev-1", "fields": []}}
        )
        args = SimpleNamespace(data_collection_id="blog", field_json='{"key":"title","type":"text"}')
        ctx = self._ctx(apply=True, yes=True, enforce_reviewed_plan=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_create_field(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-in", payload["reasons"][0])
        self.assertEqual(len(mock_client.return_value.request.call_args_list), 0)

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_delete_field_requires_ack_irreversible(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(data_collection_id="blog", field_key="title")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=False, enforce_reviewed_plan=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_delete_field(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("ack-irreversible", payload["reasons"][0].lower())
        self.assertEqual(len(mock_client.return_value.request.call_args_list), 0)

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_create_field_apply_uses_api_and_verifies(self, mock_client: unittest.mock.MagicMock) -> None:
        dry_ctx = self._ctx(enforce_reviewed_plan=True)
        dry_run_ctx = self._ctx(enforce_reviewed_plan=True)
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "collection": {
                    "id": "blog",
                    "revision": "rev-1",
                    "fields": [],
                }
            }
        )

        dry_run_buf = io.StringIO()
        with redirect_stdout(dry_run_buf):
            dry_rc = data_collections.cmd_data_collections_create_field(
                SimpleNamespace(data_collection_id="blog", field_json='{"key":"title","type":"text"}'),
                dry_ctx,
            )
        dry_payload = json.loads(dry_run_buf.getvalue())

        self.assertEqual(dry_rc, 0)
        self.assertTrue(dry_payload["dry_run"])

        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            plan_path.write_text(json.dumps(dry_payload["plan"]), encoding="utf-8")

            mock_client.return_value.request.side_effect = [
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-1",
                            "fields": [],
                        }
                    }
                ),
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-2",
                            "fields": [{"key": "title", "type": "TEXT"}],
                        }
                    }
                ),
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-2",
                            "fields": [{"key": "title", "type": "TEXT"}],
                        }
                    }
                ),
            ]
            apply_ctx = self._ctx(
                apply=True,
                yes=True,
                plan_in=str(plan_path),
                enforce_reviewed_plan=True,
            )
            mock_client.return_value.request.reset_mock()
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = data_collections.cmd_data_collections_create_field(
                    SimpleNamespace(data_collection_id="blog", field_json='{"key":"title","type":"text"}'),
                    apply_ctx,
                )
            apply_payload = json.loads(apply_buf.getvalue())

            self.assertEqual(apply_rc, 0)
            self.assertFalse(apply_payload["dry_run"])
            self.assertEqual(apply_payload["method"], "data-collections.create-field")
            calls = mock_client.return_value.request.call_args_list
            self.assertEqual(len(calls), 3)
            self.assertEqual(calls[1].kwargs["method"], "POST")
            self.assertEqual(calls[1].kwargs["url"], "https://www.wixapis.com/wix-data/v2/collections/create-field")
            self.assertEqual(
                calls[1].kwargs["json_body"],
                {"dataCollectionId": "blog", "field": {"key": "title", "type": "TEXT"}},
            )

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_patch_field_apply_uses_patch_path(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(
            data_collection_id="blog",
            field_json='{"key":"title","description":"new"}',
        )
        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            dry_ctx = self._ctx(plan_in=None, enforce_reviewed_plan=False)
            mock_client.return_value.request.side_effect = [
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-1",
                            "fields": [{"key": "title", "type": "TEXT", "description": "old"}],
                        }
                    }
                ),
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-2",
                            "fields": [{"key": "title", "type": "TEXT", "description": "new"}],
                        }
                    }
                ),
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-2",
                            "fields": [{"key": "title", "type": "TEXT", "description": "new"}],
                        }
                    }
                ),
            ]
            dry_run_buf2 = io.StringIO()
            with redirect_stdout(dry_run_buf2):
                plan_rc = data_collections.cmd_data_collections_patch_field(
                    args,
                    dry_ctx,
                )
            plan_payload = json.loads(dry_run_buf2.getvalue())
            self.assertEqual(plan_rc, 0)
            plan_path.write_text(json.dumps(plan_payload["plan"]), encoding="utf-8")

            apply_ctx = self._ctx(
                apply=True,
                yes=True,
                plan_in=str(plan_path),
                enforce_reviewed_plan=True,
            )
            mock_client.return_value.request.reset_mock()
            mock_client.return_value.request.side_effect = [
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-1",
                            "fields": [{"key": "title", "type": "TEXT", "description": "old"}],
                        }
                    }
                ),
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-2",
                            "fields": [{"key": "title", "type": "TEXT", "description": "new"}],
                        }
                    }
                ),
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-2",
                            "fields": [{"key": "title", "type": "TEXT", "description": "new"}],
                        }
                    }
                ),
            ]
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = data_collections.cmd_data_collections_patch_field(args, apply_ctx)
            apply_payload = json.loads(apply_buf.getvalue())

            self.assertEqual(apply_rc, 0)
            self.assertFalse(apply_payload["dry_run"])
            self.assertEqual(apply_payload["method"], "data-collections.patch-field")
            calls = mock_client.return_value.request.call_args_list
            self.assertEqual(len(calls), 3)
            self.assertEqual(calls[1].kwargs["method"], "PATCH")
            self.assertEqual(calls[1].kwargs["url"], "https://www.wixapis.com/wix-data/v2/collections/blog/patch-field")
            self.assertEqual(calls[1].kwargs["json_body"]["field"]["description"], "new")

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_delete_field_apply_sends_delete_api_and_verifies(self, mock_client: unittest.mock.MagicMock) -> None:
        dry_ctx = self._ctx(enforce_reviewed_plan=True)
        args = SimpleNamespace(data_collection_id="blog", field_key="title")
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "collection": {
                    "id": "blog",
                    "revision": "rev-1",
                    "fields": [{"key": "title", "type": "TEXT"}],
                }
            }
        )
        dry_run_buf = io.StringIO()
        with redirect_stdout(dry_run_buf):
            rc = data_collections.cmd_data_collections_delete_field(
                args,
                self._ctx(apply=False, enforce_reviewed_plan=True),
            )
        self.assertEqual(rc, 0)
        dry_payload = json.loads(dry_run_buf.getvalue())
        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            plan_path.write_text(json.dumps(dry_payload["plan"]), encoding="utf-8")

            mock_client.return_value.request.side_effect = [
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-1",
                            "fields": [{"key": "title", "type": "TEXT"}],
                        }
                    }
                ),
                _DummyResponse({"ok": True}),
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-2",
                            "fields": [],
                        }
                    }
                ),
            ]
            apply_ctx = self._ctx(
                apply=True,
                yes=True,
                ack_irreversible=True,
                plan_in=str(plan_path),
                enforce_reviewed_plan=True,
            )
            mock_client.return_value.request.reset_mock()
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = data_collections.cmd_data_collections_delete_field(args, apply_ctx)
            apply_payload = json.loads(apply_buf.getvalue())
            calls = mock_client.return_value.request.call_args_list
            self.assertEqual(apply_rc, 0)
            self.assertFalse(apply_payload["dry_run"])
            self.assertEqual(apply_payload["method"], "data-collections.delete-field")
            self.assertEqual(calls[1].kwargs["method"], "POST")
            self.assertEqual(calls[1].kwargs["url"], "https://www.wixapis.com/wix-data/v2/collections/delete-field")
            self.assertEqual(calls[1].kwargs["json_body"], {"dataCollectionId": "blog", "fieldKey": "title"})

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_add_plugin_apply_sends_plugin_api(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(data_collection_id="blog", plugin_json='{"type":"hook","config":{"enabled":true}}')
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "collection": {
                    "id": "blog",
                    "revision": "rev-1",
                    "plugins": [],
                    "fields": [{"key": "title", "type": "TEXT"}],
                }
            }
        )
        dry_run_buf = io.StringIO()
        with redirect_stdout(dry_run_buf):
            rc = data_collections.cmd_data_collections_add_plugin(
                args,
                self._ctx(enforce_reviewed_plan=True),
            )
        self.assertEqual(rc, 0)
        plan_payload = json.loads(dry_run_buf.getvalue())

        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            plan_path.write_text(json.dumps(plan_payload["plan"]), encoding="utf-8")
            mock_client.return_value.request.side_effect = [
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-1",
                            "plugins": [],
                            "fields": [{"key": "title", "type": "TEXT"}],
                        }
                    }
                ),
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-2",
                            "plugins": [{"type": "hook"}],
                            "fields": [{"key": "title", "type": "TEXT"}],
                        }
                    }
                ),
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-2",
                            "plugins": [{"type": "hook"}],
                            "fields": [{"key": "title", "type": "TEXT"}],
                        }
                    }
                ),
            ]
            apply_ctx = self._ctx(
                apply=True,
                yes=True,
                plan_in=str(plan_path),
                enforce_reviewed_plan=True,
            )
            mock_client.return_value.request.reset_mock()
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = data_collections.cmd_data_collections_add_plugin(args, apply_ctx)
            apply_payload = json.loads(apply_buf.getvalue())
            calls = mock_client.return_value.request.call_args_list

            self.assertEqual(apply_rc, 0)
            self.assertEqual(apply_payload["method"], "data-collections.add-plugin")
            self.assertFalse(apply_payload["dry_run"])
            self.assertEqual(calls[1].kwargs["method"], "POST")
            self.assertEqual(calls[1].kwargs["url"], "https://www.wixapis.com/wix-data/v2/collections/add-plugin")
            self.assertEqual(
                calls[1].kwargs["json_body"],
                {"dataCollectionId": "blog", "plugin": {"type": "hook", "config": {"enabled": True}}},
            )

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_delete_plugin_apply_sends_delete_plugin_api(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(data_collection_id="blog", plugin_type="hook")
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "collection": {
                    "id": "blog",
                    "revision": "rev-1",
                    "plugins": [{"type": "hook"}],
                    "fields": [{"key": "title", "type": "TEXT"}],
                }
            }
        )
        dry_run_buf = io.StringIO()
        with redirect_stdout(dry_run_buf):
            rc = data_collections.cmd_data_collections_delete_plugin(
                args,
                self._ctx(enforce_reviewed_plan=True),
            )
        self.assertEqual(rc, 0)
        plan_payload = json.loads(dry_run_buf.getvalue())

        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            plan_path.write_text(json.dumps(plan_payload["plan"]), encoding="utf-8")
            mock_client.return_value.request.side_effect = [
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-1",
                            "plugins": [{"type": "hook"}],
                            "fields": [{"key": "title", "type": "TEXT"}],
                        }
                    }
                ),
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-2",
                            "plugins": [],
                            "fields": [{"key": "title", "type": "TEXT"}],
                        }
                    }
                ),
                _DummyResponse(
                    {
                        "collection": {
                            "id": "blog",
                            "revision": "rev-2",
                            "plugins": [],
                            "fields": [{"key": "title", "type": "TEXT"}],
                        }
                    }
                ),
            ]
            apply_ctx = self._ctx(
                apply=True,
                yes=True,
                plan_in=str(plan_path),
                enforce_reviewed_plan=True,
            )
            mock_client.return_value.request.reset_mock()
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = data_collections.cmd_data_collections_delete_plugin(args, apply_ctx)
            apply_payload = json.loads(apply_buf.getvalue())
            calls = mock_client.return_value.request.call_args_list

            self.assertEqual(apply_rc, 0)
            self.assertEqual(apply_payload["method"], "data-collections.delete-plugin")
            self.assertFalse(apply_payload["dry_run"])
            self.assertEqual(calls[1].kwargs["method"], "POST")
            self.assertEqual(calls[1].kwargs["url"], "https://www.wixapis.com/wix-data/v2/collections/delete-plugin")
            self.assertEqual(calls[1].kwargs["json_body"], {"dataCollectionId": "blog", "pluginType": "hook"})

    @patch("wix_safe_agent_cli.commands.data_collections.HttpClient")
    def test_data_collections_list_rejects_invalid_fields_json_shape(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        args = SimpleNamespace(
            fields_json='{"not":"an-array"}',
            limit=None,
            offset=None,
            sort_field_name=None,
            sort_order=None,
            consistent_read=False,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_list(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_data_collections_create_rejects_invalid_permission_role(self) -> None:
        args = SimpleNamespace(
            collection_id="blog",
            display_name=None,
            display_field=None,
            field_json=['{"key":"title","type":"text"}'],
            permission_insert="not-a-role",
            permission_update="ADMIN",
            permission_remove="ADMIN",
            permission_read="ADMIN",
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_collections.cmd_data_collections_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

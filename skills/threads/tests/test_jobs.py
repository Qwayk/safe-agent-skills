from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from threads_api_tool.commands import demo as demo_cmd
from threads_api_tool.commands import jobs as jobs_cmd
from threads_api_tool.commands import posts as posts_cmd
from threads_api_tool.commands import replies as replies_cmd
from threads_api_tool.errors import ValidationError
from threads_api_tool.output import Output
from threads_api_tool.errors import SafetyError


class _NoopAudit:
    def write(self, *_args, **_kwargs) -> None:
        return None


class TestWriteSafetyAndPlanApply(unittest.TestCase):
    def _ctx(self, env_file: Path, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="http://example.invalid",
            api_version="v1.0",
            token="dummy-token",
            app_id="app-id",
            app_secret="app-secret",
            redirect_uri="https://callback.local",
            default_user_id="threads-default",
            timeout_s=30.0,
        )
        ctx = {
            "cfg": cfg,
            "out": Output(mode="json"),
            "audit": _NoopAudit(),
            "tool": "threads-api-tool",
            "tool_version": "0.1.0",
            "command_str": "threads-api-tool posts create-text",
            "env_file": str(env_file),
            "timeout_s": 30,
            "verbose": False,
            "apply": False,
            "yes": False,
            "plan_out": None,
            "plan_in": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "run_id": None,
            "artifacts_dir": None,
            "runs_index_path": None,
        }
        ctx.update(overrides)
        return ctx

    def _create_text_args(self, **overrides) -> SimpleNamespace:
        data = SimpleNamespace(
            threads_user_id="threads-user-1",
            text="hello",
            topic_tag=None,
            reply_to_id="",
            reply_control=None,
            enable_reply_approvals=False,
            quote_post_id=None,
            link_attachment=None,
            gif_id=None,
            gif_provider=None,
            location_id=None,
            spoiler_media=False,
            text_spoiler_ranges=None,
            poll_options_csv=None,
            poll_options=None,
            children=None,
            image_url=None,
            video_url=None,
            is_carousel_item=False,
        )
        for key, value in overrides.items():
            setattr(data, key, value)
        return data

    def test_posts_delete_requires_apply_yes_ack_irreversible(self) -> None:
        fake = Mock()
        args = SimpleNamespace(threads_media_id="media-1")
        with patch("threads_api_tool.commands.posts._client", return_value=fake):
            with self.assertRaises(SafetyError):
                posts_cmd.cmd_posts_delete(args, self._ctx(Path("/tmp"), apply=True))

    def test_posts_create_text_dry_run_and_apply_from_plan(self) -> None:
        fake = Mock()
        fake.create_post.return_value = {"id": "media-123"}

        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("", encoding="utf-8")
            plan_path = Path(d) / "plan.json"
            args = self._create_text_args()

            with patch("threads_api_tool.commands.posts._client", return_value=fake):
                ctx = self._ctx(env, plan_out=str(plan_path), apply=False)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = posts_cmd.cmd_posts_create_text(args, ctx)
                    self.assertEqual(rc, 0)
                    self.assertTrue(plan_path.exists())
                    payload = json.loads(buf.getvalue())
                    self.assertTrue(payload["ok"])
                    self.assertTrue(payload["dry_run"])
                    self.assertIn("plan", payload)
                    self.assertEqual(fake.create_post.call_count, 0)

                    payload_plan = payload["plan"]
                    self.assertEqual(payload_plan["proposed_changes"][0]["action"], "create_post")

                    receipt_path = Path(d) / "receipt.json"
                    ctx_apply = self._ctx(
                        env,
                        apply=True,
                        yes=True,
                        plan_in=str(plan_path),
                        plan_out=None,
                        receipt_out=str(receipt_path),
                    )
                    buf2 = io.StringIO()
                    with redirect_stdout(buf2):
                        rc2 = posts_cmd.cmd_posts_create_text(args, ctx_apply)
                        self.assertEqual(rc2, 0)
                        payload2 = json.loads(buf2.getvalue())
                        self.assertFalse(payload2["dry_run"])
                        self.assertTrue(payload2["ok"])
                        self.assertTrue(payload2["refused"])
                        self.assertEqual(payload2["plan"]["before_state"]["status"], "no_snapshot_available")
                        self.assertNotIn("receipt", payload2)
                        self.assertFalse(receipt_path.exists())
                        self.assertEqual(fake.create_post.call_count, 0)

    def test_posts_create_text_dry_run_includes_no_recovery_contract(self) -> None:
        fake = Mock()
        fake.create_post.return_value = {"id": "media-123"}
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("", encoding="utf-8")
            args = self._create_text_args()
            with patch("threads_api_tool.commands.posts._client", return_value=fake):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = posts_cmd.cmd_posts_create_text(args, self._ctx(env))
                    self.assertEqual(rc, 0)
                    payload = json.loads(buf.getvalue())
                    rollback = payload["plan"]["rollback"]
                    self.assertEqual(rollback["supported"], False)
                    self.assertEqual(rollback["mode"], "irreversible_and_clearly_labeled")
                    self.assertIn("No built-in rollback", rollback["notes"])
                    self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")

    def test_posts_create_text_apply_receipt_includes_no_recovery_contract(self) -> None:
        fake = Mock()
        fake.create_post.return_value = {"id": "media-123"}
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("", encoding="utf-8")
            plan_path = Path(d) / "plan.json"
            args = self._create_text_args()
            with patch("threads_api_tool.commands.posts._client", return_value=fake):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    self.assertEqual(
                        0,
                        posts_cmd.cmd_posts_create_text(args, self._ctx(env, plan_out=str(plan_path), apply=False)),
                    )
                with open(plan_path, "r", encoding="utf-8") as fp:
                    plan_payload = json.load(fp)
                self.assertEqual(plan_payload["command_id"], "posts.create-text")

                receipt_path = Path(d) / "receipt.json"
                apply_buf = io.StringIO()
                with redirect_stdout(apply_buf):
                    self.assertEqual(
                        0,
                        posts_cmd.cmd_posts_create_text(
                            args,
                            self._ctx(env, apply=True, plan_in=str(plan_path), receipt_out=str(receipt_path)),
                        ),
                    )
                    payload = json.loads(apply_buf.getvalue())
                    self.assertTrue(payload["refused"])
                    self.assertNotIn("receipt", payload)
                    self.assertFalse(receipt_path.exists())
                    self.assertEqual(fake.create_post.call_count, 0)
                    rollback = payload["plan"]["rollback"]
                    self.assertEqual(rollback["supported"], False)
                    self.assertEqual(rollback["mode"], "irreversible_and_clearly_labeled")
                    self.assertIn("No built-in rollback", rollback["notes"])

    def test_demo_write_apply_receipt_includes_no_recovery_contract(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("", encoding="utf-8")
            args = SimpleNamespace(selector="demo-target")

            plan_buf = io.StringIO()
            with redirect_stdout(plan_buf):
                self.assertEqual(0, demo_cmd.cmd_demo_write(args, self._ctx(env)))
            plan_payload = json.loads(plan_buf.getvalue())
            rollback = plan_payload["plan"]["rollback"]
            self.assertEqual(rollback["supported"], False)
            self.assertEqual(rollback["mode"], "irreversible_and_clearly_labeled")
            self.assertIn("no built-in rollback", rollback["notes"].lower())

            receipt_path = Path(d) / "demo-receipt.json"
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                self.assertEqual(0, demo_cmd.cmd_demo_write(args, self._ctx(env, apply=True, receipt_out=str(receipt_path))))
            apply_payload = json.loads(apply_buf.getvalue())
            self.assertTrue(apply_payload["refused"])
            self.assertNotIn("receipt", apply_payload)
            self.assertFalse(receipt_path.exists())
            rollback = apply_payload["plan"]["rollback"]
            self.assertEqual(rollback["supported"], False)
            self.assertEqual(rollback["mode"], "irreversible_and_clearly_labeled")
            self.assertIn("no built-in rollback", rollback["notes"].lower())

    def test_jobs_apply_receipt_includes_no_recovery_contract(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("", encoding="utf-8")
            job_path = Path(d) / "jobs.csv"
            with job_path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["action"])
                writer.writerow(["write.ping"])

            args = SimpleNamespace(file=str(job_path), limit=None)
            plan_buf = io.StringIO()
            with redirect_stdout(plan_buf):
                self.assertEqual(0, jobs_cmd.cmd_jobs_run(args, self._ctx(env)))
            plan_payload = json.loads(plan_buf.getvalue())
            rollback = plan_payload["plan"]["rollback"]
            self.assertEqual(rollback["supported"], False)
            self.assertEqual(rollback["mode"], "irreversible_and_clearly_labeled")
            self.assertIn("no built-in rollback", rollback["notes"].lower())

            receipt_path = Path(d) / "jobs-receipt.json"
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                self.assertEqual(0, jobs_cmd.cmd_jobs_run(args, self._ctx(env, apply=True, yes=True, receipt_out=str(receipt_path))))
            apply_payload = json.loads(apply_buf.getvalue())
            self.assertTrue(apply_payload["refused"])
            self.assertNotIn("receipt", apply_payload)
            self.assertFalse(receipt_path.exists())
            rollback = apply_payload["plan"]["rollback"]
            self.assertEqual(rollback["supported"], False)
            self.assertEqual(rollback["mode"], "irreversible_and_clearly_labeled")
            self.assertIn("no built-in rollback", rollback["notes"].lower())

    def test_posts_create_payload_uses_official_field_names(self) -> None:
        args = SimpleNamespace(
            text="hello",
            image_url=None,
            video_url=None,
            topic_tag="topic",
            reply_to_id=None,
            reply_control="everyone",
            enable_reply_approvals=True,
            quote_post_id=None,
            link_attachment=None,
            gif_id="gif-id-1",
            gif_provider="provider-1",
            location_id="loc-1",
            spoiler_media=True,
            text_spoiler_ranges=["0:2", "2:7"],
            poll_options=["a", "b", "c"],
            poll_options_csv=None,
            children=None,
            is_carousel_item=False,
        )
        payload = posts_cmd._build_create_payload(args, media_type="TEXT")
        self.assertEqual(payload["media_type"], "TEXT")
        self.assertIn("is_spoiler_media", payload)
        self.assertIn("enable_reply_approvals", payload)
        self.assertIn("text_entities", payload)
        self.assertIn("poll_attachment", payload)
        self.assertIn("gif_attachment", payload)
        self.assertNotIn("spoiler_media", payload)
        self.assertEqual(payload["is_spoiler_media"], True)
        self.assertEqual(payload["poll_attachment"], {"option_a": "a", "option_b": "b", "option_c": "c"})
        self.assertEqual(payload["gif_attachment"], {"gif_id": "gif-id-1", "provider": "provider-1"})
        self.assertEqual(
            payload["text_entities"],
            [
                {"entity_type": "SPOILER", "offset": 0, "length": 2},
                {"entity_type": "SPOILER", "offset": 2, "length": 7},
            ],
        )

    def test_posts_create_payload_rejects_mixed_gif_args(self) -> None:
        with self.assertRaises(ValidationError):
            posts_cmd._build_create_payload(
                SimpleNamespace(
                    text=None,
                    image_url=None,
                    video_url=None,
                    topic_tag=None,
                    reply_to_id=None,
                    reply_control=None,
                    enable_reply_approvals=False,
                    quote_post_id=None,
                    link_attachment=None,
                    gif_id="gif-id-1",
                    gif_provider=None,
                    location_id=None,
                    spoiler_media=False,
                    text_spoiler_ranges=None,
                    poll_options_csv=None,
                    poll_options=None,
                    children=None,
                    is_carousel_item=False,
                ),
                media_type="TEXT",
            )

    def test_posts_create_payload_sets_image_media_type(self) -> None:
        payload = posts_cmd._build_create_payload(
            SimpleNamespace(
                text="caption",
                image_url="https://example.com/image.jpg",
                video_url=None,
                topic_tag=None,
                reply_to_id=None,
                reply_control=None,
                enable_reply_approvals=False,
                quote_post_id=None,
                link_attachment=None,
                gif_id=None,
                gif_provider=None,
                location_id=None,
                spoiler_media=False,
                text_spoiler_ranges=None,
                poll_options_csv=None,
                poll_options=None,
                children=None,
                is_carousel_item=False,
            ),
            media_type="IMAGE",
        )
        self.assertEqual(payload["media_type"], "IMAGE")
        self.assertEqual(payload["image_url"], "https://example.com/image.jpg")

    def test_replies_hide_accepts_boolean_arg(self) -> None:
        fake = Mock()
        fake.manage_reply.return_value = {"ok": True}
        args = SimpleNamespace(threads_reply_id="reply-1", hide="false")
        with patch("threads_api_tool.commands.replies._client", return_value=fake):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = replies_cmd.cmd_replies_hide(
                    args,
                    self._ctx(Path("/tmp"), apply=True, yes=True),
                )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["plan"]["proposed_changes"][0]["hide"], False)
        fake.manage_reply.assert_not_called()

    def test_replies_pending_decide_accepts_boolean_arg(self) -> None:
        fake = Mock()
        fake.manage_pending_reply.return_value = {"ok": True}
        args = SimpleNamespace(threads_reply_id="reply-1", approve="true")
        with patch("threads_api_tool.commands.replies._client", return_value=fake):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = replies_cmd.cmd_replies_pending_decide(
                    args,
                    self._ctx(Path("/tmp"), apply=True, yes=True),
                )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["plan"]["proposed_changes"][0]["approve"], True)
        fake.manage_pending_reply.assert_not_called()

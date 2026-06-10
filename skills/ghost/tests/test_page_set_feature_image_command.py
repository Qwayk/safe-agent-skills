import unittest

from ghost_api_tool.commands.page import cmd_page_set_feature_image
from ghost_api_tool.errors import ValidationError


class _Out:
    def __init__(self) -> None:
        self.items = []

    def print(self, obj):
        self.items.append(obj)


class _Backup:
    def __init__(self) -> None:
        self.calls = []

    def write_before_after(self, **kwargs):
        self.calls.append(kwargs)
        return None


class PageSetFeatureImageCommandTests(unittest.TestCase):
    def test_dry_run_mirrors_post_structure(self) -> None:
        class FakeApi:
            def pages_read_by_slug(self, slug, params=None):
                assert slug == "s"
                return {"pages": [{"id": "pg1", "slug": "s", "status": "draft", "updated_at": "t0"}]}

        class Args:
            slug = "s"
            id = None
            file = "local.jpg"
            upload_name = "upload.jpg"
            alt = None
            caption = None

        out = _Out()
        ctx = {"apply": False, "out": out, "_api": FakeApi()}
        rc = cmd_page_set_feature_image(Args(), ctx)
        self.assertEqual(rc, 0)
        self.assertEqual(len(out.items), 1)
        obj = out.items[0]
        self.assertEqual(obj["apply"], False)
        self.assertEqual(obj["would_upload"]["file"], "local.jpg")
        self.assertEqual(obj["would_upload"]["upload_name"], "upload.jpg")
        self.assertEqual(obj["would_upload"]["purpose"], "image")
        self.assertEqual(obj["would_patch"]["feature_image"], "<uploaded-url>")
        self.assertEqual(obj["would_patch"]["feature_image_alt"], None)
        self.assertEqual(obj["would_patch"]["feature_image_caption"], None)

    def test_apply_uploads_then_patches_and_verifies(self) -> None:
        class FakeApi:
            def __init__(self) -> None:
                self.upload_calls = []
                self.update_calls = []
                self.read_calls = []
                self._read_count = 0

            def upload_image(self, *, file_path, purpose, ref, upload_name):
                self.upload_calls.append(
                    {
                        "file_path": file_path,
                        "purpose": purpose,
                        "ref": ref,
                        "upload_name": upload_name,
                    }
                )
                return {"images": [{"url": "https://cdn.example/feat.jpg"}]}

            def pages_read_by_id(self, page_id, params=None):
                self.read_calls.append({"page_id": page_id, "params": params})
                self._read_count += 1
                if self._read_count == 1:
                    return {"pages": [{"id": "pg1", "slug": "s", "status": "draft", "updated_at": "t0"}]}
                if self._read_count == 2:
                    return {
                        "pages": [
                            {
                                "id": "pg1",
                                "slug": "s",
                                "status": "draft",
                                "updated_at": "t0",
                                "feature_image": "https://cdn.example/feat.jpg",
                                "feature_image_alt": "Alt",
                                "feature_image_caption": "Cap",
                            }
                        ]
                    }
                raise AssertionError(f"unexpected pages_read_by_id call count: {self._read_count}")

            def pages_update(self, page_id, payload, params=None):
                self.update_calls.append({"page_id": page_id, "payload": payload, "params": params})
                return None

        class Args:
            slug = None
            id = "pg1"
            file = "feat.jpg"
            upload_name = "up.jpg"
            alt = "Alt"
            caption = "Cap"

        api = FakeApi()
        out = _Out()
        ctx = {"apply": True, "out": out, "_api": api}
        rc = cmd_page_set_feature_image(Args(), ctx)
        self.assertEqual(rc, 0)

        self.assertEqual(len(api.upload_calls), 1)
        self.assertEqual(api.upload_calls[0]["file_path"], "feat.jpg")
        self.assertEqual(api.upload_calls[0]["purpose"], "image")
        self.assertEqual(api.upload_calls[0]["ref"], "feat.jpg")
        self.assertEqual(api.upload_calls[0]["upload_name"], "up.jpg")

        self.assertGreaterEqual(len(api.read_calls), 2)
        self.assertEqual(len(api.update_calls), 1)
        self.assertEqual(api.update_calls[0]["page_id"], "pg1")
        payload_page = api.update_calls[0]["payload"]["pages"][0]
        self.assertEqual(payload_page["updated_at"], "t0")
        self.assertEqual(payload_page["feature_image"], "https://cdn.example/feat.jpg")
        self.assertEqual(payload_page["feature_image_alt"], "Alt")
        self.assertEqual(payload_page["feature_image_caption"], "Cap")

        self.assertEqual(len(out.items), 1)
        self.assertEqual(out.items[0]["apply"], True)
        self.assertEqual(out.items[0]["page_id"], "pg1")
        self.assertEqual(out.items[0]["feature_image"], "https://cdn.example/feat.jpg")

    def test_dry_run_writes_before_state_snapshot_when_backup_is_present(self) -> None:
        class FakeApi:
            def pages_read_by_id(self, page_id, params=None):
                assert page_id == "pg1"
                return {"pages": [{"id": "pg1", "slug": "s", "status": "draft", "updated_at": "t0"}]}

        class Args:
            slug = None
            id = "pg1"
            file = "local.jpg"
            upload_name = "upload.jpg"
            alt = None
            caption = None

        backup = _Backup()
        out = _Out()
        ctx = {"apply": False, "out": out, "_api": FakeApi(), "backup": backup}
        rc = cmd_page_set_feature_image(Args(), ctx)
        self.assertEqual(rc, 0)
        self.assertEqual(len(backup.calls), 1)
        self.assertEqual(backup.calls[0]["action"], "page.set_feature_image")
        self.assertEqual(backup.calls[0]["before"]["id"], "pg1")
        self.assertEqual(backup.calls[0]["meta"]["upload"]["file"], "local.jpg")

    def test_apply_omits_alt_and_caption_when_not_provided(self) -> None:
        class FakeApi:
            def __init__(self) -> None:
                self.update_payload_pages = []
                self._read_count = 0

            def upload_image(self, *, file_path, purpose, ref, upload_name):
                return {"images": [{"url": "https://cdn.example/feat.jpg"}]}

            def pages_read_by_id(self, page_id, params=None):
                self._read_count += 1
                if self._read_count == 1:
                    return {
                        "pages": [
                            {
                                "id": "pg1",
                                "slug": "s",
                                "status": "draft",
                                "updated_at": "t0",
                                "feature_image_alt": "Existing alt",
                                "feature_image_caption": "Existing cap",
                            }
                        ]
                    }
                if self._read_count == 2:
                    return {
                        "pages": [
                            {
                                "id": "pg1",
                                "slug": "s",
                                "status": "draft",
                                "updated_at": "t0",
                                "feature_image": "https://cdn.example/feat.jpg",
                                "feature_image_alt": "Existing alt",
                                "feature_image_caption": "Existing cap",
                            }
                        ]
                    }
                raise AssertionError(f"unexpected pages_read_by_id call count: {self._read_count}")

            def pages_update(self, page_id, payload, params=None):
                self.update_payload_pages.append(payload["pages"][0])
                return None

        class Args:
            slug = None
            id = "pg1"
            file = "feat.jpg"
            upload_name = None
            alt = None
            caption = None

        api = FakeApi()
        ctx = {"apply": True, "out": _Out(), "_api": api}
        rc = cmd_page_set_feature_image(Args(), ctx)
        self.assertEqual(rc, 0)
        self.assertEqual(len(api.update_payload_pages), 1)
        payload_page = api.update_payload_pages[0]
        self.assertEqual(payload_page["feature_image"], "https://cdn.example/feat.jpg")
        self.assertNotIn("feature_image_alt", payload_page)
        self.assertNotIn("feature_image_caption", payload_page)

    def test_upload_missing_url_raises(self) -> None:
        class FakeApi:
            def upload_image(self, *, file_path, purpose, ref, upload_name):
                return {"images": [{}]}

            def pages_read_by_id(self, page_id, params=None):
                raise AssertionError("resolve_page should not be called when upload is missing a url")

        class Args:
            slug = None
            id = "pg1"
            file = "feat.jpg"
            upload_name = None
            alt = None
            caption = None

        ctx = {"apply": True, "out": _Out(), "_api": FakeApi()}
        with self.assertRaises(RuntimeError):
            cmd_page_set_feature_image(Args(), ctx)

    def test_apply_requires_exactly_one_selector_before_upload(self) -> None:
        class FakeApi:
            def upload_image(self, *, file_path, purpose, ref, upload_name):
                raise AssertionError("upload_image should not be called when selector args are invalid")

        class Args:
            slug = "s"
            id = "pg1"
            file = "feat.jpg"
            upload_name = None
            alt = None
            caption = None

        ctx = {"apply": True, "out": _Out(), "_api": FakeApi()}
        with self.assertRaises(ValidationError):
            cmd_page_set_feature_image(Args(), ctx)

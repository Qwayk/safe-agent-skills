import csv
import tempfile
import unittest
from pathlib import Path

from wordpress_api_tool.commands.migration import cmd_tracking_from_xml


class _Out:
    def __init__(self):
        self.items = []

    def emit(self, obj):
        self.items.append(obj)


class MigrationTrackingFromXmlTests(unittest.TestCase):
    def test_writes_tracking_csv(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:wp="http://wordpress.org/export/1.2/">
  <channel>
    <item>
      <title>Post A</title>
      <dc:creator>author_a</dc:creator>
      <wp:post_type>post</wp:post_type>
      <wp:post_id>10</wp:post_id>
      <wp:post_name>post-a</wp:post_name>
      <wp:status>publish</wp:status>
    </item>
  </channel>
</rss>
"""
        with tempfile.TemporaryDirectory() as td:
            xml_path = Path(td) / "export.xml"
            xml_path.write_text(xml, encoding="utf-8")
            out_path = Path(td) / "tracking.csv"

            class Args:
                xml = [str(xml_path)]
                out = str(out_path)

            ctx = {"out": _Out()}
            rc = cmd_tracking_from_xml(Args(), ctx)
            self.assertEqual(rc, 0)
            self.assertTrue(out_path.exists())

            with out_path.open("r", encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["wp_post_id"], "10")
            self.assertEqual(rows[0]["wp_slug"], "post-a")
            self.assertIn("wp_tags", rows[0])
            self.assertIn("wp_categories", rows[0])
            self.assertIn("ghost_edit_url", rows[0])
            self.assertEqual(rows[0]["ghost_edit_url"], "")
            self.assertEqual(rows[0]["migration_status"], "todo")

    def test_append_preserves_existing_rows(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:wp="http://wordpress.org/export/1.2/">
  <channel>
    <item>
      <title>Post A</title>
      <dc:creator>author_a</dc:creator>
      <wp:post_type>post</wp:post_type>
      <wp:post_id>10</wp:post_id>
      <wp:post_name>post-a</wp:post_name>
      <wp:status>publish</wp:status>
    </item>
    <item>
      <title>Post B</title>
      <dc:creator>author_b</dc:creator>
      <wp:post_type>post</wp:post_type>
      <wp:post_id>11</wp:post_id>
      <wp:post_name>post-b</wp:post_name>
      <wp:status>draft</wp:status>
    </item>
  </channel>
</rss>
"""
        with tempfile.TemporaryDirectory() as td:
            xml_path = Path(td) / "export.xml"
            xml_path.write_text(xml, encoding="utf-8")
            out_path = Path(td) / "tracking.csv"

            # First write full CSV.
            class Args1:
                xml = [str(xml_path)]
                out = str(out_path)
                append = False

            ctx = {"out": _Out()}
            rc = cmd_tracking_from_xml(Args1(), ctx)
            self.assertEqual(rc, 0)

            # Simulate work on Post A.
            text = out_path.read_text(encoding="utf-8")
            self.assertIn("post-a", text)
            # Replace first data row migration_status from todo -> done.
            text = text.replace("10,post-a,Post A,publish", "10,post-a,Post A,publish", 1).replace(",todo,", ",done,", 1)
            out_path.write_text(text, encoding="utf-8")

            # Append with same XML; should not duplicate and must preserve done.
            class Args2:
                xml = [str(xml_path)]
                out = str(out_path)
                append = True

            ctx2 = {"out": _Out()}
            rc2 = cmd_tracking_from_xml(Args2(), ctx2)
            self.assertEqual(rc2, 0)

            with out_path.open("r", encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 2)
            a = next(r for r in rows if r["wp_post_id"] == "10")
            self.assertEqual(a["migration_status"], "done")

    def test_missing_slug_is_guessed_and_noted(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:wp="http://wordpress.org/export/1.2/">
  <channel>
    <item>
      <title>Welcome to Example Site</title>
      <dc:creator>author_b</dc:creator>
      <wp:post_type>post</wp:post_type>
      <wp:post_id>42</wp:post_id>
      <wp:post_name></wp:post_name>
      <wp:status>draft</wp:status>
    </item>
  </channel>
</rss>
"""
        with tempfile.TemporaryDirectory() as td:
            xml_path = Path(td) / "export.xml"
            xml_path.write_text(xml, encoding="utf-8")
            out_path = Path(td) / "tracking.csv"

            class Args:
                xml = [str(xml_path)]
                out = str(out_path)
                append = False

            ctx = {"out": _Out()}
            rc = cmd_tracking_from_xml(Args(), ctx)
            self.assertEqual(rc, 0)

            with out_path.open("r", encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["wp_post_id"], "42")
            self.assertEqual(rows[0]["wp_slug"], "welcome-to-example-site")
            self.assertIn("wp_slug_missing_in_xml", rows[0]["notes"])

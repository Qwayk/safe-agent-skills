import tempfile
import unittest

from wordpress_api_tool.wp_xml import parse_wordpress_export_xml


class WpXmlTests(unittest.TestCase):
    def test_parse_includes_only_posts(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
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
      <category domain="post_tag">Tag One</category>
      <category domain="category">Cat One</category>
    </item>
    <item>
      <title>Page B</title>
      <wp:post_type>page</wp:post_type>
      <wp:post_id>11</wp:post_id>
      <wp:post_name>page-b</wp:post_name>
      <wp:status>publish</wp:status>
    </item>
  </channel>
</rss>
"""
        with tempfile.TemporaryDirectory() as td:
            path = f"{td}/export.xml"
            with open(path, "w", encoding="utf-8") as f:
                f.write(xml)
            rows = parse_wordpress_export_xml(path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].wp_post_id, 10)
        self.assertEqual(rows[0].wp_slug, "post-a")
        self.assertEqual(rows[0].wp_title, "Post A")
        self.assertEqual(rows[0].wp_author, "author_a")
        self.assertEqual(rows[0].wp_tags, ["Tag One"])
        self.assertEqual(rows[0].wp_categories, ["Cat One"])

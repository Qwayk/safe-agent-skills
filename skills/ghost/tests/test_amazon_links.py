import unittest

from ghost_api_tool.amazon_links import is_amazon_affiliate_link, is_amazon_link, parse_amazon_link


class AmazonLinksTests(unittest.TestCase):
    def test_detects_amzn_short(self):
        info = parse_amazon_link("https://amzn.to/abc123")
        self.assertIsNotNone(info)
        assert info is not None
        self.assertTrue(info.is_amzn_short)
        self.assertTrue(is_amazon_link(info.url))
        self.assertFalse(is_amazon_affiliate_link(info.url))

    def test_detects_amazon_affiliate_tag(self):
        url = "https://www.amazon.com/dp/B000000000?tag=exampletag-20&th=1"
        info = parse_amazon_link(url)
        self.assertIsNotNone(info)
        assert info is not None
        self.assertFalse(info.is_amzn_short)
        self.assertEqual(info.affiliate_tag, "exampletag-20")
        self.assertTrue(is_amazon_affiliate_link(url))

    def test_ignores_amazonaws(self):
        self.assertFalse(is_amazon_link("https://s3.amazonaws.com/bucket/key"))

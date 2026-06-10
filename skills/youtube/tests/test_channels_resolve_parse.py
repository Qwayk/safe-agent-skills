from __future__ import annotations

import unittest

from youtube_api_tool.commands.channels import parse_channel_input


class TestChannelsResolveParse(unittest.TestCase):
    def test_raw_channel_id(self) -> None:
        inp = parse_channel_input("UC_x5XG1OV2P6uZZ5FSM9Ttw")
        self.assertEqual(inp.kind, "channel_id")
        self.assertEqual(inp.value, "UC_x5XG1OV2P6uZZ5FSM9Ttw")

    def test_channel_url(self) -> None:
        inp = parse_channel_input("https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw")
        self.assertEqual(inp.kind, "channel_id")
        self.assertEqual(inp.value, "UC_x5XG1OV2P6uZZ5FSM9Ttw")

    def test_raw_handle(self) -> None:
        inp = parse_channel_input("@GoogleDevelopers")
        self.assertEqual(inp.kind, "handle")
        self.assertEqual(inp.value, "GoogleDevelopers")

    def test_handle_url(self) -> None:
        inp = parse_channel_input("https://www.youtube.com/@GoogleDevelopers/videos")
        self.assertEqual(inp.kind, "handle")
        self.assertEqual(inp.value, "GoogleDevelopers")

    def test_user_url(self) -> None:
        inp = parse_channel_input("https://www.youtube.com/user/GoogleDevelopers")
        self.assertEqual(inp.kind, "username")
        self.assertEqual(inp.value, "GoogleDevelopers")

    def test_custom_url_is_ambiguous_query(self) -> None:
        inp = parse_channel_input("https://www.youtube.com/c/SomeCustomName")
        self.assertEqual(inp.kind, "query")
        self.assertEqual(inp.value, "SomeCustomName")


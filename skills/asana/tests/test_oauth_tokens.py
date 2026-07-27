from __future__ import annotations

import unittest

from asana_safe_agent_cli.oauth_tokens import oauth_lifecycle_supported


class TestOAuthBoundary(unittest.TestCase):
    def test_oauth_lifecycle_is_explicitly_outside_tool(self) -> None:
        self.assertFalse(oauth_lifecycle_supported())


if __name__ == "__main__":
    unittest.main()

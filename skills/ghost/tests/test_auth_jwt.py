import unittest

from ghost_api_tool.auth_jwt import generate_admin_jwt


class JwtTests(unittest.TestCase):
    def test_generate_jwt_shape(self):
        # kid=abc, secret=00... (hex)
        token, exp = generate_admin_jwt("abc:" + "00" * 32, now_s=1, ttl_s=300)
        self.assertIsInstance(token, str)
        self.assertEqual(exp, 301)
        parts = token.split(".")
        self.assertEqual(len(parts), 3)

    def test_ttl_bounds(self):
        with self.assertRaises(RuntimeError):
            generate_admin_jwt("abc:" + "00" * 32, now_s=1, ttl_s=0)
        with self.assertRaises(RuntimeError):
            generate_admin_jwt("abc:" + "00" * 32, now_s=1, ttl_s=301)

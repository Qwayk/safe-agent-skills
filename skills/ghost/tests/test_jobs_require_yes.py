import unittest

from ghost_api_tool.commands.jobs import cmd_jobs_run


class JobsSafetyTests(unittest.TestCase):
    def test_jobs_require_yes_with_apply(self):
        class _Out:
            def __init__(self):
                self.items = []

            def print(self, obj):
                self.items.append(obj)

        class Args:
            file = "x.csv"
            limit = None

        out = _Out()
        ctx = {"apply": True, "yes": False, "out": out}
        rc = cmd_jobs_run(Args(), ctx)
        self.assertEqual(rc, 0)
        self.assertEqual(len(out.items), 1)
        self.assertTrue(out.items[0]["refused"])

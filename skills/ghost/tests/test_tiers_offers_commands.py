import unittest

from ghost_api_tool.commands.offer import cmd_offer_create, cmd_offer_update
from ghost_api_tool.commands.tier import cmd_tier_create, cmd_tier_update


class _Out:
    def __init__(self) -> None:
        self.items = []

    def print(self, obj):
        self.items.append(obj)


class _TierOfferCommandTests(unittest.TestCase):
    def test_tier_create_dry_run_outputs_plan(self) -> None:
        class Args:
            name = "Gold"
            description = "Desc"
            welcome_page_url = None
            visibility = "public"
            monthly_price = 100
            yearly_price = None
            currency = "usd"
            benefit = ["A", "B"]

        out = _Out()
        ctx = {"apply": False, "out": out}
        rc = cmd_tier_create(Args(), ctx)
        self.assertEqual(rc, 0)
        self.assertEqual(len(out.items), 1)
        obj = out.items[0]
        self.assertFalse(obj["apply"])
        self.assertIn("create", obj)
        self.assertEqual(obj["create"]["name"], "Gold")

    def test_tier_update_dry_run_includes_name_required_by_api(self) -> None:
        class FakeApi:
            def tiers_read_by_id(self, _id):
                return {"tiers": [{"id": "t1", "name": "Bronze", "updated_at": "2020-01-01T00:00:00.000Z"}]}

        class Args:
            id = "t1"
            name = None
            description = "New"
            welcome_page_url = None
            visibility = None
            active = None
            monthly_price = None
            yearly_price = None
            currency = None
            benefit = None

        out = _Out()
        ctx = {"apply": False, "out": out, "_api": FakeApi()}
        rc = cmd_tier_update(Args(), ctx)
        self.assertEqual(rc, 0)
        obj = out.items[0]
        self.assertFalse(obj["apply"])
        self.assertEqual(obj["tier_id"], "t1")
        self.assertIn("name", obj["planned"]["fields"])

    def test_offer_create_dry_run_outputs_plan(self) -> None:
        class Args:
            name = "Black Friday"
            code = "black-friday"
            type = "percent"
            cadence = "year"
            duration = "once"
            amount = 10
            tier_id = "tier123"
            display_title = None
            display_description = None
            duration_in_months = None
            currency = None
            currency_restriction = None

        out = _Out()
        ctx = {"apply": False, "out": out}
        rc = cmd_offer_create(Args(), ctx)
        self.assertEqual(rc, 0)
        obj = out.items[0]
        self.assertFalse(obj["apply"])
        self.assertEqual(obj["create"]["tier"]["id"], "tier123")

    def test_offer_update_dry_run_outputs_planned_fields(self) -> None:
        class FakeApi:
            def offers_read_by_id(self, _id):
                return {"offers": [{"id": "o1", "code": "x", "updated_at": "2020-01-01T00:00:00.000Z"}]}

        class Args:
            id = "o1"
            name = None
            code = "new-code"
            display_title = None
            display_description = None

        out = _Out()
        ctx = {"apply": False, "out": out, "_api": FakeApi()}
        rc = cmd_offer_update(Args(), ctx)
        self.assertEqual(rc, 0)
        obj = out.items[0]
        self.assertFalse(obj["apply"])
        self.assertIn("code", obj["planned"]["fields"])


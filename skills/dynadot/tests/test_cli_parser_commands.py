from __future__ import annotations

import unittest

from dynadot_api_tool.cli import build_parser


class TestCliParserCommands(unittest.TestCase):
    def test_auth_check_command_registered(self) -> None:
        p = build_parser()
        args = p.parse_args(["auth", "check"])
        self.assertTrue(callable(getattr(args, "func", None)))
        self.assertFalse(bool(getattr(args, "write_capable", True)))

    def test_account_commands_registered(self) -> None:
        p = build_parser()

        info_args = p.parse_args(["account", "info"])
        self.assertTrue(callable(getattr(info_args, "func", None)))
        self.assertFalse(bool(getattr(info_args, "write_capable", True)))

        balance_args = p.parse_args(["account", "balance"])
        self.assertTrue(callable(getattr(balance_args, "func", None)))
        self.assertFalse(bool(getattr(balance_args, "write_capable", True)))

        coupons_args = p.parse_args(["account", "coupons", "--coupon-type", "registration"])
        self.assertTrue(callable(getattr(coupons_args, "func", None)))
        self.assertFalse(bool(getattr(coupons_args, "write_capable", True)))

    def test_pricing_tld_price_command_registered(self) -> None:
        p = build_parser()
        args = p.parse_args(["pricing", "tld-price"])
        self.assertTrue(callable(getattr(args, "func", None)))
        self.assertFalse(bool(getattr(args, "write_capable", True)))

    def test_domains_search_command_registered(self) -> None:
        p = build_parser()
        args = p.parse_args(["domains", "search", "--domain", "a.com"])
        self.assertTrue(callable(getattr(args, "func", None)))
        self.assertFalse(bool(getattr(args, "write_capable", True)))

    def test_domains_push_command_registered(self) -> None:
        p = build_parser()
        args = p.parse_args(["domains", "push", "--to-username", "receiver", "--domain", "a.com"])
        self.assertTrue(callable(getattr(args, "func", None)))
        self.assertTrue(bool(getattr(args, "write_capable", False)))

    def test_jobs_run_command_registered(self) -> None:
        p = build_parser()
        args = p.parse_args(["jobs", "run"])
        self.assertTrue(callable(getattr(args, "func", None)))
        self.assertTrue(bool(getattr(args, "write_capable", False)))

    def test_domains_name_servers_commands_registered(self) -> None:
        p = build_parser()
        export_args = p.parse_args(["domains", "name-servers", "export", "--domains-file", "domains.txt"])
        self.assertTrue(callable(getattr(export_args, "func", None)))
        self.assertFalse(bool(getattr(export_args, "write_capable", True)))

        diff_args = p.parse_args(
            ["domains", "name-servers", "diff", "--current-in", "current.json", "--desired-ns", "ns1.example.net"]
        )
        self.assertTrue(callable(getattr(diff_args, "func", None)))
        self.assertFalse(bool(getattr(diff_args, "write_capable", True)))

        set_args = p.parse_args(["domains", "name-servers", "set", "--diff-in", "diff.json"])
        self.assertTrue(callable(getattr(set_args, "func", None)))
        self.assertTrue(bool(getattr(set_args, "write_capable", False)))

    def test_transfer_run_command_registered(self) -> None:
        p = build_parser()
        args = p.parse_args(
            [
                "transfer",
                "run",
                "--receiver-env-file",
                "receiver.env",
                "--to-username",
                "receiver_push_username",
                "--desired-ns",
                "ns1.example.net",
                "--desired-ns",
                "ns2.example.net",
            ]
        )
        self.assertTrue(callable(getattr(args, "func", None)))
        self.assertTrue(bool(getattr(args, "write_capable", False)))

    def test_transfers_read_commands_registered(self) -> None:
        p = build_parser()

        list_args = p.parse_args(["transfers", "list"])
        self.assertTrue(callable(getattr(list_args, "func", None)))
        self.assertFalse(bool(getattr(list_args, "write_capable", True)))

        status_args = p.parse_args(["transfers", "status", "--domain", "example.com", "--transfer-type", "in"])
        self.assertTrue(callable(getattr(status_args, "func", None)))
        self.assertFalse(bool(getattr(status_args, "write_capable", True)))

        auth_args = p.parse_args(["transfers", "auth-code", "--domain", "example.com"])
        self.assertTrue(callable(getattr(auth_args, "func", None)))
        self.assertFalse(bool(getattr(auth_args, "write_capable", True)))

    def test_orders_read_commands_registered(self) -> None:
        p = build_parser()

        list_args = p.parse_args(
            ["orders", "list", "--search-by", "date_range", "--start-date", "2024/01/01", "--end-date", "2024/01/31"]
        )
        self.assertTrue(callable(getattr(list_args, "func", None)))
        self.assertFalse(bool(getattr(list_args, "write_capable", True)))

        status_args = p.parse_args(["orders", "status", "--order-id", "123"])
        self.assertTrue(callable(getattr(status_args, "func", None)))
        self.assertFalse(bool(getattr(status_args, "write_capable", True)))

    def test_contacts_read_commands_registered(self) -> None:
        p = build_parser()

        list_args = p.parse_args(["contacts", "list"])
        self.assertTrue(callable(getattr(list_args, "func", None)))
        self.assertFalse(bool(getattr(list_args, "write_capable", True)))

        get_args = p.parse_args(["contacts", "get", "--contact-id", "123"])
        self.assertTrue(callable(getattr(get_args, "func", None)))
        self.assertFalse(bool(getattr(get_args, "write_capable", True)))

    def test_dns_read_commands_registered(self) -> None:
        p = build_parser()

        get_args = p.parse_args(["dns", "get", "--domain", "example.com"])
        self.assertTrue(callable(getattr(get_args, "func", None)))
        self.assertFalse(bool(getattr(get_args, "write_capable", True)))

    def test_marketplace_read_commands_registered(self) -> None:
        p = build_parser()

        list_args = p.parse_args(["marketplace", "listings", "list", "--page", "1", "--page-size", "10"])
        self.assertTrue(callable(getattr(list_args, "func", None)))
        self.assertFalse(bool(getattr(list_args, "write_capable", True)))

        get_args = p.parse_args(["marketplace", "listings", "get", "--domain", "example.com"])
        self.assertTrue(callable(getattr(get_args, "func", None)))
        self.assertFalse(bool(getattr(get_args, "write_capable", True)))

    def test_auctions_read_commands_registered(self) -> None:
        p = build_parser()

        open_args = p.parse_args(["auctions", "open", "--page", "1", "--page-size", "10"])
        self.assertTrue(callable(getattr(open_args, "func", None)))
        self.assertFalse(bool(getattr(open_args, "write_capable", True)))

        closed_args = p.parse_args(["auctions", "closed", "--start-date", "2026-01-01", "--end-date", "2026-01-31"])
        self.assertTrue(callable(getattr(closed_args, "func", None)))
        self.assertFalse(bool(getattr(closed_args, "write_capable", True)))

        details_args = p.parse_args(["auctions", "details", "--domain", "example.com"])
        self.assertTrue(callable(getattr(details_args, "func", None)))
        self.assertFalse(bool(getattr(details_args, "write_capable", True)))

        bids_args = p.parse_args(["auctions", "bids", "--page", "1", "--page-size", "10"])
        self.assertTrue(callable(getattr(bids_args, "func", None)))
        self.assertFalse(bool(getattr(bids_args, "write_capable", True)))

    def test_backorder_auctions_read_commands_registered(self) -> None:
        p = build_parser()

        closed_args = p.parse_args(
            ["backorder-auctions", "closed", "--start-date", "2026-01-01", "--end-date", "2026-01-31"]
        )
        self.assertTrue(callable(getattr(closed_args, "func", None)))
        self.assertFalse(bool(getattr(closed_args, "write_capable", True)))

        details_args = p.parse_args(["backorder-auctions", "details", "--domain", "example.com"])
        self.assertTrue(callable(getattr(details_args, "func", None)))
        self.assertFalse(bool(getattr(details_args, "write_capable", True)))

    def test_closeouts_read_commands_registered(self) -> None:
        p = build_parser()
        args = p.parse_args(["closeouts", "list", "--page", "1"])
        self.assertTrue(callable(getattr(args, "func", None)))
        self.assertFalse(bool(getattr(args, "write_capable", True)))

    def test_backorders_read_commands_registered(self) -> None:
        p = build_parser()
        args = p.parse_args(["backorders", "requests", "list", "--start-date", "2026-01-01", "--end-date", "2026-01-31"])
        self.assertTrue(callable(getattr(args, "func", None)))
        self.assertFalse(bool(getattr(args, "write_capable", True)))

    def test_cn_audit_read_commands_registered(self) -> None:
        p = build_parser()
        args = p.parse_args(["cn-audit", "status", "--contact-id", "123"])
        self.assertTrue(callable(getattr(args, "func", None)))
        self.assertFalse(bool(getattr(args, "write_capable", True)))

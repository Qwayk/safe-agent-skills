from __future__ import annotations

import argparse
from typing import Type

from . import account as account_cmd
from . import auctions as auctions_cmd
from . import auth as auth_cmd
from . import api3 as api3_cmd
from . import backorder_auctions as backorder_auctions_cmd
from . import backorders as backorders_cmd
from . import closeouts as closeouts_cmd
from . import cn_audit as cn_audit_cmd
from . import contacts as contacts_cmd
from . import demo as demo_cmd
from . import dns as dns_cmd
from . import domains as domains_cmd
from . import jobs as jobs_cmd
from . import marketplace as marketplace_cmd
from . import onboarding as onboarding_cmd
from . import pricing as pricing_cmd
from . import orders as orders_cmd
from . import runs as runs_cmd
from . import transfer as transfer_cmd
from . import transfers as transfers_cmd


def register_all(subparsers: argparse._SubParsersAction, *, parser_class: Type[argparse.ArgumentParser]) -> None:  # type: ignore[name-defined]
    """
    Single registration entrypoint so extending the CLI is predictable:
    - add new command module
    - add one register_* call here
    """

    runs_cmd.register_runs(subparsers, parser_class=parser_class)
    onboarding_cmd.register_onboarding(subparsers, parser_class=parser_class)
    auth_cmd.register_auth(subparsers, parser_class=parser_class)
    api3_cmd.register_api3(subparsers, parser_class=parser_class)
    account_cmd.register_account(subparsers, parser_class=parser_class)
    contacts_cmd.register_contacts(subparsers, parser_class=parser_class)
    pricing_cmd.register_pricing(subparsers, parser_class=parser_class)
    dns_cmd.register_dns(subparsers, parser_class=parser_class)
    domains_cmd.register_domains(subparsers, parser_class=parser_class)
    transfer_cmd.register_transfer(subparsers, parser_class=parser_class)
    transfers_cmd.register_transfers(subparsers, parser_class=parser_class)
    orders_cmd.register_orders(subparsers, parser_class=parser_class)
    jobs_cmd.register_jobs(subparsers, parser_class=parser_class)
    marketplace_cmd.register_marketplace(subparsers, parser_class=parser_class)
    auctions_cmd.register_auctions(subparsers, parser_class=parser_class)
    backorder_auctions_cmd.register_backorder_auctions(subparsers, parser_class=parser_class)
    closeouts_cmd.register_closeouts(subparsers, parser_class=parser_class)
    backorders_cmd.register_backorders(subparsers, parser_class=parser_class)
    cn_audit_cmd.register_cn_audit(subparsers, parser_class=parser_class)
    demo_cmd.register_demo(subparsers, parser_class=parser_class)

# API coverage (endpoints → CLI)

Purpose:
- Make “all capabilities” measurable (no guessing about what’s implemented).
- Give the Manager a single main reference for review/approval.
- Help customers quickly see what the tool can and cannot do.

Rules:
- Keep this table honest. If something is missing, list it as missing.
- If behavior differs from the provider docs, note it and link `docs/references.md`.

## Summary

- Provider: Dynadot
- API base URL: https://api.dynadot.com/api3.json (sandbox: https://api-sandbox.dynadot.com/api3.json)
- Auth method: API key (URL query param `key=...`)
- Official docs: https://www.dynadot.com/domain/api-commands
- Last audited vs official docs (UTC): 2026-02-25
- Official command snapshot (for tests): `docs/official_commands.txt` (extracted from Dynadot’s published request examples)
- Current write contract: all shipped Dynadot write families plan only, then require explicit no-snapshot approval before Dynadot HTTP until command-specific saved snapshot support is available.
- Write plans expose `before_state.required: true`, `before_state.supported: false`, and `before_state.status: no_snapshot_available`.
- Plans expose the no-recovery contract through `recovery`, with `end_state`, `backups: []`, `snapshots: []`, and `rollback_plan: null`.
- Current write apply does not produce a receipt.

## Command coverage ledger (official docs)

Columns:
- API command: Dynadot `command=` value (API3 is command-based)
- Status: `Implemented` / `Missing`
- CLI command(s): first-class CLI wrapper(s) in this tool
- Safety gates: read-only or apply-gated rules (when implemented)
- Notes: important behavior differences / verification notes

Dynadot API3 is **command-based** (not REST paths). This ledger maps `command=` values → CLI support.

Legend:
- `Implemented` = available in the CLI (tested + documented)
- `Missing` = not started yet
- Any row with `--apply --yes --plan-in` is currently plan-only at apply time: after gates pass, it requires explicit no-snapshot approval before Dynadot HTTP because before-state support is missing.

| API command | Status | CLI command(s) | Safety gates | Notes |
|---|---|---|---|---|
| `account_info` | Implemented | `dynadot-api-tool api3 account-info` | read-only | — |
| `add_backorder_request` | Implemented | `dynadot-api-tool api3 add-backorder-request` | `--apply --yes --plan-in` `--ack-irreversible` | — |
| `add_ns` | Implemented | `dynadot-api-tool api3 add-ns` | `--apply --yes --plan-in` | — |
| `authorize_transfer_away` | Implemented | `dynadot-api-tool api3 authorize-transfer-away` | `--apply --yes --plan-in` | — |
| `backorder_request_list` | Implemented | `dynadot-api-tool api3 backorder-request-list` | read-only | Docs list params as `start_date`/`end_date`, but their request examples use `startDate`/`endDate`. Tool follows the examples. |
| `bulk_register` | Implemented | `dynadot-api-tool api3 bulk-register` | `--apply --yes --plan-in` `--ack-irreversible` | — |
| `buy_expired_closeout_domain` | Implemented | `dynadot-api-tool api3 buy-expired-closeout-domain` | `--apply --yes --plan-in` `--ack-irreversible` | — |
| `buy_it_now` | Implemented | `dynadot-api-tool api3 buy-it-now` | `--apply --yes --plan-in` `--ack-irreversible` | — |
| `cancel_transfer` | Implemented | `dynadot-api-tool api3 cancel-transfer` | `--apply --yes --plan-in` | — |
| `contact_list` | Implemented | `dynadot-api-tool api3 contact-list` | read-only | — |
| `create_cn_audit` | Implemented | `dynadot-api-tool api3 create-cn-audit` | `--apply --yes --plan-in` | — |
| `create_contact` | Implemented | `dynadot-api-tool api3 create-contact` | `--apply --yes --plan-in` | — |
| `create_folder` | Implemented | `dynadot-api-tool api3 create-folder` | `--apply --yes --plan-in` | — |
| `delete` | Implemented | `dynadot-api-tool api3 delete` | `--apply --yes --plan-in` `--ack-irreversible` | — |
| `delete_backorder_request` | Implemented | `dynadot-api-tool api3 delete-backorder-request` | `--apply --yes --plan-in` | — |
| `delete_contact` | Implemented | `dynadot-api-tool api3 delete-contact` | `--apply --yes --plan-in` | — |
| `delete_folder` | Implemented | `dynadot-api-tool api3 delete-folder` | `--apply --yes --plan-in` | — |
| `delete_ns` | Implemented | `dynadot-api-tool api3 delete-ns` | `--apply --yes --plan-in` | — |
| `delete_ns_by_domain` | Implemented | `dynadot-api-tool api3 delete-ns-by-domain` | `--apply --yes --plan-in` | — |
| `domain_info` | Implemented | `dynadot-api-tool api3 domain-info` | read-only | `domains status` derives `DomainInfo.Status` from `domain_info`. |
| `edit_contact` | Implemented | `dynadot-api-tool api3 edit-contact` | `--apply --yes --plan-in` | — |
| `folder_list` | Implemented | `dynadot-api-tool api3 folder-list` | read-only | Lists folder groups; useful for inventory exports. |
| `get_account_balance` | Implemented | `dynadot-api-tool api3 get-account-balance` | read-only | — |
| `get_auction_bids` | Implemented | `dynadot-api-tool api3 get-auction-bids` | read-only | Supports pagination via `--page` / `--page-size` (page size max 50) and optional `--currency`. |
| `get_auction_details` | Implemented | `dynadot-api-tool api3 get-auction-details` | read-only | Sends the `domain` param as a comma-joined list. |
| `get_backorder_auction_details` | Implemented | `dynadot-api-tool api3 get-backorder-auction-details` | read-only | — |
| `get_closed_auctions` | Implemented | `dynadot-api-tool api3 get-closed-auctions` | read-only | Accepts `YYYY-M-D` or `YYYY-MM-DD` and sends `startDate`/`endDate`; supports optional `--currency`. |
| `get_open_backorder_auctions` | Implemented | `dynadot-api-tool api3 get-open-backorder-auctions` | read-only | Docs mark `currency` as optional; request examples use `api3.html`/`api3.xml` for this command. |
| `get_closed_backorder_auctions` | Implemented | `dynadot-api-tool api3 get-closed-backorder-auctions` | read-only | Accepts `YYYY-M-D` or `YYYY-MM-DD` and sends `startDate`/`endDate`; supports optional `--currency`. |
| `get_cn_audit_status` | Implemented | `dynadot-api-tool api3 get-cn-audit-status` | read-only | `--gtld` sets `gtld=1` to query cnnic-gtld audit results. |
| `get_contact` | Implemented | `dynadot-api-tool api3 get-contact` | read-only | — |
| `get_dns` | Implemented | `dynadot-api-tool api3 get-dns` | read-only | — |
| `get_domain_push_request` | Implemented | `dynadot-api-tool api3 get-domain-push-request` | read-only | Receiver-side: list incoming push requests. |
| `get_expired_closeout_domains` | Implemented | `dynadot-api-tool api3 get-expired-closeout-domains` | read-only | Supports optional `--domain`, pagination, and optional currency. |
| `get_listing_item` | Implemented | `dynadot-api-tool api3 get-listing-item` | read-only | Dynadot sandbox does not support marketplace listing item reads. |
| `get_listings` | Implemented | `dynadot-api-tool api3 get-listings` | read-only | Dynadot sandbox does not support marketplace listing list reads. |
| `get_ns` | Implemented | `dynadot-api-tool api3 get-ns` | read-only | Reads current name servers for each domain. |
| `get_open_auctions` | Implemented | `dynadot-api-tool api3 get-open-auctions` | read-only | Supports pagination (page size max 50), optional `--type`, and optional `--currency`. |
| `get_order_status` | Implemented | `dynadot-api-tool api3 get-order-status` | read-only | — |
| `get_transfer_auth_code` | Implemented | `dynadot-api-tool api3 get-transfer-auth-code` | `--apply --yes --plan-in` | Apply-gated because Dynadot's request examples include state-changing params (`new_code`, `unlock_domain_for_transfer`). Treat the output as sensitive. |
| `get_transfer_status` | Implemented | `dynadot-api-tool api3 get-transfer-status` | read-only | `--transfer-type out` is accepted as an alias for `away`. |
| `is_processing` | Implemented | `dynadot-api-tool api3 is-processing` | read-only | Safe connectivity/auth check. |
| `list_coupons` | Implemented | `dynadot-api-tool api3 list-coupons` | read-only | Requires `--coupon-type`. |
| `list_domain` | Implemented | `dynadot-api-tool api3 list-domain` | read-only | Paginates via `page_index` / `count_per_page` when requested; `--all` stops on first empty page (or `--max-pages`). |
| `lock_domain` | Implemented | `dynadot-api-tool api3 lock-domain` | `--apply --yes --plan-in` | — |
| `order_list` | Implemented | `dynadot-api-tool api3 order-list` | read-only | — |
| `place_auction_bid` | Implemented | `dynadot-api-tool api3 place-auction-bid` | `--apply --yes --plan-in` `--ack-irreversible` | — |
| `place_backorder_auction_bid` | Implemented | `dynadot-api-tool api3 place-backorder-auction-bid` | `--apply --yes --plan-in` `--ack-irreversible` | — |
| `push` | Implemented | `dynadot-api-tool api3 push` | `--apply --yes --plan-in` | Bulk: up to 50 domains per request; uses `unlock_domain_for_push=1` by default. |
| `register` | Implemented | `dynadot-api-tool api3 register` | `--apply --yes --plan-in` `--ack-irreversible` | — |
| `register_ns` | Implemented | `dynadot-api-tool api3 register-ns` | `--apply --yes --plan-in` | — |
| `renew` | Implemented | `dynadot-api-tool api3 renew` | `--apply --yes --plan-in` `--ack-irreversible` | — |
| `search` | Implemented | `dynadot-api-tool api3 search` | read-only | Supports `--show-price` and optional `--currency`. Does not support per-domain `languageN` params. |
| `server_list` | Implemented | `dynadot-api-tool api3 server-list` | read-only | Pre-checks that desired name servers exist in the account; can warn or refuse depending on flags. |
| `set_afternic_confirm_action` | Implemented | `dynadot-api-tool api3 set-afternic-confirm-action` | `--apply --yes --plan-in` | — |
| `set_clear_default_setting` | Implemented | `dynadot-api-tool api3 set-clear-default-setting` | `--apply --yes --plan-in` | — |
| `set_clear_domain_setting` | Implemented | `dynadot-api-tool api3 set-clear-domain-setting` | `--apply --yes --plan-in` | — |
| `set_clear_folder_setting` | Implemented | `dynadot-api-tool api3 set-clear-folder-setting` | `--apply --yes --plan-in` | — |
| `set_contact_eu_setting` | Implemented | `dynadot-api-tool api3 set-contact-eu-setting` | `--apply --yes --plan-in` | — |
| `set_contact_lv_setting` | Implemented | `dynadot-api-tool api3 set-contact-lv-setting` | `--apply --yes --plan-in` | — |
| `set_customer_id` | Implemented | `dynadot-api-tool api3 set-customer-id` | `--apply --yes --plan-in` | — |
| `set_default_dns` | Implemented | `dynadot-api-tool api3 set-default-dns` | `--apply --yes --plan-in` | — |
| `set_default_dns2` | Implemented | `dynadot-api-tool api3 set-default-dns2` | `--apply --yes --plan-in` | — |
| `set_default_email_forward` | Implemented | `dynadot-api-tool api3 set-default-email-forward` | `--apply --yes --plan-in` | — |
| `set_default_forwarding` | Implemented | `dynadot-api-tool api3 set-default-forwarding` | `--apply --yes --plan-in` | — |
| `set_default_hosting` | Implemented | `dynadot-api-tool api3 set-default-hosting` | `--apply --yes --plan-in` | — |
| `set_default_ns` | Implemented | `dynadot-api-tool api3 set-default-ns` | `--apply --yes --plan-in` | — |
| `set_default_parking` | Implemented | `dynadot-api-tool api3 set-default-parking` | `--apply --yes --plan-in` | — |
| `set_default_renew_option` | Implemented | `dynadot-api-tool api3 set-default-renew-option` | `--apply --yes --plan-in` | — |
| `set_default_stealth` | Implemented | `dynadot-api-tool api3 set-default-stealth` | `--apply --yes --plan-in` | — |
| `set_default_whois` | Implemented | `dynadot-api-tool api3 set-default-whois` | `--apply --yes --plan-in` | — |
| `set_dns2` | Implemented | `dynadot-api-tool api3 set-dns2` | `--apply --yes --plan-in` | — |
| `set_dnssec` | Implemented | `dynadot-api-tool api3 set-dnssec` | `--apply --yes --plan-in` | — |
| `set_domain_push_request` | Implemented | `dynadot-api-tool api3 set-domain-push-request` | `--apply --yes --plan-in` | Receiver-side: accept/decline pushes. |
| `set_email_forward` | Implemented | `dynadot-api-tool api3 set-email-forward` | `--apply --yes --plan-in` | — |
| `set_folder` | Implemented | `dynadot-api-tool api3 set-folder` | `--apply --yes --plan-in` | — |
| `set_folder_dns` | Implemented | `dynadot-api-tool api3 set-folder-dns` | `--apply --yes --plan-in` | — |
| `set_folder_dns2` | Implemented | `dynadot-api-tool api3 set-folder-dns2` | `--apply --yes --plan-in` | — |
| `set_folder_email_forward` | Implemented | `dynadot-api-tool api3 set-folder-email-forward` | `--apply --yes --plan-in` | — |
| `set_folder_forwarding` | Implemented | `dynadot-api-tool api3 set-folder-forwarding` | `--apply --yes --plan-in` | — |
| `set_folder_hosting` | Implemented | `dynadot-api-tool api3 set-folder-hosting` | `--apply --yes --plan-in` | — |
| `set_folder_name` | Implemented | `dynadot-api-tool api3 set-folder-name` | `--apply --yes --plan-in` | — |
| `set_folder_ns` | Implemented | `dynadot-api-tool api3 set-folder-ns` | `--apply --yes --plan-in` | — |
| `set_folder_parking` | Implemented | `dynadot-api-tool api3 set-folder-parking` | `--apply --yes --plan-in` | — |
| `set_folder_renew_option` | Implemented | `dynadot-api-tool api3 set-folder-renew-option` | `--apply --yes --plan-in` | — |
| `set_folder_stealth` | Implemented | `dynadot-api-tool api3 set-folder-stealth` | `--apply --yes --plan-in` | — |
| `set_folder_whois` | Implemented | `dynadot-api-tool api3 set-folder-whois` | `--apply --yes --plan-in` | — |
| `set_for_sale` | Implemented | `dynadot-api-tool api3 set-for-sale` | `--apply --yes --plan-in` | — |
| `set_forwarding` | Implemented | `dynadot-api-tool api3 set-forwarding` | `--apply --yes --plan-in` | — |
| `set_hosting` | Implemented | `dynadot-api-tool api3 set-hosting` | `--apply --yes --plan-in` | — |
| `set_note` | Implemented | `dynadot-api-tool api3 set-note` | `--apply --yes --plan-in` | — |
| `set_ns` | Implemented | `dynadot-api-tool api3 set-ns` | `--apply --yes --plan-in` | Current apply requires explicit no-snapshot approval before Dynadot HTTP until per-domain before-state is saved. |
| `set_ns_ip` | Implemented | `dynadot-api-tool api3 set-ns-ip` | `--apply --yes --plan-in` | — |
| `set_parking` | Implemented | `dynadot-api-tool api3 set-parking` | `--apply --yes --plan-in` | — |
| `set_privacy` | Implemented | `dynadot-api-tool api3 set-privacy` | `--apply --yes --plan-in` | — |
| `set_renew_option` | Implemented | `dynadot-api-tool api3 set-renew-option` | `--apply --yes --plan-in` | — |
| `set_sedo_confirm_action` | Implemented | `dynadot-api-tool api3 set-sedo-confirm-action` | `--apply --yes --plan-in` | — |
| `set_stealth` | Implemented | `dynadot-api-tool api3 set-stealth` | `--apply --yes --plan-in` | — |
| `set_transfer_auth_code` | Implemented | `dynadot-api-tool api3 set-transfer-auth-code` | `--apply --yes --plan-in` | — |
| `set_whois` | Implemented | `dynadot-api-tool api3 set-whois` | `--apply --yes --plan-in` | — |
| `tld_price` | Implemented | `dynadot-api-tool api3 tld-price` | read-only | Supports `--page`, `--page-size`, and optional `--currency`. |
| `transfer` | Implemented | `dynadot-api-tool api3 transfer` | `--apply --yes --plan-in` `--ack-irreversible` | — |
| `transfer_domain_list` | Implemented | `dynadot-api-tool api3 transfer-domain-list` | read-only | Docs label this “Transfer Out Domain List”. |

## Known gaps (explicit)

- None for request-example-backed commands: this tool implements every Dynadot API3 `command=` value in `docs/official_commands.txt`.

### Out of scope (Dynadot docs list items without full request examples/params)

Dynadot’s docs page includes some command names in menus/links that do not have full request examples/parameter tables on the page.
To avoid guessing parameters, we treat these as out-of-scope until Dynadot publishes complete docs for them:

- `clear_dnssec`
- `get_dnssec`
- `restore`
- `set_contact_lt_setting`
- `set_reseller_contact_whois_verification_status`

If Dynadot later publishes full request examples for these, we will add them to `docs/official_commands.txt` and implement them as first-class `api3` subcommands.

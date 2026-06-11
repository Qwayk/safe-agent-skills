# References (sources)

Purpose:
- Record what sources the tool implementation relies on (so behavior is auditable and reproducible).
- Prefer official provider docs; use other sources only when needed and note why.

Rules:
- Never include secrets (tokens, client secrets) in this file.
- When a capability depends on a specific documented behavior (rate limits, required headers, download tracking), link the exact doc page.
- Update this file whenever you add/change an endpoint or behavior based on new research.

## Provider docs (official)

- Provider: Dynadot
- API docs home (API3 command list + rate limits): https://www.dynadot.com/domain/api-commands
- Note on completeness: Dynadot’s docs page includes some command names in menus/links without full request examples/parameter tables. This tool avoids guessing and treats those items as out-of-scope until Dynadot publishes complete docs for them (tracked in `docs/api_coverage.md`).
- Command docs (anchors used by this tool):
  - `account_info`: https://www.dynadot.com/domain/api-commands#account_info
  - `contact_list`: https://www.dynadot.com/domain/api-commands#contact_list
  - `get_contact`: https://www.dynadot.com/domain/api-commands#get_contact
  - `get_account_balance`: https://www.dynadot.com/domain/api-commands#get_account_balance
  - `get_dns`: https://www.dynadot.com/domain/api-commands#get_dns
  - `get_listings`: https://www.dynadot.com/domain/api-commands#get_listings
  - `get_listing_item`: https://www.dynadot.com/domain/api-commands#get_listing_item
  - `get_open_auctions`: https://www.dynadot.com/domain/api-commands#get_open_auctions
  - `get_closed_auctions`: https://www.dynadot.com/domain/api-commands#get_closed_auctions
  - `get_open_backorder_auctions`: https://www.dynadot.com/domain/api-commands#get_open_backorder_auctions
  - `get_auction_details`: https://www.dynadot.com/domain/api-commands#get_auction_details
  - `get_auction_bids`: https://www.dynadot.com/domain/api-commands#get_auction_bids
  - `get_closed_backorder_auctions`: https://www.dynadot.com/domain/api-commands#get_closed_backorder_auctions
  - `get_backorder_auction_details`: https://www.dynadot.com/domain/api-commands#get_backorder_auction_details
  - `get_expired_closeout_domains`: https://www.dynadot.com/domain/api-commands#get_expired_closeout_domains
  - `backorder_request_list`: https://www.dynadot.com/domain/api-commands#backorder_request_list
  - `get_cn_audit_status`: https://www.dynadot.com/domain/api-commands#get_cn_audit_status
  - `list_domain`: https://www.dynadot.com/domain/api-commands#list_domain
  - `list_coupons`: https://www.dynadot.com/domain/api-commands#list_coupons
  - `domain_info`: https://www.dynadot.com/domain/api-commands#domain_info
  - `folder_list`: https://www.dynadot.com/domain/api-commands#folder_list
  - `get_ns`: https://www.dynadot.com/domain/api-commands#get_ns
  - `search`: https://www.dynadot.com/domain/api-commands#search
  - `set_ns`: https://www.dynadot.com/domain/api-commands#set_ns
  - `tld_price`: https://www.dynadot.com/domain/api-commands#tld_price
  - `transfer_domain_list`: https://www.dynadot.com/domain/api-commands#transfer_out_domain_list
  - `get_transfer_status`: https://www.dynadot.com/domain/api-commands#get_transfer_status
  - `get_transfer_auth_code`: https://www.dynadot.com/domain/api-commands#get_transfer_auth_code
  - `order_list`: https://www.dynadot.com/domain/api-commands#order_list
  - `get_order_status`: https://www.dynadot.com/domain/api-commands#get_order_status
- `server_list`: https://www.dynadot.com/domain/api-commands#server_list
- Auth / API key help: https://www.dynadot.com/community/help/question/how-to-use-api
- Push Username help (needed for domain pushes): https://www.dynadot.com/community/help/question/what-is-push-username
- Last verified (UTC): 2026-02-25

## Other sources (only if needed)

- (None yet.)

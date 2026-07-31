# SAV Domain APIs v1 — coverage

## Summary

- Provider: `api.sav.com`
- API docs source: `https://documenter.getpostman.com/view/9688716/TzzANHFJ`
- Source collection URL: `https://documenter.gw.postman.com/api/collections/9688716/TzzANHFJ?segregateAuth=true&versionTag=latest`
- Collection SHA-256: `d330b3df8f1b1962fcae295b0dc47b831c15f68d0d90db73c4dcb151968e33fe`
- Base URL: `https://api.sav.com/domains_api_v1/` (fixed and enforced)
- Total official documented operations in this slice: `12`
- Read operations: `4`
- Write operations: `8`

## Operation ledger

| Command | Operation ID | Method | Semantic | Required params |
| --- | --- | --- | --- | --- |
| `sav domains active` | `get_active_domains_in_account` | GET | read | `No required params in example request.` |
| `sav sales recent-auction` | `get_recent_auction_sales` | GET | read | `No required params in example request.` |
| `sav sales recent-premium` | `get_recent_premium_sales` | GET | read | `No required params in example request.` |
| `sav pricing list` | `get_domain_pricing` | GET | read | `No required params in example request.` |
| `sav domains remove-from-sale` | `remove_domain_for_sale` | GET | write | `--domain-name` |
| `sav domains submit-transfer-code` | `submit_auth_code_for_pending_transfer_in` | GET | write | `--domain-name, --auth-code-file` |
| `sav domains set-auto-renewal` | `update_domain_auto_renewal` | GET | write | `--domain-name, --enabled` |
| `sav domains set-sale-price` | `update_domain_for_sale_price` | GET | write | `--domain-name, --sale-price` |
| `sav domains set-nameservers` | `update_domain_nameservers` | GET | write | `--domain-name, --ns-1, --ns-2` |
| `sav domains set-privacy` | `update_domain_privacy` | GET | write | `--domain-name, --enabled` |
| `sav domains set-whois-contacts` | `update_domain_whois_contacts` | GET | write | `--domain-name, --name, --organization, --email-address, --street, --city, --country, --phone, --state, --postal-code, --update-registrant, --update-tech, --update-admin` |
| `sav domains list-external-sale` | `list_external_domain_for_sale` | GET | write | `--domain-name, --sale-price` |

## Scope

- The four commands marked `read` are treated as read operations for runtime safety.
- The eight commands marked `write` are still mapped from GET methods in the official docs, but are treated as writes in runtime safety policy.
- No generic path-command bridge is shipped; only the fixed commands listed above are exposed.

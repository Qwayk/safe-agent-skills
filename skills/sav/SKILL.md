---
name: sav
description: Use when the user wants to read SAV account domains, recent sales, or transaction pricing, or prepare and approve one of the documented SAV Domain APIs v1 changes.
---

Use this skill for the 12 operations in the official SAV Domain APIs v1 collection. Do not use it for domain registration, auction bidding, website automation, undocumented SAV endpoints, or arbitrary API calls.

Start with a read such as `sav domains active` or `sav pricing list`. If the user asks for a change, create and review the dry-run plan before discussing apply.

Core rules:
- Always run `--output json` unless caller requires another format.
- Never print secret-like values (API key, auth code, WHOIS personal data).
- Reads require SAV access and may run directly. Changes always save a private plan; use `--plan-out` when a specific path is useful, then apply only from the reviewed `--plan-in`.
- Write apply always requires all: `--apply --yes --plan-in --ack-no-snapshot --ack-high-risk`.
- Plan state is `.state/` under the env-file directory with mode-`0700` directories for plans, receipts, and keys and mode-`0600` files.
- Plans are `schema_version: 2` and signed with HMAC-SHA256.
- `.state/keys/plan-hmac.key` is generated locally if missing and not shared.
- Transfer writes accept only `--auth-code-file` for dry-run; apply uses the saved plan and must not include a transfer code file or literal code.
- The transfer authorization code has no environment or literal command-line fallback.
- Keep transfer secret files in `.state/secrets`, mode-`0600`, and remove the temp file immediately after the dry-run.
- Never follow redirects. Treat every non-2xx provider response as a failure.
- Treat `provider_accepted` as a 2xx provider response only, not verified lasting account state.
- Treat `receipt_written` as local receipt persistence only. `durable_state_verified` remains false without independent readback.
- `provider_response_only` is true only when `provider_response_received` is true.
- If the apply outcome is unknown or the final receipt was not written (`receipt_written: false`), tell the user not to retry blindly.
- Require finite positive timeouts and strict domain and nameserver values before any provider request.
- Do not claim restore, rollback, or backup support for writes.
- Never use any path that exposes private workspace files in user-facing summaries.
- Say clearly that every write currently has no documented before-state snapshot, independent readback, rollback, or restore path.

Write flow examples:

```bash
sav --output json --env-file <env-file> --plan-out <plan-path> domains set-sale-price --domain-name example.com --sale-price 42
```

```bash
sav --output json --env-file <env-file> --apply --yes --ack-no-snapshot --ack-high-risk --plan-in <plan-path> --receipt-out <receipt-path> domains set-sale-price --domain-name example.com --sale-price 42
```

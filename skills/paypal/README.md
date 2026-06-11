# PayPal

Install slug: `paypal`

Use this skill when you want your AI agent to review PayPal orders, payments, payouts, invoices, webhooks, and other REST API work with clearer preview before live changes.

This is a safety-first CLI for the official PayPal REST APIs. Read commands run directly, and write commands default to preview-first. Current write apply requires explicit no-snapshot approval before PayPal auth or HTTP until command-specific saved snapshot support is available.

## For non-technical users: Start here (no coding)

Start with:

- [What you can do](docs/use_cases.md)
- [Connect your account](docs/onboarding.md)
- [How live changes stay safer](docs/safety_model.md)

## For technical users: Start here (CLI)

Full references:
- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [API coverage](docs/api_coverage.md)

Minimal examples:

```bash
qwayk-paypal-safe-agent-cli --version
qwayk-paypal-safe-agent-cli onboarding --no-write-env
qwayk-paypal-safe-agent-cli auth check
```

`auth check` needs a real PayPal app client ID and client secret in `.env`.
After that, a representative read looks like:

```bash
qwayk-paypal-safe-agent-cli orders get --id ORDER-ID
```

Plain-English examples:

- “Check that my PayPal app is connected, then list the API areas this tool can use.”
- “Show me one PayPal order and its current status.”
- “Create a dry-run preview for sending an invoice, then show the approval gate before any PayPal write.”
- “List my webhooks and show the event types on one webhook.”

Current API scope:

- Orders and order tracking
- Payments, refunds, and authorizations
- Vault setup tokens and payment tokens
- Shipping tracking
- Catalog products and subscriptions
- Invoicing
- Webhooks
- Partner, payouts, referenced payouts, and transaction reporting paths where PayPal documents them publicly

Important honesty note:

- Some PayPal areas are partner-gated, account-gated, or live-unverified in this build environment. The tool still ships the documented command surface, and the exact status is called out in [API coverage](docs/api_coverage.md) and [Proof pack](docs/proof.md).

## Proof pack (customer-ready)

- [Proof pack](docs/proof.md)
- [API coverage](docs/api_coverage.md)
- [Examples](docs/examples/)

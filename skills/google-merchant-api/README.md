# Google Merchant API Safe Agent CLI

This tool gives AI agents a safe, explicit, customer-ready way to work with the official Google Merchant API from a local machine.

## For non-technical users: start here (no coding)

- [Use cases](docs/use_cases.md)
- [Onboarding setup](docs/onboarding.md)
- [Safety model](docs/safety_model.md)

Plain-English requests you can give your agent:

- "Check whether my Merchant API access is ready."
- "Show me what Merchant actions this tool can do today."
- "Draft a safe preview to add one product input for account 123456."
- "Show me the proof from my last Merchant write."

## What ships in this release

- local helper commands: `onboarding`, `auth`, and `runs`
- `224` explicit Merchant commands across `19` official families
- stable `v1` families first (`12` families, `124` commands)
- official active `v1alpha` families that are still documented today (`98` discovery-backed alpha commands plus `2` reference-only alpha commands)
- `docs/api_coverage.md` lists every official documented Merchant operation, including what ships and what is only accounted for

This tool does not ship API-key auth. Own-account access uses service accounts. Client-account access uses OAuth 2.0.

Current write behavior: write commands still generate dry-run plans, and live Merchant writes require explicit no-snapshot approval before credentials or provider HTTP when no saved snapshot is available.

The committed proof in this repo is honest but not fully live-proved yet in this exact workspace. See `docs/proof.md` for the current live vs local boundary.

## For technical users: start here (CLI)

- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [Proof pack](docs/proof.md)

Example commands:

- `google-merchant-api-tool --output json auth check`
- `google-merchant-api-tool --output json accounts list`
- `google-merchant-api-tool --output json accounts product-inputs insert --parent accounts/123456 --body-json '{"channel":"ONLINE","contentLanguage":"en","offerId":"SKU-RED-123","feedLabel":"US"}'`
- `google-merchant-api-tool --output json --apply accounts product-inputs insert --parent accounts/123456 --body-json '{"channel":"ONLINE","contentLanguage":"en","offerId":"SKU-RED-123","feedLabel":"US"}'` stops safely when required approval is missing; with the required no-snapshot approval, supported writes can proceed and produce a receipt.
- `google-merchant-api-tool --output json --apply --yes --plan-in reviewed-plan.json --ack-irreversible accounts conversion-sources delete --name accounts/123456/conversionSources/abc`

## Safety at a glance

- writes are dry-run by default
- write plans mark before-state capture as required and currently unsupported
- `--apply` write attempts require explicit no-snapshot approval before provider HTTP when no saved snapshot is available
- high-risk and irreversible writes still require `--apply --yes --plan-in` before reaching the no-snapshot approval gate
- `DELETE` applies also require `--ack-irreversible`
- local run folders save plans, approval-gate audit logs, and summaries under `.state/runs/`

## Naming decision

The customer-facing skill wrapper uses the requested name `google-merchant-api-safe-cli`.

The internal Python package and console command stay `google_merchant_api_tool` and `google-merchant-api-tool` in this release on purpose. That was kept as an intentional compatibility choice so the customer-ready repo does not break its import paths, console entry point, tests, or committed proof examples in one large rename. The decision is tracked in `docs/engineering_notes.md` and the workspace memory files. Any future rename should be handled as an explicit breaking-change slice, not as silent drift.

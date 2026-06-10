# Command reference

Use this page when you need the exact Amazon Creators command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags

- `--output` (json | text): default is `json`.
- `--env-file <file>`: point to `.env` (defaults to `.env`).
- `--apply`:
  - For catalog commands: switch from dry-run plan to live API call.
  - For local write helpers (`onboarding`, `auth token set`, `auth token fetch`): attempts the helper, then requires explicit no-snapshot approval before local writes when no saved snapshot is available.
- `--no-artifacts`: opt out of writing `.state/runs/` metadata (audit logs, plans, receipts, and the runs index stay disabled) while leaving dry-run vs `--apply` behavior unchanged.
- `--yes`: parsed for future write workflows; not required for current catalog reads or local write helpers.
- `--plan-out <path>`: catalog commands write the dry-run plan JSON to this file.
- `--receipt-out <path>`: catalog commands write the apply receipt JSON to this file when `--apply` is used; blocked local helper applies do not create a success receipt.
- `--plan-in <path>` is reserved for future apply-from-plan flows and currently has no effect.
- `--ack-irreversible`: parsed for future irreversible actions; currently not used by shipped commands.
- `--run-id`, `--artifacts-dir`, `--log-file`: control run history and audit logging.

## Onboarding

- `amazon-creators-api-tool onboarding [--no-write-env] [--apply]`: prints required env setup. If `.env` is missing, confirmed apply now requires explicit no-snapshot approval before creating it when no saved snapshot is available.

## Authentication

- `amazon-creators-api-tool auth check`: validates env vars and token status; this command is local-only.
- `amazon-creators-api-tool auth token fetch [--force]`: creates a dry-run token-cache plan.
- `amazon-creators-api-tool auth token fetch --apply [--force]`: requires explicit no-snapshot approval before token endpoint use or `.state/token.json` writes when no saved snapshot is available.
- `amazon-creators-api-tool auth token status`: shows token metadata from `.state/token.json` without token values.
- `amazon-creators-api-tool auth token set --file <token.json>`: creates a dry-run token-cache plan.
- `amazon-creators-api-tool auth token set --file <token.json> --apply`: requires explicit no-snapshot approval before `.state/token.json` writes when no saved snapshot is available.

## Run history

- `amazon-creators-api-tool runs list [--limit N]`: list recent run records for a given `.env`.
- `amazon-creators-api-tool runs show --run-id <id>`: inspect one run entry and its summary.

## Catalog operations

The four public catalog operations are mapped to explicit commands with deterministic selectors and locale-aware resource expansion:

- `--resource <name>`: request one of the eight high-level resources (BrowseNodeInfo, BrowseNodes, Images, ItemInfo, OffersV2, ParentAsin, SearchRefinements, VariationSummary). Repeatable or comma-separated.
- `--resource-preset <preset>`: use one preset (`book-media`, `browse-basic`, `search-lens`, `inventory-view`, `full`). Presets are merged before explicit `--resource` values and validated per command. Defaults:
  - `browse-basic` for `browse-nodes describe`
  - `book-media` for `items get` and `variations get`
  - `search-lens` for `search`
- `--locale <code>`: override `AMAZON_CREATORS_LOCALE` for request shaping.
- `--include-raw`: include the raw API payload alongside simplified output when `--apply`.

Catalog commands default to dry-run: the JSON output includes `dry_run: true`, a `plan` object, and `plan_out` when run artifacts are enabled or `--plan-out` is passed.
Add `--apply` to call Amazon for the read-only catalog request, set `dry_run: false`, and get simplified data plus a `receipt` and optional `receipt_out`.

### `browse-nodes describe`

- Purpose: call `GetBrowseNodes`.
- Required flags: `--browse-node-id <id>` (repeatable).
- Default resources: `browse-basic`.
- Output: simplified browse node rows under `browse_nodes`.

### `items get`

- Purpose: call `GetItems`.
- Required flags: `--item-id <ASIN|SKU>` (repeatable). Use `--item-id-type` for non-ASIN.
- Key outputs: simplified item rows under `items`.
- Add `--include-raw` for full request payload.

### `variations get`

- Purpose: call `GetVariations`.
- Required flags: `--asin <ASIN>` (repeatable; only first ASIN is used today). `--item-id` is accepted as an alias.
- Optional flags: `--variation-count` (1-10), `--variation-page` (>= 1).
- Output: simplified variation rows under `items`.

### `search`

- Purpose: call `SearchItems`.
- Required flag: `--keywords <query>`.
- Optional flags:
  - `--item-count` (1-10), alias: `--max-results`
  - `--item-page` (1-10), alias: `--page`
- Output: simplified search rows under `items`.

## Locale helpers

- `amazon-creators-api-tool locales list`: list supported locale codes and marketplace mappings.
- `amazon-creators-api-tool locales show --locale <code>`: show one locale entry.

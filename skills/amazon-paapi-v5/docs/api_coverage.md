# API coverage

Amazon Product Advertising API coverage shows exactly what the shipped commands can do with product lookup and browse-node research. Start here when an ask sounds possible but you need to know whether it is already shipped, read-only, plan-first, gated, excluded, or outside the tool.

Read the shipped command rows first, then check the excluded or not-yet-live rows before asking an agent to act. If an endpoint or workflow is not listed here, do not assume the skill supports it.

A good first coverage check is: "Check whether the shipped commands can look up this ASIN, compare the returned product fields, and show which Product Advertising calls are not included."

## Coverage notes

Last updated (UTC): 2026-02-03

## Commands → PA-API

- `auth check`: Validates config/env and performs a PA-API request to confirm credentials.
- `product get`: `GetItems` (supports deterministic batching; see limits below)
- `product search`: `SearchItems`
- `product variations`: `GetVariations`
- `product resolve`: Local parsing only (no PA-API call).
- `browse get`: `GetBrowseNodes` (supports deterministic batching; see limits below)
- `link build`: Local link construction only (no PA-API call).
- `jobs run`: Executes a CSV job file and calls the same command handlers (read-only).

## Resource selection

PA-API requests accept a `Resources` array that controls which fields are returned.

- Use `--resources-preset basic` to use the command's default resources.
- Use `--resources-preset none` to disable defaults.
- Use `--resource <Name>` (repeatable) to add explicit resources; explicit resources are appended to the preset deterministically (deduped, stable order).
- Defaults are per-command (example: product commands include basic item fields by default; browse defaults to no resources unless you add them).

## Request limits (from official docs)

- `GetItems`: `ItemIds` up to 10 per request.
- `GetBrowseNodes`: `BrowseNodeIds` up to 10 per request.
- `GetVariations`: `VariationCount` max 10 per request (default 10); `VariationPage` is 1-based.

## Known non-coverage (intentional)

- Partner-only or account management workflows are out of scope for this CLI.

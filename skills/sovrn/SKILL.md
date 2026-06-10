# Sovrn Safe CLI

Use this skill when you need safe, explicit CLI access to the official Sovrn Commerce HTTP APIs or the official Sovrn Advertising Reporting APIs.

## What this skill is for

- Commerce campaigns, link checks, bid checks, reports, merchant groups, coupons, product recommendations, and price comparisons
- Advertising account, bid, breakout, domain, and custom reporting
- Deterministic read-only API calls with one JSON response

## Before you call the CLI

1. If auth readiness is unclear, run `sovrn-safe-cli auth check` first.
2. Pick the command family from `docs/api_coverage.md`.
3. Use only the shipped named commands. Do not invent endpoints and do not use a generic request bridge.

## Auth split to keep honest

- Commerce secret-header commands:
  - `commerce campaigns`
  - `commerce reports`
  - `commerce merchant-groups`
- Commerce site-key commands:
  - `commerce links`
  - `commerce products`
- Mixed Commerce commands:
  - `commerce coupons`
  - `commerce comparisons`
- Advertising commands:
  - `advertising reports`
  - These need both `SOVRN_ADVERTISING_API_KEY` and `SOVRN_ADVERTISING_PUBLISHER_ID`

## Good starting commands

- `sovrn-safe-cli commerce campaigns get --search PRIMARY`
- `sovrn-safe-cli commerce reports pages get --click-date-start 2026-01-01 --click-date-end 2026-01-02`
- `sovrn-safe-cli commerce products recommend --page-url article-123 --content "gift guide copy"`
- `sovrn-safe-cli advertising reports account get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions auction`

## When to refuse or redirect

- Refuse if the needed auth bundle is missing.
- Refuse if the ask is for a generic raw request or a browser-side JavaScript integration flow.
- Refuse if the ask depends on MCP beta pages as if they were shipped CLI coverage.
- Refuse if the user asks for a write workflow that the official shipped surface does not support yet.

## Notes

- `auth check` is local-config-only. Use the real read commands for live vendor proof.
- Coupons are official but access-gated by Sovrn registration.
- The current shipped surface is read-only even when an endpoint uses `POST`.

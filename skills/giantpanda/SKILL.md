---
name: giantpanda
description: Read GiantPanda domain stats and prepare bounded add plans with explicit approval gates before any live write.
---

# GiantPanda

This is the agent rule sheet for the `giantpanda` CLI in `qwayk-giantpanda-safe-agent-cli`.
The tool is source-anchored to a fixed API host and a token-based auth flow.

## Use this skill when

- You need official GiantPanda domain parking stats with date ranges.
- You need safe paging through stats results.
- You need to prepare a review plan for adding domains (up to 100 at a time).

## Do not use this skill for

- DNS, payout, transfer, registration, billing, setup UI, or dashboard operations.
- Any undocumented GiantPanda route or unknown host.
- Unsafely sending a write request without a reviewed plan.

## Safer first action

1. `giantpanda onboarding` only if local setup is missing.
2. `giantpanda --output json auth check` (local readiness).
3. `giantpanda --output json domains stats --start-date <YYYY-MM-DD> --end-date <YYYY-MM-DD>`.

`domains stats` is the first safe read and should be used before any write planning.

## Plan/apply flow

`domains add` is plan-first by default:

- Plan mode is local by default and writes a private `0600` plan file.
- Live apply requires all gates in one command:
  - `--apply`
  - `--plan-in <reviewed-plan.json>`
  - `--approve-plan <exact_plan_id>`
  - `--ack-no-snapshot`
- The exact host, endpoint, plan id, and normalized domain list must match.
- Supply no more than `100` raw `--domain` values per command. The tool normalizes and removes duplicates inside that bound.

## Environment and identity

- Fixed host: `https://account.giantpanda.com`
- Fixed auth header: `Authorization: Token <GIANTPANDA_API_TOKEN>`
- Redirect responses are refused rather than followed.
- Source identity is explicit: `qwayk-giantpanda-safe-agent-cli`.
- Process environment values override the selected `--env-file`; neither path may expose the token.

## Safety limits

- No rollback, restore, or automatic undo for write operations.
- No provider-live readback flow is embedded in this tool for post-write verification.
- If provider parse fails on live write, stop there and review the account manually before retrying.
- Never ask to apply a domain add without explicit user approval of the reviewed local plan.

Stats authentication, account permission, and response shape are provider-live verified by one governor-owned installed-wheel request on 2026-08-11. It returned HTTP `200` and an object with top-level keys `end_date`, `pagination`, `start_date`, and `stats`; private values and the raw response were not saved. `domains add` remains `provider-live-unverified`: its provider response and live account effects are proved only with local and mocked checks, and the tool has no embedded post-write readback.

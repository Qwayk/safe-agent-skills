# Skill: Google Search Console (GSC) SafeCLI

This page is the agent-facing rule sheet for the public Google Search Console skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

This skill uses the local CLI `gsc-api-tool` to work with the Google Search Console API v1 safely.

## Safety contract (must follow)

- Never ask the user to paste secrets into chat.
- For any write-capable method, run a dry-run first (no `--apply`) and present the plan for review.
- Only apply after explicit approval.
- Deletes are irreversible and require `--apply --yes --ack-irreversible --plan-in`.
- After applies, surface the receipt and verification result.
- The plan and receipt must carry `recovery.end_state` and `before_state`.
- Expected values: `sites add`, `sitemaps submit` -> `rollback_by_inverse_action`; `sites delete`, `sitemaps delete` -> `irreversible_and_clearly_labeled`.

## Preflight (every session)

1) Verify the CLI runs (no `.env` required):
- `gsc-api-tool --output json --version`

2) If setup is unknown, run onboarding and stop:
- `gsc-api-tool --output json onboarding`

3) After the user completes setup, validate auth (read-only, no token values):
- `gsc-api-tool --output json auth check`

## Core capabilities (explicit commands only)

Inventory/coverage:
- `gsc-api-tool --output json operations validate`
- `gsc-api-tool --output json operations list`

Read-like methods:
- `gsc-api-tool --output json sites list`
- `gsc-api-tool --output json sitemaps list --site-url https://example.com/`
- `gsc-api-tool --output json searchanalytics query --site-url https://example.com/ --body-json '{\"startDate\":\"2026-03-01\",\"endDate\":\"2026-03-05\",\"dimensions\":[\"query\"]}'`
- `gsc-api-tool --output json url-inspection index inspect --body-json '{\"inspectionUrl\":\"https://example.com/\",\"siteUrl\":\"sc-domain:example.com\"}'`

Write methods (plan → apply):
- Plan (default):
  - `gsc-api-tool --output json --run-id 2026-03-05T000000Z_example sites add --site-url https://example.com/`
- Apply (requires approval):
  - `gsc-api-tool --output json --apply sites add --site-url https://example.com/`
- Plan/receipt should show the expected recovery contract fields:
  - `plan.recovery.end_state`
  - `receipt.recovery.end_state`
  - `plan.before_state`
  - `receipt.before_state`

Deletes (irreversible; extra gates):
- Plan:
  - `gsc-api-tool --output json --run-id 2026-03-05T000000Z_example --plan-out plan.json sites delete --site-url https://example.com/`
- Apply:
  - Review the saved plan file, then run:
  - `gsc-api-tool --output json --apply --yes --ack-irreversible --plan-in plan.json sites delete --site-url https://example.com/`

## Refusal rules

Refuse (safe no-op) when:
- Required flags are missing (example: `--site-url`).
- Credentials are missing and the user has not completed onboarding/login.
- A delete apply is requested without the required acknowledgement flags and `--plan-in`.

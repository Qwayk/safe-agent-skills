# Skills wrappers

## When to use this skill

- Read GiantPanda domain parking traffic by date window.
- Inspect additional stats pages.
- Build a local `domains add` plan before any live action.

## When not to use this skill

- DNS, transfers, registrations, billing, payout, setup, or dashboard actions.
- Any request outside `GET /api/v1/domains/stats/` or `POST /api/v1/domains/add/`.
- Calls that ask for undocumented routes.

## Safest first action

1. `onboarding`
2. `auth check`
3. `domains stats --start-date <YYYY-MM-DD> --end-date <YYYY-MM-DD>`

`onboarding` is only required if setup is missing. `auth check` is local-only.

## Plan and apply safety rules

- `domains add` defaults to dry-run plan output.
- Apply needs all exact gates:
  - `--apply`
  - `--plan-in <plan_path>`
  - `--approve-plan <exact_plan_id>`
  - `--ack-no-snapshot`
- Refuse apply if any gate is missing, if plan metadata drifts, or if domain count changes.
- Max add size is 100 domains.

## Fixed host and behavior

- Fixed host is always `https://account.giantpanda.com`.
- Auth header uses fixed format `Authorization: Token <GIANTPANDA_API_TOKEN>`.
- Redirects are disabled and refused.

## Provider behavior and limits

- HTTP errors (including status failures) are returned only after a request is sent.
- There is no local rollback, restore, or undo path for write applies.
- Token and auth values are never written to logs.
- Provider stats are printed in the command result and must be treated as private. Saved plans and receipts use mode `0600`; receipts keep the provider verification response but never the token or authorization header.

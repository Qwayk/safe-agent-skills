# GiantPanda

This tool helps you review traffic and earnings for your parked GiantPanda domains and prepare new domains for the account.

You can ask your agent to show requests, queries, clicks, revenue, RPM, and CTR for a date range, move through result pages, or prepare a domain-add plan.

For example: "Show me stats from 2026-08-01 to 2026-08-07," "Get page 2 of that period," or "Prepare a plan to add a small list of new domains."

Stats reads can run after input and token checks. A domain add starts as a local plan with no provider request, then waits for approval before anything is sent live.

## Start here first

Run onboarding only when local setup is missing. Then confirm local token readiness and request one short stats window.

```bash
giantpanda onboarding
giantpanda --output json auth check
giantpanda --output json domains stats --start-date 2026-08-01 --end-date 2026-08-07
```

## What your agent can do

- Read domain parking stats from official windows using `domains stats`.
- Paginate through additional stats with `--page` and `--page-size`.
- Build a local `domains add` plan for up to 100 domains.
- Keep token checks and local readiness explicit through `auth check`.

## What happens before live changes

1. `auth check` verifies local readiness and is local-only.
2. `domains add` without `--apply` creates a local plan and does not call the API.
3. For live apply, the tool refuses until all exact gates are present in one command:
   - `--apply`
   - `--plan-in <reviewed-plan-path>`
   - `--approve-plan <exact-plan-id>`
   - `--ack-no-snapshot`
4. The plan path and IDs are checked against the live request shape before sending anything.

## What access this tool needs

- `GIANTPANDA_API_TOKEN` in `.env` or env vars.
- Access to fixed API host `https://account.giantpanda.com`.
- The tool can read and prepare writes only for:
  - `GET /api/v1/domains/stats/`
  - `POST /api/v1/domains/add/`
- Auth values are kept local and are not persisted in outputs.

## Install and first run

Install slug: `giantpanda`

If needed:

```bash
npx skills add Qwayk/safe-agent-skills@giantpanda -g -y
```

Then start with:

```text
Check local GiantPanda setup readiness, then show stats from 2026-08-01 to 2026-08-07.
```

## What it covers today

- Auth readiness: `auth check`
- Onboarding and local setup: `onboarding`
- Read stats: `domains stats`
- Domain add plans: `domains add` (dry run by default, reviewed local plan before apply)
- Official fixed-host coverage is listed in [API coverage](docs/api_coverage.md)

## Limits

- Only the two official GiantPanda operations above are in scope.
- Domain add supports a strict max of 100 domains per plan.
- No domain setup, payouts, transfers, registrations, DNS, or billing actions.
- There is no rollback/restore/undo flow for `domains add`.
- Live apply proof is provider-response based; this tool does not claim extra provider-side verification.

## Helpful docs

- [Docs landing page](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [Safety model](docs/safety_model.md)
- [Use cases](docs/use_cases.md)
- [API coverage](docs/api_coverage.md)
- [Proof and verification](docs/proof.md)

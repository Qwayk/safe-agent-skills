# Make.com API

**Capability:** Read Make.com account state and prepare safe, reviewed API actions.

This tool helps an agent answer operational questions first, then apply changes only after explicit review.

A useful first ask is:

`Show me active scenarios and team users, then explain any risky items before any change.`

## Start here first

- Read `docs/onboarding.md` for setup flow.
- Open `docs/quickstart.md` for the fastest first command set.
- Use `docs/use_cases.md` for real request phrasing.
- When you need exact syntax, jump to `docs/command_reference.md`.

## What this skill helps with

- Audit Make resources before editing anything.
- Review team access, scenario status, hooks, keys, data stores, and related control-plane settings.
- Build and keep reviewed write plans before writes happen.
- Keep a repeatable trail of plans, receipts, run IDs, and logs.

## Why this skill is different

Generic API calling often misses safe boundaries. This tool uses explicit Make API operations only, from official Make docs, and blocks direct free-form calls.

Reads can run directly. Writes are review-first:

- produce a plan,
- review the plan,
- apply only with explicit confirmation flags.

## What access this skill needs

- `MAKE_BASE_URL` (for example `https://eu1.make.com`)
- `MAKE_API_TOKEN` (personal token or service token)
- Optional: `MAKE_TIMEOUT_S` and `MAKE_ZONE_URL` (legacy alias).

The CLI sends token auth as `Authorization: Token <value>`.

## Install and first run

From source:

```bash
python3 -m pip install -e .
make-com-safe onboarding --output text
make-com-safe --output json auth check
```

If your environment uses an internal skill flow, install and configure from your internal control flow the same way; keep `.env` local-only.

## How this skill stays safe

- Read operations are direct and fast.
- Write operations are always dry-run first unless `--apply` is used.
- High-risk writes require `--plan-in --apply --yes`.
- If an operation is marked no-snapshot, `--ack-no-snapshot` is required.
- Secret fields are redacted in output, logs, and receipts.

## What it covers today

- Official coverage is sourced from the pinned Make Developer Hub inventory: `376` operations across `59` families.
- Command surface is mapped directly from that inventory via `api list`, `api schema`, and `api <family> <operation>`.
- No unsupported one-off endpoint bridge is exposed.

## What happens before live changes

1. The write command returns a plan JSON when not applying.
2. The user reviews operation, method, target IDs, and request body.
3. Apply requires the reviewed plan with the required flags.
4. On apply, a receipt is emitted for audit and follow-up.

## Limits

- Live Make account behavior remains unverified until credentials are used with safe targets.
- `api list` and `api schema` show what is officially declared, but not all Make API behavior is guaranteed by this tool.
- This tool is not a Make MCP setup wrapper and does not expose raw generic proxy commands.

## Helpful docs

- [docs/README.md](docs/README.md)
- [docs/quickstart.md](docs/quickstart.md)
- [docs/command_reference.md](docs/command_reference.md)
- [docs/safety_model.md](docs/safety_model.md)
- [docs/api_coverage.md](docs/api_coverage.md)
- [docs/proof.md](docs/proof.md)

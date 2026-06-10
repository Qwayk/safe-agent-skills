# stripe-api-tool

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

This is a safety-first CLI for Stripe’s API, designed for AI agents and non-technical users.

It is “plan-first” by default: generate a deterministic plan and review it before any live action. Live reads can run with `--live`; live API writes require explicit no-snapshot approval before Stripe HTTP when no saved snapshot or provider backup is available.

## For non-technical users: Start here (no coding)

Start with:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`
- Skills wrappers (required for customer-ready tools): `docs/skills_wrappers.md`

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`

Minimal examples:

```bash
stripe-api-tool --version
stripe-api-tool auth check
```

## How to pick an operation

Stripe’s API surface is large. This tool pins an official OpenAPI snapshot and exposes one explicit CLI command per operation.

Start with:
- `stripe-api-tool inventory validate` (proves the pinned inventories are consistent)
- `docs/official_commands_2026-02-25.clover_2026-03-05.txt` (the canonical list of `api ...` commands)

Then run one dry-run plan for your operation:
- `stripe-api-tool api <operation> ...` (plan-only)

To execute read-only network calls, add `--live`. Write-like API commands still generate plans. When no saved snapshot or provider backup exists, approved supported writes require explicit no-snapshot approval and receipts must record the recovery limit. See `docs/safety_model.md`.

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`

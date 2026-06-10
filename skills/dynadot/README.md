# dynadot-api-tool

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

Status: **100% Dynadot API3 command coverage from official request examples** (via `api3/`) + safe bulk workflows (push, name servers set, guided transfer run).
See `docs/progress.md`.

This is a customer-ready, safe-by-default CLI for the Dynadot API (API3).
It is designed for bulk workflows (hundreds to thousands of domains) with a strict safety loop: plan -> review -> explicit no-snapshot approval when no saved snapshot is available.
It also includes read-only lookup commands for operational visibility (contacts, DNS, transfers, orders, marketplace listings, auctions, closeouts, backorders, CN audit status).
Write dry-runs still produce reviewable plans, but live Dynadot writes need explicit no-snapshot approval after the normal gates and before Dynadot HTTP when the tool cannot save real before-state.

## For non-technical users: Start here (no coding)

Start with:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`
- Progress tracking (what’s done / next): `docs/progress.md`

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`

Minimal examples:

```bash
dynadot-api-tool --version
dynadot-api-tool onboarding
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`

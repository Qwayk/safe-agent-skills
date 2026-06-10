# zendesk-api-tool

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

Safety-first CLI for the Zendesk Support (Ticketing) API.

This tool is designed for plan-first work. Reads can run with `api --live`; write operations generate deterministic plans, and live apply needs snapshot support, stub-safe receipts, or explicit no-snapshot approval before Zendesk HTTP.

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
zendesk-api-tool --version
zendesk-api-tool auth check
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`

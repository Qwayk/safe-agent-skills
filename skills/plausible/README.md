# plausible-api-tool

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

Small, safe CLI for the Plausible Analytics **Stats API** and **Events API**.

Designed to be safe-by-default (dry-run, explicit apply gates, and machine-readable output).

## Docs

## For non-technical users: Start here (no coding)

Start with these docs:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`

What you can ask an AI agent to do (examples):

- “Give me a weekly traffic report (top pages, sources, and goals).”
- “Build a membership funnel report for the last 30 days.”
- “Validate this Stats query JSON and then run it.”
- “Send a test event only if I explicitly approve (writes analytics).”

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`

Minimal examples:

```bash
plausible-api-tool --version
plausible-api-tool --env-file .env auth check
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`

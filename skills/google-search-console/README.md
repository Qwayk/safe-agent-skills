# gsc-api-tool (Google Search Console SafeCLI)

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

This is a safety-first CLI for the **Google Search Console API v1**, designed for non-technical users working with an AI agent.
Writes are preview-first (dry-run plan by default), and destructive actions have extra safety gates.

## For non-technical users: Start here (no coding)

Start with:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`

Minimal examples:

```bash
gsc-api-tool --version
gsc-api-tool onboarding
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`

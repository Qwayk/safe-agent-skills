# openai-api-tool

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

This is a safe-by-default CLI for the OpenAI API. It is plan-only by default and requires explicit flags to make live API calls. Current write operations create reviewable plans, then require explicit no-snapshot approval before OpenAI HTTP until command-specific saved snapshot support is available.

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
openai-api-tool --version
openai-api-tool onboarding
```

Every plan, read receipt, and refusal artifact is sanitized so Authorization headers, API keys, and tokens never appear in stdout or saved JSON outputs.

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`

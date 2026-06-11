# gtm-api-tool (Google Tag Manager API v2)

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

Customer-ready, safety-first CLI for the Google Tag Manager API v2.

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
gtm-api-tool --version
gtm-api-tool auth check
```

## Proof pack (customer-ready)

- Write plans and receipts now show recovery for write methods as either `rollback_by_inverse_action` or `irreversible_and_clearly_labeled`.
- `docs/proof.md`
- `docs/api_coverage.md`

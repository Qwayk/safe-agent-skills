# mercury-api-tool

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

Safety-first, read-only Mercury API v1 CLI designed for AI agents and non-technical users.

Scope:
- Mercury API v1 GET endpoints (refuses non-GET by design).
- Safe local exports (JSON/CSV) and downloads (PDFs) gated behind `--apply` (and `--yes` for overwrite).

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
mercury-api-tool --version
mercury-api-tool auth check
mercury-api-tool accounts list
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`

## Skills wrapper

- `skills/mercury-api-safe-cli/SKILL.md`
- `docs/skills_wrappers.md`

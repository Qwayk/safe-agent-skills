# ga4-api-tool

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

Safety-first CLI for Google Analytics (GA4), based on pinned discovery snapshots.

Key properties:
- Explicit commands only (one CLI command per discovery method)
- Dry-run by default for write-like discovery methods (prints a plan; no network)
- Apply requests still enforce risk gates (`--yes`, `--plan-in`, `--ack-irreversible`), then require explicit no-snapshot approval before GA4 HTTP until before-state capture exists
- Write plans are explicitly no-recovery and include `before_state.required=true`, `before_state.supported=false`
- Plans, refusals, and audit logs are redacted (Measurement Protocol `secretValue` is always redacted)

## For non-technical users: Start here (no coding)

Start with:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`
- Agent skill prompt and install notes are included with this package.

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`
- Full generated command list: `docs/official_commands.txt`

Minimal examples:

```bash
ga4-api-tool --version
ga4-api-tool auth check
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`

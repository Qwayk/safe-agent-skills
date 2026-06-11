# qdrant-cloud-api-tool

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

Customer-ready, safety-first CLI for the **Qdrant Cloud API**.

Key properties:
- Explicit named commands for every official RPC (no raw/generic request bridge).
- No network by default. Add `--live` to allow real HTTP calls.
- Ordinary writes are plan-first and currently require explicit no-snapshot approval before Qdrant Cloud HTTP until operation-specific before-state or provider-backup capture exists.
- Provider backup/restore commands (`create-backup`, `restore-backup`, `create-cluster-from-backup`) remain explicit live workflows after the normal gates.

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

Minimal examples:

```bash
qdrant-cloud-api-tool --version
qdrant-cloud-api-tool onboarding
qdrant-cloud-api-tool --output json auth check
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`

# amazon-pa-api-tool (Amazon PA‑API v5)

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

Read-only CLI for the Amazon Product Advertising API (PA‑API v5).

## For non-technical users: Start here (no coding)

Start with these docs:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`

What you can ask an AI agent to do (examples):

- “Find 20 candidate products for ‘X’ and give me a shortlist with titles and images.”
- “Resolve these Amazon URLs into ASINs and build clean affiliate links.”
- “Create a batch job from my spreadsheet and produce a report of results.”

## Scope and safety (by design)

- This tool is **read-only** to Amazon APIs.
- `--apply` exists for consistency across tools but does not enable external writes here.

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`

Minimal examples:

```bash
amazon-pa-api-tool --version
amazon-pa-api-tool auth check
amazon-pa-api-tool product search --query "test" --limit 1
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`

## Agent skill prompt

If you use an agent runtime that supports “skills” (example: Codex), this tool ships a minimal safe wrapper:

- Agent skill prompt and install notes are included with this package.

# freepik-api-tool

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

Safe, reusable Freepik API CLI, designed for **preview-first** workflows and **license-ledger** downloads.

## For non-technical users: Start here (no coding)

Start with these docs:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`

What you can ask an AI agent to do (examples):

- “Find 30 non‑AI recipe photos for ‘X’, show me previews, and let me pick the final IDs.”
- “Prepare a safe dry-run plan for the IDs I approved, and show what live license/download approval would still require.”
- “Generate a license ledger export for my accountant/audit trail.”
- “Preview a batch download job from my spreadsheet; apply only after I approve.”

Core safety rules (high level):

- Preview-first: search/preview → explicit approval → dry-run download plan
- Downloads are dry-run by default, and current apply requires explicit no-snapshot approval before the licensed download endpoint when no saved snapshot is available.
- Audit-friendly: future inventory ledger + checksums when licensed download apply is enabled safely.

## Scope and permissions (by design)

This tool is designed for safe asset discovery and licensed downloads:

- Search and resource inspection are read-only.
- Downloads are treated as high-signal actions. Current apply needs explicit no-snapshot approval before the Freepik download/license endpoint.

Least-privilege recommendation:

- Use a dedicated API key for this tool.
- Prefer separate keys for testing vs production workflows.

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`

Minimal examples:

```bash
freepik-api-tool --version
freepik-api-tool auth check
freepik-api-tool search images --query "test" --limit 1
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`

## Agent Skills wrapper

- `docs/skills_wrappers.md`
- `skills/freepik-api-safe-cli/SKILL.md`

## Docs

See:
- `docs/README.md`
- `docs/recipe_workflow_recipes.md` (recipe images: non‑AI + “discover similar”)

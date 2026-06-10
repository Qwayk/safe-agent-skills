# Pinterest API tool (read-mostly v1)

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

Safe CLI for Pinterest API v5 operations:
- Inventory: boards, board sections, pins, board pins
- Ads (read-only): ad accounts, campaigns, ad groups, ads, aggregated analytics
- Catalogs (read-only): catalogs, feeds, feed processing results, product groups, product group products, item issues, reports/stats
- Analytics: account + top pins + pin analytics (if your scopes allow it)
- Audit snapshot: writes JSON files locally (no Pinterest writes)
- Pin link hygiene: plan link canonicalization; confirmed apply currently requires explicit no-snapshot approval before Pinterest writes when no saved snapshot is available

## For non-technical users: Start here (no coding)

Start with these docs:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`

What you can ask an AI agent to do (examples):

- “Audit my Pinterest account and export a snapshot (boards, pins, sections) to a folder.”
- “Show me my top pins and basic analytics (if my account/scopes allow it).”
- “Plan a ‘pin link cleanup’ for these pins and show me the preview.”

Core safety rules (high level):

- Read-mostly: inventory and audits do not write to Pinterest.
- Write surfaces are plan-first right now: dry-run plans are reviewable, and confirmed apply attempts require explicit no-snapshot approval before provider writes or successful receipts when no saved snapshot is available.

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`

Minimal examples:

```bash
pinterest-api-tool --version
pinterest-api-tool auth check
pinterest-api-tool boards list --limit 1
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`

## Skills wrapper

- `skills/pinterest-api-safe-cli/SKILL.md`
- `docs/skills_wrappers.md`

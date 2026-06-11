# msads-api-tool

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

Safety-first CLI for the Microsoft Advertising API (Microsoft Ads) v13.

Design goals:
- Explicit commands: one named CLI command per v13 service operation (no generic/raw request bridge).
- No network by default: live API calls require `--live`.
- Dry-run by default: write-like operations create plans, but current write applies require explicit no-snapshot approval before SOAP HTTP until safe before-state capture exists.

## For non-technical users: Start here (no coding)

Start with:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`
- Agent skill prompt and install notes are included with this package.
- Coverage ledger (“100%” mapping): `docs/api_coverage.md`

Examples of what you can ask your agent (plain English, no commands):

- “Estimate keyword volume and suggested bids for these keywords, then export the results.”
- “Pull my account performance metrics report for the last 30 days and save it as JSON.”
- “Find Microsoft Ads recommendations that are safe to review, then show me a preview plan and the approval gate for a real write attempt.”
- “Bulk-edit campaign and ad group names from this spreadsheet, with a dry-run preview and proof that no write was sent yet.”
- “Download my campaigns and keywords to a file so we can analyze them offline.”

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`

Minimal examples:

```bash
msads-api-tool --output json --version
msads-api-tool onboarding
msads-api-tool --output json --live auth check
msads-api-tool --output json campaign-management get-campaigns-by-account-id --request-json request.json
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`

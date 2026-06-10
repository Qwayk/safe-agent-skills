# ghost-api-tool

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

`ghost-api-tool` is a safety-first CLI for managing content, members, and site data through the **Ghost Admin API**.
It also supports read-only access to public content via the **Ghost Content API** (no Admin key required).

## For non-technical users: Start here (no coding)

Start with these docs:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`

What you can ask an AI agent to do (examples):

- “Audit my site and tell me what looks risky or inconsistent (tags, authors, broken links, missing metadata).”
- “Export a report of posts and email delivery stats so I can see what performed.”
- “Export member engagement (and keep emails redacted unless I explicitly approve otherwise).”
- “Find internal linking gaps and generate a report (no changes).”
- “Preview a safe cleanup of unused tags; apply only after I approve.”

Core safety rules (high level):

- Preview-first: dry-run → explicit apply → verification
- Refuse when unsure (no guessing)
- Audit-friendly: plans/receipts/logs + backups for write workflows

Supported areas (high level):
- Posts/pages (including copy + safe patch workflows)
- Tags (audit + cleanup + create/update)
- Membership tiers + offers (create/update)
- Themes (upload + high-impact activation with extra safety)
- Webhooks (create/update/delete with local receipts; secrets redacted)
- Public content reads (Content API): posts/pages/tags/authors/tiers/settings (read-only)

## Scope and permissions (by design)

This tool focuses on **content + membership + site reporting workflows**.

Least-privilege recommendations:

- Create a dedicated Ghost **Custom Integration** for this tool (instead of using personal keys).
- Use staging first for risky workflows.
- Don’t paste keys into chat; keep them only in your local `.env`.

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`

Minimal examples:

```bash
ghost-api-tool --version
ghost-api-tool auth check
ghost-api-tool post find --limit 1
ghost-api-tool content settings get
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`

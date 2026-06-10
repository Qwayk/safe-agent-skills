# wordpress-api-tool

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

`wordpress-api-tool` is a safety-first CLI for managing content through the **WordPress REST API**.

## For non-technical users: Start here (no coding)

Start with these docs:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (safe setup + what to ask your agent): `docs/onboarding.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`

What you can ask an AI agent to do (examples):

- “Find all posts mentioning ‘X’ and give me a report with links, status, and last modified date.”
- “Show me which posts have missing featured images.”
- “Preview how you would set categories/tags on a specific post, then apply only after I approve.”
- “Bulk update image captions/alt text from my spreadsheet, but show me a preview first.”
- “Plan a bulk download of media files to my computer (including filenames/paths), then only download after I approve.”
- “Preview how you would update visible image captions inside a specific post, then apply only after I approve.”
- “Generate a migration tracking CSV from my WordPress export XML.”

Core safety rules (high level):

- Preview-first: dry-run → explicit apply → verification
- Refuse when unsure (no guessing edits)
- Audit-friendly: plans/receipts/logs for review

## Scope and permissions (by design)

This tool is intentionally focused on **content + migration workflows**, not full site administration.

In scope:
- Posts/pages reads (including drafts when authorized)
- Media Library reads + metadata edits (caption/alt/title)
- Read-only reads for common site objects (comments, taxonomy terms like categories/tags, search results)
- Optional read-only admin surfaces when authorized (users, settings)
- Targeted post edits where the tool can be deterministic (example: Gutenberg `wp:image` caption edits)
- Migration helpers (example: generate tracking from WordPress export XML)

Out of scope (or intentionally kept read-only):
- Plugin/theme management, site health, templates/global styles, widgets/sidebars, menus/navigation
- Site-wide settings writes and other high-risk operational controls

Least-privilege recommendation:
- Create a dedicated WordPress user for this tool and generate an Application Password for that user.
- Avoid using an Administrator account. Use the minimum role that can do the job (often **Author** or **Editor**, depending on which posts you need to access/edit).

## For technical users: Start here (CLI)

If you want the full command list, see:
- `docs/quickstart.md`
- `docs/command_reference.md`

Minimal examples:

```bash
wordpress-api-tool --version
wordpress-api-tool auth check
wordpress-api-tool post find --query "test" --limit 1
```

## Docs

Non-technical:
- Use cases (examples): `docs/use_cases.md`.
- Onboarding (setup): `docs/onboarding.md`.

Technical references:
- Start here: `docs/quickstart.md` and `docs/command_reference.md`.

Customer-ready proof pack: `docs/proof.md` with API coverage and committed redacted examples.

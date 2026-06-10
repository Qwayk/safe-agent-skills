# unsplash-api-tool

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

Customer-ready CLI for the Unsplash API (photos-first) using an **Access Key** (Client‑ID auth).

## For non-technical users: Start here (no coding)

Start with these docs:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`

What you can ask an AI agent to do (examples):

- “Find 30 photos for ‘X’ with a consistent style, and give me a shortlist.”
- “Prepare a download plan for the final approved photos and report the current approval gate.”
- “Confirm Unsplash download tracking is not called when no saved snapshot is available.”
- “Build a small ‘image pack’ for a page: 1 hero + 3 supporting images.”

## Scope and safety (by design)

Scope:
- Photos: list/get/random/search/statistics + download tracking planning.
- Discovery endpoints that support photo workflows: collections/topics/users/search (read-only).

Out of scope:
- OAuth/Bearer token flows (example: `GET /me`, like/unlike endpoints).
- OAuth write endpoints and any provider write beyond download tracking.

Safety model (high level):
- Read-only commands are safe by default.
- `photos download` is write-capable (tracking + optional file write):
  - Dry-run default: emits a plan and performs no tracking / no file writes.
  - Current apply mode: requires `--apply` (and `--yes` when overwriting), then requires explicit no-snapshot approval before the tracking endpoint and before local file writes when no saved snapshot is available.

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`

Minimal examples:

```bash
unsplash-api-tool --version
unsplash-api-tool auth check
unsplash-api-tool photos search --query "test" --per-page 1
unsplash-api-tool stats total
unsplash-api-tool --yes export photos-list --out export.json --start-page 1 --max-pages 2 --per-page 10
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`

## Skills wrapper

- `skills/unsplash-api-safe-cli/SKILL.md`
- `docs/skills_wrappers.md`

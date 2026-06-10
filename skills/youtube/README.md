# youtube-api-tool (YouTube Data API v3)

## Simplicity lock

Build and change this area in the simplest way possible.

- Use the simplest solution that solves the real need.
- Use one clear path and the fewest moving parts.
- Use the shortest clear code that solves the real problem safely.
- Remove before you add.
- Do not build optional flexibility first.
- Add modes, settings, or extra flows only after a real repeated failure proves they are needed.
- Prove each meaningful step with real testing or real evidence.

Safety-first CLI for the YouTube Data API v3.

Core properties:
- Deterministic, offline-friendly behavior by default (plan-only; no live API calls unless explicitly requested).
- Dry-run by default for any write-capable operation.
- Live reads for GET methods require `--live` (no `--apply` needed).
- Writes (non-GET), uploads, auth token writes, demo writes, and write jobs currently plan safely, then confirmed apply requires explicit no-snapshot approval when real before-state/provider-backup support is not available.
- Local audit artifacts under `.state/` (gitignored).

## For non-technical users: Start here (no coding)

Start with:

- Use cases (ideas + benefits): `docs/use_cases.md`
- Onboarding (setup + what to ask your agent): `docs/onboarding.md`
- Safety model (how we prevent mistakes): `docs/safety_model.md`
- Skills wrappers (required for customer-ready tools): `docs/skills_wrappers.md`

## For technical users: Start here (CLI)

Full references:
- `docs/quickstart.md`
- `docs/command_reference.md`

Minimal examples:

```bash
youtube-api-tool --version
youtube-api-tool methods list
youtube-api-tool --output json auth check
youtube-api-tool --output json channels resolve --channel @GoogleDevelopers
youtube-api-tool --output json channels export --channel @GoogleDevelopers --out-dir ./channel_export
youtube-api-tool --output json api search.list --params-json '{"part":"snippet","q":"cats","maxResults":5}'
```

## Proof pack (customer-ready)

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`

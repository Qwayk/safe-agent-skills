# bluesky-safe-cli

This is a safe CLI for Bluesky (atproto XRPC). API writes use a strict plan -> review -> explicit no-snapshot approval flow when real saved snapshots are not available.

## For non-technical users: Start here

- `docs/use_cases.md` (what this tool can do)
- `docs/onboarding.md` (setup, no coding)
- `docs/safety_model.md` (how mistakes are reduced)
- `docs/skills_wrappers.md` (how to use it as an agent skill)

## For technical users: Start here

- `docs/quickstart.md` (first successful run)
- `docs/command_reference.md` (commands and flags)

## Proof pack

- `docs/proof.md`
- `docs/api_coverage.md`
- `docs/examples/`

Minimal smoke commands:

```bash
bluesky-safe-cli --version
bluesky-safe-cli auth check
```

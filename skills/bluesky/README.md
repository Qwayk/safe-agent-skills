# bluesky-safe-cli

This is a safe CLI for Bluesky (atproto XRPC). API writes use a strict plan -> review -> explicit no-snapshot approval flow when real saved snapshots are not available.

## For non-technical users: Start here

- `docs/use_cases.md` (what this tool can do)
- `docs/onboarding.md` (setup, no coding)
- `docs/safety_model.md` (how mistakes are reduced)
- Agent skill prompt and install notes are included with this package.

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

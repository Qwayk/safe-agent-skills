# Proof and verification

## What is verified

- Official Make API inventory refresh loads `376` operations from `59` official Make API Reference endpoint pages.
- CLI command model has been aligned to the actual parser: `runs`, `onboarding`, `auth`, and `api`.
- The shipped `api` surface exposes explicit inventory-backed commands as `make-com-safe api <family> <operation>`.
- Write safety gates are documented from source logic:
  - plan-first behavior,
  - `--plan-in --apply --yes`,
  - `--ack-no-snapshot`,
  - `--ack-irreversible`.
- Apply validation checks the reviewed operation, base URL, credential fingerprint, target fingerprints, and request body hash.
- Stored command text redacts raw `--body-json` values, `--body-file` paths, and secret-looking `--path-param` / `--query` values before it reaches stdout plans, saved plans, run summaries, run indexes, audit logs, or receipts.
- Plan target records redact secret-looking path/query values, and receipt response URLs redact secret-looking path/query values.
- HTTP verbose output, request exception text, HTTP error text, and provider error bodies redact secret-looking URL and body values before they reach stderr, stdout, audit logs, run summaries, or run indexes.
- Token auth header format is verified from command implementation.
- The repo-local skill wrapper exists at `skills/make-com/SKILL.md`.

## Commands run

```bash
python3 scripts/refresh_official_inventory.py
PYTHONPATH=src python3 -m unittest -q
bash scripts/update_repo_navigation_index.sh
```

Results:

- inventory refresh wrote `docs/official_inventory.json` with `376` operations from `59` pages
- unit tests passed: `28` tests with `PYTHONPATH=src python3 -m unittest -q`
- repo navigation index regenerated after adding the new source folder

## What is not live-verified

- Live Make API calls have not been executed in this pass.
- No organization-specific production behavior is tested without Make credentials.
- Public publish checks are tracked separately from live Make account verification.

## Why this is still meaningful

The docs now match source behavior and official inventory facts, so an agent using these pages gets practical constraints before first write action.

## Evidence location

- Command surface and flags: source in `src/make_com_safe_agent_cli/cli.py`.
- Safety logic: `src/make_com_safe_agent_cli/commands/api.py`.
- Inventory source: `docs/official_inventory.json`.
- Skill wrapper: `skills/make-com/SKILL.md` in source, mirrored as `SKILL.md` in the public skill folder.

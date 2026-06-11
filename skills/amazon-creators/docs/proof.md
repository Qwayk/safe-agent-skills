# Proof

You don’t need to run these commands yourself; offline unit tests cover the dry-run plans and the `--apply` flows that matter for this release.

Verification command: `python3 -m venv .venv && .venv/bin/python -m pip install -e . && .venv/bin/python -m unittest -q`
Sync command: `python3 agent-orchestrator/scripts/sync_tool_docs.py --apply --repo-path .`

Date (UTC): 2026-06-04
Last verified (UTC): 2026-06-04

What can go wrong:

- OAuth token helpers now plan and require approval before token endpoint use or `.state/token.json` writes when no saved snapshot is available. Existing cached tokens can still be used by catalog reads.
- Catalog queries rely on the cached token and the locale/credential version in `.env`. Keep `AMAZON_CREATORS_LOCALE` in sync with your target marketplace so the right token endpoint and headers are used.
- The simplified output is best-effort: catalog commands default to a dry-run `plan`, and command-specific simplified fields such as `items` or `browse_nodes` appear only with `--apply`.
- No built-in rollback, backup, or snapshot restore exists here. Catalog calls are read-only, and local write helpers require explicit no-snapshot approval before file changes.

Latest local verification: `47` unit tests passed, plus compile, version, example JSON, catalog dry-run, and local helper refusal checks.

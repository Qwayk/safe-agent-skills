# Proof and Verification

This page records what was checked for the n8n source tool.

## Last verified

- Date (UTC): **2026-06-29**
- Tool version: `0.1.0`
- Official source: `n8n-io/n8n` commit `0c92df794a07404d22cbc85a3c4ed6b332e442ab`, `packages/cli/src/public-api/v1/`
- Live n8n account behavior: not verified; no real credentials are stored in this repo

## Verified locally

Run inside `api-tools/qwayk-n8n-safe-agent-cli/`:

```bash
PYTHONPATH=src python3 -m unittest -q
```

The local suite currently has 19 tests. It checks imports, JSON error output, version output, onboarding, audit redaction, official inventory coverage, operation listing, dry-run write plans, refusal without reviewed plans, response redaction, command-string redaction, HTTP failure redaction, HTTP error-body secret-key redaction, docs and skill wrapper alignment, and auth-check redaction with a mocked safe read.

## Manual command checks

```bash
PYTHONPATH=src python3 -m n8n_safe_agent_cli --output json --version
PYTHONPATH=src python3 -m n8n_safe_agent_cli --output json api list
```

With a real `.env`, this read-only check should reach `/workflows?limit=1`:

```bash
PYTHONPATH=src python3 -m n8n_safe_agent_cli --env-file .env --output json auth check
```

## What is not live-tested

- Real n8n API credentials.
- Real workflow, credential, user, project, folder, variable, data-table, source-control, package, or execution writes.
- Instance-gated beta n8n package operations.

Those limits do not change the source-ready shape, but any real account rollout should start with `auth check`, one read command, and one dry-run plan before apply.

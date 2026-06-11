# Proof and verification

Use this page when you want the clearest proof story for Pinterest.

This repo does not rely on live Pinterest API calls for normal verification. The proof here comes from the local suite, the committed redacted examples, and the explicit write-gating behavior.

## What is already proved

- The tool can validate its command surface and JSON output contract through the local suite.
- Read-mostly flows can be exercised without live Pinterest writes.
- Current write families stay plan-first and require explicit no-snapshot approval before live Pinterest changes.
- The committed examples show the expected version, error, plan, and refusal/receipt shapes.

## Last checked

- Local docs and contract alignment rechecked: **2026-06-11 UTC**
- Local suite proof baseline: **2026-02-03 UTC**

No live Pinterest credentials are stored here, so this proof pack is intentionally local-first and redacted.

## Core validation

From the tool folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
```

## Output contract

- Default output mode is JSON with `--output json`.
- In JSON mode, every invocation emits exactly one JSON object to stdout, including usage errors and `--version`.

## Committed examples

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/error.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

The current receipt example is still a refusal-shaped proof example, not a claim that a fully backed live write path exists.

## What can still go wrong

- missing or insufficient scopes
- ads or catalogs access that needs extra roles or account tier
- missing `--ad-account-id` or `--business-id` for optional snapshot expansions
- expired tokens
- operator confusion about no-snapshot write limits

## How to verify the risky parts

- If reads fail, confirm whether the issue is auth, scopes, or account access.
- If a write attempt is missing approval, confirm the refusal happened before Pinterest HTTP.
- If you are reviewing a plan, check the target IDs, payload, and acknowledgement flags before apply.
- If a command writes local snapshot files, confirm the output folder and files look correct.

## Intentional gaps

Not covered on purpose:

- undocumented Pinterest API write surfaces
- rollback or restore claims for current live write families
- provider-backup claims that the runtime does not actually implement

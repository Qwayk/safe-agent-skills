# Proof and verification

Use this page when you want the clearest proof story for Unsplash.

This repo does not rely on live Unsplash credentials for normal proof. The evidence here comes from the local suite, the committed redacted examples, and the explicit download-planning and no-snapshot behavior.

## What is already proved

- The shipped Unsplash read surface works through explicit named commands.
- The tool uses Access Key auth and keeps OAuth-only endpoints out of scope.
- `photos download` stays dry-run first and does not trigger download tracking in plan mode.
- Current tracked download applies still require explicit no-snapshot approval when useful saved before-state is missing.
- Export safeguards, overwrite checks, and run-history behavior are covered locally.

## Last checked

- Local docs and contract alignment rechecked: **2026-06-11 UTC**
- Local suite and proof baseline: **2026-06-04 UTC**
- Tool version: `0.1.0`
- Auth mode: Access Key only

No live Unsplash credentials are stored here, so this proof pack stays local-first and redacted on purpose.

## Core validation

From the tool folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m unittest -q
.venv/bin/unsplash-api-tool --output json --version
.venv/bin/unsplash-api-tool --output json onboarding --no-write-env
```

## Example live reads

These are real command examples for customer review. They are not claims that live credentials were stored or used in this repo run:

```bash
unsplash-api-tool --output json users collections --username "example_user" --per-page 10
unsplash-api-tool --output json users statistics --username "example_user"
unsplash-api-tool --output json users likes --username "example_user" --per-page 10
unsplash-api-tool --output json search collections --query "minimal" --per-page 5
unsplash-api-tool --output json topics list --per-page 5 --order-by latest
unsplash-api-tool --output json collections list --per-page 5
unsplash-api-tool --output json stats total
unsplash-api-tool --output json stats month
```

## What can still go wrong

- missing or wrong Access Key
- rate limits
- download plans that target the wrong photo IDs or local path
- tracked download applies that still have no saved before-state
- local exports or downloads that point to the wrong destination

## How to verify the risky parts

- If auth fails, check the Access Key and the `.env` file first.
- If the photo research output looks wrong, recheck the query, page size, and search filters before you pull more data.
- If a tracked download refuses, confirm it stopped before download tracking or a local file write.
- If a future approved download succeeds, confirm the receipt records the no-snapshot approval and the recovery limit.

## Committed examples

- Plans/refusals: `docs/examples/plan.example.json`, `docs/examples/receipt.example.json`
- Outputs: `docs/examples/outputs/version.json`, `docs/examples/outputs/auth_check.json`

## Intentional limits

Not covered on purpose:

- OAuth-only endpoints like `/me` or like/unlike flows
- automatic undo for download tracking or local file writes
- fake proof of live Unsplash access when real credentials are missing

# Quickstart

Start by checking the Contentsquare OAuth connection, then read one small result such as recent export jobs or site bounce rate. The goal is to prove the agent is looking at the right Contentsquare account and project before it prepares any live change.

Need more ideas? See [good first asks](use_cases.md). Need setup help? See [set up your account step by step](onboarding.md).

A good first ask is:

> Check that Contentsquare access is connected, tell me which API endpoint the token uses, run one safe metrics or export read if permissions allow, and stop before any live change.

## What you will do first

1. Make sure the local tool can run.
2. Confirm the Contentsquare OAuth token can be created without printing secrets.
3. Run one small read against a project you recognize.
4. Stop before Data Export job creation, enrichment sends, or Speed Analysis event changes.

## 1. Install for local source use

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

## 2. Make sure Contentsquare auth is ready

Create `.env` from `.env.example`, then fill the local OAuth values that Contentsquare gave you. Never paste the secret or token into chat.

```bash
contentsquare-safe-cli onboarding
contentsquare-safe-cli auth check
```

If your OAuth credentials are account-level instead of project-level, set `CONTENTSQUARE_PROJECT_ID` or use `--oauth-project-id` before the command.

## 3. Run one small first read

Start with a read that cannot change Contentsquare state. Export jobs are a good first check:

```bash
contentsquare-safe-cli data-export list-jobs --state completed --limit 25
```

If you already know the project ID, a small metrics read is also useful:

```bash
contentsquare-safe-cli metrics site bounce-rate --project-id 123 --start-date 2026-06-01 --end-date 2026-06-07
```

The CLI keeps readable flag names, but it sends Contentsquare's documented API names behind the scenes. For example `--project-id` becomes `projectId`, `--start-date` becomes `startDate`, and `--segment-id` or `--segment-ids` becomes `segmentIds`.

## 4. Stop before anything risky

Reads can run without apply flags. Anything that changes Contentsquare should start with a dry-run plan and wait for review.

For example, a Data Export job must be planned first:

```bash
contentsquare-safe-cli --plan-out docs/examples/plan.example.json data-export create-job --body-json body.json
```

After review:

```bash
contentsquare-safe-cli --plan-in docs/examples/plan.example.json --apply --yes --receipt-out docs/examples/receipt.example.json data-export create-job
```

Do not apply a plan until a reviewer has checked the project, endpoint, request body, risk, and verification note.

## What a useful first result includes

- which Contentsquare token scope and API endpoint were used
- which project, date range, job, metric, or object list was checked
- whether the read succeeded, returned nothing, or was blocked by entitlement or permission
- what the result means in normal words
- what is safe to inspect next
- whether any plan, receipt, or saved output was written

## Where to go next

- For real examples, read [good first asks](use_cases.md).
- For setup details, read [set up your account step by step](onboarding.md).
- For exact command options, read [technical command guide](command_reference.md).
- For approval rules and limits, read [understand the safety checks](safety_model.md).

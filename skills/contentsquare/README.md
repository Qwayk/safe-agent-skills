# Contentsquare Safe CLI

Contentsquare is where teams check what visitors actually did, what changed conversion, and where site or app speed may be hurting the experience. This skill lets an AI agent pull export jobs, metrics, enrichment batches, and Speed Analysis Lab reports through the official server-side APIs, then pause before any live change.

A good first ask is: “Check which Contentsquare metrics this account can read, then show me the bounce rate for this project last week.”

Best for Contentsquare reporting, export review, enrichment planning, Speed Analysis checks, and reviewed server-side changes. Not for installing the Web Tag, setting up mobile SDK tracking, or bypassing Contentsquare permissions. Change level: **Reads + careful changes**. Live Contentsquare account behavior has not been verified yet.

## Start here first

- [See good first asks](docs/use_cases.md)
- [Set up your account step by step](docs/onboarding.md)
- [Understand the safety checks](docs/safety_model.md)
- [Run the first command](docs/quickstart.md)
- [Use the technical command guide](docs/command_reference.md)

## What this skill helps with

- Create and inspect Data Export jobs.
- List exportable fields, custom variables, dynamic variable keys, jobs, runs, and successful runs.
- Read Contentsquare object lists and Metrics API rows for site, page group, web zone, and app zone metrics.
- Send enrichment batches after a reviewed dry-run plan.
- Read Speed Analysis Lab reports and manage Speed Analysis events after review.

## What access this skill needs

The CLI uses Contentsquare server-to-server OAuth 2.0 with a `client_id` and `client_secret`. It does not support deprecated API-key auth as the normal path.

Keep credentials in a local `.env` file:

```bash
CONTENTSQUARE_CLIENT_ID=...
CONTENTSQUARE_CLIENT_SECRET=...
CONTENTSQUARE_PROJECT_ID=
CONTENTSQUARE_AUTH_BASE_URL=https://api.contentsquare.com
CONTENTSQUARE_API_BASE_URL=
CONTENTSQUARE_TIMEOUT_S=30
```

The API endpoint can come from the OAuth token response. Use `CONTENTSQUARE_API_BASE_URL` only when Contentsquare gives you a fixed endpoint. If your OAuth credentials are account-level instead of project-level, set `CONTENTSQUARE_PROJECT_ID` or pass `--oauth-project-id` so the token request targets the right project.

## Install and first run

Install slug: `contentsquare`

Ask your agent to install the skill from `Qwayk/safe-agent-skills`.

If auto-install is not available, run:

```bash
npx skills add Qwayk/safe-agent-skills@contentsquare -g -y
```

For local source use, install it from this folder:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

Then ask:

```text
Check that Contentsquare access is connected, tell me which API endpoint the token uses, run one safe metrics or export read if permissions allow, and stop before any live change.
```

## How this skill stays safe

Read commands run directly and print one JSON object. Write commands are dry-run by default and produce a plan for review.

Live writes require the reviewed plan plus `--apply --yes`. Enrichment sends and Speed Analysis event changes also require an acknowledgement when Contentsquare does not expose a safe before/after snapshot.

## What it covers today

The CLI covers the official server-side REST docs for:

- Data Export
- Metrics
- Enrichment batch send
- Speed Analysis Lab

Data Connect, Web Tag, WebView tracking, Android, iOS, and React Native SDK docs are accounted for in coverage, but they are not server-side CLI endpoint commands in this product shape.

## What happens before live changes

The agent first asks the CLI for a dry-run plan. The plan names the endpoint, request body, risk level, preconditions, and verification notes.

Only after review should the agent apply that saved plan. Apply creates a receipt when the command changes live state.

## What proof it leaves behind

Write-capable commands can save local plans, receipts, summaries, and audit logs under `.state/runs/`. These files are gitignored and must not contain secrets.

## Limits

Live Contentsquare credentials are needed for live verification. Without credentials, local tests prove command wiring, safety gates, docs, examples, and redaction, but not account-specific API access.

Some Contentsquare limits are account or entitlement dependent. The coverage and proof docs list the limits that are documented by Contentsquare.

## Helpful docs

- [Browse all Contentsquare docs](docs/README.md)
- [Good first asks](docs/use_cases.md)
- [Set up Contentsquare access](docs/onboarding.md)
- [Run the quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [API coverage ledger](docs/api_coverage.md)
- [Proof and verification](docs/proof.md)

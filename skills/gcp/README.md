# Google Cloud Platform Safe CLI

Google Cloud work often starts with one risky question: are we looking at the right project? This skill helps your agent confirm the target, inspect running resources, review IAM access, and spot cost or exposure risks before it plans a change.

A good first ask is: "Check the project this account can see, list one safe area such as Compute Engine or Cloud Run, flag cost or access risks, and stop before any change."

Best for cloud admin reviews, cleanup planning, access checks, exposure checks, and reviewed change plans. Not for bypassing Google Cloud permissions, testing random API calls, or making vague live changes. Change level: **Reads + careful changes**. Live Google Cloud account behavior has not been verified yet.

## Start here first

- Want ideas for real work? [See useful Google Cloud asks](docs/use_cases.md)
- Need setup? [Connect Google Cloud safely](docs/onboarding.md)
- Want the safety story first? [Understand review before changes](docs/safety_model.md)
- Ready for one first result? [Run the quickstart](docs/quickstart.md)
- Need exact syntax? [Use the command guide](docs/command_reference.md)

If you want evidence before trusting it, start with [Proof and verification](docs/proof.md). If you are checking coverage, use [API coverage](docs/api_coverage.md).

## What this skill helps with

- **Find the right target first.** Check which projects, folders, organizations, regions, and billing-related areas the current Google Cloud credentials can reach.
- **Review access.** Inspect IAM, service accounts, policies, and permission-sensitive areas before changing who can do what.
- **Check infrastructure.** Review Compute Engine instances, disks, images, IP addresses, load balancers, VPC networks, subnets, routes, and firewall-related resources.
- **Review app and data services.** Inspect Cloud Storage buckets, Cloud Run services, Cloud SQL instances, databases, Pub/Sub, Cloud Build, Artifact Registry, logs, monitoring, and enabled services where permissions allow.
- **Watch cost-sensitive areas.** Check running machines, reserved IPs, databases, quotas, billing scope, and enabled APIs before cleanup or expansion work.
- **Plan changes with review.** Prepare a dry-run plan for creates, updates, deletes, service enablement, IAM changes, network changes, and other risky work before it runs.
- **Leave a review trail.** Save plans, receipts, run summaries, and redacted examples so a reviewer can see what was planned and what happened.

## Example requests

- "Check which Google Cloud project this account is using and stop."
- "List projects this identity can see, then tell me which one looks like the right target."
- "Review IAM access in this project and flag users, groups, or service accounts that deserve a human check."
- "List running Compute Engine instances, machine types, external IPs, and anything that may create avoidable cost."
- "Find reserved or external IP addresses and tell me which ones may be unused or exposed."
- "Review Cloud Storage buckets for public access or settings that deserve a closer look."
- "Show Cloud Run services and Cloud SQL instances in this region, then summarize what is public, active, or cost-sensitive."
- "Check enabled services and tell me whether Compute, Storage, Cloud Run, Cloud SQL, Logging, and Service Usage are available."
- "Pull recent log entries for this service and summarize errors or warnings."
- "Prepare a plan to disable an unused service or delete an unused IP, but do not apply it."

## What access this skill needs

- Google Application Default Credentials, usually from `gcloud auth application-default login` or a local service account file.
- The `cloud-platform` scope for broad Google Cloud API access.
- A quota project when Google needs one for billing or quota checks.
- IAM permission for the specific project, folder, organization, billing account, region, or service you ask it to inspect.
- Optional allowlists for projects, folders, organizations, billing accounts, and regions so the tool refuses the wrong target.

Never paste service account JSON, OAuth files, `.env` values, tokens, or keys into chat.

## Install and first run

Install slug: `gcp`

Ask your agent to install the skill from `Qwayk/safe-agent-skills`.

If auto-install is not available, run:

```bash
npx skills add Qwayk/safe-agent-skills@gcp -g -y
```

For local source use, install it from this folder:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

Then ask:

```text
Check that Google Cloud access is connected, tell me which project or quota context you can see, run one safe read if permissions allow, and stop before any live change.
```

## How this skill stays safe

- Reads can run without apply flags.
- Every write starts as a dry-run plan.
- Live writes require a reviewed saved plan plus `--plan-in`, `--apply`, and `--yes`.
- Higher-risk work may also require `--ack-no-snapshot` or `--ack-irreversible`.
- The tool can refuse targets outside project, folder, organization, billing account, or region allowlists.
- Plans, receipts, logs, and examples are redacted.
- There is no catch-all command for arbitrary Google URLs or operations.

## What it covers today

The generated inventory was built from the official Google Discovery directory on 2026-06-25, with official fallback sources for selected gaps.

- 175 included Google Cloud services
- 9,781 operations
- 4,614 reads
- 902 remote writes
- 2,969 high-no-snapshot operations
- 1,296 irreversible operations
- 0 unknown mutating operations
- 0 unresolved selected-source gaps after official fallback checks

That proves the source coverage ledger, not live Google Cloud account behavior.

## What happens before live changes

1. The tool creates a dry-run plan with the service, operation, target, input, and risk.
2. You or the agent review the plan before anything changes.
3. The apply step refuses if the reviewed plan no longer matches the command.
4. The tool requires the needed apply and acknowledgement flags.
5. The receipt says whether read-back verification ran or whether verification was limited to the provider response.

## What proof it leaves behind

- Local run records under `.state/runs/` when commands create them.
- Dry-run plans for writes.
- Receipts for live writes when live writes actually run.
- Redacted example outputs in `docs/examples/`.
- A generated coverage ledger tied to official Google sources.
- A proof page that separates local validation from live Google Cloud verification.

## Limits

- Live Google Cloud account behavior has not been verified yet.
- Local tests, generated coverage, and mocked examples are not live proof.
- Google Cloud IAM still decides what the signed-in user or service account can see or change.
- Generic generated writes may only have limited verification unless a safe read-back path exists.
- The tool does not promise rollback, backup, restore, or undo for Google Cloud changes.
- The command surface only covers explicit operations in the generated inventory and official fallback rows.

## Helpful docs

- [Browse all GCP docs](docs/README.md)
- [Useful Google Cloud asks](docs/use_cases.md)
- [Connect Google Cloud safely](docs/onboarding.md)
- [Run the quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Safety model](docs/safety_model.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

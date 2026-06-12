# Salesforce

**Capability:** Reads + careful changes

Salesforce is where customer records, object metadata, approvals, list views, Bulk API jobs, and platform limits shape how a team actually works.

This skill helps an agent inspect a Salesforce org, run careful SOQL or SOSL questions, review object and metadata details, and prepare write plans before anything touches live org data.

Use it for questions like: "Which Account records match this query?", "What fields exist on this object?", "What limits or REST resources are available?", "Can you check this Bulk API job?", or "Can you preview this composite change before applying it?"

Salesforce access depends on your org, token scopes, API version, and enabled features. Reads run normally once access is valid; write-capable commands produce review plans first, and live apply needs explicit no-snapshot approval when the command cannot save real before-state.

A good first ask is: "Check the Salesforce connection, show the org resources and limits, run a small Account query, and stop before any writes."

## Start here first

- Want ideas for real Salesforce work? [What you can do with Salesforce](docs/use_cases.md)
- Need setup? [Connect your Salesforce org](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Inspect Salesforce REST resources, org limits, tabs, themes, and object metadata.
- Run SOQL and SOSL queries, including paged query follow-ups.
- Read sObject records, list views, quick actions, layouts, approvals, Lightning usage metrics, and org-gated areas when the org exposes them.
- Work with composite requests and Bulk API 2.0 jobs.
- Prepare reviewed write plans for Salesforce Platform REST work before live apply.

## What access this skill needs

- Your Salesforce org URL in `SALESFORCE_INSTANCE_URL`.
- A Salesforce REST API access token in `SALESFORCE_ACCESS_TOKEN`, or a token file saved through the auth commands.
- `SALESFORCE_API_VERSION=67.0` unless your org needs a different supported version.
- Org permissions and feature access for the records or metadata you want the agent to inspect.

## Install and first run

Install slug: `salesforce-platform`

Ask your agent to install the `salesforce-platform` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@salesforce-platform -g -y
```

Then try a safe first ask like:

```text
Check the Salesforce connection, show the org resources and limits, run a small Account query, and stop before any writes.
```

## How this skill stays safe

- Reads can run after valid Salesforce access is available.
- Write-capable commands default to dry-run plans.
- Apply requests need `--apply`.
- Higher-risk apply requests also need `--yes`.
- Irreversible deletes and resets need `--ack-irreversible`.
- User password set or reset commands require a reviewed `--plan-in` on apply.
- When no useful before-state can be saved, live apply requires explicit no-snapshot approval before Salesforce HTTP.

## What it covers today

This skill covers the core Salesforce Platform REST API and Bulk API 2.0 areas documented for this tool, including:

- versions, resources, limits, query, search, sObjects, list views, quick actions, and composite work
- support knowledge, consent, process resources, survey translations, and Lightning usage metrics where the org exposes them
- OpenAPI spec generation for sObjects beta
- `/services/data/vXX.X/jobs` Bulk API 2.0 work

It does not try to absorb separate Salesforce product families such as Connect/Chatter, Analytics, Metadata, Tooling, Commerce, industry-specific `connect/*` families, or internal-only resources.

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the org, object, request body, and recovery limit.
- Live apply must pass the required approval gates and plan drift checks.
- Higher-risk writes need stronger approval.
- If no before-state can be saved, live apply also needs explicit no-snapshot approval.

## What proof it leaves behind

- Dry-run plans can be saved for review.
- Approved supported apply requests can leave write receipts.
- Local run history can include `plan.json`, `receipt.json`, `summary.md`, and `audit.jsonl`.
- The docs, tests, proof pack, and API coverage ledger live in this repo.

## Limits

- Salesforce feature access depends on the org, edition, permissions, token scopes, and API version.
- Some official REST resources point to separate Salesforce guides and are intentionally outside this tool.
- This tool does not promise automatic rollback, snapshots, or provider backups for every write path.
- When no useful before-state exists, recovery is manual follow-up work, not one-click undo.

## Helpful docs

- [Browse all Salesforce docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

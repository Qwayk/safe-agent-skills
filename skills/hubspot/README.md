# HubSpot

**Capability:** Reads + careful changes

HubSpot is where CRM records become the team's customer truth: contacts, companies, deals, tickets, properties, pipelines, associations, imports, exports, and custom objects.

This skill helps an agent inspect the CRM, explain what is available in the account, export useful records, and prepare careful change plans before anything touches live customer data.

Use it for questions like: "Which companies match these rules?", "What properties exist on deals?", "How are these contacts associated?", "What stages are in this pipeline?", or "Can you preview this import before changing HubSpot?"

HubSpot access depends on your token scopes, enabled object types, and account tier. Reads run normally once access is valid; writes start as dry-run plans and need explicit approval before live work.

A good first ask is: "Run the HubSpot setup check, show which CRM areas are available in my account, read a small sample, and stop before any writes."

## Start here first

- Want ideas for real HubSpot work? [What you can do with HubSpot](docs/use_cases.md)
- Need setup? [Connect your HubSpot account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Search and review CRM object records.
- Inspect associations, labels, limits, properties, property groups, owners, pipelines, and stages.
- Check custom object schemas and object-library enablement.
- Prepare imports, exports, property changes, pipeline edits, and association changes as review plans.
- Keep proof of plans, refusals, and supported receipts for CRM work.

## What access this skill needs

- A HubSpot private app token in `HUBSPOT_ACCESS_TOKEN`, or an OAuth token JSON saved through the auth commands.
- The right scopes for the CRM objects and settings you want to inspect or change.
- Active object types and the HubSpot account tier needed for the feature.

## Install and first run

Install slug: `hubspot`

Ask your agent to install the `hubspot` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@hubspot -g -y
```

Then try a safe first ask like:

```text
Run the HubSpot setup check, show which CRM areas are available in my account, read a small sample, and stop before any writes.
```

## How this skill stays safe

- Reads run normally after valid authentication and scopes are available.
- Writes are dry-run plans by default.
- Batch or risky write actions need stronger approval such as `--yes`.
- Actions marked irreversible need `--ack-irreversible`.
- Live write apply requires explicit no-snapshot approval when command-specific before-state capture is not available.
- The tool does not create snapshots, provider backups, or automatic rollback.

## What it covers today

This skill covers:

- CRM object records and search
- associations, labels, limits, properties, property groups, owners, pipelines, and stages
- custom object schemas, imports, exports, and object-library enablement checks
- plan, refusal, receipt, audit, and run-history proof for CRM work

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the objects, filters, fields, account access, and recovery limit.
- Batch or risky changes need `--yes`.
- Irreversible actions need `--ack-irreversible`.
- Live apply needs explicit no-snapshot approval when no command-specific before-state capture exists.

## What proof it leaves behind

- Dry-run plans can be saved locally.
- Supported apply output can leave a receipt.
- Run summaries and audit logs live under `.state/runs/`.
- The docs, tests, proof pack, and API coverage ledger are all in this repo.

## Limits

- Some HubSpot features depend on account tier, enabled object types, and token scopes.
- Export download URLs can expire quickly, so export work may need prompt follow-up.
- The tool does not promise automatic rollback or snapshot-based restore.
- Live proof still depends on local credentials and the account features available to you.

## Helpful docs

- [Browse all HubSpot docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Proof pack](docs/proof.md)
- [API coverage](docs/api_coverage.md)
- [Examples](docs/examples/)

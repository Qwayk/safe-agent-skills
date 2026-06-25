# Safety model

Google Cloud mistakes can break apps, expose data, change permissions, delete resources, or create cost. This tool is built around a simple rule: look first, plan second, change last.

Safe use should feel calm. The agent checks the target, explains what it found, shows a plan before risky work, and leaves a record after live work. Secrets stay local.

A good safety ask is: "Check the project, resource, risk, and approval step before any Google Cloud change, then tell me whether verification will be full read-back or limited provider-response verification."

## What safe use looks like

- Read-only checks happen before change requests.
- The agent names the project, region, zone, service, and operation it is touching.
- Vague or dangerous requests turn into a plan, not an immediate live change.
- Bigger changes wait for a stronger approval step.
- Receipts say what happened and whether verification was full or limited.
- Live Google Cloud behavior is treated as unverified until a real safe-target read succeeds.

## Why Google Cloud needs extra care

Some Google Cloud work is low-risk, like listing enabled services or checking which project the account can see. Other work can affect IAM access, billing, public IPs, networks, databases, storage, logs, service enablement, or running workloads.

The tool should not treat those actions the same way. A small read can run quickly. A delete, IAM update, public exposure change, database change, quota change, or cost-sensitive action should slow down.

## Normal change flow

1. Generate a dry-run plan.
2. Review the target, input, service, operation, and risk.
3. Apply only from the reviewed saved plan.
4. Verify with a safe read-back when the provider supports it.
5. Save a receipt that says what happened.

## What plans and receipts are for

A plan shows what the tool wants to change before it acts. It should name the target, proposed input, risk, required approvals, and expected verification.

A receipt shows what happened after live work. It should say whether the tool changed anything and whether verification was read-back verification or only a limited provider-response check.

Plans and receipts must not include secrets.

## Approval rules

- Reads do not need apply flags.
- Writes start as dry-run plans.
- Live writes require `--plan-in`, `--apply`, and `--yes`.
- Higher-risk or no-snapshot writes can require `--ack-no-snapshot`.
- Delete-like or hard-to-undo actions can require `--ack-irreversible`.
- The tool can refuse work outside configured project, folder, organization, billing account, or region allowlists.

## First safe setup check

For a new Google Cloud setup, start with:

```bash
qwayk-gcp-safe-agent-cli --output json auth check
```

That check tells you whether the local Google credential path is available. The next safe step is one small read against a known project, zone, or service that your IAM permissions allow.

## Run history

For write-capable commands, the tool can write local run records under `.state/runs/`. Those records help answer questions later, such as what changed last time, which plan was reviewed, and whether verification passed.

Local run records are not public proof. Keep them private and never include secrets.

## If the target changes after planning

When applying from a saved plan, the tool should refuse if the reviewed target no longer matches. Examples include a different project, region, zone, billing account, resource name, operation, input file, or provider version marker when Google gives one.

If the target changed, make a new plan.

## Recovery and follow-up

Do not assume a Google Cloud change can be undone. Some Google Cloud operations have provider restore actions, some have partial follow-up actions, and some are hard to put back.

If verification fails and a safe follow-up action exists, create a new plan and require approval. If no safe follow-up exists, the tool should say that plainly before the user approves the risky work.

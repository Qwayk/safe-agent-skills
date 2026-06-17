---
name: fortnox
description: Run Fortnox read and careful write operations safely using fortnox-api-tool.
---

# Fortnox

**Capability:** Reads + careful changes

Fortnox is where invoicing, suppliers, bookkeeping, payroll, and warehouse work live. This skill helps an agent read the official Fortnox REST and websocket surface, then plan reviewed changes without guessing.

It is useful when you want to know what records exist, what is safe to change first, or what needs extra confirmation before a write.

A good first ask is: "Check the Fortnox skill is configured, confirm auth works, and list company information and customers before we plan any writes."

## Start here first

- Read the tool README if you want the public overview.
- Open the quickstart if you want the first safe commands.
- Check the safety model if you want the write rules first.

## What this skill covers

- Fortnox read commands for the published REST and websocket surface.
- Dry-run plans for write commands.
- Reviewed apply flows with `--apply --yes --plan-in`.
- High-risk applies that need `--ack-no-snapshot`.
- Irreversible applies that need `--ack-irreversible`.

## What it does not cover yet

- `jobs run` is unsupported until real registry-backed rows exist.
- Any generic raw-request bridge or arbitrary URL execution.

## Safe first commands

- `fortnox-api-tool auth check`
- `fortnox-api-tool company-information get`
- `fortnox-api-tool customers list`
- `fortnox-api-tool suppliers list`

## Before live changes

- Show a dry-run plan first.
- Review the plan before apply.
- Use `--plan-in` for the reviewed plan.
- Add `--yes` on apply.
- Add `--ack-no-snapshot` when the change is high-risk and there is no useful before-state snapshot.
- Add `--ack-irreversible` when the change cannot realistically be undone.

## Helpful docs

- `README.md`
- `docs/README.md`
- `docs/quickstart.md`
- `docs/safety_model.md`
- `docs/command_reference.md`
- `docs/proof.md`

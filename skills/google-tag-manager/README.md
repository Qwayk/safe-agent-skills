# Google Tag Manager

**Capability:** Reads + careful changes

Google Tag Manager controls the tags, triggers, variables, and containers that often decide whether analytics, ads, consent, and conversion tracking work correctly. This skill helps an agent inspect that setup carefully before a tracking change reaches a real website.

Use it for jobs like "What tags and triggers are in this container?", "Which workspace changes are waiting?", "What changed between versions?", or "Can you prepare this GTM change as a plan before anything is published?"

Read work can run first for account, container, workspace, tag, trigger, variable, and version review. Riskier GTM changes are dry-run first, publish-like actions need saved-plan review, irreversible deletes need extra approval, and some mutating families are refused for live apply if the API cannot expose the matching pre-read needed for safe before-state capture.

A good first ask is: "List my GTM accounts, containers, and workspaces, review the tags, triggers, and variables in this container, and stop before any changes."

## Start here first

- Want ideas for real GTM work? [What you can do with Google Tag Manager](docs/use_cases.md)
- Need setup? [Connect your Google Tag Manager account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- List GTM accounts, containers, workspaces, and environments.
- Review tags, triggers, variables, folders, templates, and clients before a change.
- Compare versions and inspect publish-related state.
- Build careful plans for GTM API writes across the supported discovery surface.
- Verify many writes with a matching `GET` check after apply when the API supports that path.

## What access this skill needs

- One Google auth mode: ADC, OAuth refresh token, or service-account JSON.
- Access to the GTM account or container you want to inspect or change.
- Broader scopes if you want full read and write coverage instead of read-only review.

For most local users, ADC is the shortest starting path.

## Install and first run

Install slug: `google-tag-manager`

Ask your agent to install the `google-tag-manager` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@google-tag-manager -g -y
```

Then try a safe first ask like:

```text
List my GTM accounts, containers, and workspaces, review the tags, triggers, and variables in this container, and stop before any changes.
```

## How this skill stays safe

- It keeps one explicit command per supported GTM discovery method instead of exposing a generic raw bridge.
- Writes stay dry-run first and do not run live unless you pass `--apply`.
- Medium-risk writes need `--apply`.
- Higher-risk publish, linking, move, or batch-like actions need `--apply --yes --plan-in`.
- Irreversible deletes also need `--ack-irreversible`.
- For supported write families, the tool pre-reads before-state when the GTM discovery surface exposes the matching `GET`; when it cannot, live apply is refused for that family.

## What it covers today

This skill covers:

- auth checks and GTM account discovery
- explicit GTM API v2 methods across the supported discovery surface
- reads and careful writes for accounts, containers, workspaces, tags, triggers, variables, versions, environments, folders, templates, and related GTM resources
- plan and receipt output with risk, recovery, and verification details

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the GTM account, container, workspace, or resource target before apply.
- Read work can run immediately.
- Medium-risk writes need `--apply`.
- Higher-risk writes need `--apply --yes --plan-in`.
- Irreversible deletes need `--apply --yes --ack-irreversible --plan-in`.
- If GTM does not expose the pre-read needed for safe before-state capture, live apply is refused for that method family.

## What proof it leaves behind

- Dry-run output acts as the review plan.
- Apply output acts as the receipt.
- Plans and receipts include recovery as either `rollback_by_inverse_action` or `irreversible_and_clearly_labeled`.
- Supported write families can include `before_state` and a saved `before_state.json` artifact.
- Local run history lives under `.state/runs/` when artifacts are enabled.
- The docs, tests, and API coverage notes are all in this repo.

## Limits

- The tool does not promise generic undo, snapshot rollback, or backup restore.
- Some GTM mutating families stay plan-only when the API does not expose the matching read path needed for safe live apply.
- Publish-like changes are treated as higher risk and need saved-plan review.
- You still need real GTM access for the accounts and containers you want to inspect or change.

## Helpful docs

- [Browse all Google Tag Manager docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

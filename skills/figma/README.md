# Figma

**Capability:** Reads + careful changes

Figma is where product screens, comments, libraries, variables, components, and webhooks become the shared design record for a team.

This skill helps an agent review Figma files, comments, versions, libraries, variables, webhooks, developer resources, and design-system data, then prepare careful changes before they affect the workspace.

Use it for questions like: "What unresolved comments are in this file?", "Which components or variables are published?", "Can you audit this team library?", "What webhooks exist?", or "Can you preview a comment or variable change?"

Figma reads can help a team understand a file before anyone edits it. Writes start as dry-run plans, destructive actions need extra approval, and some changes need an extra check when the tool cannot save useful before-state first.

A good first ask is: "Check the Figma connection, show me which files, teams, libraries, and comments this token can review, and preview any write before it goes live."

## Start here first

- Want ideas for real Figma work? [What you can do with Figma](docs/use_cases.md)
- Need setup? [Connect your Figma account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review files, versions, comments, and reactions in real Figma workspaces.
- Check projects, files, components, component sets, styles, variables, and team libraries.
- Inspect webhooks, webhook request history, developer logs, activity logs, discovery coverage, and payments lookups.
- Plan careful comment, webhook, variable, or dev-resource changes before they go live.
- Save exact JSON output to local files when you need proof, handoff material, or audit history.

## What access this skill needs

- A Figma personal token, OAuth token, or plan token.
- File keys, team IDs, project IDs, or webhook IDs depending on the job.
- Some analytics, activity-log, developer-log, and org-scoped endpoints need the right workspace tier or organization access.

For most people, a read-focused token and one known file key is the safest place to start.

## Install and first run

Install slug: `figma`

Ask your agent to install the `figma` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@figma -g -y
```

Then try a safe first ask like:

```text
Check the Figma connection, show me what this token can read, and preview any comment or webhook change before it goes live.
```

## How this skill stays safe

- It keeps the available Figma actions explicit instead of letting the agent send arbitrary undocumented requests.
- Read operations can run directly.
- Writes are dry-run first and need `--apply --yes`.
- Delete-like or one-way actions may also need `--ack-irreversible`.
- When Figma does not expose useful before-state, current writes also need explicit `--ack-no-snapshot` approval.
- Plans, receipts, run history, docs, tests, and coverage all live together in this repo.

## What it covers today

This skill covers:

- files, node reads, image renders, image fills, file metadata, and version history
- comments and reactions
- projects, project files, components, component sets, styles, and team libraries
- webhooks and webhook request history
- activity logs, developer logs, discovery, payments lookups, variables, dev resources, library analytics, and oEmbed
- careful write previews and reviewed applies for the supported write families

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the file, team, project, variable, dev-resource, or webhook target before apply.
- Safe reads can run immediately.
- Writes need `--apply --yes`.
- Destructive actions may also need `--ack-irreversible`.
- Current Figma writes also need `--ack-no-snapshot` when useful before-state cannot be captured first.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Reviewed applies can save receipts with `--receipt-out`.
- `runs list` and `runs show` let you inspect earlier attempts.
- `--out` can save response JSON or raw payloads to local files.
- The repo also ships examples, tests, and coverage notes so you can inspect what the agent is using.

## Limits

- Some Figma endpoints are team-gated, org-gated, or plan-gated.
- The repo proves the shipped commands locally, but real account results still depend on your token, workspace access, and Figma plan.
- Current write families do not have a broad automatic undo or restore path.
- When Figma does not expose a clean prior state, the skill can still work, but only after explicit no-snapshot approval.

## Helpful docs

- [Browse all Figma docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof pack](docs/proof.md)
- [API coverage](docs/api_coverage.md)
- [Authentication details](docs/authentication.md)

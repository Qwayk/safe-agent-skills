# Ghost

**Capability:** Reads + careful changes

Ghost is where published posts, newsletters, members, tiers, offers, themes, and webhooks all meet the public site your readers see.

This skill helps an agent audit Ghost content, check internal links, review posts, pages, tags, members, newsletters, and offers, and prepare site changes before anything affects the live publication.

Use it for questions like: "Which posts are missing metadata?", "What internal links are broken?", "Which tags need cleanup?", "Can you export newsletter or member data?", or "Can you preview this offer, theme, or webhook change?"

Ghost changes should start with the current site state. The tool builds dry-run plans, verifies many writes after apply, and saves proof. Higher-risk families need extra acknowledgements or explicit no-snapshot approval when Ghost does not expose the same safe before-state or read-back path.

A good first ask is: "Audit my Ghost posts, tags, and broken internal links, then show me the highest-risk issues before changing anything."

## Start here first

- Want ideas for real Ghost work? [What you can do with Ghost](docs/use_cases.md)
- Need setup? [Connect your Ghost account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Audit posts, pages, tags, authors, and broken internal links.
- Export content, member, newsletter, and email performance reports.
- Read public content through the Ghost Content API without an Admin key.
- Patch posts and pages carefully, including metadata and body-edit workflows.
- Clean up tags, update tiers or offers, and manage member or newsletter settings.
- Plan or apply higher-impact theme and webhook changes with stricter review.

## What access this skill needs

- A Ghost Admin API URL and Admin API key for management work and writes.
- A Ghost Content API URL and Content API key if you want lower-risk public read-only content commands.
- A local `.env` file for those credentials.
- Staging access is strongly recommended for risky site changes.

## Install and first run

Install slug: `ghost`

Ask your agent to install the `ghost` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@ghost -g -y
```

Then try a safe first ask like:

```text
Check the Ghost connection, confirm auth, then audit my latest posts, tags, and broken internal links without changing anything.
```

## How this skill stays safe

- Read-only audits and reports do not change your Ghost site.
- Write workflows start with dry-run plans.
- Many update families save local snapshot evidence before apply.
- Higher-risk applies can require saved plan review, `--yes`, `--ack-irreversible`, or explicit no-snapshot approval depending on the action.
- The tool verifies many edits by read-back or idempotence instead of trusting the write blindly.
- If Ghost does not give a safe read-back path for a family, the tool should use clearer ledger proof or stop instead of pretending the action is fully reversible.

## What it covers today

This skill covers:

- Ghost Admin API management work
- Ghost Content API read-only public content work
- post and page patch, status, copy, audit, and body-edit workflows
- tags, tiers, offers, members, and newsletters
- theme, webhook, image, and batch-job planning with stricter safety

## What happens before live changes

- The agent reads the current state first.
- The tool shows a dry-run plan before the write.
- You review the target, payload, and risk level.
- Destructive or status-changing actions need `--yes`.
- Email-triggering or other irreversible actions need `--ack-irreversible`.
- Some higher-risk applies also need a saved plan review or explicit no-snapshot approval.

## What proof it leaves behind

- Write-capable commands save plan, receipt, audit, and summary files under `.state/runs/`.
- Snapshot-backed families save local evidence under `backup-snapshots/`.
- Many write families verify by read-back or idempotence after apply.
- Ghost webhook proof stays ledger-based because Ghost does not expose a webhook get or list endpoint.
- The docs, tests, and redacted example artifacts all live in this repo.

## Limits

- Ghost sites can mix Lexical and Mobiledoc content, so the correct edit family matters.
- Not every Ghost write family has the same before-state or read-back path.
- Some higher-impact families need extra acknowledgements or stay more limited than normal update flows.
- You still need valid Ghost access for real site work.

## Helpful docs

- [Browse all Ghost docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof pack](docs/proof.md)
- [API coverage](docs/api_coverage.md)
- [Ghost content format notes](docs/content_lexical_mode.md)
- [Jobs and batch work](docs/jobs_and_batches.md)

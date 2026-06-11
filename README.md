# Qwayk skills

Give your AI agent real product work, with more review before risky changes.

Qwayk skills help agents work inside real products without turning live settings, spend, customers, or content into a blind bet. They cover jobs like reviewing calls in CallRail, planning changes in Google Ads, checking incidents in Statuspage, working inside WordPress, and inspecting Stripe, Shopify, or Cloudflare accounts with a clearer review path.

> **[Browse the full skill catalog ->](skills/README.md)**
> Start with the product you use and the job you want done.

If your agent supports installed skills, ask it to install the skill you want from `Qwayk/safe-agent-skills`. If the skill needs account access, ask the agent to run `onboarding`. For the full setup flow, use the [install guide](INSTALL.md).

Each skill keeps the agent instructions, safe API tool code, docs, and tests together in one place, so you can inspect what the agent is really using. Some skills are read-only by design. Others can change real settings or data, but they are built to look first, show the plan, ask before important changes, check the result, and leave a record of what happened.

## What makes Qwayk skills different

<p align="center">
  <img src="docs/images/repo-home-qwayk-skill-comparison.png" alt="Comparison showing a typical API skill as Ask, Act, Live change and a Qwayk skill as Ask, Check + Plan, Review, Change, Confirm + Proof." width="1100">
</p>

Many API tools for AI agents are built to help the agent move fast. Qwayk skills are built to slow the agent down where mistakes have a real cost.

This is for the work people still hesitate to hand to an AI agent: publishing on a live website, changing a real Google Ads campaign, posting from a brand account, or editing settings that already affect traffic, leads, or revenue.

One wrong move can spend money, break something that already works, delete something important, or put sensitive data in the wrong place. And even when the job seems to finish, the agent can still leave you with no clear record of what happened.

Qwayk skills are built to make that kind of work easier to trust. Before an important change, the skill can guide the agent to look at the account first and show you the plan. For bigger changes, it can slow down with a dry run, a saved plan, or clearer approval. When possible, it saves the exact setting, rule, text, file, or item it is about to change, so there is something real to compare with later. Some products also have their own restore, backup, or version history, and the skill should use that when it really exists. Some smaller changes have a clear way back. Some changes cannot be put back automatically, so the skill should say that clearly before you approve the work. It should not refuse normal approved work just because a perfect safety record is not possible.

- Look first, then act.
- Show the plan before important changes.
- Ask before touching money, customers, content, settings, or data.
- Use a dry run, saved plan, or clearer approval for bigger changes when the skill supports it.
- When possible, save the exact thing the skill is about to change.
- Use the product's own restore, backup, or version history when that really exists.
- Say clearly when a change may not be easy to put back.
- Check the result after the work runs.
- Leave a record you can review later.
- Keep the instructions, safe API tool code, docs, and tests together in the same skill folder, so nothing important is hidden.

Read the deeper explanation in [How Qwayk skills keep agents safer](docs/how-qwayk-keeps-agents-safe.md). For limits and reporting, use the [security page](SECURITY.md).

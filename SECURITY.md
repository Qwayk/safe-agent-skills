# Security

Qwayk skills are software that can touch real accounts or real business data. Review them like software, not just like prompts.

If you want the full explanation of how Qwayk skills guide agent behavior, read [How Qwayk skills keep agents safer](docs/how-qwayk-keeps-agents-safe.md).

## What this repo claims

- Public skill folders keep the instructions, the full safe API CLI code the agent uses, the docs, and the tests together.
- The repo includes visible public checks, and the skill folders keep their code, docs, and tests together where you can inspect them.
- Each skill makes its access level, change risk, and limits clear.
- Read-only skills say clearly that they do not write or sign in.
- Skills that can change real settings or data should show the plan before important changes.
- When possible, they should save the exact thing they are about to change.
- When a product has its own restore, backup, or version history, the skill should use that when it really exists.
- When a change may not be easy to put back, the skill should say so clearly before approval.

## What this repo does not claim

- zero risk
- perfect protection from prompt injection or human mistakes
- that every skill has the same risk level
- that public checks replace your own review

## Public checks in this repo

This repo includes public checks such as CI, CodeQL, Dependabot, and dependency review. These checks help review the repo, but they do not prove every skill is safe for every live account. You should still inspect the specific skill you plan to use.

## How to judge a skill

Every public skill page should tell you:

- what the skill helps with
- what access it needs
- whether it is read-only or can make careful changes
- what happens before a risky change
- what proof it can leave behind

If you want to compare the current public skills, use the full [skill catalog](skills/README.md).

## What you should still do

- inspect the skill files before broad use
- use test accounts when possible
- keep API keys local
- approve live changes carefully

## Limits and responsibility

No AI skill is risk-free. Qwayk skills do not promise zero risk or perfect protection from every attack. They reduce risk with clearer behavior, visible checks, and honest limits.

If you use these tools on live accounts, live settings, or live data, you still choose where they are safe to use. You are still responsible for reviewing the skill, checking the plan, and approving live changes.

## Reporting a problem

If you find a security problem, report it privately first. Do not post active exploit details in a public issue.

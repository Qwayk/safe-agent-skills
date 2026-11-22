# Zapier

Use Zapier to see which apps, actions, and Zaps your integration can access. You can also check past runs, read messages from a Trigger Inbox, and review a promotion enrollment.

A good first request is “Check which Zapier account I’m connected to and list the apps it can use.” The agent checks the profile first, then lists apps. Before creating a Zap or running an action, it shows the plan and waits for your approval.

## Start here first

Follow the [quickstart](docs/quickstart.md) to check your connection and list apps.

## What your agent can do

- Find available apps and actions, then look up the fields and connected accounts an action needs.
- List Zaps, check past runs, and read messages from a Trigger Inbox.
- Prepare a Zap, action run, inbox change, or promotion change for approval.

## What happens before live changes

The agent saves a plan for the exact change. Review the target, the request, and what happens if it runs. After you approve it, the tool checks that the request still matches the plan. For a new action run, the receipt gives you the command to check how it finished. [Plans and receipts](docs/safety_model.md)

## What access this tool needs

Start with a Zapier user access token for the Workflow API. Some commands also need a public integration, specific permission from Zapier, or White Label access. [Set up the connection](docs/onboarding.md)

## Install and first run

Run these from the downloaded skill folder with Python 3.12 or later.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/qwayk-zapier-safe-agent-cli --output json onboarding
```

## What it covers today

The tool recognizes 62 command names from the saved Zapier API files. The [coverage table](docs/api_coverage.md) shows which 35 can send a request and what to do for the other 27.

## Limits

Zapier retired AI Actions on May 29, 2026. Its old commands now point to [Zapier MCP](https://docs.zapier.com/mcp/quickstart). Use browser sign-in to create or connect an account. Use the inbox message list to inspect an inbox. The local checks use simulated Zapier replies. [Zapier’s retirement notice](https://nla.shared.zapier.com/updates)

## Helpful docs

- [Setup and connection problems](docs/onboarding.md)
- [Command reference](docs/command_reference.md)
- [Plans, approvals, and receipts](docs/safety_model.md)
- [Test results](docs/proof.md)

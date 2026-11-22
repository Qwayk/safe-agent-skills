# Klaviyo

Use Klaviyo to see who’s on a list, what happened on a profile, and which campaigns or flows are running. You can also prepare a list, profile, template, or catalog change for review.

A good first request is “List the audiences this key can read and show me the list I should review.” If the work would send a campaign, change a flow’s status, or change who receives messages, the agent shows the plan and waits for approval.

## Start here

Follow the [setup guide](docs/onboarding.md), then use the [quickstart](docs/quickstart.md) to list audiences.

## Install

Run these from the skill folder with Python 3.12 or later.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/klaviyo-safe-agent-cli onboarding
```

## Before a change

Start with a preview. Review the exact account, records, and request. Any live change needs approval to proceed without a saved copy of the previous state. Flow status changes and other high-impact actions also need a matching saved plan and confirmation. [Plans and receipts](docs/safety_model.md)

## What’s included

The tool has 308 named commands for the Klaviyo API revision dated April 15, 2026. Use a private key with the permissions the job needs. Client commands use the company ID. [API coverage](docs/api_coverage.md)

- [Command reference](docs/command_reference.md)
- [Verification notes](docs/proof.md)

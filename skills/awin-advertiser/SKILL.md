---
name: awin-advertiser-safe-cli
description: Review Awin advertiser results, find transactions, and prepare offers, feeds, conversion orders, or transaction changes for approval.
---

# Awin Advertiser

Use this skill for an advertiser's own program. Start by checking the chosen settings file and advertiser ID. For a report, confirm the date range and use the named read command that answers the question. For a setup problem, run onboarding, then check that auth can read the expected advertiser. Keep tokens out of chat.

Useful first commands are `awin-advertiser-safe-cli --env-file .env auth check` and `awin-advertiser-safe-cli --env-file .env publishers list --advertiser-id <id>`. Use JSON output and keep the selected settings file in each command.

Before any live change, prepare a preview and save the plan. Show the advertiser, action and what the input file contains. For a feed, include the locale. For conversion orders, include any webhook destination. Wait for approval before using `--apply --yes --ack-irreversible --plan-in`. Return the receipt path and explain what Awin confirmed. For a pending, partial or unclear result, check Awin before resending anything.

Use the named commands in the command guide. For work outside those commands, explain what Awin supports and what still needs to be done outside this skill.

[Command guide](docs/command_reference.md) · [Setup](docs/onboarding.md) · [Plan and receipt review](docs/safety_model.md)

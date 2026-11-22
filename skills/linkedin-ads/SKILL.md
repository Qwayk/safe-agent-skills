---
name: linkedin-ads-safe-cli
description: Check LinkedIn ad accounts, read campaign results, inspect creatives and lead forms, and prepare LinkedIn Ads changes for approval.
---

Use `linkedin-ads-api-tool --output json` for LinkedIn Ads work. Start with [the quickstart](docs/quickstart.md) for a first report, or [account setup](docs/onboarding.md) if the token is missing. Keep tokens and saved credentials out of prompts and replies.

1. Run `auth check`, identify the right account, and check [API coverage](docs/api_coverage.md) for the requested job. Read operations can go straight to LinkedIn within the user's request.
2. For a report, state the account and dates. If the report is empty, check access before reporting zero activity. LinkedIn may require a separate product approval, permission, or account role.
3. For a write, save the plan with `--plan-out plan.json`. Show the exact account, item, and proposed change, then get approval for that change and for proceeding without a saved copy.
4. After approval, use `--apply --ack-irreversible --ack-no-snapshot`. Add `--yes --plan-in plan.json` for delete, batch, and permission changes. Put these options before the command family.
5. Read the JSON for a refusal or a response receipt. Explain what LinkedIn returned. Check the affected item separately before saying the change is verified, and check its state before retrying a write after a lost reply.

Use [the approval guide](docs/safety_model.md) for the exact checks. Use `runs list` and `runs show --run-id <id>` when you need the local record. For tasks outside LinkedIn Ads, use the tool that fits that product.

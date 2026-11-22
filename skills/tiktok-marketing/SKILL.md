---
name: tiktok-marketing-safe-cli
description: Find TikTok ad accounts, read campaign reports, inspect ads and creatives, and prepare campaign changes for approval.
---

Use `tiktok-marketing-api-tool --output json` for TikTok Marketing. Start with [the quickstart](docs/quickstart.md) for an account check, report, or campaign plan. If credentials are missing, use [account setup](docs/onboarding.md). Keep credentials out of prompts and replies.

1. Run `auth check` and choose the account by name and ID. This contacts TikTok. Check [API coverage](docs/api_coverage.md) if you need to find an operation.
2. For a report, use `--live` when the request permits the read. Say which account and dates you used. Check `page_info` before giving a total.
3. For a write, save a plan with `--plan-out plan.json`. Show the target and exact change, then ask for approval for the change and for proceeding without a saved copy if the plan says one is unavailable.
4. After approval, use `--live --apply --yes --plan-in plan.json --ack-irreversible --ack-no-snapshot` before the command family. Apply the saved inputs. If anything changes, save a new plan and review it again.
5. Explain what TikTok returned or why the tool refused. For campaign updates, read the same campaign again to confirm its status before reporting the change as verified. If the reply is lost, check the item before trying again.

See [how to approve and check a change](docs/safety_model.md). Use `runs list` and `runs show --run-id <id>` to find a local record when useful.

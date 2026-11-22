---
name: openai-ads
description: Check ChatGPT Ads campaigns and results, review conversion settings, and prepare Ads Manager changes for the user's approval.
---

# OpenAI Ads

Start with the account the user chose. Run `openai-ads-safe-agent-cli --output json auth check` to confirm it. A useful first read is `openai-ads-safe-agent-cli --output json api campaigns list-campaigns --query limit=10`. Use the Quickstart in the tool folder when the CLI needs to be installed.

For a change, prepare a plan first. Show the user the account, target, requested change, what you checked, and any effect on spend, delivery, audiences, or tracking. Wait for approval of that plan. Use the saved plan and the acknowledgements required for the specific change. Treat starting delivery as its own decision after a paused build.

If a reply leaves the result unknown, use the receipt to check what happened before trying again. Keep keys, customer data, audience rows, and private tracking values out of the reply. Use the separate OpenAI Platform tool for general API work.

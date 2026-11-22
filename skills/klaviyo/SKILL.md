---
name: klaviyo-safe-cli
description: Review Klaviyo lists, profiles, campaigns, flows and events. Prepare changes for approval and check the results.
---

# Klaviyo

Start with the user’s job. For an audience check, run `klaviyo-safe-agent-cli --output json --live api get_lists` with the settings file they chose. If setup is missing, run onboarding and use the next command it gives you. Ask for the permission the task needs. Keep keys, tokens, and private inputs out of chat.

Use named commands and JSON output. Check the account, target IDs and request before planning a change. Save a preview and wait for the person to approve it. Use the reviewed plan when you apply. Approved writes need `--live --apply --ack-no-snapshot`. For flow status changes and other high-impact writes, also use `--plan-in` and `--yes`.

After a write, explain what Klaviyo returned. A queued job may still be running. Use the follow-up command in the receipt when it’s available. If the result is uncertain, check Klaviyo before trying again. If the tool refused the change, explain the reason and confirm what’s needed next.

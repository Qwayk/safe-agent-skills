---
name: openai
description: Check OpenAI API models, files, usage and project settings, and review supported changes before sending them.
---

# OpenAI Platform

Use this skill to work with the OpenAI API through `openai-api-tool`. Start with `api ops list` to find a supported command or `auth check` to check local settings. For an approved live read, add `--live` before the command. If setup is missing, run `onboarding` and use the settings file it names.

For changes and requests that can cost money, save a plan and wait for approval. Use `--live --apply --plan-in <file> --ack-no-snapshot` after review. A paid action also needs `--yes --ack-spend-money`. A delete also needs `--yes --ack-irreversible`. Keep the same account, settings folder, and inputs when applying. The tool has no automatic restore.

Check the receipt for the result or the resource ID. If the reply is lost or the result still needs checking, check the account before preparing another request. Keep API keys and private input out of chat and logs. Share receipt paths when they help the person take the next step.

Use Responses and Conversations for work that used to rely on the Assistants API.

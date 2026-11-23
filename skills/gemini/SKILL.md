---
name: gemini
description: Help users work with the Gemini Developer API. List models, count tokens, run approved generation or embeddings, and manage files, caches and batch jobs.
---

# Gemini API

Use Gemini when the user wants to choose a model, count tokens, run a request, or check Gemini files, caches, file search stores or batches. Use the Google Cloud tool for Cloud administration or Vertex AI work.

Start by checking local setup with `gemini-api-tool --output json auth check`. Then run `gemini-api-tool --output json models list` to check that Google accepts the key. If the key is missing, run `onboarding` and guide the user through local setup. Keep the key out of chat and use the same `--env-file` throughout.

Use named Gemini commands. List resources and count tokens within the user’s request. Get spending approval before sending requests that can charge, then add `--ack-spend-money`.

For changes or new batch jobs, make a dry-run plan and review its target and the original request or upload with the user. Once approved, use `--plan-in plan.json --apply --yes` with any required `--ack-no-snapshot`, `--ack-irreversible` or spending approval. Check Gemini’s reply and the resource where possible. If no reply comes back, check whether the action happened before making a new plan.

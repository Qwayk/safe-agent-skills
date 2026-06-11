---
name: amazon-pa-api-safe-cli
description: Run amazon-pa-api-tool safely (read-only) and enforce --yes for multi-request batching.
---

This page is the agent-facing rule sheet for the public Amazon PA-API v5 skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe wrapper for the Amazon Product Advertising API (PA‑API v5) Qwayk CLI (`amazon-pa-api-tool`).

Core rules (do not break):
- Always use `--output json` for tool calls.
- Never print or request secrets (API keys, partner tags, `.env` contents, Authorization headers).
- Refuse if required configuration is missing or ambiguous.
- This tool is read-only, but still treat large/batch requests as “risky” (cost, quota, and accidental multi-request expansion).
- Require `--yes` when a request expands into multiple PA‑API requests (examples: more than 10 ASINs, more than 10 browse node IDs, or `--max-requests` > 1).

Workflow (read-only):
1) Validate configuration: `amazon-pa-api-tool --output json auth check`
2) Discover targets (read-only):
   - Resolve ASIN from a URL: `amazon-pa-api-tool --output json product resolve --url "https://www.amazon.com/dp/B000000000/"`
3) Run the smallest read that satisfies the goal:
   - Search: `amazon-pa-api-tool --output json product search --query "air fryer" --limit 3`
   - Fetch items: `amazon-pa-api-tool --output json product get --asin B000000000 --asin B000000001`
4) If the user asks for a large batch:
   - Start with a small sample first (1–3 items).
   - Only proceed with a multi-request batch when `--yes` is present and the user understands it can issue multiple API requests.

References:
- Agent skill prompt and install notes are included with this package.
- Docs: `docs/quickstart.md`, `docs/command_reference.md`, `docs/jobs_and_batches.md`, `docs/safety_model.md`

Notes:
- `--apply` is accepted for consistency but does not enable external writes for this tool.
- `--include-raw` can increase output size substantially; only use it when explicitly needed.

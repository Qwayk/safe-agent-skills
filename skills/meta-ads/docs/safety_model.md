# Safety model

This tool is intentionally **read-only** and **GET-only**.

## What this tool will never do (in this phase)

- Create/update/delete anything in Meta Ads
- Pause/enable ads, change budgets, or modify targeting
- Send non-GET HTTP requests

If asked to do any of the above, the tool should refuse with a clear explanation.

## What this tool does safely

- Fetch inventory and reporting data via Graph API GET endpoints
- Paginate results deterministically (`paging.next`)
- Retry politely on rate limits (429) and transient server errors (5xx) with backoff
- Keep access tokens out of stdout/stderr and out of URLs shown in verbose logs (redaction)

## How to use it safely with an AI agent

Recommended workflow:
1) Run `onboarding` (if config isn’t set up).
2) Run `auth check`.
3) Run one or more read-only commands and capture the JSON output.
4) Summarize results and include the exact command(s) used.

Note: In the broader Qwayk ecosystem, write-capable tools use a plan → review → apply → verify → receipt loop.
For Meta Ads, **remote writes are not implemented in this tool yet**, so every task should be treated as read-only.

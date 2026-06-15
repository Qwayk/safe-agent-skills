# Proof and verification

Reddit proof should answer a simple question: what has actually been checked for posts, comments, mod actions, users, subreddits, and generated API calls, and what still needs live credentials, permissions, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check post/subreddit proof and moderation or write-plan evidence before trusting Reddit work.

## Last verified

- Date (UTC): 2026-06-04
- Environment: local build / pinned Reddit docs snapshot

## Smoke commands

```bash
qwayk-reddit-safe-agent-cli --version
qwayk-reddit-safe-agent-cli onboarding --no-write-env
qwayk-reddit-safe-agent-cli api ops list --section account
```

## Live smoke after auth setup

```bash
qwayk-reddit-safe-agent-cli auth login
qwayk-reddit-safe-agent-cli --live auth exchange-code --redirect-url '<paste redirect url>'
qwayk-reddit-safe-agent-cli --live auth check
qwayk-reddit-safe-agent-cli --live api get-api-v1-me
```

## Safe failure example

- `docs/examples/outputs/auth_check.json` is a safe failure case showing why token exchange is needed before live reads.

## Example proof files

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/onboarding.json`
- `docs/examples/outputs/api_ops_account.json`
- `docs/examples/outputs/auth_check_config_only.json`
- `docs/examples/outputs/auth_check.json`

## What can go wrong

- Reddit may block live access until API approval is granted.
- Reddit may reject weak or generic `User-Agent` strings.
- Some legacy docs may drift from current backend behavior.
- Write applies must either save real before-state or require explicit no-snapshot approval before provider writes or stub receipts. Missing approval, missing credentials, unclear targets, or unsupported write executors still stop safely.

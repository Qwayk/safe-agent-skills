# When a command fails

- For missing settings, run `x-api-tool onboarding --no-write-env`. For a missing token, start with [Connect your X account](onboarding.md).
- If X rejects a token or permission, compare the app settings with the command you want to run. With approval for a live read, run `x-api-tool --live auth check` to see which account the token belongs to.
- If a write is refused, read the reason in the JSON. It may need a new plan, the right account, or another approval flag. If a message or post is unconfirmed, check X before repeating it.
- If X returns a rate limit, stop and check when reads can resume. If a read returns a page token, use it with the same query to read the next page after approval.
- `--verbose` shows request start and end lines on stderr. `--debug` shows a Python traceback for local debugging. Keep tokens, settings and private message text out of shared logs.

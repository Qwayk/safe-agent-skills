# Command reference

Use this page when you need the exact Hacker News command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags

- `--output json|text`: output format. Default is `json`.
- `--env-file <PATH>`: optional env file path. Default is `.env`.
- `--config <PATH>`: optional JSON defaults file.
- `--api-root <URL>`: override the Hacker News API root for this run.
- `--timeout-s <SECONDS>`: override request timeout.
- `--log-file <PATH>`: optional sanitized JSONL audit log.
- `--verbose`: verbose HTTP logs to stderr.
- `--debug`: include stack traces on failures.

## Commands

```text
hacker-news-api-tool onboarding
hacker-news-api-tool onboarding --no-write-env
hacker-news-api-tool auth check
hacker-news-api-tool items get --id <ITEM_ID>
hacker-news-api-tool users get --id <USER_ID>
hacker-news-api-tool stories top
hacker-news-api-tool stories new
hacker-news-api-tool stories best
hacker-news-api-tool stories ask
hacker-news-api-tool stories show
hacker-news-api-tool stories jobs
hacker-news-api-tool maxitem get
hacker-news-api-tool updates get
```

## Notes

- `items get` and `users get` return a JSON error when the API payload is `null`.
- Story commands return the raw ordered array of item ids from the official endpoint.
- `auth check` is a safe live read against `maxitem.json` because this API has no authentication flow.

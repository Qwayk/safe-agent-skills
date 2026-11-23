# Hacker News commands

Use these commands after you [install the CLI](quickstart.md). Put options such as `--api-root` before the command.

```text
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
hacker-news-api-tool auth check
hacker-news-api-tool onboarding --no-write-env
```

Story lists return IDs in the order Hacker News sends them. Open an ID with `items get` to read its details. `maxitem get` returns the latest item ID. `updates get` returns the IDs of recently changed items and users. `auth check` fetches the latest item ID to check the connection.

## Optional settings

The default API address is `https://hacker-news.firebaseio.com/v0` and the default timeout is 30 seconds. Use `--api-root <URL>` (also `--base-url`) to choose the API address for one run. It takes priority over your shell and settings files. Use `--timeout-s <SECONDS>` to set how long that run waits for a reply.

For settings you want to use again, set `HACKER_NEWS_API_ROOT` and `HACKER_NEWS_TIMEOUT_S` in your shell or in `.env`. Use `--env-file <PATH>` to pick another settings file. `HACKER_NEWS_BASE_URL` is a fallback when `HACKER_NEWS_API_ROOT` is empty. Shell values take priority over the file for the same setting. You can also supply defaults with `--config <PATH>`. Its JSON keys are `api_root` (or `base_url`) and `timeout_s`. Running `onboarding` without `--no-write-env` can create a local settings file if it is missing.

- `--output json|text` chooses the output format. JSON is the default.
- `--log-file <PATH>` saves command events as one JSON object per line.
- `--verbose` prints HTTP details to standard error. `--debug` shows a stack trace when an unexpected program error occurs.
- `--version` prints the CLI version.

## If a read fails

- If an item or user is missing, check the ID. Usernames are case-sensitive. Hacker News sends `null` and the CLI reports a `ValidationError`.
- If the tool gets an unexpected reply, check the API address and run `hacker-news-api-tool --output json auth check`. It succeeds when the server returns a valid latest item ID.
- An empty story list is a valid result. If you get IDs back, fetch the items before drawing conclusions.

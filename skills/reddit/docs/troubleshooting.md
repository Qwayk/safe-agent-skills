# Troubleshooting

## `auth check` says setup is missing

- Make sure `.env` has `REDDIT_CLIENT_ID`, `REDDIT_REDIRECT_URI`, and `REDDIT_CONTACT_USERNAME`.

## Reddit rejects live calls

- Check that your app has Reddit Data API approval if your use case needs it.
- Check that your `User-Agent` is descriptive.
- Re-run `qwayk-reddit-safe-agent-cli --live auth refresh` if your token expired.

## An `api` command stays dry-run

- Reads need `--live`.
- Writes need `--live --apply`.
- Risky writes also need `--plan-in --yes`.
- Irreversible writes also need `--ack-irreversible`.
- If a write apply returns `before_state.status="blocked"`, that is the current safe behavior. Do not expect a successful receipt yet.

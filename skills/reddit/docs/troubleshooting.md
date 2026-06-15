# Troubleshooting

When Reddit stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reading posts, comments, subreddits, user context, and public discussion data, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Reddit error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

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
